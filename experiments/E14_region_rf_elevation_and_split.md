# E14 — Region-wise Random Forest: with vs without elevation, spatial CV vs random 70/30

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/14_region_rf_elevation_split.csv`
**Data:** model table, 17,273 locations; region from `mh_candidates.parquet` (used only to split the data)
**Protocol:** region-wise (final protocol from 2026-10-05; see `TEAM_SHARE/REGION_WISE_PROTOCOL.md`)

## Hypothesis (recorded before running)
1. Elevation raises R² inside regions too. E09 (with elevation) scored higher than the 41-input region reference.
2. A random 70/30 split inflates R² by about +0.1 to +0.2 over spatial CV (as in E10).
3. With elevation + random split gives the highest and most misleading numbers.

## Setup
- Model: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)`,
  log1p/expm1 target. No tuning.
- Feature sets: `without_elev_41` (final 41 inputs) and `with_elev_42` (the 41 + `elev`, appended as the last column).
- For each region separately:
  - spatial CV: 10 km blocks, `GroupKFold(5, shuffle=True, random_state=42)` on the region's blocks; pooled out-of-fold R²
  - random split: `train_test_split(test_size=0.3, random_state=42)` on the region's locations; test R² and training R²

## Results (R²)

Spatial CV inside the region:

| Region | Features | N | P | K | OC |
|---|---|---|---|---|---|
| Vidarbha | with elev | **0.184** | **0.054** | **0.274** | **0.148** |
| | without elev | 0.150 | 0.025 | 0.239 | 0.060 |
| Marathwada | with elev | **0.236** | **0.249** | **0.059** | **0.053** |
| | without elev | 0.134 | 0.211 | 0.014 | 0.020 |
| North MH | with elev | **0.081** | **0.102** | **0.120** | **0.212** |
| | without elev | 0.042 | 0.046 | 0.009 | 0.112 |
| Western MH | with elev | **0.364** | **0.242** | −0.037 | **0.265** |
| | without elev | 0.216 | 0.230 | **−0.030** | 0.177 |
| Konkan | with elev | **0.209** | −0.003 | **0.017** | **0.122** |
| | without elev | 0.141 | **0.022** | −0.022 | 0.089 |

Random 70/30, test:

| Region | Features | N | P | K | OC |
|---|---|---|---|---|---|
| Vidarbha | with elev | 0.321 | 0.137 | 0.435 | 0.263 |
| | without elev | 0.274 | 0.096 | 0.325 | 0.142 |
| Marathwada | with elev | 0.333 | 0.250 | 0.144 | 0.055 |
| | without elev | 0.202 | 0.195 | 0.068 | 0.023 |
| North MH | with elev | 0.221 | 0.225 | 0.260 | 0.319 |
| | without elev | 0.131 | 0.114 | 0.136 | 0.195 |
| Western MH | with elev | 0.452 | 0.276 | 0.049 | 0.454 |
| | without elev | 0.311 | 0.250 | 0.048 | 0.367 |
| Konkan | with elev | 0.321 | 0.099 | 0.181 | 0.292 |
| | without elev | 0.265 | 0.078 | 0.126 | 0.214 |

Random 70/30, training: 0.52–0.81 for every region, feature set and nutrient (full table in the results file).

## Interpretation
1. **The without-elevation spatial CV values reproduce the protocol reference table exactly**, so the setup is consistent.
2. **Hypothesis 1 confirmed: elevation raises spatial-CV R² inside regions in 18 of 20 cases.** Largest gains:
   Western MH N +0.148 (0.216 → 0.364), Marathwada N +0.102, North MH OC +0.100, Vidarbha OC +0.088.
   The two exceptions are small: Western MH K −0.007, Konkan P −0.025.
3. Within a region, elevation still separates sub-areas (for example hills and plains, the Ghats and the plateau), which
   differ in soil, rainfall and possibly in laboratory or district. So it carries both real landscape information and
   location-like information. The experiment cannot separate the two.
4. **Hypothesis 2 confirmed: the random split inflates R² inside regions**, without elevation by +0.03 to +0.15
   (e.g. Vidarbha N 0.150 → 0.274, North MH OC 0.112 → 0.195), and with elevation by up to +0.19 (Western MH OC 0.265 → 0.454).
5. **Hypothesis 3 confirmed:** with elevation + random split gives the highest numbers (N up to 0.452, OC up to 0.454,
   K 0.435 in Vidarbha). These are not honest estimates for new locations.
6. Training R² (0.52–0.81) is far above every test score, so the models overfit the training data.
7. The with-elevation spatial values are close to, but not identical with, E09 (e.g. Vidarbha N 0.184 here vs 0.177 in E09)
   although the model and inputs are the same. The only difference is the column order (elevation last here), which changes
   the random feature choices of the forest. **Differences of about ±0.01–0.02 between runs are therefore not meaningful**
   without repeated seeds.

## Decision needed
Whether to keep elevation out of the region-wise models (current rule) or allow it. Inside regions it gives clearly
higher scores, but it may partly act as location. Either way, the paper should report both versions.
