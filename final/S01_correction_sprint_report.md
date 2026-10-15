# S01 — Correction sprint: final dataset, final results and remaining issues

Date: 2026-10-15. For the handling editor. Follows audit A01 (`Start/audit/A01_audit_report.md`).
**All numbers below come from one executed standalone script, `Start/final/reproduce_final.py`
(run 2026-10-15, 14.9 min, exit code 0), log `Start/results_final/run_log.txt`. No notebook state is involved.**
E39–E56 numbers are superseded and must not be used in the manuscript.

---

## 1. Raw-data provenance (resolved)
- Downloaded via the Indian Open Maps viewer (`indianopenmaps.com`, layer `soil-health/slusi`), which serves the GitHub
  release **ramSeraph/indian_land_features, tag `soil-health`** (published 2025-01-09; files `SLUSI_SHC.parquet`,
  `SLUSI_SHC.geojsonl.7z`; 5,182,371 records).
- Stated original source: **Soil and Land Use Survey of India (SLUSI), https://slusi.da.gov.in/**.
- Stated licence: **CC0 1.0**, with the request to attribute the Datameet community and the original government source
  (`github.com/ramSeraph/indianopenmaps/blob/main/DATA_LICENSE.md`).
- Remaining uncertainty: the SLUSI website shows "© 2024 SLUSI" and no explicit reuse terms; no reuse terms specific
  to this dataset were found. Low risk; state the source chain and credit SLUSI and Datameet.

## 2. Final dataset (resolved)

| Step | Samples | File |
|---|---|---|
| Clean bare-soil set (D07: SCL = 5 in all 9 pixels of the 3×3 window, scene within ±3 days, impossible values removed, reflectance 0–1) | 33,877 | `mh_model_dataset.parquet` |
| − Raigad (district 491; median N 872 kg/ha, district-level laboratory offset; E47/E48) | 32,096 | |
| − samples in 30 m clusters of > 10 samples (placeholder GPS; D08 rule) | 24,610 | |
| − samples whose elevation/climate source location is > 100 m away | **24,599** | `results_final/F00_final_dataset_ids.parquet` |

- 16,759 sites (30 m clusters): 13,064 single-sample sites; 3,695 multi-sample sites holding 11,535 samples.
- Regions: Vidarbha 5,564; Marathwada 5,782; North Maharashtra 8,017; Western Maharashtra 3,819; Konkan 1,417.
- Means (SD): N 203.3 (104.8) kg/ha; P 23.7 (26.1) kg/ha; K 415.5 (251.6) kg/ha; OC 0.556 (0.431) %.
- Limits used: 20 < N ≤ 1500; 1 < P ≤ 300; 20 < K ≤ 3000; 0 < OC ≤ 5; 3.5 ≤ pH ≤ 10.5; 0 < EC ≤ 10.

## 3. Elevation/climate provenance (resolved, no new extraction needed)
All 1,334 samples with source distance > 1 km belonged to the removed placeholder clusters. In the final data the
elevation/climate source location is at most 100 m away (median 0 m, 95 % 22 m): values describe the sample's own site.
Sources: Copernicus DEM GLO-30 (elevation), TerraClimate (6 climate variables), via Microsoft Planetary Computer.

## 4. Design corrections (methodology changes, applied in all final results)
1. **Random 70/30 split grouped by 30 m site** (`GroupShuffleSplit`): co-located samples never fall on both sides.
   The ungrouped split is kept only as a reference row.
2. **Spatial blocks assigned by site centroid** (square blocks, `GroupKFold(5, shuffle=True)`): no site straddles two
   folds. Blocks statewide: 1,504 (10 km), 458 (25 km), 147 (50 km), 44 (100 km).
3. **LRS features:** 10 nearest **training** samples from **other sites** (own site, incl. the sample, excluded).
4. Unchanged: 39 inputs, LightGBM settings fixed a priori (400 trees, learning rate 0.05, 15 leaves, …), log(1 + y)
   target standardised on training data, predictions clipped to the training range.

## 5. Final results

**Table 1 — Headline, statewide LightGBM, 39 inputs + LRS, mean ± SD of 5 seeds** (`F01_headline_summary.csv`)

| Design | R² N | R² P | R² K | R² OC | RMSE N / P / K / OC | MAE N / P / K / OC |
|---|---|---|---|---|---|---|
| **Random 70/30, grouped by site (primary)** | **0.692 ± 0.009** | **0.620 ± 0.012** | **0.532 ± 0.013** | **0.696 ± 0.012** | 58.5 / 16.1 / 170 / 0.238 | 36.9 / 7.01 / 106 / 0.139 |
| Random 70/30, ungrouped (reference) | 0.702 ± 0.009 | 0.606 ± 0.028 | 0.546 ± 0.011 | 0.701 ± 0.004 | 56.6 / 16.3 / 168 / 0.234 | 36.2 / 6.96 / 104 / 0.137 |
| **Spatial 10 km blocks** | **0.352 ± 0.033** | **0.389 ± 0.005** | **0.324 ± 0.016** | **0.587 ± 0.002** | 84.3 / 20.4 / 207 / 0.277 | 49.1 / 9.27 / 131 / 0.163 |

Units: kg/ha (N, P, K), % (OC).

**Table 2 — R² against validation design, statewide (seed 42)** (`F02_block_size_statewide_regions.csv`)

| Design | N | P | K | OC |
|---|---|---|---|---|
| Random 70/30, grouped by site | 0.701 | 0.606 | 0.532 | 0.694 |
| Spatial 10 km | 0.348 | 0.386 | 0.315 | 0.589 |
| Spatial 25 km | 0.319 | 0.318 | 0.239 | 0.519 |
| Spatial 50 km | 0.237 | 0.309 | 0.198 | 0.505 |
| Spatial 100 km | 0.211 | 0.287 | 0.183 | 0.330 |

Mean of 5 regional models: random (grouped) 0.660 / 0.529 / 0.403 / 0.424; 10 km 0.395 / 0.343 / 0.244 / 0.316;
50 km 0.237 / 0.233 / 0.108 / 0.235; 100 km 0.198 / 0.209 / 0.040 / 0.184. Per region: N at 50 km Marathwada 0.463,
Western MH 0.397, North MH 0.153, Vidarbha 0.141, Konkan 0.033; K in Western MH ≤ 0 under every spatial design.

**Table 3 — Distance from each test sample to its nearest training sample (seed 42)** (`F03_train_test_distances.csv`)

| Design | 5 % | median | 95 % | ≤ 30 m | ≤ 100 m | ≤ 1 km | ≤ 5 km |
|---|---|---|---|---|---|---|---|
| Random 70/30, ungrouped (reference) | 2 m | 55 m | 2.0 km | 40.1 % | 59.8 % | 90.3 % | 98.5 % |
| Random 70/30, grouped by site | 36 m | 174 m | 2.6 km | 0.0 % | 35.3 % | 86.7 % | 97.9 % |
| Spatial 10 km | 0.54 km | 4.9 km | 11.9 km | 0.0 % | 0.3 % | 10.5 % | 51.1 % |
| Spatial 25 km | 1.1 km | 8.9 km | 20.3 km | 0.0 % | 0.2 % | 4.4 % | 22.6 % |
| Spatial 50 km | 2.5 km | 13.5 km | 29.7 km | 0.0 % | 0.0 % | 1.7 % | 11.5 % |
| Spatial 100 km | 4.3 km | 21.2 km | 47.8 km | 0.0 % | 0.0 % | 1.0 % | 6.6 % |

Blocks do not impose a minimum distance (e.g. 10.5 % of test samples within 1 km of training under 10 km blocks); the
manuscript must describe designs by these measured distances, not by block size alone.

**Table 4 — Five models, R² random (grouped) → spatial 10 km (seed 42)** (`F04_five_models.csv`)

| Model | N | P | K | OC |
|---|---|---|---|---|
| Ridge regression | 0.694 → 0.338 | 0.605 → 0.359 | 0.523 → 0.294 | 0.696 → 0.582 |
| k-nearest neighbours | 0.619 → 0.265 | 0.528 → 0.348 | 0.449 → 0.274 | 0.666 → 0.567 |
| Multilayer perceptron | 0.683 → 0.333 | 0.615 → 0.348 | 0.524 → 0.282 | 0.690 → 0.580 |
| Random forest | 0.708 → 0.376 | 0.616 → 0.394 | 0.535 → 0.322 | 0.701 → 0.600 |
| LightGBM (base) | 0.701 → 0.348 | 0.606 → 0.386 | 0.532 → 0.315 | 0.694 → 0.589 |

Drop per model: N 0.33–0.36; P 0.18–0.27; K 0.18–0.24; OC 0.10–0.11.

**Table 5 — Input ablation, R² random (grouped) / spatial 10 km (seed 42)** (`F05_input_ablation.csv`)

| Inputs | N | P | K | OC |
|---|---|---|---|---|
| All (39 + LRS) | 0.701 / 0.348 | 0.606 / 0.386 | 0.532 / 0.315 | 0.694 / 0.589 |
| Without Sentinel-2 | 0.706 / 0.349 | 0.608 / 0.380 | 0.533 / 0.316 | 0.694 / 0.584 |
| Without LRS | 0.602 / 0.278 | 0.471 / 0.360 | 0.461 / 0.300 | 0.680 / 0.578 |
| LRS only | 0.686 / 0.276 | 0.567 / 0.357 | 0.506 / 0.274 | 0.677 / 0.547 |
| Sentinel-2 + pH, EC only | 0.115 / 0.032 | 0.071 / 0.024 | 0.096 / 0.037 | 0.307 / 0.206 |

SHAP shares (`F06_shap_groups.csv`, random grouped): LRS 59–65 %, climate 9–14 %, coordinates 6–10 %,
Sentinel-2 bands + indices 13–15 %, pH/EC 2–4 %, elevation 1–2 %; same ranking under spatial 10 km.

**Table 6 — Old versus final, R²** (`F07_old_vs_final.csv`)

| Version | Data | Design | N | P | K | OC |
|---|---|---|---|---|---|---|
| Old (E56, 5 seeds) | 32,096 | random 70/30 ungrouped | 0.705 | 0.620 | 0.573 | 0.702 |
| Old (E56, 5 seeds) | 32,096 | spatial 10 km | 0.390 | 0.393 | 0.343 | 0.562 |
| Final (F01, 5 seeds) | 24,599 | random 70/30 ungrouped (reference) | 0.702 | 0.606 | 0.546 | 0.701 |
| **Final (F01, 5 seeds)** | 24,599 | **random 70/30 grouped by site** | **0.692** | **0.620** | **0.532** | **0.696** |
| **Final (F01, 5 seeds)** | 24,599 | **spatial 10 km** | **0.352** | **0.389** | **0.324** | **0.587** |
| Old (E50) / Final (F02), seed 42 | | spatial 50 km | 0.231 / 0.237 | 0.335 / 0.309 | 0.211 / 0.198 | 0.476 / 0.505 |
| Old (E50) / Final (F02), seed 42 | | spatial 100 km | 0.224 / 0.211 | 0.290 / 0.287 | 0.166 / 0.183 | 0.326 / 0.330 |

Effect of the corrections: headline random R² changes by −0.01 to −0.04; spatial 10 km N falls 0.39 → 0.35, OC rises
0.56 → 0.59; all conclusions (large random-vs-spatial gap for every model, Sentinel-2 adds no accuracy, regional
differences) are unchanged.

Figures (300 dpi): `Fig1_study_area_map.png` (24,599 samples), `Fig3_measured_vs_predicted.png` (seed 42, random
grouped and spatial 10 km), `Fig4_r2_vs_block_size.png`. Workflow diagram (Fig. 2) still to be drawn.

## 6. Novelty (status unchanged from A01)
- Verified citations: Gupta & Patil 2026 (J Indian Soc Remote Sens 54:2405–2421); Kumar et al. 2026 (Environ Chall
  22:101375); Moharana et al. 2023 (Arab J Geosci 16:560); Garg et al. 2026 (Discover Soil 3:95); Ploton 2020;
  Roberts 2017; Meyer 2019; Wadoux 2021; Valavi 2019 (details in A01).
- **Do not claim "first"** to show the random-vs-spatial gap: Kumar et al. (2026) reportedly compare random and spatial
  CV for available N in India (from a search summary; full text not read).
- Defensible contribution: state-scale SHC data with Sentinel-2 matched within ±3 days and a strict bare-soil mask;
  decline quantified over four block sizes with measured train–test distances, statewide and per region, for N, P, K
  and OC; same decline for five algorithms; ablation showing Sentinel-2 adds no accuracy beyond location-based inputs.

## 7. Remaining limitations (to state in the manuscript)
One season of one year (Jan–May 2024), one state; single-date Sentinel-2; pH and EC are laboratory values; seed 42 only
for Tables 2, 4, 5 and SHAP (5 seeds for the headline); few blocks per region at 50–100 km (single regional values
±0.05); hyperparameters fixed a priori from an earlier experiment (E36), not tuned; spatial blocks have no buffer
(distances reported in Table 3); placeholder-GPS samples and Raigad excluded (rules stated above).

## 8. Blockers and items needing the editor's decision
| Item | Status | Blocks submission? |
|---|---|---|
| Full texts of Gupta & Patil (2026) and Kumar et al. (2026) | Not accessible to me; Paresh to obtain through the college library | Blocks any "first" claim only; manuscript can proceed with the contribution stated in §6 |
| Methodology changes in §4 | Executed; need the editor's acceptance | Yes (editor decision) |
| SLUSI reuse terms | No explicit terms found; CC0 republication documented | No |
| Workflow figure | Not drawn | Needed for the manuscript, not a scientific blocker |
| Optional buffered spatial CV | Not run (optional) | No |

## 9. Files
- Script: `Start/final/reproduce_final.py` (standalone; needs only the parquet files in `Start/`).
- Results: `Start/results_final/` — `F00_dataset_counts.csv`, `F00_final_dataset_ids.parquet`, `F01_headline_5seeds.csv`,
  `F01_headline_summary.csv`, `F02_block_size_statewide_regions.csv`, `F03_train_test_distances.csv`,
  `F04_five_models.csv`, `F05_input_ablation.csv`, `F06_shap_groups.csv`, `F07_old_vs_final.csv`, three figures,
  `run_log.txt`.
- Audit: `Start/audit/A01_audit_report.md`, `A01_provenance_leakage_audit.py`, `A01_output.txt`.
