"""
One-command verification script for Member 1 (Vansh).
Run from repo root: python ml/verify_ml.py
"""

import math
import os
import sys

# Ensure repo root is importable regardless of where the script is launched
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.ml_engine import FleetTelemetryEngine


def run_verification():
    engine = FleetTelemetryEngine()
    info = engine.get_model_info()
    print("=" * 72)
    print("AGRO-TWIN | MEMBER 1 (VANSH) VERIFICATION REPORT")
    print("=" * 72)
    print(f"Model        : {info['model_type']}")
    print(f"Noise Filter : {info['noise_filter']}")
    print(f"Leak-Free    : {info['leak_free_guarantee']}")
    print("-" * 72)

    print("\n[TEST 1] Fleet Snapshot at Hour 35 (Real Fault + Noise Spike + Missing Data):")
    snap = engine.get_fleet_snapshot(step=35)
    for m in snap:
        print(
            f"  {m['machine_id']} | {m['status']:16s} | "
            f"Risk {m['fault_probability']*100:5.1f}% (+/-{m['uncertainty']*100:4.1f}%) | "
            f"Data: {m['sensor_status']:21s} | {m['reasons'][0]}"
        )

    # Assertions proving core PS 08 requirements
    by_id = {m["machine_id"]: m for m in snap}
    assert by_id["TR-101"]["status"] in ("EARLY_WARNING", "CRITICAL_WARNING"), "TR-101 should trigger early warning before Hour 46 breakdown"
    assert by_id["SD-304"]["sensor_status"] == "SENSOR_NOISE_FILTERED", "SD-304 spike at Hour 35 should be filtered as noise"
    assert by_id["TR-105"]["sensor_status"] == "MISSING_DATA_HOLD", "TR-105 missing readings at Hour 35 should trigger MISSING_DATA_HOLD"
    assert by_id["TR-105"]["uncertainty"] > by_id["HV-206"]["uncertainty"], "Missing data must raise uncertainty above healthy machine"

    comparison_history = engine.get_fleet_comparison_history(up_to_step=35)
    for step in (0, 35):
        direct = {item["machine_id"]: item for item in engine.get_fleet_snapshot(step)}
        batched = {item["machine_id"]: item for item in comparison_history[step]}
        for machine_id, snapshot in direct.items():
            comparison_snapshot = batched[machine_id]
            for key in ("status", "sensor_status", "actual_breakdown_step", "part_needed", "criticality"):
                assert comparison_snapshot[key] == snapshot[key], f"{machine_id} differs at Hour {step}: {key}"
            for key in ("fault_probability", "confidence"):
                assert math.isclose(comparison_snapshot[key], snapshot[key], abs_tol=0.001), (
                    f"{machine_id} differs at Hour {step}: {key}"
                )
    print("[TEST 1A] Batched comparison history matches individual fleet snapshots.")

    print("\n[TEST 2] Live Fault Injection Check (Injecting bearing fault into HV-206 at Hour 50):")
    ok = engine.inject_fault("HV-206", start_step=50, fault_type="fault_bearing")
    assert ok, "Fault injection failed"
    after = {m["machine_id"]: m for m in engine.get_fleet_snapshot(step=62)}["HV-206"]
    print(
        f"  HV-206 at Hour 62 -> {after['status']} | Risk {after['fault_probability']*100:.1f}% | "
        f"Why: {after['reasons'][0]}"
    )
    assert after["fault_probability"] >= 0.40, "Injected fault should raise risk score"

    engine.reset_fleet()
    print("\n[TEST 3] Heatwave Weather Stress Check:")
    normal = {m["machine_id"]: m for m in engine.get_fleet_snapshot(step=35)}["TR-101"]
    heatwave_result = engine.set_weather_mode("heatwave_45c")
    heatwave = {m["machine_id"]: m for m in engine.get_fleet_snapshot(step=35)}["TR-101"]
    assert heatwave_result["ok"], "Heatwave mode should be enabled"
    assert heatwave["actual_breakdown_step"] < normal["actual_breakdown_step"], "Heatwave should shift TR-101 breakdown earlier"
    assert heatwave["raw_sensors"]["engine_temp"] > normal["raw_sensors"]["engine_temp"], "Heatwave should raise TR-101 engine temperature"
    assert heatwave["weather_mode"] == "heatwave_45c", "Machine snapshot should report active weather mode"
    print(
        f"  TR-101 | normal breakdown Hour {normal['actual_breakdown_step']} -> "
        f"heatwave Hour {heatwave['actual_breakdown_step']} | "
        f"Engine {normal['raw_sensors']['engine_temp']:.1f}°C -> "
        f"{heatwave['raw_sensors']['engine_temp']:.1f}°C"
    )
    engine.set_weather_mode("normal")
    assert engine.get_model_info()["weather_mode"] == "normal", "Switching back should restore normal weather"

    print("\n[TEST 4] Dynamic Fleet CRUD, Condition Aliases, and Clean Reset:")
    added = engine.add_machine(
        machine_id="TR-107",
        name="Tractor Golf",
        part_needed="Sensor Harness",
        criticality=1.4,
        fault_mode="noise_spike",
    )
    assert added["ok"], added["message"]
    assert "TR-107" in engine.telemetry and "TR-107" in engine.features
    assert added["machine"]["fault_start"] == 25
    assert engine.get_model_info()["fleet_size"] == 7
    assert engine.add_machine("TR-108", "Invalid", "Sensor Harness", fault_mode="unknown")["ok"] is False

    updated = engine.update_machine(
        "tr-107",
        name="Tractor Golf Updated",
        part_needed="Coolant Pump",
        criticality=1.2,
        fault_mode="fault_bearing",
        fault_start=40,
    )
    assert updated["ok"], updated["message"]
    updated_snapshot = {m["machine_id"]: m for m in engine.get_fleet_snapshot(step=40)}["TR-107"]
    assert updated_snapshot["name"] == "Tractor Golf Updated"
    assert updated_snapshot["part_needed"] == "Coolant Pump"
    assert updated_snapshot["criticality"] == 1.2
    assert updated_snapshot["fault_mode"] == "fault_bearing"

    removed = engine.remove_machine("TR-107")
    assert removed["ok"]
    assert "TR-107" not in engine.telemetry and "TR-107" not in engine.features
    assert "TR-107" not in engine.get_all_machine_ids()
    engine.reset_fleet()
    assert len(engine.get_all_machine_ids()) == 6
    assert set(engine.telemetry) == set(engine.get_all_machine_ids())
    print("  TR-107 added, edited, removed, and reset without stale telemetry or features.")

    print("\nALL CHECKS PASSED! Member 1 (Vansh) module is 100% ready for Kunal, Mohit, and Shashi.")
    print("=" * 72)


if __name__ == "__main__":
    run_verification()
