# JupyterLite HIV Drug Resistance Maps

![JupyterLite HIV Drug Resistance Maps: an original conceptual globe, map, and molecular illustration.](content/assets/hivdr-splash.png)

## Maps, globes, 3D scenes, and other resources

**[Launch JupyterLite Lab](https://jltobias.github.io/JupyterLite-HIVDB-Drug-Resistance-Maps/lab/index.html)** · **[Read the Jupyter Book](https://jltobias.github.io/JupyterLite-HIVDB-Drug-Resistance-Maps/book/)**

| Resource | Links |
|---|---|
| **2D Maps** | [Run the global TDR choropleth notebook](https://jltobias.github.io/JupyterLite-HIVDB-Drug-Resistance-Maps/lab/index.html?path=02_global_tdr_choropleth.ipynb) · [Stanford surveillance map](https://hivdb.stanford.edu/page/surveillance-map/) · [Plotly choropleths](https://plotly.com/python/choropleth-maps/) |
| **3D Maps** | [deck.gl geographic columns](https://deck.gl/docs/api-reference/layers/column-layer) · [pydeck](https://deckgl.readthedocs.io/en/latest/) |
| **Globes** | [CesiumJS](https://cesium.com/platform/cesiumjs/) · [Plotly map projections](https://plotly.com/python/map-configuration-and-styling/) |
| **3D Scenes** | [Three.js](https://threejs.org/docs/) · [deck.gl scene graphs](https://deck.gl/docs/api-reference/layers/scenegraph-layer) · [Stanford molecular structures](https://hivdb.stanford.edu/pages/3DStructures/rt.html) |
| **Other resources** | [Mapping resource guide](content/mapping_resources.md) · [HIVDB](https://hivdb.stanford.edu/) · [WHO HIVDR report](https://www.who.int/publications/i/item/9789240086319) · [Natural Earth](https://www.naturalearthdata.com/) · [JupyterLite documentation](https://jupyterlite.readthedocs.io/en/stable/) |

The repository implements 2D surveillance maps. The 3D map, globe, and scene links are external learning resources, not additional HIVDR analyses or bundled content. Their services, imagery, models, and example datasets have separate terms.

## About this repository

The book and Lab are published together by the GitHub Pages workflow. The book link becomes available after the first successful deployment containing the book configuration. The splash is original AI-generated artwork; its markers, bars, and molecular motif are conceptual, not measured data.

Browser-based, reproducible examples for learning the fundamentals of **HIV drug resistance (HIVDR)** and mapping **transmitted HIV drug resistance (TDR)** using public data associated with the Stanford HIV Drug Resistance Database (HIVDB).

## Launch the live JupyterLite notebooks

Open the browser-based notebook environment here:

**[Launch JupyterLite Lab](https://jltobias.github.io/JupyterLite-HIVDB-Drug-Resistance-Maps/lab/index.html)**

No local Python or Jupyter installation is required once the GitHub Pages deployment is active.

### Fresh notebooks after each deployment

JupyterLite stores edited notebooks in browser storage, and a locally modified copy can otherwise take precedence over a newer server copy. This repository therefore gives each GitHub Pages deployment a new JupyterLite content-storage namespace based on the deployment commit SHA and explicitly disables service-worker caching. After a successful Pages deployment, reopening the launch link should show the notebook set published by that deployment without requiring a manual browser-cache clear.

Because browser-local edits belong to the deployment in which they were created, edits from an older deployment will not automatically appear in a newer deployment. Export or download any work you want to preserve before moving to a newly deployed version. If the browser still shows stale content, use **Help → Clear Browser Data** in JupyterLite as a manual reset.

## What this repository does

- introduces HIV drug-resistance fundamentals with a visual, citation-rich Notebook 00;
- builds a JupyterLite site that runs entirely in the browser;
- downloads and normalizes the openly published 2015 HIVDB/PLOS surveillance study table (287 studies, 111 countries, 50,870 ART-naive people) as a reproducible baseline;
- creates country-level coverage and sample-size-weighted TDR summaries from **single-country studies**;
- maps overall, NRTI, NNRTI, and PI TDR with Plotly choropleths;
- adds an MCH-centered pediatric HIVDR case study linking presentation-derived pediatric DTG-resistance examples to Stanford HIVDB mutation-interpretation concepts;
- provides an experimental, low-request Playwright network-capture utility for discovering the current HIVDB surveillance map's machine-readable payload without mass crawling;
- provides a generic importer for a current HIVDB CSV/JSON/XLS/XLSX export once a stable export/API URL is documented.

> **Important:** Stanford HIVDB's Sierra web service is a sequence interpretation service. It should not be treated as the source of country-level surveillance prevalence. This repository keeps sequence interpretation and epidemiologic surveillance data separate.

## Data status

The reproducible default dataset is the public-domain supporting spreadsheet from:

> Rhee S-Y, Blanco JL, Jordan MR, et al. (2015). *Geographic and Temporal Trends in the Molecular Epidemiology and Genetic Mechanisms of Transmitted HIV-1 Drug Resistance: An Individual-Patient- and Sequence-Level Meta-Analysis.* PLOS Medicine 12(4): e1001810. https://doi.org/10.1371/journal.pmed.1001810

HIVDB's current homepage describes a larger Transmitted Resistance Surveillance Map with published sequences from **more than 95,000 ART-naive persons in more than 120 countries**. During repository preparation, no stable documented download/API endpoint for that map was found in HIVDB's public documentation. For that reason, this project does **not** pretend that the 2015 snapshot is the current database.

See [DATA_SOURCES.md](DATA_SOURCES.md), [METHODOLOGY.md](METHODOLOGY.md), and the [optional patient-level input schema](docs/schema.md).

## JupyterLite notebooks

The `content/` directory contains:

0. **00_hiv_drug_resistance_fundamentals.ipynb** — learn the biology, vocabulary, drug classes, mutation notation, resistance categories, and Stanford HIVDB interpretation concepts before working with surveillance data.
1. **01_data_coverage.ipynb** — inspect provenance, country coverage, sample sizes, and missingness.
2. **02_global_tdr_choropleth.ipynb** — create a global choropleth of overall or drug-class TDR.
3. **03_drug_class_and_time.ipynb** — compare NRTI/NNRTI/PI patterns and explore study-year distributions.
4. **04_pediatric_hivdr_mch_case_study.ipynb** — explore pediatric HIVDR in the dolutegravir era using an MCH-centered case study, presentation-derived CADRE examples, synthetic pediatric mutation profiles, and Stanford HIVDB interpretation concepts. The MCH presentation is credited to Spencer Lloyd, MPH, MD; Laura Broyles, MD; and Jason Bacha, MD.
5. **05_mutation_geographic_clusters.ipynb** — screen patient-level mutation prevalence by geography and define a spatial-clustering analysis.
6. **06_resistance_stratification.ipynb** — drill down by subtype, ART experience, acquired/transmitted status, mutation, and drug class.
7. **07_subtype_standardized_geography.ipynb** — compare crude and directly subtype-standardized geographic estimates.
8. **08_nnrtI_to_dtg_geographic_history.ipynb** — compare earlier NNRTI resistance with later DTG resistance using paired country-time observations.

Notebook 00 is primarily narrative and visual. Notebooks 01–03 read static CSV files packaged into JupyterLite. Notebook 04 is a self-contained educational case study with synthetic genotype profiles and presentation-derived aggregate examples. Notebooks 05–08 are deliberately conditional templates: the 2015 aggregate snapshot cannot estimate patient-level mutation clusters, subtype-adjusted rates, treatment-stratified resistance, or DTG-era temporal associations. Network retrieval happens during the GitHub Actions build, not in the browser, which avoids CORS and reproducibility problems.

## Local quick start

The full JupyterLite build also requires [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) on `PATH`; the Pages workflow installs it automatically. Use Linux or WSL if Windows cannot extract the WebAssembly environment's Unix-style files. The book build runs with ordinary Python.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements-dev.txt
python scripts/fetch_plos_2015.py --output-dir content/data
pytest -q
python scripts/build_book.py
jupyter lite build --contents content --output-dir dist
python -c "import shutil; shutil.copytree('_build/html', 'dist/book', dirs_exist_ok=True)"
python scripts/validate_site.py --site-dir dist
python -m http.server -d dist 8000
```

Then open `http://localhost:8000/lab/index.html` or `http://localhost:8000/book/`. On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell.

## Jupyter Book chapters

The [Jupyter Book](https://jltobias.github.io/JupyterLite-HIVDB-Drug-Resistance-Maps/book/) uses the same nine `content/*.ipynb` files as the Lab, in the same order. Its table of contents groups Notebooks 00–04 as the learning sequence and Notebooks 05–08 as conditional templates, followed by mapping resources, provenance, methodology, the optional input schema, and this README. Every notebook's first Markdown cell contains the shared splash image and a direct link to open that notebook in the Lab.

The build uses **Jupyter Book 1.0.4.post1**, pinned in `requirements-book.txt` for the `_config.yml` / `_toc.yml` format. It executes the notebooks to publish their tables and figures, fails on execution errors, and does not execute the optional network-capture scripts. Build outputs stay in `_build/`; source notebooks remain unexecuted in version control.

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

The included workflow builds JupyterLite at `/lab/index.html` and Jupyter Book at `/book/`, then deploys them together with GitHub Pages. In repository settings, set **Pages → Build and deployment → Source = GitHub Actions**. The workflow fetches and validates the CC0 data, packages the shared splash in the Lab contents, builds the book, checks both outputs, and uploads one Pages artifact.

Each deployment writes a runtime `jupyter-lite.json` that sets `contentsStorageName` to a value derived from the GitHub commit SHA and sets `enableServiceWorkerCache` to `false`. This prevents browser-local notebook copies from an older deployment from silently overriding newer published notebooks.

## Repository layout

```text
content/                     JupyterLite notebooks and browser-side helper code
content/data/                generated normalized CSV files
content/assets/              original splash image and generation provenance
content/mapping_resources.md  2D / 3D / globe / scene resource guide
_config.yml, _toc.yml         Jupyter Book settings and notebook chapter order
index.md                     Jupyter Book landing page
requirements-book.txt        pinned book builder and visualization dependencies
scripts/fetch_plos_2015.py   reproducible baseline data fetch + normalization
scripts/fetch_current_hivdb.py generic current-export importer
scripts/capture_current_hivdb.py experimental current-map network discovery
scripts/validate_outputs.py  data validation
scripts/validate_site.py     notebook, chapter, and published-asset validation
scripts/build_book.py        book build with interactive HTML chart rendering
.github/workflows/           CI, JupyterLite Pages deployment, manual discovery
tests/                       transformation and aggregation tests
```

## Citation and attribution

### Epidemiologic data

**Rhee S-Y, Blanco JL, Jordan MR, Taylor J, Lemey P, Varghese V, et al. (2015).** *Geographic and Temporal Trends in the Molecular Epidemiology and Genetic Mechanisms of Transmitted HIV-1 Drug Resistance: An Individual-Patient- and Sequence-Level Meta-Analysis.* PLOS Medicine 12(4): e1001810. [Article and license statement](https://doi.org/10.1371/journal.pmed.1001810); [S1 Table, DOI suffix s004](https://doi.org/10.1371/journal.pmed.1001810.s004); [published correction](https://doi.org/10.1371/journal.pmed.1001845).

This **CC0/public-domain** supporting table is the source of the build-generated study, study-country, coverage, and weighted-summary CSV files used in Notebooks 01–03. The article describes 287 studies, 50,870 people, and 111 countries. This project normalizes country identifiers and calculates descriptive sample-size-weighted percentages from eligible single-country studies; these transformations are not new nationally representative estimates. Cite the original studies listed in S1 Table when using their evidence. Retrieval time, source URL, parser mapping, and raw-file SHA-256 are recorded in `content/data/hivdb_2015_metadata.json` at build time. GenBank sequences underpin the published study; this repo does not download or redistribute those sequences.

**Stanford University HIV Drug Resistance Database (HIVDB).** [Database](https://hivdb.stanford.edu/); [Transmitted Resistance Surveillance Map](https://hivdb.stanford.edu/page/surveillance-map/); [Sierra documentation](https://hivdb.stanford.edu/page/graphiql/). Credit Stanford HIVDB for the surveillance and interpretation resources. The live map is a separate resource; it is not the packaged 2015 snapshot. No current HIVDB export or Sierra result is bundled. Any future export needs its own source citation, retrieval/version record, and redistribution terms; the CC0 status of the PLOS table does not license the entire HIVDB site.

**Lloyd S, Broyles L, Bacha J. (August 19, 2026).** *HIV Drug Resistance in MCH Populations.* MCH Office Hours, CDC/GHC/DGHT/HCTB. The existing Notebook 04 credits Spencer Lloyd, MPH, MD; Laura Broyles, MD; and Jason Bacha, MD for its presentation-derived pediatric CADRE aggregate values and MCH context. The presentation file and a verifiable public URL are **not included in this checkout**, so the transcription cannot be independently checked here. These values describe selected pediatric analysis populations, not national prevalence or Stanford surveillance estimates. No presentation slides, images, or logos are reproduced. Its rights status is not inferred from the presenters' affiliations. The fictional child profiles and denominator thought experiment are explicitly synthetic teaching examples, not patient records.

Notebooks 05–08 contain **conditional analysis templates**, not additional datasets. User-supplied patient-level, denominator, adjacency, or country-time inputs require source-specific provenance and permission for their intended use; none are supplied by this repository.

### Educational references

The narrative and original diagrams in Notebooks 00 and 04 refer readers to these sources; their websites, figures, reports, and videos are not copied into this repository:

- **Stanford HIVDB:** [historical resistance primer](https://hivdb.stanford.edu/pages/documentPage/primer.html), [release notes](https://hivdb.stanford.edu/page/release-notes/), [NRTI](https://hivdb.stanford.edu/dr-summary/resistance-notes/NRTI/), [NNRTI](https://hivdb.stanford.edu/dr-summary/resistance-notes/NNRTI/), [PI](https://hivdb.stanford.edu/dr-summary/resistance-notes/PI/), [INSTI](https://hivdb.stanford.edu/dr-summary/resistance-notes/INSTI/), and [CAI](https://hivdb.stanford.edu/dr-summary/resistance-notes/CAI/) resistance notes; [analysis by mutations](https://hivdb.stanford.edu/hivdb/by-mutations/); [reverse-transcriptase structures](https://hivdb.stanford.edu/pages/3DStructures/rt.html). Algorithm examples are teaching illustrations; use the versioned live resource for current interpretation.
- **NIH ClinicalInfo.** [Life Cycle, HIV/AIDS Glossary](https://clinicalinfo.hiv.gov/en/glossary/life-cycle). Background for Notebook 00's original life-cycle diagram.
- **World Health Organization (2024).** [HIV drug resistance — brief report 2024](https://www.who.int/publications/i/item/9789240086319), ISBN 978-92-4-008631-9. Background for resistance definitions; linked, not republished.
- **Linked videos in Notebook 00:** [HHMI BioInteractive — HIV Life Cycle](https://www.youtube.com/watch?v=PlSvywlLuNw) and [The HIV Life Cycle and Antiretroviral Drugs — Part 1](https://www.youtube.com/watch?v=lRwlpfhYl-c). Credits and rights remain with the original publishers; no video or thumbnail is bundled.

### Geography, software, and original artwork

- **Natural Earth contributors:** geographic boundaries used by the pinned Plotly 6.2.0 renderer. Natural Earth declares its map data [public domain](https://www.naturalearthdata.com/about/terms-of-use/). [Plotly documents](https://plotly.com/python/choropleth-maps/) the change in base-geometry sources starting with 6.3; the Lab and book deliberately pin 6.2.0 to retain Natural Earth-only geometry. Basemap outlines are downloaded by the browser from Plotly's CDN, so map rendering needs network access. These boundaries supply geographic context, not epidemiologic observations.
- **pycountry / Debian iso-codes:** [pycountry](https://github.com/pycountry/pycountry) supplies the ISO country identifiers and names used in normalization, derived from [iso-codes](https://salsa.debian.org/iso-codes-team/iso-codes). This is reference metadata, not an HIV dataset; retain the packages' distributed license notices.
- **Project Jupyter, JupyterLite, Jupyter Book, and the scientific Python contributors:** browser notebooks, book publishing, data processing, and visualization use their independently licensed software. See [requirements.txt](requirements.txt), [requirements-book.txt](requirements-book.txt), and [environment.yml](environment.yml). The repository's [MIT license](LICENSE) covers its code, not every linked resource or third-party package.
- **Splash artwork:** `content/assets/hivdr-splash.png` was generated specifically for this project with the built-in OpenAI image-generation tool on November 16, 2026, without source images, copied maps, third-party artwork, logos, or screenshots. The [asset provenance and exact generation prompt](content/assets/README.md) record how it was made. It is an illustrative cover, not a scientific figure or an institutional endorsement. No claim is made that all linked resources are copyright-free.

See [CITATION.cff](CITATION.cff) for this repository's software citation and [DATA_SOURCES.md](DATA_SOURCES.md) for file-level provenance.
