# Study notebook validation

Validated on November 16, 2026, using the versioned input snapshots.

- All 13 notebooks executed during a strict Jupyter Book build with execution errors and Sphinx warnings treated as failures.
- All 13 automated tests passed, including the independent equal-variance REML oracle, zero-heterogeneity boundary, invalid-count gates, rounding ambiguity, geographic exclusions and distinct-publication matrix rules.
- The exported country matrix contains 152 rows and 306 domain/category columns. Every HTML table value agrees with the computed pivot and exported source ledger.
- The 71 conditional study effects, variances, weights and pooled summary agree with the analytical exports. Input hashes, package versions and numerical results are recorded in [study_validation.json](study_validation.json).
- Headless Microsoft Edge rendered the four new Book chapters without JavaScript errors: 14 interactive plots, 19 semantic tables, country map outlines and the orthographic globe. The matrix, forest plot, evidence maps, globe controls and research-question table were visually inspected. Screenshot artifacts remain in the ignored local build directory.
- CI and Pages builds repeat notebook execution and exported-output checks. Their results are available in [GitHub Actions](https://github.com/jltobias/JupyterLite-HIVDB-Drug-Resistance-Maps/actions).

These checks validate implementation and rendering. They do not constitute independent data extraction, cohort-overlap adjudication, risk-of-bias assessment or validation of the reconstructed event counts against original reports. See the [scope and methods](../content/study_matrix_methods.md).
