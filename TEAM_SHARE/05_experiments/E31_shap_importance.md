# E31 — Which inputs the model uses (SHAP values on held-out blocks), region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 3 of the three-part cell)
**Results:** `results/31_shap_importance.csv` (per region × input set × nutrient × input: mean |SHAP| and share in %)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Hypothesis (recorded before running)
pH and EC are the top single inputs with the 41 inputs. With elevation + climate added, climate takes the largest share.

## Setup
- Model: XGBoost (400 trees, learning rate 0.03, max_depth 4, min_child_weight 10, subsample 0.8, colsample 0.5, L2 5),
  target log1p standardised, fitted on the training folds.
- SHAP values: exact tree SHAP from XGBoost (`pred_contribs=True`), computed **on the test blocks** of each outer fold,
  so they describe how the model forms predictions for unseen areas.
- Importance of an input = mean |SHAP| over all held-out locations; share = its percentage of the total over all inputs.
  Shares are averaged over the 5 regions.
- Input groups: pH, EC (2); satellite bands (12); satellite indices (16); change between dates (5 `c_std_*`);
  terrain without elevation (6); elevation (1); climate (6).

## Results — share of total SHAP by input group (%), mean over 5 regions

41 inputs:

| Group (number of inputs) | N | P | K | OC |
|---|---|---|---|---|
| pH, EC (2) | **25.4** | **25.1** | 20.9 | **24.3** |
| Satellite: indices (16) | 23.1 | 20.9 | 25.2 | 20.8 |
| Satellite: bands (12) | 22.5 | 23.3 | **26.8** | 20.7 |
| Terrain, no elevation (6) | 15.7 | 15.5 | 13.7 | 17.5 |
| Satellite: change between dates (5) | 13.2 | 15.1 | 13.4 | 16.7 |

Top single inputs (share %): N — EC 13.1, pH 12.3, relpos_2km 6.3, c_B01 4.6; P — pH 15.7, EC 9.5, relpos_2km 5.3,
c_B01 3.9; K — EC 12.5, pH 8.4, c_B11 4.1, c_B09 4.1; OC — EC 12.2, pH 12.1, relpos_2km 4.5, tpi_1km 4.1.

41 + elev + climate:

| Group (number of inputs) | N | P | K | OC |
|---|---|---|---|---|
| Climate (6) | **54.7** | **52.0** | **46.1** | **46.8** |
| pH, EC (2) | 9.2 | 10.2 | 10.5 | 10.6 |
| Satellite: indices (16) | 8.9 | 9.6 | 11.7 | 10.7 |
| Satellite: bands (12) | 8.1 | 9.1 | 11.6 | 10.4 |
| Elevation (1) | 8.0 | 7.4 | 6.3 | 7.7 |
| Terrain, no elevation (6) | 6.0 | 6.0 | 7.5 | 7.3 |
| Satellite: change between dates (5) | 5.1 | 5.7 | 6.2 | 6.4 |

Top single inputs: the first four to six places are climate variables and elevation for every nutrient
(e.g. N — tmax_mean 11.6, def_annual 11.5, ppt_monsoon 10.8, tmin_mean 9.0, elev 8.0).

## Interpretation
1. **Hypothesis confirmed.** With the 41 inputs, pH and EC are the two most used inputs for every nutrient:
   2 of 41 inputs carry 21–25 % of the total. Each satellite input carries on average about 1.5–2 %.
2. **The 33 satellite inputs together carry 57–65 %**, spread thinly over many correlated inputs; no single band or index
   stands out (largest: c_B01 3–5 %). The model has no dominant spectral feature for any nutrient.
3. **With elevation + climate, these 7 inputs take 53–63 % of the total**, and the share of the satellite inputs falls
   from about 60 % to about 22–30 %. Seven smooth, slowly varying inputs displace 33 field-level satellite inputs.
   Together with E16 (climate behaves like location) this shows the model predicts mainly from where the field is.
4. The most used terrain input is `relpos_2km` (relative position within 2 km), a landscape-position variable.

## Caveats
- SHAP shows what the model uses, not what causes the nutrient level. With R² of 0.04–0.15 (41 inputs) the model uses
  these inputs for a weak prediction.
- Correlated inputs share importance among themselves, so group totals are more reliable than single-input shares.
- One model type (XGBoost), fixed settings, single seed. pH and EC are laboratory values.
