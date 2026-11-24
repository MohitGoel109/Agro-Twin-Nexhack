"""
One-command verification script for Member 1 (Vansh).
Run from repo root: python ml/verify_ml.py
"""

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
    print("\nALL CHECKS PASSED! Member 1 (Vansh) module is 100% ready for Kunal, Mohit, and Shashi.")
    print("=" * 72)


if __name__ == "__main__":
    run_verification()
