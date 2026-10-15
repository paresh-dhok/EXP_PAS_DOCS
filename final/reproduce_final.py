"""reproduce_final.py - final dataset and all essential results of the paper (correction sprint, 2026-10-15).

Standalone: needs only the parquet files in Start/. Writes everything to Start/results_final/.
    python reproduce_final.py

Final dataset (F00):
    mh_model_dataset (33,877; D07: bare-soil Sentinel-2 3x3 window within +-3 days, impossible values removed)
    - Raigad district (code 491; district-level laboratory offset, E47/E48)
    - samples in 30 m clusters of > 10 samples (placeholder GPS, D08 rule)
    - samples whose elevation/climate source location is > 100 m away
Design changes against E49-E56 (all reported in F07):
    * random 70/30 split grouped by 30 m site (co-located samples never split between training and test);
      the ungrouped random split is kept as a reference row;
    * spatial blocks assigned by site centroid (a site never straddles two folds);
    * LRS features: 10 nearest training samples from OTHER sites (own site excluded, incl. the sample itself).
"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from pathlib import Path
from joblib import Parallel, delayed
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, train_test_split
from sklearn.metrics import r2_score

ROOT = Path(r"D:\SEM 7\CAPSTONE\DATA\slusi\Start")
OUT = ROOT / "results_final"; OUT.mkdir(exist_ok=True)
LOG = open(OUT / "run_log.txt", "w", encoding="utf-8")
def say(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n"); LOG.flush(); sys.stdout.flush()

BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI",
           "R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
CLIMATE = ["ppt_annual", "ppt_monsoon", "tmax_mean", "tmin_mean", "tmean", "def_annual"]
FEATS   = BANDS + INDICES + ["pH", "EC"] + ["elev"] + CLIMATE + ["longitude", "latitude"]
TARGETS = ["N", "P", "K", "OC"]
REGIONS = ["Vidarbha", "Marathwada", "North MH", "Western MH", "Konkan"]
SEEDS   = [42, 7, 13, 99, 2024]
BLOCKS  = [10, 25, 50, 100]
K_LRS, CLUSTER_M, MAX_SITE = 10, 30.0, 10

def xy(lon, lat):
    la = np.deg2rad(lat); return np.c_[lon * 111320 * np.cos(la), lat * 110574]

# ======================= F00 final dataset =======================
t_all = time.time()
reg  = pd.read_parquet(ROOT / "mh_candidates.parquet", columns=["id", "region"])
raw  = pd.read_parquet(ROOT / "mh_model_dataset.parquet").merge(reg, on="id", how="left")
dec  = pd.read_parquet(ROOT / "mh_final_dataset.parquet")
ctx  = (pd.read_parquet(ROOT / "mh_terrain.parquet").merge(pd.read_parquet(ROOT / "mh_climate.parquet"), on="id")
          .merge(dec[["id", "longitude", "latitude"]], on="id"))
dist, nn = cKDTree(xy(ctx.longitude.values, ctx.latitude.values)).query(xy(raw.longitude.values, raw.latitude.values))
for c in ["elev"] + CLIMATE:
    raw[c] = ctx[c].to_numpy()[nn]
raw["context_dist_m"] = dist
raw["district"] = raw["id"].str.split("_").str[1]
counts = [("mh_model_dataset (D07 output)", len(raw))]
d = raw[raw["district"] != "491"].reset_index(drop=True); counts.append(("minus Raigad (491)", len(d)))
P0 = xy(d.longitude.values, d.latitude.values)
pr = cKDTree(P0).query_pairs(CLUSTER_M, output_type="ndarray")
_, lab = connected_components(coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(len(d), len(d))), directed=False)
d["site_size"] = np.bincount(lab)[lab]
d = d[d["site_size"] <= MAX_SITE].reset_index(drop=True); counts.append(("minus samples in 30 m clusters > 10 (placeholder GPS)", len(d)))
d = d[d["context_dist_m"] <= 100].reset_index(drop=True); counts.append(("minus elevation/climate source > 100 m away", len(d)))
# recompute sites on the final set
P = xy(d.longitude.values, d.latitude.values)
pr = cKDTree(P).query_pairs(CLUSTER_M, output_type="ndarray")
_, site = connected_components(coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(len(d), len(d))), directed=False)
d["site"] = site
cent = pd.DataFrame(P, columns=["x", "y"]).groupby(site).transform("mean").to_numpy()   # site centroid per sample
def blocks(km, idx=None):
    c = cent if idx is None else cent[idx]; s = km * 1000
    return pd.Series([f"{a}_{b}" for a, b in zip((c[:, 0] // s).astype(int), (c[:, 1] // s).astype(int))]).factorize()[0]
say("=== F00 final dataset ===")
for k, v in counts: say(f"{k:60s} {v:>7,}")
ss = d.groupby("site").size()
say(f"sites (30 m clusters) {len(ss):,}: single-sample {int((ss == 1).sum()):,}; multi-sample {int((ss > 1).sum()):,} holding {int(ss[ss > 1].sum()):,} samples")
say("per region:", d["region"].value_counts().reindex(REGIONS).to_dict())
say("elevation/climate source distance (m): median {:.0f}, 95% {:.0f}, max {:.0f}".format(*np.percentile(d.context_dist_m, [50, 95, 100])))
say("target summary:\n" + d[TARGETS].describe().T[["mean", "std", "min", "25%", "50%", "75%", "max"]].round(3).to_string())
pd.DataFrame(counts, columns=["step", "samples"]).to_csv(OUT / "F00_dataset_counts.csv", index=False)
d[["id", "district", "region", "longitude", "latitude", "site", "site_size", "context_dist_m"] + TARGETS].to_parquet(OUT / "F00_final_dataset_ids.parquet", index=False)
X = d[FEATS].to_numpy(float); G = d["site"].to_numpy(); R = d["region"].to_numpy()

# ======================= helpers =======================
def lgbm(seed):
    from lightgbm import LGBMRegressor
    return LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=15, min_child_samples=20, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.5, reg_lambda=5.0, n_jobs=1, random_state=seed, verbose=-1)
def make_model(name, seed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.neural_network import MLPRegressor
    from sklearn.ensemble import RandomForestRegressor
    if name == "Ridge regression": return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == "k-nearest neighbours": return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=15, weights="distance"))
    if name == "Multilayer perceptron": return make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(64, 32), alpha=1e-3, max_iter=200, early_stopping=True, random_state=seed))
    if name == "Random forest": return RandomForestRegressor(n_estimators=100, min_samples_leaf=5, max_features=0.33, n_jobs=1, random_state=seed)
    return lgbm(seed)
def lrs(Ptr, ytr, gtr, Pq, gq, mode):
    """Local reference sample features from training points only. mode 'site': exclude own site; 'self': exclude row itself (E49 rule); 'none': test rows."""
    k = K_LRS + (MAX_SITE if mode == "site" else 1 if mode == "self" else 0)
    dd, ii = cKDTree(Ptr).query(Pq, k=k)
    if mode == "site":
        bad = gtr[ii] == gq[:, None]
        order = np.argsort(bad, axis=1, kind="stable")[:, :K_LRS]
        dd, ii = np.take_along_axis(dd, order, 1), np.take_along_axis(ii, order, 1)
    elif mode == "self":
        dd, ii = dd[:, 1:], ii[:, 1:]
    w = 1 / np.maximum(dd, 1.0); v = np.log1p(ytr)[ii]
    return np.c_[(w * v).sum(1) / w.sum(1), v[:, 0], np.log1p(dd[:, 0]), v.std(1)]
def fit_predict(Xs, Ps, y, g, tr, te, seed, model="LightGBM", use_lrs=True, mode="site", cols=None, contrib=False):
    Xtr, Xte = (Xs[tr], Xs[te]) if cols is None else (Xs[tr][:, cols], Xs[te][:, cols])
    if use_lrs:
        Xtr = np.c_[Xtr, lrs(Ps[tr], y[tr], g[tr], Ps[tr], g[tr], mode)]
        Xte = np.c_[Xte, lrs(Ps[tr], y[tr], g[tr], Ps[te], g[te], "site" if mode == "site" else "none")]
    z = np.log1p(y[tr]); mu, sd = z.mean(), z.std()
    m = make_model(model, seed).fit(Xtr, (z - mu) / sd)
    pz = np.clip(m.predict(Xte) * sd + mu, z.min(), z.max())
    out = np.expm1(pz)
    if contrib:
        return out, np.abs(m.predict(Xte, pred_contrib=True)[:, :-1])
    return out
def metrics(y, p):
    e = p - y; rmse = np.sqrt(np.mean(e ** 2))
    return {"n": len(y), "R2": r2_score(y, p), "RMSE": rmse, "MAE": np.mean(np.abs(e)), "bias": e.mean(),
            "RPIQ": (np.percentile(y, 75) - np.percentile(y, 25)) / rmse}
def splits(design, n, g, seed, idx=None):
    """design: 'random' (ungrouped), 'random_site' (grouped by 30 m site), or block size in km."""
    if design == "random":
        return [train_test_split(np.arange(n), test_size=0.30, random_state=seed)]
    if design == "random_site":
        return [next(GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=seed).split(np.zeros(n), groups=g))]
    return list(GroupKFold(n_splits=5, shuffle=True, random_state=seed).split(np.zeros(n), groups=blocks(design, idx)))
def evaluate(design, idx, t, seed, model="LightGBM", use_lrs=True, cols=None, keep=False, contrib=False):
    import warnings; warnings.filterwarnings("ignore")
    Xs, Ps, gs, y = X[idx], P[idx], G[idx], d[t].to_numpy(float)[idx]
    mode = "self" if design == "random" else "site"
    yy, pp, ss = [], [], []
    for tr, te in splits(design, len(idx), gs, seed, idx):
        r = fit_predict(Xs, Ps, y, gs, tr, te, seed, model, use_lrs, mode, cols, contrib)
        if contrib: r, s = r; ss.append(s)
        yy.append(y[te]); pp.append(r)
    yy, pp = np.concatenate(yy), np.concatenate(pp)
    res = metrics(yy, pp)
    if contrib: res["shap"] = np.vstack(ss).mean(0)
    if keep: res["yy"], res["pp"] = yy, pp
    return res
ALL = np.arange(len(d))
DES_NAME = {"random": "random 70/30 (ungrouped, reference)", "random_site": "random 70/30 grouped by site", 10: "spatial 10 km", 25: "spatial 25 km", 50: "spatial 50 km", 100: "spatial 100 km"}
def run(jobs):
    return Parallel(n_jobs=-1)(delayed(evaluate)(*j[0], **j[1]) for j in jobs)

# ======================= F01 headline, 5 seeds =======================
t0 = time.time()
designs = ["random", "random_site", 10]
jobs = [((dz, ALL, t, s), {"keep": s == 42}) for dz in designs for t in TARGETS for s in SEEDS]
out = run(jobs)
rows = [{"design": DES_NAME[j[0][0]], "target": j[0][2], "seed": j[0][3], **{k: v for k, v in o.items() if k not in ("yy", "pp")}} for j, o in zip(jobs, out)]
f01 = pd.DataFrame(rows); f01.to_csv(OUT / "F01_headline_5seeds.csv", index=False)
summ = f01.groupby(["design", "target"])[["R2", "RMSE", "MAE", "bias", "RPIQ"]].agg(["mean", "std"]).round(3)
summ.to_csv(OUT / "F01_headline_summary.csv")
say(f"\n=== F01 headline, LightGBM, 39 inputs + LRS, mean (sd) over 5 seeds  [{(time.time() - t0) / 60:.1f} min] ===")
for dz in designs:
    s = f01[f01.design == DES_NAME[dz]].groupby("target")[["R2", "RMSE", "MAE"]].agg(["mean", "std"]).reindex(TARGETS)
    say(f"-- {DES_NAME[dz]} (n test per seed ~{int(f01[f01.design == DES_NAME[dz]].n.mean()):,})")
    say("   R2   " + "  ".join(f"{t} {s.loc[t, ('R2', 'mean')]:.3f}±{s.loc[t, ('R2', 'std')]:.3f}" for t in TARGETS))
    say("   RMSE " + "  ".join(f"{t} {s.loc[t, ('RMSE', 'mean')]:.3g}" for t in TARGETS) + " | MAE " + "  ".join(f"{t} {s.loc[t, ('MAE', 'mean')]:.3g}" for t in TARGETS))
keep42 = {(j[0][0], j[0][2]): o for j, o in zip(jobs, out) if j[0][3] == 42}

# ======================= F02 block sizes, statewide + regions (seed 42) =======================
t0 = time.time()
scopes = [("statewide", ALL)] + [(r, np.where(R == r)[0]) for r in REGIONS]
jobs = [((dz, idx, t, 42), {}) for sc, idx in scopes for dz in ["random_site"] + BLOCKS for t in TARGETS]
labels = [(sc, dz, t) for sc, idx in scopes for dz in ["random_site"] + BLOCKS for t in TARGETS]
out = run(jobs)
f02 = pd.DataFrame([{"scope": sc, "design": DES_NAME[dz], "target": t, **o} for (sc, dz, t), o in zip(labels, out)])
f02.to_csv(OUT / "F02_block_size_statewide_regions.csv", index=False)
ORD = [DES_NAME[x] for x in ["random_site"] + BLOCKS]
say(f"\n=== F02 R2 by validation design, seed 42  [{(time.time() - t0) / 60:.1f} min] ===")
say("statewide:\n" + f02[f02.scope == "statewide"].pivot_table(index="design", columns="target", values="R2").reindex(ORD)[TARGETS].round(3).to_string())
say("mean of 5 regional models:\n" + f02[f02.scope != "statewide"].pivot_table(index="design", columns="target", values="R2", aggfunc="mean").reindex(ORD)[TARGETS].round(3).to_string())
for t in TARGETS:
    say(f"{t} per region:\n" + f02[(f02.scope != "statewide") & (f02.target == t)].pivot_table(index="scope", columns="design", values="R2").reindex(REGIONS)[ORD].round(3).to_string())
say("blocks statewide: " + ", ".join(f"{km} km {blocks(km).max() + 1}" for km in BLOCKS))

# ======================= F03 train-test distances (seed 42) =======================
rows = []
for dz in ["random", "random_site"] + BLOCKS:
    dd = np.zeros(0)
    for tr, te in splits(dz, len(d), G, 42):
        dd = np.r_[dd, cKDTree(P[tr]).query(P[te])[0]]
    q = np.percentile(dd, [5, 25, 50, 75, 95])
    rows.append({"design": DES_NAME[dz], "test samples": len(dd), "p5_m": q[0], "p25_m": q[1], "median_m": q[2], "p75_m": q[3], "p95_m": q[4],
                 "share_le_30m": np.mean(dd <= 30), "share_le_100m": np.mean(dd <= 100), "share_le_1km": np.mean(dd <= 1000), "share_le_5km": np.mean(dd <= 5000)})
f03 = pd.DataFrame(rows); f03.to_csv(OUT / "F03_train_test_distances.csv", index=False)
say("\n=== F03 distance from each test sample to its nearest training sample (seed 42) ===\n" + f03.round(3).to_string(index=False))

# ======================= F04 five models (seed 42) =======================
t0 = time.time()
MODELS = ["Random forest", "Multilayer perceptron", "k-nearest neighbours", "LightGBM", "Ridge regression"]
jobs = [((dz, ALL, t, 42), {"model": m}) for m in MODELS for dz in ["random_site", 10] for t in TARGETS]
labels = [(m, dz, t) for m in MODELS for dz in ["random_site", 10] for t in TARGETS]
out = run(jobs)
f04 = pd.DataFrame([{"model": m, "design": DES_NAME[dz], "target": t, **o} for (m, dz, t), o in zip(labels, out)])
f04.to_csv(OUT / "F04_five_models.csv", index=False)
say(f"\n=== F04 five models, R2 (seed 42)  [{(time.time() - t0) / 60:.1f} min] ===")
for dz in ["random_site", 10]:
    say(f"-- {DES_NAME[dz]}:\n" + f04[f04.design == DES_NAME[dz]].pivot_table(index="model", columns="target", values="R2").reindex(MODELS)[TARGETS].round(3).to_string())

# ======================= F05 input ablation (seed 42) =======================
SETS = {"All (39 + LRS)": (FEATS, True), "Without Sentinel-2 (11 + LRS)": ([f for f in FEATS if f not in BANDS + INDICES], True),
        "Without LRS (39)": (FEATS, False), "LRS only (4)": ([], True), "Sentinel-2 + pH, EC only (30)": (BANDS + INDICES + ["pH", "EC"], False)}
jobs, labels = [], []
for sname, (fs, use) in SETS.items():
    cols = [FEATS.index(f) for f in fs]
    for dz in ["random_site", 10]:
        for t in TARGETS:
            jobs.append(((dz, ALL, t, 42), {"use_lrs": use, "cols": cols})); labels.append((sname, dz, t))
out = run(jobs)
f05 = pd.DataFrame([{"inputs": s, "design": DES_NAME[dz], "target": t, **o} for (s, dz, t), o in zip(labels, out)])
f05.to_csv(OUT / "F05_input_ablation.csv", index=False)
say("\n=== F05 input ablation, R2 (seed 42) ===")
for dz in ["random_site", 10]:
    say(f"-- {DES_NAME[dz]}:\n" + f05[f05.design == DES_NAME[dz]].pivot_table(index="inputs", columns="target", values="R2").reindex(list(SETS))[TARGETS].round(3).to_string())

# ======================= F06 SHAP by input group (seed 42) =======================
NAMES = FEATS + ["lrs_idw_mean", "lrs_nearest_value", "lrs_nearest_dist", "lrs_sd"]
GROUPS = {"LRS features (4)": NAMES[-4:], "Climate (6)": CLIMATE, "Coordinates (2)": ["longitude", "latitude"],
          "Sentinel-2 bands (12)": BANDS, "Spectral indices (16)": INDICES, "pH, EC (2)": ["pH", "EC"], "Elevation (1)": ["elev"]}
jobs = [((dz, ALL, t, 42), {"contrib": True}) for dz in ["random_site", 10] for t in TARGETS]
out = run(jobs)
rows = []
for j, o in zip(jobs, out):
    sh = o["shap"]; share = 100 * sh / sh.sum()
    for gname, names in GROUPS.items():
        rows.append({"design": DES_NAME[j[0][0]], "target": j[0][2], "group": gname, "share_pct": share[[NAMES.index(n) for n in names]].sum()})
f06 = pd.DataFrame(rows); f06.to_csv(OUT / "F06_shap_groups.csv", index=False)
say("\n=== F06 SHAP share by input group (%), seed 42 ===")
for dz in ["random_site", 10]:
    say(f"-- {DES_NAME[dz]}:\n" + f06[f06.design == DES_NAME[dz]].pivot_table(index="group", columns="target", values="share_pct").reindex(list(GROUPS))[TARGETS].round(1).to_string())

# ======================= F07 old vs final =======================
old49 = pd.read_csv(ROOT / "results" / "49_headline_metrics.csv")
old56 = pd.read_csv(ROOT / "results" / "56_headline_seeds.csv")
old50 = pd.read_csv(ROOT / "results" / "50_block_size_final.csv")
rows = []
def add(label, data, design, vals):
    rows.append({"version": label, "data": data, "design": design, **{t: round(v, 3) for t, v in zip(TARGETS, vals)}})
o56 = old56.groupby(["test", "target"])["R2"].mean()
add("old (E56, 5-seed mean)", "32,096", "random 70/30 (ungrouped)", [o56[("random 70/30", t)] for t in TARGETS])
add("old (E56, 5-seed mean)", "32,096", "spatial 10 km", [o56[("spatial 10 km", t)] for t in TARGETS])
f01m = f01.groupby(["design", "target"])["R2"].mean()
nf = f"{len(d):,}"
add("final (F01, 5-seed mean)", nf, "random 70/30 (ungrouped, reference)", [f01m[(DES_NAME['random'], t)] for t in TARGETS])
add("final (F01, 5-seed mean)", nf, "random 70/30 grouped by site", [f01m[(DES_NAME['random_site'], t)] for t in TARGETS])
add("final (F01, 5-seed mean)", nf, "spatial 10 km", [f01m[(DES_NAME[10], t)] for t in TARGETS])
o50 = old50[old50.scope == "statewide"].set_index(["test", "target"])["R2_spatial_10km" if "R2_spatial_10km" in old50 else "R2"]
for km in [25, 50, 100]:
    add("old (E50, seed 42)", "32,096", f"spatial {km} km", [o50[(f"spatial {km} km", t)] for t in TARGETS])
    add("final (F02, seed 42)", nf, f"spatial {km} km", [f02[(f02.scope == "statewide") & (f02.design == DES_NAME[km]) & (f02.target == t)].R2.iat[0] for t in TARGETS])
f07 = pd.DataFrame(rows); f07.to_csv(OUT / "F07_old_vs_final.csv", index=False)
say("\n=== F07 old vs final, R2 ===\n" + f07.to_string(index=False))

# ======================= figures =======================
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
UNITS = {"N": "kg/ha", "P": "kg/ha", "K": "kg/ha", "OC": "%"}
fig, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
for j, t in enumerate(TARGETS):
    for i, dz in enumerate(["random_site", 10]):
        o = keep42[(dz, t)]; yy, pp = o["yy"], o["pp"]; ax = axes[i, j]
        hi = np.percentile(np.r_[yy, pp], 99.5)
        ax.hexbin(yy, pp, gridsize=45, extent=(0, hi, 0, hi), bins="log", mincnt=1, cmap="Blues", linewidths=0)
        ax.plot([0, hi], [0, hi], color="#6b6b6b", lw=1, ls="--"); ax.set_xlim(0, hi); ax.set_ylim(0, hi); ax.set_aspect("equal")
        ax.text(0.04, 0.96, f"R² = {o['R2']:.2f}\nRMSE = {o['RMSE']:.3g}\nn = {o['n']:,}", transform=ax.transAxes, va="top", fontsize=9, color="#2b2b2b")
        ax.set_title(f"{t} ({UNITS[t]}) – {'Random 70/30 (grouped by site)' if dz == 'random_site' else 'Spatial 10 km CV'}", fontsize=10, color="#2b2b2b")
        ax.set_xlabel("Measured", fontsize=9, color="#555555"); ax.set_ylabel("Predicted", fontsize=9, color="#555555"); ax.tick_params(labelsize=8, colors="#555555")
        for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)
        for s_ in ["left", "bottom"]: ax.spines[s_].set_color("#bbbbbb")
fig.savefig(OUT / "Fig3_measured_vs_predicted.png", dpi=300); plt.close(fig)

XLAB = ["Random\n70/30*", "Spatial\n10 km", "Spatial\n25 km", "Spatial\n50 km", "Spatial\n100 km"]
COL = {"N": "#2a78d6", "P": "#eb6834", "K": "#1baf7a", "OC": "#eda100"}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, constrained_layout=True)
for ax, (title, sel) in zip(axes, [("Statewide model", f02.scope == "statewide"), ("Regional models (mean of 5 regions)", f02.scope != "statewide")]):
    p = f02[sel].pivot_table(index="design", columns="target", values="R2", aggfunc="mean").reindex(ORD)
    placed = []
    for t in TARGETS:
        ax.plot(range(5), p[t].to_numpy(), color=COL[t], lw=2, marker="o", ms=6, label=t)
    for t, yv in sorted({t: p[t].iloc[-1] for t in TARGETS}.items(), key=lambda kv: kv[1]):
        if placed and yv - placed[-1] < 0.035: yv = placed[-1] + 0.035
        placed.append(yv); ax.text(4.15, yv, t, color="#0b0b0b", fontsize=10, va="center")
    ax.set_xticks(range(5)); ax.set_xticklabels(XLAB, fontsize=9, color="#52514e"); ax.set_xlim(-0.3, 4.6)
    ax.set_ylim(min(0, np.nanmin(p.values) - 0.05), 0.8)
    ax.set_title(title, fontsize=11); ax.grid(axis="y", color="#e5e5e5", lw=0.8); ax.set_axisbelow(True)
    ax.axhline(0, color="#bbbbbb", lw=0.8)
    for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)
    for s_ in ["left", "bottom"]: ax.spines[s_].set_color("#bbbbbb")
axes[0].set_ylabel("R²"); axes[0].legend(frameon=False, ncol=4, loc="upper right", fontsize=9)
fig.supxlabel("* Random 70/30 split grouped by 30 m site", fontsize=8, color="#52514e")
fig.savefig(OUT / "Fig4_r2_vs_block_size.png", dpi=300); plt.close(fig)

REGC = {"Vidarbha": "#2a78d6", "Marathwada": "#eb6834", "North MH": "#1baf7a", "Western MH": "#eda100", "Konkan": "#e87ba4"}
LBL = {"Konkan": (72.95, 18.75), "Western MH": (75.15, 16.2)}
fig, ax = plt.subplots(figsize=(9, 6.5), constrained_layout=True)
for r in REGIONS:
    s = d[d.region == r]; ax.scatter(s.longitude, s.latitude, s=2, c=REGC[r], alpha=0.6, linewidths=0, label=f"{r} (n = {len(s):,})", rasterized=True)
for r in REGIONS:
    s = d[d.region == r]; x0, y0 = LBL.get(r, (s.longitude.median(), s.latitude.median()))
    ax.text(x0, y0, r, fontsize=11, weight="bold", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.8))
ax.set_aspect(1 / np.cos(np.deg2rad(d.latitude.mean()))); ax.set_xlim(72.3, 81.1)
ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.set_title(f"Soil Health Card samples used in this study (n = {len(d):,}; January–May 2024)", fontsize=11)
ax.legend(markerscale=6, frameon=False, loc="lower right", fontsize=9)
lon0, lat0 = d.longitude.min() + 0.2, d.latitude.max() - 0.2; dl = 100 / (111.32 * np.cos(np.deg2rad(lat0)))
ax.plot([lon0, lon0 + dl], [lat0, lat0], color="k", lw=2); ax.text(lon0 + dl / 2, lat0 + 0.08, "100 km", ha="center", fontsize=9)
ax.annotate("N", xy=(0.96, 0.95), xytext=(0.96, 0.84), xycoords="axes fraction", ha="center", fontsize=11, arrowprops=dict(arrowstyle="-|>", color="k"))
fig.savefig(OUT / "Fig1_study_area_map.png", dpi=300); plt.close(fig)
say(f"\nAll done in {(time.time() - t_all) / 60:.1f} min. Outputs in {OUT}")
