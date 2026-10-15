# W01 — Clarifications for manuscript writing (primary analysis: E49–E56, 32,096 samples)

Date: 2026-10-15. For the handling editor and the writing team. Decision received: the primary analysis is the
original E49–E56 dataset (32,096 samples); the clustered records are retained and are **not** described as invalid.
No result file was changed. The S01 files (`Start/final/S01_*`, `Start/results_final/`) are a separate sensitivity
analysis on a different dataset and must not be mixed into the manuscript's numbers.

---

## 1. Which number is which (authoritative files)

| Manuscript item | Values | Type | File |
|---|---|---|---|
| Headline table (R², RMSE) | random 70/30: 0.71 ± 0.01 / 0.62 ± 0.01 / 0.57 ± 0.01 / 0.70 ± 0.01; spatial 10 km: 0.39 ± 0.03 / 0.39 ± 0.01 / 0.34 ± 0.02 / 0.56 ± 0.02 (N / P / K / OC); RMSE random 54.0 / 15.2 / 163.5 / 0.21, spatial 76.8 / 19.3 / 201.8 / 0.26 | **Mean ± SD of 5 seeds** (42, 7, 13, 99, 2024) | `Start/results/56_headline_seeds.csv` |
| MAE, bias, RPIQ, train R² | see file | **Seed 42 only** | `Start/results/49_headline_metrics.csv` |
| Measured-vs-predicted figure | R² 0.71 / 0.61 / 0.56 / 0.70 (random), 0.39 / 0.40 / 0.35 / 0.58 (spatial 10 km) | **Seed 42 only** | `Start/results/49_measured_vs_predicted.png` |
| R² vs block size (table + figure), statewide and regional | see file | **Seed 42 only** | `Start/results/50_block_size_final.csv`, `55_r2_vs_block_size.png` |
| Five algorithms | see file | **Seed 42 only** | `Start/results/51_model_comparison_final.csv` |
| SHAP | see file | Seed 42 | `Start/results/52_shap_final.csv` |
| Input ablation | see file | Seed 42 | `Start/results/53_input_ablation.csv` |
| Train–test distances | §4 below | Seed 42, exact E49/E50 splits | `Start/results/57_train_test_distances_E49_E50.csv` (new, distances only) |

**Table vs figure:** the small differences (e.g. P 0.62 in the table vs 0.61 in the figure; spatial N RMSE 76.8 vs
76.7) are 5-seed means vs the seed-42 run. Label every caption: "mean ± SD of five repetitions" or "single run (seed
42)".
**Scale:** all R², RMSE and MAE are computed after back-transforming predictions from log(1 + y) to the original
units (kg/ha for N, P, K; % for OC) — notebook cells 66 and 77.

## 2. Corrected regional statement (supersedes the summary's sentence)

The sentence "N and P … fell below 0.16 in Vidarbha and North Maharashtra" is **incorrect** (North MH P at 50 km =
0.314). Values at 50 km blocks, regional models, seed 42 (`50_block_size_final.csv`):

| R² at 50 km | Marathwada | Western MH | North MH | Vidarbha | Konkan |
|---|---|---|---|---|---|
| N | 0.462 | 0.303 | 0.158 | 0.125 | 0.060 |
| P | 0.526 | 0.388 | 0.314 | 0.032 | 0.147 |

Suggested wording: *"With 50 km blocks, N and P retained R² of 0.30–0.53 in Marathwada and Western Maharashtra. N fell
to 0.16 or below in North Maharashtra, Vidarbha and Konkan, and P to 0.15 or below in Vidarbha and Konkan, while P in
North Maharashtra retained 0.31."*

## 3. Sentinel-2: stand-alone performance vs incremental contribution

- **Stand-alone:** the existing ablation has **no Sentinel-2-only model**. The closest set is **Sentinel-2 + pH + EC,
  without location inputs** (`53_input_ablation.csv`): R² random / spatial 10 km = N 0.168 / 0.036, P 0.121 / 0.033,
  K 0.161 / 0.049, OC 0.324 / 0.201.
- **Incremental:** removing all 28 Sentinel-2 inputs from the full model changes R² by −0.015 to +0.004
  (random: N 0.706 → 0.710, P 0.614 → 0.616, K 0.564 → 0.568, OC 0.701 → 0.703; spatial: N 0.393 → 0.390,
  P 0.396 → 0.381, K 0.352 → 0.357, OC 0.578 → 0.578).
- **Attribution:** SHAP share of Sentinel-2 bands + indices in the full model 11–12 % (random test data)
  (`52_shap_final.csv`). Attribution is not added accuracy.

Suggested wording: *"Without location inputs, Sentinel-2 reflectance and indices together with pH and EC explained
R² of 0.12–0.32 under the random split (highest for OC) and 0.03–0.20 under 10 km blocks. In the full model,
Sentinel-2 inputs received 11–12 % of the SHAP attribution, but removing them changed R² by less than 0.02."*
If the editor wants a true Sentinel-2-only figure, that requires one new small run (not done).

## 4. Measured train–test distances (exact E49/E50 splits, seed 42; new file 57, no model fitted)

| Design | 5 % | median | 95 % | ≤ 30 m | ≤ 1 km | ≤ 5 km |
|---|---|---|---|---|---|---|
| Random 70/30 | 1 m | 24 m | 1.4 km | 53.7 % | 93.1 % | 98.8 % |
| Spatial 10 km | 0.57 km | 4.7 km | 12.1 km | 0.3 % | 10.2 % | 53.7 % |
| Spatial 25 km | 1.1 km | 9.0 km | 20.7 km | 0.2 % | 4.7 % | 23.9 % |
| Spatial 50 km | 2.5 km | 14.2 km | 28.7 km | 0.0 % | 1.8 % | 11.6 % |
| Spatial 100 km | 4.0 km | 22.2 km | 47.6 km | 0.2 % | 1.5 % | 7.1 % |

Script: `Start/final/distances_E49_E50.py`. Use this table to describe geographic separation; blocks do not impose a
minimum distance, so do not write "test fields ≥ 10 km from training".

## 5. Facts to state neutrally in Methods (no claim of invalidity)

- **Location structure:** 23.3 % of samples (7,486) lie in groups of more than 10 samples within 30 m of each other;
  142 samples share exact coordinates; no record is fully duplicated (`Start/audit/A01_output.txt` §2a). All were
  retained. Under the random split 53.7 % of test samples have a training sample within 30 m (§4).
- **Elevation and climate:** extracted at 17,620 de-duplicated locations (D09, D11) and assigned to each sample from the
  nearest location: median 3 m, 95 % ≤ 793 m; 1,335 samples (4.2 %) > 1 km, maximum 12.6 km (A01 §1).
- **Raigad:** excluded because 50.8 % of its samples report N > 850 kg/ha (median 872 vs 301 in neighbouring
  Ratnagiri; 5.3 % of samples carrying 60.9 % of N variance) (E47, E48). A laboratory or district offset is a
  possible explanation, not verified.
- **Data source:** SLUSI Soil Health Card data, republished under CC0 1.0 in GitHub `ramSeraph/indian_land_features`
  (release `soil-health`, 2025-01-09; attribute Datameet and SLUSI), accessed via indianopenmaps.com.
- **Computing time:** in one run on one machine, Random Forest (100 trees) used 823 CPU s and LightGBM (400 trees) 47 CPU
  s over all jobs (`51_model_comparison_final.csv`, column `sec`); in the reproduction run 833 vs 55 CPU s. Quote as
  "15–18 times in two runs", or drop.

## 6. Confirmed issues the editor should decide on

1. **Random-split co-location (central to the paper's topic).** 53.7 % of random-split test samples have a training
   sample within 30 m. This does not invalidate the results, but the random-split R² must be interpreted as
   prediction at or next to sampled sites. Reporting the distance table (§4) addresses it. A site-grouped random split
   exists only in the separate S01 analysis (different dataset); whether to cite it as a sensitivity analysis is the
   editor's decision.
2. **Elevation/climate assignment** (§5) — disclose; affects 4.2 % of samples by > 1 km.
3. **Reproducibility.** E49–E56 were run interactively in `Start/new.ipynb` (cells 66–85, out of order, one helper
   defined in an excluded cell). A01's script reproduced E49's seed-42 random R² exactly, but there is no standalone
   script for all of E49–E56. For a code-availability statement, a script reproducing E49–E56 can be written (it would
   re-fit the same models, ~5–10 min); not done without your approval.
4. **Novelty.** No "first" claim. Kumar et al. (2026, Environ Chall 22:101375) reportedly compare random and spatial CV
   for available N in India (full text unread); Gupta & Patil (2026) validation unknown (abstract only). The earlier
   "Frontiers 2025 Sentinel-2 R² 0.79–0.92" citation is wrong; "Mundada & Jain 2025" is unverified.
