# Soil N, P, K, OC prediction from Sentinel-2 — Team Share Package

Capstone: *Development of an Autonomous Multimodular Precision Agriculture System* (soil soft-sensing part).
Package prepared on 2026-10-02. Everything in this folder was produced between 2026-09-28 and 2026-10-01.

**Goal:** predict soil Nitrogen (N), Phosphorus (P), Potassium (K) and Organic Carbon (OC) for a farmer's field
from Sentinel-2 satellite data plus pH and EC (the values a field sensor would measure), using Soil Health Card (SHC)
laboratory results from Maharashtra as ground truth.

**Planned output:** a research paper = data findings (done) + comparison of algorithms + a novel model.

**⚠ FINAL EXPERIMENT SETUP: [REGION_WISE_PROTOCOL.md](REGION_WISE_PROTOCOL.md).** All models are trained and tested
inside one region at a time. It replaces the statewide setup described in section 4 below.

**New to the project? Read [PROJECT_GUIDE.md](PROJECT_GUIDE.md) first.** It explains everything from the basics
(soil, satellite, composite, how we test models) up to the current results. This README is the short reference.

---

## 0. Key terms in plain words

**Soil data**
- **Soil Health Card (SHC):** a government programme in which a soil sample is taken from a farmer's field before sowing
  and tested in a laboratory. Each record has the lab results (N, P, K, OC, pH, EC …), the date, and a GPS point.
- **N, P, K:** plant-available nitrogen, phosphorus and potassium in kg per hectare. **OC:** organic carbon in percent.
  These four are what we predict (the **targets**).
- **pH, EC:** soil acidity and electrical conductivity. Our field sensor can measure these, so they are allowed as **inputs**.

**Satellite data**
- **Sentinel-2:** a European satellite that photographs every place about every 5 days. Each image has 12 **bands**
  (B01–B12, B8A). A band is the brightness of the ground in one colour range: B02 blue, B03 green, B04 red,
  B05–B07 red-edge, B08/B8A near-infrared, B11/B12 short-wave infrared. One pixel is 10–20 m wide.
- **Scene:** one satellite image of one tile (about 110 km × 110 km) on one date.
- **Reflectance:** the fraction of sunlight the ground reflects in a band, between 0 and 1. The files store whole numbers
  (called DN); reflectance = (DN − 1000) / 10000.
- **SCL (scene classification):** a label the satellite processing gives every pixel: 4 = vegetation, **5 = bare soil**,
  8/9 = cloud, and so on. We use only pixels labelled bare soil, because crops hide the soil.
- **3×3 window:** instead of one pixel we take the 9 pixels (30 m × 30 m) around the sample point and use their median.
  This protects against GPS error and odd single pixels.
- **Single-date data:** the satellite values from **one image**, taken within ±3 days of the day the soil sample was collected.
- **Composite (multi-date composite):** instead of one image, we take **up to 12 images of the same location between
  March and May 2024**, keep only the dates when all 9 pixels were bare soil, and take the **median of each band across
  those dates**. One image can be affected by that day's conditions (wet soil after rain, haze, shadows); the median over
  many dates cancels this out and gives a more stable picture of the soil. Columns starting with `c_` are composite values.
  `c_n_dates` is how many bare dates were used, and `c_std_*` is how much the value changed between dates.
- **Spectral index:** a formula that combines bands to highlight one property, for example NDVI (greenness) or BSI
  (bare soil). Formulas are in section 3.
- **Terrain features:** computed from an elevation map: height, slope, and whether the field sits in a valley or on a ridge
  (**TPI** = topographic position index: positive = higher than its surroundings, negative = lower).
- **Microsoft Planetary Computer:** the free online service we downloaded the satellite and elevation data from.

**Data cleaning**
- **Placeholder GPS / cluster:** many samples recorded at the same spot (for example where the sampling team stood) instead
  of in each field. The satellite pixel at that spot is not those fields.
- **Clustered vs de-clustered:** the clustered dataset still contains samples within 30 m of each other. In the de-clustered
  dataset the fake spots are dropped and close samples are merged, so every row is a separate place on the ground.

**Modelling and testing**
- **R²:** how much of the variation in the true values the model explains. 1 = perfect, 0 = no better than always
  predicting the average, negative = worse than the average.
- **Random split:** choosing test samples at random. Nearby samples are similar, so the model has effectively seen the
  test fields' neighbours, and the score looks better than it really is.
- **Spatial cross-validation (spatial CV):** the map is cut into 10 km × 10 km squares (**blocks**); whole squares are used
  for testing, so the model is always tested on areas it never saw. The data is split into 5 parts (**folds**); each part is
  the test set once.
- **Out-of-fold predictions:** each sample's prediction comes from the model that did *not* train on it.
- **Data leakage:** when information about the test samples slips into training, giving falsely high scores.
- **District average baseline:** predicting every field as the average of its district, with no machine learning.
- **Within-district R²:** how well a model explains why one field differs from its district's average.
- **Noise ceiling:** the best score any model could reach, given how much lab results for the same spot disagree.
- **Ablation:** running the model with and without one part, to measure what that part contributes.

---

## 1. What is in this folder

```
TEAM_SHARE/
├── README.md                      ← this file (short reference)
├── PROJECT_GUIDE.md               ← full explanation from basics to current results
├── 01_source_data/                ← original soil data
├── 02_datasets/                   ← the datasets we built from it
├── 03_satellite_and_terrain/      ← everything downloaded from Microsoft Planetary Computer
├── 04_results/                    ← result tables of every experiment (CSV)
├── 05_experiments/                ← one documentation file per step / experiment (read its README.md)
└── 06_code/                       ← the working notebook and the download script
```

### 01_source_data — original soil data
| File | Rows × cols | What it is |
|---|---|---|
| `SLUSI_SHC_all_india.parquet` | 5,182,371 × 46 | The complete SLUSI Soil Health Card file for India, converted from the 4.2 GB GeoJSON to Parquet (fast to load). All columns are text except `geometry` (binary WKB point: x = longitude, y = latitude). Original file name: `SLUSI_Soil_Health_data.16-5037---7-8388--125-3251--41-5041.parquet` |
| `maharashtra_raw.parquet` | 355,562 × 46 | All Maharashtra records (`sid == "27"`), same 46 columns, nothing changed |

Important columns: `id` (format `27_<district code>_shc_...`), `date` (text like `7/23/24, 12:00 AM`), `N`, `P`, `K`, `OC`, `pH`, `EC`,
micronutrients (`S`, `Zn`, `Fe`, `Cu`, `Mn`, `B`), `sid` (state code), `did` (district code), `cycle`, `geometry`.
`VILLAGE`, `TEHSIL` and `BLOCK` are empty for Maharashtra.

### 02_datasets — datasets we built
| File | Rows × cols | Stage |
|---|---|---|
| `mh_candidates.parquet` | 91,818 × 51 | **Candidates:** Maharashtra samples that are the only record at their GPS point, have a valid date, are sampled Jan–Jun (bare-soil season), and have numeric N/P/K. Original 46 columns + `longitude`, `latitude`, `sample_date`, `region`, `mgrs_tile` |
| `mh_model_dataset.parquet` | 33,877 × 44 | **Clean but still CLUSTERED:** samples with a fully bare-soil satellite window, impossible soil values removed, reflectance and indices computed. Many samples are within 30 m of each other (placeholder GPS). Use this only to study the clustering or noise, not for honest model testing |
| **`mh_final_dataset.parquet`** | **17,620 × 44** | **FINAL, DE-CLUSTERED:** one row per independent location. **This is the dataset for modelling.** |

Columns of `mh_final_dataset.parquet`:
- `id`, `ids_merged` (all original sample ids merged into this location), `n_merged` (how many: 1–10), `sample_date`
- `longitude`, `latitude` — **for building test folds only, NOT model inputs** (see section 4)
- Targets: `N`, `P`, `K` (kg/ha), `OC` (%)
- Sensor-type inputs: `pH`, `EC` (dS/m) — these are lab values standing in for a field sensor
- `sentinel_scene_id`, `date_difference_days` (satellite date − sampling date, within ±3)
- 12 Sentinel-2 bands as **reflectance** (0–1): `B01 B02 B03 B04 B05 B06 B07 B08 B8A B09 B11 B12`
- `AOT` (aerosol), `WVP` (water vapour, cm)
- 16 spectral indices (formulas in section 3)

### 03_satellite_and_terrain — downloaded from Microsoft Planetary Computer
| File | Rows × cols | What it is |
|---|---|---|
| `mh_scenes.parquet` | 2,666 × 5 | Sentinel-2 L2A scenes found for the candidates (id, tile, datetime, cloud cover, footprint) |
| `mh_pairs.parquet` | 151,831 × 10 | Sample–scene pairs: scene within ±3 days of sampling and the point inside the scene's valid area |
| `mh_s2_3x3.parquet` | 61,617 × 36 | **Raw single-date download:** for each extracted pair, the median of the 3×3 pixel window (30 m × 30 m) for every band, in raw digital numbers (DN), plus pixel counts (`n_*`) and the scene classification (`SCL_major`, `SCL_min`, `SCL_max`; 5 = bare soil) |
| `comp_scenes_2024MarMay.parquet` | 1,377 × 5 | Scenes from 1 March to 31 May 2024 used for the multi-date composite |
| `comp_tasks.parquet` | 211,440 × 7 | The 12 least-cloudy scenes chosen for each of the 17,620 locations |
| `composite_parts/` (43 files) | 211,440 rows | **Raw multi-date download:** the same 3×3 window statistics for every location on up to 12 dates (raw DN) |
| **`mh_composite.parquet`** | **17,273 × 35** | **Multi-date composite features** (prefix `c_`): per location, the median reflectance over all fully-bare dates, 16 indices computed from it, temporal variability (`c_std_*`), and `c_n_dates`. Only locations with ≥ 3 bare dates |
| **`mh_terrain.parquet`** | **17,620 × 8** | **Terrain features** from the Copernicus 30 m elevation model: `elev`, `slope`, `tpi_150m`, `tpi_500m`, `tpi_1km`, `rough_90m`, `relpos_2km` |

We never downloaded full satellite images. Each request sent a 30 m square and received only the statistics for it.

### 04_results — numbers of every experiment
`01_…csv` to `08_…csv`. Each one is explained in the matching file in `05_experiments/`
(note: files 06 and 07 are swapped relative to the experiment IDs; the experiments README explains this).

### 05_experiments — documentation
Start with `05_experiments/README.md`. D00–D10 describe how the data was built. E01–E08 describe the modelling experiments.
Each file has: question or hypothesis, exact setup, results, interpretation, decision.

### 06_code
`new.ipynb` (all cells that were run, with outputs) and `s2_composite.py` (the multi-date download script).

---

## 2. How the dataset was built (lineage)

| Step | Remaining | Reason |
|---|---|---|
| All-India SLUSI SHC file | 5,182,371 | — |
| Maharashtra (state code 27) | 355,562 | Study area |
| Only record at its GPS point | 214,795 | Points shared by several records with different N/P/K were dropped |
| + valid date, inside Maharashtra, numeric N/P/K | 119,814 | Needed to match a satellite image |
| Sampled Jan–Jun | **91,818** → `mh_candidates.parquet` | Monsoon months have clouds and crops |
| Sentinel-2 scene within ±3 days | 89,973 samples (151,831 pairs) | Same soil surface state as at sampling |
| 3×3 window downloaded | 61,617 pairs | Closest-date scene first |
| Window mostly bare soil | 40,988 | Scene classification (SCL) = 5 |
| **All 9 pixels** bare soil, complete window | 36,005 | Strict bare-soil rule |
| Impossible soil values removed | 34,578 | Limits: N 20–1500, P 1–300, K 20–3000, OC 0–5, pH 3.5–10.5, EC 0–10 |
| Impossible reflectance removed | **33,877** → `mh_model_dataset.parquet` (clustered) | Reflectance must be in (0, 1] |
| OC > 0.02 and EC > 0.005 | 33,842 | Too-low values removed |
| Clusters of > 10 samples within 30 m dropped | 25,981 | Placeholder GPS: e.g. 179 "fields" inside 70 m |
| Clusters of 2–10 merged into one location (median) | 17,630 | Samples within 30 m share the same satellite window |
| Locations still < 30 m apart removed | **17,620** → `mh_final_dataset.parquet` (de-clustered) | — |
| With a multi-date composite (≥ 3 bare dates) | **17,273** | Used when composite features are needed |

---

## 3. Satellite processing and features

- **Source:** Sentinel-2 L2A (surface reflectance) from Microsoft Planetary Computer.
- **Window:** exact 3×3 pixels at 10 m (30 m × 30 m) centred on the pixel containing the sample; median per band.
  Verified identical to a direct read of the image file (20 of 20 test cases).
- **Bare-soil rule:** all 9 pixels have scene classification 5 (bare soil).
- **Reflectance = (DN − 1000) / 10000** (all imagery is from 2024; the +1000 offset applies). AOT and WVP = DN / 1000.

**Indices** (computed from reflectance; `c_` versions are computed from the composite medians):

| Name | Formula |
|---|---|
| NDVI | (B08 − B04) / (B08 + B04) |
| SAVI | 1.5 (B08 − B04) / (B08 + B04 + 0.5) |
| NBR2 | (B11 − B12) / (B11 + B12) |
| NDMI | (B08 − B11) / (B08 + B11) |
| NDWI | (B03 − B08) / (B03 + B08) |
| BSI | ((B11 + B04) − (B08 + B02)) / ((B11 + B04) + (B08 + B02)) |
| NDRE | (B8A − B05) / (B8A + B05) |
| CI (colour) | (B04 − B03) / (B04 + B03) |
| BI (brightness) | sqrt((B04² + B03²) / 2) |
| RI (redness) | B04² / (B02 · B03³) |
| R_B4B2, R_B11B12, R_B12B8, R_B11B8, R_B7B5, R_B6B5 | simple band ratios (iron oxide, clay, ferrous, SWIR/NIR, red-edge) |

**Feature groups**

| Group | Columns | Count |
|---|---|---|
| Single-date satellite | 12 bands + 16 indices (in `mh_final_dataset`) | 28 |
| Composite satellite | `c_` 12 bands + 16 indices + 5 `c_std_*` (in `mh_composite`) | 33 |
| Terrain | 7 columns of `mh_terrain` | 7 |
| Sensor | `pH`, `EC` | 2 |

---

## 4. Rules for every new experiment (so all results are comparable)

1. **Do not modify the data files.** Save new outputs under new names.
2. **No location inputs.** Never use `longitude`, `latitude`, district codes or district averages as model inputs.
   A model that uses location only tells a farmer what neighbouring fields had. Location is used only to build the test folds.
3. **Test with spatial block cross-validation, never a random split.** A random split gives falsely high scores
   (see experiment E08: the same model scores 0.17 with spatial testing but 0.35 with a random split on raw data).
4. **Targets:** N, P, K, OC, each modelled separately as `log1p(y)`; convert predictions back with `expm1` before computing metrics.
5. **Metrics:** R² over all out-of-fold predictions (main), RMSE, MAE, RPIQ (= IQR / RMSE).
6. **Seed 42.** For stability, repeat with seeds 42, 7, 13, 99, 2024.
7. **Fit any scaler, feature selection or tuning on the training folds only.**
8. **Document every experiment** in the format used in `05_experiments/` (hypothesis written before running, setup, results, interpretation).

### Exact code to load the data and build the folds
Use exactly this so that everyone has the same rows and the same folds (needs scikit-learn ≥ 1.6).

```python
import numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold

D = "TEAM_SHARE/"   # adjust to your path
data = (pd.read_parquet(D + "02_datasets/mh_final_dataset.parquet")
          .merge(pd.read_parquet(D + "03_satellite_and_terrain/mh_terrain.parquet"), on="id")
          .merge(pd.read_parquet(D + "03_satellite_and_terrain/mh_composite.parquet"), on="id")
          .reset_index(drop=True))                       # 17,273 rows

BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI",
           "R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
TERRAIN = ["elev","slope","tpi_150m","tpi_500m","tpi_1km","rough_90m","relpos_2km"]
C_BANDS, C_INDICES = [f"c_{b}" for b in BANDS], [f"c_{i}" for i in INDICES]
C_TEMP  = [f"c_std_{v}" for v in ["NDVI","BSI","NDMI","B11","B12"]]
TARGETS = ["N", "P", "K", "OC"]

# FINAL feature set (decided 2026-10-05): composite + pH/EC + terrain WITHOUT elevation = 41 features
# (elevation is excluded because it mostly encodes the region, i.e. it acts as hidden location; see E11)
TERR6 = [f for f in TERRAIN if f != "elev"]
FEATS = C_BANDS + C_INDICES + C_TEMP + ["pH", "EC"] + TERR6
assert len(FEATS) == 41

# 10 km spatial blocks -> 5 folds
lat_r = np.deg2rad(data["latitude"].to_numpy())
x = data["longitude"].to_numpy() * 111320 * np.cos(lat_r)
y = data["latitude"].to_numpy() * 110574
groups = pd.Series([f"{a}_{b}" for a, b in zip((x // 10000).astype(int), (y // 10000).astype(int))]).factorize()[0]
cv = GroupKFold(n_splits=5, shuffle=True, random_state=42)
# for train_idx, test_idx in cv.split(data[FEATS], data["N"], groups): ...
```

**Check your setup first.** With `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)`
on the 41 `FEATS` with a log1p target, pooled out-of-fold R² should be: **N 0.272, P 0.041, K 0.055, OC 0.291**
(experiment E11, set "no_elevation", 10 km). If you get these, your data and folds match ours.

Results already available on these 41 inputs (spatial CV, R²): Random Forest N 0.272 / P 0.041 / K 0.055 / OC 0.291;
SVR 0.215 / 0.007 / 0.047 / 0.231; KNN 0.153 / −0.009 / 0.034 / 0.209 (E12).

---

## 5. What we found so far (R², spatial 10 km test)

| Inputs | N | P | K | OC | Location used? |
|---|---|---|---|---|---|
| Single-date satellite only | 0.02 | −0.03 | −0.03 | 0.09 | No |
| pH + EC only | 0.17 | 0.01 | 0.00 | 0.18 | No |
| Single-date satellite + pH/EC | 0.17 | 0.02 | 0.02 | 0.23 | No |
| **Composite + pH/EC + terrain (current best without location)** | **0.41** | **0.11** | **0.12** | **0.37** | **No** |
| GPS only | 0.65 | 0.37 | 0.30 | 0.58 | Yes |
| District average (no machine learning) | 0.62 | 0.38 | 0.37 | 0.61 | Yes |

Key findings:
1. **Placeholder GPS:** 60 % of clean samples were in clusters within 30 m (e.g. 179 samples inside 70 m). Handled by de-clustering.
2. **Location explains most of the variation:** a simple district average is as good as any model that uses GPS.
3. **Within a district, field-to-field differences are not predicted by any feature we have** (satellite, composite, terrain, pH/EC all ≈ 0).
4. **Noise ceiling:** 44–61 % of the variance is between districts. Within districts about half is lab/sampling noise;
   the best possible within-district R² is about 0.39–0.52.
5. **Evaluation matters (no GPS):** with satellite + pH/EC, a random 70/30 split on raw data gives N 0.35, OC 0.38, and
   training R² reaches 0.73 / 0.76; honest spatial testing of the same model gives 0.17 (N) and 0.23 (OC).

Open check on the current best result: confirm it holds without `elev` (elevation partly encodes region) and with 50 km blocks.

Caveats: pH and EC are lab values, so sensor results are a best case. All data are from 2024. Targets are plant-available N, P, K and OC %.

---

## 6. Novelty ideas we can try

These are candidates, not decisions. Each should be tested with an ablation (with vs without the idea).

1. **Noise-aware sample weighting.** Locations merged from several lab tests (`n_merged` > 1) have more reliable target
   values. Give them more weight in training (e.g. weight = `n_merged` or its square root). Motivation: the noise-ceiling result.
2. **Nutrient chain.** Predict OC first (the most predictable target), then use the *predicted* OC as an extra input for
   N, P and K. The predicted OC must come from out-of-fold predictions to avoid leakage.
3. **Calibrated prediction ranges.** A Quantile Random Forest (or quantile gradient boosting) gives a range such as
   "N 180–260 kg/ha". Calibrate the range on held-out spatial blocks so that the stated coverage (e.g. 90 %) really holds.
   Report coverage and average range width.
4. **Class prediction.** Predict the official Soil Health Card rating classes instead of exact values:
   N low < 280, medium 280–560, high > 560 kg/ha; P low < 10, medium 10–25, high > 25 kg/ha;
   K low < 110, medium 110–280, high > 280 kg/ha; OC low < 0.5, medium 0.5–0.75, high > 0.75 %.
   Report accuracy, balanced accuracy and the confusion matrix (the classes are imbalanced).
5. **Nutrient-specific feature selection.** A separate feature subset per nutrient (the literature says N, P, K and OC
   respond to different bands). Selection must be done inside the training folds.
6. **Stacking ensemble.** Combine the best models of different families with a simple meta-model, using out-of-fold predictions.
7. **Other composite types** (data already in `composite_parts/`): the date with maximum BSI, the 90th-percentile reflectance,
   or only the driest dates, instead of the median.
8. **Multi-task learning.** One model predicting N, P, K and OC together.
9. **Crop-history features (needs a new download).** NDVI through the previous crop seasons shows irrigation and cropping
   intensity, which drive nutrients. Deferred for now.

The three ideas 1 + 2 + 3 can be combined into one proposed model ("noise-aware chained quantile forest").
