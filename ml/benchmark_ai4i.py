"""Public benchmark on the UCI AI4I 2020 Predictive Maintenance dataset (10,000 rows, milling machines, itself synthetic).

This proves the METHOD (Random Forest on sensor snapshots) on a public dataset. It does NOT prove accuracy on tractors,
and it only tests the sensor side, not the farmer check-up.

Usage:  python ml/benchmark_ai4i.py [path/to/ai4i2020.csv]      (default: data/ai4i2020.csv, not committed to git)
Writes: ml/ai4i_report.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 42
TYPES = {"TWF": "tool wear failure", "HDF": "heat dissipation failure", "PWF": "power failure",
         "OSF": "overstrain failure", "RNF": "random failure (unpredictable by design)"}
COLS = {"Air temperature [K]": "air_k", "Process temperature [K]": "proc_k", "Rotational speed [rpm]": "rpm",
        "Torque [Nm]": "torque", "Tool wear [min]": "wear"}


def features(df):
    X = df[list(COLS.values())].copy()
    X["temp_diff"] = X["proc_k"] - X["air_k"]
    X["power_w"] = X["torque"] * X["rpm"] * 2 * np.pi / 60.0
    X["strain"] = X["torque"] * X["wear"]
    for t in ("L", "M", "H"):
        X["q_" + t] = (df["Type"] == t).astype(int)
    return X


def _forest():
    # no class weighting: it ruined probability calibration in the first bulk run
    return RandomForestClassifier(n_estimators=200, min_samples_leaf=3, random_state=SEED, n_jobs=-1)


def _scores(y, pred):
    return {"precision": round(float(precision_score(y, pred, zero_division=0)), 3),
            "recall": round(float(recall_score(y, pred, zero_division=0)), 3),
            "f1": round(float(f1_score(y, pred, zero_division=0)), 3)}


def run(path):
    df = pd.read_csv(path, encoding="utf-8-sig").rename(columns=COLS)
    need = list(COLS.values()) + ["Type", "Machine failure"] + list(TYPES)
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit("CSV is missing columns: %s" % missing)
    df = df.drop_duplicates(subset=["UDI"]) if "UDI" in df.columns else df
    X = features(df)
    idx_train, idx_test = train_test_split(df.index, test_size=0.30, random_state=SEED, stratify=df["Machine failure"])
    Xtr, Xte = X.loc[idx_train], X.loc[idx_test]
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)

    def evaluate(label):
        ytr, yte = df.loc[idx_train, label].values, df.loc[idx_test, label].values
        if ytr.sum() < 5 or yte.sum() < 1:
            return {"support_test": int(yte.sum()), "note": "too few cases to evaluate"}
        # decision threshold chosen on TRAIN only (out-of-fold), never on the test rows
        oof = cross_val_predict(_forest(), Xtr, ytr, cv=cv, method="predict_proba")[:, 1]
        grid = np.linspace(0.05, 0.9, 35)
        thr = float(grid[int(np.argmax([f1_score(ytr, oof >= g, zero_division=0) for g in grid]))])
        model = _forest().fit(Xtr, ytr)
        p = model.predict_proba(Xte)[:, 1]
        out = {"support_test": int(yte.sum()), "threshold": round(thr, 2), **_scores(yte, p >= thr),
               "roc_auc": round(float(roc_auc_score(yte, p)), 3),
               "brier": round(float(brier_score_loss(yte, p)), 4),
               "brier_base_rate": round(float(brier_score_loss(yte, np.full(len(yte), ytr.mean()))), 4)}
        return out, model, p

    any_out, any_model, any_p = evaluate("Machine failure")
    yte = df.loc[idx_test, "Machine failure"].values
    rule = (df.loc[idx_test, "wear"].values > 200).astype(int)
    per_type = {}
    for t, desc in TYPES.items():
        r = evaluate(t)
        per_type[t] = {"meaning": desc, **(r[0] if isinstance(r, tuple) else r)}
    imp = sorted(zip(X.columns, any_model.feature_importances_), key=lambda kv: -kv[1])[:5]
    return {
        "dataset": "UCI AI4I 2020 Predictive Maintenance (milling machines; itself synthetic)",
        "honest_label": "DIFFERENT MACHINE TYPE and synthetic. Shows the method works on a public benchmark, NOT that it works on tractors.",
        "rows": int(len(df)), "failures": int(df["Machine failure"].sum()),
        "failure_rate": round(float(df["Machine failure"].mean()), 4),
        "split": "70% train / 30% test, stratified, seed 42. Each row is a different machine, so no machine appears in both. "
                 "Decision threshold chosen by 5-fold CV on train only.",
        "features_note": "Raw sensors plus temperature difference, mechanical power and torque x wear. These engineered "
                         "features follow the physics the dataset was generated from.",
        "any_failure": any_out,
        "baseline_tool_wear_over_200_min": _scores(yte, rule),
        "per_failure_type": per_type,
        "top_features": [{"feature": f, "importance": round(float(v), 3)} for f, v in imp],
        "not_tested": ["No owner-form fields or farmer symptoms in this dataset (check-up not tested).",
                       "No time-to-failure column (no hours-left prediction).",
                       "Random failures (RNF) are noise by design and are reported, not hidden."],
    }


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "ai4i2020.csv")
    if not os.path.exists(path):
        raise SystemExit("Dataset not found: %s\nDownload ai4i2020.csv (UCI) and put it in data/ (not committed)." % path)
    rep = run(path)
    with open(os.path.join(ROOT, "ml", "ai4i_report.json"), "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=2)
    a = rep["any_failure"]
    print("AI4I any-failure: precision %.2f recall %.2f F1 %.2f AUC %.3f Brier %.4f (base-rate %.4f)" % (
        a["precision"], a["recall"], a["f1"], a["roc_auc"], a["brier"], a["brier_base_rate"]))
    b = rep["baseline_tool_wear_over_200_min"]
    print("Rule 'tool wear > 200 min': precision %.2f recall %.2f F1 %.2f" % (b["precision"], b["recall"], b["f1"]))
    for t, v in rep["per_failure_type"].items():
        print("  %s (%d test cases): %s" % (t, v.get("support_test", 0), {k: v[k] for k in ("precision", "recall", "f1") if k in v}))
