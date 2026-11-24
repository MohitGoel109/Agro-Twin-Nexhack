"""
One-command verification script for Member 4 (Shashi).
Run from repo root (once ml/, ops/, and backend/ are in the repo):
    python frontend/verify_frontend.py
"""

import ast
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from frontend.api_client import AgroTwinClient
from frontend.charts import (
    build_availability_comparison_chart,
    build_downtime_bar_chart,
    build_risk_uncertainty_chart,
    build_telemetry_chart,
)


def run_verification():
    print("=" * 74)
    print("AGRO-TWIN | MEMBER 4 (SHASHI) FRONTEND & FULL-STACK VERIFICATION")
    print("=" * 74)

    # 1. Verify dashboard.py syntax is 100% clean
    dash_path = os.path.join(REPO_ROOT, "frontend", "dashboard.py")
    with open(dash_path, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=dash_path)
    print("[CHECK 1] frontend/dashboard.py syntax valid.")

    # 2. Initialize smart dual-mode client (auto-detects FastAPI or offline-safe local twin)
    client = AgroTwinClient(timeout=0.5)
    print(f"[CHECK 2] AgroTwinClient connected in mode: {client.mode}")

    # 3. Fetch Hour 35 snapshot & build Risk + Uncertainty Plotly chart
    fleet35 = client.get_fleet(step=35)
    assert len(fleet35["machines"]) == 6
    fig_risk = build_risk_uncertainty_chart(fleet35["machines"])
    assert len(fig_risk.data) == 1
    print(f"[CHECK 3] Fleet cards & Risk/Uncertainty chart built (Readiness: {fleet35['fleet_readiness_pct']}%).")

    # 4. Simulate live judge intervention (Acknowledge -> Schedule -> Verify Breakdown Prevented at Hr 48)
    ack = client.acknowledge_alert("TR-101", step=35)
    assert ack["ok"]
    sched = client.schedule_maintenance("TR-101", step=35)
    assert sched["ok"]
    fleet48 = client.get_fleet(step=48)
    tr101_48 = {m["machine_id"]: m for m in fleet48["machines"]}["TR-101"]
    assert tr101_48["breakdown_prevented"] is True and tr101_48["is_available"] is True
    print(f"[CHECK 4] Live UI Intervention flow verified: TR-101 saved at Hour 48 ({tr101_48['status']}).")

    # 5. Build Telemetry Replay chart (TR-101)
    hist = client.get_machine_history("TR-101", up_to_step=35)
    assert hist["ok"] and len(hist["history"]) == 36
    fig_tel = build_telemetry_chart("TR-101", hist["history"])
    assert len(fig_tel.data) == 4
    print("[CHECK 5] 4-sensor Telemetry Replay chart built cleanly.")

    # 6. Build Fair Baseline Comparison charts (Calendar-Only vs AI Twin)
    client.reset()
    comp = client.compare_baseline(calendar_interval=72)
    fig_avail = build_availability_comparison_chart(comp)
    fig_bar = build_downtime_bar_chart(comp)
    assert len(fig_avail.data) == 2 and len(fig_bar.data) == 2
    print(
        f"[CHECK 6] Baseline Comparison charts built (+{comp['improvement']['availability_gain_pct']}% "
        f"availability, {comp['improvement']['downtime_hours_saved']}h downtime saved)."
    )

    print("\nALL 4 MODULES INTEGRATED & VERIFIED! Run the live app with:")
    print("    streamlit run frontend/dashboard.py")
    print("=" * 74)


if __name__ == "__main__":
    run_verification()
