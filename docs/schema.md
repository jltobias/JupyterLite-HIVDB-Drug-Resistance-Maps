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
