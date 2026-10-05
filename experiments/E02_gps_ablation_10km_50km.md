# E02 — What does GPS contribute? (10 km vs 50 km blocks)

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cell 25
**Results:** `results/02_rf_gps_ablation.csv`
**Data:** 17,620 locations

## Question (before running)
In E01, adding longitude/latitude raised R² sharply. Does the satellite add anything once GPS is included?
Does the GPS effect survive stricter spatial validation, or is it local interpolation?

## Setup
Same RF as E01 (300 trees, min_samples_leaf 3, max_features 0.33, log target, seed 42).
- 10 km blocks: 1,567 blocks. **50 km blocks: 150 blocks, median 84 locations per block.**

| Set | Features |
|---|---|
| F_GPS_only | longitude, latitude |
| E_sensor_GPS | pH, EC, longitude, latitude |
| D_fusion_plus_GPS | 12 bands + 16 indices + pH, EC + longitude, latitude |

## Results (R², pooled out-of-fold)
| Blocks | Set | N | P | K | OC |
|---|---|---|---|---|---|
| 10 km | **F_GPS_only** | **0.650** | **0.365** | **0.304** | **0.584** |
| 10 km | E_sensor_GPS | 0.594 | 0.316 | 0.300 | 0.558 |
| 10 km | D_fusion_plus_GPS | 0.576 | 0.301 | 0.247 | 0.519 |
| 50 km | **F_GPS_only** | **0.522** | **0.285** | 0.211 | **0.506** |
| 50 km | E_sensor_GPS | 0.474 | 0.250 | **0.221** | 0.476 |
| 50 km | D_fusion_plus_GPS | 0.470 | 0.233 | 0.187 | 0.455 |

Fold std is larger at 50 km (e.g. N GPS-only: 0.451 ± 0.185).

## Interpretation
- **GPS alone was the best model.** Adding pH/EC and the satellite made it *worse*.
- What a GPS-only model learns is a map: it predicts a test field from the lab values of nearby training fields
  (spatial interpolation). It measures nothing about the field itself.
- The drop from 10 km to 50 km blocks (N 0.65 → 0.52) shows part of this is short-range interpolation, but strong
  regional patterns remain.
- Two explanations were open: (1) a Random Forest artefact (feature dilution with max_features 0.33), or
  (2) the predictable signal is mainly regional (district or lab level). Tested in E03.

## Status
Uses location. Diagnostic only. Under the rule adopted on 2026-10-01, GPS is not a valid model input:
it would tell a farmer "your field is like the fields tested 5–10 km away".
