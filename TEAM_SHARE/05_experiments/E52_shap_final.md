# E52 — Final setup: what the model uses (SHAP by input group)

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E51)
**Results:** `results/52_shap_final.csv` (nutrient × test × input: mean |SHAP|, share %)
**Replaces E46 for the paper** (E46 included Raigad).

## Setup
As E46 (LightGBM exact tree SHAP via `pred_contrib=True`, on test data only), on the final data: 32,096 samples
(Raigad excluded), 39 inputs + 4 neighbourhood features, statewide. Run time 0.5 min.

## Results — share of total |SHAP| by input group (%)

| Group (inputs) | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| **Neighbourhood (4)** | **63.8** | **62.9** | **62.7** | **63.6** | **61.0** | **62.6** | **59.9** | **62.6** |
| Climate (6) | 14.7 | 11.5 | 10.2 | 13.5 | 15.5 | 11.0 | 11.0 | 13.0 |
| Coordinates (2) | 6.0 | 9.2 | 10.2 | 7.7 | 5.8 | 9.5 | 10.1 | 7.8 |
| Spectral indices (16) | 6.0 | 6.2 | 5.6 | 6.0 | 7.2 | 6.8 | 6.6 | 6.8 |
| Satellite bands (12) | 5.1 | 4.7 | 5.2 | 5.8 | 5.6 | 5.1 | 5.8 | 6.1 |
| pH, EC (2) | 2.3 | 3.9 | 4.6 | 2.6 | 3.0 | 3.7 | 4.6 | 2.6 |
| Elevation (1) | 2.1 | 1.6 | 1.5 | 0.8 | 1.9 | 1.3 | 1.9 | 1.1 |

Sentinel-2 total (bands + indices, 28 inputs): random N 11.1 %, P 10.9 %, K 10.8 %, OC 11.8 %;
spatial 12.8 %, 11.9 %, 12.4 %, 12.9 %.

Top 8 single inputs, random 70/30 (share %):
- **N:** nb_idw_mean 50.6, nb_nearest_value 9.9, ppt_monsoon 4.7, longitude 3.8, ppt_annual 2.4, nb_sd 2.3, latitude 2.2, tmin_mean 2.1
- **P:** nb_idw_mean 50.1, nb_nearest_value 9.9, longitude 5.1, latitude 4.1, tmin_mean 3.0, pH 2.5, tmax_mean 2.0, nb_sd 2.0
- **K:** nb_idw_mean 49.0, nb_nearest_value 10.5, longitude 7.5, EC 3.5, latitude 2.6, ppt_monsoon 2.4, nb_sd 2.3, ppt_annual 2.2
- **OC:** nb_idw_mean 48.4, nb_nearest_value 8.3, nb_sd 6.1, longitude 3.9, latitude 3.8, tmin_mean 2.9, ppt_annual 2.8, ppt_monsoon 2.7

## Interpretation
1. Same picture as E46: neighbourhood context about 60–64 %, climate 10–16 %, coordinates 6–10 %, Sentinel-2
   11–13 %, pH/EC 2–5 %, elevation 1–2 %. Removing Raigad does not change the ranking.
2. Sentinel-2's share is slightly higher under spatial testing (about 12–13 % vs 11–12 %): with fewer close
   neighbours the model relies a little more on the field's own reflectance.
3. Paper wording: "predictions are dominated by neighbourhood context and climate; Sentinel-2 reflectance and
   indices contribute about 11–13 % and soil chemistry 2–5 % of the attributions."

## Caveats
SHAP shares describe the model, not causation; correlated inputs share credit. One seed, one split.
