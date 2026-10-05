# E07 — Variance decomposition and noise ceiling

**Date:** 2026-10-01
**Notebook:** cell run on 2026-10-01 (not yet saved to disk when this file was written)
**Results:** `results/06_noise_ceiling.csv` (file number 06; experiment ID E07, see the README note)
**Data:** `mh_model_dataset.parquet` with OC > 0.02 and EC > 0.005 → 33,842 samples (before de-clustering)

## Question (before running)
Within-district R² stayed ≈ 0 in E04–E06. Is that because the features are weak, or because field-level differences in
SHC data are mostly measurement noise? What is the **highest within-district R² any model could reach**?

## Method (log1p scale, the same scale as the models)
- **Same-spot clusters:** samples within 30 m of each other (connected components of 30 m pairs), clusters of size 2–10:
  **12,278 samples in 3,927 clusters**. Differences inside such a cluster = lab error + sampling error + micro-scale
  variation that a 10–30 m pixel cannot resolve.
- Pooled variance around group means: Σ(y − group mean)² / (n − number of groups).
  - `var_same_spot`: pooled within same-spot clusters (the noise)
  - `var_within_district`: pooled within districts, all 33,842 samples (what a within-district model must explain)
  - `var_total`: total variance
- `share_between_districts = 1 − var_within_district / var_total`
- **`noise_ceiling = 1 − var_same_spot / var_within_district`**

## Results
| Target | var same spot | var within district | var total | Share between districts | **Noise ceiling** | Achieved within-district (best, with GPS) |
|---|---|---|---|---|---|---|
| N | 0.054 | 0.112 | 0.284 | 0.605 | **0.522** | 0.125 |
| P | 0.127 | 0.251 | 0.471 | 0.467 | **0.494** | 0.061 |
| K | 0.098 | 0.186 | 0.332 | 0.440 | **0.470** | 0.031 |
| OC | 0.012 | 0.019 | 0.047 | 0.602 | **0.385** | 0.038 |
| pH | 0.001 | 0.003 | 0.008 | 0.586 | 0.603 | — |
| EC | 0.009 | 0.020 | 0.030 | 0.338 | 0.521 | — |

## Interpretation
1. **44–61 % of all variance is between districts**, which matches the district-average R² (N 0.62, OC 0.61).
2. **Within districts, about half of the variance is noise**: samples at the same spot disagree about half as much as different fields do.
3. **The other half is real field-level variation.** A perfect model could reach within-district R² ≈ 0.39–0.52.
   Our models reach 0.02–0.12 with GPS and ≈ 0 without. Real field-level signal exists, but none of the bare-soil
   features capture it.
4. The ceiling is conservative: some "same spot" pairs are actually neighbouring fields, so the true ceiling is, if anything, higher.

## Hypothesis generated (not yet tested)
Field-level available N, P and K are driven mainly by **management** (fertiliser, irrigation, crop type and rotation).
This is invisible in bare soil but potentially visible in **crop phenology** (an NDVI time series over the previous kharif/rabi seasons).
