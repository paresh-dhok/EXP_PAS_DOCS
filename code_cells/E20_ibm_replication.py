"""E20 - Repeating the IBM study (Kaur, Das & Hazra, IGARSS 2020) on our data.

Pune + Ahmednagar, IBM-like inputs (satellite composite + terrain with elevation + climate),
four models (MLR, RFR, GB, SVR), IBM value ranges and our full ranges,
random 80/20 test and 10 km spatial CV. Reports R2, RMSE and sMAPE.
Documentation: experiments/E20_ibm_replication.md   Results: results/20_ibm_replication.csv

This file is the notebook code: PART 1 is the setup cell (loads the data and builds the
spatial blocks), PART 2 is the experiment cell. Run from the Start folder.
"""

# ===================== PART 1: setup =====================
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score

OUT_DIR = Path(r"D:\SEM 7\CAPSTONE\DATA\slusi\Start")
RES_DIR = OUT_DIR / "results"
SEED = 42

BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI",
           "R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
TERRAIN = ["elev","slope","tpi_150m","tpi_500m","tpi_1km","rough_90m","relpos_2km"]
TARGETS = ["N", "P", "K", "OC"]
C_BANDS, C_INDICES = [f"c_{b}" for b in BANDS], [f"c_{i}" for i in INDICES]
C_TEMP  = [f"c_std_{v}" for v in ["NDVI", "BSI", "NDMI", "B11", "B12"]]

data = (pd.read_parquet(OUT_DIR / "mh_final_dataset.parquet")
          .merge(pd.read_parquet(OUT_DIR / "mh_terrain.parquet"), on="id")
          .merge(pd.read_parquet(OUT_DIR / "mh_composite.parquet"), on="id")
          .reset_index(drop=True))
data["district"] = data["id"].str.split("_").str[1]

lat_r = np.deg2rad(data["latitude"].to_numpy())
x = data["longitude"].to_numpy() * 111320 * np.cos(lat_r)
y = data["latitude"].to_numpy() * 110574
groups = pd.Series([f"{a}_{b}" for a, b in zip((x // 10000).astype(int), (y // 10000).astype(int))]).factorize()[0]
spatial_cv = GroupKFold(n_splits=5, shuffle=True, random_state=SEED)

print(f"Model table: {len(data):,} locations | 10 km blocks: {groups.max() + 1:,}")


# ===================== PART 2: IBM replication =====================
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

CLIMATE = ["ppt_annual", "ppt_monsoon", "tmax_mean", "tmin_mean", "tmean", "def_annual"]
if "ppt_annual" not in data.columns:
    data = data.merge(pd.read_parquet(OUT_DIR / "mh_climate.parquet"), on="id", how="left")

mask2 = data["district"].isin(["490", "466"]).to_numpy()          # 490 = Pune, 466 = Ahmednagar (Ahilyanagar)
d2, g2 = data[mask2].reset_index(drop=True), groups[mask2]
print(f"Pune + Ahmednagar locations: {len(d2):,} | 10 km blocks: {len(np.unique(g2))}")

SAT = C_BANDS + C_INDICES + C_TEMP
SETS_20 = {"IBM-like (satellite + terrain + elevation + climate)": SAT + TERRAIN + CLIMATE,
           "IBM-like + pH, EC":                                    SAT + TERRAIN + CLIMATE + ["pH", "EC"]}
IBM_RANGE = {"N": (150, 350), "K": (150, 350), "P": (0, 30), "OC": (0, 1)}
MODELS_20 = {
    "MLR": lambda: make_pipeline(StandardScaler(), LinearRegression()),
    "RFR": lambda: RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, n_jobs=-1, random_state=SEED),
    "GB":  lambda: GradientBoostingRegressor(random_state=SEED),
    "SVR": lambda: make_pipeline(StandardScaler(), SVR(kernel="rbf", C=1.0)),
}

def smape(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(np.mean(np.abs(y - p) / ((np.abs(y) + np.abs(p)) / 2)))

rows20, t0 = [], time.time()
for rng_name in ["IBM value range", "our full range"]:
    for t in TARGETS:
        if rng_name == "IBM value range":
            lo, hi = IBM_RANGE[t]
            keep = d2[t].between(lo, hi).to_numpy()
        else:
            keep = np.ones(len(d2), bool)
        sub, g = d2[keep].reset_index(drop=True), g2[keep]
        y_t = sub[t]
        for set_name, feats in SETS_20.items():
            X = sub[feats]
            Xtr, Xte, ytr, yte = train_test_split(X, y_t, test_size=0.2, random_state=SEED)
            for m_name, make in MODELS_20.items():
                p = make().fit(Xtr, ytr).predict(Xte)                         # random 80/20 (IBM's test)
                oof = np.zeros(len(sub))
                for a, b in spatial_cv.split(X, y_t, g):                       # spatial 10 km (our test)
                    oof[b] = make().fit(X.iloc[a], y_t.iloc[a]).predict(X.iloc[b])
                rows20.append({"range": rng_name, "features": set_name, "target": t, "model": m_name, "n": len(sub),
                               "R2_8020": r2_score(yte, p), "RMSE_8020": mean_squared_error(yte, p) ** 0.5, "sMAPE_8020": smape(yte, p),
                               "R2_spatial": r2_score(y_t, oof), "RMSE_spatial": mean_squared_error(y_t, oof) ** 0.5,
                               "sMAPE_spatial": smape(y_t, oof)})
    print(f"{rng_name} done | {time.time() - t0:.0f}s")

res20 = pd.DataFrame(rows20)
res20.to_csv(RES_DIR / "20_ibm_replication.csv", index=False)

IBM = pd.DataFrame({"N": [0.294, 35.464, 0.125], "P": [0.225, 5.727, 0.362], "K": [0.322, 54.979, 0.209], "OC": [0.182, 0.138, 0.274]},
                   index=["R2", "RMSE", "sMAPE"])
print("\n=== IBM paper, Table 4 (RFR, test data) ===")
print(IBM.to_string())
first_set = list(SETS_20)[0]
for rng_name in ["IBM value range", "our full range"]:
    s = res20[(res20["range"] == rng_name) & (res20["features"] == first_set)]
    print(f"\n=== Ours: Pune + Ahmednagar, {rng_name}, IBM-like inputs | n per nutrient: "
          f"{s.groupby('target')['n'].first().reindex(TARGETS).to_dict()} ===")
    for col in ["R2_8020", "RMSE_8020", "sMAPE_8020", "R2_spatial"]:
        print(f"-- {col}")
        print(s.pivot(index="model", columns="target", values=col).reindex(list(MODELS_20))[TARGETS].round(3).to_string())
print("\n=== Effect of adding pH, EC (RFR, R2 random 80/20) ===")
print(res20[res20["model"] == "RFR"].pivot_table(index=["range", "features"], columns="target", values="R2_8020")[TARGETS].round(3).to_string())

