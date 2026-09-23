# HackAlem MoneyGraph

This repository contains the HackAlem MoneyGraph solution. Milestone 2 provides
a deterministic batch pipeline that reads the organizer parquet files, computes
node features, assigns explainable roles, detects graph communities, ranks nodes,
and writes the three required CSV files.

The frontend and FastAPI scaffold remain unchanged. API endpoints, an AI
assistant, persistence, deployment, and interactive visualization are future
milestones.

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

## Structure

- `backend/app/analysis/` contains feature, role, clustering, ranking and evidence logic.
- `backend/pipeline.py` runs and validates the complete batch pipeline.
- `frontend/` contains the minimal Next.js TypeScript scaffold.
- `config/thresholds.yaml` records the explainable analysis settings.
- `data/` contains organizer-provided parquet inputs.
- `output/` contains generated hackathon CSV outputs.
- `starter/` contains the organizer-provided reference loader and graph builder.
- `docs/architecture.md` describes the current data flow and limitations.
