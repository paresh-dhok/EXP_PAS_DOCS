# E08 — Random 70/30 split vs spatial CV (why the literature reports higher accuracy)

**Date:** 2026-10-01
**Notebook:** cell run on 2026-10-01 (after the E06/E07 cells)
**Results:** `results/08_split_7030_vs_spatial.csv`
**Data:**
- Final de-clustered model table: 17,273 locations (final + terrain + composite), 10 km blocks (1,554)
- Raw data before de-clustering: `mh_model_dataset.parquet` with OC > 0.02 and EC > 0.005 → 33,842 samples

## Hypothesis (recorded before running)
A random 70/30 split (the common literature setup) gives much higher test R² than spatial CV for the same features,
and training R² is higher still. Data that is not de-clustered (placeholder clusters, near-duplicate locations) inflates
scores most, because near-copies fall into both training and test.

## Setup
- Model: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)` with a
  log1p/expm1 target transform (same as E01). No tuning.
- Random split: `train_test_split(test_size=0.3, random_state=42)`. Reported: train R² and test R².
- Spatial CV: 5-fold `GroupKFold(shuffle=True, random_state=42)` on 10 km blocks, pooled out-of-fold R².

| Feature set | Features | Location? |
|---|---|---|
| C_single_fusion | single-date 12 bands + 16 indices + pH, EC (30) | No |
| CCT_comp_fusion_terrain | composite 12 bands + 16 indices + 5 temporal std + pH, EC + 7 terrain (42) | No (but see the elevation caveat) |
| CCTG_plus_GPS / C_plus_GPS | the above + longitude, latitude | Yes |

## Results (R²)
| Data | Features | Eval | N | P | K | OC |
|---|---|---|---|---|---|---|
| final 17,273 | C_single_fusion | train | 0.694 | 0.468 | 0.618 | 0.746 |
| | | test 70/30 | 0.247 | 0.058 | 0.069 | 0.284 |
| | | **spatial CV** | **0.169** | **0.017** | **0.020** | **0.230** |
| final 17,273 | CCT_comp_fusion_terrain | train | 0.819 | 0.568 | 0.703 | 0.819 |
| | | test 70/30 | 0.527 | 0.185 | 0.212 | 0.443 |
| | | **spatial CV** | **0.409** | **0.108** | **0.116** | **0.370** |
| final 17,273 | CCTG_plus_GPS | train | 0.899 | 0.748 | 0.784 | 0.887 |
| | | test 70/30 | 0.741 | 0.447 | 0.408 | 0.640 |
| | | spatial CV | 0.606 | 0.334 | 0.267 | 0.525 |
| raw 33,842 | C_single_fusion | train | 0.733 | 0.524 | 0.656 | 0.763 |
| | | test 70/30 | 0.352 | 0.145 | 0.193 | 0.381 |
| raw 33,842 | C_plus_GPS | train | 0.906 | 0.761 | 0.780 | 0.875 |
| | | test 70/30 | **0.735** | **0.486** | **0.468** | **0.676** |

## Interpretation
1. **The hypothesis is confirmed.** For the same features and data, the evaluation design alone moves R² from ≈ 0.02–0.23
   (honest spatial CV) to 0.06–0.28 (random 70/30), 0.15–0.38 (random 70/30 on non-de-clustered data) and 0.47–0.76 (training R²).
   With GPS and raw data, the random split gives N 0.735 and OC 0.676, the range many published studies report.
2. **De-clustering matters.** Random-split test R² on the raw data is higher than on the de-clustered data
   (N 0.352 vs 0.247; OC 0.381 vs 0.284) because near-duplicate samples leak between training and test.
3. **New result: field-only model with composite + terrain.** Under spatial CV with no coordinates and no district input:
   **N 0.409, P 0.108, K 0.116, OC 0.370**. This is 2.4× the single-date fusion for N (0.169) and better for OC (0.230 → 0.370).
4. The within-district tests (E05/E06) showed ≈ 0 for these features. The gain therefore comes from **regional soil
   differences recognised through the field's own properties** (soil spectral signature, terrain), not from field-to-field
   detail within a district.

## Caveat / open check
Elevation (part of the terrain set) partly encodes region (Konkan low, plateau high) and may act as a hidden location
proxy. Before using CCT as the headline field-only result:
- (a) rerun without elevation
- (b) rerun with 50 km blocks
- (c) ablate composite vs terrain to see which part drives the gain

## Use in the report
A figure or table showing the same data evaluated four ways (train / random raw / random de-clustered / spatial).
It explains why literature R² values (often 0.7–0.9) are not comparable to honest spatial validation.

**Decision 2026-10-05:** the rows that use GPS (`CCTG_plus_GPS`, `C_plus_GPS`) are **excluded from the paper**.
Location inputs are not acceptable, so they stay only as a diagnostic record. The paper uses the no-GPS comparison:

| Satellite + pH/EC (no GPS) | N | P | K | OC |
|---|---|---|---|---|
| Spatial CV, de-clustered | 0.169 | 0.017 | 0.020 | 0.230 |
| Random 70/30, de-clustered | 0.247 | 0.058 | 0.069 | 0.284 |
| Random 70/30, raw (clustered) | 0.352 | 0.145 | 0.193 | 0.381 |
| Training R² (raw) | 0.733 | 0.524 | 0.656 | 0.763 |
