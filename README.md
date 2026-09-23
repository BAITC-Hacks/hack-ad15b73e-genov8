# HackAlem MoneyGraph

MoneyGraph is an explainable AML investigation prototype for the HackAlem case.
A deterministic batch pipeline analyzes the organizer parquet files and writes the
required CSV findings. A FastAPI service exposes those findings, and the Next.js
workspace provides a priority queue, bounded money graph, node evidence, cluster
context, and an optional grounded AI investigator.

All roles, scores, paths, amounts, and graph facts originate from the deterministic
MoneyGraph data. The AI investigator is an investigation aid and does not determine
guilt or customer intent.

## Analysis pipeline

Install the backend dependencies in an isolated environment:

```sh
make install-backend
```

Regenerate all required outputs from `data/*.parquet`:

```sh
make analyze
```

The pipeline writes only:

- `output/nodes_roles.csv`
- `output/clusters.csv`
- `output/top_nodes.csv`

Role thresholds, clustering parameters, and ranking weights are documented in
`config/thresholds.yaml`. The rules treat seed inflow as incomplete and depth 4
as an unobserved downstream boundary.

## API and frontend

Start the API and frontend in separate terminals:

```sh
make backend
make frontend
```

The workspace is available at `http://localhost:3000`. The API documentation is
available at `http://127.0.0.1:8000/docs`. GIDs are serialized as strings so their
int64 values remain exact in JavaScript clients.

Set `NEXT_PUBLIC_API_BASE_URL` when the frontend should use a backend other than
`http://localhost:8000`.

## Optional AI investigator

The `POST /api/investigator` endpoint uses the OpenAI Responses API with six
read-only MoneyGraph tools. The loop executes at most five tool calls and derives
its clickable GID references from tool results. It does not send the API key to
the browser.

Configure the backend environment when AI investigation is wanted:

```sh
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4.1-mini"  # optional override
```

Model access and billing depend on the configured OpenAI account. If
`OPENAI_API_KEY` is absent, the endpoint returns a clear unavailable response and
all deterministic analysis, API, and frontend functionality continues to work.
Do not put `OPENAI_API_KEY` in a `NEXT_PUBLIC_` variable.

## Structure

- `backend/app/analysis/` contains feature, role, clustering, ranking, and evidence logic.
- `backend/app/agent/` contains the bounded AI loop and grounded graph tools.
- `backend/app/api/` contains the cached repository, response models, and routes.
- `backend/pipeline.py` runs and validates the deterministic batch pipeline.
- `frontend/` contains the Next.js TypeScript investigation workspace.
- `config/thresholds.yaml` records the explainable analysis settings.
- `data/` contains organizer-provided parquet inputs.
- `output/` contains generated hackathon CSV outputs.
- `starter/` contains the organizer-provided reference loader and graph builder.
- `docs/architecture.md` describes the deterministic data flow and limitations.
