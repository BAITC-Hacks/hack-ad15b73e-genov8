export type Role =
  | "coordinator"
  | "distributor"
  | "consolidator"
  | "transit"
  | "terminal"
  | "peripheral";

export interface SummaryResponse {
  total_nodes: number;
  total_edges: number;
  total_transactions: number;
  total_observed_kzt: number;
  seed_count: number;
  cluster_count: number;
  role_distribution: Record<Role, number>;
  depth_4_boundary_count: number;
}

export interface PriorityItem {
  rank: number;
  gid: string;
  role: Role;
  role_score: number;
  priority_score: number;
  cluster_id: number;
  depth: number;
  is_seed: boolean;
  why: string;
}

export interface PrioritiesResponse {
  count: number;
  items: PriorityItem[];
}

export interface PriorityComponents {
  role_strength: number;
  money_significance: number;
  structural_importance: number;
  seed_connectivity: number;
  anomaly_evidence: number;
}

export interface NodeMetrics {
  in_degree: number;
  out_degree: number;
  unique_senders: number;
  unique_recipients: number;
  incoming_kzt: number;
  outgoing_kzt: number;
  total_observed_kzt: number;
  incoming_transaction_count: number;
  outgoing_transaction_count: number;
  pass_through_ratio: number | null;
  retained_kzt: number;
  retained_share: number | null;
  fast_forward_ratio: number;
  fast_forward_kzt: number;
  median_forward_days: number | null;
  pagerank: number;
  betweenness: number;
  structural_score: number;
  seed_ancestor_count: number;
  direct_seed_senders: number;
}

export interface Observability {
  outgoing_observed: boolean;
  is_depth_4_boundary: boolean;
  seed_incoming_incomplete: boolean;
  warning: string | null;
}

export interface NodeDetail {
  gid: string;
  role: Role;
  role_score: number;
  priority_score: number;
  cluster_id: number;
  evidence: string;
  depth: number;
  is_seed: boolean;
  metrics: NodeMetrics;
  priority_components: PriorityComponents;
  observability: Observability;
}

export interface GraphNode {
  gid: string;
  role: Role;
  cluster_id: number;
  depth: number;
  is_seed: boolean;
  priority_score: number;
  is_selected: boolean;
}

export interface GraphEdge {
  source_gid: string;
  target_gid: string;
  sum_kzt: number;
  transaction_count: number;
}

export interface EgoGraphResponse {
  selected_gid: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  available_neighbor_count: number;
  displayed_neighbor_count: number;
  truncated: boolean;
}

export interface ClusterSummary {
  cluster_id: number;
  n_nodes: number;
  n_seed: number;
  sum_kzt_internal: number;
  top_gids: string[];
  hypothesis: string;
}

export interface ClusterNode {
  gid: string;
  role: Role;
  role_score: number;
  priority_score: number;
  depth: number;
  is_seed: boolean;
  evidence: string;
}

export interface ClusterDetail extends ClusterSummary {
  important_nodes: ClusterNode[];
}

export interface ClustersResponse {
  count: number;
  items: ClusterSummary[];
}

export type InvestigatorStatus = "ok" | "unavailable";

export interface ToolCallRecord {
  name:
    | "node_card"
    | "common_receivers"
    | "paths"
    | "filter_nodes"
    | "cluster_summary"
    | "what_if_remove";
  arguments: Record<string, unknown>;
  status: "ok" | "error";
  referenced_gids: string[];
}

export interface InvestigatorResponse {
  status: InvestigatorStatus;
  answer: string;
  referenced_gids: string[];
  tool_calls: ToolCallRecord[];
}

const configuredBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_URL = configuredBase.replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    cache: "no-store",
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // Keep the status-based message when an error body is not JSON.
    }
    throw new ApiError(message, response.status);
  }
  return (await response.json()) as T;
}

async function investigate(question: string): Promise<InvestigatorResponse> {
  const response = await fetch(`${API_BASE_URL}/api/investigator`, {
    method: "POST",
    cache: "no-store",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });
  const body = (await response.json()) as InvestigatorResponse | { detail?: string };
  if (response.status === 503 && "status" in body && body.status === "unavailable") {
    return body;
  }
  if (!response.ok) {
    const message = "detail" in body && body.detail
      ? body.detail
      : `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status);
  }
  return body as InvestigatorResponse;
}

export const moneyGraphApi = {
  summary: (signal?: AbortSignal) => request<SummaryResponse>("/api/summary", signal),
  priorities: (signal?: AbortSignal) =>
    request<PrioritiesResponse>("/api/priorities", signal),
  node: (gid: string, signal?: AbortSignal) =>
    request<NodeDetail>(`/api/nodes/${encodeURIComponent(gid)}`, signal),
  nodeGraph: (gid: string, signal?: AbortSignal) =>
    request<EgoGraphResponse>(`/api/nodes/${encodeURIComponent(gid)}/graph`, signal),
  clusters: (signal?: AbortSignal) => request<ClustersResponse>("/api/clusters", signal),
  cluster: (clusterId: number, signal?: AbortSignal) =>
    request<ClusterDetail>(`/api/clusters/${clusterId}`, signal),
  investigate,
};
