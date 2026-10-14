# E32 — Nearby pairs: do similar satellite features mean similar nutrients?

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 1 of a four-part cell; parts 2–4 are E33–E35)
**Results:** `results/32_nearby_pairs.csv`
**Data:** model table, 17,273 locations

## Question
Published work shows that soil nutrients vary between fields. The specific question here: for two nearby fields whose
satellite features are nearly the same, are the nutrients also more alike?

No hypothesis was recorded in advance: the test was first run as an exploratory script on 2026-10-09 and then repeated
unchanged as this notebook cell (same numbers).

## Setup
- All pairs of locations closer than 2 km and inside the same region (`cKDTree.query_pairs`).
- N, P, K, OC as log1p; the 28 composite satellite features (12 bands + 16 indices). Every variable is standardised
  **inside its region**.
- Measure per pair group: half the mean squared difference of the standardised values. This is the share of the
  regional variance that separates the two locations of a pair: 0 = identical, 1.0 = as different as two random
  locations of the region.
- "Most similar satellite": the 25 % of pairs under 500 m with the smallest standardised satellite distance.

## Results

| Pair group | Pairs | Satellite | N | P | K | OC |
|---|---|---|---|---|---|---|
| 30–100 m | 5,813 | 0.36 | 0.22 | 0.22 | 0.32 | 0.32 |
| 100–250 m | 12,337 | 0.50 | 0.24 | 0.21 | 0.34 | 0.36 |
| 250–500 m | 21,842 | 0.57 | 0.26 | 0.23 | 0.36 | 0.37 |
| 500–1000 m | 43,867 | 0.61 | 0.28 | 0.26 | 0.39 | 0.40 |
| 1000–2000 m | 65,539 | 0.67 | 0.30 | 0.29 | 0.42 | 0.45 |
| **All pairs < 500 m** | 39,992 | **0.52** | 0.25 | 0.22 | 0.35 | 0.36 |
| **< 500 m and most similar satellite** | 9,998 | **0.10** | 0.25 | 0.23 | 0.32 | 0.35 |

Nearby pairs with the most similar satellite features, original units:

| Nutrient | Median absolute difference | Median % difference | Pairs differing by > 30 % |
|---|---|---|---|
| N | 29.0 kg/ha | 14.5 % | 25.1 % |
| P | 3.5 kg/ha | 20.8 % | 36.5 % |
| K | 62.9 kg/ha | 17.5 % | 31.6 % |
| OC | 0.09 % | 20.8 % | 35.7 % |

Correlation between satellite difference and nutrient difference, pairs < 500 m: N −0.000, P 0.003, K 0.033, OC −0.003.

## Interpretation
1. **Nearby fields are much more alike than random fields of the region.** Only 22–36 % of the regional variance
   separates two fields less than 100 m apart. This is the spatial structure that location-based prediction and random
   splits exploit.
2. **Satellite similarity adds nothing to that.** Selecting the pairs whose satellite features are five times more alike
   (0.52 → 0.10) leaves the nutrient difference unchanged (N 0.25 → 0.25, P 0.22 → 0.23, K 0.35 → 0.32, OC 0.36 → 0.35),
   and the correlation between the two differences is zero.
3. **The remaining difference is not small in practice:** a quarter to a third of nearby, satellite-similar pairs differ
   by more than 30 %.
4. Wording for the paper: neighbouring fields are similar on average, but the difference that remains between them is
   not related to their Sentinel-2 composite features.

## Caveats
- Nearby samples were often analysed by the same laboratory in the same batch, so part of their similarity may be a
  shared laboratory effect.
- Minimum pair distance is 30 m (closer samples were merged in D08). GPS error of the SHC positions is unknown.
- Composite features are Mar–May 2024 medians; the test says nothing about other sensors or hyperspectral data.
