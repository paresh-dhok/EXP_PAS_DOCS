# C01 — Editorial clarification: existing approach and results (E49–E56)

Date: 2026-10-15. For the handling editor. Existing evidence only: no new experiments, no data or result changes.
Main evidence: `Start/new.ipynb` cells 66–85 (one kernel session, execution counts 3–22), `Start/results/49–56_*.csv`,
experiment notes `Start/experiments/D03–D08, E47–E56`, audit `Start/audit/A01_*`, sprint `Start/final/S01_*`.

> **Important context.** This report answers for the E49–E56 approach (32,096 samples), as requested. On 15 October an
> audit (A01) and a correction sprint (S01) were already completed; S01 produced a corrected dataset (24,599 samples)
> and re-ran the essential results. Which version the manuscript uses is the first decision in section B.

---

## A. Confirmed and ready to write

### A1. Dataset and preprocessing (E49–E56 version)

| Stage | Records | Source (file / note) |
|---|---|---|
| All-India SLUSI Soil Health Card records | 5,182,371 | `TEAM_SHARE/01_source_data/SLUSI_SHC_all_india.parquet` |
| Maharashtra (state code 27) | 355,562 | `maharashtra_raw.parquet` (DATASETS.md) |
| Eligible: only record at its GPS point, parseable date, inside Maharashtra bounding box, numeric N/P/K | 119,814 | D03 (notebook cell 7) |
| Candidates sampled January–June | 91,818 | `mh_candidates.parquet` (D05) |
| Sample–scene pairs: Sentinel-2 L2A scene within ±3 days, point inside scene footprint | 151,831 pairs | `mh_pairs.parquet` (D05) |
| 3×3 windows extracted | 61,617 pairs (61,332 OK) | `mh_s2_3x3.parquet` (D06) |
| All 9 pixels bare soil (SCL = 5), complete window | 36,005 samples | D07 (cells 19–21) |
| Impossible soil values removed (limits below) | 34,578 | D07 |
| Reflectance outside 0–1 removed | 33,877 | `mh_model_dataset.parquet` (D07) |
| Raigad district (code 491) removed | **32,096** | cell 77 output; `results/49_headline_metrics.csv` (n) |

- **Date range** of the 32,096 samples: 1 Jan 2024 – 31 May 2024 (Jan 2,155; Feb 3,367; Mar 5,945; Apr 7,734;
  May 12,895). Scene–sample difference −3 to +3 days. (Checked from `mh_model_dataset.parquet`.)
- **Regions:** Vidarbha 7,236; Marathwada 9,293; North MH 9,738; Western MH 4,329; Konkan 1,500
  (`results/50_block_size_final.csv`, n column).
- **Laboratory value limits (keep if):** 20 < N ≤ 1500 kg/ha; 1 < P ≤ 300; 20 < K ≤ 3000; 0 < OC ≤ 5 %;
  3.5 ≤ pH ≤ 10.5; 0 < EC ≤ 10 dS/m (D07). Reflectance = (DN − 1000)/10000.
- **District exclusion:** only Raigad (491).

### A2. Experimental design (cells 66, 69, 70, 71, 77, 78, 85)
- **Random 70/30:** `train_test_split(test_size=0.30, random_state=seed)` on samples (not grouped). Score = R² on the
  30 % test set.
- **Spatial blocks:** square grid cells of 10, 25, 50 or 100 km on approximate local metres
  (x = lon·111,320·cos lat, y = lat·110,574; `blocks()` cell 66, `blocks_km()` cell 69); blocks assigned to
  **5 folds** with `GroupKFold(n_splits=5, shuffle=True, random_state=seed)`. Score = R² over all pooled out-of-fold
  predictions (every sample predicted once). No buffer between folds.
- **Statewide vs regional:** statewide = one model on all 32,096 samples; regional = a separate model trained and tested
  inside each of the 5 regions (cell 78); "mean of 5 regions" = arithmetic mean of the five regional R² values.
- **Seeds:** only E56 (cell 85) uses 5 seeds (42, 7, 13, 99, 2024); each seed changes the random split, the fold
  assignment of blocks and the model seed. **E49–E55 use seed 42 only.**
- **Scale:** the model is trained on log(1 + y) standardised with training-set mean/SD; predictions are
  back-transformed with expm1 **before** R², RMSE and MAE are computed (cells 66, 77) → **all metrics on the original
  scale** (kg/ha; % for OC).

### A3. Headline metrics — which number is which
| Value in the 4-page summary | Type | Authoritative file |
|---|---|---|
| Table "Headline": 0.71 ± 0.01 / 0.62 / 0.57 / 0.70 (random), 0.39 ± 0.03 / 0.39 / 0.34 / 0.56 (10 km); RMSE 54.0 / 15.2 / 163.5 / 0.21 and 76.8 / 19.3 / 201.8 / 0.26 | **Mean ± SD of 5 seeds** | `results/56_headline_seeds.csv` |
| Figure 1 (measured vs predicted): 0.71 / 0.61 / 0.56 / 0.70 random; 0.39 / 0.40 / 0.35 / 0.58 spatial; RMSE 55 … | **Single run, seed 42** | `results/49_headline_metrics.csv`, `49_measured_vs_predicted.png` |
| Distance table and Figure 2 (10–100 km) | **Single run, seed 42** | `results/50_block_size_final.csv`, `55_r2_vs_block_size.png` |
| Five-model table | Single run, seed 42 | `results/51_model_comparison_final.csv` |
The small table–figure differences (e.g. P 0.62 vs 0.61; spatial N RMSE 76.8 vs 76.7) are mean-of-5-seeds vs seed 42.
MAE, bias and RPIQ exist only for seed 42 (`49_headline_metrics.csv`).

### A4. Features (cells 66, 70)
- Sentinel-2 (28): 12 bands (B01–B12, B8A) and 16 indices (NDVI, SAVI, NBR2, NDMI, NDWI, BSI, NDRE, CI, BI, RI,
  B4/B2, B11/B12, B12/B8, B11/B8, B7/B5, B6/B5); single-date, median of the 3×3 window.
- pH, EC: SHC laboratory values. Elevation (Copernicus DEM GLO-30) and 6 climate variables (TerraClimate) — **copied
  from the nearest de-clustered location** (see C1). Longitude, latitude.
- LRS (4): from the 10 nearest training samples (KD-tree on approximate metres): inverse-distance-weighted mean of
  log(1 + y) (distance floor 1 m), log value of the nearest, log distance to the nearest, SD of the 10 log values.
- **Test labels cannot enter:** test-row LRS uses `cKDTree(P[tr])` and `y[tr]` only (cell 70 `fit_predict_nb`, cell 77
  `fit_nb_both`). **Own target:** training rows query 11 neighbours and drop the first (the row itself); audit A01
  verified 0 failures in the seed-42 training set and identical R² with explicit index-based exclusion
  (`audit/A01_output.txt`, section 2c–2d).

### A5. Algorithms (cells 72, 79)
Same inputs (39 + LRS), same splits, target log(1 + y) standardised, predictions clipped to the training range:
Ridge (α = 1, standardised inputs), KNN (k = 15, distance-weighted, standardised), MLP (64-32, α = 1e-3, early
stopping, standardised), Random Forest (100 trees, min_samples_leaf 5, max_features 0.33), LightGBM (400 trees,
learning rate 0.05, 15 leaves, min_child_samples 20, subsample 0.8, colsample 0.5, L2 = 5). Seed 42, untuned.
**Computing-time claim:** `results/51_model_comparison_final.csv` column `sec` (CPU seconds summed over all jobs):
Random Forest 823 s, LightGBM 47 s → ratio 17.5. Verified, but must be qualified: one run, one machine, RF with
100 trees vs LightGBM with 400, measured inside parallel jobs.

### A6. SHAP and ablation (E52 `52_shap_final.csv`; E53 `53_input_ablation.csv`; seed 42)
- SHAP share (random test data): LRS 63–64 %, climate 10–15 %, coordinates 6–10 %, Sentinel-2 bands + indices
  11–12 %, pH/EC 2–5 %, elevation 1–2 %; same ranking on spatial test data.
- Ablation R² random / spatial 10 km — full: N 0.706 / 0.393, P 0.614 / 0.396, K 0.564 / 0.352, OC 0.701 / 0.578;
  **without Sentinel-2:** 0.710 / 0.390, 0.616 / 0.381, 0.568 / 0.357, 0.703 / 0.578 (change −0.015 to +0.004);
  without LRS: 0.613 / 0.326, 0.529 / 0.359, 0.498 / 0.312, 0.680 / 0.557; LRS only: 0.694 / 0.333, 0.590 / 0.367,
  0.548 / 0.288, 0.686 / 0.533; **Sentinel-2 + pH + EC only (no location):** 0.168 / 0.036, 0.121 / 0.033,
  0.161 / 0.049, 0.324 / 0.201.
- **Distinction:** stand-alone value of satellite (+ pH/EC) inputs is low (R² ≤ 0.32, mainly OC); **incremental**
  value of Sentinel-2 in the full model is ≈ 0. The SHAP share of 11–12 % is attribution, not added accuracy.

### A7. Regional results (E50 `50_block_size_final.csv`; seed 42; one model per region; spatial R² pooled over 5 folds)
R² at 50 km — N: Marathwada 0.462, Western MH 0.303, North MH 0.158, Vidarbha 0.125, Konkan 0.060.
P: Marathwada 0.526, Western MH 0.388, North MH 0.314, Konkan 0.147, Vidarbha 0.032.
Values are single-run (seed 42), not averages across runs; each is computed on pooled out-of-fold predictions.

### A8. Raigad and data source
- **Established (E47, E48):** 904 of the 983 samples with N > 850 kg/ha are from Raigad; 50.8 % of Raigad samples
  exceed 850; Raigad median N 872 kg/ha vs neighbouring Ratnagiri 301 (statewide median ≈ 195); 113 distinct values
  spaced 6.27 kg/ha (titration step); Raigad = 5.3 % of samples but 60.9 % of total N variance; with Raigad N R² is
  0.812 random / 0.661 spatial (E42), without 0.706 / 0.393 (E48).
- **Interpretation, not verified:** that the cause is a district- or laboratory-level offset. Must be worded as
  "suggesting", not as fact.
- **Source:** SLUSI data republished on GitHub `ramSeraph/indian_land_features`, release `soil-health`
  (2025-01-09), licence CC0 1.0 (attribute Datameet and SLUSI); downloaded via indianopenmaps.com. SLUSI states no
  explicit reuse terms.

---

## B. Clarifications required (decisions for the editor / Paresh)

1. **Which dataset is primary?** (a) E49–E56, 32,096 samples, as in the 4-page summary; or (b) the S01 correction,
   24,599 samples (placeholder-GPS samples removed, elevation/climate at the sample's own site, random split grouped by
   30 m site, LRS excluding own site). S01 changes the headline by −0.01 to −0.04 and leaves all conclusions
   unchanged (`final/S01_correction_sprint_report.md`, Table 6). Option (a) keeps the known problems in C1–C2.
2. **Full texts** of Gupta & Patil (2026) and Kumar et al. (2026) — needed to describe their validation designs; not
   accessible to me.
3. Should the computing-time comparison stay (qualified) or be removed?
4. Workflow figure (Fig. 2): who draws it?

---

## C. Essential submission risks

1. **Placeholder coordinates in the E49–E56 data (material).** 7,486 of the 32,096 samples (23.3 %) sit in 30 m
   clusters of > 10 samples, which the project's own D08 step identified as many fields geotagged at one point
   (`audit/A01_output.txt` §2a). Their coordinates, Sentinel-2 pixel and LRS features describe the placeholder point.
   In a paper about spatial validation this is a central-claim risk if undisclosed. Addressed in S01.
2. **Borrowed elevation/climate (material for ~4 %).** In E49–E56 these come from the nearest de-clustered location:
   1,335 samples > 1 km away, max 12.6 km — all within the placeholder clusters (S01 §3).
3. **Co-located samples in the random split.** 54 % of random-split test samples have a training sample within 30 m
   (A01). The random-split R² therefore includes near-duplicate-site prediction; must be described as such (S01 uses
   a site-grouped split).
4. **Block size ≠ separation.** With 10 km blocks, 10.3 % of test samples have a training sample within 1 km
   (A01 §2b). The text must report measured distances, not imply "≥ 10 km".
5. **Incorrect statement in the summary/abstract:** "N and P … fell below 0.16 in Vidarbha and North Maharashtra" —
   **North MH P at 50 km is 0.314** (`50_block_size_final.csv`). Correct: N below 0.16 in Vidarbha (0.125) and North MH
   (0.158); P below 0.16 in Vidarbha (0.032) and Konkan (0.147).
6. **Mislabelled claim:** "Sentinel-2 reflectance explained … on its own (R² up to 0.32 for OC)" — that set is
   **Sentinel-2 + pH + EC**, not Sentinel-2 alone. Correct the wording.
7. **Novelty:** no "first" claim; Kumar et al. (2026) appears to compare random and spatial CV for available N in India
   (search summary; full text unread). An earlier cited "Frontiers 2025 Sentinel-2 R² 0.79–0.92" is wrong (that paper
   is a sensor-classification study); "Mundada & Jain (2025)" could not be located.
8. **Reproducibility:** E49–E56 depend on notebook kernel state (out-of-order cells, helper defined in an excluded
   cell); there is no standalone script for them. A standalone script exists only for S01
   (`final/reproduce_final.py`).

---

## D. Recommended writing plan

**Claims that can be written now (wording must carry the numbers of the chosen dataset, B1):**
1. A single LightGBM model reaches R² ≈ 0.53–0.71 (random split, by nutrient) but ≈ 0.32–0.59 under 10 km spatial
   blocks and ≈ 0.20–0.51 at 50 km.
2. The random-to-spatial drop is similar for five algorithms (in E51: N 0.31–0.35, P 0.21–0.26, K 0.21–0.24,
   OC 0.12–0.13).
3. The decline with distance differs by region (A7, with the corrected wording from C5).
4. LRS features and climate dominate; Sentinel-2 adds no accuracy beyond location-based inputs; satellite + pH/EC alone
   explains little (C6 wording).
5. Recommendation: report spatially blocked validation with measured train–test distances alongside random splits.

**Tables:** (1) data processing stages (A1); (2) headline, 5-seed mean ± SD; (3) R² by validation design, statewide and
regional mean; (4) five models; (5) ablation; (6) measured train–test distances per design; supplement: per-region
tables, Raigad sensitivity (E48), with/without placeholder samples if dataset (a) is kept.

**Figures:** Fig. 1 study area; Fig. 2 workflow (to draw); Fig. 3 measured vs predicted (seed 42, label as single run);
Fig. 4 R² vs block size. For dataset (b) use `results_final/Fig1/Fig3/Fig4`.

**Methods text needs:** the processing table (A1), limits, Sentinel-2 matching and bare-soil rule, feature list with
LRS definition and leakage controls (A4), model settings (A5), split definitions with seeds/folds/pooled scoring (A2),
metrics on original scale, Raigad rule with facts (A8, interpretation hedged), data source and licence (A8).

**Minimum still needed for submission:** decision B1; the two full texts (B2) or neutral wording without them;
corrected statements C5–C6; Fig. 2; the data-availability text (A8); the journal's template, keywords and declarations.
