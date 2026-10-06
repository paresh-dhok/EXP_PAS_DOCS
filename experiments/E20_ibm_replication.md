# E20 — Repeating the IBM study (Kaur, Das & Hazra, IGARSS 2020) on our data

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/20_ibm_replication.csv`
**Reference:** G. Kaur, K. Das, J. Hazra, "Soil nutrients prediction using remote sensing data in Western India: an
evaluation of machine learning models", IGARSS 2020, DOI 10.1109/IGARSS39084.2020.9324201

## The IBM study (from the full paper)
- Area: Pune and Ahmednagar districts; Soil Health Card data, March–June 2016.
- Satellite: Landsat-8 (7 bands) and Sentinel-2 (13 bands), April–May 2016, plus BI, SI, HI, CI, RI, NDVI.
- Static inputs: elevation (CartoDEM), slope, aspect, flow direction; annual precipitation and radiation (WorldClim, 1 km);
  sand, silt, clay (SoilGrids).
- Value ranges shown: N and K 150–350 kg/ha, P 0–30 kg/ha, OC 0–1 %.
- Evaluation: random 80 % / 20 % split; 10-fold cross-validation on the training part. Number of samples not stated.
- Models: MLR, RFR, SVR, GB (R `caret`). Best: RFR. "R² for all nutrients varies from 8 %–32 %."

IBM Table 4, RFR on test data:

| | N | P | K | OC |
|---|---|---|---|---|
| R² | 0.294 | 0.225 | 0.322 | 0.182 |
| RMSE | 35.464 | 5.727 | 54.979 | 0.138 |
| sMAPE | 0.125 | 0.362 | 0.209 | 0.274 |

## Question (recorded before running)
With their two districts, their kind of inputs, their value ranges, their four models and their random 80/20 test,
how do our 2024 data compare with their reported R², RMSE and sMAPE? And what happens under our spatial test?

## Setup
- Locations: districts 490 (Pune) and 466 (Ahmednagar/Ahilyanagar) from the model table: **723 locations, 83 blocks (10 km)**.
- Inputs "IBM-like": composite satellite (33) + terrain with elevation (7) + climate (6) = 46; second set adds pH, EC.
  Not available: aspect, flow direction, SoilGrids texture, radiation.
- Two versions of the targets: **IBM value range** (N, K 150–350; P 0–30; OC 0–1) and **our full range**.
- Models: MLR (`LinearRegression`, standardised inputs), RFR (300 trees, min_samples_leaf 3, max_features 0.33),
  GB (`GradientBoostingRegressor` defaults), SVR (RBF, C 1, standardised inputs). Seed 42. **No log transform** (as in IBM).
- Evaluation: random 80/20 (`random_state=42`) and 10 km spatial CV (5 folds).
- sMAPE = mean(|y − ŷ| / ((|y| + |ŷ|) / 2)).

## Results — IBM value range, IBM-like inputs
Locations per nutrient: N 438, P 263, K 299, OC 357 (test sets of about 53–88).

Random 80/20:

| Model | R² N | R² P | R² K | R² OC | RMSE N | RMSE P | RMSE K | RMSE OC | sMAPE N | sMAPE P | sMAPE K | sMAPE OC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MLR | 0.466 | −0.073 | −0.180 | −0.063 | 29.58 | 8.50 | 63.62 | 0.302 | 0.116 | 0.483 | 0.238 | 0.564 |
| **RFR** | **0.472** | **0.198** | 0.052 | **0.275** | 29.41 | 7.35 | 57.02 | 0.249 | 0.107 | 0.415 | 0.221 | 0.457 |
| GB | 0.425 | 0.176 | −0.060 | 0.198 | 30.67 | 7.45 | 60.28 | 0.262 | 0.113 | 0.411 | 0.228 | 0.450 |
| SVR | 0.110 | −0.098 | 0.056 | 0.039 | 38.18 | 8.60 | 56.90 | 0.287 | 0.132 | 0.451 | 0.212 | 0.508 |

Spatial 10 km CV, R²:

| Model | N | P | K | OC |
|---|---|---|---|---|
| MLR | 0.281 | −0.409 | −0.175 | −0.141 |
| RFR | 0.207 | −0.018 | 0.006 | 0.093 |
| GB | 0.192 | −0.124 | −0.206 | −0.033 |
| SVR | 0.056 | −0.085 | −0.064 | 0.030 |

## Results — our full range, IBM-like inputs (723 locations)
Random 80/20:

| Model | R² N | R² P | R² K | R² OC | RMSE N | RMSE P | RMSE K | RMSE OC | sMAPE N | sMAPE P | sMAPE K | sMAPE OC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MLR | 0.127 | 0.096 | 0.031 | 0.234 | 50.89 | 36.78 | 150.05 | 0.545 | 0.268 | 0.613 | 0.595 | 0.537 |
| **RFR** | **0.395** | **0.498** | **0.182** | **0.361** | 42.35 | 27.40 | 137.84 | 0.498 | 0.218 | 0.453 | 0.495 | 0.415 |
| GB | 0.335 | 0.437 | 0.111 | 0.346 | 44.42 | 29.01 | 143.70 | 0.504 | 0.229 | 0.484 | 0.517 | 0.443 |
| SVR | 0.093 | 0.121 | −0.009 | 0.313 | 51.87 | 36.25 | 153.14 | 0.517 | 0.246 | 0.628 | 0.573 | 0.473 |

Spatial 10 km CV, R²: MLR 0.136 / −0.165 / −0.234 / −0.034; RFR 0.013 / 0.226 / 0.043 / 0.322;
GB −0.200 / 0.049 / −0.074 / 0.275; SVR 0.081 / −0.016 / −0.104 / 0.187 (N / P / K / OC).

## Effect of adding pH, EC (RFR, random 80/20, R²)
| Range | Inputs | N | P | K | OC |
|---|---|---|---|---|---|
| IBM range | IBM-like | 0.472 | 0.198 | 0.052 | 0.275 |
| IBM range | + pH, EC | 0.521 | 0.202 | 0.078 | 0.282 |
| Full range | IBM-like | 0.395 | 0.498 | 0.182 | 0.361 |
| Full range | + pH, EC | 0.397 | 0.518 | 0.231 | 0.376 |

## Comparison with IBM (RFR, random 80/20, IBM value range)
| | N | P | K | OC |
|---|---|---|---|---|
| R²: IBM / ours | 0.294 / **0.472** | **0.225** / 0.198 | **0.322** / 0.052 | 0.182 / **0.275** |
| RMSE: IBM / ours | 35.46 / **29.41** | **5.73** / 7.35 | **54.98** / 57.02 | **0.138** / 0.249 |
| sMAPE: IBM / ours | 0.125 / **0.107** | **0.362** / 0.415 | **0.209** / 0.221 | **0.274** / 0.457 |

## Interpretation
1. **Same order of magnitude as IBM.** Under their conditions our Random Forest is better for N on all three metrics,
   better for OC on R² but worse on RMSE and sMAPE, slightly worse for P, and clearly worse for K on R² (similar RMSE and sMAPE).
2. **Random Forest is the best model in both studies**; MLR and SVR are the weakest.
3. **The value range drives RMSE and sMAPE.** Restricting to IBM's ranges lowers our N RMSE from 42.4 to 29.4 and
   sMAPE from 0.218 to 0.107. RMSE and sMAPE are therefore not comparable between studies with different value ranges.
4. **The random split inflates these results too.** In the same two districts, RFR R² falls from 0.472 to 0.207 (N),
   0.198 to −0.018 (P) and 0.275 to 0.093 (OC) under spatial CV (IBM range). IBM's reported R² (random split, with
   elevation and climate) would probably also be lower under spatial testing.
5. pH and EC add a little (N 0.472 → 0.521 in the IBM range).

## Caveats
- **Small sample:** 723 locations (263–438 in the IBM ranges); the 20 % test sets have only about 53–145 locations,
  so single-split R² values are uncertain by roughly ±0.1. One random split, one seed.
- Different year (2024 vs 2016) and sensors (no Landsat-8); aspect, flow direction, soil texture and radiation not included.
- IBM's sample size, exact filtering and outlier handling are not stated, so the "IBM value range" is taken from the
  ranges described in their text.
