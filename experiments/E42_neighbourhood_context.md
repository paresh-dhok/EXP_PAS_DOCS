# E42 — Neighbourhood context: values of the nearest training samples as extra inputs

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E39–E41, reuses their data and functions)
**Results:** `results/42_neighbourhood_context.csv` (nutrient × inputs × test: R², RMSE)

## Why
Gupta & Patil (2026), J. Indian Soc. Remote Sens. 54:2405–2421, doi:10.1007/s12524-026-02443-9, report R² of
0.77 (N), 0.61 (P), 0.72 (K), 0.71 (OC) on 168,000 Karnataka Soil Health Card samples with LightGBM, using
"global geolocation and local neighbourhood context". Only the abstract was available: it does **not** state how the
neighbourhood context is built, how many neighbours, or how the data were split. This experiment is therefore **our own
implementation** of neighbourhood context, similar in spirit, not a replication of their method.

No blind hypothesis: the cell was test-run before it was given (identical numbers).

## Setup
- Data, base inputs and model as E39–E41: clustered `mh_model_dataset` (33,877), **39 inputs** (12 single-date bands,
  16 indices, pH, EC, elevation, 6 climate, longitude, latitude), LightGBM fixed settings, log1p target, statewide.
  (The cell labels this set "50 inputs"; that label is wrong — it is the 39-input single-date set.)
- **Neighbourhood features (4):** from the 10 nearest **training** samples (metric coordinates, `cKDTree`):
  inverse-distance-weighted mean of log1p(target) (distance floor 1 m), log1p value of the nearest one, log1p
  distance to the nearest one, standard deviation of the 10 log1p values.
- **No leakage:** neighbours are always taken from the training part of the split or fold only. For training rows the
  sample itself is excluded (11 nearest queried, the first dropped).
- Tests: random 70/30 (`random_state=42`) and 10 km spatial CV (5 folds). Run time 0.1 min.

## Results

| Inputs | Test | R² N | R² P | R² K | R² OC | RMSE N | RMSE P | RMSE K | RMSE OC |
|---|---|---|---|---|---|---|---|---|---|
| 39 inputs | Random 70/30 | 0.774 | 0.499 | 0.465 | 0.686 | 74.8 | 17.39 | 190.7 | 0.234 |
| 39 inputs | Spatial 10 km | 0.598 | 0.334 | 0.256 | 0.543 | 100.7 | 20.12 | 223.3 | 0.287 |
| **39 inputs + neighbourhood** | **Random 70/30** | **0.812** | **0.606** | **0.551** | **0.712** | 68.3 | 15.41 | 174.7 | 0.224 |
| 39 inputs + neighbourhood | Spatial 10 km | 0.661 | 0.375 | 0.308 | 0.537 | 92.5 | 19.49 | 215.4 | 0.289 |
| Gupta & Patil 2026 (Karnataka) | not stated | 0.77 | 0.61 | 0.72 | 0.71 | | | | |

## Interpretation
1. **Neighbourhood context raises the random-split R²** by 0.03–0.11 (P +0.107, K +0.086, N +0.038, OC +0.026).
   With it, N, P and OC are at or above the values reported for Karnataka; K is lower.
2. **Under 10 km spatial CV the gain is smaller and shrinks for OC** (N +0.063, P +0.041, K +0.052, OC −0.006):
   the neighbour values help most when a measured sample lies very close to the test field.
3. Random 70/30 → spatial 10 km still costs 0.15–0.24 with neighbourhood context, as without it (E41).

## Caveats
- One seed, one split. k = 10 and the four features were chosen by us, not tuned and not taken from the paper.
- Comparison with Gupta & Patil is indicative only: different state, sensor (Landsat vs Sentinel-2), sample
  count, and unknown validation design. Get the full text before writing the comparison in the paper.
