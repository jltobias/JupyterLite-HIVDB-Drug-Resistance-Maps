"""Check notebook/book parity and that the Pages artifact contains shared assets."""
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import nbformat
import yaml

ROOT = Path(__file__).resolve().parents[1]


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.sources.extend(value for key, value in attrs if key == "src")


def validate_sources() -> list[Path]:
    notebooks = sorted((ROOT / "content").glob("*.ipynb"))
    assert notebooks, "No notebooks found"
    toc = yaml.safe_load((ROOT / "_toc.yml").read_text(encoding="utf-8"))
    chapters = [c["file"] for part in toc["parts"] for c in part["chapters"]]
    notebook_chapters = [c for c in chapters if (ROOT / f"{c}.ipynb").exists()]
    expected = [p.relative_to(ROOT).with_suffix("").as_posix() for p in notebooks]
    assert notebook_chapters == expected, "Book chapters must match Lab notebooks in order"
    for path in notebooks:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        first = notebook.cells[0]
        assert first.cell_type == "markdown", f"{path.name}: first cell must be Markdown"
        assert "(assets/hivdr-splash.png)" in first.source, f"{path.name}: missing splash"
        assert f"lab/index.html?path={path.name}" in first.source, f"{path.name}: missing Lab link"
    assert (ROOT / "content/assets/hivdr-splash.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    return notebooks


def validate_artifact(site: Path, notebooks: list[Path]) -> None:
    assert (site / "lab/index.html").is_file(), "Missing Lab entry point"
    assert (site / "book/index.html").is_file(), "Missing Book entry point"
    assert (site / ".nojekyll").is_file(), "Missing Pages .nojekyll marker"
    splash = site / "files/assets/hivdr-splash.png"
    assert splash.read_bytes() == (ROOT / "content/assets/hivdr-splash.png").read_bytes()
    for source in notebooks:
        published = site / "files" / source.name
        assert json.loads(published.read_text(encoding="utf-8")) == json.loads(source.read_text(encoding="utf-8"))
        page = site / "book/content" / f"{source.stem}.html"
        html = page.read_text(encoding="utf-8")
        images = Images()
        images.feed(html)
        covers = [src for src in images.sources if "hivdr-splash" in src]
        assert covers, f"{page}: splash missing from rendered chapter"
        for src in covers:
            resolved = page.parent / unquote(urlsplit(src).path)
            assert resolved.is_file(), f"{page}: broken image {src}"
        assert f"lab/index.html?path={source.name}" in html, f"{page}: missing launch link"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path)
    args = parser.parse_args()
    notebooks = validate_sources()
    if args.site_dir:
        validate_artifact(args.site_dir, notebooks)
    print(f"Validated splash images and chapter coverage for {len(notebooks)} notebooks"
          + (f" and Pages artifact {args.site_dir}" if args.site_dir else ""))


if __name__ == "__main__":
    main()
