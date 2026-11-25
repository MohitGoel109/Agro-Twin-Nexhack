import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from ml.bulk_data import generate_fleet, SYSTEMS


def test_same_seed_same_data_and_different_seed_differs():
    a, b, c = generate_fleet(300, 7), generate_fleet(300, 7), generate_fleet(300, 8)
    pd.testing.assert_frame_equal(a, b)
    assert not a["true_fault"].equals(c["true_fault"]) or not a["hours_since_service"].equals(c["hours_since_service"])


def test_no_machine_in_train_and_test():
    df = generate_fleet(600, 3)
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=3).split(df, groups=df["machine_id"]))
    assert not (set(df["machine_id"].iloc[tr]) & set(df["machine_id"].iloc[te]))
    assert df["machine_id"].is_unique


def test_features_do_not_contain_labels_or_hazards():
    from ml.train_bulk import make_features
    from ml.bulk_data import load_intervals
    X = make_features(generate_fleet(100, 1), load_intervals())
    bad = [c for c in X.columns if c.startswith("hazard_") or "true_fault" in c or "hours_to_failure" in c]
    assert bad == []


def test_report_exists_and_is_honest_and_model_beats_baseline():
    import json
    rep = json.load(open(os.path.join(ROOT, "ml", "bulk_report.json")))
    assert rep["n_train_machines"] >= 1000 and rep["n_test_machines"] >= 300
    assert "SYNTHETIC" in rep["data"].upper() and "not that it is accurate on real" in rep["limitations"]
    # either it beats the fixed-interval baseline, or the report says it does not
    assert rep["beats_baseline_macro_f1"] == (rep["macro"]["f1"] > rep["baseline_fixed_interval"]["macro"]["f1"])
    assert rep["macro"]["f1"] > rep["baseline_fixed_interval"]["macro"]["f1"]


def test_bulk_endpoints():
    sys.path.insert(0, os.path.join(ROOT, "web"))
    from web.app import app
    c = app.test_client()
    r = c.get("/api/checkup/bulk-report").get_json()
    assert r["ok"] and "simulated machines" in r["label"] and "Synthetic" in r["label"]
    mid = c.get("/api/checkup/machines").get_json()["machines"][0]["machine_id"]
    c.post("/api/checkup/%s/submit" % mid, json={"owner": {"hours_since_service": 900, "days_idle_30": 25, "storage": "outdoors"}, "answers": {"sound": ["knocking"]}})
    b = c.get("/api/checkup/%s/bulk-risk" % mid).get_json()
    assert b["ok"] and 0 <= b["p_any_fault"] <= 1 and b["synthetic"] is True and len(b["hours_to_failure_range"]) == 2
    assert c.get("/api/checkup/NOPE/bulk-risk").status_code == 404
