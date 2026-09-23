"""Interpretable multi-component node priority ranking."""

import numpy as np
import pandas as pd

from backend.app.analysis.features import percentile_strength


def add_priority_scores(features: pd.DataFrame, config: dict) -> pd.DataFrame:
    result = features.copy()
    settings, weights = config["ranking"], config["ranking"]["weights"]
    if not np.isclose(sum(float(value) for value in weights.values()), 1.0):
        raise ValueError("priority weights must sum to 1.0")
    result["money_significance"] = result["total_kzt_pct"].clip(0, 1)
    result["structural_importance"] = result["structural_score"].clip(0, 1)
    depth_range = float(config["observability"]["boundary_depth"])
    proximity = (1.0 - result["depth"] / depth_range).clip(0, 1)
    reach = (result["seed_ancestor_count"] / float(settings["seed_ancestor_saturation"])).clip(0, 1)
    result["seed_connectivity"] = (0.65 * reach + 0.35 * proximity).clip(0, 1)
    log_imbalance = (np.log1p(result["out_kzt"]) - np.log1p(result["in_kzt"])).abs()
    flow_complete = (~result["is_seed"]) & result["outgoing_observed"]
    imbalance_strength = percentile_strength(log_imbalance.where(flow_complete, 0.0))
    result["anomaly_evidence"] = (0.40 * result["fast_forward_ratio"].fillna(0).clip(0, 1)
                                  + 0.30 * imbalance_strength + 0.30 * result["total_tx_pct"]).clip(0, 1)
    result["priority_score"] = (
        float(weights["role_strength"]) * result["role_score"]
        + float(weights["money_significance"]) * result["money_significance"]
        + float(weights["structural_importance"]) * result["structural_importance"]
        + float(weights["seed_connectivity"]) * result["seed_connectivity"]
        + float(weights["anomaly_evidence"]) * result["anomaly_evidence"]
    ).clip(0, 1).round(6)
    return result


def top_nodes(features: pd.DataFrame, top_n: int) -> pd.DataFrame:
    ordered = features.sort_values(["priority_score", "gid"], ascending=[False, True], kind="mergesort").head(top_n)
    result = ordered[["gid", "role", "priority_score", "evidence"]].copy()
    result.insert(0, "rank", range(1, len(result) + 1))
    return result.rename(columns={"evidence": "why"})
