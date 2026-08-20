#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))
sys.path.insert(0, str(ROOT / "scripts"))

from hivdr_tools.aggregation import weighted_country_summary  # noqa: E402
from normalization import first_matching_column, key, normalize_country, split_countries  # noqa: E402

SOURCE_DOI = "10.1371/journal.pmed.1001810"
SOURCE_URL = (
    "https://journals.plos.org/plosmedicine/article/file?"
    "type=supplementary&id=info:doi/10.1371/journal.pmed.1001810.s004"
)

COLUMN_PATTERNS = {
    "reference": [r"^reference$", r"reference", r"author"],
    "participants": [r"number.*(participant|individual|sequence)", r"study.*size", r"^n$"],
    "countries": [r"^countries?$", r"country"],
    "recruitment_method": [r"recruit.*method", r"recruitment"],
    "median_sample_year": [r"median.*(sample|sampling).*year", r"sample.*year", r"year"],
    "study_purpose": [r"study.*purpose", r"purpose"],
    "recruitment_site": [r"recruit.*site", r"site"],
    "subtype_distribution": [r"subtype.*distribution", r"subtype"],
    "tdr_overall_pct": [r"overall.*tdr", r"tdr.*overall", r"overall.*resistance"],
    "tdr_nrti_pct": [r"(^| )nrti( |$).*tdr", r"tdr.*(^| )nrti( |$)", r"(^| )nrti( |$).*resistance"],
    "tdr_nnrti_pct": [r"(^| )nnrti( |$).*tdr", r"tdr.*(^| )nnrti( |$)", r"(^| )nnrti( |$).*resistance"],
    "tdr_pi_pct": [r"(^| )pi.*tdr", r"tdr.*(^| )pi", r"protease.*tdr"],
    "cpr_url": [r"cpr.*(analysis|output|url|link)", r"cpr"],
}


def download(url: str, destination: Path) -> str:
    response = requests.get(url, timeout=120, headers={"User-Agent": "hivdr-jupyterlite-teaching/0.1"})
    response.raise_for_status()
    destination.write_bytes(response.content)
    return hashlib.sha256(response.content).hexdigest()


def detect_header(path: Path) -> int:
    preview = pd.read_excel(path, sheet_name=0, header=None, nrows=30)
    best = (0, 0)
    for i, row in preview.iterrows():
        values = " | ".join(key(v) for v in row.tolist() if pd.notna(v))
        score = sum(token in values for token in ("country", "tdr", "participant", "reference"))
        if score > best[1]:
            best = (int(i), score)
    if best[1] < 2:
        raise ValueError("Could not identify the spreadsheet header row confidently.")
    return best[0]


def to_percent(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce")
    nonnull = values.dropna()
    if not nonnull.empty and nonnull.max() <= 1.0:
        values = values * 100.0
    return values


def canonicalize(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    mapping = {}
    for canonical, patterns in COLUMN_PATTERNS.items():
        found = first_matching_column(raw.columns, patterns)
        mapping[canonical] = str(found) if found is not None else None

    required = ["participants", "countries", "tdr_overall_pct"]
    missing = [c for c in required if mapping[c] is None]
    if missing:
        raise ValueError(f"Required source fields were not detected: {missing}. Mapping: {mapping}")

    frame = pd.DataFrame(index=raw.index)
    for canonical, source_name in mapping.items():
        if source_name is not None:
            source_col = next(c for c in raw.columns if str(c) == source_name)
            frame[canonical] = raw[source_col]
        else:
            frame[canonical] = pd.NA

    frame = frame.dropna(how="all").copy()
    frame["participants"] = pd.to_numeric(frame["participants"], errors="coerce")
    frame["median_sample_year"] = pd.to_numeric(frame["median_sample_year"], errors="coerce")
    for col in ("tdr_overall_pct", "tdr_nrti_pct", "tdr_nnrti_pct", "tdr_pi_pct"):
        frame[col] = to_percent(frame[col])
    frame = frame[frame["countries"].notna() & frame["participants"].notna()].copy()
    frame.insert(0, "study_id", [f"RHEE2015-{i:03d}" for i in range(1, len(frame) + 1)])
    return frame.reset_index(drop=True), mapping


def explode_study_countries(studies: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, study in studies.iterrows():
        labels = split_countries(study["countries"])
        count = len(labels)
        for label in labels:
            iso3, canonical_name = normalize_country(label)
            row = study.to_dict()
            row.update(
                {
                    "country_source_raw": label,
                    "country": canonical_name,
                    "iso3": iso3,
                    "study_country_count": count,
                    "is_single_country": count == 1,
                }
            )
            rows.append(row)
    return pd.DataFrame(rows)


def coverage_table(study_countries: pd.DataFrame) -> pd.DataFrame:
    mapped = study_countries[study_countries["iso3"].notna()].copy()
    if mapped.empty:
        return pd.DataFrame(columns=["iso3", "country", "n_studies_total", "n_studies_single_country"])
    total = mapped.groupby(["iso3", "country"], as_index=False).agg(
        n_studies_total=("study_id", "nunique"),
        n_participants_study_rows=("participants", "sum"),
    )
    singles = (
        mapped[mapped["is_single_country"]]
        .groupby("iso3", as_index=False)
        .agg(n_studies_single_country=("study_id", "nunique"))
    )
    out = total.merge(singles, on="iso3", how="left")
    out["n_studies_single_country"] = out["n_studies_single_country"].fillna(0).astype(int)
    out["has_weighted_estimate"] = out["n_studies_single_country"] > 0
    return out.sort_values("iso3").reset_index(drop=True)


def run(source_url: str, output_dir: Path, keep_xlsx: bool = False) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    xlsx = output_dir / "rhee2015_s1_table.xlsx"
    sha256 = download(source_url, xlsx)
    header_row = detect_header(xlsx)
    raw = pd.read_excel(xlsx, sheet_name=0, header=header_row)
    studies, mapping = canonicalize(raw)
    study_countries = explode_study_countries(studies)
    coverage = coverage_table(study_countries)
    summary = weighted_country_summary(study_countries)
    summary = coverage.merge(summary, on=["iso3", "country"], how="left")

    studies.to_csv(output_dir / "hivdb_surveillance_studies_2015.csv", index=False)
    study_countries.to_csv(output_dir / "hivdb_study_countries_2015.csv", index=False)
    coverage.to_csv(output_dir / "hivdb_country_coverage_2015.csv", index=False)
    summary.to_csv(output_dir / "hivdb_country_summary_2015.csv", index=False)

    unmatched = sorted(study_countries.loc[study_countries["iso3"].isna(), "country_source_raw"].dropna().unique().tolist())
    metadata = {
        "source": "PLOS Medicine S1 Table associated with Stanford HIVDB surveillance analysis",
        "doi": SOURCE_DOI,
        "source_url": source_url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256,
        "header_row_zero_based": header_row,
        "source_column_mapping": mapping,
        "n_studies": int(studies["study_id"].nunique()),
        "n_country_associations": int(len(study_countries)),
        "n_iso3_countries": int(study_countries["iso3"].nunique()),
        "n_weighted_countries": int(summary["n_studies_weighted"].fillna(0).gt(0).sum()) if "n_studies_weighted" in summary else 0,
        "unmatched_country_labels": unmatched,
        "aggregation_note": "Weighted prevalence uses single-country studies only unless country-specific denominators are available.",
    }
    (output_dir / "hivdb_2015_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if not keep_xlsx:
        xlsx.unlink(missing_ok=True)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "content" / "data")
    parser.add_argument("--keep-xlsx", action="store_true")
    args = parser.parse_args()
    metadata = run(args.source_url, args.output_dir, args.keep_xlsx)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
