"""Deterministic feature extraction for the MoneyGraph parquet data.

The organizer loader and directed-graph builder are reused from
``starter/starter.py``; this module adds integrity checks and features.
"""

from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from starter.starter import build_graph as starter_build_graph
from starter.starter import load as starter_load


@dataclass(frozen=True)
class AnalysisData:
    edges: pd.DataFrame
    nodes: pd.DataFrame
    transactions: pd.DataFrame
    graph: nx.DiGraph


def _require_columns(frame: pd.DataFrame, name: str, columns: set[str]) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing columns: {sorted(missing)}")


def load_and_validate(data_dir: Path) -> AnalysisData:
    """Load organizer data and verify cross-file consistency."""
    edges, nodes, transactions = starter_load(data_dir)
    _require_columns(nodes, "nodes.parquet", {"gid", "depth", "is_seed"})
    _require_columns(edges, "edges.parquet", {"src", "dst", "sum_kzt", "n_tx", "depth"})
    _require_columns(transactions, "transactions.parquet", {"src", "dst", "date", "sum_kzt"})
    if nodes["gid"].duplicated().any():
        raise ValueError("nodes.parquet contains duplicate gids")
    node_ids = set(nodes["gid"])
    endpoints = set(edges["src"]) | set(edges["dst"])
    tx_endpoints = set(transactions["src"]) | set(transactions["dst"])
    if not endpoints <= node_ids or not tx_endpoints <= node_ids:
        raise ValueError("edge or transaction endpoint is absent from nodes.parquet")

    tx_agg = (transactions.groupby(["src", "dst"], as_index=False)
              .agg(tx_sum_kzt=("sum_kzt", "sum"), tx_count=("sum_kzt", "size")))
    merged = edges.merge(tx_agg, on=["src", "dst"], how="outer", indicator=True)
    if not (merged["_merge"] == "both").all():
        raise ValueError("edge pairs do not match transaction pairs")
    if not np.allclose(merged["sum_kzt"], merged["tx_sum_kzt"], rtol=0, atol=0.01):
        raise ValueError("edge sums do not match aggregated transactions")
    if not (merged["n_tx"].astype(int) == merged["tx_count"].astype(int)).all():
        raise ValueError("edge counts do not match transaction counts")
    depth_by_gid = nodes.set_index("gid")["depth"]
    source_traversal_depth = edges["src"].map(depth_by_gid).to_numpy() + 1
    if not (source_traversal_depth == edges["depth"].to_numpy()).all():
        raise ValueError("edge traversal depth does not follow source-node depth")

    graph = starter_build_graph(edges)
    graph.add_nodes_from(nodes["gid"].tolist())
    return AnalysisData(edges, nodes, transactions, graph)


def percentile_strength(values: pd.Series) -> pd.Series:
    """Return a deterministic 0..1 empirical strength with zero kept at zero."""
    numeric = values.astype(float).clip(lower=0)
    result = pd.Series(0.0, index=values.index)
    positive = numeric > 0
    if positive.any():
        result.loc[positive] = numeric.loc[positive].rank(method="average", pct=True)
    return result


def _temporal_features(transactions: pd.DataFrame, node_ids: pd.Series, window_days: int) -> pd.DataFrame:
    """Measure outgoing value near the latest prior observed incoming date."""
    tx = transactions.copy()
    tx["date"] = pd.to_datetime(tx["date"])
    incoming_dates = {
        gid: np.sort(group["date"].to_numpy(dtype="datetime64[D]"))
        for gid, group in tx.groupby("dst", sort=False)
    }
    ratios: dict[int, float] = {}
    amounts: dict[int, float] = {}
    median_days: dict[int, float] = {}
    for gid, outgoing in tx.groupby("src", sort=False):
        inbound = incoming_dates.get(gid)
        if inbound is None or not len(inbound):
            ratios[gid], amounts[gid], median_days[gid] = 0.0, 0.0, np.nan
            continue
        outgoing_dates = outgoing["date"].to_numpy(dtype="datetime64[D]")
        prior_index = np.searchsorted(inbound, outgoing_dates, side="right") - 1
        has_prior = prior_index >= 0
        days = np.full(len(outgoing), 10_000, dtype=int)
        days[has_prior] = (outgoing_dates[has_prior] - inbound[prior_index[has_prior]]).astype("timedelta64[D]").astype(int)
        near = has_prior & (days <= window_days)
        outgoing_amounts = outgoing["sum_kzt"].to_numpy(dtype=float)
        near_amount, total_amount = float(outgoing_amounts[near].sum()), float(outgoing_amounts.sum())
        ratios[gid] = near_amount / total_amount if total_amount else 0.0
        amounts[gid] = near_amount
        median_days[gid] = float(np.median(days[has_prior])) if has_prior.any() else np.nan
    temporal = pd.DataFrame({"gid": node_ids})
    temporal["fast_forward_ratio"] = temporal["gid"].map(ratios).fillna(0.0)
    temporal["fast_forward_kzt"] = temporal["gid"].map(amounts).fillna(0.0)
    temporal["median_forward_days"] = temporal["gid"].map(median_days)
    return temporal


def build_node_features(data: AnalysisData, config: dict) -> pd.DataFrame:
    """Build deterministic structural, monetary and temporal node features."""
    graph = data.graph
    features = data.nodes[["gid", "depth", "is_seed"]].copy()
    for _, _, edge_data in graph.edges(data=True):
        edge_data["distance"] = 1.0 / np.log1p(edge_data["sum_kzt"])
    mappings = {
        "in_deg": dict(graph.in_degree()), "out_deg": dict(graph.out_degree()),
        "in_kzt": dict(graph.in_degree(weight="sum_kzt")), "out_kzt": dict(graph.out_degree(weight="sum_kzt")),
        "in_tx": dict(graph.in_degree(weight="n_tx")), "out_tx": dict(graph.out_degree(weight="n_tx")),
        "pagerank": nx.pagerank(graph, weight="sum_kzt", tol=1e-10, max_iter=500),
        "betweenness": nx.betweenness_centrality(graph, weight="distance", normalized=True),
    }
    for column, mapping in mappings.items():
        features[column] = features["gid"].map(mapping).fillna(0)
    integer_columns = ["in_deg", "out_deg", "in_tx", "out_tx"]
    features[integer_columns] = features[integer_columns].astype(int)
    features["unique_senders"], features["unique_recipients"] = features["in_deg"], features["out_deg"]
    features["total_degree"] = features["in_deg"] + features["out_deg"]
    features["total_kzt"] = features["in_kzt"] + features["out_kzt"]
    features["total_tx"] = features["in_tx"] + features["out_tx"]

    max_observed_depth = int(config["observability"]["max_observed_depth"])
    boundary_depth = int(config["observability"]["boundary_depth"])
    features["outgoing_observed"] = features["depth"] <= max_observed_depth
    features["truncated_by_depth"] = features["depth"] == boundary_depth
    complete_flow = (~features["is_seed"]) & features["outgoing_observed"]
    features["pass_through"] = np.where(complete_flow & (features["in_kzt"] > 0), features["out_kzt"] / features["in_kzt"].replace(0, np.nan), np.nan)
    features["retained_kzt"] = np.where(complete_flow, np.maximum(features["in_kzt"] - features["out_kzt"], 0), 0.0)
    features["retained_share"] = np.where(complete_flow & (features["in_kzt"] > 0), features["retained_kzt"] / features["in_kzt"].replace(0, np.nan), np.nan)

    seeds = set(data.nodes.loc[data.nodes["is_seed"], "gid"])
    seed_ancestors = {gid: 0 for gid in data.nodes["gid"]}
    for seed in sorted(seeds):
        seed_ancestors[seed] += 1
        for gid in nx.descendants(graph, seed):
            seed_ancestors[gid] += 1
    features["seed_ancestor_count"] = features["gid"].map(seed_ancestors).fillna(0).astype(int)
    direct_seed_senders = data.edges.loc[data.edges["src"].isin(seeds)].groupby("dst")["src"].nunique()
    features["direct_seed_senders"] = features["gid"].map(direct_seed_senders).fillna(0).astype(int)

    temporal = _temporal_features(data.transactions, features["gid"], int(config["transit"]["fast_forward_window_days"]))
    features = features.merge(temporal, on="gid", how="left", validate="one_to_one")
    seed_mask = features["is_seed"]
    features.loc[seed_mask, ["fast_forward_ratio", "fast_forward_kzt"]] = 0.0
    features.loc[seed_mask, "median_forward_days"] = np.nan
    for column in ["in_kzt", "out_kzt", "total_kzt", "in_tx", "out_tx", "total_tx", "in_deg", "out_deg", "total_degree", "pagerank", "betweenness", "retained_kzt"]:
        features[f"{column}_pct"] = percentile_strength(features[column])
    features["structural_score"] = (0.35 * features["pagerank_pct"] + 0.35 * features["betweenness_pct"] + 0.30 * features["total_degree_pct"]).clip(0, 1)
    return features
