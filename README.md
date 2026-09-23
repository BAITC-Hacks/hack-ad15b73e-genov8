# HackAlem MoneyGraph

This repository contains the HackAlem MoneyGraph solution. The deterministic
batch pipeline reads the organizer parquet files, computes explainable findings,
and writes the three required CSV files. A read-only FastAPI service exposes the
generated investigation results to the frontend.

The frontend remains a scaffold. An AI assistant, persistence, deployment, and
interactive visualization are future milestones.

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

Role thresholds, clustering parameters and ranking weights are documented in
`config/thresholds.yaml`. The rules treat seed inflow as incomplete and treat
depth 4 as an unobserved downstream boundary.

## Read-only API

Start the API after `make analyze` has generated the CSV outputs:

```sh
make backend
```

The OpenAPI documentation is available at `http://127.0.0.1:8000/docs`. The
service provides `/health`, `/api/summary`, `/api/priorities`, node detail and
ego-graph routes, and cluster list/detail routes. GIDs are serialized as strings
so their int64 values remain exact in JavaScript clients.

## Structure

- `backend/app/analysis/` contains feature, role, clustering, ranking and evidence logic.
- `backend/app/api/` contains the cached read-only API repository, models and routes.
- `backend/pipeline.py` runs and validates the complete batch pipeline.
- `frontend/` contains the minimal Next.js TypeScript scaffold.
- `config/thresholds.yaml` records the explainable analysis settings.
- `data/` contains organizer-provided parquet inputs.
- `output/` contains generated hackathon CSV outputs.
- `starter/` contains the organizer-provided reference loader and graph builder.
- `docs/architecture.md` describes the current data flow and limitations.
