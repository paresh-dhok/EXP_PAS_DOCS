# E12 — SVR and KNN regression, and low/medium/high class prediction (41 inputs)

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/12_svr_knn_regression.csv`, `results/12_class_prediction.csv`
**Data:** model table, 17,273 locations; 10 km spatial blocks, 5 folds (same folds as all earlier experiments)

## Inputs (final 41-feature set, decided 2026-10-05)
- Sensor (2): `pH`, `EC`
- Satellite composite (33): 12 bands `c_B01…c_B12`, 16 indices `c_NDVI…c_R_B6B5`, 5 variability features `c_std_*`
- Terrain without elevation (6): `slope`, `tpi_150m`, `tpi_500m`, `tpi_1km`, `rough_90m`, `relpos_2km`
- Not used: `elev`, longitude, latitude, district, single-date bands, AOT, WVP

## Hypothesis (recorded before running)
1. SVR and KNN score at or below Random Forest on the same 41 inputs (RF, E11: N 0.272, P 0.041, K 0.055, OC 0.291).
2. For the classes, plain accuracy looks high for N because ~80 % of fields are "low". Balanced accuracy (chance = 0.333)
   is the fair measure and will be only modestly above chance.

## Setup
**Regression**
- KNN: `StandardScaler` + `KNeighborsRegressor(n_neighbors=25, weights="distance")`
- SVR: `StandardScaler` + `SVR(kernel="rbf", C=1.0, epsilon=0.1)`
- Target: log1p, then standardised (`TransformedTargetRegressor`); predictions back-transformed. Scalers fitted on training folds only.
- No tuning.

**Classes** (official Soil Health Card limits: low < lower limit, medium = between the limits (inclusive), high > upper limit)

| Nutrient | Limits | Class share (low / medium / high) |
|---|---|---|
| N (kg/ha) | 280, 560 | 80.6 % / 15.2 % / 4.2 % |
| P (kg/ha) | 10, 25 | 16.5 % / 60.1 % / 23.5 % |
| K (kg/ha) | 110, 280 | 2.8 % / 26.8 % / 70.4 % |
| OC (%) | 0.5, 0.75 | 57.5 % / 23.9 % / 18.6 % |

- KNN: `StandardScaler` + `KNeighborsClassifier(n_neighbors=25, weights="distance")`
- SVC: `StandardScaler` + `SVC(kernel="rbf", C=1.0, class_weight="balanced")`
- RF: `RandomForestClassifier(n_estimators=300, min_samples_leaf=3, max_features=0.33, class_weight="balanced", random_state=42)`
- Majority baseline: always predict the most common class of the training folds.
- Metrics: accuracy, balanced accuracy (mean recall over the 3 classes; chance = 0.333), macro F1.

## Results — regression (R², spatial CV)
| Model | N | P | K | OC |
|---|---|---|---|---|
| KNN | 0.153 | −0.009 | 0.034 | 0.209 |
| SVR | 0.215 | 0.007 | 0.047 | 0.231 |
| Random Forest (E11, same 41 inputs) | **0.272** | **0.041** | **0.055** | **0.291** |

## Results — classes
Accuracy:

| Model | N | P | K | OC |
|---|---|---|---|---|
| Majority baseline | 0.806 | 0.601 | 0.704 | 0.575 |
| KNN | 0.809 | 0.600 | 0.717 | 0.626 |
| RF | **0.822** | **0.624** | **0.722** | **0.643** |
| SVC | 0.705 | 0.481 | 0.581 | 0.583 |

Balanced accuracy (chance = 0.333):

| Model | N | P | K | OC |
|---|---|---|---|---|
| Majority baseline | 0.333 | 0.333 | 0.333 | 0.333 |
| KNN | 0.387 | 0.367 | 0.378 | 0.460 |
| RF | 0.520 | 0.429 | 0.403 | 0.513 |
| **SVC** | **0.623** | **0.493** | **0.515** | **0.524** |

Macro F1:

| Model | N | P | K | OC |
|---|---|---|---|---|
| Majority baseline | 0.298 | 0.250 | 0.275 | 0.243 |
| KNN | 0.394 | 0.336 | 0.368 | 0.453 |
| RF | **0.530** | 0.430 | 0.408 | 0.504 |
| SVC | **0.530** | **0.453** | **0.430** | **0.522** |

Confusion matrices of SVC (best balanced accuracy for every nutrient); rows = true class, columns = predicted (low, medium, high):

| N | low | medium | high | recall |
|---|---|---|---|---|
| low | 10,570 | 2,641 | 710 | 76 % |
| medium | 1,125 | 1,092 | 401 | 42 % |
| high | 85 | 140 | 509 | **69 %** |

| P | low | medium | high | recall |
|---|---|---|---|---|
| low | 1,500 | 703 | 644 | 53 % |
| medium | 2,906 | 4,844 | 2,624 | 47 % |
| high | 903 | 1,179 | 1,970 | 49 % |

| K | low | medium | high | recall |
|---|---|---|---|---|
| low | 214 | 117 | 155 | 44 % |
| medium | 757 | 2,214 | 1,657 | 48 % |
| high | 1,608 | 2,950 | 7,601 | 63 % |

| OC | low | medium | high | recall |
|---|---|---|---|---|
| low | 6,986 | 2,109 | 842 | 70 % |
| medium | 2,013 | 1,347 | 768 | 33 % |
| high | 926 | 538 | 1,744 | 54 % |

## Interpretation
1. **Regression: RF > SVR > KNN for all four nutrients** (hypothesis 1 confirmed). KNN weights all 41 inputs equally,
   so weak inputs dilute it; RF selects useful inputs itself.
2. **Plain accuracy is misleading.** For N, KNN's 0.809 equals the majority baseline (0.806), so it is no better than
   always saying "low". RF's accuracy is only slightly above the baseline for N, P and K (+0.01–0.02), and +0.07 for OC.
3. **Class prediction with class weighting works clearly better than chance.** SVC reaches balanced accuracy
   N 0.623, P 0.493, K 0.515, OC 0.524 (chance 0.333). For N this is almost double chance, which is more than
   hypothesis 2 expected.
4. **SVC finds the rare classes.** It catches 69 % of high-N fields and 54 % of high-OC fields. The price is lower overall
   accuracy, because some low fields are labelled medium or high.
5. **Severe errors (low ↔ high) are uncommon for N:** 85 of 734 high-N fields (12 %) are called low, and 710 of 13,921
   low-N fields (5 %) are called high. For OC, 29 % of high-OC fields are called low.
6. Practical meaning: a class output separates low, medium and high fields better than chance, even though exact
   values (R²) are weak. This supports showing the device output as classes.

## Caveats
- No tuning (C, number of neighbours, class weights); single seed (42).
- The medium class is the hardest for every nutrient (recall 33–48 %).
- Class limits are the official SHC ratings; values exactly at a limit count as medium.
