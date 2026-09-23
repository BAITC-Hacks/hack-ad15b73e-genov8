"""Explainable threshold-based primary role assignment."""

import numpy as np
import pandas as pd


ALLOWED_ROLES = {"coordinator", "distributor", "consolidator", "transit", "terminal", "peripheral"}


def _ratio_strength(values: pd.Series, threshold: float) -> pd.Series:
    return (values.astype(float) / float(threshold)).clip(0, 1)


def assign_roles(features: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Assign one role in precedence order, respecting data observability."""
    result = features.copy()
    role = pd.Series("peripheral", index=result.index, dtype="object")
    score = pd.Series(np.nan, index=result.index, dtype=float)
    available = pd.Series(True, index=result.index)
    observed = result["outgoing_observed"]

    cfg = config["coordinator"]
    regular = ((~result["is_seed"]) & observed & (result["in_deg"] > 0) & (result["out_deg"] > 0)
               & (((result["in_deg"] >= cfg["min_in_degree"]) & (result["out_deg"] >= cfg["min_out_degree"]))
                  | ((result["total_degree"] >= cfg["min_total_degree"]) & (result["structural_score"] >= cfg["min_structural_score"]))))
    seed = (result["is_seed"] & (result["out_deg"] >= cfg["seed_min_out_degree"])
            & (result["structural_score"] >= cfg["min_structural_score"]))
    mask = available & (regular | seed)
    role.loc[mask] = "coordinator"
    regular_score = (0.30 * _ratio_strength(result["in_deg"], cfg["min_in_degree"])
                     + 0.30 * _ratio_strength(result["out_deg"], cfg["min_out_degree"])
                     + 0.40 * _ratio_strength(result["structural_score"], cfg["min_structural_score"]))
    seed_score = (0.55 * _ratio_strength(result["out_deg"], cfg["seed_min_out_degree"])
                  + 0.45 * _ratio_strength(result["structural_score"], cfg["min_structural_score"]))
    score.loc[mask] = np.where(result.loc[mask, "is_seed"], seed_score[mask], regular_score[mask])
    available &= ~mask

    cfg = config["distributor"]
    mask = available & observed & (result["out_deg"] >= cfg["min_out_degree"])
    role.loc[mask] = "distributor"
    score.loc[mask] = (0.70 * _ratio_strength(result["out_deg"], cfg["min_out_degree"]) + 0.30 * result["out_kzt_pct"])[mask]
    available &= ~mask

    cfg = config["consolidator"]
    mask = (available & observed & (~result["is_seed"]) & (result["in_deg"] >= cfg["min_in_degree"])
            & (result["out_deg"] <= cfg["max_out_degree"]) & (result["in_kzt"] >= cfg["min_incoming_kzt"]))
    role.loc[mask] = "consolidator"
    concentration = (1.0 - result["out_deg"] / (cfg["max_out_degree"] + 1.0)).clip(0, 1)
    score.loc[mask] = (0.50 * _ratio_strength(result["in_deg"], cfg["min_in_degree"])
                       + 0.30 * result["in_kzt_pct"] + 0.20 * concentration)[mask]
    available &= ~mask

    cfg = config["transit"]
    mask = (available & observed & (~result["is_seed"]) & (result["in_deg"] > 0) & (result["out_deg"] > 0)
            & result["pass_through"].between(cfg["min_pass_through_ratio"], cfg["max_pass_through_ratio"], inclusive="both")
            & (result["fast_forward_ratio"] >= cfg["min_fast_forward_ratio"]))
    role.loc[mask] = "transit"
    pass_width = max(1.0 - cfg["min_pass_through_ratio"], cfg["max_pass_through_ratio"] - 1.0)
    pass_match = (1.0 - (result["pass_through"] - 1.0).abs() / pass_width).clip(0, 1)
    flow_strength = pd.concat([result["in_kzt_pct"], result["out_kzt_pct"]], axis=1).min(axis=1)
    score.loc[mask] = (0.45 * pass_match + 0.35 * result["fast_forward_ratio"] + 0.20 * flow_strength)[mask]
    available &= ~mask

    cfg = config["terminal"]
    mask = (available & observed & (~result["is_seed"]) & (result["in_kzt"] >= cfg["min_incoming_kzt"])
            & (result["retained_kzt"] >= cfg["min_retained_kzt"]) & (result["retained_share"] >= cfg["min_retained_share"])
            & (result["out_deg"] <= cfg["max_out_degree"]))
    role.loc[mask] = "terminal"
    score.loc[mask] = (0.50 * result["retained_kzt_pct"] + 0.30 * result["retained_share"].fillna(0).clip(0, 1) + 0.20 * result["in_kzt_pct"])[mask]
    available &= ~mask

    activity = pd.concat([result["total_degree_pct"], result["total_kzt_pct"]], axis=1).max(axis=1)
    fallback = (0.25 + 0.50 * (1.0 - activity)).clip(0.25, 0.75)
    fallback.loc[result["truncated_by_depth"]] = fallback.loc[result["truncated_by_depth"]].clip(upper=0.35)
    fallback.loc[result["is_seed"]] = fallback.loc[result["is_seed"]].clip(upper=0.40)
    score.loc[available] = fallback[available]
    result["role"], result["role_score"] = role, score.clip(0, 1).round(6)
    return result
