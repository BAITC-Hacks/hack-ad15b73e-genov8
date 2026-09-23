# HackAlem MoneyGraph Architecture

This repository contains the initial architecture for the HackAlem MoneyGraph solution. It separates
the deterministic graph-analysis pipeline, the FastAPI API layer, the Next.js
frontend, configuration, input data, generated outputs, and documentation.

## Current Shape

- `backend/app/analysis/` contains placeholders for feature extraction, role
  assignment, clustering, ranking, and evidence generation.
- `backend/app/main.py` exposes a minimal FastAPI health endpoint.
- `backend/pipeline.py` is the future command-line entrypoint for reading real
  parquet files from `data/` and writing required CSV outputs to `output/`.
- `frontend/` contains a minimal Next.js TypeScript application.
- `config/thresholds.yaml` documents placeholder threshold sections for future
  explainable role assignment.

## TODO

- Add organizer-provided parquet files to `data/`.
- Implement deterministic graph analysis with pandas, pyarrow, and networkx.
- Add API routes that expose analysis results.
- Build the frontend workflow around real generated outputs.
