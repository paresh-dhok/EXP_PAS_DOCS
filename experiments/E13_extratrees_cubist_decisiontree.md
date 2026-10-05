# E13 — Extra Trees, Cubist and a single decision tree (41 inputs)

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05 (after a kernel restart and the short setup cell)
**Results:** `results/13_et_cubist_tree.csv`
**Data:** model table, 17,273 locations; final 41 inputs (see E12); 10 km spatial blocks, 5 folds (same folds as before)
**New package:** `cubist` 1.2.2 (installed 2026-10-05 into the Anaconda base environment)

## Hypothesis (recorded before running)
1. Extra Trees ≈ Random Forest (within about ±0.02 R²).
2. A single decision tree is clearly below Random Forest, showing what averaging many trees gains.
3. Cubist is close to Random Forest, possibly slightly better for OC (as often reported in soil-mapping studies).

## Setup
All models use a log1p/expm1 target transform (`TransformedTargetRegressor`). No tuning. Seed 42.

| Model | Settings |
|---|---|
| DecisionTree | `DecisionTreeRegressor(min_samples_leaf=20)` |
| ExtraTrees | `ExtraTreesRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33)` |
| Cubist | `Cubist(n_committees=5)` (default 500 max rules) |

## Results — this experiment
| Model | N | P | K | OC |
|---|---|---|---|---|
| DecisionTree | 0.161 | −0.039 | −0.089 | 0.116 |
| ExtraTrees | 0.225 | 0.018 | 0.034 | 0.264 |
| Cubist | 0.246 | 0.016 | 0.052 | 0.270 |

RMSE, MAE and RPIQ for each model and nutrient are in the results file.

## All regression models so far (same 41 inputs, same folds; R²)
| Rank | Model | N | P | K | OC | Source |
|---|---|---|---|---|---|---|
| 1 | **Random Forest** | **0.272** | **0.041** | **0.055** | **0.291** | E11 |
| 2 | Cubist | 0.246 | 0.016 | 0.052 | 0.270 | E13 |
| 3 | Extra Trees | 0.225 | 0.018 | 0.034 | 0.264 | E13 |
| 4 | SVR | 0.215 | 0.007 | 0.047 | 0.231 | E12 |
| 5 | Decision tree | 0.161 | −0.039 | −0.089 | 0.116 | E13 |
| 6 | KNN | 0.153 | −0.009 | 0.034 | 0.209 | E12 |

## Interpretation
1. **Random Forest remains the best model for every nutrient.**
2. Hypothesis 1 **not confirmed:** Extra Trees is lower than RF by more than 0.02 (N −0.047, OC −0.027, K −0.021, P −0.023).
   Its fully random split points seem to suit these weak, noisy relationships less well.
3. Hypothesis 2 **confirmed:** a single tree is far below RF (N 0.161 vs 0.272, OC 0.116 vs 0.291) and negative for P and K.
   Averaging many trees roughly doubles OC skill.
4. Hypothesis 3 **partly confirmed:** Cubist is the second-best model and close to RF (N −0.026, K −0.003, OC −0.021),
   but not better for OC.
5. The ranking is consistent: ensembles of trees (RF, Cubist committees, ET) > kernel (SVR) > single tree and neighbours (KNN).
6. Across all six models, P and K stay ≈ 0. This matches the earlier findings: the inputs carry little information about
   available P and K, whatever the algorithm.

## Caveats
- No hyperparameter tuning for any model; single seed (42). Differences of about 0.02 between models may not be significant
  without repeated seeds.
