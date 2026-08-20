#!/usr/bin/env python3
"""Import a documented current HIVDB surveillance export.

This script intentionally requires an explicit source URL. The current surveillance
map's machine-readable endpoint is not hard-coded because a stable documented URL
was not identified when this repository was prepared.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))
sys.path.insert(0, str(ROOT / "scripts"))

from hivdr_tools.aggregation import weighted_country_summary  # noqa: E402
from normalization import first_matching_column, normalize_country, split_countries  # noqa: E402
from fetch_plos_2015 import COLUMN_PATTERNS, canonicalize, coverage_table, explode_study_countries  # noqa: E402


def read_remote_table(url: str) -> tuple[pd.DataFrame, bytes, str]:
    r = requests.get(url, timeout=120, headers={"User-Agent": "hivdr-jupyterlite-teaching/0.1"})
    r.raise_for_status()
    payload = r.content
    ctype = r.headers.get("content-type", "").lower()
    path = urlparse(url).path.lower()
    if path.endswith((".xlsx", ".xls")) or "spreadsheet" in ctype or "excel" in ctype:
        return pd.read_excel(io.BytesIO(payload)), payload, "excel"
    if path.endswith(".csv") or "csv" in ctype:
        return pd.read_csv(io.BytesIO(payload)), payload, "csv"
    if path.endswith(".json") or "json" in ctype:
        obj = r.json()
        if isinstance(obj, dict):
            for key in ("data", "records", "studies", "results"):
                if isinstance(obj.get(key), list):
                    obj = obj[key]
                    break
        if not isinstance(obj, list):
            raise ValueError("JSON source did not contain a top-level record list or recognized list field.")
        return pd.json_normalize(obj), payload, "json"
    try:
        return pd.read_csv(io.BytesIO(payload)), payload, "csv-sniffed"
    except Exception as exc:
        raise ValueError("Unsupported source. Use a direct CSV, JSON, XLS, or XLSX export URL.") from exc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-url", required=True, help="Official/current machine-readable HIVDB surveillance export URL")
    ap.add_argument("--output-dir", type=Path, default=ROOT / "content" / "data" / "current")
    args = ap.parse_args()

    raw, payload, kind = read_remote_table(args.source_url)
    studies, mapping = canonicalize(raw)
    studies["study_id"] = [f"CURRENT-{i:05d}" for i in range(1, len(studies) + 1)]
    study_countries = explode_study_countries(studies)
    coverage = coverage_table(study_countries)
    summary = coverage.merge(weighted_country_summary(study_countries), on=["iso3", "country"], how="left")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    studies.to_csv(args.output_dir / "hivdb_surveillance_studies_current.csv", index=False)
    study_countries.to_csv(args.output_dir / "hivdb_study_countries_current.csv", index=False)
    summary.to_csv(args.output_dir / "hivdb_country_summary_current.csv", index=False)
    metadata = {
        "source_url": args.source_url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source_kind": kind,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "source_column_mapping": mapping,
        "n_studies": int(studies["study_id"].nunique()),
        "n_iso3_countries": int(study_countries["iso3"].nunique()),
        "unmatched_country_labels": sorted(study_countries.loc[study_countries["iso3"].isna(), "country_source_raw"].dropna().unique().tolist()),
    }
    (args.output_dir / "hivdb_current_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
