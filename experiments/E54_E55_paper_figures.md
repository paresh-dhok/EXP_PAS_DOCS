# E54–E55 — Paper figures: study-area map and R² against block size

**Date:** 2026-10-14
**Notebook:** cells run on 2026-10-14 (after E53)

## E54 — Study-area map (Figure 1)
- **Files:** `results/54_study_area_map.png`, `results/54_sample_points.csv` (id, longitude, latitude, region; for QGIS)
- 32,096 samples (Raigad excluded) coloured by region (Vidarbha 7,236; Marathwada 9,293; North MH 9,738;
  Western MH 4,329; Konkan 1,500), region names on the map, 100 km scale bar, north arrow.
- Palette checked with the dataviz validator (colour-blind separation passes; light colours need the on-map labels,
  which are present). Konkan and Western MH labels placed by hand to avoid overlap.
- Missing for a typical journal map: state/district boundaries and an India inset. Can be added in QGIS from the CSV.

## E55 — R² against validation design (Figure 4)
- **File:** `results/55_r2_vs_block_size.png` (from `results/50_block_size_final.csv`)
- Two panels: statewide model; mean of the 5 regional models. One line per nutrient over random 70/30 and spatial
  blocks of 10, 25, 50, 100 km. Legend plus end-of-line labels (N and OC end at almost the same value in the regional
  panel; their labels are nudged apart).

## Planned figure list for the paper
1. Study-area map (E54)
2. Workflow diagram (to be drawn: SHC data → Sentinel-2 matching → inputs → LightGBM → validation designs)
3. Measured vs predicted, random 70/30 and spatial 10 km (E49, `results/49_measured_vs_predicted.png`)
4. R² against block size (E55)
