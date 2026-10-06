# Experiment Documentation — Soil N, P, K, OC from Sentinel-2 (Maharashtra)

Capstone: *Development of an Autonomous Multimodular Precision Agriculture System* — soil soft-sensing component.
Working folder: `D:\SEM 7\CAPSTONE\DATA\slusi\Start`
Main notebook: `Start\new.ipynb` (cell numbers below are 0-based positions in that notebook).

Every step is documented in its own file. **D-files** describe how the dataset was built.
**E-files** describe modelling experiments. Each file records the objective or hypothesis, the exact setup,
the results, the interpretation, and the decision taken.

## Index

### Dataset construction (D)

| ID | File | Date | Summary |
|---|---|---|---|
| D00 | [D00_background_previous_attempt.md](D00_background_previous_attempt.md) | before 2026-09-28 | Earlier 5,000-point pilot; extraction took 8.4 min/scene, so the approach was abandoned |
| D01 | [D01_maharashtra_filter.md](D01_maharashtra_filter.md) | 2026-09-28 | 5,182,371 → 355,562 Maharashtra records |
| D02 | [D02_gps_decoding_repeated_points.md](D02_gps_decoding_repeated_points.md) | 2026-09-28 | WKB → lon/lat; 246,285 unique GPS points; repeated points excluded |
| D03 | [D03_pilot_1000_scene_search.md](D03_pilot_1000_scene_search.md) | 2026-09-28 | 1,000-sample pilot; tile-based STAC search; region and season decision |
| D04 | [D04_extraction_method_3x3_window.md](D04_extraction_method_3x3_window.md) | 2026-09-28 | Data-API point vs rasterio; exact 3×3 window verified 20/20 |
| D05 | [D05_full_candidates_matching.md](D05_full_candidates_matching.md) | 2026-09-28 | 91,818 candidates → 151,831 sample–scene pairs |
| D06 | [D06_full_extraction_rounds.md](D06_full_extraction_rounds.md) | 2026-09-28 | 61,617 pairs extracted; 40,988 usable samples |
| D07 | [D07_soil_value_cleaning_reflectance.md](D07_soil_value_cleaning_reflectance.md) | 2026-09-30 | Strictly bare 36,005 → 33,877 after impossible values; reflectance and indices |
| D08 | [D08_gps_clusters_declustering.md](D08_gps_clusters_declustering.md) | 2026-09-30 | Placeholder-GPS clusters found; 33,842 samples → 17,620 independent locations |
| D09 | [D09_terrain_features.md](D09_terrain_features.md) | 2026-09-30 | 7 terrain features from the Copernicus 30 m DEM |
| D10 | [D10_multidate_bare_soil_composite.md](D10_multidate_bare_soil_composite.md) | 2026-09-30 → 10-01 | 211,440 extra requests; 12-date bare-soil composite for 17,273 locations |
| D11 | [D11_climate_features.md](D11_climate_features.md) | 2026-10-05 | 10-year TerraClimate averages: rainfall, monsoon rainfall, temperatures, water deficit |

### Modelling experiments (E)

| ID | File | Date | Results file | Uses location? |
|---|---|---|---|---|
| E01 | [E01_rf_feature_sets.md](E01_rf_feature_sets.md) | 2026-09-30 | `results/01_rf_baseline_feature_sets.csv` | Sets A/B/C no; set D yes |
| E02 | [E02_gps_ablation_10km_50km.md](E02_gps_ablation_10km_50km.md) | 2026-09-30 | `results/02_rf_gps_ablation.csv` | Yes |
| E03 | [E03_district_baseline_feature_dilution.md](E03_district_baseline_feature_dilution.md) | 2026-09-30 | `results/03_diagnostics_district_dilution.csv` | Yes |
| E04 | [E04_two_stage_district_residual.md](E04_two_stage_district_residual.md) | 2026-09-30 | `results/04_two_stage_district_residual.csv` | Yes (district stage) |
| E05 | [E05_two_stage_terrain.md](E05_two_stage_terrain.md) | 2026-09-30 | `results/05_two_stage_terrain.csv` | Yes (district stage) |
| E06 | [E06_two_stage_composite.md](E06_two_stage_composite.md) | 2026-10-01 | `results/07_two_stage_composite.csv` | Yes (district stage) |
| E07 | [E07_noise_ceiling.md](E07_noise_ceiling.md) | 2026-10-01 | `results/06_noise_ceiling.csv` | — (no model) |
| E08 | [E08_random_7030_vs_spatial_cv.md](E08_random_7030_vs_spatial_cv.md) | 2026-10-01 | `results/08_split_7030_vs_spatial.csv` | Sets C/CCT no; CCTG/C+GPS yes |
| E09 | [E09_region_transfer_and_region_models.md](E09_region_transfer_and_region_models.md) | 2026-10-05 | `results/09_region_transfer.csv`, `results/09_region_models.csv` | No (region used only to split / select the model) |
| E10 | [E10_region_models_7030_vs_spatial.md](E10_region_models_7030_vs_spatial.md) | 2026-10-05 | `results/10_region_models_7030_vs_spatial.csv` | No (region used only to split) |
| E11 | [E11_headline_checks.md](E11_headline_checks.md) | 2026-10-05 | `results/11_headline_checks.csv` | No (elevation acts partly as location; see the file) |
| E12 | [E12_svr_knn_and_class_prediction.md](E12_svr_knn_and_class_prediction.md) | 2026-10-05 | `results/12_svr_knn_regression.csv`, `results/12_class_prediction.csv` | No (final 41 inputs) |
| E13 | [E13_extratrees_cubist_decisiontree.md](E13_extratrees_cubist_decisiontree.md) | 2026-10-05 | `results/13_et_cubist_tree.csv` | No (final 41 inputs) |
| E14 | [E14_region_rf_elevation_and_split.md](E14_region_rf_elevation_and_split.md) | 2026-10-05 | `results/14_region_rf_elevation_split.csv` | Region-wise; one set includes `elev` |
| E15 | [E15_region_rf_climate_elevation.md](E15_region_rf_climate_elevation.md) | 2026-10-05 | `results/15_region_rf_climate_elevation.csv` | Region-wise; sets include `elev` and/or climate |
| E16 | [E16_climate_vs_location_check.md](E16_climate_vs_location_check.md) | 2026-10-05 | `results/16_climate_vs_location_check.csv` | Diagnostic: lon/lat used only to test climate |
| E17 | [E17_split_ratio_cluster_comparison.md](E17_split_ratio_cluster_comparison.md) | 2026-10-05 | `results/17_split_comparison_region.csv` | Region-wise; one set includes `elev` + climate |
| E18 | [E18_region_algorithm_comparison.md](E18_region_algorithm_comparison.md) | 2026-10-05 | `results/18_region_algorithm_comparison.csv` | Region-wise; 41 inputs and 41 + `elev` + climate |
| E19 | [E19_semivariogram.md](E19_semivariogram.md) | 2026-10-05 | `results/19_semivariogram.csv`, `results/19_semivariogram.png` | — (no model; distances only) |
| E20 | [E20_ibm_replication.md](E20_ibm_replication.md) | 2026-10-05 | `results/20_ibm_replication.csv` | Yes (elevation + climate, to mirror the IBM study) |
Note: the results-file numbers 06 and 07 are swapped relative to the experiment IDs. The noise-ceiling cell was
written first (06) but run after the composite test (07). Experiment IDs follow the order in which they were run.

## Final data files (do not modify)

| File | Rows | Content |
|---|---|---|
| `maharashtra_raw.parquet` | 355,562 | All Maharashtra records, 46 original columns, unchanged |
| `mh_candidates.parquet` | 91,818 | Eligible Jan–Jun samples + lon, lat, sample_date, region, mgrs_tile |
| `mh_scenes.parquet` | 2,666 | Sentinel-2 scenes (all cloud levels) found for the candidates |
| `mh_pairs.parquet` | 151,831 | Sample–scene pairs (±3 days, point inside scene footprint) |
| `mh_s2_3x3.parquet` | 61,617 | Raw 3×3 window statistics (DN) for every extracted pair |
| `mh_model_dataset.parquet` | 33,877 | Strictly bare, cleaned samples before de-clustering |
| **`mh_final_dataset.parquet`** | **17,620** | **Final independent locations: soil values + single-date S2 + indices** |
| **`mh_terrain.parquet`** | **17,620** | **7 terrain features per location** |
| **`mh_composite.parquet`** | **17,273** | **Multi-date (Mar–May 2024) bare-soil composite features** |
| `composite_parts/*.parquet` | 211,440 | Raw per-date window statistics behind the composite |

## Fixed evaluation protocol (for all comparable experiments)

- **Validation:** 5-fold **spatial block** cross-validation. The blocks are a 10 km × 10 km grid
  (`GroupKFold(n_splits=5, shuffle=True, random_state=42)`). Anything learned from data (e.g. district means)
  is computed **from the training folds only**.
- **Targets:** N, P, K (kg/ha) and OC (%), modelled as `log1p(y)`. Predictions are back-transformed with `expm1`
  and metrics are computed on the original scale.
- **Metrics:** R² over all out-of-fold predictions (main), fold mean ± std R², RMSE, MAE, RPIQ = IQR / RMSE.
- **Seed:** 42 so far. Planned stability check with seeds [42, 7, 13, 99, 2024].
- **Rule adopted on 2026-10-01: no location inputs** (no longitude/latitude, no district averages) in models
  intended as the final field-level predictor. Location is used **only** to build the spatial CV blocks.
  E02–E06 used location and are kept as **diagnostic** experiments.

## Caveats that apply to all experiments

- pH and EC are **laboratory** values from the Soil Health Card. They stand in for a field sensor, so results
  that use them are a best case for a real low-cost sensor.
- Soil targets are SHC laboratory results: available N (alkaline KMnO₄), available P, available K, OC (%).
  These are not total N or SOC stocks.
- All usable imagery and samples are from 2024 (3 candidates from 2023, none in the final set).
