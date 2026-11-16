#!/usr/bin/env python3
"""
Project: JupyterLite HIV Drug Resistance Maps
Script: build_meta_inputs.py
Purpose: Preserve original S1 study identifiers and create an audited Africa input.
Author: [Repository contributors; generated with Codex]
Email / Organization: [Not supplied]
Created / Updated: 2026-11-16
Input: Rhee et al. 2015 CC0 S1 XLSX; UN M49 geographic facts; study catalogue.
Output: content/data/meta_analysis/*.csv and source_manifest.json.
Dependencies: Python 3.11+, pandas, openpyxl, requests, lxml, beautifulsoup4, pycountry.
Notes: Percentages are rounded to 0.1 percentage point. Event counts are explicitly
       RECONSTRUCTED conditional on the reported N being the correct denominator.
       Inconsistent or ambiguous counts are not rounded into eligibility.
Change log: 2026-11-16 - Initial source-preserving extraction and geographic audit.
"""
from __future__ import annotations
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))
from study_query import Fetcher, country_code

S1_URL = "https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=info:doi/10.1371/journal.pmed.1001810.s004"
M49_URL = "https://unstats.un.org/unsd/methodology/m49/"


def african_areas(raw: bytes) -> pd.DataFrame:
    """Read the English M49 geographic hierarchy, retaining countries AND areas."""
    tables = pd.read_html(io.StringIO(raw.decode("utf-8")))
    table = next(t for t in tables if "Other groupings" in t.columns and "Africa" in t["Country or Area"].values)
    active, subregion, records = False, "", []
    for r in table.to_dict("records"):
        name, iso = r["Country or Area"], r["ISO-alpha3 code"]
        if name == "Africa":
            active = True
            continue
        if active and name == "Americas":
            break
        if not active:
            continue
        if pd.isna(iso):
            if name != "Sub-Saharan Africa":
                subregion = name
        else:
            records.append({"iso3": iso, "country_area": name, "subregion": subregion})
    frame = pd.DataFrame(records)
    if frame.empty or frame.iso3.duplicated().any() or set(frame.subregion) != {"Northern Africa","Eastern Africa","Middle Africa","Southern Africa","Western Africa"}:
        raise ValueError("Unexpected M49 hierarchy")
    return frame


def parse_countries(raw: str) -> tuple[list[str], bool]:
    """Resolve protected historical names before treating commas as separators."""
    aliases = {
        "CONGO, THE DEMOCRATIC REPUBIC OF THE": "COD",
        "CONGO, THE DEMOCRATIC REPUBLIC OF THE": "COD",
        "ANGOLA, REPUBLIC OF": "AGO", "TANZANIA, UNITED REPUBLIC OF": "TZA",
        "MADAGASCAR, REPUBLIC OF": "MDG",
        "KOREA, REPUBLIC OF": "KOR", "MOLDOVA, REPUBLIC OF": "MDA",
        "COTE D'IVOIRE": "CIV", "SWAZILAND": "SWZ", "ZAIRE": "COD",
        "CONGO": "COG", "IRAN (ISLAMIC REPUBLIC OF)": "IRN",
    }
    value = str(raw).strip().upper()
    for old, new in sorted(aliases.items(), key=lambda x: -len(x[0])):
        value = value.replace(old, new)
    codes, complete = [], True
    for part in value.split(","):
        iso, _ = country_code(part.strip())
        if iso:
            codes.append(iso)
        else:
            complete = False
    return sorted(set(codes)), complete


def reconstruct_count(n: int, percent: float, lower: int, upper: int) -> tuple[str, int | None, int]:
    """Find integer counts compatible with the reported one-decimal percentage.

    A conservative closed interval includes ties at either rounding boundary.
    Mutation marginals constrain the union, but are NEVER added as people.
    """
    candidates = [x for x in range(n + 1) if abs(100 * x / n - percent) <= 0.05 + 1e-10]
    if len(candidates) != 1:
        return ("Inconsistent denominator / percentage" if not candidates else "Ambiguous rounded count", None, len(candidates))
    x = candidates[0]
    if not lower <= x <= upper:
        return "Count violates mutation-union bounds", None, 1
    return "Unique rounding-compatible count (conditional)", x, 1


def main() -> None:
    fetch = Fetcher(ROOT / "_build/meta-source-cache", refresh="--refresh" in sys.argv)
    areas = african_areas(fetch.get(M49_URL))
    african = set(areas.iso3)
    raw = fetch.get(S1_URL)
    source = pd.read_excel(io.BytesIO(raw), dtype={"MedlineID": str})
    if len(source) != 287 or source.StudyID.duplicated().any():
        raise ValueError("S1 table no longer has the expected unique 287 study rows")
    catalogue = pd.read_csv(ROOT / "content/data/studies/catalogue.csv", dtype=str, keep_default_na=False)
    pmids = catalogue.loc[catalogue.pmid.ne("")].groupby("pmid").ref_id.agg(lambda x: "|".join(sorted(set(x))))
    # Marginals bound the union of persons with any SDRM. Summing them would
    # double-count persons with several mutations and is not an overall numerator.
    mutation_cols = [c for c in source.columns if re.fullmatch(r"[A-Z]\d+(?:[A-Z]|i)", c)]
    records = []
    for r in source.to_dict("records"):
        codes, geo_complete = parse_countries(r["Country"])
        n, pct = int(r["Number of Individuals (Sequences)"]), float(r["Overall-TDR (%)"])
        marginal = [int(r[c]) for c in mutation_cols]
        lo, hi = max(marginal), min(n, sum(marginal))
        status, count, n_candidates = reconstruct_count(n, pct, lo, hi)
        pmid = "" if pd.isna(r["MedlineID"]) else str(r["MedlineID"])
        iso = codes[0] if geo_complete and len(codes) == 1 else ""
        in_africa = bool(codes) and geo_complete and set(codes).issubset(african)
        # First applicable reason is used in the reproducible exclusion flow.
        reason = "Included (conditional)"
        if not in_africa:
            reason = "Outside Africa / unresolved or mixed geography"
        elif not iso:
            reason = "Multicountry: country denominators unavailable"
        elif count is None:
            reason = status
        records.append({
            "study_id": f"RHEE2015-{int(r['StudyID']):03d}", "source_study_id": int(r["StudyID"]),
            "study_label": r["StudyName"], "author": r["Author"], "publication_year": r["Year of Publication"],
            "pmid": pmid, "matrix_ref_ids": pmids.get(pmid, "") if pmid else "",
            "countries_raw": r["Country"], "country_isos": "|".join(codes), "iso3": iso,
            "geography_complete": geo_complete, "wholly_in_africa": in_africa,
            "source_region_label": r["Region"], "median_sample_year": r["Median Sample Year"],
            "n": n, "overall_tdr_pct_reported": pct, "events_reconstructed": count,
            "count_status": status, "candidate_count": n_candidates,
            "mutation_union_lower": lo, "mutation_union_upper": hi,
            "sampling_method": r["Sampling-Method"], "recruitment_site": r["Site-Type (Risk-group)"],
            "study_purpose": r["Study-Purpose"], "urban_rural": r["Urban vs Rural"],
            "inclusion_reason": reason, "cpr_url": r["CPR Analysis"],
            "source_url": "https://doi.org/10.1371/journal.pmed.1001810.s004"})
    studies = pd.DataFrame(records)
    included = studies.loc[studies.inclusion_reason.eq("Included (conditional)")]
    if included.loc[included.pmid.ne(""), "pmid"].duplicated().any():
        raise ValueError("Repeated publication among eligible rows: reconcile cohort independence before pooling")
    out = ROOT / "content/data/meta_analysis"
    out.mkdir(parents=True, exist_ok=True)
    studies.to_csv(out / "harmonized_studies.csv", index=False, lineterminator="\n")
    areas.to_csv(out / "africa_country_areas.csv", index=False, lineterminator="\n")
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "requests": fetch.receipts,
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("*.csv")},
                "counts": studies.inclusion_reason.value_counts().to_dict(),
                "notes": ["Counts are conditionally reconstructed from rounded percentages, not exact numerators reported by the study.",
                          "Original CPR reports were unreachable during preparation (HTTPS handshake failure; HTTP timeout).",
                          "M49 country/area membership overrides source region labels; Iran is not Africa despite S1's regional label.",
                          "Primary analysis excludes multicountry rows without country-specific denominators.",
                          "No independent risk-of-bias or cross-publication cohort-overlap adjudication has been completed."]}
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))
    print("Included:", len(included), "studies;", included.iso3.nunique(), "countries; N =", included.n.sum())


if __name__ == "__main__":
    main()
