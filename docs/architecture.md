# MoneyGraph architecture

## Milestone 2 data flow

```text
nodes.parquet + edges.parquet + transactions.parquet
  -> integrity checks and directed weighted graph
  -> structural, monetary, temporal and seed-connectivity features
  -> threshold-based primary role assignment
  -> deterministic weighted Louvain communities
  -> five-component priority score
  -> cautious numeric evidence
  -> nodes_roles.csv + clusters.csv + top_nodes.csv
```

The pipeline reuses the organizer loader and directed graph builder in
`starter/starter.py`. The undirected graph is used only for Louvain community
detection; direction is retained for features and role assignment. Reciprocal
edge values are summed in the community projection.

## Explainability

Role assignment follows a fixed precedence: coordinator, distributor,
consolidator, transit, terminal, then peripheral. All cutoffs are documented in
`config/thresholds.yaml`. `role_score` measures the strength of the matched rule.

`priority_score` is a bounded weighted sum of role strength, money significance,
structural importance, seed connectivity and anomaly evidence. PageRank is one
part of the structural component and cannot dominate the final score.

## Observability limits

Outgoing behavior is observed only through depth 3. Every depth-4 node is
assigned the cautious peripheral fallback, and its evidence explicitly says
that downstream behavior is unobserved. It cannot be called terminal from an
observed zero out-degree.

Seed incoming flow is incomplete. Seed nodes therefore do not use pass-through,
retention, fast-forward or incoming-fan-in rules. Their coordinator and
distributor decisions use observed outgoing structure and centrality only.

Transaction dates have daily resolution. The temporal feature measures outgoing
value on the same day or within two days after the latest observed incoming
date; it does not infer ordering within a day or prove fund identity.

## Milestone 3A API

FastAPI loads the parquet inputs and generated CSV results once when the process
starts. It reuses the shared feature functions to provide explanatory metrics
and verifies that recomputed roles and scores match the CSV snapshot. Requests
do not recompute graph metrics.

The API is read-only and has no database. Summary, priority, node and cluster
responses use explicit Pydantic models. Node graph responses contain a bounded,
directed neighborhood selected by observed connection value. GIDs are returned
as strings to preserve their full int64 values in browser clients.

Local CORS access is allowed for the Next.js development origins on port 3000.
