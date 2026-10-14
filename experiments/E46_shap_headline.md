# E46 — What the headline model uses (SHAP by input group)

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E45, reuses its data and functions)
**Results:** `results/46_shap_headline.csv` (nutrient × test × input: mean |SHAP|, share %)

## Why
The draft abstract said "climate and soil chemistry (pH, EC) are the most important inputs", based on E31, which used
older region-wise models without coordinates or neighbourhood features. E45 showed that pH and EC hardly matter in the
headline model. This measures the importance of each input group in the headline model itself.

The cell was **not** test-run before it was given (user's request).

## Setup
- Headline model: statewide LightGBM (E36 settings), clustered `mh_model_dataset` (33,877), 39 inputs + 4
  neighbourhood features.
- SHAP: LightGBM's exact tree SHAP (`predict(..., pred_contrib=True)`, in standardised log units), computed on
  **test data only** (random 70/30 test set; held-out folds of the 10 km spatial CV). Importance = mean |SHAP|;
  share = percentage of the total over all 43 inputs. Run time 0.6 min.

## Results — share of total |SHAP| by input group (%)

| Group (inputs) | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| **Neighbourhood (4)** | **66.0** | **62.9** | **61.5** | **63.0** | **62.9** | **62.0** | **60.4** | **62.1** |
| Climate (6) | 13.5 | 12.3 | 10.7 | 15.3 | 14.7 | 12.3 | 10.5 | 14.3 |
| Coordinates (2) | 7.3 | 9.1 | 9.9 | 8.0 | 6.9 | 8.4 | 10.0 | 8.0 |
| Spectral indices (16) | 4.6 | 5.9 | 6.1 | 5.0 | 5.7 | 6.8 | 6.9 | 6.1 |
| Satellite bands (12) | 4.5 | 4.7 | 5.5 | 5.4 | 5.1 | 5.6 | 5.8 | 5.7 |
| pH, EC (2) | 2.3 | 3.6 | 4.7 | 2.2 | 2.7 | 3.6 | 4.7 | 2.7 |
| Elevation (1) | 1.8 | 1.4 | 1.6 | 1.1 | 2.0 | 1.4 | 1.8 | 1.2 |

Sentinel-2 total (bands + indices, 28 inputs), random: N 9.1 %, P 10.6 %, K 11.6 %, OC 10.4 %.

Top 8 single inputs, random 70/30 (share %):
- **N:** nb_idw_mean 52.5, nb_nearest_value 10.4, longitude 5.3, ppt_monsoon 4.4, ppt_annual 3.2, nb_sd 2.1, latitude 2.0, tmin_mean 1.9
- **P:** nb_idw_mean 49.9, nb_nearest_value 10.4, latitude 4.6, longitude 4.5, tmin_mean 3.8, tmean 2.8, pH 2.2, ppt_monsoon 2.1
- **K:** nb_idw_mean 48.3, nb_nearest_value 10.5, longitude 6.7, EC 3.6, latitude 3.2, ppt_monsoon 2.5, tmax_mean 2.1, nb_sd 2.1
- **OC:** nb_idw_mean 47.9, nb_nearest_value 10.2, ppt_annual 5.3, longitude 4.6, nb_sd 4.2, latitude 3.4, def_annual 2.8, tmin_mean 2.7

## Interpretation
1. **Neighbourhood context carries about 60–66 % of the model's attributions**; the inverse-distance-weighted mean of
   the 10 nearest samples alone carries 48–53 %. Then climate (11–15 %) and coordinates (7–10 %).
2. **Sentinel-2 (28 inputs together) carries about 9–12 %**, pH and EC 2–5 %, elevation 1–2 %. Consistent with E45
   (removing pH/EC costs ≤ 0.012) and E37 (satellite alone R² ≤ 0.04).
3. The ranking is the same under random and spatial testing.
4. Consequence for the paper: the abstract must not say that pH/EC (or Sentinel-2) are the most important inputs.
   Correct statement: "predictions are dominated by neighbourhood context and climate; Sentinel-2 reflectance and
   soil chemistry contribute about 10 % and 2–5 % of the attributions."

## Caveats
- SHAP shares describe what this model uses, not causal importance; correlated inputs (coordinates, climate,
  neighbour values) share credit between them.
- One seed, one split.
