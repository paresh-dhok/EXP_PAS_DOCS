> **SUPERSEDED (2026-10-15):** use `TEAM_SHARE/MANUSCRIPT_HANDOVER.md` for writing the paper (approved by the
> handling editor; corrected sentences, labelled tables, verified citations). This brief is kept for history only.

# Paper brief — everything needed to write the paper

For the team member writing the paper and their AI agent. Final version, approved 2026-10-14.
Every number below comes from a documented experiment in `05_experiments/` (E49–E56 unless stated) with its CSV or
figure in `04_results/`. Do not use numbers from older experiments (E01–E48) in the paper; they belong to earlier
setups.

---

## 1. Journal and title

- **Journal:** *Environmental Monitoring and Assessment* (Springer) — https://link.springer.com/journal/10661
  - Impact factor 3.6 (2025), median 10 days from submission to first decision, no submission deadline.
  - Original research article: up to 9,000 words; abstract up to 350 words. Check the current guidelines:
    https://link.springer.com/journal/10661/submission-guidelines
  - Fallback if desk-rejected: *Journal of the Indian Society of Remote Sensing* (Springer,
    https://link.springer.com/journal/12524; abstract ≤ 200 words; IF 2.1).
- **Title:** *Validation design and sampling distance control the reported accuracy of soil nutrient prediction from
  Soil Health Card monitoring data in Maharashtra, India*

## 2. Core idea

1. Take **one base model** (LightGBM) and reach high accuracy with a **random 70/30 split**.
2. Test the **same model** with **spatially blocked cross-validation** (10, 25, 50, 100 km blocks), statewide and
   inside each of five regions.
3. Show that the drop occurs for **every algorithm** (five models), show **which inputs drive the predictions**, and
   give a **recommendation for monitoring and validation practice**.

**Novelty (one paragraph at the end of the Introduction):** the first quantified evaluation of how validation design
and distance to measured samples change the reported accuracy of Soil Health Card–based nutrient prediction at state
scale; the decline is the same for five algorithms; it differs by region; date-matched bare-soil Sentinel-2 adds little
once local reference information is used. **Do a literature check before writing "first".**

## 3. Data (Study area and data section)

| Step | Samples |
|---|---|
| SHC records, Maharashtra (SLUSI / Soil Health Card portal) | 355,562 |
| Sampled January–June, with coordinates | 91,818 |
| Sentinel-2 L2A scene within ±3 days of sampling | 151,831 sample–scene pairs |
| 3×3-pixel window extracted (Microsoft Planetary Computer) | 61,617 pairs |
| All 9 pixels bare soil (scene classification SCL = 5), complete window | 36,005 |
| Impossible soil values removed (limits below) | 34,578 |
| Reflectance outside 0–1 removed | 33,877 |
| **Raigad district excluded** (reason below) | **32,096** |

- All samples January–May 2024. Regions: Vidarbha 7,236; Marathwada 9,293; North Maharashtra 9,738;
  Western Maharashtra 4,329; Konkan 1,500.
- **Cleaning limits (keep if):** 20 < N ≤ 1500 kg/ha; 1 < P ≤ 300 kg/ha; 20 < K ≤ 3000 kg/ha; 0 < OC ≤ 5 %;
  3.5 ≤ pH ≤ 10.5; 0 < EC ≤ 10 dS/m. Values outside were unit/decimal errors or placeholders (e.g. N = 1).
- **Reflectance:** (DN − 1000) / 10000 (Sentinel-2 processing baseline ≥ 04.00).
- **Raigad sentence (use as is or close to it):** "Raigad district was excluded because half of its samples report
  available N above 850 kg/ha (median 872 kg/ha, compared with about 195 kg/ha across the state and 301 kg/ha in the
  neighbouring Ratnagiri district), indicating a district-level laboratory offset." (Source: E47.)
- Targets are SHC laboratory values: available N (alkaline KMnO₄), available P, available K (kg/ha) and OC (%).

## 4. Inputs (39 + 4)

| Group | Inputs | Source |
|---|---|---|
| Sentinel-2 (28) | 12 bands (B01–B12, B8A) + 16 indices: NDVI, SAVI, NBR2, NDMI, NDWI, BSI, NDRE, CI, BI, RI, B4/B2, B11/B12, B12/B8, B11/B8, B7/B5, B6/B5 | Sentinel-2 L2A, median of the 3×3 window, scene within ±3 days |
| Soil properties (2) | pH, EC | SHC laboratory analyses |
| Elevation (1) | elevation | Copernicus DEM GLO-30 |
| Climate (6) | annual precipitation, monsoon (June–Sept) precipitation, mean Tmax, Tmin, Tmean, annual climatic water deficit | TerraClimate |
| Coordinates (2) | longitude, latitude | SHC |
| **Local reference sample (LRS) features (4)** | from the 10 nearest **training** samples: inverse-distance-weighted mean of log(1+value), log value of the nearest sample, log distance to the nearest sample, standard deviation of the 10 log values | computed inside each training fold only |

**LRS features — how to describe them:** they summarise the laboratory values of the nearest training samples, which
act as local references for the field being predicted. They are computed only from the training part of each split or
fold; for training rows the sample itself is excluded. Test values are never used (no leakage).
**Use the term "local reference sample (LRS) features" throughout. Do not use "spatial context", "neighbourhood
context" or "interpolation".**

## 5. Model and validation (Methods)

- **Base model:** LightGBM — 400 trees, learning rate 0.05, 15 leaves, min_child_samples 20, subsample 0.8,
  colsample_bytree 0.5, L2 regularisation 5. Target log(1 + y), standardised; predictions back-transformed. One
  statewide model per nutrient.
- **Comparison models (same inputs and tests):** ridge regression (α = 1, standardised inputs); k-nearest neighbours
  (k = 15, distance-weighted, standardised); multilayer perceptron (64-32, early stopping, standardised); random forest
  (100 trees, min_samples_leaf 5, max_features 0.33).
- **Validation designs:**
  1. Random 70/30 split.
  2. Spatially blocked 5-fold cross-validation: square blocks of 10, 25, 50 and 100 km assigned to folds
     (`GroupKFold`, shuffled).
  3. Both statewide and with one model per region.
  4. Headline repeated with 5 seeds (42, 7, 13, 99, 2024); each seed changes the split, the fold assignment and the
     model seed.
- **Metrics:** R², RMSE, MAE, bias, RPIQ = (Q3 − Q1) / RMSE.
- **Importance:** exact tree SHAP from LightGBM (`pred_contrib`), computed on test data only; plus input ablation
  (removing groups and retraining).

## 6. Results

**Table 1 — Headline, statewide LightGBM (mean ± SD of 5 seeds; E56)**

| | N | P | K | OC |
|---|---|---|---|---|
| R², random 70/30 | 0.71 ± 0.01 | 0.62 ± 0.01 | 0.57 ± 0.01 | 0.70 ± 0.01 |
| RMSE, random 70/30 | 54.0 kg/ha | 15.2 kg/ha | 163.5 kg/ha | 0.21 % |
| R², spatial 10 km | 0.39 ± 0.03 | 0.39 ± 0.01 | 0.34 ± 0.02 | 0.56 ± 0.02 |
| RMSE, spatial 10 km | 76.8 kg/ha | 19.3 kg/ha | 201.8 kg/ha | 0.26 % |

Full metrics for seed 42 (E49): random 70/30 test — MAE 34.6 / 6.49 / 101.6 / 0.126; RPIQ 1.69 / 0.77 / 1.72 / 1.17;
spatial 10 km — MAE 45.9 / 8.80 / 127.7 / 0.153; RPIQ 1.21 / 0.62 / 1.44 / 0.97. Train R² (random): 0.75 / 0.74 /
0.65 / 0.79 (no strong overfitting).

**Table 2 — R² against validation design, statewide (seed 42; E50)**

| Test | N | P | K | OC |
|---|---|---|---|---|
| Random 70/30 | 0.71 | 0.61 | 0.56 | 0.70 |
| Spatial 10 km | 0.39 | 0.40 | 0.35 | 0.58 |
| Spatial 25 km | 0.31 | 0.37 | 0.27 | 0.50 |
| Spatial 50 km | 0.23 | 0.34 | 0.21 | 0.48 |
| Spatial 100 km | 0.22 | 0.29 | 0.17 | 0.33 |

Regional models (mean of 5 regions): random 0.65 / 0.59 / 0.48 / 0.50; 10 km 0.38 / 0.33 / 0.23 / 0.32;
50 km 0.22 / 0.28 / 0.12 / 0.21; 100 km 0.17 / 0.24 / 0.06 / 0.17. Per-region values: E50.

**Regional differences (E50):** N and P keep R² of 0.30–0.53 at 50 km in Marathwada and Western Maharashtra, but fall
below 0.16 in Vidarbha and North Maharashtra. OC holds best in Western Maharashtra (0.49 at 50 km). K in Western
Maharashtra is below zero under every spatial test. Konkan (1,500 samples) reaches 0.78 for N with a random split
but about 0.13 at 10 km.

**Table 3 — Five models, R² random 70/30 → spatial 10 km (seed 42; E51)**

| Model | N | P | K | OC |
|---|---|---|---|---|
| Ridge regression | 0.70 → 0.36 | 0.60 → 0.35 | 0.55 → 0.32 | 0.70 → 0.57 |
| k-nearest neighbours | 0.65 → 0.33 | 0.56 → 0.35 | 0.51 → 0.30 | 0.68 → 0.56 |
| Multilayer perceptron | 0.70 → 0.35 | 0.60 → 0.34 | 0.55 → 0.32 | 0.70 → 0.56 |
| Random forest | 0.71 → 0.39 | 0.62 → 0.39 | 0.57 → 0.35 | 0.71 → 0.59 |
| **LightGBM (base)** | **0.71 → 0.39** | **0.61 → 0.40** | **0.56 → 0.35** | **0.70 → 0.58** |

Drop for every model: N 0.31–0.35, P 0.21–0.26, K 0.21–0.24, OC 0.12–0.13. LightGBM equals random forest at about
1/18 of the computing time (47 vs 823 CPU seconds). RMSE per model: E51.

**Inputs (E52 SHAP, E53 ablation):**
- SHAP share (random 70/30 test): LRS features 63–64 %, climate 10–15 %, coordinates 6–10 %, Sentinel-2
  (bands + indices) 11–12 %, pH and EC 2–5 %, elevation 1–2 %. Same ranking under spatial testing.
- Ablation, R² random / spatial 10 km:

| Inputs | N | P | K | OC |
|---|---|---|---|---|
| All (39 + LRS) | 0.71 / 0.39 | 0.61 / 0.40 | 0.56 / 0.35 | 0.70 / 0.58 |
| Without Sentinel-2 | 0.71 / 0.39 | 0.62 / 0.38 | 0.57 / 0.36 | 0.70 / 0.58 |
| Without LRS features | 0.61 / 0.33 | 0.53 / 0.36 | 0.50 / 0.31 | 0.68 / 0.56 |
| LRS features only | 0.69 / 0.33 | 0.59 / 0.37 | 0.55 / 0.29 | 0.69 / 0.53 |
| Sentinel-2 + pH, EC only | 0.17 / 0.04 | 0.12 / 0.03 | 0.16 / 0.05 | 0.32 / 0.20 |

  Wording: "LRS features and climate were the most influential predictors. Sentinel-2 reflectance explained part of
  the variation on its own (R² up to 0.32 for OC) but contributed little additional information once LRS features
  were included. Under spatial testing, climate and coordinates added 0.03–0.06 over the LRS features alone."

## 7. Figures

| No. | Figure | File |
|---|---|---|
| 1 | Study-area map: 32,096 samples by region, scale bar, north arrow | `04_results/54_study_area_map.png` (points for QGIS: `54_sample_points.csv`) |
| 2 | Workflow diagram — **to draw** (PowerPoint / draw.io): SHC data → cleaning → Sentinel-2 matching (±3 days, bare-soil mask, 3×3 window) → inputs (+ elevation, climate, LRS) → LightGBM → validation designs (random 70/30; spatial 10–100 km; statewide and regional; 5 seeds) → metrics, SHAP, ablation | — |
| 3 | Measured vs predicted, random 70/30 (top) and spatial 10 km (bottom), N/P/K/OC | `04_results/49_measured_vs_predicted.png` |
| 4 | R² against validation design, statewide and regional panels | `04_results/55_r2_vs_block_size.png` |

Optional improvement: Figure 1 in QGIS with Maharashtra boundary and an India inset.

## 8. Abstract (≈ 275 words; EMA limit 350)

> India's Soil Health Card (SHC) programme provides laboratory analyses of millions of farm soil samples, and these
> data are increasingly used to train machine-learning models that map soil fertility. Such studies usually report
> accuracy from random train–test splits. We quantified how the validation design and the distance to measured samples
> change the reported accuracy of predicting available nitrogen (N), phosphorus (P), potassium (K) and organic carbon
> (OC) from 32,096 SHC samples collected in Maharashtra between January and May 2024. Predictors were bare-soil
> Sentinel-2 reflectance and spectral indices acquired within ±3 days of sampling, pH and electrical conductivity (EC)
> from the SHC laboratory analyses, elevation, climate, coordinates and local reference sample (LRS) features derived
> from the nearest training samples. A LightGBM model evaluated with a random 70/30 split achieved R² of 0.71 (N),
> 0.62 (P), 0.57 (K) and 0.70 (OC) (mean of five repetitions, SD ≤ 0.01). Under spatially blocked cross-validation the
> same model reached 0.39, 0.39, 0.34 and 0.56 with 10 km blocks, and 0.23, 0.34, 0.21 and 0.48 with 50 km blocks.
> Ridge regression, k-nearest neighbours, a multilayer perceptron and random forest showed similar declines
> (0.12–0.35), so the validation design changed R² far more than the choice of algorithm. The decline with distance
> differed between regions: N and P retained R² of 0.30–0.53 at 50 km in Marathwada and Western Maharashtra but fell
> below 0.16 in Vidarbha and North Maharashtra. LRS features and climate were the most influential predictors;
> Sentinel-2 reflectance explained part of the variation on its own (R² up to 0.32 for OC) but contributed little
> additional information once LRS features were included. Accuracy reported from random splits therefore reflects the
> density of the existing sampling network more than the transferability of the model. We recommend reporting
> spatially blocked validation at several distances alongside random splits in SHC-based soil fertility mapping.

## 9. Paper structure and what goes where

1. **Introduction** — SHC programme and its data; ML mapping of soil nutrients (cite Gupta & Patil 2026 and other
   SHC / Sentinel-2 studies); validation of spatial models (Ploton et al. 2020; Meyer et al. 2019; Wadoux et al. 2021);
   gap: SHC studies report random splits; novelty paragraph (section 2).
2. **Study area and data** — Figure 1; SHC laboratory methods; data steps and cleaning limits (section 3); Raigad
   sentence.
3. **Methods** — Figure 2; Sentinel-2 matching and bare-soil mask; inputs (section 4) incl. LRS definition;
   LightGBM; comparison models; validation designs; metrics; SHAP and ablation.
4. **Results** — Table 1 + Figure 3; Table 2 + Figure 4; regional differences; Table 3; inputs (SHAP + ablation).
5. **Discussion**
   - Why random splits score higher: test fields have measured samples close by in the training data, which the LRS
     features and coordinates exploit; spatial blocks remove that advantage.
   - Monitoring implication: accuracy depends on sampling density; predictions are most reliable close to existing
     samples and degrade with distance; regions differ.
   - Sentinel-2: bare-soil reflectance carries a weak signal (mainly OC, consistent with darker soils being richer in
     organic matter) but adds little beyond local reference and climate information.
   - Comparison with published values: SHC-based studies with geolocation report R² of 0.6–0.8 (e.g. Gupta & Patil
     2026: 0.77 N, 0.61 P, 0.72 K, 0.71 OC); our random-split values are similar, our spatial values show what
     remains for new areas. Neutral tone — do not criticise them.
   - Limitations: one season of one year, one state, single-date Sentinel-2, laboratory pH and EC.
6. **Conclusion and recommendations** — report spatially blocked validation at several distances alongside random
   splits; state the distance at which results were obtained.
7. **Statements** — Data availability (SHC data public on the Soil Health Card portal; code on GitHub); competing
   interests (none); author contributions; funding (none).

## 10. Wording rules

1. Label every R² with its test ("random 70/30", "spatial 10 km blocks").
2. Use **"local reference sample (LRS) features"**. Never "spatial context", "neighbourhood context" or
   "interpolation".
3. pH and EC: "from the SHC laboratory analyses". No sensor, hardware or low-cost framing.
4. Do not claim that Sentinel-2 drives the predictions.
5. Cite Gupta & Patil (2026) neutrally.
6. Leave out of the paper: kriging, class (low/medium/high) results, the sensor-noise test (E45), hardware, the
   GPS-cluster analysis, the IBM paper (Kaur et al. 2020), the 16-model comparison (E23–E30).
7. Every number from E49–E56 (or the files cited above). Round R² to two decimals in text, three in tables if wanted.

## 11. Desk-rejection checklist (EMA)

- [ ] Title and abstract lead with the validation/monitoring message (not with Sentinel-2).
- [ ] Novelty paragraph at the end of the Introduction; literature check done.
- [ ] 2–3 recent references from EMA itself and 1–2 from JISRS (incl. Gupta & Patil 2026).
- [ ] Four figures at 300 dpi; tables with units; every R² labelled with its test.
- [ ] Springer template; abstract ≤ 350 words; text ≤ 9,000 words; keywords.
- [ ] Statements: data availability, code availability, competing interests, author contributions, funding.
- [ ] Cover letter: fit to EMA (validation and design of soil monitoring data), novelty in two sentences, not under
      review elsewhere.
- [ ] Similarity check below about 10–15 %; clear English.

## 12. Prepared answers for reviewers (do NOT put in the paper; for the response letter)

| Likely question | Answer and source |
|---|---|
| Why use laboratory pH/EC as inputs? | They carry 2–5 % of SHAP; retraining without them changes R² by ≤ 0.012 (E45, row "retrained without pH, EC", data incl. Raigad) |
| Is the model more than nearby-sample averaging? | LRS-only is close under random splits but 0.03–0.06 lower under spatial testing (E53) |
| Why exclude Raigad? | E47/E48: 5.3 % of samples carry 61 % of N variance; with Raigad N R² is 0.81 random / 0.66 spatial |
| Duplicate or co-located samples? | Merging samples within 30 m changed R² by ≤ 0.05 (E39) |
| Single split / seed? | Five seeds, SD ≤ 0.01 (random), ≤ 0.03 (spatial) (E56) |

## 13. Key references

- Gupta C., Patil N. (2026) Smart Agriculture: Spatial Context-Based Nutrient Prediction and Crop-Fertilizer
  Recommendations Using Remote Sensing and Soil Health Data. *J Indian Soc Remote Sens* 54:2405–2421.
  doi:10.1007/s12524-026-02443-9
- Ploton P. et al. (2020) Spatial validation reveals poor predictive performance of large-scale ecological mapping
  models. *Nat Commun* 11:4540. doi:10.1038/s41467-020-18321-y
- Meyer H. et al. (2019) Importance of spatial predictor variable selection in machine learning applications.
  *Ecol Model* 411:108815. doi:10.1016/j.ecolmodel.2019.108815
- Wadoux A.M.J.-C. et al. (2021) Spatial cross-validation is not the right way to evaluate map accuracy.
  *Ecol Model* 457:109692. doi:10.1016/j.ecolmodel.2021.109692
- Data sources: Sentinel-2 L2A (ESA/Copernicus via Microsoft Planetary Computer); Copernicus DEM GLO-30;
  TerraClimate (Abatzoglou et al. 2018, *Sci Data* 5:170191); LightGBM (Ke et al. 2017, NeurIPS);
  SHAP (Lundberg & Lee 2017, NeurIPS).

**Verify every reference (authors, year, volume, DOI) before submission.**
