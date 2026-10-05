# Region-wise experiment protocol (FINAL — use this for every experiment)

Decided 2026-10-05. This replaces the statewide setup in README.md section 4.

## 1. The rule
**Every model is trained and tested inside ONE region.** We never train one model for the whole of Maharashtra.
For each of the 5 regions, a separate model is trained on that region's fields and tested on other fields of the
**same** region.

## 2. Why
- Maharashtra's regions have different soils. Konkan has acidic laterite (median N 395, OC 1.20 %, pH 6.4). The other four
  regions are mostly Deccan black soil (median N ~180, OC ~0.4 %, pH ~7.7).
- Experiment E09: a model trained in one region fails in another (negative R² in 19 of 20 cases), and a region-specific
  model beat the statewide model in **all 20** region × nutrient cases.
- Inside regions the input–nutrient relationships are much stronger (up to Spearman 0.55 for K in Vidarbha) than statewide
  (best 0.09–0.27), because each region has its own relationships that cancel out statewide.

## 3. The five regions
The region of each location comes from `02_datasets/mh_candidates.parquet`, column `region`. It is used **only to split
the data**, never as a model input.

| Region | Districts (codes) | Locations in model table | 10 km blocks |
|---|---|---|---|
| Vidarbha | 467 468 471 472 473 475 476 484 498 499 500 | 3,561 | 419 |
| Marathwada | 469 470 477 479 481 485 488 489 | 3,838 | 362 |
| North MH | 466 474 478 486 487 | 5,373 | 369 |
| Western MH | 480 490 493 494 496 | 2,729 | 245 |
| Konkan | 491 492 495 497 665 | 1,772 | 172 |

## 4. Inputs and outputs (fixed)
**41 inputs:**
- Sensor (2): `pH`, `EC`
- Satellite composite (33): `c_B01 … c_B12` (12 bands), 16 indices (`c_NDVI`, `c_SAVI`, `c_NBR2`, `c_NDMI`, `c_NDWI`,
  `c_BSI`, `c_NDRE`, `c_CI`, `c_BI`, `c_RI`, `c_R_B4B2`, `c_R_B11B12`, `c_R_B12B8`, `c_R_B11B8`, `c_R_B7B5`, `c_R_B6B5`),
  5 variability features (`c_std_NDVI`, `c_std_BSI`, `c_std_NDMI`, `c_std_B11`, `c_std_B12`)
- Terrain (6): `slope`, `tpi_150m`, `tpi_500m`, `tpi_1km`, `rough_90m`, `relpos_2km`

**Never use as inputs:** `elev`, `longitude`, `latitude`, district, `region`, single-date bands (`B01`… without `c_`),
`AOT`, `WVP`.

**Outputs:** `N`, `P`, `K` (kg/ha) and `OC` (%), one model per nutrient per region (5 regions × 4 nutrients = 20 models
per algorithm). Regression targets are trained as `log1p(y)` and predictions converted back with `expm1`.

## 5. Testing inside a region (spatial cross-validation)
- Locations are grouped into 10 km × 10 km squares (blocks). The blocks are computed **once for the whole state** and
  then subset to the region (exact code below), so everyone gets identical folds.
- Inside each region: `GroupKFold(n_splits=5, shuffle=True, random_state=42)` on the region's blocks. Each fold's test
  locations are in squares the model never saw.
- **Never use a random train/test split.** It inflates R² by about +0.1 to +0.2 inside regions (experiment E10).
- Fit any scaler, feature selection or tuning **on the training folds only**. If you tune hyperparameters, use an inner
  split of the training blocks, never the test fold.

## 6. Exact code (copy this)

```python
import numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

D = "TEAM_SHARE/"          # adjust to your path
data = (pd.read_parquet(D + "02_datasets/mh_final_dataset.parquet")
          .merge(pd.read_parquet(D + "03_satellite_and_terrain/mh_terrain.parquet"), on="id")
          .merge(pd.read_parquet(D + "03_satellite_and_terrain/mh_composite.parquet"), on="id")
          .reset_index(drop=True))
data = data.merge(pd.read_parquet(D + "02_datasets/mh_candidates.parquet", columns=["id", "region"]),
                  on="id", how="left")                                   # 17,273 rows

BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI",
           "R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
FEATS = ([f"c_{b}" for b in BANDS] + [f"c_{i}" for i in INDICES]
         + [f"c_std_{v}" for v in ["NDVI","BSI","NDMI","B11","B12"]]
         + ["pH", "EC"] + ["slope","tpi_150m","tpi_500m","tpi_1km","rough_90m","relpos_2km"])
assert len(FEATS) == 41
TARGETS = ["N", "P", "K", "OC"]
REGIONS = ["Vidarbha", "Marathwada", "North MH", "Western MH", "Konkan"]

# 10 km blocks, computed once for the whole state
lat_r = np.deg2rad(data["latitude"].to_numpy())
x = data["longitude"].to_numpy() * 111320 * np.cos(lat_r)
y = data["latitude"].to_numpy() * 110574
groups = pd.Series([f"{a}_{b}" for a, b in zip((x // 10000).astype(int), (y // 10000).astype(int))]).factorize()[0]
cv = GroupKFold(n_splits=5, shuffle=True, random_state=42)

def evaluate_region_wise(make_model, model_name):
    """make_model() must return a fresh, unfitted model that takes X (41 columns) and the raw target y
    (wrap with TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1) for the log target)."""
    rows = []
    for r in REGIONS:
        idx = np.where(data["region"] == r)[0]
        sub, g = data.iloc[idx], groups[idx]
        X = sub[FEATS]
        for t in TARGETS:
            y_t = sub[t]
            oof = np.zeros(len(sub))
            for a, b in cv.split(X, y_t, g):
                oof[b] = make_model().fit(X.iloc[a], y_t.iloc[a]).predict(X.iloc[b])
            rmse = mean_squared_error(y_t, oof) ** 0.5
            rows.append({"model": model_name, "region": r, "target": t, "n": len(sub),
                         "R2": r2_score(y_t, oof), "RMSE": rmse, "MAE": mean_absolute_error(y_t, oof),
                         "RPIQ": (y_t.quantile(0.75) - y_t.quantile(0.25)) / rmse})
            print(f"{model_name} | {r:<11} {t:<3} R2={rows[-1]['R2']:.3f}")
    return pd.DataFrame(rows)

# Example:
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.compose import TransformedTargetRegressor
# make_rf = lambda: TransformedTargetRegressor(
#     regressor=RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, n_jobs=-1, random_state=42),
#     func=np.log1p, inverse_func=np.expm1)
# res = evaluate_region_wise(make_rf, "RandomForest")
# res.to_csv("results_<yourname>_RandomForest.csv", index=False)
```

## 7. Check your setup first (reference result)
Run the Random Forest example above. You must get these R² values (computed 2026-10-05):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.150 | 0.025 | 0.239 | 0.060 |
| Marathwada | 0.134 | 0.211 | 0.014 | 0.020 |
| North MH | 0.042 | 0.046 | 0.009 | 0.112 |
| Western MH | 0.216 | 0.230 | −0.030 | 0.177 |
| Konkan | 0.141 | 0.022 | −0.022 | 0.089 |

If your numbers differ, your data, inputs or folds are not the same as ours. Fix that before running anything else.

## 8. What to report for every model
- One row per region × nutrient: `model, region, target, n, R2, RMSE, MAE, RPIQ` (the function above does this).
- Save as CSV: `results_<yourname>_<model>.csv`. Do not overwrite anyone else's files.
- For class prediction (low / medium / high), use the official Soil Health Card limits:
  N 280 / 560 kg/ha, P 10 / 25 kg/ha, K 110 / 280 kg/ha, OC 0.5 / 0.75 %
  (below the lower limit = low, between the limits inclusive = medium, above = high).
  Report accuracy, **balanced accuracy** (chance = 0.333) and macro F1 per region, plus the majority-class baseline.
  Plain accuracy is misleading because the classes are imbalanced.
- Use seed 42. If time allows, repeat with seeds 7, 13, 99, 2024 and report mean ± std.

## 9. Documenting an experiment
Before running, write down the hypothesis (what you expect and why). After running, record the setup (model + exact
settings), the results table, the interpretation, and failures as well as successes. Use the same format as the files in
`05_experiments/`.

## 10. Notes for an AI assistant helping with this work
- Follow sections 1–8 exactly; do not change the data files, the 41 inputs, the regions, the folds or the metrics.
- Do not add location inputs (longitude, latitude, elevation, district, region) to any model.
- Do not use random train/test splits or report training-set scores as results.
- Reproduce the reference table in section 7 before running new models.
- Save results in the format of section 8 and document each experiment as in section 9.
