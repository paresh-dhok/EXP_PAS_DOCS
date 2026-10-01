# D07 — Soil-value cleaning, reflectance and spectral indices

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cells 19–21 (analysis in 19–20, build in 21)
**Output:** `mh_model_dataset.parquet` (33,877 rows × 44 columns)

## Objective
Remove physically impossible soil values (after analysing them first, not by blind thresholds), convert the satellite
values to reflectance, and compute spectral indices.

## Starting set
Strictly bare (SCL min = max = 5, all 9 pixels) and complete window (`n_B04 = n_B11 = n_SCL = 9`): **36,005 samples**.

## Step 1 — Analysis of soil values (cells 19–20)
Basic problems:

| | N | P | K | OC | pH | EC |
|---|---|---|---|---|---|---|
| missing / non-numeric | 0 | 0 | 0 | 0 | 0 | 0 |
| negative | 7 | 1 | 0 | 2 | 6 | 6 |
| zero | 110 | 29 | 26 | 46 | 41 | 49 |

Distribution (before cleaning):

| | min | 1 % | 50 % | 99 % | 99.9 % | max |
|---|---|---|---|---|---|---|
| N | −178.1 | 1.0 | 192.0 | 984.9 | 2,767.3 | 213,225 |
| P | −3.1 | 1.0 | 15.7 | 159.3 | 532.1 | 11,797 |
| K | 0.0 | 5.9 | 366.4 | 1,444.8 | 2,425.5 | 552,016 |
| OC | −1.61 | 0.081 | 0.46 | 2.56 | 15.43 | 1,362 |
| pH | −26.9 | 4.82 | 7.64 | 8.70 | 9.15 | 6,982 |
| EC | −1.83 | 0.02 | 0.31 | 1.02 | 9.35 | 2,388 |

Findings:
- **Decimal / unit errors:** pH 77.63 and 80.7 (= 7.763, 8.07), pH 559–6,982, OC 37–58 and 763–1,362, EC 459–2,388,
  N and K in the tens of thousands. These were **removed, not repaired**, because repairing would require guessing.
- **Placeholder value "1":** N = 1 (314×), P = 1 (309×) and K = 1 (207×) are among the most frequent values.
- Other frequent values (N 245, 217, 188.16, 163.07 …) are genuine: the lab method gives discrete steps.
- pH between 0 and 3.5 occurs in 215 samples. That is not soil pH (probably another value in the column).
- Range counts (cell 20), for example N: (0,10] 542, (10,20] 54, (20,50] 343, (50,100] 2,416. Values thin out sharply below 20.
- SHC rating classes (for reference): N low < 280: 29,212; K high > 280: 25,543; pH alkaline > 7.5: 21,784.

## Step 2 — Limits applied (agreed with the user)
A sample is removed if **any** of its six values is outside these limits:

| Parameter | Keep if | Removed (a sample may fail several) |
|---|---|---|
| N (kg/ha) | 20 < N ≤ 1500 | 925 |
| P (kg/ha) | 1 < P ≤ 300 (excludes the placeholder 1) | 702 |
| K (kg/ha) | 20 < K ≤ 3000 | 478 |
| OC (%) | 0 < OC ≤ 5 | 204 |
| pH | 3.5 ≤ pH ≤ 10.5 | 283 |
| EC (dS/m) | 0 < EC ≤ 10 | 91 |

After removal: **34,578**. In D08 the lower limits were later tightened to OC > 0.02 and EC > 0.005 (35 more samples).

Genuinely high but possible values (e.g. N = 900) were **kept**. No statistical outlier trimming was applied.

## Step 3 — Reflectance
- Bands B01–B12: **reflectance = (DN − 1000) / 10000** (L2A processing baseline ≥ 04.00, which adds a +1000 offset; all imagery is from 2024).
- AOT = DN / 1000 (unitless); WVP = DN / 1000 (cm).
- Samples with reflectance ≤ 0 or > 1 in **any** band were removed: **701 removed → 33,877**.

## Step 4 — Spectral indices (16)
NDVI, SAVI, NBR2, NDMI, NDWI, BSI, NDRE, CI (colour), BI (brightness), RI (redness), R_B4B2 (iron oxide),
R_B11B12 (clay), R_B12B8 (ferrous), R_B11B8 (SWIR/NIR), R_B7B5 and R_B6B5 (red-edge ratios).
Non-finite values: 0.

## Checks reported but not used as filters
| Check | Count | Decision |
|---|---|---|
| NDVI > 0.3 | 8,853 (26 %) | Not filtered. Median NDVI ≈ 0.27 for dark Vertisols; to be tested as an experiment |
| NBR2 > 0.075 | 29,142 (86 %) | Not used. The threshold comes from European light soils and does not transfer to dry, dark Indian soils |
| Another sample within 30 m | 20,170 | Investigated in D08 |

## Final targets in `mh_model_dataset.parquet`
| | mean | min | 1 % | 50 % | 99 % | max |
|---|---|---|---|---|---|---|
| N | 231.3 | 22.09 | 50.17 | 194.95 | 922.44 | 1,474.66 |
| P | 22.66 | 1.012 | 2.63 | 15.81 | 131.71 | 298.54 |
| K | 433.4 | 20.38 | 69.22 | 369.15 | 1,405.59 | 2,969.12 |
| OC | 0.570 | 0.006 | 0.09 | 0.46 | 2.278 | 4.928 |
| pH | 7.48 | 3.70 | 5.30 | 7.65 | 8.65 | 10.00 |
| EC | 0.360 | 0.001 | 0.02 | 0.31 | 1.00 | 9.35 |

Columns kept (user decision: no village/district fields): id, sample_date, longitude, latitude, N, P, K, OC, pH, EC,
sentinel_scene_id, sentinel_datetime, date_difference_days, 12 bands, AOT, WVP, 16 indices, n_within_30m.
