# Methodology notes

## Unit of analysis

The historical source is study-level surveillance data, not a population-based country survey. A country choropleth is therefore a visualization of the published study evidence represented in the source, not a statement that every mapped value is nationally representative.

## Country normalization

Country labels are normalized to ISO 3166-1 alpha-3 codes with `pycountry` plus a small transparent alias table for common historical or colloquial labels. Unmatched labels are retained and reported; they are never silently dropped.

## Multi-country studies

When a source row lists more than one country but provides only a combined study sample size, there is no defensible country-specific denominator. By default, multi-country rows:

- count toward evidence coverage for every parsed country;
- do not contribute to weighted country prevalence;
- remain available for separate sensitivity analysis.

## Weighted country prevalence

For a resistance outcome `p_i` reported as a percent in study `i`, with sample size `n_i`, the country summary is:

`sum(n_i * p_i) / sum(n_i)`

using eligible single-country rows with nonmissing outcome and sample size.

This is a descriptive pooled proportion, not a meta-analytic random-effects estimate. Study heterogeneity, sampling design, calendar time, recruitment setting, sequencing method, HIV subtype, and representativeness remain important.

## Missing values

Missing prevalence values remain missing. They are not converted to zero. A country may therefore have study coverage but no estimate for a particular drug class.

## Time

The default historical snapshot covers studies published through 2013 as described by the 2015 article. The notebooks show study/sample-year distributions but do not imply that the historical snapshot reflects present-day resistance patterns.

## Current-data workflow

A current HIVDB export should be normalized separately and retained with retrieval date, source URL, schema mapping, and raw-file checksum. Never overwrite a historical snapshot without preserving provenance.
