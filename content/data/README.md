# Generated data

The `studies/` and `meta_analysis/` directories additionally contain versioned factual snapshots for Notebooks 09–12. Their manifests, source links and hashes identify the exact inputs. See [study sources and definitions](../study_matrix_methods.md). Refresh with `python scripts/fetch_study_metadata.py --refresh` and `python scripts/build_meta_inputs.py --refresh` from the repository root. The following build-generated 2015 CSVs remain a separate dataset.

The GitHub Pages build populates this directory by running:

```bash
python scripts/fetch_plos_2015.py --output-dir content/data
```

Generated CSV/XLSX files are intentionally not committed in this starter bundle. This keeps provenance explicit and allows the build to retrieve the public source directly.
