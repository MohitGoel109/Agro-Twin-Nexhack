"""Use the bulk-trained model (models/bulk_model.joblib) for one machine. Returns None if the model is missing or
cannot be loaded (for example a different scikit-learn version), so the site keeps working without it."""
import json
import logging
import os
import pickle

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHE = {}
_LOG = logging.getLogger(__name__)


def report():
    try:
        with open(os.path.join(ROOT, "ml", "bulk_report.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        _LOG.warning("Bulk model report is missing; train it with python ml/train_bulk.py")
        return None


def benchmark():
    """Public AI4I benchmark report (ml/ai4i_report.json) or None."""
    try:
        with open(os.path.join(ROOT, "ml", "ai4i_report.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        _LOG.warning("AI4I benchmark report is missing; benchmark details are unavailable")
        return None


def _model():
    if "m" not in _CACHE:
        try:
            import joblib
            _CACHE["m"] = joblib.load(os.path.join(ROOT, "models", "bulk_model.joblib"))
        except (FileNotFoundError, ImportError, AttributeError, ValueError, EOFError, OSError,
                TypeError, KeyError, IndexError, pickle.UnpicklingError) as exc:
            _LOG.warning("Bulk model could not be loaded; model-derived risk is unavailable: %s", exc, exc_info=True)
            _CACHE["m"] = None
    return _CACHE["m"]


def _symptom_weights(answers):
    from checkup.questions import QUESTION_BANK
    sym, unsure = {}, 0
    for q in QUESTION_BANK:
        for oid in answers.get(q["id"], []):
            if oid == "unsure":
                unsure += 1
            for o in q["options"]:
                if o["id"] == oid:
                    for s in o["systems"]:
                        sym[s] = sym.get(s, 0) + o["weight"]
    return sym, unsure


def predict(machine_type, owner, answers, sensors=None):
    """owner: validated owner-profile dict; answers: validated check-up answers; sensors: dict of the 4 raw sensors or None."""
    m = _model()
    if m is None:
        return None
    from ml.bulk_data import MACHINE_TYPES, SYSTEMS
    from ml.train_bulk import make_features
    sym, unsure = _symptom_weights(answers or {})
    sensors = sensors or {}
    storage = owner.get("storage", "outdoors")
    work = owner.get("work_type", "light")
    row = {"type": machine_type if machine_type in MACHINE_TYPES else "Tractor",
           "age_years": max(0, 2026 - int(owner.get("year", 2018))), "work_type": work, "storage": storage, "dusty": 0,
           "hours_per_week": owner.get("hours_this_week", 20.0), "hours_this_season": owner.get("hours_this_season", 300.0),
           "hours_since_service": owner.get("hours_since_service", 150.0), "days_idle_30": owner.get("days_idle_30", 5.0),
           "fuel_age_months": owner.get("fuel_age_months", 2.0), "sym_unsure": float(unsure)}
    for k in ("engine_temp", "vibration", "oil_pressure", "rpm_variance"):
        row[k] = sensors.get(k, np.nan)
    for s in SYSTEMS:
        row["sym_" + s] = float(sym.get(s, 0))
    df = pd.DataFrame([row])
    X = make_features(df, m["intervals"])[m["features"]]
    proba = m["clf"].predict_proba(X)[0]
    by_sys = {c: float(p) for c, p in zip(m["classes"], proba)}
    trees = np.array([t.predict(X.values)[0] for t in m["reg"].estimators_])
    p_fault = 1.0 - by_sys.get("none", 0.0)
    ranked = sorted([(s, v) for s, v in by_sys.items() if s != "none"], key=lambda kv: -kv[1])
    return {"synthetic": True, "n_train_machines": m["n_train_machines"], "p_any_fault": round(p_fault, 3),
            "system_risk": {s: round(v, 3) for s, v in ranked}, "top_system": ranked[0][0] if ranked else None,
            "hours_to_failure_range": [round(float(np.percentile(trees, 10)), 0), round(float(np.percentile(trees, 90)), 0)],
            "hours_to_failure_median": round(float(np.median(trees)), 0)}
