# E27 — Tuning the remaining models (RF, Extra Trees, Cubist, SVR, KNN, decision tree), region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/27_tuned_models_region.csv` (the 6 tuned models, with the most often chosen setting);
`results/27_all_models_tuned_region.csv` (final table: 6 tuned models + Linear, Ridge, Lasso, ElasticNet, PLSR, MLP_improved)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Why
E26 tuned the neural network (regularisation chosen on the training blocks, 5-network ensemble) while Random Forest,
Extra Trees, Cubist, SVR, KNN and the decision tree were still at fixed settings. For a like-for-like comparison the
same kind of tuning is applied to them.

## Hypothesis (recorded before running)
1. The tree ensembles gain only a little (about +0.01–0.02 on average).
2. KNN, SVR and the single decision tree gain more; the single tree stops being negative.
3. The top of the ranking does not change: Random Forest, Cubist and Extra Trees stay ahead.

## Setup
- Outer folds: `GroupKFold(5, shuffle=True, random_state=42)` inside each region (identical to E18–E26).
- Target: log1p, standardised with the training-fold mean and SD; predictions back-transformed with expm1.
- Settings chosen by lowest mean squared error on the **training blocks only** (inner `GroupKFold(3)`), then the model
  is refitted on the whole training fold and tested on the untouched fold.

| Model | Settings tried | Inner splits used |
|---|---|---|
| Decision tree | min_samples_leaf {5, 20, 50, 100} × max_depth {None, 6, 10} | 3 |
| KNN (standardised inputs) | n_neighbors {10, 25, 50, 100} × weights {distance, uniform} | 3 |
| SVR, RBF (standardised inputs) | C {0.3, 1, 3, 10} × epsilon {0.1, 0.3} | 3 |
| Cubist | (5 committees), (20 committees), (5 committees + 5 neighbours) | 1 |
| Extra Trees | max_features {0.2, 0.5} × min_samples_leaf {3, 15} | 1 |
| Random Forest | max_features {0.2, 0.5} × min_samples_leaf {3, 15} | 1 |

- Tree ensembles: 100 trees while comparing settings, 300 trees for the final model of each fold.
- 240 jobs (6 models × 5 regions × 2 input sets × 4 nutrients). Run time 21.6 min.
- A first attempt with larger grids (9 settings for the ensembles, 3 inner splits, 300 trees) was stopped unfinished
  after about 40 minutes; the reduced design above was used instead.

## Results — mean R² over the 5 regions (spatial 10 km)

41 inputs, untuned (E18) → tuned:

| Model | N | P | K | OC | Mean gain |
|---|---|---|---|---|---|
| Random Forest | 0.137 → 0.133 | 0.107 → 0.102 | 0.042 → 0.042 | 0.092 → 0.088 | −0.003 |
| Cubist | 0.129 → 0.126 | 0.088 → 0.082 | 0.053 → 0.054 | 0.053 → 0.058 | −0.001 |
| SVR | 0.117 → 0.121 | 0.070 → 0.063 | 0.022 → 0.034 | 0.022 → 0.038 | +0.006 |
| Extra Trees | 0.125 → 0.120 | 0.077 → 0.077 | 0.036 → 0.037 | 0.079 → 0.080 | −0.001 |
| KNN | 0.072 → 0.069 | 0.036 → 0.030 | 0.015 → 0.021 | 0.019 → 0.023 | 0.000 |
| Decision tree | −0.054 → 0.048 | 0.042 → 0.073 | −0.142 → −0.015 | −0.077 → 0.028 | +0.091 |

41 + elev + climate, untuned → tuned:

| Model | N | P | K | OC | Mean gain |
|---|---|---|---|---|---|
| Cubist | 0.416 → 0.425 | 0.287 → 0.292 | 0.183 → 0.198 | 0.231 → 0.253 | +0.013 |
| Extra Trees | 0.391 → 0.408 | 0.249 → 0.264 | 0.180 → 0.185 | 0.250 → 0.258 | +0.012 |
| Random Forest | 0.400 → 0.400 | 0.269 → 0.269 | 0.194 → 0.189 | 0.269 → 0.268 | −0.002 |
| Decision tree | 0.248 → 0.293 | 0.164 → 0.155 | 0.023 → 0.090 | 0.096 → 0.148 | +0.039 |
| SVR | 0.285 → 0.282 | 0.155 → 0.152 | 0.089 → 0.103 | 0.122 → 0.127 | +0.003 |
| KNN | 0.224 → 0.225 | 0.123 → 0.123 | 0.070 → 0.072 | 0.093 → 0.094 | +0.001 |

### Final comparison, every model in its tuned form (12 models)

| Model | 41 inputs: N | P | K | OC | + elev + climate: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Random Forest | **0.133** | **0.102** | 0.042 | **0.088** | 0.400 | 0.269 | 0.189 | **0.268** |
| Cubist | 0.126 | 0.082 | **0.054** | 0.058 | **0.425** | **0.292** | **0.198** | 0.253 |
| SVR | 0.121 | 0.063 | 0.034 | 0.038 | 0.282 | 0.152 | 0.103 | 0.127 |
| Extra Trees | 0.120 | 0.077 | 0.037 | 0.080 | 0.408 | 0.264 | 0.185 | 0.258 |
| MLP improved (E26) | 0.118 | 0.092 | 0.042 | 0.069 | 0.335 | 0.178 | 0.140 | 0.176 |
| KNN | 0.069 | 0.030 | 0.021 | 0.023 | 0.225 | 0.123 | 0.072 | 0.094 |
| Decision tree | 0.048 | 0.073 | −0.015 | 0.028 | 0.293 | 0.155 | 0.090 | 0.148 |
| ElasticNet (E23) | 0.036 | 0.036 | −0.012 | 0.006 | 0.209 | 0.146 | 0.064 | 0.137 |
| Ridge (E23) | 0.035 | 0.047 | −0.000 | 0.016 | 0.215 | 0.152 | 0.067 | 0.146 |
| Lasso (E23) | 0.035 | 0.035 | −0.012 | 0.007 | 0.218 | 0.150 | 0.060 | 0.136 |
| PLSR (E24) | 0.027 | 0.044 | −0.006 | 0.011 | 0.162 | 0.124 | 0.070 | 0.100 |
| Linear (E23) | 0.023 | 0.054 | −0.016 | 0.008 | 0.225 | 0.157 | 0.067 | 0.117 |

### Best tuned model per region and nutrient, 41 inputs (R² of the best model)

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.169 (MLP) | 0.032 (MLP) | 0.269 (Cubist) | 0.057 (RF) |
| Marathwada | 0.126 (ET) | 0.231 (MLP) | 0.016 (MLP) | 0.024 (ET) |
| North MH | 0.038 (RF) | 0.037 (RF) | 0.025 (Cubist) | 0.104 (ET) |
| Western MH | 0.265 (Cubist) | 0.216 (RF) | −0.021 (Cubist) | 0.167 (RF) |
| Konkan | 0.140 (RF) | 0.039 (MLP) | −0.002 (Cubist) | 0.093 (RF) |

Number of the 20 region × nutrient cells won, 41 inputs: Random Forest 7, Cubist 5, MLP improved 5, Extra Trees 3.
With elevation + climate: Cubist 8, Random Forest 6, Extra Trees 5, MLP improved 1.

Settings chosen most often (41 inputs, N): decision tree min_samples_leaf 100 (50 in Konkan); KNN 25–100 neighbours,
distance-weighted; SVR C 0.3–1.0, epsilon 0.3; Cubist 20 committees, no neighbours (5 in Western MH); Extra Trees
max_features 0.5, min_samples_leaf 3 in all regions; Random Forest varies by region.

## Interpretation
1. **Hypothesis 1: the ensembles gain less than expected.** With the 41 inputs, tuning changes Random Forest, Extra
   Trees and Cubist by −0.003 to −0.001 on average, i.e. nothing. With elevation + climate, Cubist and Extra Trees gain
   about +0.012 and Random Forest does not change. The small negative values are tuning noise: a setting chosen on the
   inner split is not guaranteed to beat the fixed setting on the outer fold.
2. **Hypothesis 2: confirmed only for the decision tree.** It gains +0.09 (41 inputs) and is positive for N, P and OC;
   K is still slightly negative (−0.015). SVR gains a little for K and OC (+0.012, +0.016). KNN does not change.
3. **Hypothesis 3: confirmed.** Random Forest and Cubist stay first and second with the 41 inputs; Cubist, Extra Trees
   and Random Forest stay the top three with elevation + climate.
4. **The five best models are within 0.015 of each other for N with the 41 inputs** (0.118–0.133), and no model wins
   more than 7 of the 20 region × nutrient cells. Under equal tuning there is no single clearly best algorithm for the
   field-level inputs.
5. **Tuning does not move the ceiling.** The best mean R² with the 41 inputs remains about 0.13 (N), 0.10 (P),
   0.05 (K) and 0.09 (OC). The chosen settings all favour strong smoothing (large leaves, many neighbours, low C,
   wide epsilon), which is what is expected when the signal is weak relative to the unexplained variation.

## Caveats
- The ensembles and Cubist were tuned on a reduced grid with a single inner split and 100 trees, to keep the run time
  practical. Their tuning is therefore rougher than that of SVR, KNN and the decision tree.
- Several chosen settings are at the edge of the grid (decision tree leaf 100, SVR epsilon 0.3 and C 0.3, Extra Trees
  leaf 3 and max_features 0.5), so slightly better settings may exist outside it.
- Single seed (42). Differences of about 0.01 between models are within the noise of the procedure.
- Boosting models (XGBoost, LightGBM) and stacking are still not run under this protocol.
