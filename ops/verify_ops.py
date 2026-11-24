"""
One-command verification script for Member 2 (Kunal).
Run from repo root (once Vansh's ml/ folder is in the repo):
    python ops/verify_ops.py
"""

import os
import sys
import types

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from ml.ml_engine import FleetTelemetryEngine
except ModuleNotFoundError:
    class FleetTelemetryEngine:
        """
        Minimal deterministic stub for local verification when ml/ is unavailable.
        Implements only the interface used by ops.scheduler and this script.
        """

        def __init__(self):
            self.num_steps = 121  # 0..120 inclusive (120-hour harvest window)
            self._machines = [
                {
                    "machine_id": "TR-101",
                    "name": "Tractor 101",
                    "type": "Tractor",
                    "part_needed": "Coolant Pump",
                    "actual_breakdown_step": 46,
                },
                {
                    "machine_id": "HV-202",
                    "name": "Harvester 202",
                    "type": "Harvester",
                    "part_needed": "Hydraulic Valve",
                    "actual_breakdown_step": 60,
                },
                {
                    "machine_id": "SD-303",
                    "name": "Seeder 303",
                    "type": "Seeder",
                    "part_needed": "Drive Bearing",
                    "actual_breakdown_step": 90,
                },
            ]

        def get_all_machine_ids(self):
            return [m["machine_id"] for m in self._machines]

        def _machine_snapshot(self, machine, step):
            b_step = machine["actual_breakdown_step"]
            # Default healthy state
            status = "NORMAL"
            fault_probability = 0.05
            confidence = 0.95
            sensor_status = "CLEAN"

            # Rising risk ahead of known breakdowns for early-warning behavior
            if b_step is not None and step < b_step:
                hours_to_breakdown = b_step - step
                if hours_to_breakdown <= 30:
                    fault_probability = 0.72
                    status = "CRITICAL_WARNING" if hours_to_breakdown <= 15 else "EARLY_WARNING"
                    confidence = 0.93
                elif hours_to_breakdown <= 45:
                    fault_probability = 0.45
                    status = "EARLY_WARNING"
                    confidence = 0.88

            # If not prevented, machine reaches breakdown at b_step (scheduler handles downtime)
            if b_step is not None and step >= b_step:
                status = "CRITICAL_WARNING"
                fault_probability = 1.0
                confidence = 0.99

            return {
                "machine_id": machine["machine_id"],
                "name": machine["name"],
                "type": machine["type"],
                "part_needed": machine["part_needed"],
                "status": status,
                "fault_probability": fault_probability,
                "confidence": confidence,
                "sensor_status": sensor_status,
                "actual_breakdown_step": b_step,
            }

        def get_fleet_snapshot(self, step):
            step = max(0, min(int(step), self.num_steps - 1))
            return [self._machine_snapshot(m, step) for m in self._machines]

    _ml_mod = types.ModuleType("ml")
    _ml_engine_mod = types.ModuleType("ml.ml_engine")
    _ml_engine_mod.FleetTelemetryEngine = FleetTelemetryEngine
    _ml_mod.ml_engine = _ml_engine_mod
    sys.modules["ml"] = _ml_mod
    sys.modules["ml.ml_engine"] = _ml_engine_mod

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

    # TEST 4: ROI Summary and Multilingual SMS Job Card
    print("\n[TEST 4] ROI Summary and Multilingual SMS Job Card:")
    sched.reset_operations()
    roi = sched.compute_roi_summary()
    print(
        f"  ROI Summary   -> Net Savings: INR {roi['net_savings_inr']} | "
        f"ROI Multiple: {roi['roi_multiple']}x | Breakdowns Avoided: {roi['breakdowns_avoided']}"
    )
    assert roi["net_savings_inr"] > 0
    assert roi["roi_multiple"] > 1

    card = sched.generate_sms_job_card("TR-101", 35)
    print(f"  SMS EN        -> {card['sms_en']}")
    print(f"  SMS HI        -> {card['sms_hi']}")
    assert card["ok"] is True
    assert isinstance(card["sms_en"], str) and card["sms_en"]
    assert len(card["sms_en"]) <= 160
    assert isinstance(card["sms_hi"], str) and card["sms_hi"]
    assert isinstance(card["checklist"], list) and len(card["checklist"]) == 4

    print("\nALL CHECKS PASSED! Member 2 (Kunal) module is 100% ready for Mohit and Shashi.")
    print("=" * 74)


if __name__ == "__main__":
    run_verification()
