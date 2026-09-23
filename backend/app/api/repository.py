"""Cached read-only access to MoneyGraph inputs, features and outputs."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from backend.app.analysis.features import build_node_features, load_and_validate
from backend.app.analysis.ranking import add_priority_scores
from backend.app.analysis.roles import assign_roles
from backend.app.api.models import (
    ClusterDetailResponse,
    ClusterNode,
    ClustersResponse,
    ClusterSummary,
    EgoGraphResponse,
    GraphEdge,
    GraphNode,
    NodeDetailResponse,
    NodeMetrics,
    Observability,
    PrioritiesResponse,
    PriorityComponents,
    PriorityItem,
    SummaryResponse,
)
from backend.pipeline import (
    CLUSTER_COLUMNS,
    NODE_COLUMNS,
    TOP_COLUMNS,
    _load_config,
    _validate_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def _optional_float(value: object) -> Optional[float]:
    return None if pd.isna(value) else float(value)


class MoneyGraphRepository:
    """An immutable in-memory view initialized once per API process."""

    def __init__(self, repo_root: Path = REPO_ROOT) -> None:
        self.repo_root = repo_root
        self.config = _load_config(repo_root / "config" / "thresholds.yaml")
        self.data = load_and_validate(repo_root / "data")
        self.node_results = pd.read_csv(
            repo_root / "output" / "nodes_roles.csv", dtype={"gid": "int64"}
        )
        self.cluster_results = pd.read_csv(repo_root / "output" / "clusters.csv")
        self.top_results = pd.read_csv(
            repo_root / "output" / "top_nodes.csv", dtype={"gid": "int64"}
        )
        self.node_results = self.node_results[NODE_COLUMNS]
        self.cluster_results = self.cluster_results[CLUSTER_COLUMNS]
        self.top_results = self.top_results[TOP_COLUMNS]
        _validate_outputs(self.node_results, self.cluster_results, self.top_results)

        # Reuse the shared feature implementation once for explanatory metrics.
        computed = build_node_features(self.data, self.config)
        computed = assign_roles(computed, self.config)
        computed = add_priority_scores(computed, self.config)
        verification = self.node_results.merge(
            computed[["gid", "role", "role_score", "priority_score"]],
            on="gid",
            how="left",
            suffixes=("_csv", "_computed"),
            validate="one_to_one",
        )
        roles_match = (
            verification["role_csv"] == verification["role_computed"]
        ).all()
        scores_match = np.allclose(
            verification["role_score_csv"], verification["role_score_computed"], atol=1e-6
        ) and np.allclose(
            verification["priority_score_csv"],
            verification["priority_score_computed"],
            atol=1e-6,
        )
        if not roles_match or not scores_match:
            raise RuntimeError("generated analysis outputs are stale; run `make analyze`")

        computed = computed.drop(columns=["role", "role_score", "priority_score"])
        self.nodes = computed.merge(
            self.node_results, on="gid", how="inner", validate="one_to_one"
        )
        self.nodes_by_gid = self.nodes.set_index("gid", drop=False)
        self.clusters_by_id = self.cluster_results.set_index("cluster_id", drop=False)

    @staticmethod
    def _parse_gid(gid: str) -> Optional[int]:
        if not gid.isdigit():
            return None
        try:
            return int(gid)
        except ValueError:
            return None

    def has_gid(self, gid: str) -> bool:
        parsed = self._parse_gid(gid)
        return parsed is not None and parsed in self.nodes_by_gid.index

    def summary(self) -> SummaryResponse:
        boundary_depth = int(self.config["observability"]["boundary_depth"])
        roles = self.node_results["role"].value_counts().sort_index()
        return SummaryResponse(
            total_nodes=int(len(self.data.nodes)),
            total_edges=int(len(self.data.edges)),
            total_transactions=int(len(self.data.transactions)),
            total_observed_kzt=float(self.data.edges["sum_kzt"].sum()),
            seed_count=int(self.data.nodes["is_seed"].sum()),
            cluster_count=int(len(self.cluster_results)),
            role_distribution={str(role): int(count) for role, count in roles.items()},
            depth_4_boundary_count=int((self.data.nodes["depth"] == boundary_depth).sum()),
        )

    def _observability(self, row: pd.Series) -> Observability:
        is_boundary = bool(row["truncated_by_depth"])
        is_seed = bool(row["is_seed"])
        warning = None
        if is_boundary:
            warning = (
                "Depth 4 is the traversal boundary. Outgoing activity is unobserved, "
                "so zero observed out-degree is not terminal evidence."
            )
        elif is_seed:
            warning = (
                "Seed incoming flow is incomplete; pass-through and retained-funds "
                "conclusions are not used."
            )
        return Observability(
            outgoing_observed=bool(row["outgoing_observed"]),
            is_depth_4_boundary=is_boundary,
            seed_incoming_incomplete=is_seed,
            warning=warning,
        )

    def _priority_components(self, row: pd.Series) -> PriorityComponents:
        return PriorityComponents(
            role_strength=float(row["role_score"]),
            money_significance=float(row["money_significance"]),
            structural_importance=float(row["structural_importance"]),
            seed_connectivity=float(row["seed_connectivity"]),
            anomaly_evidence=float(row["anomaly_evidence"]),
        )

    def _metrics(self, row: pd.Series) -> NodeMetrics:
        return NodeMetrics(
            in_degree=int(row["in_deg"]),
            out_degree=int(row["out_deg"]),
            unique_senders=int(row["unique_senders"]),
            unique_recipients=int(row["unique_recipients"]),
            incoming_kzt=float(row["in_kzt"]),
            outgoing_kzt=float(row["out_kzt"]),
            total_observed_kzt=float(row["total_kzt"]),
            incoming_transaction_count=int(row["in_tx"]),
            outgoing_transaction_count=int(row["out_tx"]),
            pass_through_ratio=_optional_float(row["pass_through"]),
            retained_kzt=float(row["retained_kzt"]),
            retained_share=_optional_float(row["retained_share"]),
            fast_forward_ratio=float(row["fast_forward_ratio"]),
            fast_forward_kzt=float(row["fast_forward_kzt"]),
            median_forward_days=_optional_float(row["median_forward_days"]),
            pagerank=float(row["pagerank"]),
            betweenness=float(row["betweenness"]),
            structural_score=float(row["structural_score"]),
            seed_ancestor_count=int(row["seed_ancestor_count"]),
            direct_seed_senders=int(row["direct_seed_senders"]),
        )

    def node(self, gid: str) -> Optional[NodeDetailResponse]:
        parsed = self._parse_gid(gid)
        if parsed is None or parsed not in self.nodes_by_gid.index:
            return None
        row = self.nodes_by_gid.loc[parsed]
        return NodeDetailResponse(
            gid=str(parsed),
            role=str(row["role"]),
            role_score=float(row["role_score"]),
            priority_score=float(row["priority_score"]),
            cluster_id=int(row["cluster_id"]),
            evidence=str(row["evidence"]),
            depth=int(row["depth"]),
            is_seed=bool(row["is_seed"]),
            metrics=self._metrics(row),
            priority_components=self._priority_components(row),
            observability=self._observability(row),
        )

    def priorities(self) -> PrioritiesResponse:
        items = []
        for top in self.top_results.itertuples(index=False):
            row = self.nodes_by_gid.loc[int(top.gid)]
            items.append(PriorityItem(
                rank=int(top.rank), gid=str(int(top.gid)), role=str(top.role),
                role_score=float(row["role_score"]), priority_score=float(top.priority_score),
                cluster_id=int(row["cluster_id"]), depth=int(row["depth"]),
                is_seed=bool(row["is_seed"]), why=str(top.why),
            ))
        return PrioritiesResponse(count=len(items), items=items)

    def ego_graph(self, gid: str, limit: int) -> Optional[EgoGraphResponse]:
        parsed = self._parse_gid(gid)
        if parsed is None or parsed not in self.nodes_by_gid.index:
            return None
        edges = self.data.edges
        incident = edges[(edges["src"] == parsed) | (edges["dst"] == parsed)].copy()
        neighbors = (set(incident["src"]) | set(incident["dst"])) - {parsed}
        scored_neighbors = []
        for neighbor in neighbors:
            connection = incident[
                ((incident["src"] == parsed) & (incident["dst"] == neighbor))
                | ((incident["src"] == neighbor) & (incident["dst"] == parsed))
            ]["sum_kzt"].sum()
            priority = float(self.nodes_by_gid.loc[neighbor, "priority_score"])
            scored_neighbors.append((int(neighbor), float(connection), priority))
        scored_neighbors.sort(key=lambda item: (-item[1], -item[2], item[0]))
        chosen = [item[0] for item in scored_neighbors[: max(0, limit - 1)]]
        displayed = {parsed, *chosen}
        displayed_edges = edges[
            edges["src"].isin(displayed) & edges["dst"].isin(displayed)
        ].sort_values(["sum_kzt", "src", "dst"], ascending=[False, True, True])
        ordered_nodes = sorted(
            displayed,
            key=lambda node_gid: (
                node_gid != parsed,
                -float(self.nodes_by_gid.loc[node_gid, "priority_score"]),
                node_gid,
            ),
        )
        graph_nodes = []
        for node_gid in ordered_nodes:
            row = self.nodes_by_gid.loc[node_gid]
            graph_nodes.append(GraphNode(
                gid=str(int(node_gid)), role=str(row["role"]), cluster_id=int(row["cluster_id"]),
                depth=int(row["depth"]), is_seed=bool(row["is_seed"]),
                priority_score=float(row["priority_score"]), is_selected=node_gid == parsed,
            ))
        graph_edges = [
            GraphEdge(source_gid=str(int(edge.src)), target_gid=str(int(edge.dst)),
                      sum_kzt=float(edge.sum_kzt), transaction_count=int(edge.n_tx))
            for edge in displayed_edges.itertuples(index=False)
        ]
        return EgoGraphResponse(
            selected_gid=str(parsed), nodes=graph_nodes, edges=graph_edges,
            available_neighbor_count=len(neighbors), displayed_neighbor_count=len(chosen),
            truncated=len(neighbors) > len(chosen),
        )

    @staticmethod
    def _cluster_summary(row: pd.Series) -> ClusterSummary:
        gids = [] if pd.isna(row["top_gids"]) else str(row["top_gids"]).split("|")
        return ClusterSummary(
            cluster_id=int(row["cluster_id"]), n_nodes=int(row["n_nodes"]),
            n_seed=int(row["n_seed"]), sum_kzt_internal=float(row["sum_kzt_internal"]),
            top_gids=gids, hypothesis=str(row["hypothesis"]),
        )

    def clusters(self) -> ClustersResponse:
        items = [self._cluster_summary(row) for _, row in self.cluster_results.iterrows()]
        return ClustersResponse(count=len(items), items=items)

    def cluster(self, cluster_id: int) -> Optional[ClusterDetailResponse]:
        if cluster_id not in self.clusters_by_id.index:
            return None
        summary = self._cluster_summary(self.clusters_by_id.loc[cluster_id])
        members = self.nodes[self.nodes["cluster_id"] == cluster_id].sort_values(
            ["priority_score", "gid"], ascending=[False, True], kind="mergesort"
        ).head(10)
        important_nodes = [
            ClusterNode(
                gid=str(int(row.gid)), role=str(row.role), role_score=float(row.role_score),
                priority_score=float(row.priority_score), depth=int(row.depth),
                is_seed=bool(row.is_seed), evidence=str(row.evidence),
            )
            for row in members.itertuples(index=False)
        ]
        return ClusterDetailResponse(**summary.model_dump(), important_nodes=important_nodes)


@lru_cache(maxsize=1)
def get_repository() -> MoneyGraphRepository:
    """Return the process-wide cached repository snapshot."""
    return MoneyGraphRepository()
