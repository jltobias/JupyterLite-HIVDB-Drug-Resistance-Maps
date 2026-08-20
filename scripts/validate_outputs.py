#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

OUTCOMES = ["tdr_overall_pct", "tdr_nrti_pct", "tdr_nnrti_pct", "tdr_pi_pct"]


def validate(data_dir: Path) -> dict:
    studies_path = data_dir / "hivdb_surveillance_studies_2015.csv"
    countries_path = data_dir / "hivdb_study_countries_2015.csv"
    summary_path = data_dir / "hivdb_country_summary_2015.csv"
    for path in (studies_path, countries_path, summary_path):
        if not path.exists():
            raise FileNotFoundError(path)

    studies = pd.read_csv(studies_path)
    countries = pd.read_csv(countries_path)
    summary = pd.read_csv(summary_path)

    assert studies["study_id"].is_unique, "Study IDs must be unique."
    assert (studies["participants"].dropna() > 0).all(), "Participant counts must be positive."
    for frame_name, frame in (("studies", studies), ("summary", summary)):
        for col in OUTCOMES:
            if col in frame:
                bad = frame[col].dropna().loc[lambda s: (s < 0) | (s > 100)]
                assert bad.empty, f"{frame_name}.{col} contains values outside 0-100."
    assert countries.loc[countries["is_single_country"].astype(bool), "study_country_count"].eq(1).all()
    assert summary["iso3"].dropna().str.len().eq(3).all()

    report = {
        "n_studies": int(studies["study_id"].nunique()),
        "n_country_associations": int(len(countries)),
        "n_iso3_countries": int(countries["iso3"].nunique()),
        "n_country_summary_rows": int(len(summary)),
    }
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=Path("content/data"))
    args = ap.parse_args()
    validate(args.data_dir)


if __name__ == "__main__":
    main()
