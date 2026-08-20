import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalization import normalize_country, split_countries


def test_common_aliases_map_to_iso3():
    assert normalize_country("Cote d'Ivoire")[0] == "CIV"
    assert normalize_country("South Korea")[0] == "KOR"
    assert normalize_country("Viet Nam")[0] == "VNM"


def test_country_split_keeps_multiple_labels():
    assert split_countries("Kenya; Uganda; Tanzania") == ["Kenya", "Uganda", "Tanzania"]


def test_nrti_and_nnrti_column_detection_are_distinct():
    from fetch_plos_2015 import COLUMN_PATTERNS
    from normalization import first_matching_column
    cols = ["Overall TDR (%)", "NRTI TDR (%)", "NNRTI TDR (%)"]
    assert first_matching_column(cols, COLUMN_PATTERNS["tdr_nrti_pct"]) == "NRTI TDR (%)"
    assert first_matching_column(cols, COLUMN_PATTERNS["tdr_nnrti_pct"]) == "NNRTI TDR (%)"
