"""Scientific invariants for real metadata and labelled synthetic edge cases."""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))
from study_matrix import (UNKNOWN, build_domains, country_matrix, country_membership,
                          load_snapshot, country_summary)
from study_query import country_code


def test_distinct_counts_unknowns_and_country_scope():
    """Synthetic fixture: repeated genes/records and a two-country publication."""
    catalogue = pd.DataFrame({"ref_id":["A","B","C"],"source_url":["a","b","c"]})
    evidence = pd.DataFrame([
        ["A","NGA","Nigeria","< 2003","","Upper bound only","None","IN","GenoRx IN"],
        ["A","NGA","Nigeria","< 2003","","Upper bound only","None","IN","GenoRx IN"],
        ["A","ZAF","South Africa","= 2002","2002","Exact year","DTG","IN","Live DTG query"],
        ["B","NGA","Nigeria","= 2004","2004","Exact year","DTG","IN","Live DTG query"],
    ], columns=["ref_id","iso3","country","collection_year_raw","collection_year_exact",
                "collection_year_status","drug_exposure","gene","source"])
    annotations = pd.DataFrame(columns=["ref_id","domain","value","source_url"])
    facts = build_domains(catalogue,evidence,annotations)
    matrix = country_matrix(facts)
    assert matrix.loc[("NGA","Nigeria"),("art_status",UNKNOWN)] == 2
    assert matrix.loc[("NGA","Nigeria"),("drug_exposure","DTG")] == 1
    assert matrix.loc[("ZAF","South Africa"),("drug_exposure","DTG")] == 1
    assert "Before 2003 (bound)" in facts.value.values
    assert "2003" not in facts.value.values
    assert "ART naive" not in facts.value.values
    membership = country_membership(catalogue,evidence)
    assert len(membership) == 4  # A in two countries, B in one, C has no geography.
    assert set(membership.ref_id) == {"A","B","C"}


def test_ambiguous_countries_are_not_guessed():
    assert country_code("Korea")[0] == ""
    assert country_code("Africa")[0] == ""
    assert country_code("Congo-Brazzaville")[0] == "COG"
    assert country_code("Zaire")[0] == "COD"


def test_real_snapshot_conserves_query_and_publication_counts():
    c,e,s,a,m = load_snapshot(ROOT / "content/data/studies")
    assert len(c) == m["catalogue_references"]
    assert e.ref_id.nunique() == m["evidence_references"]
    for q in m["queries"]:
        data = e.loc[e.source.eq(f"Live {q['drug']} query")]
        assert data.ref_id.nunique() == q["totals"]["reference_count"]
        assert pd.to_numeric(data.source_record_count).sum() == q["totals"]["isolates"]
    facts = build_domains(c,e,a)
    assert set(facts.ref_id) == set(c.ref_id)
    assert "Unverified title cue" not in facts.status.values
    assert country_summary(c,e).Publications.max() <= len(c)
    # CALIBRATE trial sites include Dominican Republic, but its selected LEN
    # isolates are US samples. Do not assign those query isolates to all sites.
    assert set(e.loc[e.source.eq("Live LEN query") & e.ref_id.eq("3448"),"iso3"]) == {"USA"}
