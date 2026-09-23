"""Explicit response models for the read-only MoneyGraph API."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


Role = Literal[
    "coordinator",
    "distributor",
    "consolidator",
    "transit",
    "terminal",
    "peripheral",
]


class HealthResponse(BaseModel):
    status: Literal["ok"]


class SummaryResponse(BaseModel):
    total_nodes: int
    total_edges: int
    total_transactions: int
    total_observed_kzt: float
    seed_count: int
    cluster_count: int
    role_distribution: Dict[str, int]
    depth_4_boundary_count: int


class PriorityComponents(BaseModel):
    role_strength: float
    money_significance: float
    structural_importance: float
    seed_connectivity: float
    anomaly_evidence: float


class NodeMetrics(BaseModel):
    in_degree: int
    out_degree: int
    unique_senders: int
    unique_recipients: int
    incoming_kzt: float
    outgoing_kzt: float
    total_observed_kzt: float
    incoming_transaction_count: int
    outgoing_transaction_count: int
    pass_through_ratio: Optional[float]
    retained_kzt: float
    retained_share: Optional[float]
    fast_forward_ratio: float
    fast_forward_kzt: float
    median_forward_days: Optional[float]
    pagerank: float
    betweenness: float
    structural_score: float
    seed_ancestor_count: int
    direct_seed_senders: int


class Observability(BaseModel):
    outgoing_observed: bool
    is_depth_4_boundary: bool
    seed_incoming_incomplete: bool
    warning: Optional[str]


class NodeDetailResponse(BaseModel):
    gid: str = Field(description="String form preserves the full int64 identifier.")
    role: Role
    role_score: float
    priority_score: float
    cluster_id: int
    evidence: str
    depth: int
    is_seed: bool
    metrics: NodeMetrics
    priority_components: PriorityComponents
    observability: Observability


class PriorityItem(BaseModel):
    rank: int
    gid: str
    role: Role
    role_score: float
    priority_score: float
    cluster_id: int
    depth: int
    is_seed: bool
    why: str


class PrioritiesResponse(BaseModel):
    count: int
    items: List[PriorityItem]


class GraphNode(BaseModel):
    gid: str
    role: Role
    cluster_id: int
    depth: int
    is_seed: bool
    priority_score: float
    is_selected: bool


class GraphEdge(BaseModel):
    source_gid: str
    target_gid: str
    sum_kzt: float
    transaction_count: int


class EgoGraphResponse(BaseModel):
    selected_gid: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    available_neighbor_count: int
    displayed_neighbor_count: int
    truncated: bool


class ClusterSummary(BaseModel):
    cluster_id: int
    n_nodes: int
    n_seed: int
    sum_kzt_internal: float
    top_gids: List[str]
    hypothesis: str


class ClustersResponse(BaseModel):
    count: int
    items: List[ClusterSummary]


class ClusterNode(BaseModel):
    gid: str
    role: Role
    role_score: float
    priority_score: float
    depth: int
    is_seed: bool
    evidence: str


class ClusterDetailResponse(ClusterSummary):
    important_nodes: List[ClusterNode]


class InvestigatorRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    locale: Literal["en", "ru", "kk"] = "en"
    selected_gid: Optional[str] = Field(default=None, pattern=r"^\d+$", max_length=32)


class ToolCallRecord(BaseModel):
    name: Literal[
        "node_card",
        "common_receivers",
        "paths",
        "filter_nodes",
        "cluster_summary",
        "what_if_remove",
    ]
    arguments: Dict[str, Any]
    status: Literal["ok", "error"]
    referenced_gids: List[str]


class InvestigatorResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    answer: str
    referenced_gids: List[str]
    tool_calls: List[ToolCallRecord]
