"""Concise, cautious and numeric evidence strings."""

import pandas as pd


def _money(value: float) -> str:
    value = float(value)
    if value >= 1_000_000:
        return f"KZT{value / 1_000_000:.1f}m"
    if value >= 1_000:
        return f"KZT{value / 1_000:.0f}k"
    return f"KZT{value:.0f}"


def _row_evidence(row: pd.Series) -> str:
    if row["truncated_by_depth"]:
        return f"Depth 4 boundary: {_money(row.in_kzt)} from {row.in_deg} senders; downstream activity is unobserved, so no terminal conclusion."
    if row["role"] == "coordinator":
        caveat = " Seed inflow incomplete." if row["is_seed"] else ""
        return f"Coordination signs: {row.in_deg} senders, {row.out_deg} recipients, {_money(row.in_kzt)} in/{_money(row.out_kzt)} out; structural {row.structural_score:.2f}.{caveat}"
    if row["role"] == "distributor":
        caveat = " Seed inflow incomplete." if row["is_seed"] else ""
        return f"Distribution signs: {row.out_deg} recipients, {_money(row.out_kzt)} out in {row.out_tx} tx; investigation hypothesis.{caveat}"
    if row["role"] == "consolidator":
        return f"Consolidation signs: {row.in_deg} senders, {_money(row.in_kzt)} in, {row.out_deg} recipients; investigation hypothesis."
    if row["role"] == "transit":
        return f"Pass-through signs: {row.pass_through:.0%} sent onward; {row.fast_forward_ratio:.0%} outgoing value within 0-2 days; hypothesis only."
    if row["role"] == "terminal":
        return f"Observed depth {row.depth}: {_money(row.retained_kzt)} retained ({row.retained_share:.0%}) with {row.out_deg} recipients; terminal-behavior hypothesis."
    if row["is_seed"]:
        return f"Seed: {row.out_deg} recipients and {_money(row.out_kzt)} observed out; incoming flow is incomplete; investigation hypothesis only."
    return f"Peripheral pattern: {row.in_deg} senders, {row.out_deg} recipients, {_money(row.total_kzt)} observed flow; no stronger rule matched."


def add_evidence(features: pd.DataFrame) -> pd.DataFrame:
    result = features.copy()
    result["evidence"] = result.apply(_row_evidence, axis=1)
    too_long = result["evidence"].str.len() >= 200
    if too_long.any():
        raise ValueError(f"evidence exceeds 199 characters for {int(too_long.sum())} nodes")
    return result
