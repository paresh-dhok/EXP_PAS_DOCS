# Audit A01 — provenance, validation/leakage and novelty of the final experiments (E49–E56)

Date: 2026-10-15. Prepared for the handling editor. No manuscript text was written and no result file was changed.
Evidence: `Start/new.ipynb` (cells 66–85), `Start/audit/A01_provenance_leakage_audit.py` (read-only script, executed
2026-10-15, run time < 1 min) and its full output `Start/audit/A01_output.txt`.

---

## Issue 1 — Dataset provenance

**Inspected.** Notebook cells that produced E49–E56: cell 67 (setup, exec 3), 66 (data load, exec 4), 69 (block grids),
70 (LRS features), 71 (task43), 72 (models), 73 (`lgbm` helper), 77 (E49), 78 (E50), 79 (E51), 80 (E52), 81 (E53),
84 (Fig.), 85 (E56) — one kernel session, execution counts 3–22. Data files, `DATASETS.md`, D07/D08 documentation,
result CSVs 49–56. The A01 script rebuilds the data with the same code and re-fits the headline model.

**Verified.**
- E49–E56 use **`mh_model_dataset.parquet` (33,877 rows)** — output of D07: strictly bare 3×3 window (SCL = 5, all
  9 pixels), Sentinel-2 scene within ±3 days, impossible soil values removed, reflectance 0–1 — **minus Raigad
  (district code 491, 1,781 rows) = 32,096**. Region counts 7,236 / 9,293 / 9,738 / 4,329 / 1,500 (no missing region).
- **Reproduction:** the A01 script reproduces E49's random-split R² exactly (N 0.706, P 0.614, K 0.564, OC 0.701).
- Inputs: 12 single-date bands + 16 indices, pH, EC (all from `mh_model_dataset`); elevation + 6 climate variables are
  **copied from the nearest location in `mh_final_dataset` (17,620 rows)** via `mh_terrain.parquet` /
  `mh_climate.parquet`; longitude, latitude; 4 LRS features.
- **The three counts:** 33,877 → 32,096 = final data (Raigad removed). **17,620** = de-clustered locations (D08); in
  E49–E56 used **only as the source of elevation and climate**. **17,273** = `mh_composite.parquet` (multi-date
  composite, ids are a subset of the 17,620); **not used in E49–E56** (used in E01–E38 only).

**Problems found.**
1. **Borrowed elevation/climate:** distance from a sample to the location whose elevation/climate it received: median
   3 m, 95 % 793 m, 99 % 4.6 km, max 12.6 km; **1,335 samples > 1 km, 226 > 5 km**. For these, elevation in
   particular may be wrong.
2. **Placeholder-GPS samples are in the final data:** with the D08 rule (30 m connected clusters), **7,486 of 32,096
   samples (23.3 %) lie in clusters of > 10 samples** (largest 179) — the clusters D08 identified as many fields
   geotagged at one point and removed from the de-clustered set. Their coordinates, Sentinel-2 pixel and LRS
   features describe the placeholder point, not the field. (The team decided on 2026-10-14 not to discuss clustering
   in the paper; this audit reports it because it affects both provenance and validation.)
3. D08's tighter lower limits (OC > 0.02, EC > 0.005) are not applied in this data (OC min 0.006, EC min 0.001).
   Minor, but the methods text must state the limits actually used (0 < OC, 0 < EC).
4. **Reproducibility:** results depend on notebook kernel state (cells run out of order; helper `lgbm` defined in the
   E45 cell, which is excluded from the paper). There is no standalone script that regenerates E49–E56.

**Uncertain.** How the original all-India file (5,182,371 records, `SLUSI_Soil_Health_data…geojson`, dated
2026-08-31) was obtained (portal download/export or script) is not documented; needed for the data-availability
statement and for compliance with the SHC portal terms.

**Scientific risk.** Medium–high: undisclosed placeholder coordinates in a paper about spatial validation; input
errors for ~4 % of samples; results not reproducible from a script.

**Proposed corrections.**
- (a) Extract elevation and climate **at each of the 32,096 points** (or exclude samples with borrow distance
  > 1 km) and re-run E49–E56.
- (b) Decide on placeholder-GPS samples: exclude clusters > 10 (consistent with D08) and re-run, **or** keep them and
  disclose with the sensitivity result from Issue 2.
- (c) One standalone script (`reproduce_E49_E56.py`) that rebuilds the data and all final tables/figures.
- (d) Document how the raw SHC file was obtained.

**Before submission:** (a), (c), (d) yes; (b) a decision is required (exclusion or disclosure).

---

## Issue 2 — Validation and leakage

**Inspected (code).**
- Blocks: cell 66 `blocks()` / cell 69 `blocks_km()` — `floor(x / s), floor(y / s)` on approximate local metres
  (x = lon·111,320·cos(lat), y = lat·110,574), block ids assigned to 5 folds by
  `GroupKFold(n_splits=5, shuffle=True, random_state=seed)`. **No buffer between folds.**
- LRS: cell 70 `nb_features` / `fit_predict_nb`, cell 77 `fit_nb_both`: training rows query the 11 nearest training
  points and drop column 0 (assumed to be the row itself); test rows query the 10 nearest **training** points
  (`cKDTree(P[tr])`, labels `y[tr]`). Target log-transform mean/SD from training rows only; scalers inside sklearn
  pipelines (E51). Hyperparameters fixed a priori (taken from E36), not tuned on these test sets.

**Verified by executed tests (A01 output, sections 2a–2d).**

Distance from each test sample to its nearest training sample (32,096 samples, seed 42):

| Design | 5 % | median | 75 % | ≤ 30 m | ≤ 1 km | ≤ 5 km |
|---|---|---|---|---|---|---|
| Random 70/30 | 1 m | 24 m | 160 m | **53.7 %** | 93.1 % | 98.8 % |
| Spatial 10 km blocks | 565 m | 4.7 km | 7.2 km | 0.3 % | **10.3 %** | 53.7 % |
| Spatial 25 km blocks | 1.2 km | 9.0 km | 12.9 km | 0.2 % | 4.5 % | 23.7 % |
| Spatial 50 km blocks | 2.5 km | 14.2 km | 20.8 km | 0.0 % | 1.8 % | 11.6 % |
| Spatial 100 km blocks | 4.0 km | 22.2 km | 33.7 km | 0.2 % | 1.5 % | 7.1 % |

- **Nominal block size does not guarantee a minimum distance:** with 10 km blocks, 10.3 % of test samples have a
  training sample within 1 km (samples near block edges).
- Repeated/nearby samples: no fully identical records (0); 142 samples (0.4 %) share exact coordinates (groups ≤ 5);
  exact-coordinate groups are **never split across folds** (0 at every block size); only 0.0–0.2 % of ≤ 30 m pairs
  fall in different folds.
- **LRS uses only eligible training labels:** test-row features come from training rows only (by construction).
  Self-exclusion for training rows: in the seed-42 training set (22,467 rows) the row itself was returned first in
  every case (0 failures), its own label never entered its features (0), and an exact index-based self-exclusion gives
  identical R² (diagnostic row B).

Diagnostic sensitivity runs (seed 42, statewide LightGBM, 39 inputs + LRS; **diagnostics, not replacements**):

| Run | N | P | K | OC |
|---|---|---|---|---|
| A random 70/30, notebook LRS (= E49) | 0.706 | 0.614 | 0.564 | 0.701 |
| B random 70/30, index-based self-exclusion | 0.706 | 0.615 | 0.564 | 0.701 |
| C split by exact location (GroupShuffleSplit) | 0.694 | 0.633 | 0.557 | 0.685 |
| D split by 30 m cluster | 0.665 | 0.641 | 0.536 | 0.690 |
| E split by 30 m cluster, no LRS | 0.573 | 0.525 | 0.441 | 0.663 |

Keeping 30 m clusters together lowers the random-split R² for N by 0.04 and K by 0.03; P rises by 0.03 (different test
set); OC changes by −0.01.

**Uncertain.** Single seed for the diagnostics; distances measured to the single nearest training sample only; grid
origin is arbitrary (block boundaries could be shifted); 100 km blocks give only 45 statewide blocks.

**Scientific risk.** Medium. No label leakage was found in the LRS construction. The risks are in **wording and
interpretation**: "10 km blocks" must not be described as "test fields ≥ 10 km from training", and the random-split
headline includes many co-located training–test pairs (54 % within 30 m), which inflates N and K slightly.

**Proposed corrections / experiments.**
- (a) Report the measured train–test distance table above with every spatial result.
- (b) Report the cluster-grouped random split (row D) as sensitivity, or adopt it as the random baseline.
- (c) Optional: buffered block CV (drop training samples within e.g. 2 km of the test block) to give a true minimum
  distance; or nearest-neighbour-distance-matched CV.
- (d) Code hygiene: index-based self-exclusion (no change in results, row B).
- (e) State that hyperparameters were fixed before these experiments.

**Before submission:** (a), (e) yes; (b) strongly recommended; (c), (d) optional.

---

## Issue 3 — Novelty and closest work

**Inspected.** Crossref metadata (all DOIs below), the Springer article page of Gupta & Patil (abstract and data
availability statement, read 2026-10-14), Semantic Scholar records, web searches, and the local PDF of
Gunasekaran et al. (2025). Full texts of Gupta & Patil and Kumar et al. were **not** accessible.

**Verified citations (metadata via Crossref).**

| Study | Verified content | Relevance |
|---|---|---|
| Gupta C., Patil N. (2026) J Indian Soc Remote Sens 54:2405–2421, doi:10.1007/s12524-026-02443-9 | Abstract: Karnataka, 168,000 instances (KSHSID), Landsat-8/9 + SHC, "global geolocation and local neighborhood context", KNN/MLP/LightGBM; R² N 0.77, P 0.61, K 0.72, OC 0.71, EC 0.98. Data statement: raw data from the SHC portal; processed data on request | Closest work; **validation design and neighbourhood definition not stated in the abstract** |
| Kumar A. et al. (2026) Environmental Challenges 22:101375, doi:10.1016/j.envc.2025.101375 | Metadata verified. Content (random vs spatial CV for available N in sericultural soils of NE India; spatial R² 0.02–0.27; RF best) **from a search-engine summary only — not verified against the full text** | **Already shows that spatial CV lowers accuracy for available N in India** |
| Moharana P.C. et al. (2023) Arab J Geosci 16:560, doi:10.1007/s12517-023-11670-0 | Metadata verified; DSM of SHC parameters (Thar Desert) with quantile regression forest | Prior SHC-based mapping; validation design not checked |
| Garg A.K. et al. (2026) Discover Soil 3:95, doi:10.1007/s44378-026-00243-8 | Abstract verified: OC, EC, pH, N, P₂O₅, K₂O in the Krishna Delta with RF/kNN/ANN/Cubist; RF R² OC 0.43, K₂O 0.51; mentions spatial validation | Recent Indian DSM of the same nutrients |
| Balkrishna A. et al. (2026) Soil Advances 5:100124, doi:10.1016/j.soilad.2026.100124 | Metadata verified; systematic review of soil health research and the SHC framework | Context |
| Ploton P. et al. (2020) Nat Commun 11:4540, doi:10.1038/s41467-020-18321-y | Abstract verified: non-spatial validation suggests > 50 % explained, spatial validation near-null | Method foundation |
| Roberts D.R. et al. (2017) Ecography 40:913–929, doi:10.1111/ecog.02881 | Abstract verified: block CV for structured data | Method foundation |
| Meyer H. et al. (2019) Ecol Model 411:108815, doi:10.1016/j.ecolmodel.2019.108815 | Metadata verified | Spatial predictors / spatial prediction |
| Wadoux A.M.J.-C. et al. (2021) Ecol Model 457:109692, doi:10.1016/j.ecolmodel.2021.109692 | Metadata verified | Counter-view on spatial CV (must be cited) |
| Valavi R. et al. (2019) Methods Ecol Evol 10:225–232, doi:10.1111/2041-210X.13107 | Abstract verified: blockCV package | Implementation reference |

**Corrections to earlier team material.** Gunasekaran K. et al. (2025) Front. Soil Sci. 5:1652058 is a sensor-based
fertility *classification* study (1,980 samples, stratified 5-fold CV) — **not** an SHC/Sentinel-2 study; an earlier
claim of "Sentinel-2 N R² 0.79–0.92" from a search summary was wrong and must not be cited. "Mundada & Jain (2025)" in
`PROJECT_GUIDE.md` could not be located and is unverified.

**What our study adds (defensible from our results).** (i) State-scale SHC data (32,096 samples) with Sentinel-2
matched within ±3 days and a strict bare-soil mask; (ii) the decline of accuracy quantified across four block sizes,
statewide and per region, for N, P, K and OC together; (iii) the same decline for five algorithms (E51);
(iv) ablation showing that Sentinel-2 adds no accuracy once location-based inputs are present (E53);
(v) measured train–test distances for each design (this audit).

**Not new.** That spatial CV lowers accuracy (Ploton 2020; Roberts 2017; for available N in India, Kumar et al. 2026
if confirmed); combining location/neighbourhood context with SHC data and LightGBM (Gupta & Patil 2026).

**Uncertain.** No systematic database search (Scopus/Web of Science not accessible); full texts of the two closest
papers not read; Gupta & Patil's validation method unknown.

**Scientific risk.** High if the paper claims to be "the first" to show the random-vs-spatial gap; moderate otherwise.

**Proposed corrections.** Obtain the full texts of Gupta & Patil (2026) and Kumar et al. (2026) through the college
library; run and document a structured search (e.g. Scopus: ("soil health card" OR "SHC") AND ("machine learning" OR
"random forest") AND ("spatial cross-validation" OR "block")); restate the contribution as (i)–(v) above and drop
"first" unless the search supports it.

**Before submission:** yes (claim wording and the two full texts).

---

## Summary for the editor

| Issue | Must resolve before submission | Main action |
|---|---|---|
| 1 Provenance | Yes | Point-level elevation/climate; decision on 7,486 placeholder-GPS samples; standalone reproduction script; document raw-data source |
| 2 Validation/leakage | Wording yes; sensitivity recommended | Report distance table; cluster-grouped random split as sensitivity; no label leakage found in LRS |
| 3 Novelty | Yes | Read the two closest full texts; documented search; contribution restated without "first" |
