# E22 — All-India transfer test and per-state calibration

**Date:** 2026-10-08
**Code:** `06_code/E22_national_transfer/` (`build_locations.py`, `nat_*.py` extraction, `nat_transfer.py`, `nat_calib.py`;
`nat_model.py` / `nat_knn.py` were the slower first versions, kept for reference)
**Results:** `04_results/22_national_transfer.csv`, `04_results/22_state_calibration.csv`, `04_results/22_india_locations_log.json`,
`04_results/22_knn_prelim_noNDVI_blk10.csv`
**Machine:** Linux workstation (24 cores, RTX 4070 SUPER); data and features at `~/agrosense_soil/` on that machine
(not in the repo: location table 75 MB, feature tables up to 100 MB each)

## Question (recorded before running)
E16 and E21 showed that, inside Maharashtra's regions, coordinates beat every set of field and causal covariates.
But inside a region both are *interpolation*. Coordinates cannot extrapolate to territory with no nearby samples;
physical covariates (climate, soil, terrain, irrigation, groundwater, vegetation) might.
**Hypothesis:** when whole areas are held out, causal covariates keep more skill than location does.
Follow-up hypothesis (after the first run): the collapse across states is a per-state offset (laboratory calibration),
which a few local samples can remove.

## Data: all-India independent locations
Source: the full SLUSI Soil Health Card file (5,182,371 records, all cycles 2015–2025).
Rules of D02 (repeated GPS), D07 (value limits, OC > 0.02, EC > 0.005) and D08 (30 m clusters: drop > 10, merge 2–10 by
median, remove locations still < 30 m apart), applied nationally. **No date, season or satellite filter**, so undated and
older-cycle records are kept.

| Step | Count |
|---|---|
| Raw | 5,182,371 |
| Plausible values | 4,159,483 |
| After repeated-GPS rule (1.9 M records at shared points set aside) | 2,293,790 |
| In clusters > 10 (dropped; 17,850 clusters, largest 4,624 records) | 538,891 |
| **Independent locations** | **1,334,556** (Maharashtra 146,270; 447 k from undated 2015–21 cycles) |

Only 77 % of the E01–E21 Maharashtra samples survive this national version, because clustering against all records
(every month and cycle) puts more of them into placeholder clusters.

## Covariates (all 1,334,556 locations)
| Group | Source | Resolution | Cols |
|---|---|---|---|
| climate | TerraClimate 2011–2020 means (as D11) | ~4 km | 6 |
| soilgrids | SoilGrids v2 (clay, sand, silt, CEC, SOC, pH, N, bdod, cfvo; 0–5, 5–15 cm) | 250 m | 18 |
| terrain | Copernicus GLO-90: elev, slope, TPI 500 m / 2 km, roughness | 90 m | 5 |
| lgrip | LGRIP30 irrigated / rainfed (class at point, fractions in ~1 km cells) | 30 m | 3 |
| groundwater | CGWB 2019–21 stations (29,115 with coordinates, EC and K), IDW of 8 nearest | stations | 8 |
| ndvi | MODIS MOD13Q1, Jun 2019 – May 2024 season maxima etc. | 250 m | 11 |

`elev` and climate are allowed here **as physical variables**, because the point of the test is whether they transfer.
Sentinel-2 composites, hydrology, surface water, burning and Sentinel-1 were not extracted nationally (no value in E21,
or per-point extraction does not scale to 1.3 M points).

## Setup
- Targets log1p(N, P, K, OC); predictions back-transformed; R² on the original scale over all out-of-fold predictions.
- Model: XGBoost on GPU, 300 trees, depth 8, learning rate 0.1, subsample/colsample 0.8, min_child_weight 20; each fold
  trains on a random 400 k subsample of its training locations.
- **Location baseline = kNN:** inverse-distance mean (log space) of the 25 nearest *training* locations.
  (A first version used XGBoost on lon/lat; it interpolated poorly, N 0.25 at 10 km, so it was replaced.)
- Feature sets: `causal`, `onsite+causal` (pH, EC + causal), `knn_loc`, `knn+onsite`, `knn+onsite+causal`.
- Held-out schemes (`GroupKFold`, shuffle, seed 42):
  - `blk10`: 10 km blocks, 5 folds (interpolation)
  - `blk100`: 100 km blocks, 5 folds
  - `state`: state codes, 10 folds (each fold holds out about 3–4 states)
  - `zone`: 20 data-driven agro-ecological zones, 10 folds. Zones come from k-means on standardised annual and monsoon
    rainfall, mean temperature, water deficit, elevation, SoilGrids clay, sand and pH. Official NBSS&LUP AER/AESR
    boundaries were not obtainable.
- `zone` also runs `knn+onsite+causal` minus each covariate group.

## Results 1 — transfer (R², N / P / K / OC)

| Held out | Median distance to nearest training location | causal | onsite+causal | knn_loc | knn+onsite+causal |
|---|---|---|---|---|---|
| 10 km blocks | 3 km | 0.48 / 0.22 / 0.30 / 0.33 | 0.50 / 0.24 / 0.32 / 0.35 | 0.54 / 0.30 / 0.35 / 0.37 | **0.55 / 0.31 / 0.36 / 0.39** |
| 100 km blocks | 19 km | 0.32 / 0.11 / 0.20 / 0.22 | 0.34 / 0.12 / 0.22 / 0.23 | 0.34 / 0.11 / 0.19 / 0.20 | **0.37 / 0.13 / 0.22 / 0.24** |
| States | 46 km | −0.25 / −0.17 / −0.05 / 0.00 | −0.19 / −0.17 / −0.01 / 0.01 | −0.29 / −0.24 / −0.17 / −0.23 | −0.22 / −0.22 / −0.10 / −0.12 |
| Zones | 8 km | 0.22 / 0.09 / 0.14 / 0.19 | 0.25 / 0.11 / 0.19 / 0.20 | 0.39 / 0.21 / 0.27 / 0.25 | **0.41 / 0.21 / 0.26 / 0.26** |

Mean R² *within* held-out states: −0.2 to −1.7 for every set. Within held-out zones: causal 0.01–0.04, knn 0.11–0.20.

Zone ablation (`knn+onsite+causal`, N within-zone R² 0.224): without ndvi 0.171; without any other single group 0.215–0.229.

## Results 2 — per-state calibration
Leave-states-out predictions (10 folds as above) for the 22 states with ≥ 2,000 locations. In each held-out state, *m*
random locations are treated as local lab samples (3 random draws; scored only on the other locations of that state):
- `offset`: shift predictions by the mean log error on the *m* samples
- `linear`: intercept + slope in log space, *m* ≥ 50
- `local_only`: kNN using only the *m* local samples
- `oracle`: offset estimated from all of the state's samples

| Method | m | Pooled R² | Mean R² within state | Mean within-state Spearman |
|---|---|---|---|---|
| causal, none | 0 | −0.24 / −0.18 / −0.03 / 0.00 | −0.85 / −0.40 / −0.23 / −0.55 | −0.01 / 0.03 / 0.08 / 0.08 |
| causal, offset | 10 | 0.11 / −0.02 / 0.08 / 0.03 | −0.38 / −0.18 / −0.16 / −0.16 | (unchanged by an offset) |
| causal, offset | oracle | 0.17 / 0.03 / 0.13 / 0.10 | −0.26 / −0.13 / −0.10 / −0.09 | |
| causal, linear | 50 | 0.31 / 0.06 / 0.13 / 0.12 | −0.05 / −0.07 / −0.07 / −0.02 | 0.08 / 0.04 / 0.06 / 0.07 |
| causal, linear | 500 | 0.32 / 0.08 / 0.15 / 0.16 | −0.03 / −0.04 / −0.04 / 0.01 | 0.11 / 0.09 / 0.10 / 0.10 |
| onsite+causal, linear | 500 | 0.33 / 0.08 / 0.15 / 0.16 | −0.02 / −0.05 / −0.04 / 0.01 | 0.13 / 0.08 / 0.10 / 0.09 |
| local_only | 50 | **0.39 / 0.12 / 0.20 / 0.20** | 0.10 / 0.01 / 0.01 / 0.08 | **0.33 / 0.28 / 0.28 / 0.30** |
| local_only | 500 | **0.50 / 0.25 / 0.30 / 0.31** | 0.27 / 0.15 / 0.16 / 0.22 | **0.50 / 0.46 / 0.46 / 0.45** |

## Interpretation
1. **The hypothesis is not supported.** Causal covariates never beat location by a clear margin. At 10 km they are below
   kNN, as in Maharashtra. At 100 km blocks (~19 km to the nearest training location) they roughly equal it, and combining
   both gives the best score (N 0.37 vs 0.34). Within held-out zones they explain almost nothing (within-zone R² ≤ 0.04).
2. **Across states every method fails, and the failure is mostly a per-state level shift.** About 10 local samples turn
   pooled R² from negative to positive; 50 samples with a linear correction bring N to 0.31. The covariates (climate,
   soil, terrain) do not predict these shifts, which points to differences in laboratory method or calibration rather than
   soil. This cannot be proven from SHC data alone, but in practice **state boundaries behave as laboratory boundaries**.
3. **After calibration, a model from other states still cannot rank fields inside a new state** (within-state R² ≈ 0,
   Spearman 0.08–0.13). The covariate–nutrient relationships learned in one set of states do not carry over to another.
4. **Local lab samples are worth more than any transferred model.** 50 local samples alone give pooled N 0.39 and a
   within-state Spearman of about 0.3; 500 give 0.50 and 0.5. For a new area, collect local SHC-type samples first
   ("history sets the mean"); covariates are at most a small add-on (E21: +0.03–0.04 for K and OC).
5. Of the covariate groups, only multi-year NDVI carries information that the others do not (zone ablation, N).

## Caveats
- Single seed; 400 k training subsample per fold; untuned XGBoost and an untuned kNN (k = 25, IDW).
- Data-driven zones are scattered patches (held-out zone points are 8 km from training data), so `zone` is
  environmental, not geographic, extrapolation.
- 447 k locations come from undated 2015–21 cycles, while NDVI (2019–24), LGRIP30 (~2015) and groundwater (2019–21)
  describe other years.
- Groundwater covariates are unreliable where the nearest station is far (up to 550 km in the islands and the north-east).
- LGRIP30 classes 85 % (median) of the 1 km neighbourhood of SHC locations as irrigated; not validated.
- The calibration test treats random locations in the held-out state as "local lab samples"; real calibration samples
  would come from the same labs, which is the case here because each state's SHC data come from its own labs.

## Decision / next step
- Report the national result as a negative result for transfer: physical covariates do not substitute for local data.
- Any deployment in a new area needs local laboratory samples (on the order of 50–500 per state) to set the level and
  the local pattern; a lab-effect term (state, or lab where known) is required when pooling states.
- Possible follow-up: local samples + model combined (kNN on local samples plus covariates and pH/EC), to see whether the
  model adds anything once some local history exists.
