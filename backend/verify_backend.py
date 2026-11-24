"""
One-command verification script for Member 3 (Mohit).
Run from repo root (once Vansh's ml/ and Kunal's ops/ folders are in the repo):
    python backend/verify_backend.py
"""

import ast
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.state import TwinStateManager


def run_verification():
    print("=" * 74)
    print("AGRO-TWIN | MEMBER 3 (MOHIT) BACKEND & TWIN STATE VERIFICATION")
    print("=" * 74)

    # 1. Verify FastAPI app.py syntax is 100% valid
    app_path = os.path.join(REPO_ROOT, "backend", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=app_path)
    print("[CHECK 1] backend/app.py syntax valid.")

    # 2. If FastAPI is installed, verify app imports cleanly & routes are registered
    try:
        from backend.app import app as fastapi_app

        route_paths = sorted({r.path for r in fastapi_app.routes})
        required = {
            "/health",
            "/fleet",
            "/step",
            "/machines/{machine_id}/history",
            "/acknowledge",
            "/schedule",
            "/inject-fault",
            "/constraints",
            "/work-orders",
            "/compare",
            "/reset",
        }
        missing = required - set(route_paths)
        assert not missing, f"Missing FastAPI routes: {missing}"
        print(f"[CHECK 2] FastAPI loaded with {len(required)} verified REST endpoints.")
    except ImportError:
        print("[CHECK 2] FastAPI not installed in current Python env (install via pip install -r requirements.txt).")

    # 3. Full end-to-end TwinStateManager workflow test (ml/ + ops/ + backend/)
    twin = TwinStateManager(num_steps=120, technicians_total=2)

    health = twin.get_health()
    assert health["status"] == "ok" and len(health["machine_ids"]) == 6
    print(f"[CHECK 3] Health OK | Fleet size: {len(health['machine_ids'])} | Model: {health['model_info']['model_type']}")

    # Jump to Hour 35 where TR-101 has a developing fault, SD-304 has spike, TR-105 has missing data
    state35 = twin.advance_step(target_step=35)
    by_id = {m["machine_id"]: m for m in state35["machines"]}
    assert by_id["TR-101"]["status"] == "CRITICAL_WARNING"
    assert by_id["SD-304"]["sensor_status"] == "SENSOR_NOISE_FILTERED"
    assert by_id["TR-105"]["sensor_status"] == "MISSING_DATA_HOLD"
    print(f"[CHECK 4] Hour 35 replay synced | Readiness: {state35['fleet_readiness_pct']}% | Priority #1: {state35['priority_queue'][0]['machine_id']}")

    # Acknowledge + Schedule TR-101
    ack = twin.acknowledge_alert("TR-101", step=35)
    assert ack["ok"]
    sched = twin.schedule_maintenance("TR-101", step=35)
    assert sched["ok"]
    print(f"[CHECK 5] Intervention OK | {sched['message']}")

    # Machine history retrieval
    hist = twin.get_machine_detail("TR-101", up_to_step=35)
    assert hist["ok"] and len(hist["history"]) == 36
    print(f"[CHECK 6] Telemetry history OK | {len(hist['history'])} hourly points returned for TR-101.")

    # Live fault injection on healthy machine HV-206
    inj = twin.inject_fault("HV-206", start_step=50, fault_type="fault_bearing")
    assert inj["ok"]
    state62 = twin.get_fleet_state(step=62)
    hv206 = {m["machine_id"]: m for m in state62["machines"]}["HV-206"]
    assert hv206["fault_probability"] >= 0.40
    print(f"[CHECK 7] Live fault injection OK | HV-206 at Hour 62 -> {hv206['status']} ({hv206['fault_probability']*100:.1f}% risk)")

    # Reset and run baseline comparison
    reset_res = twin.reset()
    assert reset_res["ok"] and twin.current_step == 0
    comp = twin.get_baseline_comparison()
    assert comp["improvement"]["downtime_hours_saved"] > 0
    print(
        f"[CHECK 8] Reset & Fair Comparison OK | AI Twin saves {comp['improvement']['downtime_hours_saved']}h "
        f"downtime (+{comp['improvement']['availability_gain_pct']}% availability)."
    )

    print("\nALL CHECKS PASSED! Member 3 (Mohit) backend is 100% ready for Shashi's dashboard.")
    print("=" * 74)


if __name__ == "__main__":
    run_verification()
