"""
Project: JupyterLite HIV Drug Resistance Maps
Script: meta_analysis_tools.py
Purpose: Exploratory random-effects synthesis of compatible single-arm TDR data.
Author: [Repository contributors; generated with Codex]
Email / Organization: [Not supplied]
Created / Updated: 2026-11-16
Input: Audited independent study rows: n and events_reconstructed (conditional).
Output: Study logit effects, REML heterogeneity, modified HKSJ intervals,
        prediction interval, weights, Q and I-squared; no national estimates.
Dependencies: Python 3.11+, NumPy, pandas, SciPy >=1.14 (tested 1.18.1).
Notes: Independent normal study logits with known approximate binomial sampling
       variances. Boundary proportions receive a specified continuity correction.
       Between-publication cohort independence remains an exploratory assumption.
       The inverse-logit mean is a typical study proportion, not a population
       prevalence or the arithmetic mean of the logistic-normal distribution.
Change log: 2026-11-16 - Initial REML model with analytic-oracle validation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import expit
from scipy.stats import chi2, norm, t


def load_meta_inputs(folder: str | Path = "data/meta_analysis") -> tuple:
    """Load dated source extractions only if their recorded hashes still match."""
    folder = Path(folder)
    manifest = json.loads((folder / "source_manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["outputs_sha256"].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Meta-analysis input hash mismatch: {name}")
    studies = pd.read_csv(folder / "harmonized_studies.csv", dtype={"pmid": str, "matrix_ref_ids": str}, keep_default_na=False)
    areas = pd.read_csv(folder / "africa_country_areas.csv", keep_default_na=False)
    return studies, areas, manifest


def study_effects(studies: pd.DataFrame, correction: float = 0.5) -> pd.DataFrame:
    """Calculate logits and approximate variances from audited integer counts.

    Parameters
    ----------
    studies : DataFrame
        One independent effect per study, with study_id, n, events_reconstructed.
    correction : float
        Add to both cells ONLY for zero-event or all-event studies.
    """
    if not 0 < correction <= 1:
        raise ValueError("Use a declared positive correction no larger than 1")
    if studies.study_id.duplicated().any():
        raise ValueError("Repeated study effects cannot be treated as independent")
    n = pd.to_numeric(studies.n, errors="raise").to_numpy(dtype=float)
    x = pd.to_numeric(studies.events_reconstructed, errors="raise").to_numpy(dtype=float)
    if not (np.isfinite(n).all() and np.isfinite(x).all() and (n > 0).all()
            and (x >= 0).all() and (x <= n).all() and (n == np.floor(n)).all() and (x == np.floor(x)).all()):
        raise ValueError("Counts must be finite integers with 0 <= events <= n and n > 0")
    cc = np.where((x == 0) | (x == n), correction, 0.0)
    out = studies.copy()
    out["proportion_reconstructed"] = x / n
    out["continuity_corrected"] = cc > 0
    out["logit"] = np.log((x + cc) / (n - x + cc))
    out["variance"] = 1 / (x + cc) + 1 / (n - x + cc)
    out["se"] = np.sqrt(out.variance)
    # Study-level logit-normal intervals match the effects used in pooling.
    out["study_lower"] = expit(out.logit - norm.ppf(.975) * out.se)
    out["study_upper"] = expit(out.logit + norm.ppf(.975) * out.se)
    out["study_effect_proportion"] = expit(out.logit)
    return out


def reml_meta(effect: np.ndarray, variance: np.ndarray) -> dict:
    """Fit an intercept-only normal random-effects model by restricted ML.

    The objective omits constants: 0.5 * [sum(log(v+tau2)) + log(sum(w))
    + sum(w*(y-mu)**2)]. A coarse grid and bounded local refinements search
    the nonnegative axis; the zero boundary is evaluated explicitly.
    Modified Hartung-Knapp uses max(1, residual Q/(k-1)), avoiding an interval
    narrower than the conventional random-effects standard error.
    """
    y, v = np.asarray(effect, float), np.asarray(variance, float)
    if y.ndim != 1 or y.shape != v.shape or len(y) < 2 or not np.isfinite(y).all() or not np.isfinite(v).all() or (v <= 0).any():
        raise ValueError("Need at least two finite effects with positive sampling variances")
    k = len(y)

    def objective(tau2: float) -> float:
        w = 1 / (v + tau2)
        mu = np.sum(w * y) / np.sum(w)
        return float(.5 * (np.log(v + tau2).sum() + np.log(w.sum()) + np.sum(w * (y - mu) ** 2)))

    # Expand until the objective is increasing well beyond empirical dispersion.
    upper = max(1.0, float(np.var(y, ddof=1)) * 4, float(v.max()))
    for _ in range(20):
        if objective(upper) > objective(upper / 2):
            break
        upper *= 2
    else:
        raise RuntimeError("Could not bracket the REML minimum")
    grid = np.r_[0.0, np.geomspace(upper * 1e-10, upper, 160)]
    values = np.array([objective(z) for z in grid])
    candidates = [(objective(0), 0.0)]
    for i in range(1, len(grid)-1):
        if values[i] <= values[i-1] and values[i] <= values[i+1]:
            opt = minimize_scalar(objective, bounds=(grid[i-1], grid[i+1]), method="bounded", options={"xatol": 1e-11})
            if not opt.success:
                raise RuntimeError("REML optimization did not converge")
            candidates.append((float(opt.fun), float(opt.x)))
    _, tau2 = min(candidates)
    w = 1 / (v + tau2)
    mu = float(np.sum(w * y) / w.sum())
    q_re = float(np.sum(w * (y - mu) ** 2))
    hk_scale = max(1.0, q_re / (k - 1))
    se_mu = float(np.sqrt(hk_scale / w.sum()))
    ci = mu + np.array([-1, 1]) * t.ppf(.975, k-1) * se_mu
    # Approximate prediction interval for a similar future study's TRUE logit;
    # it does not include that future study's measurement error.
    pi = mu + np.array([-1, 1]) * t.ppf(.975, k-2) * np.sqrt(tau2 + se_mu**2) if k > 2 else np.array([np.nan, np.nan])
    w0 = 1 / v
    common = float(np.sum(w0*y) / w0.sum())
    q = float(np.sum(w0 * (y-common)**2))
    return {"k": k, "mu_logit": mu, "tau2": tau2, "Q": q, "Q_df": k-1,
            "Q_p": float(chi2.sf(q, k-1)), "I2_percent": max(0.0, (q-(k-1))/q)*100 if q > 0 else 0.0,
            "hk_scale": hk_scale, "se_mu": se_mu, "pooled": float(expit(mu)),
            "ci_lower": float(expit(ci[0])), "ci_upper": float(expit(ci[1])),
            "pi_lower": float(expit(pi[0])), "pi_upper": float(expit(pi[1])),
            "weights": w/w.sum(), "common_effect": float(expit(common))}


def pool(studies: pd.DataFrame, correction: float = 0.5) -> tuple[pd.DataFrame, dict]:
    """Return the exact effect table and fitted summary used in all visualizations."""
    effects = study_effects(studies, correction=correction)
    result = reml_meta(effects.logit.to_numpy(), effects.variance.to_numpy())
    effects["weight_pct"] = result["weights"] * 100
    if not np.isclose(effects.weight_pct.sum(), 100):
        raise AssertionError("Meta-analysis weights do not sum to 100 percent")
    return effects, result
