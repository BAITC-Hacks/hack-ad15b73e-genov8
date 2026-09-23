# MoneyGraph

MoneyGraph is an explainable anti-money-laundering investigation prototype built for HackAlem. It helps an AML or financial monitoring analyst answer one question:

> **Which of these 2,248 clients should be reviewed first, and why?**

The system ingests the organizer's parquet files, computes deterministic graph and transaction features, assigns one explainable role to every client, groups the graph into communities, and ranks investigation hypotheses. It exports the required CSV findings, serves them through a read-only FastAPI API, and presents them in a desktop-first Next.js investigation workspace.

An optional OpenAI investigator can answer natural-language questions by calling bounded, read-only graph tools. AI does not assign roles, scores, clusters, or evidence. Tool results from the deterministic engine remain the source of truth.

## How it works

```text
parquet inputs
  -> validated directed money graph and deterministic features
  -> threshold-based roles, Louvain clusters, priority scores, evidence
  -> required CSV findings
  -> cached read-only FastAPI repository
  -> Next.js investigation workspace
  -> optional OpenAI investigator using grounded graph tools
```

The pipeline reuses the organizer loader and graph builder in `starter/starter.py`. It validates node and edge consistency, aggregate amounts, transaction counts, and traversal depth before analysis.

For each node it computes observed incoming and outgoing degree, unique senders and recipients, KZT totals, transaction counts, pass-through and retained-flow measures, short-window forwarding behavior, weighted PageRank, weighted betweenness, combined structural strength, and seed connectivity. All calculations are deterministic.

Communities use NetworkX Louvain detection with resolution `1.0` and random seed `42`. Louvain runs on an undirected weighted projection, with reciprocal transfer values summed; direction is retained for features, roles, evidence, path tools, and the UI graph.

## Explainable roles

Roles are evaluated in this fixed order: **coordinator, distributor, consolidator, transit, terminal, peripheral**. Once a rule matches, later rules are not considered. The values below come directly from `config/thresholds.yaml`.

| Role | Plain-language interpretation | Implemented rule | Limitation |
|---|---|---|---|
| **Coordinator** | A strongly connected node that may organize or bridge several flows. | For an observed non-seed with both incoming and outgoing links: either at least `3` senders and `3` recipients, or total degree at least `8` with structural score at least `0.90`. A seed instead requires at least `8` recipients and structural score at least `0.90`. | This is a structural investigation signal. Seed inflow is incomplete, so seed classification uses outgoing structure and centrality only. |
| **Distributor** | A node sending observed funds to many recipients. | Among nodes not already classified, outgoing behavior must be observable and unique recipients must be at least `5`. | Only observed in-bank recipients are counted; missing downstream or external transfers can change the picture. |
| **Consolidator** | A node receiving from several senders while sending to few recipients. | Among remaining observed non-seeds: at least `3` senders, at most `2` recipients, and at least `100,000 KZT` observed incoming. | It excludes seeds because their incoming flow is incomplete. It indicates signs of consolidation, not ownership or intent. |
| **Transit** | A node with observed onward movement close to its incoming flow and fast forwarding. | Among remaining observed non-seeds with incoming and outgoing links: pass-through ratio from `0.50` to `1.50`, and at least `0.50` of outgoing value sent on the same day or within `2` days of the latest prior observed receipt. | Dates have daily resolution, so same-day ordering and identity of funds cannot be proven. |
| **Terminal** | A node where a meaningful share of observed incoming funds appears retained. | Among remaining observed non-seeds: at least `100,000 KZT` incoming, at least `100,000 KZT` retained, retained share at least `0.80`, and at most `1` recipient. | Applied only where outgoing behavior is observable. It is a terminal-behavior hypothesis, not proof that funds finally stopped there. |
| **Peripheral** | No higher-information role rule matched in the observed graph. | Deterministic fallback. Every depth-4 boundary node is handled as peripheral with a boundary caveat. | Peripheral does not mean safe or unimportant. At depth 4 it primarily reflects missing downstream observation. |

`role_score` is a bounded `[0,1]` strength score derived from the metrics in the matched rule. It is not a probability of wrongdoing.

## Priority ranking

`priority_score` is an interpretable weighted sum in `[0,1]`, not a black-box model:

| Component | Weight | Implemented signal |
|---|---:|---|
| Role strength | `0.25` | Strength of the matched role rule. |
| Money significance | `0.27` | Empirical percentile of total observed incoming plus outgoing KZT. |
| Structural importance | `0.15` | Combined percentile score: `0.35` PageRank, `0.35` betweenness, and `0.30` total degree. |
| Seed connectivity | `0.17` | `0.65` seed-ancestor reach, saturated at `10` seeds, plus `0.35` proximity to depth 0. |
| Anomaly evidence | `0.16` | `0.40` fast-forward ratio, `0.30` flow-imbalance percentile, and `0.30` transaction-count percentile. |

The structural weight is deliberately limited because coordinator role strength already contains structural evidence. No single metric such as PageRank determines the queue.

Evidence strings summarize the observed numbers behind each hypothesis in fewer than 200 characters. Cluster hypotheses and all UI wording remain investigation-oriented.

## Observability and responsible interpretation

The source extract is a bounded view of activity:

- Outgoing traversal is observed only through depth `3`; depth `4` is the traversal boundary.
- A depth-4 node with observed out-degree zero is **not** evidence of terminal behavior. Its downstream activity is unobserved and it receives a boundary warning.
- Seed incoming flow is incomplete because traversal begins from seed outgoing activity. Seed rules do not use observed incoming KZT, pass-through, retention, or fast-forward measures; seed coordinator detection uses outgoing degree plus graph centrality.
- Only outgoing traversal visible within the supplied intra-bank graph is observed. External-bank and otherwise unobserved activity is outside the dataset.
- Transfers below `5,000 KZT` are absent from the supplied extract.
- Findings are investigation hypotheses for analyst review, never determinations of guilt, criminal status, ownership, or intent.

## Prerequisites

- Python 3.9 or newer
- Node.js 20 or newer with npm
- `make`

The repository includes the required organizer parquet files and frontend lockfile. From the repository root, create an isolated Python environment and install exact frontend lockfile dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm ci
cd ..
```

`make install-backend` and `make install-frontend` are convenience targets. The explicit commands above make the isolated environment and lockfile use clear.

## Run the deterministic analysis

From the repository root:

```sh
make analyze
```

This command reads `data/nodes.parquet`, `data/edges.parquet`, and `data/transactions.parquet`, then regenerates exactly these required findings:

- `output/nodes_roles.csv` — one row per GID with `gid`, `role`, `role_score`, `cluster_id`, `priority_score`, and `evidence`.
- `output/clusters.csv` — one row per cluster with node count, seed count, internal observed KZT, important GIDs, and a cautious hypothesis.
- `output/top_nodes.csv` — the ranked investigation queue with at least 20 nodes and a short explanation for each.

The pipeline validates the schemas, exactly 2,248 unique node rows, complete required fields, allowed roles, bounded scores, cluster coverage, evidence length, and ranking order before replacing the CSVs.

## Start the application

Start the backend and frontend in separate terminals from the repository root:

```sh
make backend
```

```sh
make frontend
```

Open `http://localhost:3000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`; health is at `http://127.0.0.1:8000/health`.

The read-only API exposes:

- `GET /api/summary`
- `GET /api/priorities`
- `GET /api/nodes/{gid}`
- `GET /api/nodes/{gid}/graph`
- `GET /api/clusters`
- `GET /api/clusters/{cluster_id}`
- `POST /api/investigator` when the optional AI integration is configured

GIDs are serialized as strings so full int64 identifiers remain exact in JavaScript.

## Environment and optional OpenAI investigator

The deterministic pipeline, API, and workspace work without an API key. To configure local environment values, copy the secret-free template:

```sh
cp .env.example .env
```

The backend loads the repository-root `.env`. Set `OPENAI_API_KEY` only when the optional investigator is wanted, and optionally override `OPENAI_MODEL`. The default model is recorded in `.env.example`. `NEXT_PUBLIC_API_BASE_URL` controls the browser's API URL.

```dotenv
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4.1-mini
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`.env` is gitignored. The OpenAI key is backend-only and must never use a `NEXT_PUBLIC_` name. When the key is absent, `/api/investigator` returns a clear unavailable response while every mandatory deterministic feature remains available.

The investigator uses the OpenAI Responses API and a maximum of five calls to six read-only tools: node card, common receivers, bounded paths, node filtering, cluster summary, and removal impact. Tool results are the source of truth for GIDs, paths, roles, scores, amounts, and other graph facts. Answers preserve depth-4 and seed-inflow caveats and remain hypotheses for human review.

## Repeatable judge demo

1. Regenerate the findings with `make analyze` and inspect the three files in `output/`.
2. Start `make backend` and `make frontend` in separate terminals.
3. Open the first row in the priority queue and review its role, priority components, evidence, and bounded directed ego graph.
4. Search any exact GID to load a node outside the top queue.
5. Search depth-4 GID `100000000404740100` and confirm the visible observability warning.
6. Click a neighboring graph node and confirm that its investigation card and ego graph load.
7. If the backend has `OPENAI_API_KEY`, ask: `Why is GID 100000004156082100 high priority?` and inspect the factual tool activity log.

## Scaling beyond the hackathon dataset

The current implementation is intentionally optimized for a convincing, explainable prototype on 2,248 nodes. For materially larger datasets, realistic changes would include:

- replace in-memory pandas ingestion and joins with Polars or DuckDB;
- replace NetworkX with igraph, graph-tool, Neo4j Graph Data Science, or cuGraph where their operating model fits;
- use approximate or sampled betweenness instead of exact all-node betweenness;
- partition inputs and incrementally recompute affected features, communities, and cached API snapshots;
- continue serving bounded ego networks to the browser instead of rendering the full graph;
- precompute or index bounded path and neighborhood queries for interactive latency.

These scaling changes are not implemented in this repository.

## Repository layout

```text
backend/
  app/analysis/       deterministic features, roles, clustering, ranking, evidence
  app/api/            cached repository, response models, read-only routes
  app/agent/          bounded OpenAI loop and grounded graph tools
  pipeline.py         end-to-end analysis and output validation
config/
  thresholds.yaml     implemented rules, weights, clustering, observability settings
data/                  organizer parquet inputs
output/                generated required CSV findings
frontend/              Next.js TypeScript investigation workspace
starter/               organizer-provided loader and graph builder
docs/
  architecture.md     architecture diagram and layer responsibilities
```
