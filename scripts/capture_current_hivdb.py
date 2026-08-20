#!/usr/bin/env python3
"""Experimental one-page network capture for HIVDB's current surveillance map.

This utility performs one browser page load, records JSON responses, and searches
those payloads for record-like dictionaries whose keys suggest both geography and
resistance/TDR. It is intended to discover a stable source endpoint/schema, not to
replace a documented API and not for aggressive scheduled crawling.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

MAP_URL = "https://hivdb.stanford.edu/page/surveillance-map/"


def candidate_dicts(obj):
    if isinstance(obj, dict):
        keys = " ".join(str(k).lower() for k in obj)
        has_geo = bool(re.search(r"countr|location|nation", keys))
        has_dr = bool(re.search(r"tdr|resist|sdrm", keys))
        if has_geo and has_dr:
            yield obj
        for value in obj.values():
            yield from candidate_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from candidate_dicts(item)


async def run(url: str, output_dir: Path, wait_ms: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    captures = []
    candidates = []
    seen = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async def on_response(response):
            ctype = (response.headers.get("content-type") or "").lower()
            if "json" not in ctype and not response.url.lower().endswith(".json"):
                return
            try:
                payload = await response.json()
            except Exception:
                return
            captures.append({"url": response.url, "status": response.status, "payload": payload})
            for obj in candidate_dicts(payload):
                signature = json.dumps(obj, sort_keys=True, default=str)
                if signature not in seen:
                    seen.add(signature)
                    candidates.append({"source_url": response.url, "record": obj})

        page.on("response", on_response)
        await page.goto(url, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_timeout(wait_ms)
        title = await page.title()
        await browser.close()

    metadata = {
        "map_url": url,
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "page_title": title,
        "n_json_responses": len(captures),
        "n_candidate_records": len(candidates),
        "note": "Discovery output only. Confirm source URL and schema before analytic use.",
    }
    (output_dir / "capture_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    with (output_dir / "json_responses.jsonl").open("w", encoding="utf-8") as fh:
        for item in captures:
            fh.write(json.dumps(item, default=str) + "\n")
    (output_dir / "candidate_records.json").write_text(json.dumps(candidates, indent=2, default=str), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=MAP_URL)
    ap.add_argument("--output-dir", type=Path, default=Path("captured_hivdb"))
    ap.add_argument("--wait-ms", type=int, default=8000)
    args = ap.parse_args()
    asyncio.run(run(args.url, args.output_dir, args.wait_ms))


if __name__ == "__main__":
    main()
