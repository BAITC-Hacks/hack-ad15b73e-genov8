# HackAlem MoneyGraph

This repository contains the initial project structure for the HackAlem MoneyGraph solution.
It is set up for a Python deterministic graph-analysis pipeline, a FastAPI API
layer, a Next.js TypeScript frontend, documented threshold configuration, input
data, generated outputs, and project documentation.

Analysis logic is TODO. The backend does not yet ingest parquet files, compute
features, assign roles, cluster transactions, rank findings, generate evidence,
or write hackathon CSV outputs.

## Structure

- `backend/` contains the future Python pipeline and FastAPI application.
- `frontend/` contains a minimal Next.js TypeScript application.
- `config/thresholds.yaml` contains documented placeholder sections for role
  thresholds.
- `data/` is reserved for real organizer-provided parquet files.
- `output/` is reserved for generated CSV outputs.
- `docs/architecture.md` describes the current project structure.

## Development

Install dependencies:

```sh
make install
```

Run the placeholder pipeline:

```sh
make analyze
```

Start the FastAPI app:

```sh
make backend
```

Start the frontend:

```sh
make frontend
```
