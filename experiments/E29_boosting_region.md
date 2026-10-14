# E29 — Gradient boosting models (LightGBM, XGBoost, HistGradientBoosting, CatBoost), tuned, region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 1 of a three-part cell; parts 2 and 3 are E30 and E31)
**Results:** `results/29_boosting_region.csv` (4 boosting models, with the most often chosen setting);
`results/29_all_models_region.csv` (final table: 16 models, all tuned)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Hypothesis (recorded before running)
The boosting models land within ±0.02 of Random Forest with the 41 inputs.

## Setup
- Outer folds `GroupKFold(5, shuffle=True, random_state=42)` inside each region (identical to E18–E28).
- Target log1p, standardised with training-fold mean and SD; back-transformed with expm1.
- Settings chosen on the training blocks only (one inner grouped split, one third of the training blocks held out).

| Model | Fixed | Settings tried |
|---|---|---|
| LightGBM 4.7.0 | 400 trees, learning rate 0.03, subsample 0.8, colsample 0.5, L2 5 | num_leaves {7, 15} × min_child_samples {20, 60} |
| XGBoost 3.4.1 | 400 trees, learning rate 0.03, subsample 0.8, colsample 0.5, L2 5 | max_depth {3, 5} × min_child_weight {5, 20} |
| HistGradientBoosting (scikit-learn 1.7.2) | 300 iterations, learning rate 0.04, max_features 0.5, L2 5, no early stopping | max_leaf_nodes {7, 15} × min_samples_leaf {20, 60} |
| CatBoost 1.2.10 | 300 iterations, learning rate 0.05, rsm 0.5, L2 5 | depth {4, 6} |

160 jobs; run time 4.8 min.

## Results — mean R² over the 5 regions (spatial 10 km), all 16 tuned models

| Model | 41 inputs: N | P | K | OC | + elev + climate: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| **LightGBM** | **0.145** | **0.118** | 0.043 | 0.087 | 0.392 | 0.250 | 0.173 | 0.246 |
| **HistGB** | 0.143 | 0.116 | 0.040 | 0.082 | 0.394 | 0.249 | 0.170 | 0.249 |
| **XGBoost** | 0.142 | 0.115 | 0.039 | **0.095** | 0.396 | 0.264 | 0.173 | 0.248 |
| **CatBoost** | 0.141 | 0.113 | 0.045 | 0.094 | 0.394 | 0.260 | 0.176 | 0.254 |
| Random Forest | 0.133 | 0.102 | 0.042 | 0.088 | 0.400 | 0.269 | 0.189 | **0.268** |
| Cubist | 0.126 | 0.082 | **0.054** | 0.058 | **0.425** | **0.292** | **0.198** | 0.253 |
| SVR | 0.121 | 0.063 | 0.034 | 0.038 | 0.282 | 0.152 | 0.103 | 0.127 |
| Extra Trees | 0.120 | 0.077 | 0.037 | 0.080 | 0.408 | 0.264 | 0.185 | 0.258 |
| MLP improved | 0.118 | 0.092 | 0.042 | 0.069 | 0.335 | 0.178 | 0.140 | 0.176 |
| KNN | 0.069 | 0.030 | 0.021 | 0.023 | 0.225 | 0.123 | 0.072 | 0.094 |
| Decision tree | 0.048 | 0.073 | −0.015 | 0.028 | 0.293 | 0.155 | 0.090 | 0.148 |
| ElasticNet | 0.036 | 0.036 | −0.012 | 0.006 | 0.209 | 0.146 | 0.064 | 0.137 |
| Ridge | 0.035 | 0.047 | −0.000 | 0.016 | 0.215 | 0.152 | 0.067 | 0.146 |
| Lasso | 0.035 | 0.035 | −0.012 | 0.007 | 0.218 | 0.150 | 0.060 | 0.136 |
| PLSR | 0.027 | 0.044 | −0.006 | 0.011 | 0.162 | 0.124 | 0.070 | 0.100 |
| Linear | 0.023 | 0.054 | −0.016 | 0.008 | 0.225 | 0.157 | 0.067 | 0.117 |

LightGBM per region, 41 inputs (R²):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.159 | 0.026 | 0.255 | 0.040 |
| Marathwada | 0.125 | 0.233 | 0.010 | 0.015 |
| North MH | 0.043 | 0.055 | 0.007 | 0.119 |
| Western MH | 0.255 | 0.235 | −0.033 | 0.200 |
| Konkan | 0.144 | 0.043 | −0.023 | 0.061 |

Region × nutrient cells won (41 inputs, 20 cells, 16 models): Cubist 5, CatBoost 4, LightGBM 3, XGBoost 3, HistGB 2,
MLP improved 2, Random Forest 1.

## Interpretation
1. **Hypothesis confirmed.** With the 41 inputs the four boosting models are +0.008 to +0.016 above Random Forest for N
   and P and within ±0.007 for K and OC. They are the best group for N and P, by about 0.01.
2. **The four boosting libraries are interchangeable:** they differ by ≤ 0.005 for N and P.
3. **With elevation + climate the order changes:** Cubist, Extra Trees and Random Forest are ahead of all four boosting
   models (N 0.40–0.43 vs 0.39). No model family is best in both input sets.
4. **The ceiling is unchanged.** After 16 tuned models from 7 families, the best mean R² with the 41 field-level inputs
   is 0.145 (N), 0.118 (P), 0.054 (K), 0.095 (OC). The seven best models are within 0.027 of each other for N.
5. No model wins more than 5 of the 20 region × nutrient cells.

## Caveats
- Small grids, one inner split, fixed number of trees (no early stopping); single seed. Differences of about 0.01 are
  within the noise of the procedure.
- LightGBM and CatBoost were installed on 2026-10-09 for this run.
