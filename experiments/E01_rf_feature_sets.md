# E01 — Random Forest baseline: four feature sets (+ random vs spatial CV)

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cell 24
**Results:** `results/01_rf_baseline_feature_sets.csv`
**Data:** `mh_final_dataset.parquet`, 17,620 locations (the 10 locations < 30 m apart were removed at the start of this cell)

## Question / hypothesis (before running)
Does combining field-sensor values (pH, EC) with Sentinel-2 predict N, P, K and OC better than either alone?
Expectation from the literature: satellite alone is weak for N, P and K, somewhat better for OC; fusion should help.

## Setup
| Item | Value |
|---|---|
| Model | `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, n_jobs=-1, random_state=42)` |
| Target transform | `TransformedTargetRegressor(func=log1p, inverse_func=expm1)` |
| Tuning | none (fixed settings) |
| Validation | spatial 5-fold `GroupKFold(shuffle=True, random_state=42)`; groups = 10 km grid blocks (1,567 blocks, median 5 locations per block) |
| Extra | random `KFold(5, shuffle=True, random_state=42)` once on set C |
| Metrics | pooled out-of-fold R², fold mean ± std R², RMSE, MAE, RPIQ |

| Set | Features | Count | Location? |
|---|---|---|---|
| A_satellite | 12 bands (reflectance) + 16 indices, single date ±3 days | 28 | No |
| B_sensor_pH_EC | pH, EC | 2 | No |
| C_fusion | A + B | 30 | No |
| D_fusion_plus_GPS | C + longitude, latitude | 32 | **Yes** |

## Results — spatial CV (10 km)
| Set | N R² | P R² | K R² | OC R² |
|---|---|---|---|---|
| A_satellite | 0.022 | −0.033 | −0.030 | 0.085 |
| B_sensor_pH_EC | 0.167 | 0.012 | −0.003 | 0.180 |
| C_fusion | 0.153 | 0.014 | 0.016 | **0.223** |
| D_fusion_plus_GPS | 0.576 | 0.301 | 0.247 | 0.519 |

Fold mean ± std (example, set C): N 0.154 ± 0.049, P 0.012 ± 0.023, K 0.015 ± 0.031, OC 0.220 ± 0.027.

RMSE / RPIQ (set C): N 145.1 kg/ha / 0.70; P 25.6 / 0.49; K 254.7 / 1.08; OC 0.382 % / 0.77.
RMSE / RPIQ (set D): N 102.6 / 0.99; P 21.5 / 0.58; K 222.8 / 1.23; OC 0.301 / 0.97.

## Results — random CV (set C only)
| | N | P | K | OC |
|---|---|---|---|---|
| Spatial CV | 0.153 | 0.014 | 0.016 | 0.223 |
| **Random CV** | **0.250** | 0.059 | 0.065 | **0.295** |

## Interpretation
- Satellite alone has almost no predictive power (R² ≈ 0 for N, P, K; 0.09 for OC).
- pH + EC alone beat the satellite (N 0.17, OC 0.18).
- Fusion helps slightly, mainly for OC (0.18 → 0.22).
- Adding GPS produces a large jump. This raised the question of what location is learning (→ E02, E03).
- Random CV inflates R² (N 0.15 → 0.25) because of spatial autocorrelation. Spatial CV is the honest test.

## Status under the "no location" rule
Sets A, B and C are **valid field-level results**. Set D uses location and is diagnostic only.
