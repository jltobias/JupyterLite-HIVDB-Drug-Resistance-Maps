"""
Project: JupyterLite HIV Drug Resistance Maps
Script: study_matrix.py
Purpose: Build auditable publication-country matrices across eight study domains.
Author: [Repository contributors; generated with Codex]
Email / Organization: [Not supplied]
Created / Updated: 2026-11-16
Input: data/studies/{catalogue,evidence,signals,annotations}.csv and manifest.json.
Output: pandas tables; notebooks export CSV/semantic HTML and Plotly figures.
Dependencies: Python 3.11+; pandas (tested 2.3.3), standard library.
Notes: Descriptive inventory, not a population sample or meta-analysis. RefID is
       a publication record; repeated cohorts are not resolved. Count distinct
       refs per country/category. Multi-country and multi-category totals overlap.
       Unknown fields remain explicit. No imputation or prevalence estimation.
Change log: 2026-11-16 - Initial matrix pipeline with evidence-status separation.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

DOMAINS = {
    "age_group": "1a. Population: age group",
    "art_status": "1b. Population: ART status at baseline",
    "geography": "2. Geography of sampled isolates",
    "primary_outcome": "3. Primary outcome",
    "drug_exposure": "4. Recorded drug exposure",
    "clinical_outcome": "5. Clinical outcome / eligibility",
    "collection_year": "6. Year of data collection",
    "resistance_outcome": "7. Resistance outcome",
    "study_design": "8. Study / sampling design",
}
UNKNOWN = "Not reported in selected sources"


def load_snapshot(folder: str | Path = "data/studies") -> tuple:
    """Read the shipped factual snapshot and verify its generated hashes."""
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["outputs_sha256"].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Snapshot hash mismatch: {name}; rerun retrieval or restore the file")
    tables = [pd.read_csv(folder / f"{name}.csv", dtype=str, keep_default_na=False)
              for name in ["catalogue", "evidence", "signals", "annotations"]]
    catalogue, evidence, _, annotations = tables
    if catalogue.ref_id.duplicated().any() or not set(evidence.ref_id).issubset(catalogue.ref_id):
        raise ValueError("Catalogue reference IDs are not a valid unique parent key")
    if not set(annotations.ref_id).issubset(catalogue.ref_id):
        raise ValueError("Annotation references are absent from this catalogue snapshot")
    return (*tables, manifest)


def country_membership(catalogue: pd.DataFrame, evidence: pd.DataFrame) -> pd.DataFrame:
    """Return distinct reference-country rows, including explicit unmapped rows.

    A publication without selected-source geography is retained. Multi-country
    publications occur in each evidenced country, once per country.
    """
    membership = evidence[["ref_id", "iso3", "country"]].drop_duplicates()
    missing = catalogue.loc[~catalogue.ref_id.isin(membership.ref_id), ["ref_id"]].copy()
    missing["iso3"], missing["country"] = "", "No geography in selected sources"
    result = pd.concat([membership, missing], ignore_index=True)
    return result.merge(catalogue, on="ref_id", how="left", validate="many_to_one")


def build_domains(catalogue: pd.DataFrame, evidence: pd.DataFrame, annotations: pd.DataFrame) -> pd.DataFrame:
    """Construct long-form country/domain facts with field-level provenance.

    Bibliographic annotations describe the publication, not country-specific
    estimates. Drug/year facts retain their actual source-country scope.
    No title cue is promoted into this source-supported domain table.
    """
    membership = country_membership(catalogue, evidence)
    rows = []
    for r in membership.itertuples(index=False):
        geo = r.country if r.iso3 else UNKNOWN
        rows.append((r.ref_id, r.iso3, r.country, "geography", geo, "Source metadata", r.source_url))
    for r in evidence.itertuples(index=False):
        if r.collection_year_exact:
            value = r.collection_year_exact
        elif r.collection_year_status == "Upper bound only":
            value = f"Before {re.search(r'[0-9]{4}', r.collection_year_raw).group(0)} (bound)"
        else:
            value = UNKNOWN
        rows.append((r.ref_id, r.iso3, r.country, "collection_year", value, "Source metadata", r.source))
        # Gene-specific drug-class naivety does not establish overall ART naivety.
        for drug in re.split(r"\s*,\s*", r.drug_exposure):
            if drug in {"", "Unknown"}:
                continue
            if drug == "None":
                drug = f"No {r.gene}-class inhibitor recorded"
            rows.append((r.ref_id, r.iso3, r.country, "drug_exposure", drug, "Source metadata", r.source))
    for a in annotations.itertuples(index=False):
        if a.domain not in DOMAINS:
            continue  # Outcome-focus fields remain available in the annotation audit.
        for r in membership.loc[membership.ref_id.eq(a.ref_id)].itertuples(index=False):
            rows.append((r.ref_id, r.iso3, r.country, a.domain, a.value, "Source-checked annotation", a.source_url))
    cols = ["ref_id", "iso3", "country", "domain", "value", "status", "source"]
    facts = pd.DataFrame(rows, columns=cols).drop_duplicates()
    # Generate explicit unknowns independently for each reference-country-domain.
    full = membership[["ref_id", "iso3", "country"]].merge(pd.DataFrame({"domain": list(DOMAINS)}), how="cross")
    known_keys = facts[["ref_id", "iso3", "country", "domain"]].drop_duplicates()
    absent = full.merge(known_keys, how="left", indicator=True).query('_merge == "left_only"').drop(columns="_merge")
    absent["value"], absent["status"], absent["source"] = UNKNOWN, "Missing", "Selected sources do not supply this field"
    facts = pd.concat([facts, absent], ignore_index=True)
    # Keep partial missingness when one isolate has a year and another does not.
    return facts.drop_duplicates().sort_values(["country", "ref_id", "domain", "value"]).reset_index(drop=True)


def country_matrix(facts: pd.DataFrame, domains: list[str] | None = None, *, mapped_only: bool = False) -> pd.DataFrame:
    """Count distinct publication IDs per country/domain/value, not source rows."""
    data = facts.copy()
    if domains is not None:
        data = data.loc[data.domain.isin(domains)]
    if mapped_only:
        data = data.loc[data.iso3.ne("")]
    return data.pivot_table(index=["iso3", "country"], columns=["domain", "value"], values="ref_id",
                            aggfunc="nunique", fill_value=0).astype(int).sort_index()


def coverage_table(facts: pd.DataFrame, catalogue: pd.DataFrame) -> pd.DataFrame:
    """Summarize whether each publication has any information for each domain."""
    supported = facts.loc[facts.value.ne(UNKNOWN)].groupby("domain").ref_id.nunique()
    return pd.DataFrame({"Domain": list(DOMAINS.values()),
                         "With information": [int(supported.get(d, 0)) for d in DOMAINS],
                         "Not reported": [len(catalogue) - int(supported.get(d, 0)) for d in DOMAINS]})


def country_summary(catalogue: pd.DataFrame, evidence: pd.DataFrame) -> pd.DataFrame:
    """Summarize mapped countries; query membership requires that geography."""
    membership = country_membership(catalogue, evidence)
    mapped = membership.loc[membership.iso3.ne("")]
    result = mapped.groupby(["iso3", "country"]).ref_id.nunique().rename("Publications").to_frame()
    for drug in ["DTG", "LEN"]:
        selected = evidence.loc[evidence.source.eq(f"Live {drug} query") & evidence.iso3.ne("")]
        result[f"{drug} query publications"] = selected.groupby(["iso3", "country"]).ref_id.nunique()
    exact = evidence.loc[evidence.collection_year_exact.ne("") & evidence.iso3.ne("")]
    result["Publications with exact sample year"] = exact.groupby(["iso3", "country"]).ref_id.nunique()
    return result.fillna(0).astype(int).reset_index()


def evidence_ledger(catalogue: pd.DataFrame, evidence: pd.DataFrame, annotations: pd.DataFrame) -> pd.DataFrame:
    """Create one readable audit row per publication and evidenced geography."""
    facts = build_domains(catalogue, evidence, annotations)
    wide = facts.groupby(["ref_id", "iso3", "country", "domain"]).value.agg(lambda x: " | ".join(sorted(set(x))))
    wide = wide.unstack("domain").reset_index()
    return wide.merge(catalogue[["ref_id", "author_year", "publication_year", "pmid", "source_url"]], on="ref_id", validate="many_to_one")
