"""Deterministic weighted Louvain clustering and cluster summaries."""

import networkx as nx
import pandas as pd


def assign_clusters(graph: nx.DiGraph, features: pd.DataFrame, config: dict) -> pd.Series:
    """Cluster an undirected projection whose reciprocal values are summed."""
    undirected = nx.Graph()
    undirected.add_nodes_from(features["gid"].tolist())
    for source, target, edge in graph.edges(data=True):
        amount = float(edge["sum_kzt"])
        if undirected.has_edge(source, target):
            undirected[source][target]["sum_kzt"] += amount
        else:
            undirected.add_edge(source, target, sum_kzt=amount)
    settings = config["clustering"]
    communities = nx.community.louvain_communities(
        undirected, weight="sum_kzt", resolution=float(settings["resolution"]), seed=int(settings["random_seed"])
    )
    ordered = sorted(communities, key=lambda community: min(community))
    cluster_by_gid = {gid: cluster_id for cluster_id, community in enumerate(ordered, start=1) for gid in sorted(community)}
    return features["gid"].map(cluster_by_gid).astype(int)


def _cluster_hypothesis(group: pd.DataFrame) -> str:
    if len(group) == 1 and group["total_degree"].iloc[0] == 0:
        return "Isolated in the observed graph; no transactional hypothesis."
    if group["truncated_by_depth"].all():
        return "Depth-4 boundary community; downstream behavior is unobserved."
    if group["is_seed"].sum() >= 2 and (group["role"] == "coordinator").any():
        return "Investigation hypothesis: multi-seed coordination network."
    leading_role = group["role"].value_counts().index[0]
    return {
        "coordinator": "Investigation hypothesis: coordination-centered transfer network.",
        "distributor": "Investigation hypothesis: distribution-centered transfer network.",
        "consolidator": "Investigation hypothesis: consolidation-centered transfer network.",
        "transit": "Investigation hypothesis: pass-through transfer network.",
        "terminal": "Investigation hypothesis: observed retention-centered network.",
        "peripheral": "Investigation hypothesis: mixed or peripheral transfer network.",
    }[leading_role]


def summarize_clusters(features: pd.DataFrame, edges: pd.DataFrame, top_gid_count: int) -> pd.DataFrame:
    cluster_by_gid = features.set_index("gid")["cluster_id"]
    edge_clusters = edges[["src", "dst", "sum_kzt"]].copy()
    edge_clusters["src_cluster"] = edge_clusters["src"].map(cluster_by_gid)
    edge_clusters["dst_cluster"] = edge_clusters["dst"].map(cluster_by_gid)
    internal = edge_clusters.loc[edge_clusters["src_cluster"] == edge_clusters["dst_cluster"]].groupby("src_cluster")["sum_kzt"].sum()
    rows = []
    for cluster_id, group in features.groupby("cluster_id", sort=True):
        top = group.sort_values(["priority_score", "gid"], ascending=[False, True], kind="mergesort").head(top_gid_count)
        rows.append({
            "cluster_id": int(cluster_id), "n_nodes": int(len(group)), "n_seed": int(group["is_seed"].sum()),
            "sum_kzt_internal": round(float(internal.get(cluster_id, 0.0)), 2),
            "top_gids": "|".join(str(int(gid)) for gid in top["gid"]), "hypothesis": _cluster_hypothesis(group),
        })
    return pd.DataFrame(rows)
