# Study matrix and Meta Analysis: sources and definitions

Notebooks 09–12 use a factual snapshot retrieved on November 16, 2026. Run All uses these dated files. Native Python can refresh the exact requests; no silent network fallback or simulated studies are used.

## What is covered

The catalogue unions the public HIVDB reference index with the reference tables for the GenoRx and genotype-phenotype downloads. It contains **2,282 publication/reference records**; **2,156** appear in the default current reference index. The selected sources provide sampling evidence for **1,507 references**, mapped to **143 countries/areas**. This does not constitute every table or every study component in HIVDB.

The PR, RT and IN bulk files contain 176,809, 187,327 and 25,916 records respectively. These are input record counts, not independent participant counts. The separate live HIV1 group M queries return 87 DTG references (2,475 selected isolates) and 7 LEN references (62 selected isolates). Query API version: **0.1.18**; database version: **2026-11-11T17:52:51**. Legacy downloads have a different update schedule; neither their retrieval date nor the API version dates every underlying study.

## Eight requested domains

| Domain | Implementation | Interpretation limit |
|---|---|---|
| Population | Separate age group and baseline ART fields | Nine source-checked publication examples; missing elsewhere unless extended. No class-specific drug list establishes overall ART naivety. |
| Geography | Exact sampling labels mapped to ISO3; unmapped labels retained | Country of an isolate is not author affiliation, every trial site, or laboratory location. |
| Primary outcome | Only explicitly designated endpoints in the checked sources | Mutation, prevalence and susceptibility **outcome focus** is a separate annotation. A title does not establish primacy. |
| Drug exposure | Recorded drug list in the gene-specific export/query | Prior exposure, trial baseline ART status and prevention use are different concepts. “None” applies to the sequenced gene's drug class. |
| Clinical outcome | Labels distinguish enrollment/sampling eligibility from measured follow-up outcomes | No harmonized suppression or failure denominator is supplied by the catalogue. |
| Collection year | Exact years and `< year` upper bounds retained separately | Publication, enrollment and observation-period fields are not substituted for specimen years. |
| Resistance outcome | Source-checked outcome descriptions | Query membership and mutation presence cannot be treated as prevalence. No susceptibility threshold is inferred. |
| Study/sampling design | Multi-label source-checked annotations; separate unverified title-cue matrix | One paper may contain a clinical trial and laboratory experiment; a cohort can appear in several publications. |

The compact matrix counts publications with information for each domain. The full matrix counts **distinct RefIDs** for each country/domain/category. Multi-country and multi-category totals overlap. A zero is a count in this snapshot, not evidence of absent resistance or absent research. Unmapped geography and publications lacking selected-source geography remain explicit rows.

## Files and reproducibility

- `data/studies/catalogue.csv`: IDs, bibliographic facts, source links and index/export membership.
- `data/studies/evidence.csv`: compact reference-country-year-drug metadata, gene/source, exact/bounded year status and source record counts. No patient or isolate identifiers are published.
- `data/studies/signals.csv`: unverified title labels, domain and exact regular-expression rule. These never enter the source-supported matrix or meta-analysis eligibility.
- `data/studies/annotations.csv`: original factual classifications for nine publications, with per-field source links, cohort label, extraction date and limitations. These were checked by Codex against primary abstracts, are a single extraction, and have **not been independently dual-reviewed**.
- `data/studies/manifest.json`: exact search filters, versions, pagination totals, timestamps, raw-response SHA-256 values and generated-file hashes. Form payload identifiers are replaced with a request hash.
- [study_query.py](study_query.py): complete native retrieval/normalization code. Repository command: `python scripts/fetch_study_metadata.py --refresh`.
- [study_matrix.py](study_matrix.py): browser-compatible table/ledger transformations. Notebook 10 exposes the distinct-count pivot operation and exports semantic HTML/CSV.

Raw responses stay in ignored `_build/` caches. Refresh can change the data, counts and schema. Cached replay preserves original retrieval timestamps. Country aliases are explicit; ambiguous “Korea”, regional labels and abbreviated territory labels are not guessed. Repeated subject/isolate labels in Stanford's displayed tables are restored only within a reference; identical clone metadata are collapsed and conflicting join keys fail.

## Meta-analysis scope

The user selected **overall TDR among ART-naive populations**. Notebook 12 uses the original CC0 Rhee 2015 S1 Table with original study identifiers, source sampling fields and PMIDs. It links to the broader matrix using nonempty PMIDs while retaining unlinked studies. A shared publication ID does not establish equality of samples across releases.

UN M49 determines African country/area membership. The original regional labels remain in the audit; the source's Northern Africa label for Iran is not adopted. Historical country names containing commas are protected before splitting.

The primary conditional subset contains **71 single-country studies**, **28 countries**, and **6,144 reported participants**, with median collection years **1994–2011**. Of the 97 wholly African source rows, 10 are multicountry without country denominators and 16 have incompatible reported denominators/percentages. The remaining 190 of the 287 source rows are outside the wholly African scope. See `data/meta_analysis/harmonized_studies.csv` for every decision.

**Numerators are reconstructed, not directly reported.** The pipeline enumerates integer counts consistent with rounding to 0.1 percentage point and requires exactly one candidate. The candidate must lie between the largest mutation marginal and the sum of marginals capped at N. Marginals are bounds, never summed as people. This remains conditional on the source N being the correct overall-TDR denominator. Exact original CPR reports were unreachable during preparation. Inconsistent values are not repaired by rounding. This exclusion process can introduce selection bias; the pooled result is not an estimate for all African studies.

The model uses study logits with approximate binomial variance, boundary-only continuity correction, REML heterogeneity and a modified Hartung–Knapp interval with scale at least one. A t-based prediction interval is approximate; tau-squared uncertainty is not fully propagated. The inverse-logit mean is a typical included-study proportion, not an arithmetic continental population prevalence. Independence across publication cohorts and sampling assumptions remain to be adjudicated for formal use. Country subgroup display requires at least three included studies but does not imply national representation or adequate precision.

Notebook 12 includes forest/funnel displays, Q/I²/tau², a prediction interval, correction and sampling sensitivity checks, leave-one-country-out influence, and a screening template with unassessed fields. It does not claim a new systematic review, current whole-database meta-analysis, risk-of-bias assessment or GRADE rating. Descriptive funnel asymmetry is not equated with publication bias, and no automatic Egger test is used for mechanically related prevalence effects and standard errors.

Run `python scripts/build_meta_inputs.py --refresh` to rebuild the original-source input and geographic frame. The model is in [meta_analysis_tools.py](meta_analysis_tools.py); its equations, numerical boundary checks and analytic test oracle are documented. All figures and tables derive from the computed objects.

## Citations, attributions and rights

Credit **Stanford University HIV Drug Resistance Database** and the contributing studies. Recommended database reference: Rhee S-Y, Gonzales MJ, Kantor R, Betts BJ, Ravela J, Shafer RW. (2003). *Human immunodeficiency virus reverse transcriptase and protease sequence database.* Nucleic Acids Research 31:298–303. [DOI](https://doi.org/10.1093/nar/gkg100). Source endpoints: [reference index](https://hivdb.stanford.edu/cgi-bin/Reference.cgi), [GenoRx downloads](https://hivdb.stanford.edu/pages/geno-rx-datasets.html), [genotype-phenotype data](https://hivdb.stanford.edu/pages/genopheno.dataset.html), [IN query](https://hivdb.stanford.edu/HIVDB3/inhibitors-mutations/IN/), [CA query](https://hivdb.stanford.edu/HIVDB3/inhibitors-mutations/CA/), [citation guidance](https://hivdb.stanford.edu/pages/citation.html), [FAQs/terms](https://hivdb.stanford.edu/pages/FAQ/FAQ.html).

Source-checked annotation references: [Cahn 2013, SAILING](https://pubmed.ncbi.nlm.nih.gov/23830355/); [Gupta 2023, CALIBRATE](https://pubmed.ncbi.nlm.nih.gov/36566079/); [Abdullahi 2023](https://pubmed.ncbi.nlm.nih.gov/37367727/); [Margot 2025, CAPELLA](https://pubmed.ncbi.nlm.nih.gov/39873394/); [Turkova 2021, ODYSSEY](https://pubmed.ncbi.nlm.nih.gov/34965338/); [Frange 2021](https://pubmed.ncbi.nlm.nih.gov/34369051/); [Charpentier 2011](https://pubmed.ncbi.nlm.nih.gov/21599597/); [Margot 2022, study 4072](https://pubmed.ncbi.nlm.nih.gov/35028668/); [Kelley 2024, PURPOSE 2](https://pubmed.ncbi.nlm.nih.gov/39602624/). Their methods and full texts require further review before extending these annotations to a formal synthesis.

Meta-analysis data: [Rhee et al. 2015](https://doi.org/10.1371/journal.pmed.1001810), [CC0 S1 Table](https://doi.org/10.1371/journal.pmed.1001810.s004), [correction](https://doi.org/10.1371/journal.pmed.1001845). Geography: [UN Statistics Division M49](https://unstats.un.org/unsd/methodology/m49/) factual codes and group membership; [Natural Earth public-domain outlines](https://www.naturalearthdata.com/about/terms-of-use/) via Plotly 6.2.0; ISO identifiers via pycountry/iso-codes.

Methods: [Viechtbauer 2010](https://doi.org/10.18637/jss.v036.i03); [Röver, Knapp and Friede 2015](https://doi.org/10.1186/s12874-015-0091-1); [Cochrane synthesis guidance](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10); [missing-evidence guidance](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-13); [PRISMA 2020](https://www.prisma-statement.org/prisma-2020).

Only factual metadata, original classifications/code, computed aggregates and original graphics are redistributed. Article text, abstracts, sequences, website artwork, logos and publication figures are not bundled. Public access is not a blanket license to the Stanford website or linked papers; retain their source terms. The PLOS CC0 designation applies to its specific source, not all HIVDB content. Software dependencies retain their own licenses.
