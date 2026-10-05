# E17 — Random 70/30, 80/20, 60/40 vs 10 km spatial CV; clustered vs de-clustered (region-wise)

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/17_split_comparison_region.csv` (per region); tables below are means over the 5 regions

## Question (recorded before running)
How much do (a) the split ratio, (b) random vs spatial testing, (c) clustered vs de-clustered data and (d) adding
elevation + climate change the reported R², under the region-wise protocol?
Expectation: random splits inflate R² far more than the split ratio changes it; clustered data inflates random-split
scores further (identical inputs for samples within 30 m); spatial CV removes most of this.

## Data
- **De-clustered:** one row per independent location, 17,273 rows (final dataset with composite).
- **Clustered:** every original clean lab sample with its own N, P, K, OC, pH, EC, linked through `ids_merged` to its
  location's composite, terrain and climate values: **25,454 rows**. Samples within 30 m therefore share identical
  satellite/terrain/climate inputs. The 7,861 samples of the large placeholder clusters (> 10 within 30 m) are not included,
  because no composite/terrain/climate was computed for them.
- Region per row from `mh_candidates.parquet`; 10 km blocks computed from each row's own coordinates.

## Setup
- Model: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)`, log1p/expm1 target.
- Input sets: **41 inputs** (final field-observable set) and **41 + elev + climate** (48).
- Evaluations inside each region: random `train_test_split` with test sizes 0.3, 0.2, 0.4 (`random_state=42`; training R²
  reported for 70/30), and 10 km spatial CV (`GroupKFold(5, shuffle=True, random_state=42)`).

## Results (mean R² over the 5 regions)

N
| Data | Inputs | train 70/30 | test 70/30 | test 80/20 | test 60/40 | spatial 10 km |
|---|---|---|---|---|---|---|
| clustered | 41 + elev + climate | 0.854 | 0.630 | 0.630 | 0.619 | 0.378 |
| clustered | 41 inputs | 0.764 | 0.359 | 0.364 | 0.347 | 0.128 |
| de-clustered | 41 + elev + climate | 0.874 | 0.590 | 0.599 | 0.587 | 0.400 |
| de-clustered | 41 inputs | 0.751 | 0.237 | 0.233 | 0.235 | **0.137** |

P
| Data | Inputs | train 70/30 | test 70/30 | test 80/20 | test 60/40 | spatial 10 km |
|---|---|---|---|---|---|---|
| clustered | 41 + elev + climate | 0.752 | 0.563 | 0.587 | 0.533 | 0.253 |
| clustered | 41 inputs | 0.603 | 0.324 | 0.347 | 0.293 | 0.095 |
| de-clustered | 41 + elev + climate | 0.749 | 0.445 | 0.479 | 0.427 | 0.269 |
| de-clustered | 41 inputs | 0.593 | 0.147 | 0.159 | 0.148 | **0.107** |

K
| Data | Inputs | train 70/30 | test 70/30 | test 80/20 | test 60/40 | spatial 10 km |
|---|---|---|---|---|---|---|
| clustered | 41 + elev + climate | 0.756 | 0.397 | 0.414 | 0.384 | 0.177 |
| clustered | 41 inputs | 0.695 | 0.214 | 0.239 | 0.209 | 0.035 |
| de-clustered | 41 + elev + climate | 0.765 | 0.395 | 0.404 | 0.367 | 0.194 |
| de-clustered | 41 inputs | 0.684 | 0.141 | 0.137 | 0.129 | **0.042** |

OC
| Data | Inputs | train 70/30 | test 70/30 | test 80/20 | test 60/40 | spatial 10 km |
|---|---|---|---|---|---|---|
| clustered | 41 + elev + climate | 0.780 | 0.470 | 0.484 | 0.458 | 0.259 |
| clustered | 41 inputs | 0.721 | 0.267 | 0.284 | 0.248 | 0.076 |
| de-clustered | 41 + elev + climate | 0.827 | 0.453 | 0.444 | 0.420 | 0.269 |
| de-clustered | 41 inputs | 0.739 | 0.188 | 0.205 | 0.175 | **0.092** |

## Interpretation
1. **The split ratio hardly matters:** 70/30, 80/20 and 60/40 differ by at most ~0.05 R².
2. **Random vs spatial testing is the big effect.** With the 41 inputs on de-clustered data, random splits give
   N 0.23–0.24 vs spatial 0.137; on clustered data N 0.35–0.36 vs 0.128 (≈ 3×).
3. **Clustered data inflates random-split scores** (41 inputs: N 0.359 vs 0.237, P 0.324 vs 0.147, K 0.214 vs 0.141,
   OC 0.267 vs 0.188), because samples within 30 m have identical inputs and leak between training and test.
   **Under spatial CV the difference disappears** (N 0.128 vs 0.137), so spatial CV neutralises this leakage.
4. **Elevation + climate raise every score**, but much more under random splits (N up to 0.63) than under spatial CV
   (0.38–0.40), consistent with E16 (they act largely as location).
5. **Training R² is 0.59–0.87**, far above every test score.
6. **From the honest setup to a literature-style setup, the same data moves from**
   N 0.137 → 0.630, P 0.107 → 0.587, K 0.042 → 0.414, OC 0.092 → 0.484 (de-clustered 41 inputs + spatial CV vs clustered
   + elevation + climate + random split), and to 0.75–0.85 if training R² is reported.

## Per-region highlights (from the results file)
Spatial 10 km, de-clustered:

| Region | 41 inputs: N / P / K / OC | 41 + elev + climate: N / P / K / OC |
|---|---|---|
| Vidarbha | 0.150 / 0.025 / 0.239 / 0.060 | 0.331 / 0.193 / **0.453** / 0.262 |
| Marathwada | 0.134 / 0.211 / 0.014 / 0.020 | 0.447 / **0.530** / 0.213 / 0.127 |
| North MH | 0.042 / 0.046 / 0.009 / 0.112 | 0.332 / 0.250 / 0.271 / 0.332 |
| Western MH | **0.216** / **0.230** / −0.030 / **0.177** | **0.447** / 0.339 / −0.019 / **0.443** |
| Konkan | 0.141 / 0.022 / −0.022 / 0.089 | **0.445** / 0.036 / 0.050 / 0.182 |

- The pattern (training ≫ random test ≫ spatial; clustered > de-clustered under random splits) holds in every region.
- Largest cluster leakage under random splits with the 41 inputs: Vidarbha P (0.370 clustered vs 0.096 de-clustered),
  North MH P (0.298 vs 0.114).
- Persistent failures even with elevation + climate under spatial CV: K in Western MH and Konkan (≤ 0.05),
  P in Konkan (0.036), OC in Marathwada (0.127).
- Literature-style numbers per region (clustered + elev + climate, random 80/20) reach N 0.73 and K 0.67 in Vidarbha,
  P 0.74 in Marathwada, OC 0.73 in Western MH.

## Use in the paper
A single table or figure: the same data, the same model, four design choices (split type, split ratio, de-clustering,
location-like covariates), showing which choices inflate the reported accuracy and by how much.
