# JupyterLite HIV Drug Resistance Maps

Browser-based, reproducible examples for mapping **transmitted HIV drug resistance (TDR)** using public data associated with the Stanford HIV Drug Resistance Database (HIVDB).

## What this repository does

- builds a JupyterLite site that runs entirely in the browser;
- downloads and normalizes the openly published 2015 HIVDB/PLOS surveillance study table (287 studies, 111 countries, 50,870 ART-naive people) as a reproducible baseline;
- creates country-level coverage and sample-size-weighted TDR summaries from **single-country studies**;
- maps overall, NRTI, NNRTI, and PI TDR with Plotly choropleths;
- provides an experimental, low-request Playwright network-capture utility for discovering the current HIVDB surveillance map's machine-readable payload without mass crawling;
- provides a generic importer for a current HIVDB CSV/JSON/XLS/XLSX export once a stable export/API URL is documented.

> **Important:** Stanford HIVDB's Sierra web service is a sequence interpretation service. It should not be treated as the source of country-level surveillance prevalence. This repository keeps sequence interpretation and epidemiologic surveillance data separate.

## Data status

The reproducible default dataset is the public-domain supporting spreadsheet from:

> Rhee S-Y, Blanco JL, Jordan MR, et al. (2015). *Geographic and Temporal Trends in the Molecular Epidemiology and Genetic Mechanisms of Transmitted HIV-1 Drug Resistance: An Individual-Patient- and Sequence-Level Meta-Analysis.* PLOS Medicine 12(4): e1001810. https://doi.org/10.1371/journal.pmed.1001810

HIVDB's current homepage describes a larger Transmitted Resistance Surveillance Map with published sequences from **more than 95,000 ART-naive persons in more than 120 countries**. During repository preparation, no stable documented download/API endpoint for that map was found in HIVDB's public documentation. For that reason, this project does **not** pretend that the 2015 snapshot is the current database.

See [DATA_SOURCES.md](DATA_SOURCES.md) and [METHODOLOGY.md](METHODOLOGY.md).

## JupyterLite notebooks

The `content/` directory contains:

1. **01_data_coverage.ipynb** — inspect provenance, country coverage, sample sizes, and missingness.
2. **02_global_tdr_choropleth.ipynb** — create a global choropleth of overall or drug-class TDR.
3. **03_drug_class_and_time.ipynb** — compare NRTI/NNRTI/PI patterns and explore study-year distributions.

The notebooks only read static CSV files packaged into JupyterLite. Network retrieval happens during the GitHub Actions build, not in the browser, which avoids CORS and reproducibility problems.

## Local quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements-dev.txt
python scripts/fetch_plos_2015.py --output-dir content/data
pytest -q
jupyter lite build --contents content --output-dir dist
python -m http.server -d dist 8000
```

Then open `http://localhost:8000`.

## Current HIVDB data: two supported paths

### Preferred: use a documented machine-readable export

If Stanford provides a stable CSV/JSON/XLS/XLSX URL for the current surveillance map:

```bash
python scripts/fetch_current_hivdb.py \
  --source-url "https://...official-hivdb-export..." \
  --output-dir content/data/current
```

The importer is deliberately schema-tolerant and writes a field-mapping report. Review that report before treating results as analytic data.

### Experimental: discover the map's network payload

The current surveillance map is a JavaScript application. A single-page Playwright capture can record JSON responses and identify candidate records containing country plus TDR/resistance fields:

```bash
python -m playwright install chromium
python scripts/capture_current_hivdb.py --output-dir captured_hivdb
```

This is **discovery**, not a guaranteed stable API. Do not schedule it aggressively. Once a stable response URL/schema is confirmed, use `fetch_current_hivdb.py` and pin the source URL/schema in version control.

## Epidemiologic aggregation rule

For a study that reports several countries but only one combined sample size, assigning the full denominator (or an arbitrary fraction) to each country would bias a country estimate. Therefore:

- all parsed countries are retained in the **coverage** table;
- only **single-country** studies contribute to sample-size-weighted country prevalence by default;
- multi-country studies can be added to country prevalence only when country-specific denominators are available.

This is a teaching repository, not a replacement for HIVDB, WHO guidance, or a formal surveillance analysis.

## GitHub Pages

The included workflow builds JupyterLite and deploys it with GitHub Pages. In repository settings, set **Pages → Build and deployment → Source = GitHub Actions**.

## Repository layout

```text
content/                     JupyterLite notebooks and browser-side helper code
content/data/                generated normalized CSV files
scripts/fetch_plos_2015.py   reproducible baseline data fetch + normalization
scripts/fetch_current_hivdb.py generic current-export importer
scripts/capture_current_hivdb.py experimental current-map network discovery
scripts/validate_outputs.py  data validation
.github/workflows/           CI, JupyterLite Pages deployment, manual discovery
tests/                       transformation and aggregation tests
```

## Citation and attribution

Please cite Stanford HIVDB and the source studies used in your analysis. The repository's code is MIT licensed; source datasets retain their own terms/licensing. The 2015 PLOS Medicine article and its supporting material are dedicated to the public domain under CC0.
