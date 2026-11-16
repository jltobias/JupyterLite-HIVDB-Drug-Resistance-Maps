# Data sources and provenance

## 1. Current Stanford HIVDB Transmitted Resistance Surveillance Map

Homepage: https://hivdb.stanford.edu/

Surveillance map: https://hivdb.stanford.edu/page/surveillance-map/

Stanford HIVDB currently describes the map as covering published virus sequences from more than 95,000 ART-naive persons in more than 120 countries. HIVDB is the authoritative source for the current content and definitions.

At the time this repository was prepared, the map was a JavaScript application and a stable machine-readable surveillance-map download/API was not identified in HIVDB's public documentation. Do not infer that the Sierra GraphQL service supplies these country prevalence data: Sierra interprets submitted sequences/mutations.

## 2. Reproducible published baseline (default build data)

Rhee S-Y, Blanco JL, Jordan MR, et al. (2015). Geographic and Temporal Trends in the Molecular Epidemiology and Genetic Mechanisms of Transmitted HIV-1 Drug Resistance: An Individual-Patient- and Sequence-Level Meta-Analysis. PLOS Medicine 12(4): e1001810.

DOI: https://doi.org/10.1371/journal.pmed.1001810

The article reports 287 studies, 50,870 individuals, and 111 countries. Its S1 Table is an XLSX summary containing study reference, number of participants, countries, recruitment characteristics, median sample year, subtype distribution, overall/NRTI/NNRTI TDR, CPR links, and SDRM counts. PLOS marks the article as CC0/public domain.

The build script downloads S1 Table from the PLOS supplementary-file endpoint identified by DOI suffix `s004`.

## 3. Sierra / HIVdb interpretation web service

Documentation: https://hivdb.stanford.edu/page/graphiql/

Sierra is useful when an epidemiologist has viral sequences or mutation lists and wants HIVDB resistance interpretation output. It is not used here to manufacture country-level prevalence estimates.

## 4. Pediatric MCH teaching examples (Notebook 04)

Lloyd S, Broyles L, Bacha J. *HIV Drug Resistance in MCH Populations.* MCH Office Hours, CDC/GHC/DGHT/HCTB; August 19, 2026. The existing notebook attributes pediatric CADRE percentages to this presentation. The presentation itself and a verifiable public URL are absent from this checkout, so its numeric transcription has not been independently verified here. Its rights status is not established by its institutional attribution. No slides or images are reproduced.

These aggregate examples describe selected pediatric populations and are separate from the CC0 PLOS surveillance table. The child profiles and denominator thought experiment are synthetic educational examples, not patient data. Notebooks 05–08 ship no patient-level, adjacency, or longitudinal datasets; they report missing-input limitations until suitable source-documented inputs are supplied.

## 5. Geography and educational sources

The pinned Plotly 6.2.0 renderer uses [Natural Earth public-domain map geometry](https://www.naturalearthdata.com/about/terms-of-use/), fetched from Plotly's CDN by the browser. The version pin precedes [Plotly's 6.3 change in geometry sources](https://plotly.com/python/choropleth-maps/). Country labels and ISO codes are normalized with [pycountry](https://github.com/pycountry/pycountry), derived from Debian iso-codes; these are reference metadata, not resistance measurements.

Notebook 00 cites Stanford HIVDB interpretation notes, NIH ClinicalInfo's HIV life-cycle glossary, and WHO's *HIV drug resistance — brief report 2024*. Notebook 04 also uses Stanford's NRTI/INSTI notes and mutation interpretation concepts. The [README citation and attribution section](README.md#citation-and-attribution) lists all source links, video credits, software credits, and scope of reuse. Linked media are not bundled. The [splash provenance](content/assets/README.md) records the original AI-generated illustration and prompt; it contains no measured data.

## Generated outputs

`fetch_plos_2015.py` writes:

- `hivdb_surveillance_studies_2015.csv` — one row per source study.
- `hivdb_study_countries_2015.csv` — one row per parsed study-country association.
- `hivdb_country_coverage_2015.csv` — country coverage from all studies.
- `hivdb_country_summary_2015.csv` — weighted prevalence from single-country studies only.
- `hivdb_2015_metadata.json` — retrieval/source metadata and parser diagnostics.

Generated files preserve source values as much as possible while adding normalized ISO-3 codes and explicit analytic flags.

## Study inventory and Africa synthesis additions

Notebooks 09–12 add dated factual snapshots in `content/data/studies/` and `content/data/meta_analysis/`. These are separate from the older build-generated surveillance CSVs. The [source and field documentation](content/study_matrix_methods.md) describes every input, exact query scope, field limitations, source-checked annotations and conditional reconstructed meta-analysis counts. The manifests record retrieval times, versions, raw-response hashes and output hashes. Raw responses, article text, abstracts, sequences and third-party graphics are not redistributed.
