#!/usr/bin/env python3
"""
Project: JupyterLite HIV Drug Resistance Maps
Script: study_query.py
Purpose: Rebuild a factual study catalogue and country evidence from HIVDB calls.
Author: [Repository contributors; generated with Codex]
Email / Organization: [Not supplied]
Created / Updated: 2026-11-16
Input: Public HIVDB reference catalogue, GenoRx downloads, phenotype references,
       explicit HIV1 group M DTG and LEN queries and their isolate metadata.
Output: content/data/studies/{catalogue,evidence,signals}.csv and manifest.json.
Dependencies: Python 3.11+; requests, pandas, beautifulsoup4, lxml, pycountry.
Notes: Reference IDs are publication records, not independent cohorts. No patient
       identifiers, sequences, article text, or website artwork are published.
       Raw responses stay in an ignored cache. Failures do not fabricate data.
Change log: 2026-11-16 - Initial factual metadata retrieval and provenance audit.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pycountry
import requests
from bs4 import BeautifulSoup

BASE = "https://hivdb.stanford.edu"
API = BASE + "/HIVDB3/api/v1"
ROOT = Path(__file__).resolve().parents[1]
QUERY_FILTERS = {
    "DTG": {"gene": "IN", "num_iis": "0To5", "iis": ["DTG"]},
    "LEN": {"gene": "CA", "num_cais": "0To1", "cais": ["LEN"]},
}
# These are discovery cues, NEVER confirmed primary outcomes or study designs.
SIGNAL_RULES = {
    "age_group": {"Children / adolescents": r"\b(child\w*|pa?ediatric|adolescen\w*|infant\w*|youth\w*)\b", "Adults": r"\badults?\b"},
    "art_status": {"ART naive": r"(?:antiretroviral|art|treatment|drug)[ -](?:na[iï]ve|untreated)", "ART experienced": r"(?:antiretroviral|art|treatment)[ -](?:experienced|treated)|heavily treated"},
    "outcome_topic": {"Mutation": r"\bmutation\w*\b", "Prevalence": r"\bprevalence\b", "Susceptibility": r"\bsusceptibil\w*\b"},
    "clinical_outcome": {"Suppression": r"\bsuppress\w*\b", "Viremia": r"\bvira?emi\w*\b", "Treatment failure": r"\bfail(?:ure|ing|ed)\b"},
    "resistance_outcome": {"Transmitted resistance": r"\btransmitted\b", "Acquired resistance": r"\bacquired\b", "Emergent resistance": r"\bemergen\w*\b"},
    "study_design": {"Cross-sectional": r"cross[ -]sectional", "Longitudinal": r"\blongitudinal\b", "Cohort": r"\bcohort\b", "Randomized trial": r"\brandomi[sz]ed\b", "In vitro": r"\bin vitro\b"},
    "drug_mention": {"DTG": r"\b(dolutegravir|DTG)\b", "LEN": r"\b(lenacapavir|LEN)\b"},
}


class Fetcher:
    """Cache exact read-only calls and record response hashes and versions."""

    def __init__(self, cache: Path, refresh: bool):
        self.cache, self.refresh, self.receipts = cache, refresh, []
        cache.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "HIVDB-study-matrix/1.0 (public metadata research)"

    def get(self, url: str, *, payload: dict | None = None, form: bool = False) -> bytes:
        """Return response bytes; cached replay preserves the original timestamp."""
        request = {"url": url, "method": "GET" if payload is None else "POST", "body": payload, "form": form}
        key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        raw, meta = self.cache / f"{key}.bin", self.cache / f"{key}.json"
        if self.refresh or not (raw.exists() and meta.exists()):
            time.sleep(0.25)  # Sequential calls; avoid burdening the source server.
            kwargs = {} if payload is None else {"data" if form else "json": payload}
            r = self.session.request(request["method"], url, timeout=120, **kwargs)
            r.raise_for_status()
            if r.status_code != 200:
                raise RuntimeError(f"Unexpected asynchronous response {r.status_code}: {url}")
            raw.write_bytes(r.content)
            receipt = {**request, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                       "sha256": hashlib.sha256(r.content).hexdigest(), "bytes": len(r.content),
                       "api_version": r.headers.get("x-api-version"),
                       "database_version": r.headers.get("x-database-version"),
                       "last_modified": r.headers.get("last-modified")}
            meta.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        data = raw.read_bytes()
        receipt = json.loads(meta.read_text(encoding="utf-8"))
        if hashlib.sha256(data).hexdigest() != receipt["sha256"]:
            raise ValueError("Cached response hash mismatch; restore or refresh the cache")
        self.receipts.append(receipt)
        return data


def reference_catalogue(raw: bytes) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse IDs and bibliographic facts; retain only labels from title cue rules."""
    soup = BeautifulSoup(raw, "html.parser")
    catalogue, signals = [], []
    for field in soup.select('input[name="SelectedReference"]'):
        row = field.find_parent("tr")
        cells = row.find_all("td", recursive=False)
        ref = str(field["value"])
        author_year = cells[0].get_text(" ", strip=True)
        title = cells[1].get_text(" ", strip=True)
        year = re.search(r"\((\d{4})\)", author_year)
        link = cells[0].find("a", href=True)
        pmid = parse_qs(urlparse(link["href"]).query).get("list_uids", [""])[0] if link else ""
        catalogue.append({"ref_id": ref, "author_year": author_year,
                          "publication_year": year.group(1) if year else "", "pmid": pmid,
                          "source_url": BASE + f"/cgi-bin/Reference.cgi?SelectedReference={ref}&Submit=Data"})
        for domain, rules in SIGNAL_RULES.items():
            for label, pattern in rules.items():
                if re.search(pattern, title, re.I):
                    signals.append({"ref_id": ref, "domain": domain, "value": label,
                                    "status": "Unverified title cue", "rule": pattern})
    result = pd.DataFrame(catalogue)
    if result.empty or result.ref_id.duplicated().any():
        raise ValueError("Reference catalogue is empty or reference IDs are duplicated")
    return result, pd.DataFrame(signals)


def country_code(raw: str) -> tuple[str, str]:
    """Map exact country labels; retain ambiguous geography without guessing."""
    aliases = {"U.S.": "USA", "U.K.": "GBR", "DRC": "COD", "Zaire": "COD",
               "Dijibouti": "DJI", "Republic Of Georgia": "GEO", "Cote d'Ivoire": "CIV",
               "Tanzania": "TZA", "Russia": "RUS", "Iran": "IRN", "Laos": "LAO",
               "Venezuela": "VEN", "Vietnam": "VNM", "Bolivia": "BOL",
               "Swaziland": "SWZ", "Cape Verde": "CPV", "Burma": "MMR",
               "Turkey": "TUR", "Congo-Brazzaville": "COG"}
    # 'Korea', 'Trinidad', regions and multinational labels remain unmapped.
    if raw in aliases:
        c = pycountry.countries.get(alpha_3=aliases[raw])
    else:
        try:
            c = pycountry.countries.lookup(raw)
        except LookupError:
            return "", f"Unmapped: {raw or 'Not reported'}"
    return c.alpha_3, c.name


def compact(rows: pd.DataFrame, source: str, gene: str, drug_field: str) -> pd.DataFrame:
    """Collapse identical source metadata, retaining a raw record count for audit."""
    keep = rows.rename(columns={"RefID": "ref_id", "Region": "country_raw", "Year": "collection_year_raw", drug_field: "drug_exposure"})
    keys = ["ref_id", "country_raw", "collection_year_raw", "drug_exposure"]
    out = keep[keys].fillna("").astype(str).groupby(keys, dropna=False).size().reset_index(name="source_record_count")
    out["source"], out["gene"] = source, gene
    return out


def query_isolates(fetch: Fetcher, drug: str) -> tuple[pd.DataFrame, dict]:
    """Retrieve every page of a prespecified drug query and check its totals."""
    config = QUERY_FILTERS[drug].copy()
    gene = config.pop("gene")
    filters = {"mutations": [], "no_other_major_mutations": False, "virus": "HIV1",
               "group": "Main", "subtype": "All", "include_filtered": False,
               "include_unpublished": False, "complete_rx_history": False,
               "complete_mutation_list": False, "subtype_data": True, **config}
    pages, page, expected, database_version = [], 1, None, None
    while True:
        raw = fetch.get(API + f"/{gene.lower()}/isolates/search", payload={"filters": filters, "page": page, "page_size": 1000})
        data = json.loads(raw)
        if expected is None:
            expected = data["totals"]
            database_version = fetch.receipts[-1]["database_version"]
        if expected != data["totals"] or database_version != fetch.receipts[-1]["database_version"]:
            raise ValueError("Database changed during pagination; refresh the query")
        pages.extend(data["rows"])
        if page >= data["pages"]:
            break
        page += 1
    rows = pd.DataFrame(pages)
    if rows.IsolateID.duplicated().any() or len(rows) != expected["isolates"] or rows.RefID.nunique() != expected["reference_count"]:
        raise ValueError("Incomplete or duplicated query pages")
    rows["RefID"] = rows.RefID.astype(str)
    return rows, {"drug": drug, "gene": gene, "filters": filters, "totals": expected, "pages": page,
                  "api_version": fetch.receipts[-1]["api_version"], "database_version": database_version}


def sampling_metadata(fetch: Fetcher, rows: pd.DataFrame, gene: str) -> pd.DataFrame:
    """Use the public Isolate Data form once per reference, for selected IDs only.

    The exact (subject, isolate) key is checked before a one-to-one merge. Rows
    from other references cannot leak into a study's country assignments.
    """
    results = []
    for ref, subset in rows.groupby("RefID", sort=True):
        ids = ",".join(subset.IsolateID.astype(str))
        payload = {"SelectedGene": gene, "SelectedSpecies": "HIV1", "SelectedGroup": "M",
                   "SelectedType": "Clinical", "DType": "Genotype", "IsolateIDs": ids,
                   "IsolateIDsOnPage": ids, "NumIsolates": str(len(subset)),
                   "Content": "IsolData", "ADDI_DATA_REQUEST": "VIEW ADDITIONAL DATA"}
        url = BASE + f"/_wrapper/cgi-bin/Reference.cgi?RefID={ref}&Gene={gene}&Species=HIV1&Group=M&Type=Clinical"
        raw = fetch.get(url, payload=payload, form=True)
        tables = pd.read_html(io.StringIO(raw.decode("utf-8", errors="replace")), match="CloneMethod", keep_default_na=False,
                              converters={"Subject": str, "Isolate": str, "Year": str, "Region": str})
        table = tables[0]
        table.columns = [str(c).strip() for c in table.columns]
        table = table.rename(columns={"Subject": "PseudoName", "Isolate": "IsolateName"})
        for column in ["PseudoName", "IsolateName"]:
            table[column] = table[column].astype(str).str.strip().str.rstrip("*")
        # HIVDB suppresses repeated subject labels within its displayed study
        # table. Restore this presentation grouping only, never clinical fields.
        table["PseudoName"] = table.PseudoName.replace("", pd.NA).ffill()
        table["IsolateName"] = table.IsolateName.replace("", pd.NA).ffill()
        # Clone rows repeat one isolate's geography. Collapse only identical
        # metadata; differing years/countries still fail the one-to-one join.
        table = table[["PseudoName", "IsolateName", "Year", "Region"]].drop_duplicates()
        chosen = subset.copy()
        for column in ["PseudoName", "IsolateName"]:
            chosen[column] = chosen[column].astype(str).str.strip().str.rstrip("*")
        joined = chosen.merge(table[["PseudoName", "IsolateName", "Year", "Region"]],
                              on=["PseudoName", "IsolateName"], how="left", validate="one_to_one", indicator=True)
        if not joined._merge.eq("both").all():
            raise ValueError(f"Unmatched sampling metadata for reference {ref}")
        results.append(joined.drop(columns="_merge"))
        print(f"Sampling metadata {gene} RefID={ref}: {len(joined)} isolates", flush=True)
    return pd.concat(results, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "content/data/studies")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "_build/study-source-cache")
    parser.add_argument("--refresh", action="store_true", help="Replace all cached source responses")
    args = parser.parse_args()
    fetch = Fetcher(args.cache_dir, args.refresh)
    catalogue, signals = reference_catalogue(fetch.get(BASE + "/_wrapper/cgi-bin/Reference.cgi"))
    reference_index_count = len(catalogue)
    catalogue["in_current_reference_index"] = True
    # Historical bulk exports contain references absent from today's default
    # index. Preserve them explicitly, using their own reference table.
    rxrefs = pd.read_csv(io.BytesIO(fetch.get(BASE + "/download/GenoRxDatasets/Ref.txt")), sep="\t", dtype=str, keep_default_na=False)
    phenotype = pd.read_csv(io.BytesIO(fetch.get(BASE + "/download/GenoPhenoDatasets/references.txt")), sep="\t", dtype=str, keep_default_na=False)
    extra = []
    seen = set(catalogue.ref_id)
    for frame in [rxrefs, phenotype]:
        for r in frame.to_dict("records"):
            ref = r["RefID"]
            if ref in seen:
                continue
            seen.add(ref)
            year = r.get("RefYear", "")
            extra.append({"ref_id": ref, "author_year": r["Author"] + (f" ({year})" if year else " (year not supplied)"),
                          "publication_year": year, "pmid": r["MedlineID"], "in_current_reference_index": False,
                          "source_url": BASE + f"/cgi-bin/Reference.cgi?SelectedReference={ref}&Submit=Data"})
    catalogue = pd.concat([catalogue, pd.DataFrame(extra)], ignore_index=True)
    catalogue["phenotype_reference"] = catalogue.ref_id.isin(phenotype.RefID)
    evidence, counts, query_reports = [], {}, []
    for gene, drug_field in [("PR", "PIList"), ("RT", "RTIList"), ("IN", "INIList")]:
        raw = fetch.get(BASE + f"/download/GenoRxDatasets/{gene}.txt")
        rows = pd.read_csv(io.BytesIO(raw), sep="\t", usecols=["RefID", "Region", "Year", drug_field], dtype=str, keep_default_na=False)
        counts[gene] = {"records": len(rows), "references": rows.RefID.nunique()}
        evidence.append(compact(rows, f"GenoRx {gene}", gene, drug_field))
        print(f"Downloaded {gene}: {counts[gene]}", flush=True)
    for drug in QUERY_FILTERS:
        rows, report = query_isolates(fetch, drug)
        geo = sampling_metadata(fetch, rows, report["gene"])
        evidence.append(compact(geo, f"Live {drug} query", report["gene"], "IIList" if drug == "DTG" else "CAIList"))
        query_reports.append(report)
    evidence = pd.concat(evidence, ignore_index=True)
    mapped = evidence.country_raw.map(country_code)
    evidence["iso3"] = mapped.map(lambda x: x[0])
    evidence["country"] = mapped.map(lambda x: x[1])
    # A bounded year ('< 2003') never becomes an observed year of collection.
    exact = evidence.collection_year_raw.str.extract(r"^\s*=?\s*(\d{4})\s*$", expand=False)
    evidence["collection_year_exact"] = exact.fillna("")
    evidence["collection_year_status"] = evidence.collection_year_raw.map(
        lambda x: "Upper bound only" if re.match(r"^\s*<\s*\d{4}", x) else "Exact year" if re.fullmatch(r"\s*=?\s*\d{4}\s*", x) else "Not reported / unparsed")
    missing = set(evidence.ref_id) - set(catalogue.ref_id)
    if missing:
        raise ValueError(f"References absent from catalogue: {sorted(missing)}")
    # Raw response text and person/isolate IDs stay in the private local cache.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in [("catalogue", catalogue), ("evidence", evidence), ("signals", signals)]:
        frame.to_csv(args.output_dir / f"{name}.csv", index=False, lineterminator="\n")
    # Public receipts retain query filters, hashes and counts; form patient/isolate
    # identifiers are replaced by a request hash rather than redistributed.
    receipts = []
    for receipt in fetch.receipts:
        clean = receipt.copy()
        if clean["form"]:
            clean["request_body_sha256"] = hashlib.sha256(json.dumps(clean.pop("body"), sort_keys=True).encode()).hexdigest()
        receipts.append(clean)
    manifest = {"built_utc": datetime.now(timezone.utc).isoformat(), "catalogue_references": len(catalogue),
                "reference_index_references": reference_index_count,
                "evidence_references": evidence.ref_id.nunique(), "normalized_evidence_rows": len(evidence),
                "mapped_countries_or_territories": evidence.loc[evidence.iso3.ne(""), "iso3"].nunique(),
                "genorx": counts, "queries": query_reports, "requests": receipts,
                "python": sys.version, "packages": {x: version(x) for x in ["pandas", "requests", "beautifulsoup4", "lxml", "pycountry"]},
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output_dir.glob("*.csv") if p.stem in {"catalogue", "evidence", "signals"}},
                "limitations": ["Catalogue reference IDs are publication records; cohorts can recur across publications.",
                                "Country evidence covers GenoRx PR/RT/IN downloads plus the explicit DTG/LEN query subset, not all HIVDB collections.",
                                "Legacy downloadable datasets and live API queries have different update schedules.",
                                "Title cues are unverified discovery aids; absence is not absence of a study characteristic.",
                                "Facts and computed aggregates only; no papers, abstracts, figures, sequences or website assets are redistributed."]}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k in ["catalogue_references", "evidence_references", "mapped_countries_or_territories"]}, indent=2))


if __name__ == "__main__":
    main()
