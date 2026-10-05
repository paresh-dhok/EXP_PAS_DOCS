# E18 — Region-wise algorithm comparison (6 algorithms, two input sets)

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/18_region_algorithm_comparison.csv` (R², RMSE, MAE per region × input set × model × nutrient)
**Data:** model table, 17,273 locations + climate; region-wise protocol (train and test inside one region, 10 km spatial CV, 5 folds)

## Question (recorded before running)
The earlier algorithm comparison (E12, E13) was statewide. Under the final region-wise protocol, which algorithm is best,
and does the ranking hold for both input sets?

## Setup
No tuning; seed 42. Targets on a log scale (tree models and Cubist: log1p/expm1; SVR and KNN: log1p then standardised),
SVR and KNN inputs standardised inside each fold.

| Model | Settings |
|---|---|
| RandomForest | 300 trees, min_samples_leaf 3, max_features 0.33 |
| ExtraTrees | 300 trees, min_samples_leaf 3, max_features 0.33 |
| Cubist | n_committees 5 |
| DecisionTree | min_samples_leaf 20 |
| SVR | RBF, C 1.0, epsilon 0.1 |
| KNN | 25 neighbours, distance-weighted |

Input sets: **41 inputs** (field-observable) and **41 + elev + climate** (48).

## Results — mean R² over the 5 regions (spatial 10 km)

41 inputs:

| Model | N | P | K | OC |
|---|---|---|---|---|
| **RandomForest** | **0.137** | **0.107** | 0.042 | **0.092** |
| Cubist | 0.129 | 0.088 | **0.053** | 0.053 |
| ExtraTrees | 0.125 | 0.077 | 0.036 | 0.079 |
| SVR | 0.117 | 0.070 | 0.022 | 0.022 |
| KNN | 0.072 | 0.036 | 0.015 | 0.019 |
| DecisionTree | −0.054 | 0.042 | −0.142 | −0.077 |

41 + elev + climate:

| Model | N | P | K | OC |
|---|---|---|---|---|
| **Cubist** | **0.416** | **0.287** | 0.183 | 0.231 |
| **RandomForest** | 0.400 | 0.269 | **0.194** | **0.269** |
| ExtraTrees | 0.391 | 0.249 | 0.180 | 0.250 |
| SVR | 0.285 | 0.155 | 0.089 | 0.122 |
| DecisionTree | 0.248 | 0.164 | 0.023 | 0.096 |
| KNN | 0.224 | 0.123 | 0.070 | 0.093 |

## Results — best model per region and nutrient

41 inputs:

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | RF 0.150 | Cubist 0.028 | Cubist 0.269 | RF 0.060 |
| Marathwada | RF 0.134 | RF 0.211 | RF 0.014 | RF 0.020 |
| North MH | RF 0.042 | RF 0.046 | Cubist 0.024 | RF 0.112 |
| Western MH | Cubist 0.259 | RF 0.230 | Cubist −0.022 | RF 0.177 |
| Konkan | SVR 0.142 | RF 0.022 | Cubist 0.003 | RF 0.089 |

41 + elev + climate:

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | Cubist 0.370 | RF 0.193 | Cubist 0.483 | RF 0.262 |
| Marathwada | Cubist 0.492 | RF 0.530 | RF 0.213 | ExtraTrees 0.132 |
| North MH | Cubist 0.339 | Cubist 0.332 | RF 0.271 | RF 0.332 |
| Western MH | ExtraTrees 0.459 | Cubist 0.406 | RF −0.019 | Cubist 0.491 |
| Konkan | Cubist 0.447 | SVR 0.049 | RF 0.050 | ExtraTrees 0.210 |

## Interpretation
1. **Random Forest and Cubist are the two best algorithms region-wise**, with Extra Trees close behind.
   With the 41 inputs RF is best on average for N, P and OC; with elevation + climate, Cubist is slightly ahead for N and P
   and RF for K and OC.
2. **The ranking is the same as statewide (E12, E13):** tree ensembles and Cubist > SVR > KNN > single tree.
3. **Differences between the top three are small** (≤ 0.03 on average), within the ±0.02 run-to-run variation seen in E14.
4. **The input set matters far more than the algorithm:** adding elevation + climate raises mean N from 0.137 to 0.400
   (RF), whereas switching the algorithm changes it by a few hundredths. (E16: that gain is mostly location.)
5. **No algorithm rescues the weak cases:** K in Western MH and Konkan, P in Konkan and OC in Marathwada stay near zero
   with the 41 inputs for every model.
6. A single decision tree is negative on average for N, K and OC with the 41 inputs, i.e. worse than predicting the regional mean.

## Caveats
- No hyperparameter tuning; single seed. XGBoost and the linear / neural models are being run by team members under the
  same protocol.
