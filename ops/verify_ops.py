"""
One-command verification script for Member 2 (Kunal).
Run from repo root (once Vansh's ml/ folder is in the repo):
    python ops/verify_ops.py
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.ml_engine import FleetTelemetryEngine
from ops.scheduler import FleetOperationsScheduler


def run_verification():
    ml_engine = FleetTelemetryEngine()
    sched = FleetOperationsScheduler(ml_engine=ml_engine, technicians_total=2)

    print("=" * 74)
    print("AGRO-TWIN | MEMBER 2 (KUNAL) OPERATIONS & SCHEDULER VERIFICATION")
    print("=" * 74)

    # TEST 1: Live Intervention Flow (Replay fault -> Acknowledge -> Schedule -> Readiness Change)
    print("\n[TEST 1] Live Intervention on TR-101 at Hour 35 (Before Hour 46 Breakdown):")
    before = sched.get_operational_fleet_state(step=35)
    tr101_before = {m["machine_id"]: m for m in before["machines"]}["TR-101"]
    print(f"  Before Action -> Status: {tr101_before['status']} | Priority: {tr101_before['priority_score']} | Action: {tr101_before['recommended_action']}")
    assert tr101_before["status"] in ("EARLY_WARNING", "CRITICAL_WARNING")

    ack = sched.acknowledge_alert("TR-101", current_step=35)
    assert ack["ok"]
    print(f"  Acknowledge   -> {ack['message']}")

    wo_res = sched.schedule_maintenance("TR-101", current_step=35)
    assert wo_res["ok"]
    print(f"  Schedule WO   -> {wo_res['message']}")

    during = sched.get_operational_fleet_state(step=36)
    tr101_during = {m["machine_id"]: m for m in during["machines"]}["TR-101"]
    print(f"  Hour 36 State -> {tr101_during['availability_state']} | Fleet Readiness: {during['fleet_readiness_pct']}%")
    assert tr101_during["availability_state"] == "IN_PREVENTIVE_SERVICE"

    after_breakdown_hour = sched.get_operational_fleet_state(step=48)
    tr101_after = {m["machine_id"]: m for m in after_breakdown_hour["machines"]}["TR-101"]
    print(f"  Hour 48 State -> {tr101_after['status']} (Prevented Breakdown: {tr101_after['breakdown_prevented']}) | Downtime: {tr101_after['cumulative_downtime_hours']}h")
    assert tr101_after["breakdown_prevented"] is True
    assert tr101_after["is_available"] is True
    assert tr101_after["cumulative_downtime_hours"] == 4

    # TEST 2: Resource Scarcity Check (Out-of-stock spare part defers gracefully)
    print("\n[TEST 2] Spare Parts Scarcity Check (Zero Hydraulic Valves):")
    sched.update_constraints(parts_inventory={"Hydraulic Valve": 0})
    deferred = sched.schedule_maintenance("HV-202", current_step=50)
    print(f"  HV-202 Result -> {deferred['message']}")
    assert deferred["deferred"] is True

    # TEST 3: Fair Calendar-Only vs AI Twin Comparison
    sched.reset_operations()
    comp = sched.compare_against_calendar_baseline()
    print("\n[TEST 3] Fair Replay: Calendar-Only vs Agro-Twin AI (120-Hour Harvest Window):")
    print(f"  Calendar-Only -> Availability: {comp['calendar_only']['fleet_availability_pct']}% | Downtime: {comp['calendar_only']['total_downtime_hours']}h | Unplanned Breakdowns: {comp['calendar_only']['unplanned_breakdowns']} | Lead Time: {comp['calendar_only']['avg_warning_lead_time_hours']}h")
    print(f"  Agro-Twin AI  -> Availability: {comp['ai_twin']['fleet_availability_pct']}% | Downtime: {comp['ai_twin']['total_downtime_hours']}h | Unplanned Breakdowns: {comp['ai_twin']['unplanned_breakdowns']} | Lead Time: {comp['ai_twin']['avg_warning_lead_time_hours']}h")
    print(f"  Net Gains     -> +{comp['improvement']['availability_gain_pct']}% Availability | {comp['improvement']['downtime_hours_saved']}h Downtime Saved | {comp['improvement']['breakdowns_avoided']} Breakdowns Avoided | {comp['ai_twin']['noisy_or_missing_alerts_held']} Noisy/Missing Holds")

    assert comp["ai_twin"]["fleet_availability_pct"] > comp["calendar_only"]["fleet_availability_pct"]
    assert comp["ai_twin"]["total_downtime_hours"] < comp["calendar_only"]["total_downtime_hours"]
    assert comp["ai_twin"]["avg_warning_lead_time_hours"] > 0

    print("\nALL CHECKS PASSED! Member 2 (Kunal) module is 100% ready for Mohit and Shashi.")
    print("=" * 74)


if __name__ == "__main__":
    run_verification()
