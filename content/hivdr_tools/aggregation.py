from __future__ import annotations

import math
import pandas as pd

OUTCOME_COLUMNS = (
    "tdr_overall_pct",
    "tdr_nrti_pct",
    "tdr_nnrti_pct",
    "tdr_pi_pct",
)


def outcome_columns(frame: pd.DataFrame) -> list[str]:
    """Return resistance outcome columns present in a frame."""
    return [c for c in OUTCOME_COLUMNS if c in frame.columns]


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return math.nan
    return float((values[mask] * weights[mask]).sum() / weights[mask].sum())


def weighted_country_summary(study_countries: pd.DataFrame) -> pd.DataFrame:
    """Create country summaries using only rows with defensible country denominators.

    Required columns: iso3, participants, is_single_country.
    TDR percentage columns are optional and summarized when present.
    """
    required = {"iso3", "participants", "is_single_country"}
    missing = required - set(study_countries.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    work = study_countries.copy()
    eligible = work[
        work["is_single_country"].fillna(False)
        & work["iso3"].notna()
        & work["participants"].notna()
        & (work["participants"] > 0)
    ].copy()

    rows: list[dict] = []
    for iso3, group in eligible.groupby("iso3", dropna=False):
        row = {
            "iso3": iso3,
            "country": group["country"].dropna().iloc[0] if group["country"].notna().any() else iso3,
            "n_studies_weighted": int(group["study_id"].nunique()) if "study_id" in group else len(group),
            "n_participants_weighted": int(group["participants"].sum()),
        }
        for col in outcome_columns(group):
            row[col] = _weighted_mean(group[col], group["participants"])
        if "median_sample_year" in group:
            row["sample_year_weighted"] = _weighted_mean(group["median_sample_year"], group["participants"])
        rows.append(row)

    cols = ["iso3", "country", "n_studies_weighted", "n_participants_weighted"] + outcome_columns(eligible)
    if "median_sample_year" in eligible.columns:
        cols.append("sample_year_weighted")
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows).sort_values("iso3").reset_index(drop=True)
