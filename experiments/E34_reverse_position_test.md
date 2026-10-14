# E34 — Reverse test: can the inputs predict where a field is?

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 3 of the four-part cell)
**Results:** `results/34_reverse_position.csv`
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Why
Ploton et al. (2020) showed that their remote-sensing and environmental predictors could predict a pixel's position to
within about 25 km, so a model using them could reproduce local values without any real link to the target. This is
the same test for our input groups.

## Hypothesis
Elevation + climate predict a field's position far better than chance; the 41 inputs only partly.
**Not a blind hypothesis:** the result was seen in a preview run.

## Setup
- Targets: easting and northing of the field (km), predicted separately with LightGBM (fixed settings as in E33).
- 10 km block cross-validation inside each region: the model never sees fields of the test blocks.
- Error = distance between predicted and true position; the median over all fields of a region is reported.
- Null = always predict the mean position of the training fields.

## Results — median position error (km)

| Inputs | Vidarbha | Marathwada | North MH | Western MH | Konkan | Mean | Share of null error |
|---|---|---|---|---|---|---|---|
| Null | 133.8 | 90.9 | 89.6 | 85.5 | 83.3 | 96.6 | 1.00 |
| Terrain without elevation (6) | 125.0 | 94.9 | 77.6 | 68.8 | 87.7 | 90.8 | 0.94 |
| pH, EC (2) | 87.9 | 74.0 | 61.2 | 66.1 | 63.5 | 70.6 | 0.74 |
| Satellite (33) | 69.9 | 72.0 | 71.8 | 63.1 | 62.9 | 67.9 | 0.72 |
| 41 inputs | 63.2 | 61.7 | 54.3 | 51.8 | 44.2 | 55.0 | 0.58 |
| **Elevation + climate (7)** | **16.0** | **15.7** | **20.4** | **16.9** | **17.6** | **17.3** | **0.19** |
| 41 + elev + climate | 17.3 | 16.3 | 21.4 | 18.4 | 16.7 | 18.0 | 0.19 |

## Interpretation
1. **Hypothesis confirmed.** Seven variables (elevation and six climate averages) place a field to within about 17 km
   in regions that are 150–500 km across, five times better than the null. Ploton et al. report about 25 km for their
   predictors. A model given these inputs effectively knows where the field is, which confirms E16 with a direct test.
2. **The 41 field-level inputs also carry some position information:** median error 55 km, 58 % of the null. pH/EC
   alone and the satellite features alone each reach about 70 km. These inputs vary across a region in a structured
   way (soil type, landscape), so part of their predictive value is regional position (consistent with E33, where the
   R² of the 41 inputs falls to zero at 20 km).
3. **Local terrain shape carries almost no position information** (0.94 of null), as intended when elevation was
   removed from the terrain set.
4. Adding the 41 inputs to elevation + climate does not improve the position estimate (18.0 vs 17.3 km).

## Caveats
- Position is predicted with the same spatial cross-validation as the nutrients; with a random split the errors would
  be smaller.
- TerraClimate has a grid of about 4 km and is smooth, so it behaves almost like a function of position by construction.
- One model type, fixed settings, one seed.
