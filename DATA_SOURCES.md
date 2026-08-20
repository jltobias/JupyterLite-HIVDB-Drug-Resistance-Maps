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

## Generated outputs

`fetch_plos_2015.py` writes:

- `hivdb_surveillance_studies_2015.csv` — one row per source study.
- `hivdb_study_countries_2015.csv` — one row per parsed study-country association.
- `hivdb_country_coverage_2015.csv` — country coverage from all studies.
- `hivdb_country_summary_2015.csv` — weighted prevalence from single-country studies only.
- `hivdb_2015_metadata.json` — retrieval/source metadata and parser diagnostics.

Generated files preserve source values as much as possible while adding normalized ISO-3 codes and explicit analytic flags.
