import numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import TransformedTargetRegressor
D = "/Users/mihirmohite/Downloads/EXP_PAS_DOCS/TEAM_SHARE/"
FEATDIR = "/private/tmp/claude-502/-Users-mihirmohite-MIT-Capstone/f643fcfb-f07d-48ba-bf86-c378aa469694/scratchpad/feat/"
def load():
    data = (pd.read_parquet(D + "02_datasets/mh_final_dataset.parquet")
              .merge(pd.read_parquet(D + "03_satellite_and_terrain/mh_terrain.parquet"), on="id")
              .merge(pd.read_parquet(D + "03_satellite_and_terrain/mh_composite.parquet"), on="id")
              .reset_index(drop=True))
    data = data.merge(pd.read_parquet(D + "02_datasets/mh_candidates.parquet", columns=["id", "region"]), on="id", how="left")
    lat_r = np.deg2rad(data["latitude"].to_numpy())
    x = data["longitude"].to_numpy() * 111320 * np.cos(lat_r); y = data["latitude"].to_numpy() * 110574
    groups = pd.Series([f"{a}_{b}" for a, b in zip((x // 10000).astype(int), (y // 10000).astype(int))]).factorize()[0]
    return data, groups
BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI","R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
FEATS = ([f"c_{b}" for b in BANDS] + [f"c_{i}" for i in INDICES] + [f"c_std_{v}" for v in ["NDVI","BSI","NDMI","B11","B12"]]
         + ["pH", "EC"] + ["slope","tpi_150m","tpi_500m","tpi_1km","rough_90m","relpos_2km"])
assert len(FEATS) == 41
TARGETS = ["N", "P", "K", "OC"]
REGIONS = ["Vidarbha", "Marathwada", "North MH", "Western MH", "Konkan"]
def make_rf(seed=42):
    return TransformedTargetRegressor(regressor=RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, n_jobs=-1, random_state=seed),
                                      func=np.log1p, inverse_func=np.expm1)
def evaluate_region_wise(data, groups, feats, name, make_model=make_rf, seed=42, verbose=False):
    cv = GroupKFold(n_splits=5, shuffle=True, random_state=42); rows = []
    for r in REGIONS:
        idx = np.where(data["region"] == r)[0]; sub, g = data.iloc[idx], groups[idx]; X = sub[feats]
        for t in TARGETS:
            y_t = sub[t]; oof = np.zeros(len(sub))
            for a, b in cv.split(X, y_t, g):
                oof[b] = make_model(seed).fit(X.iloc[a], y_t.iloc[a]).predict(X.iloc[b])
            rmse = mean_squared_error(y_t, oof) ** 0.5
            rows.append({"set": name, "seed": seed, "region": r, "target": t, "n": len(sub), "R2": r2_score(y_t, oof), "RMSE": rmse,
                         "MAE": mean_absolute_error(y_t, oof), "RPIQ": (y_t.quantile(0.75) - y_t.quantile(0.25)) / rmse})
            if verbose: print(f"{name} | {r:<11} {t:<3} R2={rows[-1]['R2']:.3f}", flush=True)
    return pd.DataFrame(rows)
