# Manuscript handover — everything needed to write the paper

For the team member drafting the manuscript (and their AI agent). Approved by the handling editor on 2026-10-15.
Target: *Environmental Monitoring and Assessment* (Springer), submission 19 October 2026.

**Source of truth.** Primary analysis = experiments E49–E56 on **32,096 samples**. All numbers below come from the
original result files in `Start/results/` (files 49–57). Reproduction status: see §0.
**Do not use:** numbers from `Start/results_final/` or `S01_*` (separate sensitivity analysis on a different dataset),
numbers from E01–E48, or the old `PAPER_BRIEF.md` tables without the corrections in §6.

---

## 0. Reproduction status

**Reproduced exactly (2026-10-15).** The standalone script `Start/final/reproduce_E49_E56.py` (no notebook state;
4.7 min) re-ran E49–E56 from the processed data files. All six result files are **identical** to the originals
(maximum absolute difference 0 in every numeric column; 596 rows compared): `49_headline_metrics`,
`50_block_size_final`, `51_model_comparison_final`, `52_shap_final`, `53_input_ablation`, `56_headline_seeds`.
Evidence: `Start/results_repro/comparison_with_original.csv` and `run_log.txt`. Only the CPU-time column differs
between runs (timing is not deterministic; see §6.4).

## 1. Title and journal

- **Title:** *Validation design and sampling distance control the reported accuracy of soil nutrient prediction from
  Soil Health Card monitoring data in Maharashtra, India*
- **Journal:** Environmental Monitoring and Assessment — https://link.springer.com/journal/10661 (original research up
  to 9,000 words; abstract up to 350 words; check the current submission guidelines and template).

## 2. Abstract (≈ 330 words)

> India's Soil Health Card (SHC) programme provides laboratory analyses of millions of farm soil samples, and these
> data are increasingly used to train machine-learning models that map soil fertility. Such studies usually report
> accuracy from random train–test splits. We quantified how the validation design and the geographic separation between
> training and test samples change the reported accuracy of predicting available nitrogen (N), phosphorus (P),
> potassium (K) and organic carbon (OC) from 32,096 SHC samples collected in Maharashtra between January and May 2024.
> Predictors were bare-soil Sentinel-2 reflectance and spectral indices acquired within ±3 days of sampling, pH and
> electrical conductivity (EC) from the SHC laboratory analyses, elevation, climate, coordinates and local reference
> sample (LRS) features derived from the nearest training samples. A LightGBM model evaluated with a random 70/30 split
> achieved R² of 0.71 (N), 0.62 (P), 0.57 (K) and 0.70 (OC) (mean of five repetitions, SD ≤ 0.01); the median distance
> from a test sample to its nearest training sample was 24 m. Under spatially blocked cross-validation with 10 km blocks
> (median distance 4.7 km), R² fell to 0.39, 0.39, 0.34 and 0.56, and with 50 km blocks (median 14.2 km) to 0.23, 0.34,
> 0.21 and 0.48. Ridge regression, k-nearest neighbours, a multilayer perceptron and random forest showed similar
> declines (0.12–0.35). The decline differed between regions: with 50 km blocks, N and P retained R² of 0.30–0.53 in
> Marathwada and Western Maharashtra, whereas N fell to 0.16 or below in North Maharashtra, Vidarbha and Konkan. LRS
> features and climate were the most influential predictors. Without location inputs, Sentinel-2 reflectance together
> with pH and EC explained R² of 0.12–0.32 under the random split, and removing Sentinel-2 from the full model changed
> R² by less than 0.02. Reported accuracy therefore depends strongly on how far test samples are from training samples,
> and we recommend reporting spatially blocked validation with measured train–test distances alongside random splits
> in SHC-based soil fertility mapping.

## 3. Methods — facts to write (with sources)

**3.1 Data source.** Soil Health Card laboratory data published by the Soil and Land Use Survey of India (SLUSI),
obtained from the open republication by the Datameet community (GitHub `ramSeraph/indian_land_features`, release
`soil-health`, published 9 Jan 2025, licence CC0 1.0), accessed via indianopenmaps.com in August 2026. Credit SLUSI and
Datameet. Targets: available N (alkaline KMnO₄), available P, available K (kg/ha) and OC (%).

**3.2 Processing (Table A1).**

| Stage | Records |
|---|---|
| All-India SHC records | 5,182,371 |
| Maharashtra (state code 27) | 355,562 |
| Only record at its GPS point, parseable date, inside Maharashtra, numeric N/P/K | 119,814 |
| Sampled January–June | 91,818 |
| Sentinel-2 L2A scene within ±3 days, point inside scene footprint | 151,831 sample–scene pairs |
| 3×3 pixel windows extracted (Microsoft Planetary Computer) | 61,617 pairs |
| All 9 pixels bare soil (scene classification SCL = 5), complete window | 36,005 |
| Laboratory values outside limits removed | 34,578 |
| Reflectance outside 0–1 removed | 33,877 |
| Raigad district removed | **32,096** |

- Dates 1 Jan – 31 May 2024. Regions: Vidarbha 7,236; Marathwada 9,293; North Maharashtra 9,738; Western Maharashtra
  4,329; Konkan 1,500.
- Limits (keep if): 20 < N ≤ 1500 kg/ha; 1 < P ≤ 300; 20 < K ≤ 3000; 0 < OC ≤ 5 %; 3.5 ≤ pH ≤ 10.5; 0 < EC ≤ 10 dS/m.
  Reflectance = (DN − 1000)/10000.
- **Raigad (write as):** "Raigad district was excluded because 50.8 % of its samples report available N above
  850 kg/ha (median 872 kg/ha, compared with 301 kg/ha in the neighbouring Ratnagiri district); these 5.3 % of the
  samples accounted for 60.9 % of the total N variance. The pattern suggests a district-level measurement offset,
  which could not be verified." Report the with-Raigad result as a sensitivity in the supplement (N R² 0.81 random,
  0.66 spatial 10 km; E42/E48).
- **Location structure (one neutral sentence, optional):** "Sample locations are spatially clustered: 23.3 % of samples
  lie in groups of more than ten samples within 30 m, and 142 samples share identical coordinates; all were retained."
  Do **not** describe these records as invalid.

**3.3 Predictors (39 + 4).**
- Sentinel-2 (28): 12 bands (B01–B12, B8A) and 16 indices (NDVI, SAVI, NBR2, NDMI, NDWI, BSI, NDRE, CI, BI, RI, B4/B2,
  B11/B12, B12/B8, B11/B8, B7/B5, B6/B5); single date, median of the 3×3 window.
- pH and EC from the SHC laboratory analyses.
- **Elevation and climate (write as):** "Elevation (Copernicus DEM GLO-30) and six climate variables (TerraClimate:
  annual and monsoon precipitation, mean maximum, minimum and mean temperature, annual climatic water deficit) were
  extracted at 17,620 de-duplicated sample locations and assigned to each sample from the nearest extracted location
  (median distance 3 m; 95 % within 793 m; 4.2 % of samples more than 1 km away, maximum 12.6 km)." Do **not** write
  that every value was extracted at the sample's own coordinate.
- Coordinates: longitude, latitude.
- **LRS features (4):** from the 10 nearest *training* samples (Euclidean distance on a local metric projection):
  inverse-distance-weighted mean of log(1 + y) (distance floor 1 m), log(1 + y) of the nearest sample, log distance to
  the nearest sample, standard deviation of the 10 values. For test samples they are computed from training samples
  only; for training samples the sample itself is excluded. Test labels never enter.

**3.4 Model.** LightGBM (400 trees, learning rate 0.05, 15 leaves, min_child_samples 20, subsample 0.8,
colsample_bytree 0.5, L2 = 5; fixed a priori, not tuned). Target log(1 + y), standardised with training mean and SD;
predictions back-transformed; **all metrics on the original scale** (kg/ha, %). One statewide model per nutrient;
regional analysis = one model per region.
Comparison models (same inputs and splits; predictions clipped to the training range): ridge regression (α = 1),
k-nearest neighbours (k = 15, distance-weighted), multilayer perceptron (64-32, early stopping) — all on standardised
inputs — and random forest (100 trees, min_samples_leaf 5, max_features 0.33).

**3.5 Validation designs (write precisely).**
- Random 70/30: samples split at random (seed-controlled); R² on the 30 % test set.
- Spatial block cross-validation: samples assigned to square blocks of 10, 25, 50 or 100 km on a local metric grid;
  blocks randomly allocated to 5 folds; each fold predicted by a model trained on the other four; R² computed on the
  pooled out-of-fold predictions. **No buffer between folds — blocks do not guarantee a minimum distance; the measured
  distances are reported (Table 3).** Do not write "test samples at least 10 km from training".
- Repetitions: the headline (random 70/30 and 10 km) repeated with five seeds (42, 7, 13, 99, 2024; each seed changes
  the split, the fold allocation and the model seed); all other analyses are single runs with seed 42.
- Metrics: R², RMSE, MAE, bias, RPIQ = (Q3 − Q1)/RMSE.
- Importance: exact tree SHAP (LightGBM `pred_contrib`) on test data only; input ablation by retraining without
  input groups.

## 4. Results — tables (copy exactly; label as shown)

**Table 1. Headline, statewide LightGBM — mean ± SD of five repetitions** (`results/56_headline_seeds.csv`)

| Evaluation | N | P | K | OC |
|---|---|---|---|---|
| R², random 70/30 | 0.705 ± 0.006 | 0.620 ± 0.006 | 0.573 ± 0.010 | 0.702 ± 0.010 |
| RMSE, random 70/30 | 54.0 ± 0.8 | 15.2 ± 0.5 | 163.5 ± 2.3 | 0.213 ± 0.006 |
| R², spatial 10 km blocks | 0.390 ± 0.031 | 0.393 ± 0.008 | 0.343 ± 0.015 | 0.562 ± 0.015 |
| RMSE, spatial 10 km blocks | 76.8 ± 1.9 | 19.3 ± 0.1 | 201.8 ± 2.3 | 0.263 ± 0.004 |

Units: kg/ha (N, P, K), % (OC). Supplementary (single run, seed 42; `results/49_headline_metrics.csv`): MAE random
34.6 / 6.49 / 102 / 0.126, spatial 45.9 / 8.80 / 128 / 0.153; RPIQ random 1.69 / 0.77 / 1.72 / 1.17; training R²
0.75 / 0.74 / 0.65 / 0.79.

**Table 2. R² against validation design — single run (seed 42)** (`results/50_block_size_final.csv`)

| Validation | Statewide N | P | K | OC | Regional mean N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Random 70/30 | 0.71 | 0.61 | 0.56 | 0.70 | 0.64 | 0.59 | 0.48 | 0.50 |
| Spatial 10 km | 0.39 | 0.40 | 0.35 | 0.58 | 0.38 | 0.33 | 0.23 | 0.32 |
| Spatial 25 km | 0.31 | 0.37 | 0.27 | 0.50 | 0.29 | 0.31 | 0.17 | 0.28 |
| Spatial 50 km | 0.23 | 0.34 | 0.21 | 0.48 | 0.22 | 0.28 | 0.12 | 0.21 |
| Spatial 100 km | 0.22 | 0.29 | 0.17 | 0.33 | 0.17 | 0.24 | 0.06 | 0.17 |

**Table 3. Distance from each test sample to its nearest training sample — seed 42, exact E49/E50 splits**
(`results/57_train_test_distances_E49_E50.csv`)

| Validation | 5th pct | Median | 95th pct | ≤ 30 m | ≤ 1 km | ≤ 5 km |
|---|---|---|---|---|---|---|
| Random 70/30 | 1 m | 24 m | 1.4 km | 53.7 % | 93.1 % | 98.8 % |
| Spatial 10 km | 0.57 km | 4.7 km | 12.1 km | 0.3 % | 10.2 % | 53.7 % |
| Spatial 25 km | 1.1 km | 9.0 km | 20.7 km | 0.2 % | 4.7 % | 23.9 % |
| Spatial 50 km | 2.5 km | 14.2 km | 28.7 km | 0.0 % | 1.8 % | 11.6 % |
| Spatial 100 km | 4.0 km | 22.2 km | 47.6 km | 0.2 % | 1.5 % | 7.1 % |

**Table 4. R² at 50 km blocks by region — single run (seed 42)** (`results/50_block_size_final.csv`; all designs per
region in the supplement)

| Region (samples) | N | P | K | OC |
|---|---|---|---|---|
| Marathwada (9,293) | 0.46 | 0.53 | 0.20 | 0.11 |
| Western Maharashtra (4,329) | 0.30 | 0.39 | −0.17 | 0.49 |
| North Maharashtra (9,738) | 0.16 | 0.31 | −0.07 | 0.19 |
| Vidarbha (7,236) | 0.13 | 0.03 | 0.46 | 0.06 |
| Konkan (1,500) | 0.06 | 0.15 | 0.18 | 0.20 |

**Table 5. Five algorithms, R² random 70/30 → spatial 10 km — single run (seed 42)**
(`results/51_model_comparison_final.csv`)

| Model | N | P | K | OC |
|---|---|---|---|---|
| Ridge regression | 0.70 → 0.36 | 0.60 → 0.35 | 0.55 → 0.32 | 0.70 → 0.57 |
| k-nearest neighbours | 0.65 → 0.33 | 0.56 → 0.35 | 0.51 → 0.30 | 0.68 → 0.56 |
| Multilayer perceptron | 0.70 → 0.35 | 0.60 → 0.34 | 0.55 → 0.32 | 0.69 → 0.56 |
| Random forest | 0.71 → 0.39 | 0.62 → 0.39 | 0.57 → 0.35 | 0.71 → 0.59 |
| LightGBM | 0.71 → 0.39 | 0.61 → 0.40 | 0.56 → 0.35 | 0.70 → 0.58 |

Drop: N 0.31–0.35, P 0.21–0.26, K 0.21–0.24, OC 0.12–0.13.

**Table 6. Input ablation, R² random 70/30 / spatial 10 km — single run (seed 42)** (`results/53_input_ablation.csv`)

| Inputs | N | P | K | OC |
|---|---|---|---|---|
| All (39 + LRS) | 0.71 / 0.39 | 0.61 / 0.40 | 0.56 / 0.35 | 0.70 / 0.58 |
| Without Sentinel-2 (11 + LRS) | 0.71 / 0.39 | 0.62 / 0.38 | 0.57 / 0.36 | 0.70 / 0.58 |
| Without LRS (39) | 0.61 / 0.33 | 0.53 / 0.36 | 0.50 / 0.31 | 0.68 / 0.56 |
| LRS only (4) | 0.69 / 0.33 | 0.59 / 0.37 | 0.55 / 0.29 | 0.69 / 0.53 |
| Sentinel-2 + pH + EC, no location (30) | 0.17 / 0.04 | 0.12 / 0.03 | 0.16 / 0.05 | 0.32 / 0.20 |

**Table 7. SHAP share by input group (%), random test / spatial 10 km — single run (seed 42)**
(`results/52_shap_final.csv`)

| Input group | N | P | K | OC |
|---|---|---|---|---|
| LRS features (4) | 63.8 / 61.0 | 62.9 / 62.6 | 62.7 / 59.9 | 63.6 / 62.6 |
| Climate (6) | 14.7 / 15.5 | 11.5 / 11.0 | 10.2 / 11.0 | 13.5 / 13.0 |
| Sentinel-2 bands + indices (28) | 11.2 / 12.8 | 10.9 / 11.9 | 10.8 / 12.4 | 11.8 / 12.9 |
| Coordinates (2) | 6.0 / 5.8 | 9.2 / 9.5 | 10.2 / 10.1 | 7.7 / 7.8 |
| pH, EC (2) | 2.3 / 3.0 | 3.9 / 3.7 | 4.6 / 4.6 | 2.6 / 2.6 |
| Elevation (1) | 2.1 / 1.9 | 1.6 / 1.3 | 1.5 / 1.9 | 0.8 / 1.1 |

## 5. Figures and captions

| Fig. | File | Caption must say |
|---|---|---|
| 1 | `results/54_study_area_map.png` | 32,096 samples by region, January–May 2024 |
| 2 | **to draw** (workflow: SHC data → filtering → Sentinel-2 matching and bare-soil mask → predictors incl. LRS → LightGBM → random 70/30 and spatial blocks 10–100 km, statewide and regional → metrics, SHAP, ablation) | — |
| 3 | `results/49_measured_vs_predicted.png` | "single run (seed 42)"; top: random 70/30 test; bottom: spatial 10 km out-of-fold |
| 4 | `results/55_r2_vs_block_size.png` | "single run (seed 42)"; statewide model and mean of five regional models |

## 6. Mandatory wording corrections

1. **Regional sentence** (replaces "N and P fell below 0.16 in Vidarbha and North Maharashtra", which is wrong):
   "With 50 km blocks, N and P retained R² of 0.30–0.53 in Marathwada and Western Maharashtra. N fell to 0.16 or below
   in North Maharashtra, Vidarbha and Konkan, and P to 0.15 or below in Vidarbha and Konkan, while P in North
   Maharashtra retained 0.31."
2. **Sentinel-2:** never "Sentinel-2 alone". Write: "Without location inputs, Sentinel-2 reflectance and indices
   together with pH and EC explained R² of 0.12–0.32 under the random split (highest for OC) and 0.03–0.20 under 10 km
   blocks. In the full model, Sentinel-2 inputs received 11–13 % of the SHAP attribution, but removing them changed R²
   by less than 0.02." (Attribution is not added accuracy.)
3. **Random split interpretation:** "Under the random split, 53.7 % of test samples had a training sample within 30 m;
   random-split accuracy therefore reflects prediction at or next to already-sampled sites."
4. **Computing time (optional; else drop):** "In two runs, the random forest (100 trees) required 15–18 times the CPU
   time of LightGBM (400 trees) with similar accuracy (823–833 vs 47–55 CPU-seconds over all jobs)." Do not write
   "one-eighteenth" as a fixed ratio.
5. Label every R² with its validation design; label single-run vs five-repetition values.
6. Use "local reference sample (LRS) features"; never "interpolation", "spatial context" or "neighbourhood context".

## 7. Related work — verified citations only

Verified (Crossref): use these, with claims limited to what is stated.
- Roberts D.R. et al. (2017) Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic
  structure. *Ecography* 40:913–929. doi:10.1111/ecog.02881 — random CV underestimates error for structured data;
  block CV for prediction to new data.
- Ploton P. et al. (2020) Spatial validation reveals poor predictive performance of large-scale ecological mapping
  models. *Nat Commun* 11:4540. doi:10.1038/s41467-020-18321-y — non-spatial validation >50 % explained vs near-null
  under spatial validation.
- Meyer H. et al. (2019) Importance of spatial predictor variable selection in machine learning applications.
  *Ecol Model* 411:108815. doi:10.1016/j.ecolmodel.2019.108815.
- Wadoux A.M.J.-C. et al. (2021) Spatial cross-validation is not the right way to evaluate map accuracy. *Ecol Model*
  457:109692. doi:10.1016/j.ecolmodel.2021.109692 — cite as the counter-view.
- Valavi R. et al. (2019) blockCV: an R package for generating spatially or environmentally separated folds.
  *Methods Ecol Evol* 10:225–232. doi:10.1111/2041-210X.13107.
- Gupta C., Patil N. (2026) Smart Agriculture: Spatial Context-Based Nutrient Prediction and Crop-Fertilizer
  Recommendations Using Remote Sensing and Soil Health Data. *J Indian Soc Remote Sens* 54:2405–2421.
  doi:10.1007/s12524-026-02443-9 — abstract only: Karnataka, 168,000 instances, Landsat-8/9 + SHC, geolocation and local
  neighbourhood context, LightGBM, R² 0.77 (N), 0.61 (P), 0.72 (K), 0.71 (OC). Their validation design is not stated in
  the abstract — do not describe it.
- Garg A.K. et al. (2026) Spatial assessment of soil health in the Krishna Delta using machine learning and land use
  patterns. *Discover Soil* 3:95. doi:10.1007/s44378-026-00243-8 — RF best; R² 0.43 (OC), 0.51 (K₂O).
- Moharana P.C. et al. (2023) Digital mapping of soil health card parameters and nutrient management zones in the Thar
  Desert regions of India using quantile regression forest techniques. *Arab J Geosci* 16:560.
  doi:10.1007/s12517-023-11670-0 — cite by topic only.
- Kumar A. et al. (2026) Prediction of soil available nitrogen using machine learning and digital mapping techniques in
  Northeast India. *Environmental Challenges* 22:101375. doi:10.1016/j.envc.2025.101375 — cite by topic only (full text
  not read; do not quote its results).
- Balkrishna A. et al. (2026) Contemporary soil health research (2020–2025) and its implications for India's Soil
  Health Card framework: a systematic review. *Soil Advances* 5:100124. doi:10.1016/j.soilad.2026.100124.

**Do not:** claim "first"; cite Gunasekaran et al. 2025 (Front. Soil Sci.) as a Sentinel-2/SHC study (it is not);
cite "Mundada & Jain 2025" (not found); cite the IBM paper (Kaur et al. 2020).

**Contribution (write in these terms):** (1) state-scale SHC data (32,096 samples) with Sentinel-2 matched within
±3 days under a strict bare-soil mask; (2) accuracy quantified across four block sizes with measured train–test
distances, statewide and per region, for N, P, K and OC; (3) the same random-to-spatial decline for five algorithms;
(4) the incremental contribution of Sentinel-2 separated from its attribution and stand-alone performance;
(5) recommendation for reporting validation design and distances in SHC-based mapping.

## 8. Limitations to state

One season of one year (Jan–May 2024) and one state; single-date Sentinel-2; pH and EC are laboratory values;
elevation/climate assigned from the nearest extracted location (§3.3); spatially clustered sample locations retained
(§3.2); spatial blocks without buffer (distances in Table 3); headline repeated five times, other analyses single runs;
regional values at 50–100 km rest on few blocks (variation of a few hundredths expected); hyperparameters fixed, not
tuned; Raigad excluded (offset unverified).

## 9. Declarations and availability

- **Data availability:** SHC data: SLUSI, via Datameet republication (CC0 1.0; §3.1). Sentinel-2 L2A, Copernicus DEM
  GLO-30 and TerraClimate via Microsoft Planetary Computer.
- **Code availability:** `Start/final/reproduce_E49_E56.py` (reproduces all E49–E56 results from the processed files)
  and `Start/final/distances_E49_E50.py`; repository link to be added.
- Competing interests, funding, author contributions: to be filled by the authors.
