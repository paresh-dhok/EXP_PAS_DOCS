"""reproduce_E49_E56.py - standalone reproduction of the paper's primary analysis (E49-E56, 32,096 samples).

Mirrors notebook Start/new.ipynb cells 66-85 (same data files, same functions, same seeds, same job definitions).
Writes ONLY to Start/results_repro/ and then compares every numeric value with the original files in Start/results/.
    python reproduce_E49_E56.py
"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from pathlib import Path
from joblib import Parallel, delayed
from scipy.spatial import cKDTree
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.metrics import r2_score

# ---------------- cell 67: setup ----------------
OUT_DIR = Path(r"D:\SEM 7\CAPSTONE\DATA\slusi\Start")
ORIG_DIR = OUT_DIR / "results"
RES_DIR = OUT_DIR / "results_repro"; RES_DIR.mkdir(exist_ok=True)
SEED = 42
BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI",
           "R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
TARGETS = ["N", "P", "K", "OC"]
LOG = open(RES_DIR / "run_log.txt", "w", encoding="utf-8")
def say(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n"); LOG.flush(); sys.stdout.flush()

# ---------------- cell 66: data, elevation/climate assignment, blocks, features ----------------
TERRAIN = ["elev","slope","tpi_150m","tpi_500m","tpi_1km","rough_90m","relpos_2km"]
CLIMATE = ["ppt_annual", "ppt_monsoon", "tmax_mean", "tmin_mean", "tmean", "def_annual"]
REGIONS = ["Vidarbha", "Marathwada", "North MH", "Western MH", "Konkan"]
reg = pd.read_parquet(OUT_DIR / "mh_candidates.parquet", columns=["id", "region"])
clus = pd.read_parquet(OUT_DIR / "mh_model_dataset.parquet").merge(reg, on="id", how="left")
dec  = pd.read_parquet(OUT_DIR / "mh_final_dataset.parquet").merge(reg, on="id", how="left")
ctx  = (pd.read_parquet(OUT_DIR / "mh_terrain.parquet").merge(pd.read_parquet(OUT_DIR / "mh_climate.parquet"), on="id")
          .merge(dec[["id", "longitude", "latitude"]], on="id"))
def xy(d):
    lat_r = np.deg2rad(d["latitude"].to_numpy())
    return np.c_[d["longitude"].to_numpy() * 111320 * np.cos(lat_r), d["latitude"].to_numpy() * 110574]
dist, nn = cKDTree(xy(ctx)).query(xy(clus))
for c in ["elev"] + CLIMATE:
    clus[c] = ctx[c].to_numpy()[nn]
def blocks(d):
    p = xy(d); return pd.Series([f"{a}_{b}" for a, b in zip((p[:,0]//10000).astype(int), (p[:,1]//10000).astype(int))]).factorize()[0]
FEATS = BANDS + INDICES + ["pH", "EC"] + ["elev"] + CLIMATE + ["longitude", "latitude"]
def fit_predict(Xtr, ytr, Xte, seed):
    from lightgbm import LGBMRegressor
    z = np.log1p(ytr); mu, sd = z.mean(), z.std()
    m = LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=15, min_child_samples=20, subsample=0.8,
                      subsample_freq=1, colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, random_state=seed, verbose=-1)
    return np.expm1(m.fit(Xtr, (z - mu) / sd).predict(Xte) * sd + mu)

# ---------------- cell 68: metrics ----------------
UNITS = {"N": "kg/ha", "P": "kg/ha", "K": "kg/ha", "OC": "%"}
def metrics(y, p):
    e = p - y
    rmse = np.sqrt(np.mean(e ** 2))
    return {"R2": r2_score(y, p), "RMSE": rmse, "MAE": np.mean(np.abs(e)), "bias": e.mean(),
            "RPIQ": (np.percentile(y, 75) - np.percentile(y, 25)) / rmse}

# ---------------- cell 69: block grids ----------------
BLOCKS_KM = [10, 25, 50, 100]
def blocks_km(d, km):
    p = xy(d); s = km * 1000
    return pd.Series([f"{a}_{b}" for a, b in zip((p[:,0]//s).astype(int), (p[:,1]//s).astype(int))]).factorize()[0]
G = {km: blocks_km(clus, km) for km in BLOCKS_KM}

# ---------------- cell 70: LRS features ----------------
K_NB = 10
def nb_features(P_tr, y_tr, P_q, self_query):
    k = K_NB + 1 if self_query else K_NB
    d, i = cKDTree(P_tr).query(P_q, k=k)
    if self_query:
        d, i = d[:, 1:], i[:, 1:]
    w = 1 / np.maximum(d, 1.0)
    v = np.log1p(y_tr)[i]
    return np.c_[(w * v).sum(1) / w.sum(1), v[:, 0], np.log1p(d[:, 0]), v.std(1)]
def fit_predict_nb(X, P, y, tr, te, seed):
    Xtr = np.c_[X[tr], nb_features(P[tr], y[tr], P[tr], True)]
    Xte = np.c_[X[te], nb_features(P[tr], y[tr], P[te], False)]
    return fit_predict(Xtr, y[tr], Xte, seed)
P_cl = xy(clus)
G10 = blocks(clus)

# ---------------- cell 71: task43 ----------------
def task43(region, target, inputs, test, X, P, y, g, seed):
    import warnings; warnings.filterwarnings("ignore")
    if "neighbourhood" in inputs:
        run = fit_predict_nb
    else:
        run = lambda X, P, y, tr, te, s: fit_predict(X[tr], y[tr], X[te], s)
    if g is None:
        tr, te = train_test_split(np.arange(len(y)), test_size=0.30, random_state=seed)
        yy, pp = y[te], run(X, P, y, tr, te, seed)
    else:
        pp = np.zeros(len(y))
        for a, b in GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, g):
            pp[b] = run(X, P, y, a, b, seed)
        yy = y
    return {"region": region, "target": target, "inputs": inputs, "test": test, "n": len(y),
            "R2": r2_score(yy, pp), "RMSE": np.sqrt(np.mean((pp - yy) ** 2))}

# ---------------- cell 72: models ----------------
MODELS = ["Linear (ridge)", "KNN", "MLP", "Random Forest", "LightGBM"]
def make_model(name, seed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.neural_network import MLPRegressor
    from sklearn.ensemble import RandomForestRegressor
    from lightgbm import LGBMRegressor
    if name == "Linear (ridge)":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == "KNN":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=15, weights="distance"))
    if name == "MLP":
        return make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(64, 32), alpha=1e-3, max_iter=200,
                                                            early_stopping=True, random_state=seed))
    if name == "Random Forest":
        return RandomForestRegressor(n_estimators=100, min_samples_leaf=5, max_features=0.33, n_jobs=1, random_state=seed)
    return LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=15, min_child_samples=20, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, random_state=seed, verbose=-1)
def fit_predict_m(name, X, P, y, tr, te, seed):
    Xtr = np.c_[X[tr], nb_features(P[tr], y[tr], P[tr], True)]
    Xte = np.c_[X[te], nb_features(P[tr], y[tr], P[te], False)]
    z = np.log1p(y[tr]); mu, sd = z.mean(), z.std()
    m = make_model(name, seed).fit(Xtr, (z - mu) / sd)
    return np.expm1(np.clip(m.predict(Xte) * sd + mu, z.min(), z.max()))
def task44(name, target, test, X, P, y, g, seed):
    import warnings, time; warnings.filterwarnings("ignore")
    t_start = time.time()
    if g is None:
        tr, te = train_test_split(np.arange(len(y)), test_size=0.30, random_state=seed)
        yy, pp = y[te], fit_predict_m(name, X, P, y, tr, te, seed)
    else:
        pp = np.zeros(len(y))
        for a, b in GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, g):
            pp[b] = fit_predict_m(name, X, P, y, a, b, seed)
        yy = y
    e = pp - yy
    return {"model": name, "target": target, "test": test, "R2": r2_score(yy, pp),
            "RMSE": np.sqrt(np.mean(e ** 2)), "MAE": np.mean(np.abs(e)), "sec": time.time() - t_start}
X_all = clus[FEATS].to_numpy(float)

# ---------------- cell 73: lgbm helper ----------------
def lgbm(seed):
    from lightgbm import LGBMRegressor
    return LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=15, min_child_samples=20, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, random_state=seed, verbose=-1)

# ---------------- cell 74: SHAP task ----------------
NB_NAMES = ["nb_idw_mean", "nb_nearest_value", "nb_nearest_dist", "nb_sd"]
NAMES = FEATS + NB_NAMES
GROUPS = {"Satellite bands (12)": BANDS, "Spectral indices (16)": INDICES, "pH, EC (2)": ["pH", "EC"],
          "Elevation (1)": ["elev"], "Climate (6)": CLIMATE, "Coordinates (2)": ["longitude", "latitude"],
          "Neighbourhood (4)": NB_NAMES}
def task46(target, test, X, P, y, g, seed):
    import warnings; warnings.filterwarnings("ignore")
    if g is None:
        splits = [train_test_split(np.arange(len(y)), test_size=0.30, random_state=seed)]
    else:
        splits = list(GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, g))
    sh = []
    for tr, te in splits:
        nb_tr = nb_features(P[tr], y[tr], P[tr], True)
        nb_te = nb_features(P[tr], y[tr], P[te], False)
        z = np.log1p(y[tr]); mu, sd = z.mean(), z.std()
        m = lgbm(seed).fit(np.c_[X[tr], nb_tr], (z - mu) / sd)
        sh.append(np.abs(m.predict(np.c_[X[te], nb_te], pred_contrib=True)[:, :-1]))
    a = np.vstack(sh).mean(0)
    return [{"target": target, "test": test, "input": n, "mean_abs_shap": v, "share_pct": 100 * v / a.sum()}
            for n, v in zip(NAMES, a)]

# ---------------- cell 75/77: Raigad exclusion ----------------
clus["district"] = clus["id"].str.split("_").str[1]
mask = (clus["district"] != "491").to_numpy()
X_nr, P_nr, G_nr = X_all[mask], P_cl[mask], G10[mask]
say(f"Dataset: {len(clus):,} rows -> {mask.sum():,} after removing Raigad (491)")

def fit_nb_both(X, P, y, tr, te, seed):
    Xtr = np.c_[X[tr], nb_features(P[tr], y[tr], P[tr], True)]
    Xte = np.c_[X[te], nb_features(P[tr], y[tr], P[te], False)]
    z = np.log1p(y[tr]); mu, sd = z.mean(), z.std()
    m = lgbm(seed).fit(Xtr, (z - mu) / sd)
    return np.expm1(m.predict(Xte) * sd + mu), np.expm1(m.predict(Xtr) * sd + mu)
def task49(target, X, P, y, g, seed):
    import warnings; warnings.filterwarnings("ignore")
    tr, te = train_test_split(np.arange(len(y)), test_size=0.30, random_state=seed)
    p_te, p_tr = fit_nb_both(X, P, y, tr, te, seed)
    oof = np.zeros(len(y))
    for a, b in GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, g):
        oof[b] = fit_nb_both(X, P, y, a, b, seed)[0]
    rows = [{"target": target, "evaluation": ev, "n": len(yy), **metrics(yy, pp)}
            for ev, yy, pp in [("random 70/30 train", y[tr], p_tr), ("random 70/30 test", y[te], p_te),
                               ("spatial 10 km CV", y, oof)]]
    return rows, (y[te], p_te), (y, oof)

T0 = time.time()
# ---------------- E49 (cell 77) ----------------
t0 = time.time()
out49 = Parallel(n_jobs=4)(delayed(task49)(t, X_nr, P_nr, clus[t].to_numpy(float)[mask], G_nr, SEED) for t in TARGETS)
res49 = pd.DataFrame([r for rows, _, _ in out49 for r in rows])
res49.to_csv(RES_DIR / "49_headline_metrics.csv", index=False)
say(f"E49 done in {(time.time() - t0) / 60:.1f} min")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
for j, t in enumerate(TARGETS):
    for i, (label, (yy, pp)) in enumerate([("Random 70/30 test", out49[j][1]), ("Spatial 10 km CV", out49[j][2])]):
        ax = axes[i, j]
        hi = np.percentile(np.r_[yy, pp], 99.5)
        ax.hexbin(yy, pp, gridsize=45, extent=(0, hi, 0, hi), bins="log", mincnt=1, cmap="Blues", linewidths=0)
        ax.plot([0, hi], [0, hi], color="#6b6b6b", lw=1, ls="--")
        ax.set_xlim(0, hi); ax.set_ylim(0, hi); ax.set_aspect("equal")
        m = metrics(yy, pp)
        ax.text(0.04, 0.96, f"R² = {m['R2']:.2f}\nRMSE = {m['RMSE']:.3g}\nn = {len(yy):,}", transform=ax.transAxes, va="top", fontsize=9, color="#2b2b2b")
        ax.set_title(f"{t} ({UNITS[t]}) – {label}", fontsize=10, color="#2b2b2b")
        ax.set_xlabel("Measured", fontsize=9, color="#555555"); ax.set_ylabel("Predicted", fontsize=9, color="#555555")
        ax.tick_params(labelsize=8, colors="#555555")
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        for s in ["left", "bottom"]: ax.spines[s].set_color("#bbbbbb")
fig.savefig(RES_DIR / "49_measured_vs_predicted.png", dpi=300); plt.close(fig)

# ---------------- E50 (cell 78) ----------------
t0 = time.time()
reg_nr = clus["region"].to_numpy()[mask]
jobs = []
for scope in ["statewide"] + REGIONS:
    idx = np.arange(mask.sum()) if scope == "statewide" else np.where(reg_nr == scope)[0]
    X, P = X_nr[idx], P_nr[idx]
    for t in TARGETS:
        y = clus[t].to_numpy(float)[mask][idx]
        jobs.append((scope, t, "39 inputs + neighbourhood", "random 70/30", X, P, y, None, SEED))
        for km in BLOCKS_KM:
            jobs.append((scope, t, "39 inputs + neighbourhood", f"spatial {km} km", X, P, y, G[km][mask][idx], SEED))
res50 = pd.DataFrame(Parallel(n_jobs=-1)(delayed(task43)(*j) for j in jobs)).rename(columns={"region": "scope"})
res50.to_csv(RES_DIR / "50_block_size_final.csv", index=False)
say(f"E50 done in {(time.time() - t0) / 60:.1f} min")

# ---------------- E51 (cell 79) ----------------
t0 = time.time()
jobs = []
for name in ["Random Forest", "MLP", "KNN", "LightGBM", "Linear (ridge)"]:
    for t in TARGETS:
        y = clus[t].to_numpy(float)[mask]
        jobs.append((name, t, "spatial 10 km", X_nr, P_nr, y, G_nr, SEED))
        jobs.append((name, t, "random 70/30", X_nr, P_nr, y, None, SEED))
res51 = pd.DataFrame(Parallel(n_jobs=-1)(delayed(task44)(*j) for j in jobs))
res51.to_csv(RES_DIR / "51_model_comparison_final.csv", index=False)
say(f"E51 done in {(time.time() - t0) / 60:.1f} min; CPU s per model: {res51.groupby('model')['sec'].sum().round(0).to_dict()}")

# ---------------- E52 (cell 80) ----------------
t0 = time.time()
jobs = []
for t in TARGETS:
    y = clus[t].to_numpy(float)[mask]
    jobs.append((t, "random 70/30", X_nr, P_nr, y, None, SEED))
    jobs.append((t, "spatial 10 km", X_nr, P_nr, y, G_nr, SEED))
res52 = pd.DataFrame([r for out in Parallel(n_jobs=-1)(delayed(task46)(*j) for j in jobs) for r in out])
res52.to_csv(RES_DIR / "52_shap_final.csv", index=False)
say(f"E52 done in {(time.time() - t0) / 60:.1f} min")

# ---------------- E53 (cell 81) ----------------
t0 = time.time()
SETS53 = {"Full (39 inputs + neighbourhood)": (FEATS, True),
          "Without Sentinel-2 (11 + neighbourhood)": ([f for f in FEATS if f not in BANDS + INDICES], True),
          "Without neighbourhood (39 inputs)": (FEATS, False),
          "Neighbourhood only (4)": ([], True),
          "Sentinel-2 + pH, EC only (30)": (BANDS + INDICES + ["pH", "EC"], False)}
def task53(set_name, target, test, X, P, y, g, seed, cols, use_nb):
    import warnings; warnings.filterwarnings("ignore")
    def fp(tr, te):
        Xtr, Xte = X[tr][:, cols], X[te][:, cols]
        if use_nb:
            Xtr = np.c_[Xtr, nb_features(P[tr], y[tr], P[tr], True)]
            Xte = np.c_[Xte, nb_features(P[tr], y[tr], P[te], False)]
        z = np.log1p(y[tr]); mu, sd = z.mean(), z.std()
        return np.expm1(lgbm(seed).fit(Xtr, (z - mu) / sd).predict(Xte) * sd + mu)
    if g is None:
        tr, te = train_test_split(np.arange(len(y)), test_size=0.30, random_state=seed)
        yy, pp = y[te], fp(tr, te)
    else:
        pp = np.zeros(len(y))
        for a, b in GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, g):
            pp[b] = fp(a, b)
        yy = y
    return {"inputs": set_name, "target": target, "test": test, **metrics(yy, pp)}
jobs = []
for set_name, (feats, use_nb) in SETS53.items():
    cols = [FEATS.index(f) for f in feats]
    for t in TARGETS:
        y = clus[t].to_numpy(float)[mask]
        jobs.append((set_name, t, "random 70/30", X_nr, P_nr, y, None, SEED, cols, use_nb))
        jobs.append((set_name, t, "spatial 10 km", X_nr, P_nr, y, G_nr, SEED, cols, use_nb))
res53 = pd.DataFrame(Parallel(n_jobs=-1)(delayed(task53)(*j) for j in jobs))
res53.to_csv(RES_DIR / "53_input_ablation.csv", index=False)
say(f"E53 done in {(time.time() - t0) / 60:.1f} min")

# ---------------- E54 map (cell 83) and E55 figure (cell 84) ----------------
REG_COLORS = {"Vidarbha": "#2a78d6", "Marathwada": "#eb6834", "North MH": "#1baf7a", "Western MH": "#eda100", "Konkan": "#e87ba4"}
LABEL_POS = {"Konkan": (72.95, 18.75), "Western MH": (75.15, 16.2)}
d = clus[mask]
fig, ax = plt.subplots(figsize=(9, 6.5), constrained_layout=True)
for r in REGIONS:
    s = d[d["region"] == r]
    ax.scatter(s["longitude"], s["latitude"], s=2, c=REG_COLORS[r], alpha=0.6, linewidths=0, label=f"{r} (n = {len(s):,})", rasterized=True)
for r in REGIONS:
    s = d[d["region"] == r]
    x0, y0 = LABEL_POS.get(r, (s["longitude"].median(), s["latitude"].median()))
    ax.text(x0, y0, r, fontsize=11, weight="bold", color="#0b0b0b", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.8))
ax.set_aspect(1 / np.cos(np.deg2rad(d["latitude"].mean()))); ax.set_xlim(72.3, 81.1)
ax.set_xlabel("Longitude (°E)", color="#52514e"); ax.set_ylabel("Latitude (°N)", color="#52514e")
ax.set_title(f"Soil Health Card samples used in this study (n = {len(d):,}; January–May 2024)", fontsize=11, color="#0b0b0b")
ax.legend(markerscale=6, frameon=False, loc="lower right", fontsize=9)
ax.tick_params(colors="#52514e", labelsize=9)
for sp in ax.spines.values(): sp.set_color("#bbbbbb")
lon0, lat0 = d["longitude"].min() + 0.2, d["latitude"].max() - 0.2
dlon = 100 / (111.32 * np.cos(np.deg2rad(lat0)))
ax.plot([lon0, lon0 + dlon], [lat0, lat0], color="#0b0b0b", lw=2)
ax.text(lon0 + dlon / 2, lat0 + 0.08, "100 km", ha="center", fontsize=9, color="#0b0b0b")
ax.annotate("N", xy=(0.96, 0.95), xytext=(0.96, 0.84), xycoords="axes fraction", ha="center", fontsize=11, color="#0b0b0b", arrowprops=dict(arrowstyle="-|>", color="#0b0b0b"))
fig.savefig(RES_DIR / "54_study_area_map.png", dpi=300); plt.close(fig)

r50 = res50
ORDER = ["random 70/30", "spatial 10 km", "spatial 25 km", "spatial 50 km", "spatial 100 km"]
XLAB = ["Random\n70/30", "Spatial\n10 km", "Spatial\n25 km", "Spatial\n50 km", "Spatial\n100 km"]
NUT_COLORS = {"N": "#2a78d6", "P": "#eb6834", "K": "#1baf7a", "OC": "#eda100"}
def end_labels(ax, vals, gap=0.035):
    placed = []
    for t, yv in sorted(vals.items(), key=lambda kv: kv[1]):
        if placed and yv - placed[-1] < gap: yv = placed[-1] + gap
        placed.append(yv); ax.text(4.15, yv, t, color="#0b0b0b", fontsize=10, va="center")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, constrained_layout=True)
for ax, (title, sel) in zip(axes, [("Statewide model", r50["scope"] == "statewide"), ("Regional models (mean of 5 regions)", r50["scope"] != "statewide")]):
    p = r50[sel].pivot_table(index="test", columns="target", values="R2", aggfunc="mean").reindex(ORDER)
    for t in TARGETS:
        ax.plot(range(5), p[t].to_numpy(), color=NUT_COLORS[t], lw=2, marker="o", ms=6, label=t)
    end_labels(ax, {t: p[t].iloc[-1] for t in TARGETS})
    ax.set_xticks(range(5)); ax.set_xticklabels(XLAB, fontsize=9, color="#52514e"); ax.set_xlim(-0.3, 4.6); ax.set_ylim(0, 0.8)
    ax.set_title(title, fontsize=11, color="#0b0b0b"); ax.grid(axis="y", color="#e5e5e5", lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(colors="#52514e", labelsize=9)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color("#bbbbbb")
axes[0].set_ylabel("R²", color="#52514e"); axes[0].legend(frameon=False, ncol=4, loc="upper right", fontsize=9)
fig.savefig(RES_DIR / "55_r2_vs_block_size.png", dpi=300); plt.close(fig)

# ---------------- E56 (cell 85) ----------------
t0 = time.time()
SEEDS = [42, 7, 13, 99, 2024]
jobs = []
for seed in SEEDS:
    for t in TARGETS:
        y = clus[t].to_numpy(float)[mask]
        jobs.append((f"seed {seed}", t, "39 inputs + neighbourhood", "random 70/30", X_nr, P_nr, y, None, seed))
        jobs.append((f"seed {seed}", t, "39 inputs + neighbourhood", "spatial 10 km", X_nr, P_nr, y, G_nr, seed))
res56 = pd.DataFrame(Parallel(n_jobs=-1)(delayed(task43)(*j) for j in jobs)).rename(columns={"region": "seed"})
res56.to_csv(RES_DIR / "56_headline_seeds.csv", index=False)
say(f"E56 done in {(time.time() - t0) / 60:.1f} min")

# ---------------- comparison with the original result files ----------------
say("\n=== Comparison with original files in Start/results/ (max absolute difference of each numeric column) ===")
KEYS = {"49_headline_metrics.csv": ["target", "evaluation"], "50_block_size_final.csv": ["scope", "target", "test"],
        "51_model_comparison_final.csv": ["model", "target", "test"], "52_shap_final.csv": ["target", "test", "input"],
        "53_input_ablation.csv": ["inputs", "target", "test"], "56_headline_seeds.csv": ["seed", "target", "test"]}
summary = []
for f, keys in KEYS.items():
    o = pd.read_csv(ORIG_DIR / f); r = pd.read_csv(RES_DIR / f)
    m = o.merge(r, on=keys, suffixes=("_orig", "_repro"), how="outer", indicator=True)
    unmatched = int((m["_merge"] != "both").sum())
    nums = [c for c in o.columns if c not in keys and pd.api.types.is_numeric_dtype(o[c]) and c != "sec"]
    diffs = {c: float(np.nanmax(np.abs(m[f"{c}_orig"] - m[f"{c}_repro"]))) for c in nums}
    worst = max(diffs.values())
    status = "IDENTICAL" if worst < 1e-9 and unmatched == 0 else ("MATCH (< 1e-6)" if worst < 1e-6 and unmatched == 0 else "DIFFERS")
    summary.append({"file": f, "rows": len(o), "unmatched_rows": unmatched, "max_abs_diff": worst, "status": status, **{f"diff_{c}": v for c, v in diffs.items()}})
    say(f"{f:34s} rows {len(o):>4} | unmatched {unmatched} | max |diff| {worst:.2e} | {status}")
pd.DataFrame(summary).to_csv(RES_DIR / "comparison_with_original.csv", index=False)
say(f"\nTotal run time {(time.time() - T0) / 60:.1f} min. Outputs in {RES_DIR}")
