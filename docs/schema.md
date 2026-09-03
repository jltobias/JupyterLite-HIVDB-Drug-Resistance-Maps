# Normalized schema

## Study table

Core fields:

| Field | Meaning |
|---|---|
| `study_id` | Stable ID within the generated snapshot |
| `reference` | Source study reference/label |
| `participants` | Study sample size reported by source |
| `countries` | Original country field |
| `median_sample_year` | Source median sample year when available |
| `tdr_overall_pct` | Overall TDR percent |
| `tdr_nrti_pct` | NRTI-associated TDR percent |
| `tdr_nnrti_pct` | NNRTI-associated TDR percent |
| `tdr_pi_pct` | PI-associated TDR percent when source provides it |
| `cpr_url` | Calibrated Population Resistance output link when provided |

## Study-country table

Adds:

- `country_source_raw`
- `country`
- `iso3`
- `study_country_count`
- `is_single_country`

## Country summary

A country can have `n_studies_total > 0` and no weighted TDR estimate if all available rows are multi-country or the relevant outcome is missing.

## Optional patient-level analysis inputs

Notebooks 05–08 are intentionally separate from the 2015 study aggregate. They accept exported CSV files placed under `content/data/` (or `content/data/current/`). The files below are contracts, not files that can be inferred from the published aggregate.

### `hivdb_patient_mutations.csv`

One row per person–mutation observation. Required: `patient_id`, `iso3`, `mutation`. Recommended: `subtype`, `sample_year`, `art_status`, `acquisition`, and `drug_class`.

### `hivdr_patient_denominators.csv`

One row per sequenced person, including people without the mutation of interest. Required: `patient_id`, `iso3`. Recommended: `subtype`, `sample_year`, `art_status`, and `acquisition`.

### `hivdb_patient_resistance.csv`

One row per person and pre-specified outcome (or one row per person–drug class after deduplication). Required: `patient_id`, `iso3`, and binary `resistant` (0/1). Optional descriptive fields: `subtype`, `art_status`, `acquisition`, `mutation`, and `drug_class`. `resistance_pct` is accepted for compatibility, but values must be 0–100 and must not be averaged across duplicated mutation rows.

### `hivdb_country_resistance_time.csv`

One row per country and comparable sampling window. Required: `iso3`, `sample_year`, `nnrti_resistance_pct`, `dtg_resistance_pct`, and `n_tested`. Missing early observations mean “not observed”, not zero. Use consistent transmitted/acquired definitions and record the source and assay in accompanying metadata.

### `country_adjacency.csv`

Optional undirected edge list for the cluster screen with columns `iso3_i`, `iso3_j`, and optional positive `weight`. A geographic adjacency result is only as defensible as the pre-specified boundary/distance definition and its sampling coverage.
