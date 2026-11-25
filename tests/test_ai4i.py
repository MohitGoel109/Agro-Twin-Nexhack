import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _rep():
    with open(os.path.join(ROOT, "ml", "ai4i_report.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_ai4i_report_is_honest_and_sane():
    r = _rep()
    assert r["rows"] == 10000 and r["failures"] == 339
    assert "NOT that it works on tractors" in r["honest_label"]
    a = r["any_failure"]
    assert a["brier"] < a["brier_base_rate"]  # calibrated better than guessing the base rate
    assert a["f1"] > r["baseline_tool_wear_over_200_min"]["f1"]
    assert "RNF" in r["per_failure_type"] and "TWF" in r["per_failure_type"]  # hard types are reported, not hidden


def test_benchmark_features_and_endpoint_field():
    import pandas as pd
    from ml.benchmark_ai4i import COLS, features
    df = pd.DataFrame([{"Type": "M", "Air temperature [K]": 298.0, "Process temperature [K]": 308.0,
                        "Rotational speed [rpm]": 1500, "Torque [Nm]": 40.0, "Tool wear [min]": 100}]).rename(columns=COLS)
    X = features(df)
    assert abs(X["temp_diff"][0] - 10.0) < 1e-9 and X["q_M"][0] == 1 and X["q_L"][0] == 0
    from ml import bulk_predict
    assert bulk_predict.benchmark()["rows"] == 10000
