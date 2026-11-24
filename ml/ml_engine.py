"""
Agro-Twin: Leak-Free Predictive Maintenance & Explainability Engine
Owner: Member 1 (Vansh) - AI & Explainability Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery
"""

import math
import re
from copy import deepcopy

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Healthy baseline values for fictional farm machinery sensors
BASELINES = {
    "engine_temp": 82.0,    # deg C
    "vibration": 2.0,       # mm/s
    "oil_pressure": 45.0,   # PSI
    "rpm_variance": 15.0,   # RPM
}

# Thresholds used to detect isolated single-step sensor spikes (noise vs real trend)
SPIKE_LIMITS = {
    "engine_temp": 14.0,
    "vibration": 1.4,
    "oil_pressure": 10.0,
    "rpm_variance": 20.0,
}

SENSORS = list(BASELINES.keys())

DEFAULT_FLEET_META = [
    {
        "id": "TR-101",
        "name": "Tractor Alpha (Sowing)",
        "type": "Tractor",
        "part_needed": "Coolant Pump",
        "mode": "fault_engine",
        "fault_start": 24,
        "seed": 101,
    },
    {
        "id": "HV-202",
        "name": "Harvester Bravo (Wheat)",
        "type": "Harvester",
        "part_needed": "Hydraulic Valve",
        "mode": "fault_hydraulic",
        "fault_start": 40,
        "seed": 202,
    },
    {
        "id": "TR-103",
        "name": "Tractor Charlie (Plowing)",
        "type": "Tractor",
        "part_needed": "Drive Bearing",
        "mode": "fault_bearing",
        "fault_start": 62,
        "seed": 303,
    },
    {
        "id": "SD-304",
        "name": "Seed Drill Delta",
        "type": "Seeder",
        "part_needed": "Sensor Harness",
        "mode": "noisy",
        "fault_start": None,
        "seed": 404,
    },
    {
        "id": "TR-105",
        "name": "Tractor Echo (Hauling)",
        "type": "Tractor",
        "part_needed": "Sensor Harness",
        "mode": "missing",
        "fault_start": None,
        "seed": 505,
    },
    {
        "id": "HV-206",
        "name": "Harvester Foxtrot",
        "type": "Harvester",
        "part_needed": "Drive Bearing",
        "mode": "healthy",
        "fault_start": None,
        "seed": 606,
    },
]

FAULT_MODE_TO_INTERNAL = {
    "healthy": "healthy",
    "fault_engine": "fault_engine",
    "fault_hydraulic": "fault_hydraulic",
    "fault_bearing": "fault_bearing",
    "noise_spike": "noisy",
    "noisy": "noisy",
    "missing_data": "missing",
    "missing": "missing",
}
FAULT_MODE_TO_PUBLIC = {
    "healthy": "healthy",
    "fault_engine": "fault_engine",
    "fault_hydraulic": "fault_hydraulic",
    "fault_bearing": "fault_bearing",
    "noisy": "noise_spike",
    "missing": "missing_data",
}
VALID_PARTS = {machine["part_needed"] for machine in DEFAULT_FLEET_META}
MACHINE_TYPES_BY_PREFIX = {"TR": "Tractor", "HV": "Harvester", "SD": "Seeder"}


def _generate_single_machine(
    seed: int,
    mode: str = "healthy",
    fault_start: int = None,
    num_steps: int = 120,
    weather_mode: str = "normal",
) -> pd.DataFrame:
    """Generates hourly synthetic telemetry for one fictional farm machine."""
    rng = np.random.default_rng(seed)

    engine_temp = rng.normal(BASELINES["engine_temp"], 1.4, num_steps)
    vibration = rng.normal(BASELINES["vibration"], 0.14, num_steps)
    oil_pressure = rng.normal(BASELINES["oil_pressure"], 1.3, num_steps)
    rpm_variance = rng.normal(BASELINES["rpm_variance"], 2.0, num_steps)

    heatwave = weather_mode == "heatwave_45c"
    if heatwave:
        engine_temp += 8.0
        oil_pressure -= 2.5

    breakdown_step = None

    # Gradual developing faults over ~20-24 hours before breakdown
    if mode == "fault_engine" and fault_start is not None:
        breakdown_step = min(fault_start + 22, num_steps - 1)
        for t in range(fault_start, num_steps):
            age = t - fault_start
            slope = 1.25 if heatwave else 1.0
            engine_temp[t] += 1.15 * age * slope
            oil_pressure[t] -= 0.85 * age * slope
            vibration[t] += 0.10 * age * slope
            rpm_variance[t] += 1.40 * age * slope

    elif mode == "fault_hydraulic" and fault_start is not None:
        breakdown_step = min(fault_start + 24, num_steps - 1)
        for t in range(fault_start, num_steps):
            age = t - fault_start
            slope = 1.25 if heatwave else 1.0
            oil_pressure[t] -= 1.05 * age * slope
            vibration[t] += 0.16 * age * slope
            engine_temp[t] += 0.65 * age * slope

    elif mode == "fault_bearing" and fault_start is not None:
        breakdown_step = min(fault_start + 20, num_steps - 1)
        for t in range(fault_start, num_steps):
            age = t - fault_start
            slope = 1.25 if heatwave else 1.0
            vibration[t] += 0.24 * age * slope
            rpm_variance[t] += 2.10 * age * slope
            engine_temp[t] += 0.45 * age * slope

    if heatwave and breakdown_step is not None:
        breakdown_step = max(fault_start + 12, breakdown_step - 4)

    # Isolated 1-hour sensor spikes (noise, NOT real machine degradation)
    if mode == "noisy":
        for spike_t in [20, 35, 42, 68, 95]:
            if spike_t < num_steps:
                engine_temp[spike_t] += 36.0
                vibration[spike_t] += 3.5

    # Temporary missing sensor dropouts (raises uncertainty, NOT a real fault)
    if mode == "missing":
        for drop_t in [28, 29, 30, 34, 35, 72, 73, 74]:
            if drop_t < num_steps:
                engine_temp[drop_t] = np.nan
                oil_pressure[drop_t] = np.nan

    return pd.DataFrame(
        {
            "step": np.arange(num_steps),
            "engine_temp": engine_temp,
            "vibration": vibration,
            "oil_pressure": oil_pressure,
            "rpm_variance": rpm_variance,
            "breakdown_step": breakdown_step if breakdown_step is not None else -1,
        }
    )


def _extract_leak_free_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes features STRICTLY from backward/current windows [t-5 .. t].
    Never reads future timestamps or failure labels (100% leak-free).
    """
    feat = pd.DataFrame(index=df.index)

    missing_per_row = df[SENSORS].isna().sum(axis=1)
    feat["missing_recent"] = missing_per_row.rolling(window=3, min_periods=1).sum()

    spike_flags = np.zeros(len(df), dtype=int)

    for col in SENSORS:
        raw = df[col]
        # 3-hour rolling median suppresses isolated 1-hour spikes
        med3 = raw.rolling(window=3, min_periods=1).median()
        med3 = med3.ffill().fillna(BASELINES[col])

        # 5-hour backward slope (past-only)
        slope = med3 - med3.shift(5).fillna(med3)

        # Deviation from healthy operating baseline
        dev = med3 - BASELINES[col]

        feat[f"{col}_med3"] = med3
        feat[f"{col}_slope"] = slope
        feat[f"{col}_dev"] = dev

        is_spike = (raw - med3).abs() > SPIKE_LIMITS[col]
        spike_flags = np.maximum(spike_flags, is_spike.fillna(False).astype(int))

    feat["spike_flag"] = spike_flags
    return feat


# ML model uses ONLY smoothed, leak-free sensor trends; noise/missing flags are handled by the quality layer
FEATURE_COLS = (
    [f"{c}_med3" for c in SENSORS]
    + [f"{c}_slope" for c in SENSORS]
    + [f"{c}_dev" for c in SENSORS]
)


class FleetTelemetryEngine:
    """
    Core Predictive Maintenance Twin Engine for PS 08.
    Consumed directly by Member 2 (scheduler), Member 3 (backend API), and Member 4 (dashboard).
    """

    def __init__(self, num_steps: int = 120):
        self.num_steps = num_steps
        self.weather_mode = "normal"
        self.model = None
        self._base_fleet_meta = deepcopy(DEFAULT_FLEET_META)
        self.fleet_meta = deepcopy(self._base_fleet_meta)
        self._next_machine_seed = max(m["seed"] for m in self.fleet_meta) + 1
        self.telemetry = {}
        self.features = {}
        self._train_leak_free_model()
        self._build_fleet_data()

    def _train_leak_free_model(self):
        """Trains Random Forest strictly on historical synthetic fleets with zero future leakage."""
        X_list, y_list = [], []
        training_scenarios = [
            ("healthy", None),
            ("noisy", None),
            ("missing", None),
            ("fault_engine", 25),
            ("fault_engine", 50),
            ("fault_engine", 70),
            ("fault_hydraulic", 30),
            ("fault_hydraulic", 55),
            ("fault_bearing", 35),
            ("fault_bearing", 65),
        ]

        for idx, (mode, f_start) in enumerate(training_scenarios * 4):
            df = _generate_single_machine(
                seed=1000 + idx,
                mode=mode,
                fault_start=f_start,
                num_steps=self.num_steps,
            )
            feat = _extract_leak_free_features(df)
            b_step = int(df["breakdown_step"].iloc[0])

            # Target = 1 only once real degradation is active and before breakdown
            if b_step != -1 and f_start is not None:
                labels = ((df["step"] >= f_start + 3) & (df["step"] <= b_step)).astype(int)
                valid_mask = df["step"] <= b_step
            else:
                labels = pd.Series(0, index=df.index)
                valid_mask = pd.Series(True, index=df.index)

            X_list.append(feat.loc[valid_mask, FEATURE_COLS].to_numpy())
            y_list.append(labels.loc[valid_mask].to_numpy())

        X_train = np.vstack(X_list)
        y_train = np.concatenate(y_list)

        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=6,
            random_state=42,
        )
        self.model.fit(X_train, y_train)

    def _build_fleet_data(self):
        """Generates telemetry and features for every active fleet machine."""
        self.telemetry = {}
        self.features = {}
        for m in self.fleet_meta:
            df = _generate_single_machine(
                seed=m["seed"],
                mode=m["mode"],
                fault_start=m["fault_start"],
                num_steps=self.num_steps,
                weather_mode=self.weather_mode,
            )
            self.telemetry[m["id"]] = df
            self.features[m["id"]] = _extract_leak_free_features(df)

    @staticmethod
    def _normalize_fault_mode(fault_mode: str):
        if not isinstance(fault_mode, str):
            return None
        return FAULT_MODE_TO_INTERNAL.get(fault_mode.strip().lower())

    @staticmethod
    def _normalize_machine_id(machine_id: str):
        if not isinstance(machine_id, str):
            return None
        normalized = machine_id.strip().upper()
        if not normalized or not re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)*", normalized):
            return None
        return normalized

    def add_machine(
        self,
        machine_id: str,
        name: str,
        part_needed: str,
        criticality: float = 1.0,
        fault_mode: str = "healthy",
        fault_start: int = None,
    ) -> dict:
        """Adds a uniquely identified machine and generates its synthetic telemetry."""
        normalized_id = self._normalize_machine_id(machine_id)
        if normalized_id is None:
            return {"ok": False, "message": "Machine ID must contain only letters, numbers, and hyphens."}
        if normalized_id in self.get_all_machine_ids():
            return {"ok": False, "message": f"Machine '{normalized_id}' already exists."}
        if not isinstance(name, str) or not name.strip():
            return {"ok": False, "message": "Machine name is required."}
        if not isinstance(part_needed, str) or part_needed not in VALID_PARTS:
            return {"ok": False, "message": f"Part must be one of: {', '.join(sorted(VALID_PARTS))}."}

        try:
            priority = float(criticality)
        except (TypeError, ValueError):
            return {"ok": False, "message": "Criticality must be a number between 0.8 and 1.5."}
        if not math.isfinite(priority) or not 0.8 <= priority <= 1.5:
            return {"ok": False, "message": "Criticality must be between 0.8 and 1.5."}

        internal_mode = self._normalize_fault_mode(fault_mode)
        if internal_mode is None:
            return {"ok": False, "message": "Unsupported machine condition."}
        if fault_start is not None:
            try:
                start = int(fault_start)
            except (TypeError, ValueError):
                return {"ok": False, "message": "Fault start must be a valid simulation hour."}
            if not 0 <= start < self.num_steps:
                return {"ok": False, "message": f"Fault start must be between 0 and {self.num_steps - 1}."}
        else:
            start = None if internal_mode == "healthy" else min(25, self.num_steps - 1)

        prefix = normalized_id.split("-", 1)[0]
        machine = {
            "id": normalized_id,
            "name": name.strip(),
            "type": MACHINE_TYPES_BY_PREFIX.get(prefix, "Tractor"),
            "part_needed": part_needed,
            "mode": internal_mode,
            "fault_start": start,
            "seed": self._next_machine_seed,
            "criticality": priority,
        }
        self._next_machine_seed += 1
        self.fleet_meta.append(machine)
        self._build_fleet_data()
        return {"ok": True, "message": f"Machine '{normalized_id}' added.", "machine": dict(machine)}

    def update_machine(
        self,
        machine_id: str,
        name: str = None,
        part_needed: str = None,
        criticality: float = None,
        fault_mode: str = None,
        fault_start: int = None,
    ) -> dict:
        """Updates supplied machine metadata and regenerates that fleet's telemetry."""
        normalized_id = self._normalize_machine_id(machine_id)
        machine = next((m for m in self.fleet_meta if m["id"] == normalized_id), None)
        if machine is None:
            return {"ok": False, "message": f"Machine '{machine_id}' not found."}

        updated = dict(machine)
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                return {"ok": False, "message": "Machine name is required."}
            updated["name"] = name.strip()
        if part_needed is not None:
            if not isinstance(part_needed, str) or part_needed not in VALID_PARTS:
                return {"ok": False, "message": f"Part must be one of: {', '.join(sorted(VALID_PARTS))}."}
            updated["part_needed"] = part_needed
        if criticality is not None:
            try:
                priority = float(criticality)
            except (TypeError, ValueError):
                return {"ok": False, "message": "Criticality must be a number between 0.8 and 1.5."}
            if not math.isfinite(priority) or not 0.8 <= priority <= 1.5:
                return {"ok": False, "message": "Criticality must be between 0.8 and 1.5."}
            updated["criticality"] = priority

        if fault_mode is not None:
            internal_mode = self._normalize_fault_mode(fault_mode)
            if internal_mode is None:
                return {"ok": False, "message": "Unsupported machine condition."}
            updated["mode"] = internal_mode
            if internal_mode == "healthy" and fault_start is None:
                updated["fault_start"] = None
            elif fault_start is None and updated.get("fault_start") is None:
                updated["fault_start"] = min(25, self.num_steps - 1)

        if fault_start is not None:
            try:
                start = int(fault_start)
            except (TypeError, ValueError):
                return {"ok": False, "message": "Fault start must be a valid simulation hour."}
            if not 0 <= start < self.num_steps:
                return {"ok": False, "message": f"Fault start must be between 0 and {self.num_steps - 1}."}
            updated["fault_start"] = start

        machine.update(updated)
        self._build_fleet_data()
        return {"ok": True, "message": f"Machine '{normalized_id}' updated.", "machine": dict(machine)}

    def remove_machine(self, machine_id: str) -> dict:
        """Removes a machine and its telemetry, retaining at least one fleet unit."""
        normalized_id = self._normalize_machine_id(machine_id)
        machine = next((m for m in self.fleet_meta if m["id"] == normalized_id), None)
        if machine is None:
            return {"ok": False, "message": f"Machine '{machine_id}' not found."}
        if len(self.fleet_meta) <= 1:
            return {"ok": False, "message": "At least one machine must remain in the fleet."}

        self.fleet_meta.remove(machine)
        self.telemetry.pop(normalized_id, None)
        self.features.pop(normalized_id, None)
        return {"ok": True, "message": f"Machine '{normalized_id}' removed.", "machine_id": normalized_id}

    def reset_fleet(self):
        """Resets all machines back to the default deterministic harvest scenario."""
        self.fleet_meta = deepcopy(self._base_fleet_meta)
        self._next_machine_seed = max(m["seed"] for m in self.fleet_meta) + 1
        self.weather_mode = "normal"
        self._build_fleet_data()

    def set_weather_mode(self, mode: str) -> dict:
        """Switches the fleet between normal weather and severe harvest heat."""
        self.weather_mode = (
            mode if isinstance(mode, str) and mode in {"normal", "heatwave_45c"} else "normal"
        )
        self._build_fleet_data()
        return {
            "ok": True,
            "weather_mode": self.weather_mode,
            "ambient_temp_c": 45 if self.weather_mode == "heatwave_45c" else 30,
            "stress_note": (
                "45°C harvest heat raises engine temperatures and tightens fault lead times."
                if self.weather_mode == "heatwave_45c"
                else "Normal 30°C operating conditions."
            ),
        }

    def get_all_machine_ids(self) -> list:
        """Returns the list of all machine IDs in the fleet."""
        return [m["id"] for m in self.fleet_meta]

    def get_model_info(self) -> dict:
        """Metadata proving leak-free setup and uncertainty calibration for judges."""
        return {
            "model_type": "RandomForestClassifier (50 trees, max_depth=6)",
            "prediction_horizon_hours": 20,
            "feature_window_hours": 5,
            "noise_filter": "3-hour backward rolling median",
            "leak_free_guarantee": "All features computed strictly from [t-5 .. t]; future breakdown labels never enter prediction inputs.",
            "uncertainty_method": "Ensemble tree disagreement (std across 50 trees) + missing-telemetry & spike penalties.",
            "fleet_size": len(self.fleet_meta),
            "simulation_hours": self.num_steps,
            "weather_mode": self.weather_mode,
        }

    def inject_fault(
        self, machine_id: str, start_step: int, fault_type: str = "fault_engine"
    ) -> bool:
        """Injects a developing fault into any machine live during judge demonstrations."""
        valid_faults = {"fault_engine", "fault_hydraulic", "fault_bearing"}
        if fault_type not in valid_faults:
            fault_type = "fault_engine"

        for m in self.fleet_meta:
            if m["id"] == machine_id:
                m["mode"] = fault_type
                m["fault_start"] = int(start_step)
                df = _generate_single_machine(
                    seed=m["seed"] + 99,
                    mode=fault_type,
                    fault_start=int(start_step),
                    num_steps=self.num_steps,
                    weather_mode=self.weather_mode,
                )
                self.telemetry[machine_id] = df
                self.features[machine_id] = _extract_leak_free_features(df)
                return True
        return False

    def _explain_prediction(self, feat_row: pd.Series, sensor_status: str) -> list:
        """Generates plain-English top-3 drivers for non-technical operators and judges."""
        if sensor_status == "SENSOR_NOISE_FILTERED":
            return [
                "Single-hour sensor spike filtered out by 3h rolling median - holding alarm to prevent false dispatch."
            ]
        if sensor_status == "MISSING_DATA_HOLD":
            return [
                "Recent sensor readings missing - uncertainty elevated; holding dispatch until clean telemetry resumes."
            ]

        drivers = []
        temp_dev = float(feat_row["engine_temp_dev"])
        vib_dev = float(feat_row["vibration_dev"])
        oil_dev = float(feat_row["oil_pressure_dev"])
        rpm_dev = float(feat_row["rpm_variance_dev"])

        if temp_dev > 4.0:
            drivers.append(
                (abs(temp_dev) / 10.0, f"Engine Temp +{temp_dev:.1f} C above baseline (rising)")
            )
        if vib_dev > 0.5:
            drivers.append(
                (abs(vib_dev) / 1.0, f"Vibration +{vib_dev:.2f} mm/s above baseline")
            )
        if oil_dev < -3.5:
            drivers.append(
                (abs(oil_dev) / 8.0, f"Oil Pressure {oil_dev:.1f} PSI below normal")
            )
        if rpm_dev > 6.0:
            drivers.append(
                (abs(rpm_dev) / 12.0, f"RPM Variance +{rpm_dev:.1f} RPM instability")
            )

        drivers.sort(key=lambda x: x[0], reverse=True)
        if not drivers:
            return ["All smoothed sensors within normal operating range."]
        return [text for _, text in drivers[:3]]

    def get_fleet_snapshot(self, step: int) -> list:
        """
        Returns JSON-safe fleet health, fault probability, uncertainty, sensor quality flag,
        and plain-English explanations at a given hour `step`.
        """
        step = max(0, min(int(step), self.num_steps - 1))
        snapshot = []

        for m in self.fleet_meta:
            m_id = m["id"]
            raw_row = self.telemetry[m_id].iloc[step]
            feat_row = self.features[m_id].iloc[step]
            X_vec = feat_row[FEATURE_COLS].to_numpy().reshape(1, -1)

            # Ensemble disagreement across all 50 trees quantifies model uncertainty
            tree_probs = np.array(
                [tree.predict_proba(X_vec)[0][1] for tree in self.model.estimators_]
            )
            fault_prob = float(np.mean(tree_probs))
            tree_std = float(np.std(tree_probs))

            missing_count = int(feat_row["missing_recent"])
            spike_flag = int(feat_row["spike_flag"])

            # Missing readings or sudden spikes directly increase reported uncertainty
            uncertainty = min(
                0.45,
                round(tree_std + (0.06 * missing_count) + (0.12 * spike_flag), 3),
            )
            confidence = round(max(0.10, 1.0 - uncertainty * 2.0), 3)

            # Distinguish sensor noise / missing data from genuine developing faults
            if missing_count >= 3 and fault_prob < 0.65:
                sensor_status = "MISSING_DATA_HOLD"
            elif spike_flag == 1 and fault_prob < 0.55:
                sensor_status = "SENSOR_NOISE_FILTERED"
            else:
                sensor_status = "CLEAN"

            b_step = int(raw_row["breakdown_step"])
            is_broken = (b_step != -1) and (step >= b_step)

            if is_broken:
                status = "BROKEN_DOWN"
                fault_prob = 1.0
            elif fault_prob >= 0.70 and sensor_status == "CLEAN":
                status = "CRITICAL_WARNING"
            elif fault_prob >= 0.40 and sensor_status == "CLEAN":
                status = "EARLY_WARNING"
            elif sensor_status != "CLEAN":
                status = "DATA_CHECK"
            else:
                status = "HEALTHY"

            safe_raw = {
                s: (None if pd.isna(raw_row[s]) else round(float(raw_row[s]), 2))
                for s in SENSORS
            }

            snapshot.append(
                {
                    "machine_id": m_id,
                    "name": m["name"],
                    "type": m["type"],
                    "fault_mode": FAULT_MODE_TO_PUBLIC.get(m["mode"], m["mode"]),
                    "fault_start": m["fault_start"],
                    "criticality": m.get(
                        "criticality",
                        {"Harvester": 1.25, "Tractor": 1.10, "Seeder": 1.0}.get(m["type"], 1.0),
                    ),
                    "step": step,
                    "weather_mode": self.weather_mode,
                    "status": status,
                    "sensor_status": sensor_status,
                    "fault_probability": round(fault_prob, 3),
                    "uncertainty": uncertainty,
                    "confidence": confidence,
                    "part_needed": m["part_needed"],
                    "actual_breakdown_step": b_step if b_step != -1 else None,
                    "reasons": self._explain_prediction(feat_row, sensor_status),
                    "raw_sensors": safe_raw,
                }
            )

        return snapshot

    def get_fleet_comparison_history(self, up_to_step: int = None) -> list:
        """Builds comparison snapshots with batched tree predictions across the replay."""
        max_step = self.num_steps - 1 if up_to_step is None else min(int(up_to_step), self.num_steps - 1)
        total_hours = max_step + 1
        history = [[] for _ in range(total_hours)]

        for machine in self.fleet_meta:
            machine_id = machine["id"]
            features = self.features[machine_id].iloc[:total_hours]
            telemetry = self.telemetry[machine_id].iloc[:total_hours]
            feature_values = features[FEATURE_COLS].to_numpy()
            tree_probabilities = np.asarray(
                [tree.predict_proba(feature_values)[:, 1] for tree in self.model.estimators_]
            )
            fault_probabilities = np.mean(tree_probabilities, axis=0)
            tree_stds = np.std(tree_probabilities, axis=0)

            for step in range(total_hours):
                feature_row = features.iloc[step]
                raw_row = telemetry.iloc[step]
                fault_probability = float(fault_probabilities[step])
                missing_count = int(feature_row["missing_recent"])
                spike_flag = int(feature_row["spike_flag"])
                uncertainty = min(
                    0.45,
                    round(float(tree_stds[step]) + (0.06 * missing_count) + (0.12 * spike_flag), 3),
                )
                confidence = round(max(0.10, 1.0 - uncertainty * 2.0), 3)

                if missing_count >= 3 and fault_probability < 0.65:
                    sensor_status = "MISSING_DATA_HOLD"
                elif spike_flag == 1 and fault_probability < 0.55:
                    sensor_status = "SENSOR_NOISE_FILTERED"
                else:
                    sensor_status = "CLEAN"

                breakdown_step = int(raw_row["breakdown_step"])
                if breakdown_step != -1 and step >= breakdown_step:
                    status = "BROKEN_DOWN"
                    fault_probability = 1.0
                elif fault_probability >= 0.70 and sensor_status == "CLEAN":
                    status = "CRITICAL_WARNING"
                elif fault_probability >= 0.40 and sensor_status == "CLEAN":
                    status = "EARLY_WARNING"
                elif sensor_status != "CLEAN":
                    status = "DATA_CHECK"
                else:
                    status = "HEALTHY"

                history[step].append(
                    {
                        "machine_id": machine_id,
                        "type": machine["type"],
                        "status": status,
                        "sensor_status": sensor_status,
                        "fault_probability": round(fault_probability, 3),
                        "confidence": confidence,
                        "part_needed": machine["part_needed"],
                        "actual_breakdown_step": breakdown_step if breakdown_step != -1 else None,
                        "criticality": machine.get(
                            "criticality",
                            {"Harvester": 1.25, "Tractor": 1.10, "Seeder": 1.0}.get(
                                machine["type"], 1.0
                            ),
                        ),
                    }
                )

        return history

    def get_machine_history(self, machine_id: str, up_to_step: int) -> list:
        """Returns hourly sensor history up to `up_to_step` for plotting in the UI."""
        if machine_id not in self.telemetry:
            return []
        up_to_step = max(0, min(int(up_to_step), self.num_steps - 1))
        df = self.telemetry[machine_id].iloc[: up_to_step + 1]
        history = []
        for _, row in df.iterrows():
            history.append(
                {
                    "step": int(row["step"]),
                    "engine_temp": None
                    if pd.isna(row["engine_temp"])
                    else round(float(row["engine_temp"]), 2),
                    "vibration": None
                    if pd.isna(row["vibration"])
                    else round(float(row["vibration"]), 2),
                    "oil_pressure": None
                    if pd.isna(row["oil_pressure"])
                    else round(float(row["oil_pressure"]), 2),
                    "rpm_variance": None
                    if pd.isna(row["rpm_variance"])
                    else round(float(row["rpm_variance"]), 2),
                }
            )
        return history


if __name__ == "__main__":
    engine = FleetTelemetryEngine()
    print("=== AGRO-TWIN ML ENGINE QUICK CHECK (HOUR 35) ===")
    for item in engine.get_fleet_snapshot(step=35):
        print(
            f"{item['machine_id']} | {item['status']:16s} | "
            f"Risk: {item['fault_probability']*100:5.1f}% (+/-{item['uncertainty']*100:4.1f}%) | "
            f"Data: {item['sensor_status']:21s} | {item['reasons'][0]}"
        )
