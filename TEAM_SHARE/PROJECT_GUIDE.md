# Project Guide — from the basics to the current results

Read this once from top to bottom. It assumes no background in soil science or remote sensing, only basic Python and
machine learning. `README.md` is the short reference; `05_experiments/` has the exact details of every step.

**Contents**
1. The problem we are solving
2. Soil basics
3. The ground-truth data: Soil Health Card
4. Satellite basics: Sentinel-2
5. How we got the satellite data
6. Building the dataset, step by step
7. The features
8. Machine-learning basics used here
9. How we test models (the most important part)
10. The experiments and what each one showed
11. What the results mean
12. What is still open and ideas to try
13. Rules for new work
14. Software needed

---

## 1. The problem we are solving

A farmer needs to know how much nitrogen (N), phosphorus (P), potassium (K) and organic carbon (OC) the soil has, to
decide how much fertiliser to apply. Today this needs a laboratory test, which is slow and often not done.

**Our idea (soft sensing):** estimate these values without a lab test, from things that are cheap to obtain:
- **satellite images** of the field (free, every few days), and
- **pH and EC** measured by a low-cost soil sensor in the field.

"Soft sensing" means a value that is hard to measure directly (N, P, K, OC) is estimated by a model from values that are
easy to measure.

To train and test such a model we need many fields where the true lab values are known. That is the Soil Health Card data.

**The research output** is a paper with three parts:
1. the dataset and what we learned about its quality (done),
2. a fair comparison of many algorithms (to do),
3. a new model of our own (to do).

---

## 2. Soil basics

| Term | Meaning | Typical values in our data |
|---|---|---|
| **N** (available nitrogen) | Nitrogen that plants can take up, in kg per hectare. Measured in the lab with the alkaline KMnO₄ method | median 189, most between 50 and 900 |
| **P** (available phosphorus) | kg per hectare | median 16, most between 3 and 137 |
| **K** (available potassium) | kg per hectare | median 362, most between 63 and 1,420 |
| **OC** (organic carbon) | Percent of the soil that is carbon from decayed plant matter. Linked to fertility | median 0.46 %, most between 0.09 and 2.3 |
| **pH** | Acidity: 7 neutral, below acidic, above alkaline | median 7.66 (Maharashtra soils are mostly alkaline) |
| **EC** (electrical conductivity) | Saltiness of the soil, in dS/m | median 0.30 |

"Available" matters: it is the small part of the nutrient that plants can use, not the total amount in the soil.
Available N, P and K depend strongly on **farm management** (fertiliser, irrigation, crops grown), not only on soil type.

**Official Soil Health Card rating classes:**

| | Low | Medium | High |
|---|---|---|---|
| N (kg/ha) | < 280 | 280–560 | > 560 |
| P (kg/ha) | < 10 | 10–25 | > 25 |
| K (kg/ha) | < 110 | 110–280 | > 280 |
| OC (%) | < 0.5 | 0.5–0.75 | > 0.75 |

**Maharashtra soils.** Most of the state is the Deccan plateau with **black cotton soil (Vertisol)**: dark, clay-rich,
alkaline, usually high in K and low in N and OC. The Konkan coast has red laterite soils, which are acidic.
The dark colour of black soil comes from its clay minerals, not from organic carbon. This is important later.

**Crop seasons.** Kharif (monsoon crops) is sown in June–July. Rabi (winter crops) is sown in October–November and
harvested by February–March. Between March and May most fields are empty (**fallow**) and the soil is bare and dry.
Soil Health Card samples are taken when the field is bare, before sowing.

---

## 3. The ground-truth data: Soil Health Card

The **Soil Health Card (SHC)** scheme is a Government of India programme. A sample is taken from a farmer's field
(soil from the centre and four corners, mixed), sent to a district laboratory, and the results are recorded together
with the date and a GPS point.

Our source file is the SLUSI Soil Health data for all of India:
`01_source_data/SLUSI_SHC_all_india.parquet` — **5,182,371 records, 46 columns**.

- It was converted from a 4.2 GB GeoJSON file to **Parquet** (a compressed column format that pandas loads in about a second).
- Every column is stored as text, so numbers must be converted with `pd.to_numeric`.
- `geometry` holds the GPS point in a binary format (WKB). It is decoded with `shapely.from_wkb`; x = longitude, y = latitude.
- `id` looks like `27_485_shc_2024-25.1923`: state code 27 (Maharashtra), district code 485 (Nanded).
- `date` is text like `7/23/24, 12:00 AM` (month/day/year).

**Problems in this data that we had to handle** (details in section 6):
- wrong values typed in (pH 6,982; K 552,016), zeros and "1" used as "no value";
- many samples sharing one GPS point, or recorded at a village collection spot instead of in the field;
- different laboratories in different districts, which do not measure exactly alike.

---

## 4. Satellite basics: Sentinel-2

**Sentinel-2** is a pair of European Space Agency satellites. Together they photograph every place on land about every
5 days. The images are free.

**Bands.** A normal camera records 3 colours. Sentinel-2 records 12 ranges of light, called bands, including ones the
eye cannot see. Different materials (soil, plants, water) reflect these ranges differently.

| Band | Light | Pixel size | Useful for |
|---|---|---|---|
| B01 | coastal blue | 60 m | haze in the air |
| B02, B03, B04 | blue, green, red | 10 m | soil colour, iron |
| B05, B06, B07 | red-edge | 20 m | plant health |
| B08, B8A | near-infrared | 10 m, 20 m | plants reflect this strongly; soil less |
| B09 | water vapour | 60 m | moisture in the air |
| B11, B12 | short-wave infrared | 20 m | soil moisture, clay, crop residue |

**Pixel.** The smallest square of the image: 10 m × 10 m for the sharpest bands. A typical small Indian field is
several pixels wide.

**L2A product.** Raw satellite images include the effect of the atmosphere. "Level-2A" images are already corrected
so that the values describe the ground itself (**surface reflectance**). We use only L2A.

**Reflectance.** The fraction of sunlight the ground reflects in a band, from 0 to 1. The files store whole numbers
called digital numbers (DN) to save space. For images from 2022 onwards:

`reflectance = (DN − 1000) / 10000`

Example: DN 2226 in the red band means (2226 − 1000) / 10000 = 0.12, so the soil reflects 12 % of red light.
Forgetting this conversion makes indices wrong (NDVI of a typical sample is 0.17 from raw numbers but 0.27 from reflectance).

**SCL (scene classification layer).** Each L2A image comes with a label for every pixel:

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| 0 | no data | 6 | water |
| 2 | dark / shadow | 7 | unclassified |
| 3 | cloud shadow | 8, 9 | cloud |
| 4 | vegetation | 10 | thin cirrus cloud |
| **5** | **bare soil** | 11 | snow |

To see the soil, the pixel must be **bare soil (5)**. If a crop is growing, the satellite sees the plants, not the soil.

**Tiles and scenes.** The world is divided into fixed squares of about 110 km called **MGRS tiles** (names like `43QGB`).
One image of one tile on one date is a **scene**. Maharashtra is covered by about 56 tiles.

**AOT and WVP.** Two extra layers describing the air: aerosol thickness and water vapour. They are kept in the data but
they describe the atmosphere on that day, not the soil.

**Cloud cover.** Each scene has an overall cloud percentage. We do not filter on it, because a scene that is 60 % cloudy
can still be clear over our field. We check the label of our own pixels instead.

---

## 5. How we got the satellite data

**Microsoft Planetary Computer** is a free online archive of satellite data. Two of its services are used:

- **STAC search:** a catalogue. You ask "which Sentinel-2 scenes cover this area between these dates?" and get a list.
- **Data API:** you send a small square and a scene name, and the server reads the pixels and returns only the numbers.

**Why this matters.** A scene is hundreds of megabytes. The first attempt opened the image files directly and needed
8.4 minutes per scene (about 10 days in total). Letting the server read the pixels and return only the statistics
brought this down to about 0.05 seconds per request. We never download whole images.

**Rate limit.** The service refuses clients that send too many searches. One search per soil sample (tens of thousands)
was blocked. The fix was **one search per tile** (56 searches), then matching samples to scenes on our own machine.

**The 3×3 window.** For each sample we find the 10 m pixel that contains the GPS point and take the 3×3 block of pixels
around it (30 m × 30 m). For every band the server returns the **median** of those 9 pixels. Reasons:
- phone GPS is off by 5–10 m, so a single pixel may be the wrong one;
- one odd pixel (a tree, a bund, a path) cannot dominate;
- the median ignores extreme values.

The 20 m bands are placed on the same 10 m grid, so they also give 9 values. We checked the method against a direct
read of the image file: identical in 20 of 20 cases (experiment D04).

**Matching rule.** A scene is used for a sample only if:
1. it was taken within **±3 days** of the day the soil was sampled (the soil surface must look the same as when sampled), and
2. the point lies inside the part of the scene that actually has data, and
3. **all 9 pixels are labelled bare soil**.

---

## 6. Building the dataset, step by step

| Step | Rows left | What and why |
|---|---|---|
| 1 | 5,182,371 | All-India file |
| 2 | 355,562 | **Maharashtra only** (state code 27). We checked three places where the code is stored; all agreed |
| 3 | 214,795 | **Dropped GPS points shared by several records.** 31,490 points carried 140,767 records with different N/P/K values (one point had 112). We cannot tell which sample the pixel belongs to |
| 4 | 119,814 | Kept samples with a valid date, inside Maharashtra, and numeric N, P, K |
| 5 | 91,818 | **Sampled January–June.** A pilot showed 53–68 % of Feb–May samples are usable but only 6 % in June and 0 % in July (monsoon clouds, crops sown) |
| 6 | 89,973 | Have a scene within ±3 days (151,831 sample–scene pairs) |
| 7 | 40,988 | Window downloaded and **mostly** bare soil |
| 8 | 36,005 | **All 9 pixels** bare soil and a complete window |
| 9 | 34,578 | **Impossible soil values removed** (see below) |
| 10 | 33,877 | **Impossible reflectance removed** (≤ 0 or > 1 in any band) — saved as `mh_model_dataset.parquet` (the *clustered* dataset) |
| 11 | 33,842 | OC > 0.02 and EC > 0.005 |
| 12 | 17,620 | **De-clustering** (see below) — saved as `mh_final_dataset.parquet` (the *final* dataset) |

**Step 9 — cleaning soil values.** We first looked at the values, then set limits:

| Value | Kept if | Examples of what was removed |
|---|---|---|
| N | 20 < N ≤ 1500 | negative values, 0, the placeholder "1" (314 times), 213,225 |
| P | 1 < P ≤ 300 | "1" (309 times), 11,797 |
| K | 20 < K ≤ 3000 | "1" (207 times), 552,016 |
| OC | 0 < OC ≤ 5 | 37–58 and 763–1,362 (decimal point errors) |
| pH | 3.5 ≤ pH ≤ 10.5 | 77.63 (= 7.763), 6,982, values below 3.5 |
| EC | 0 < EC ≤ 10 | 459–2,388 |

A sample was removed entirely if any one of its six values failed. Wrong values were removed, not "repaired", because
repairing means guessing. Genuinely high values (for example N = 900) were kept.

**Step 12 — de-clustering (the most important data finding).**
We measured the distance between samples and found that **60 % had another sample within 30 m**.

- *Large clusters.* One spot in Nanded had 179 samples inside 71 m × 81 m, taken on 6 different dates, with N from 27 to 266.
  That many fields cannot fit in 0.6 hectare. The samples came from fields around a village but were all recorded at one
  spot (**placeholder GPS**). **Clusters of more than 10 samples were dropped** (347 clusters, 7,861 samples).
- *Small clusters.* Samples within 30 m share the same 3×3 window, so they have the same satellite values but different
  lab values. Each cluster of 2–10 samples was **merged into one location** using the median of its values
  (12,278 samples became 3,927 locations). `n_merged` records how many were merged, and `ids_merged` lists them.
- *Isolated samples* (13,703) were kept as they are.

So there are 33,842 clean lab samples but **17,620 independent places on the ground**.

---

## 7. The features

A **feature** is an input column the model learns from.

### 7.1 Single-date satellite features (28) — in `mh_final_dataset.parquet`
The 12 bands (reflectance) from the one scene within ±3 days of sampling, plus 16 indices.

A **spectral index** combines bands to highlight one property. Most use the pattern (A − B) / (A + B), which gives a
value between −1 and 1 and cancels overall brightness.

| Index | Formula | What it shows |
|---|---|---|
| NDVI | (B08 − B04) / (B08 + B04) | greenness; bare soil is low (about 0.1–0.3) |
| SAVI | 1.5 (B08 − B04) / (B08 + B04 + 0.5) | greenness, corrected for soil background |
| NBR2 | (B11 − B12) / (B11 + B12) | crop residue and moisture on the soil |
| NDMI | (B08 − B11) / (B08 + B11) | moisture |
| NDWI | (B03 − B08) / (B03 + B08) | water |
| BSI | ((B11 + B04) − (B08 + B02)) / ((B11 + B04) + (B08 + B02)) | how bare the soil is |
| NDRE | (B8A − B05) / (B8A + B05) | red-edge greenness |
| CI | (B04 − B03) / (B04 + B03) | soil colour |
| BI | sqrt((B04² + B03²) / 2) | soil brightness |
| RI | B04² / (B02 · B03³) | soil redness (iron) |
| R_B4B2 | B04 / B02 | iron oxide |
| R_B11B12 | B11 / B12 | clay minerals |
| R_B12B8 | B12 / B08 | ferrous minerals |
| R_B11B8 | B11 / B08 | short-wave infrared vs near-infrared |
| R_B7B5, R_B6B5 | B07 / B05, B06 / B05 | red-edge ratios |

### 7.2 Multi-date composite features (33) — in `mh_composite.parquet`, prefix `c_`
One image shows the soil on one day. That day may be just after rain (wet soil is darker), hazy, or freshly ploughed.
A **composite** combines many dates to remove these one-day effects:

1. For each location, take the 12 least-cloudy scenes between **1 March and 31 May 2024** (211,440 requests in total).
2. Keep only the dates when all 9 pixels were bare soil (185,946 observations in total).
3. For each band, take the **median across those dates** → `c_B01` … `c_B12`.
4. Compute the 16 indices from these medians → `c_NDVI` …
5. Record how much the soil's appearance varied between dates → `c_std_NDVI`, `c_std_BSI`, `c_std_NDMI`, `c_std_B11`, `c_std_B12`.
6. `c_n_dates` = number of bare dates used (median 12). Locations with fewer than 3 are left out, so the composite exists
   for **17,273** of the 17,620 locations.

Single-date and composite values of the same band correlate only 0.63–0.85, so the composite really is a different,
steadier measurement.

### 7.3 Terrain features (7) — in `mh_terrain.parquet`
Computed from the Copernicus 30 m elevation map (60 map tiles).

| Feature | Meaning |
|---|---|
| `elev` | height above sea level (m) |
| `slope` | steepness in degrees |
| `tpi_150m`, `tpi_500m`, `tpi_1km` | **topographic position index:** the field's height minus the average height around it, at three distances. Positive = higher than surroundings (ridge), negative = lower (valley) |
| `rough_90m` | how uneven the ground is locally |
| `relpos_2km` | position between the lowest point (0) and the highest point (1) within about 2 km |

Valleys collect soil, water and nutrients; slopes and ridges lose them. Note that `elev` also partly reveals the region
(the coast is low, the plateau is high).

### 7.4 Sensor features (2)
`pH` and `EC`. In the real system these come from the field sensor. In our data they are lab values, so results using
them are a best case.

### 7.5 Not allowed as features
`longitude`, `latitude`, district code, district average. See section 9.

---

## 8. Machine-learning basics used here

- **Regression:** predicting a number (N = 212 kg/ha). **Classification:** predicting a class (N is "low").
- **Training and testing:** the model learns from one part of the data and is scored on another part it has not seen.
- **Overfitting:** the model memorises the training data and scores much worse on new data. The gap between training score
  and test score shows it.
- **Random Forest (RF):** many decision trees, each trained on a random part of the data, whose predictions are averaged.
  It works well on table data and needs little tuning. Settings used so far: 300 trees, at least 3 samples per leaf,
  each split considers 33 % of the features, seed 42.
- **Other model families to compare:** linear models (linear regression, Ridge, Lasso, ElasticNet, PLSR), kernel and
  neighbour models (SVR, KNN), neural networks (MLP), other tree ensembles (Extra Trees), boosting (XGBoost, LightGBM,
  CatBoost), and stacking (combining several models).
- **Feature scaling:** linear models, SVR, KNN and neural networks need all features on a similar scale
  (`StandardScaler`), fitted on the training part only. Tree models do not need it.
- **Hyperparameters:** settings chosen before training (number of trees, learning rate …). Tuning them must use only the
  training part.
- **Log transform of the target:** N, P and K have a long tail of high values. Models are trained on `log1p(y)` =
  log(1 + y) and predictions are converted back with `expm1`. This stops a few very high values from dominating.
- **Seed:** a number that fixes the random choices so a run can be repeated exactly. We use 42.

**Metrics**

| Metric | Meaning | Good is |
|---|---|---|
| **R²** | Share of the variation in the true values that the model explains. 1 = perfect; 0 = same as always predicting the average; negative = worse than the average | high |
| **RMSE** | Typical size of the error, in the target's units, with big errors counted more | low |
| **MAE** | Average size of the error, in the target's units | low |
| **RPIQ** | (spread of the middle half of the true values) / RMSE. A soil-science standard | high (above about 2 is considered good) |

---

## 9. How we test models (the most important part)

### 9.1 Why a random split is wrong here
Soil is similar in nearby places. If test samples are picked at random, almost every test field has training fields a few
hundred metres away. The model can score well simply because it has seen the neighbours, not because it understands the
soil. This is **data leakage** caused by **spatial autocorrelation**.

### 9.2 Spatial block cross-validation
- The map is cut into **10 km × 10 km squares (blocks)**: about 1,550 blocks.
- The blocks are divided into **5 groups (folds)**.
- Five rounds: each round, four folds train the model and the fifth is the test set. Every location is tested exactly once,
  by a model that never saw its block.
- The predictions from all five rounds together are the **out-of-fold predictions**, and R² is computed on them.

Measured difference on our data, same model and features (experiment E08):

| How it is tested (satellite + pH/EC, no GPS) | N | OC |
|---|---|---|
| Spatial blocks, de-clustered data (our method) | 0.17 | 0.23 |
| Random 70/30 split, de-clustered data | 0.25 | 0.28 |
| Random 70/30 split, clustered data | 0.35 | 0.38 |
| Score on the training data itself | 0.73 | 0.76 |

Many published papers use the lower rows. This is the main reason their numbers look higher than ours.

### 9.3 Why location is not allowed as an input
A model given longitude and latitude learns a map of lab results and predicts each field from its neighbours. It scored
N 0.65 using GPS alone. But it measures nothing about the field: it tells the farmer "your soil is probably like the
fields tested 5–10 km away". Our aim is to estimate **this field** from what is observed **at this field**. So:

- **Not inputs:** longitude, latitude, district, district average.
- **Location is used only to build the test blocks.**

---

## 10. The experiments and what each one showed

All use Random Forest and the 10 km spatial test. R² values are shown. Full details are in `05_experiments/`.

**E01 — Which inputs help?**

| Inputs | N | P | K | OC |
|---|---|---|---|---|
| Single-date satellite | 0.02 | −0.03 | −0.03 | 0.09 |
| pH + EC | 0.17 | 0.01 | 0.00 | 0.18 |
| Satellite + pH/EC | 0.15 | 0.01 | 0.02 | 0.22 |
| Satellite + pH/EC + GPS | 0.58 | 0.30 | 0.25 | 0.52 |

The satellite alone predicts almost nothing. pH and EC help a little. GPS causes a large jump.

**E02 — What is GPS doing?** GPS alone scored N 0.65, P 0.37, K 0.30, OC 0.58, better than GPS plus everything else.
With stricter 50 km blocks it still scored N 0.52. So nutrients follow large regional patterns.

**E03 — Is it just the district?** Predicting each field as its district's average, with no machine learning, scored
N 0.62, P 0.38, K 0.37, OC 0.61: as good as the best model. Most of the predictable variation is between districts.

**E04 — Two-stage model.** Stage 1 predicts the district average. Stage 2 is a Random Forest that predicts how far each
field is from that average. The **within-district R²** measures how well stage 2 does:

| Stage-2 inputs | N | P | K | OC |
|---|---|---|---|---|
| Satellite | −0.02 | −0.02 | −0.02 | −0.02 |
| pH + EC | −0.06 | −0.07 | −0.09 | −0.07 |
| Satellite + pH/EC | −0.01 | −0.01 | −0.02 | −0.01 |
| + GPS | 0.12 | 0.06 | 0.02 | 0.04 |

Inside a district, neither the satellite nor pH/EC can tell one field from another.

**E05 — Add terrain.** Terrain alone: nothing. Terrain with the satellite: N rises to 0.04 within districts; others stay near 0.

**E06 — Add the multi-date composite.** No gain within districts, not even for OC. So one-day noise in the image was not
the reason the satellite failed.

**E07 — Noise ceiling.** We asked: how much could any model explain? Samples within 30 m of each other are effectively
the same spot, so the differences between their lab values are noise.

| | N | P | K | OC |
|---|---|---|---|---|
| Share of all variation that is between districts | 61 % | 47 % | 44 % | 60 % |
| Best possible within-district R² (the ceiling) | 0.52 | 0.49 | 0.47 | 0.39 |
| What we reached within districts (with GPS) | 0.12 | 0.06 | 0.03 | 0.04 |

About half of the within-district variation is noise. The other half is real, and our features do not capture it.

**E08 — Random split vs spatial test, and the best model without location.** The inflation table is in section 9.2.
The same experiment gave the best result so far **without any location input**:

| Inputs (no location) | N | P | K | OC |
|---|---|---|---|---|
| Single-date satellite + pH/EC | 0.17 | 0.02 | 0.02 | 0.23 |
| **Composite + pH/EC + terrain** | **0.41** | **0.11** | **0.12** | **0.37** |

---

## 11. What the results mean

1. **Where a field is explains most of what can be predicted.** Soil nutrients in this data differ mainly between regions.
   Part of that is real geography (black soil vs laterite) and part is probably differences between district laboratories.
2. **The composite plus terrain plus pH/EC reaches N 0.41 and OC 0.37 without location.** It works by recognising the
   regional soil type from the field's own appearance and terrain. It does not separate neighbouring fields
   (within-district scores stay near 0).
3. **Field-to-field differences inside a district are not predicted by anything we have.** Likely reasons:
   - available N, P and K have no direct colour signature in 12 broad bands;
   - in black soil the darkness comes from clay, not organic carbon, and OC varies only a little;
   - the lab values contain a lot of noise;
   - the real driver is farm management (fertiliser, irrigation, crop history), which bare soil does not show.
4. **Honest testing gives lower numbers than most papers report**, and we can show exactly why (section 9.2).
   One published study on Soil Health Card data (Mundada & Jain, 2025) reports a training R² of 0.95; a literature
   review we compiled gives its test R² as about 0.03–0.12 (check the full paper before quoting the test figures).

---

## 12. What is still open and ideas to try

**Open check:** confirm that the best no-location result (N 0.41, OC 0.37) still holds without `elev` and with 50 km blocks,
and find out whether the composite or the terrain causes the gain.

**Algorithm comparison:** run each model family under exactly the same data, features, folds and metrics.

**Novelty ideas** (each tested with and without the idea):
1. **Noise-aware weighting:** give more training weight to locations merged from several lab tests (`n_merged` > 1),
   because their target values are more reliable.
2. **Nutrient chain:** predict OC first, then use the predicted OC as an input for N, P and K (using out-of-fold predictions).
3. **Calibrated ranges:** predict a range (for example "N 180–260 kg/ha") with a Quantile Random Forest, and calibrate it
   on held-out blocks so the stated coverage (such as 90 %) is real.
4. **Class prediction:** predict low / medium / high (section 2) and report accuracy, balanced accuracy and the confusion matrix.
5. **Nutrient-specific feature selection:** a separate feature subset per nutrient, chosen inside the training folds.
6. **Stacking:** combine the best models of different families.
7. **Other composites:** the date with the highest BSI, the 90th percentile, or only the driest dates
   (the per-date data is in `03_satellite_and_terrain/composite_parts/`).
8. **Multi-task model:** one model predicting all four targets together.
9. **Crop history (later):** greenness through the previous crop seasons shows irrigation and cropping intensity.

Ideas 1 + 2 + 3 can form one proposed model.

---

## 13. Rules for new work

1. Never change the data files. Save new outputs under new names.
2. No location inputs (section 9.3).
3. Test only with the 10 km spatial blocks and 5 folds, built with the exact code in `README.md` section 4.
4. Train on `log1p(y)`, convert back with `expm1`, then compute metrics.
5. Report R² (out-of-fold), RMSE, MAE and RPIQ for each of N, P, K, OC.
6. Seed 42; repeat with 7, 13, 99, 2024 to check stability.
7. Fit scalers, feature selection and tuning on the training folds only.
8. Use the final 41 inputs (composite 33 + pH, EC + 6 terrain features without `elev`; see README section 4).
   First reproduce the reference result (Random Forest on these 41: N 0.272, P 0.041, K 0.055, OC 0.291).
   If your numbers match, your setup is correct.
9. Write the hypothesis **before** running an experiment, then record setup, results and interpretation in the same
   format as `05_experiments/`. Record failures as well as successes.

---

## 14. Software needed

Python 3.10 or newer with: `pandas`, `numpy`, `pyarrow`, `scikit-learn` (1.6 or newer), `scipy`.
For specific models: `xgboost`, `lightgbm`, `catboost`, `shap`, `quantile-forest`, `tensorflow` or `torch`.
Only needed to repeat the downloads: `pystac-client`, `planetary-computer`, `rasterio`, `shapely`, `pyproj`, `mgrs`, `requests`.
