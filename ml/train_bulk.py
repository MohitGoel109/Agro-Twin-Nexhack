"""Train + validate on the BULK SIMULATED fleet (Python 3.9). Uses only numpy, pandas, scikit-learn, joblib.

Split is BY MACHINE ID (GroupShuffleSplit). The test machines are never used for training or for any choice we make.
No hyper-parameter tuning is done, so there is nothing to leak. Compared against a fixed-interval service rule.
Run:  python ml/train_bulk.py --n 5000 --seed 42
Writes: models/bulk_model.joblib, ml/bulk_report.json
"""
import argparse
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import brier_score_loss, confusion_matrix, mean_absolute_error, precision_recall_fscore_support
from sklearn.model_selection import GroupShuffleSplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ml.bulk_data import MACHINE_TYPES, SYSTEMS, STORAGE, WORK, generate_fleet, load_intervals  # noqa: E402

SENSORS = ["engine_temp", "vibration", "oil_pressure", "rpm_variance"]
BASE = {"engine_temp": 82.0, "vibration": 2.0, "oil_pressure": 45.0, "rpm_variance": 15.0}
CLASSES = ["none"] + SYSTEMS


def make_features(df, intervals):
    """Feature table. Uses ONLY what an owner/sensor/farmer could supply: no hazards, no true labels."""
    X = pd.DataFrame(index=df.index)
    for c in ["age_years", "hours_per_week", "hours_this_season", "hours_since_service", "days_idle_30", "fuel_age_months", "dusty"]:
        X[c] = df[c].astype(float)
    for t in MACHINE_TYPES:
        X["type_" + t] = (df["type"] == t).astype(float)
    for s in STORAGE:
        X["storage_" + s] = (df["storage"] == s).astype(float)
    for w in WORK:
        X["work_" + w] = (df["work_type"] == w).astype(float)
    # deviation from the IDEAL: how far past each system's service interval
    for s in SYSTEMS:
        iv = np.array([intervals[t][s] for t in df["type"]])
        X["over_" + s] = df["hours_since_service"].values / iv
    X["idle_over_30pct"] = (df["days_idle_30"] > 9).astype(float)
    for k in SENSORS:
        X[k + "_missing"] = df[k].isna().astype(float)
        X[k + "_dev"] = (df[k].fillna(BASE[k]) - BASE[k])
    for s in SYSTEMS:
        X["sym_" + s] = df["sym_" + s].astype(float)
    X["sym_unsure"] = df["sym_unsure"].astype(float)
    return X


def fixed_interval_rule(df, intervals):
    """Baseline: flag the system most past its interval; 'none' if nothing is past its interval."""
    out = []
    for _, r in df.iterrows():
        ratios = {s: r["hours_since_service"] / intervals[r["type"]][s] for s in SYSTEMS}
        s = max(ratios, key=ratios.get)
        out.append(s if ratios[s] > 1.0 else "none")
    return np.array(out)


def macro(y, p):
    pr, rc, f1, _ = precision_recall_fscore_support(y, p, labels=CLASSES, zero_division=0)
    return float(np.mean(pr)), float(np.mean(rc)), float(np.mean(f1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--test-size", type=float, default=0.3)
    a = ap.parse_args()

    intervals = load_intervals()
    df = generate_fleet(a.n, a.seed)
    X = make_features(df, intervals)
    y = df["true_fault"].values
    hrs = df["hours_to_failure"].values

    gss = GroupShuffleSplit(n_splits=1, test_size=a.test_size, random_state=a.seed)
    tr, te = next(gss.split(X, y, groups=df["machine_id"].values))
    assert not (set(df["machine_id"].iloc[tr]) & set(df["machine_id"].iloc[te])), "machine appears in train and test"

    # no class_weight: re-weighting classes distorts the probabilities (we measured a worse Brier score with it)
    clf = RandomForestClassifier(n_estimators=150, max_depth=12, min_samples_leaf=5, random_state=a.seed, n_jobs=-1)
    clf.fit(X.iloc[tr], y[tr])
    reg = RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=5, random_state=a.seed, n_jobs=-1)
    reg.fit(X.iloc[tr], hrs[tr])

    pred = clf.predict(X.iloc[te])
    proba = clf.predict_proba(X.iloc[te])
    base_pred = fixed_interval_rule(df.iloc[te], intervals)
    yt = y[te]

    p, r, f, _ = precision_recall_fscore_support(yt, pred, labels=CLASSES, zero_division=0)
    per_sys = {c: {"precision": round(float(p[i]), 3), "recall": round(float(r[i]), 3), "f1": round(float(f[i]), 3),
                   "support": int((yt == c).sum())} for i, c in enumerate(CLASSES)}
    mp, mr, mf = macro(yt, pred)
    bp, br, bf = macro(yt, base_pred)

    # calibration: Brier score of P(any fault) and multi-class Brier vs predicting the class frequencies
    idx_none = list(clf.classes_).index("none")
    p_fault = 1.0 - proba[:, idx_none]
    brier_model = float(brier_score_loss((yt != "none").astype(int), p_fault))
    prior = np.mean(y[tr] != "none")
    brier_prior = float(brier_score_loss((yt != "none").astype(int), np.full(len(yt), prior)))
    onehot = np.array([[1.0 if c == t else 0.0 for c in clf.classes_] for t in yt])
    brier_multi = float(np.mean(np.sum((proba - onehot) ** 2, axis=1)))

    hp = reg.predict(X.iloc[te])
    faulty = yt != "none"
    mae_all = float(mean_absolute_error(hrs[te], hp))
    mae_fault = float(mean_absolute_error(hrs[te][faulty], hp[faulty])) if faulty.any() else None
    mae_const = float(mean_absolute_error(hrs[te], np.full(len(te), np.mean(hrs[tr]))))
    mae_fault_const = float(mean_absolute_error(hrs[te][faulty], np.full(int(faulty.sum()), np.mean(hrs[tr])))) if faulty.any() else None

    cm = confusion_matrix(yt, pred, labels=CLASSES).tolist()
    report = {
        "data": "SYNTHETIC: simulated from our own wear-model assumptions. Not real tractor data.",
        "n_machines_total": int(len(df)), "n_train_machines": int(len(tr)), "n_test_machines": int(len(te)),
        "seed": a.seed, "split": "GroupShuffleSplit by machine_id; no tuning on the test set",
        "models": {"fault_by_system": "RandomForestClassifier(150 trees, depth 12)", "hours_to_failure": "RandomForestRegressor(100 trees, depth 12)"},
        "accuracy": round(float(np.mean(pred == yt)), 4),
        "macro": {"precision": round(mp, 3), "recall": round(mr, 3), "f1": round(mf, 3)},
        "baseline_fixed_interval": {"accuracy": round(float(np.mean(base_pred == yt)), 4),
                                    "macro": {"precision": round(bp, 3), "recall": round(br, 3), "f1": round(bf, 3)}},
        "beats_baseline_macro_f1": bool(mf > bf),
        "per_system": per_sys, "labels": CLASSES, "confusion_matrix": cm,
        "hours_to_failure_mae": {"all_test_machines": round(mae_all, 1), "faulty_machines_only": None if mae_fault is None else round(mae_fault, 1),
                                 "baseline_predict_mean_all": round(mae_const, 1),
                                 "baseline_predict_mean_faulty": None if mae_fault_const is None else round(mae_fault_const, 1)},
        "brier_any_fault": {"model": round(brier_model, 4), "baseline_prior_only": round(brier_prior, 4)},
        "brier_multiclass": round(brier_multi, 4),
        "limitations": ("The data is generated from our own assumptions, so high scores show the method works, not that it is accurate on "
                        "real tractors. Next step: validate on real pilot-pool logs."),
    }
    os.makedirs(os.path.join(ROOT, "models"), exist_ok=True)
    joblib.dump({"clf": clf, "reg": reg, "features": list(X.columns), "classes": list(clf.classes_), "intervals": intervals,
                 "n_train_machines": int(len(tr)), "n_test_machines": int(len(te)), "synthetic": True}, os.path.join(ROOT, "models", "bulk_model.joblib"), compress=3)
    with open(os.path.join(ROOT, "ml", "bulk_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print("BULK TRAINING (SYNTHETIC DATA) seed=%d" % a.seed)
    print("train machines: %d | test machines: %d (split by machine id)" % (len(tr), len(te)))
    print("%-28s %10s %10s" % ("metric (held-out)", "model", "baseline"))
    print("%-28s %10.3f %10.3f" % ("accuracy", report["accuracy"], report["baseline_fixed_interval"]["accuracy"]))
    print("%-28s %10.3f %10.3f" % ("macro precision", mp, bp))
    print("%-28s %10.3f %10.3f" % ("macro recall", mr, br))
    print("%-28s %10.3f %10.3f" % ("macro F1", mf, bf))
    print("%-28s %10.1f %10.1f" % ("hours-to-failure MAE (all)", mae_all, mae_const))
    print("%-28s %10.4f %10.4f" % ("Brier any-fault", brier_model, brier_prior))
    print("model beats fixed-interval baseline on macro F1: %s" % report["beats_baseline_macro_f1"])


if __name__ == "__main__":
    main()
