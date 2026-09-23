#!/usr/bin/env python3
"""Run the deterministic MoneyGraph analysis pipeline."""

import argparse
import sys
from pathlib import Path
from time import perf_counter

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.analysis.clustering import assign_clusters, summarize_clusters
from backend.app.analysis.evidence import add_evidence
from backend.app.analysis.features import build_node_features, load_and_validate
from backend.app.analysis.ranking import add_priority_scores, top_nodes
from backend.app.analysis.roles import ALLOWED_ROLES, assign_roles


NODE_COLUMNS = ["gid", "role", "role_score", "cluster_id", "priority_score", "evidence"]
CLUSTER_COLUMNS = ["cluster_id", "n_nodes", "n_seed", "sum_kzt_internal", "top_gids", "hypothesis"]
TOP_COLUMNS = ["rank", "gid", "role", "priority_score", "why"]
EXPECTED_NODE_COUNT = 2_248


def _load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("threshold configuration must be a mapping")
    return config


def _validate_outputs(nodes: pd.DataFrame, clusters: pd.DataFrame, top: pd.DataFrame) -> None:
    if list(nodes.columns) != NODE_COLUMNS or list(clusters.columns) != CLUSTER_COLUMNS or list(top.columns) != TOP_COLUMNS:
        raise ValueError("output schema mismatch")
    if len(nodes) != EXPECTED_NODE_COUNT or nodes["gid"].nunique() != EXPECTED_NODE_COUNT:
        raise ValueError(f"nodes_roles.csv must contain {EXPECTED_NODE_COUNT} unique gids")
    if nodes.isna().any().any() or (nodes.astype(str) == "").any().any():
        raise ValueError("nodes_roles.csv contains missing required fields")
    if not set(nodes["role"]) <= ALLOWED_ROLES:
        raise ValueError("nodes_roles.csv contains an unsupported role")
    for column in ["role_score", "priority_score"]:
        if not nodes[column].between(0, 1, inclusive="both").all():
            raise ValueError(f"{column} is outside [0, 1]")
    if nodes["cluster_id"].isna().any() or (nodes["cluster_id"] < 1).any():
        raise ValueError("every node must have a positive cluster_id")
    if (nodes["evidence"].str.len() >= 200).any():
        raise ValueError("node evidence must be under 200 characters")
    if clusters.empty or clusters.isna().any().any() or int(clusters["n_nodes"].sum()) != EXPECTED_NODE_COUNT:
        raise ValueError("cluster summary is incomplete")
    if len(top) < 20 or top.isna().any().any():
        raise ValueError("top_nodes.csv must contain at least 20 complete rows")
    if not top["priority_score"].is_monotonic_decreasing:
        raise ValueError("top_nodes.csv must be sorted by priority_score")
    if top["rank"].tolist() != list(range(1, len(top) + 1)):
        raise ValueError("top_nodes.csv ranks must be consecutive")


def _write_atomic(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    temporary.replace(path)


def run(data_dir: Path, config_path: Path, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    config = _load_config(config_path)
    data = load_and_validate(data_dir)
    features = build_node_features(data, config)
    features = assign_roles(features, config)
    features["cluster_id"] = assign_clusters(data.graph, features, config)
    features = add_priority_scores(features, config)
    features = add_evidence(features)

    nodes_output = features[NODE_COLUMNS].sort_values("gid", kind="mergesort").reset_index(drop=True)
    clusters_output = summarize_clusters(features, data.edges, int(config["clustering"]["top_gids_per_cluster"]))[CLUSTER_COLUMNS]
    top_output = top_nodes(features, int(config["ranking"]["top_n"]))[TOP_COLUMNS]
    _validate_outputs(nodes_output, clusters_output, top_output)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_atomic(nodes_output, output_dir / "nodes_roles.csv")
    _write_atomic(clusters_output, output_dir / "clusters.csv")
    _write_atomic(top_output, output_dir / "top_nodes.csv")
    return nodes_output, clusters_output, top_output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=REPO_ROOT / "data")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "config" / "thresholds.yaml")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "output")
    args = parser.parse_args()
    started = perf_counter()
    nodes, clusters, top = run(args.data, args.config, args.out)
    runtime = perf_counter() - started
    print(f"MoneyGraph analysis complete in {runtime:.2f}s")
    print(f"rows: nodes_roles={len(nodes)}, clusters={len(clusters)}, top_nodes={len(top)}")
    print("roles:", ", ".join(f"{role}={count}" for role, count in nodes["role"].value_counts().sort_index().items()))
    print(f"clusters: min={clusters.n_nodes.min()}, median={clusters.n_nodes.median():.0f}, max={clusters.n_nodes.max()}")


if __name__ == "__main__":
    main()
