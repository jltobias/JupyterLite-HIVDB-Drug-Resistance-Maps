"""Validate new notebook outputs after a clean Jupyter Book execution.

Project: HIV Drug Resistance Maps; Script: validate_study_outputs.py.
Purpose: Cross-check semantic tables and analytical exports against source inputs.
Author: [Repository contributors; generated with Codex]. Email/organization: [Not supplied].
Created/updated: 2026-11-16. Dependencies: Python 3.11+, pandas, NumPy, bs4, SciPy.
Input: content/data snapshots and content/outputs produced by Notebooks 10-12.
Output: docs/study_validation.json when --report is supplied.
Change log: 2026-11-16 - Initial complete-run evidence and output agreement checks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))
from study_matrix import load_snapshot, build_domains, country_matrix, country_summary
from meta_analysis_tools import load_meta_inputs, pool


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    c,e,s,a,m = load_snapshot(ROOT / "content/data/studies")
    facts = build_domains(c,e,a)
    expected_matrix = country_matrix(facts)
    out = ROOT / "content/outputs"
    long = pd.read_csv(out / "study_matrix/domain_evidence_long.csv", dtype=str, keep_default_na=False)
    pd.testing.assert_frame_equal(long, facts)
    table_html = (out / "study_matrix/country_domain_matrix.html").read_text(encoding="utf-8")
    table = BeautifulSoup(table_html,"html.parser").find("table")
    assert table is not None and len(table.select("tbody tr")) == len(expected_matrix)
    assert len(table.select("tbody td")) == expected_matrix.size
    actual_cells = [int(td.get_text(strip=True)) for td in table.select("tbody td")]
    assert actual_cells == expected_matrix.to_numpy().ravel().tolist()
    atlas_summary = pd.read_csv(out / "study_atlas/country_evidence_summary.csv", keep_default_na=False)
    pd.testing.assert_frame_equal(atlas_summary, country_summary(c, e), check_dtype=False)
    globe_html = (out / "study_atlas/evidence_globe.html").read_text(encoding="utf-8")
    assert "Plotly.newPlot" in globe_html and "orthographic" in globe_html
    studies, areas, meta_manifest = load_meta_inputs(ROOT / "content/data/meta_analysis")
    eligible = studies.loc[studies.inclusion_reason.eq("Included (conditional)")]
    effects, result = pool(eligible)
    actual = pd.read_csv(out / "meta_analysis/conditional_study_effects.csv", keep_default_na=False)
    assert actual.study_id.tolist() == effects.study_id.tolist()
    np.testing.assert_allclose(actual[["logit","variance","weight_pct"]], effects[["logit","variance","weight_pct"]],rtol=1e-10)
    summary = pd.read_csv(out / "meta_analysis/conditional_summary.csv")
    assert summary.iloc[0]["Studies"] == len(eligible)
    assert np.isclose(summary.iloc[0]["Typical study TDR (%)"],100*result["pooled"])
    for name in ["forest.html","funnel.html"]:
        html = (out / "meta_analysis" / name).read_text(encoding="utf-8")
        assert "Plotly.newPlot" in html and len(html) > 10000
    inputs = sorted([*ROOT.glob("content/data/studies/*.csv"),*ROOT.glob("content/data/meta_analysis/*.csv"),
                     *ROOT.glob("content/09_*.ipynb"),*ROOT.glob("content/10_*.ipynb"),*ROOT.glob("content/11_*.ipynb"),
                     *ROOT.glob("content/12_*.ipynb"),ROOT/"content/study_matrix.py",ROOT/"content/study_query.py",ROOT/"content/meta_analysis_tools.py"])
    report = {"validated_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,
              "packages":{name:version(name) for name in ["numpy","pandas","scipy","plotly","jupyter-book"]},
              "checks":["Source snapshot hashes", "Distinct-count pivot equals exported evidence",
                        "Every semantic HTML matrix cell equals its computed value", "Study effect/variance/weight exports match the model",
                        "Conditional summary matches the model", "Interactive forest and funnel artifacts exist",
                        "Atlas country summary matches source evidence and interactive globe exists"],
              "catalogue_records":len(c),"matrix_shape":list(expected_matrix.shape),
              "meta_studies":len(eligible),"meta_countries":eligible.iso3.nunique(),
              "conditional_meta_summary":{k:v for k,v in result.items() if k!="weights"},
              "input_sha256":{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              "outputs":"content/outputs/study_matrix, content/outputs/study_atlas, content/outputs/meta_analysis",
              "limitations":["Conditional reconstructed event counts", "No independent cohort-overlap or risk-of-bias adjudication",
                             "Browser visual inspection is recorded separately; this report validates data and HTML structure"]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(f"Validated {expected_matrix.shape} matrix cells and {len(effects)} meta-analysis study effects")


if __name__ == "__main__":
    main()
