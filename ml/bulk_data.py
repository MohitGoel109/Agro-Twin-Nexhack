"""Bulk SIMULATED fleet generator (Python 3.9). Deterministic with a seed.

IMPORTANT: this data comes from OUR OWN assumptions (a wear model + the placeholder service intervals in
checkup/service_intervals.json). High scores on it show the method works, NOT that it works on real tractors.

One row per machine (a snapshot). Hidden true fault per system, hours-until-failure, noisy sensors (with spikes and
missing values) and noisy symptom answers (with wrong and "Not sure" answers) derived from the hidden fault.
Run:  python ml/bulk_data.py --n 5000 --seed 42   -> data/bulk_fleet.csv
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

SYSTEMS = ["engine", "cooling", "brakes", "hydraulics", "drivetrain", "electrical", "tyres", "fuel"]
MACHINE_TYPES = ["Tractor", "Harvester", "Seeder"]
STORAGE = ["indoors", "outdoors", "rain"]
WORK = ["heavy", "light", "road", "harvest"]
DEFAULT_INTERVAL = {"electrical": 1500.0, "tyres": 1500.0, "fuel": 600.0}  # used if the JSON has no hours for a system
CAP_HOURS = 24 * 90  # failures further than 90 days away are treated as "no failure in the window"


def load_intervals():
    with open(os.path.join(ROOT, "checkup", "service_intervals.json"), encoding="utf-8") as fh:
        raw = json.load(fh)
    out = {}
    for mt in MACHINE_TYPES:
        table = raw.get(mt) or raw["Tractor"]
        out[mt] = {s: float((table.get(s) or {}).get("hours") or DEFAULT_INTERVAL.get(s, 1000.0)) for s in SYSTEMS}
    return out


def question_systems():
    """option id -> systems it points to, from the check-up question bank (so symptom columns match ml/symptoms ids)."""
    from checkup.questions import QUESTION_BANK
    opts = []
    for q in QUESTION_BANK:
        for o in q["options"]:
            if o["systems"]:
                opts.append((q["id"], o["id"], o["systems"], o["weight"]))
    return opts


def _hazards(df, intervals):
    """Per-system failure hazard (0..1) from usage: hours past interval, heavy use, idle damage rules of thumb."""
    h = {}
    hs = df["hours_since_service"].values
    heavy = (df["work_type"].isin(["heavy", "harvest"])).values.astype(float)
    season_load = np.clip(df["hours_this_season"].values / 600.0, 0, 2)
    idle = df["days_idle_30"].values
    outdoors = df["storage"].isin(["outdoors", "rain"]).values.astype(float)
    rain = (df["storage"] == "rain").values.astype(float)
    ivals = {s: np.array([intervals[t][s] for t in df["type"]]) for s in SYSTEMS}
    for s in SYSTEMS:
        over = np.clip(hs / ivals[s] - 1.0, 0, 3)      # fraction past the ideal interval
        base = -4.2 + 1.6 * over
        if s in ("engine", "drivetrain", "hydraulics"):
            base = base + 0.9 * heavy + 0.7 * season_load
        if s == "cooling":
            base = base + 0.5 * heavy + 0.4 * (df["dusty"].values)
        if s == "brakes":
            base = base + 0.5 * (df["type"].values == "Tractor") + 0.4 * (df["work_type"].values == "road") + 0.3 * df["dusty"].values
        if s == "electrical":
            base = base + 0.06 * np.clip(idle - 10, 0, None) + 0.5 * outdoors + 0.04 * df["age_years"].values
        if s == "tyres":
            base = base + 0.04 * np.clip(idle - 10, 0, None) * outdoors + 0.5 * rain + 0.05 * df["age_years"].values
        if s == "fuel":
            base = base + 0.35 * np.clip(df["fuel_age_months"].values - 5, 0, None)
        h[s] = 1.0 / (1.0 + np.exp(-base))
    return h


def generate_fleet(n_machines=5000, seed=42):
    rng = np.random.RandomState(seed)
    intervals = load_intervals()
    n = int(n_machines)
    df = pd.DataFrame({
        "machine_id": ["M%06d" % i for i in range(n)],
        "type": rng.choice(MACHINE_TYPES, n, p=[0.55, 0.3, 0.15]),
        "age_years": rng.randint(1, 16, n),
        "work_type": rng.choice(WORK, n, p=[0.3, 0.3, 0.15, 0.25]),
        "storage": rng.choice(STORAGE, n, p=[0.4, 0.45, 0.15]),
        "dusty": rng.binomial(1, 0.5, n),
    })
    df["hours_per_week"] = np.clip(rng.gamma(3.0, 6.0, n), 0, 100).round(1)
    df["hours_this_season"] = np.clip(df["hours_per_week"] * rng.uniform(6, 16, n), 0, 3000).round(0)
    df["hours_since_service"] = np.clip(rng.gamma(2.2, 180.0, n), 0, 3500).round(0)
    df["days_idle_30"] = np.clip(rng.exponential(8.0, n) + rng.binomial(1, 0.15, n) * rng.uniform(10, 30, n), 0, 30).round(0)
    df["fuel_age_months"] = np.clip(rng.exponential(2.5, n), 0, 24).round(1)

    haz = _hazards(df, intervals)
    # true fault: each system fails with its hazard; if several do, the one with the highest hazard wins
    draws = {s: rng.uniform(size=n) < haz[s] for s in SYSTEMS}
    score = np.stack([np.where(draws[s], haz[s] + rng.uniform(0, 0.05, n), -1.0) for s in SYSTEMS], axis=1)
    has = score.max(axis=1) > 0
    fault = np.where(has, np.array(SYSTEMS)[score.argmax(axis=1)], "none")
    df["true_fault"] = fault
    top_h = np.stack([haz[s] for s in SYSTEMS], axis=1).max(axis=1)
    # hours until failure: sooner when the hazard is high; no-fault machines are capped at the window
    mean_h = 24.0 * (3 + 40 * (1 - np.clip(top_h, 0, 0.95)))
    hrs = rng.exponential(mean_h)
    df["hours_to_failure"] = np.where(has, np.clip(hrs, 4, CAP_HOURS), CAP_HOURS).round(1)
    for s in SYSTEMS:
        df["hazard_" + s] = haz[s].round(4)   # kept for transparency; NOT used as a training feature

    # sensors from the hidden fault: engine_temp, vibration, oil_pressure, rpm_variance (healthy baselines as in the demo)
    sens = {"engine_temp": rng.normal(82, 2.0, n), "vibration": rng.normal(2.0, 0.25, n),
            "oil_pressure": rng.normal(45, 1.5, n), "rpm_variance": rng.normal(15, 2.0, n)}
    effect = {"engine": (6, 0.4, -4, 8), "cooling": (9, 0.2, 0, 3), "brakes": (0, 0.5, 0, 2), "hydraulics": (1, 0.6, -7, 0),
              "drivetrain": (2, 1.1, 0, 9), "electrical": (0, 0.1, 0, 4), "tyres": (0, 0.7, 0, 1), "fuel": (1, 0.2, -1, 12)}
    sev = np.clip(1.2 - hrs / (24.0 * 20), 0.2, 1.0) * has
    for s, (dt, dv, dp, dr) in effect.items():
        m = (fault == s) * sev
        sens["engine_temp"] = sens["engine_temp"] + dt * m
        sens["vibration"] = sens["vibration"] + dv * m
        sens["oil_pressure"] = sens["oil_pressure"] + dp * m
        sens["rpm_variance"] = sens["rpm_variance"] + dr * m
    for k, v in sens.items():
        spike = rng.uniform(size=n) < 0.03
        v = np.where(spike, v + rng.choice([-1, 1], n) * np.abs(v) * 0.25, v)   # single-reading spikes
        v = np.where(rng.uniform(size=n) < 0.08, np.nan, v)                        # missing data
        df[k] = np.round(v, 2)

    # symptom answers from the hidden fault: right clues most of the time, wrong ones sometimes, many "Not sure"
    opts = question_systems()
    sym = {s: np.zeros(n) for s in SYSTEMS}
    unsure = np.zeros(n)
    for qid, oid, systems, weight in opts:
        for s in systems:
            truly = fault == s
            p = np.where(truly, 0.55, 0.04)                        # chance this clue is reported
            say = rng.uniform(size=n) < p
            skip = rng.uniform(size=n) < 0.2                       # farmer answers "Not sure" instead
            unsure = unsure + (say & skip)
            say = say & ~skip
            sym[s] = sym[s] + say * weight
    for s in SYSTEMS:
        df["sym_" + s] = sym[s]
    df["sym_unsure"] = unsure
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "bulk_fleet.csv"))
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    df = generate_fleet(a.n, a.seed)
    df.to_csv(a.out, index=False)
    print("Wrote %d simulated machines to %s (SYNTHETIC data)" % (len(df), a.out))
    print(df["true_fault"].value_counts().to_string())


if __name__ == "__main__":
    main()
