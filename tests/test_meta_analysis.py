"""Independent analytic oracles and input-quality gates for the meta-analysis."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "content"), str(ROOT / "scripts")]
from meta_analysis_tools import reml_meta, study_effects, load_meta_inputs, pool
from build_meta_inputs import reconstruct_count, parse_countries


def test_reml_equal_variance_analytic_oracle():
    # For equal known variances, REML's total variance is the unbiased sample
    # variance, truncated below at the known within-study variance.
    y = np.array([-2.,-1.,0.,1.])
    v = np.full(4,.2)
    r = reml_meta(y,v)
    assert r["tau2"] == pytest.approx(np.var(y,ddof=1)-.2,abs=1e-6)
    assert r["mu_logit"] == pytest.approx(y.mean())
    np.testing.assert_allclose(r["weights"],np.repeat(.25,4))
    shifted = reml_meta(y+2,v)
    assert shifted["tau2"] == pytest.approx(r["tau2"],abs=1e-6)
    assert shifted["mu_logit"] == pytest.approx(r["mu_logit"]+2)


def test_zero_heterogeneity_boundary_and_invalid_variance():
    r = reml_meta(np.array([-1.,-1.,-1.]),np.array([.1,.2,.3]))
    assert r["tau2"] == 0
    assert r["I2_percent"] == 0
    assert r["ci_lower"] < r["pooled"] < r["ci_upper"]
    with pytest.raises(ValueError):
        reml_meta(np.array([1.,2.]),np.array([0.,1.]))


def test_boundary_correction_only_changes_boundary_studies():
    # Labelled synthetic fixture, never used as research data.
    d = pd.DataFrame({"study_id":["zero","middle","all"],"n":[10,10,10],"events_reconstructed":[0,2,10]})
    e = study_effects(d)
    np.testing.assert_allclose(e.logit,[np.log(.5/10.5),np.log(2/8),np.log(10.5/.5)])
    assert e.continuity_corrected.tolist() == [True,False,True]
    with pytest.raises(ValueError):
        study_effects(pd.concat([d,d]))
    with pytest.raises(ValueError):
        study_effects(d.assign(events_reconstructed=[0,2,11]))


def test_rounding_does_not_repair_inconsistent_or_ambiguous_inputs():
    assert reconstruct_count(36,2.8,1,1)[1] == 1
    assert reconstruct_count(45,6.5,0,45)[1] is None
    assert reconstruct_count(2468,6.2,0,2468)[2] == 3
    assert reconstruct_count(100,4.,5,8)[0] == "Count violates mutation-union bounds"
    assert parse_countries("ANGOLA, REPUBLIC OF") == (["AGO"],True)
    assert parse_countries("CAMEROON,SENEGAL,CONGO, THE DEMOCRATIC REPUBIC OF THE") == (["CMR","COD","SEN"],True)
    assert parse_countries("IRAN (ISLAMIC REPUBLIC OF)") == (["IRN"],True)


def test_real_source_eligibility_is_conserved_and_effects_are_finite():
    studies, areas, manifest = load_meta_inputs(ROOT / "content/data/meta_analysis")
    assert len(studies) == sum(manifest["counts"].values()) == 287
    selected = studies.loc[studies.inclusion_reason.eq("Included (conditional)")]
    assert selected.study_id.is_unique
    assert selected.loc[selected.pmid.ne(""),"pmid"].is_unique
    assert set(selected.iso3).issubset(areas.iso3)
    assert "IRN" not in selected.iso3.values
    assert len(selected) == 71 and selected.n.sum() == 6144
    effects,result = pool(selected)
    assert np.isfinite(effects[["logit","variance","weight_pct"]].to_numpy()).all()
    assert effects.weight_pct.sum() == pytest.approx(100)
    assert 0 < result["pi_lower"] <= result["ci_lower"] < result["pooled"] < result["ci_upper"] <= result["pi_upper"] < 1
