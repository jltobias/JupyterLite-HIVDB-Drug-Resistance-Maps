import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))

from hivdr_tools.aggregation import weighted_country_summary


def test_weighted_summary_excludes_multi_country_rows():
    frame = pd.DataFrame(
        [
            {"study_id": "a", "iso3": "AAA", "country": "A", "participants": 100, "is_single_country": True, "tdr_overall_pct": 10.0},
            {"study_id": "b", "iso3": "AAA", "country": "A", "participants": 300, "is_single_country": True, "tdr_overall_pct": 20.0},
            {"study_id": "c", "iso3": "AAA", "country": "A", "participants": 999, "is_single_country": False, "tdr_overall_pct": 99.0},
        ]
    )
    out = weighted_country_summary(frame).set_index("iso3")
    assert out.loc["AAA", "tdr_overall_pct"] == pytest.approx(17.5)
    assert out.loc["AAA", "n_participants_weighted"] == 400
    assert out.loc["AAA", "n_studies_weighted"] == 2


def test_missing_outcome_is_not_zero():
    frame = pd.DataFrame(
        [
            {"study_id": "a", "iso3": "AAA", "country": "A", "participants": 100, "is_single_country": True, "tdr_overall_pct": None},
            {"study_id": "b", "iso3": "AAA", "country": "A", "participants": 100, "is_single_country": True, "tdr_overall_pct": 20.0},
        ]
    )
    out = weighted_country_summary(frame).iloc[0]
    assert out["tdr_overall_pct"] == pytest.approx(20.0)
