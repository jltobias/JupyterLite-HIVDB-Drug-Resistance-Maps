from __future__ import annotations

import re
import unicodedata
from typing import Iterable

import pandas as pd
import pycountry

ALIASES = {
    "bolivia": "BOL",
    "brunei": "BRN",
    "burma": "MMR",
    "cape verde": "CPV",
    "cote d ivoire": "CIV",
    "cote divoire": "CIV",
    "ivory coast": "CIV",
    "democratic republic of congo": "COD",
    "democratic republic of the congo": "COD",
    "dr congo": "COD",
    "drc": "COD",
    "congo democratic republic": "COD",
    "congo": "COG",
    "iran": "IRN",
    "laos": "LAO",
    "moldova": "MDA",
    "north korea": "PRK",
    "south korea": "KOR",
    "korea republic of": "KOR",
    "republic of korea": "KOR",
    "russia": "RUS",
    "russian federation": "RUS",
    "swaziland": "SWZ",
    "eswatini": "SWZ",
    "syria": "SYR",
    "taiwan": "TWN",
    "tanzania": "TZA",
    "united republic of tanzania": "TZA",
    "usa": "USA",
    "us": "USA",
    "united states": "USA",
    "united states of america": "USA",
    "uk": "GBR",
    "united kingdom": "GBR",
    "venezuela": "VEN",
    "vietnam": "VNM",
    "viet nam": "VNM",
}


def key(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def normalize_country(value: object) -> tuple[str | None, str | None]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None, None
    raw = str(value).strip()
    if not raw:
        return None, None
    k = key(raw)
    if k in ALIASES:
        c = pycountry.countries.get(alpha_3=ALIASES[k])
        return c.alpha_3, c.name
    try:
        c = pycountry.countries.lookup(raw)
        return c.alpha_3, c.name
    except LookupError:
        return None, raw


def split_countries(value: object) -> list[str]:
    """Split a source country field conservatively.

    The historical spreadsheet generally uses comma/semicolon-delimited labels.
    This function keeps unique labels in source order. Labels that cannot be
    normalized are retained for explicit review.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    if ";" in text or "|" in text:
        parts = re.split(r"\s*[;|]\s*", text)
    elif " / " in text:
        parts = re.split(r"\s+/\s+", text)
    elif "," in text:
        protected = {
            "Korea, Republic of": "Korea Republic of",
            "Congo, Democratic Republic of the": "Democratic Republic of the Congo",
            "Tanzania, United Republic of": "United Republic of Tanzania",
        }
        tmp = text
        for old, new in protected.items():
            tmp = tmp.replace(old, new)
        parts = re.split(r"\s*,\s*", tmp)
    else:
        parts = [text]
    result = []
    seen = set()
    for part in parts:
        p = part.strip()
        if p and p not in seen:
            result.append(p)
            seen.add(p)
    return result


def first_matching_column(columns: Iterable[object], patterns: list[str]) -> object | None:
    scored = []
    for col in columns:
        k = key(col)
        for rank, pattern in enumerate(patterns):
            if re.search(pattern, k):
                scored.append((rank, len(k), col))
                break
    return min(scored)[2] if scored else None
