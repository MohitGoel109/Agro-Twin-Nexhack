"""
Agro-Twin: Constrained Maintenance Scheduler, Work-Order Tracker & Fair Baseline Comparator
Owner: Member 2 (Kunal) - Fleet Operations & Optimization Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery
"""

from copy import deepcopy
from ml.ml_engine import FleetTelemetryEngine

# Operational constants (hours)
PREVENTIVE_SERVICE_HOURS = 4       # Short planned service when fault is caught early
UNPLANNED_BREAKDOWN_HOURS = 18     # Severe field breakdown downtime during harvest
CALENDAR_SERVICE_HOURS = 4         # Routine fixed-schedule servicing duration
DEFAULT_CALENDAR_INTERVAL = 72     # Fixed calendar check every 72 hours (3 days)

# Harvest-window operational priority weights by machine type
MACHINE_CRITICALITY = {
    "Harvester": 1.25,   # Highest harvest bottleneck cost
    "Tractor": 1.10,     # Core sowing/plowing/hauling workhorse
    "Seeder": 1.00,
}

DEFAULT_PARTS_INVENTORY = {
    "Coolant Pump": 1,
    "Hydraulic Valve": 1,
    "Drive Bearing": 1,
    "Sensor Harness": 2,
}


class FleetOperationsScheduler:
    """
    Maintains live machine operational state (availability, downtime, open work orders),
    prioritizes constrained maintenance under scarce technicians & spare parts, tracks
    operator alert acknowledgements, and compares AI Twin vs. Calendar-Only servicing fairly.
    """

    def __init__(
        self,
        ml_engine: FleetTelemetryEngine = None,
        technicians_total: int = 2,
        parts_inventory: dict = None,
    ):
        self.ml_engine = ml_engine if ml_engine is not None else FleetTelemetryEngine()
        self.initial_technicians = int(technicians_total)
        self.initial_parts = deepcopy(
            parts_inventory if parts_inventory is not None else DEFAULT_PARTS_INVENTORY
        )
        self.reset_operations()

    def reset_operations(self):
        """Resets operational state, work orders, acknowledgements, and resource inventory."""
        self.technicians_total = self.initial_technicians
        self.parts_inventory = deepcopy(self.initial_parts)
        self.acknowledged_alerts = {}      # machine_id -> {step, note}
        self.work_orders = []              # list of work order dicts
        self.event_log = []                # chronological audit trail for judges
        self._wo_counter = 1
        # Tracks scheduled preventive interventions: machine_id -> {start_step, end_step, wo_id}
        self.preventive_interventions = {}

    def update_constraints(self, technicians_total: int = None, parts_inventory: dict = None) -> dict:
        """Lets the UI/demo adjust technician count or spare part stock live to test scarcity."""
        if technicians_total is not None:
            self.technicians_total = max(1, int(technicians_total))
        if parts_inventory is not None:
            for part, qty in parts_inventory.items():
                self.parts_inventory[part] = max(0, int(qty))
        self.event_log.append(
            {
                "event": "CONSTRAINTS_UPDATED",
                "technicians_total": self.technicians_total,
                "parts_inventory": deepcopy(self.parts_inventory),
            }
        )
        return self.get_resource_status(step=0)

    def _active_techs_at_step(self, step: int) -> int:
        """Counts how many technicians are currently occupied at hour `step`."""
        busy = 0
        for wo in self.work_orders:
            if wo["status"] in ("SCHEDULED", "IN_PROGRESS"):
                if wo["scheduled_start"] is not None and wo["scheduled_start"] <= step < wo["completion_step"]:
                    busy += 1
        return busy

    def get_resource_status(self, step: int) -> dict:
        """Returns live technician availability and spare-parts stock."""
        busy = self._active_techs_at_step(step)
        return {
            "technicians_total": self.technicians_total,
            "technicians_busy": busy,
            "technicians_available": max(0, self.technicians_total - busy),
            "parts_inventory": deepcopy(self.parts_inventory),
        }

    def _compute_priority_score(self, machine_snap: dict) -> float:
        """
        Computes a transparent 0-100 priority score combining:
        - Fault probability (core risk)
        - Model confidence (prevents noisy/missing telemetry from hijacking technicians)
        - Machine harvest criticality (Harvester > Tractor > Seeder)
        - Part availability boost (prioritize actionable jobs when parts are on hand)
        """
        if machine_snap["sensor_status"] != "CLEAN":
            return round(machine_snap["fault_probability"] * 15.0, 1)

        crit = MACHINE_CRITICALITY.get(machine_snap["type"], 1.0)
        part_ok = self.parts_inventory.get(machine_snap["part_needed"], 0) > 0
        actionable_factor = 1.0 if part_ok else 0.72

        raw_score = (
            machine_snap["fault_probability"]
            * (0.55 + 0.45 * machine_snap["confidence"])
            * crit
            * actionable_factor
            * 100.0
        )
        return round(min(100.0, max(0.0, raw_score)), 1)

    def _get_machine_work_order(self, machine_id: str):
        """Returns the most recent work order for a machine, if any."""
        matching = [wo for wo in self.work_orders if wo["machine_id"] == machine_id]
        return matching[-1] if matching else None

    def _machine_operational_status_at_step(self, m_snap: dict, step: int) -> dict:
        """
        Computes a single machine's operational state (availability, downtime, work order,
        recommended action) at hour `step`, accounting for any scheduled preventive repairs.
        """
        m_id = m_snap["machine_id"]
        wo = self._get_machine_work_order(m_id)
        intervention = self.preventive_interventions.get(m_id)
        b_step = m_snap["actual_breakdown_step"]

        wo_view = None
        if wo is not None:
            wo_view = dict(wo)
            if wo["status"] != "DEFERRED_SCARCITY":
                if step < wo["scheduled_start"]:
                    wo_view["status"] = "SCHEDULED"
                elif wo["scheduled_start"] <= step < wo["completion_step"]:
                    wo_view["status"] = "IN_PROGRESS"
                else:
                    wo_view["status"] = "COMPLETED"

        # Determine if preventive maintenance prevented the real breakdown
        prevented = (
            intervention is not None
            and (b_step is None or intervention["start_step"] < b_step)
        )

        # Compute cumulative downtime hours up to `step`
        downtime_hours = 0
        if prevented:
            overlap = max(0, min(step + 1, intervention["end_step"]) - intervention["start_step"])
            downtime_hours = overlap
        elif b_step is not None and step >= b_step:
            downtime_hours = min(step - b_step + 1, UNPLANNED_BREAKDOWN_HOURS)

        # Current availability status at exact hour `step`
        if prevented and intervention["start_step"] <= step < intervention["end_step"]:
            availability_state = "IN_PREVENTIVE_SERVICE"
            is_available = False
            effective_status = "SERVICING"
            effective_prob = 0.05
        elif prevented and step >= intervention["end_step"]:
            availability_state = "AVAILABLE"
            is_available = True
            effective_status = "SERVICED_READY"
            effective_prob = 0.02
        elif b_step is not None and b_step <= step < b_step + UNPLANNED_BREAKDOWN_HOURS:
            availability_state = "UNPLANNED_DOWNTIME"
            is_available = False
            effective_status = "BROKEN_DOWN"
            effective_prob = 1.0
        elif wo_view is not None and wo_view["status"] == "DEFERRED_SCARCITY":
            availability_state = "AVAILABLE_AT_RISK"
            is_available = True
            effective_status = m_snap["status"]
            effective_prob = m_snap["fault_probability"]
        else:
            availability_state = "AVAILABLE"
            is_available = True
            effective_status = m_snap["status"]
            effective_prob = m_snap["fault_probability"]

        priority_score = 0.0 if prevented else self._compute_priority_score(m_snap)
        part_qty = self.parts_inventory.get(m_snap["part_needed"], 0)
        techs_free = self.get_resource_status(step)["technicians_available"]

        # Plain-English operational recommendation for non-technical operators & judges
        if effective_status == "SERVICED_READY":
            action = "Service completed early - breakdown prevented; machine ready for harvest."
        elif effective_status == "SERVICING":
            rem = max(1, intervention["end_step"] - step)
            action = f"Preventive repair in progress ({rem}h remaining) using {m_snap['part_needed']}."
        elif effective_status == "BROKEN_DOWN":
            action = "Unplanned field breakdown! Emergency recovery required (18h downtime impact)."
        elif m_snap["sensor_status"] == "SENSOR_NOISE_FILTERED":
            action = "HOLD - Single-hour sensor glitch filtered out; do not waste a technician."
        elif m_snap["sensor_status"] == "MISSING_DATA_HOLD":
            action = "HOLD - Sensor dropout detected (high uncertainty); verify telemetry first."
        elif effective_prob >= 0.40:
            if part_qty <= 0:
                action = f"DEFERRED - Part '{m_snap['part_needed']}' out of stock; reorder urgently."
            elif techs_free <= 0:
                action = "QUEUED - All technicians busy; next free slot will be assigned."
            elif m_id in self.acknowledged_alerts:
                action = f"ACKNOWLEDGED - Ready to schedule 4h preventive service ({m_snap['part_needed']} in stock)."
            else:
                action = f"ACTION NEEDED - Acknowledge alert & schedule 4h preventive service ({m_snap['part_needed']} in stock)."
        else:
            action = "Continue normal field operation."

        return {
            **m_snap,
            "status": effective_status,
            "fault_probability": round(effective_prob, 3),
            "availability_state": availability_state,
            "is_available": is_available,
            "acknowledged": m_id in self.acknowledged_alerts,
            "acknowledged_at_step": self.acknowledged_alerts[m_id]["step"]
            if m_id in self.acknowledged_alerts
            else None,
            "priority_score": priority_score,
            "part_in_stock": part_qty,
            "cumulative_downtime_hours": downtime_hours,
            "breakdown_prevented": prevented,
            "open_work_order": wo_view,
            "recommended_action": action,
        }

    def get_operational_fleet_state(self, step: int) -> dict:
        """
        Main unified operational state consumed by backend/app.py and frontend/dashboard.py.
        Combines Vansh's ML predictions with Kunal's availability, downtime, work orders & priority queue.
        """
        step = max(0, min(int(step), self.ml_engine.num_steps - 1))
        raw_snaps = self.ml_engine.get_fleet_snapshot(step)
        machines = [self._machine_operational_status_at_step(m, step) for m in raw_snaps]

        available_count = sum(1 for m in machines if m["is_available"])
        readiness_pct = round((available_count / len(machines)) * 100.0, 1)
        total_downtime = sum(m["cumulative_downtime_hours"] for m in machines)
        open_wos = [
            m["open_work_order"]
            for m in machines
            if m["open_work_order"] is not None and m["open_work_order"]["status"] != "COMPLETED"
        ]
        prevented_count = sum(1 for m in machines if m["breakdown_prevented"])

        priority_queue = sorted(
            [
                {
                    "machine_id": m["machine_id"],
                    "name": m["name"],
                    "status": m["status"],
                    "priority_score": m["priority_score"],
                    "fault_probability": m["fault_probability"],
                    "confidence": m["confidence"],
                    "part_needed": m["part_needed"],
                    "part_in_stock": m["part_in_stock"],
                    "acknowledged": m["acknowledged"],
                    "recommended_action": m["recommended_action"],
                }
                for m in machines
                if m["priority_score"] >= 20.0 or m["status"] in ("EARLY_WARNING", "CRITICAL_WARNING", "BROKEN_DOWN")
            ],
            key=lambda x: x["priority_score"],
            reverse=True,
        )

        return {
            "step": step,
            "fleet_readiness_pct": readiness_pct,
            "machines_available": available_count,
            "machines_total": len(machines),
            "total_downtime_hours": total_downtime,
            "breakdowns_prevented": prevented_count,
            "open_work_orders_count": len(open_wos),
            "resources": self.get_resource_status(step),
            "priority_queue": priority_queue,
            "machines": machines,
            "work_orders": self.get_all_work_orders(step),
            "recent_events": self.event_log[-10:],
        }

    def get_all_work_orders(self, current_step: int) -> list:
        """Returns all work orders with up-to-date lifecycle statuses for `current_step`."""
        result = []
        for wo in self.work_orders:
            item = dict(wo)
            if item["status"] != "DEFERRED_SCARCITY":
                if current_step < item["scheduled_start"]:
                    item["status"] = "SCHEDULED"
                elif item["scheduled_start"] <= current_step < item["completion_step"]:
                    item["status"] = "IN_PROGRESS"
                else:
                    item["status"] = "COMPLETED"
            result.append(item)
        return result

    def acknowledge_alert(self, machine_id: str, current_step: int, note: str = "Alert acknowledged by fleet manager") -> dict:
        """Records explicit operator acknowledgement of a developing fault alert."""
        if machine_id not in self.ml_engine.get_all_machine_ids():
            return {"ok": False, "message": f"Unknown machine_id: {machine_id}"}

        self.acknowledged_alerts[machine_id] = {
            "step": int(current_step),
            "note": note,
        }
        event = {
            "step": int(current_step),
            "event": "ALERT_ACKNOWLEDGED",
            "machine_id": machine_id,
            "note": note,
        }
        self.event_log.append(event)
        return {"ok": True, "message": f"Alert acknowledged for {machine_id} at Hour {current_step}.", "event": event}

    def schedule_maintenance(self, machine_id: str, current_step: int) -> dict:
        """
        Schedules constrained preventive maintenance for `machine_id` at `current_step`.
        Checks spare parts & technician slots, updates fleet readiness, and prevents breakdown.
        """
        current_step = max(0, min(int(current_step), self.ml_engine.num_steps - 1))
        snaps = {m["machine_id"]: m for m in self.ml_engine.get_fleet_snapshot(current_step)}
        if machine_id not in snaps:
            return {"ok": False, "message": f"Unknown machine_id: {machine_id}"}

        if machine_id in self.preventive_interventions:
            return {"ok": False, "message": f"{machine_id} already has preventive maintenance scheduled."}

        m_snap = snaps[machine_id]

        if machine_id not in self.acknowledged_alerts:
            self.acknowledge_alert(machine_id, current_step, note="Auto-acknowledged upon work-order scheduling")

        part_needed = m_snap["part_needed"]
        part_stock = self.parts_inventory.get(part_needed, 0)
        res_status = self.get_resource_status(current_step)
        priority_score = self._compute_priority_score(m_snap)

        wo_id = f"WO-{self._wo_counter:03d}"
        self._wo_counter += 1

        # Enforce spare-parts constraint
        if part_stock <= 0:
            wo = {
                "wo_id": wo_id,
                "machine_id": machine_id,
                "machine_name": m_snap["name"],
                "part_needed": part_needed,
                "status": "DEFERRED_SCARCITY",
                "created_step": current_step,
                "scheduled_start": None,
                "completion_step": None,
                "priority_score": priority_score,
                "reason": f"Deferred: Spare part '{part_needed}' is out of stock.",
            }
            self.work_orders.append(wo)
            self.event_log.append({"step": current_step, "event": "WO_DEFERRED_PARTS", "machine_id": machine_id, "wo_id": wo_id})
            return {"ok": False, "deferred": True, "message": wo["reason"], "work_order": wo}

        # Enforce technician availability constraint
        start_step = current_step
        if res_status["technicians_available"] <= 0:
            while start_step < self.ml_engine.num_steps - 1 and self._active_techs_at_step(start_step) >= self.technicians_total:
                start_step += 1

        completion_step = min(self.ml_engine.num_steps, start_step + PREVENTIVE_SERVICE_HOURS)

        self.parts_inventory[part_needed] = part_stock - 1

        wo = {
            "wo_id": wo_id,
            "machine_id": machine_id,
            "machine_name": m_snap["name"],
            "part_needed": part_needed,
            "status": "IN_PROGRESS" if start_step == current_step else "SCHEDULED",
            "created_step": current_step,
            "scheduled_start": start_step,
            "completion_step": completion_step,
            "priority_score": priority_score,
            "reason": f"Preventive 4h service scheduled ({part_needed} reserved; saves ~14h unplanned downtime).",
        }
        self.work_orders.append(wo)
        self.preventive_interventions[machine_id] = {
            "start_step": start_step,
            "end_step": completion_step,
            "wo_id": wo_id,
        }
        self.event_log.append(
            {
                "step": current_step,
                "event": "WO_SCHEDULED",
                "machine_id": machine_id,
                "wo_id": wo_id,
                "scheduled_start": start_step,
                "completion_step": completion_step,
            }
        )

        return {
            "ok": True,
            "deferred": False,
            "message": f"{wo_id} scheduled for {machine_id} (Hours {start_step}-{completion_step}) using 1x {part_needed}.",
            "work_order": wo,
            "resources": self.get_resource_status(current_step),
        }

    def compare_against_calendar_baseline(
        self,
        up_to_step: int = None,
        calendar_interval: int = DEFAULT_CALENDAR_INTERVAL,
    ) -> dict:
        """
        Fairly replays the EXACT SAME telemetry scenario and resource constraints under:
        1) Calendar-Only Servicing (fixed interval every `calendar_interval` hours)
        2) Agro-Twin AI Condition-Based Servicing (noise-filtered, uncertainty-aware)
        """
        max_step = self.ml_engine.num_steps - 1 if up_to_step is None else min(int(up_to_step), self.ml_engine.num_steps - 1)
        total_hours = max_step + 1
        machine_ids = self.ml_engine.get_all_machine_ids()
        n_machines = len(machine_ids)

        all_snaps = [
            {m["machine_id"]: m for m in self.ml_engine.get_fleet_snapshot(t)}
            for t in range(total_hours)
        ]

        # ---------------- POLICY 1: CALENDAR-ONLY BASELINE ----------------
        cal_repaired = set()
        cal_down_until = {m_id: -1 for m_id in machine_ids}
        cal_downtime = 0
        cal_unplanned_breakdowns = 0
        cal_unnecessary_services = 0
        cal_hourly_avail = []

        for t in range(total_hours):
            avail_now = 0
            for m_id in machine_ids:
                snap = all_snaps[t][m_id]
                b_step = snap["actual_breakdown_step"]

                if t < cal_down_until[m_id]:
                    cal_downtime += 1
                    continue

                if t > 0 and (t % calendar_interval == 0):
                    cal_down_until[m_id] = t + CALENDAR_SERVICE_HOURS
                    cal_downtime += 1
                    if b_step is not None and t < b_step:
                        cal_repaired.add(m_id)
                    else:
                        cal_unnecessary_services += 1
                    continue

                if b_step is not None and t == b_step and m_id not in cal_repaired:
                    cal_unplanned_breakdowns += 1
                    cal_down_until[m_id] = t + UNPLANNED_BREAKDOWN_HOURS
                    cal_repaired.add(m_id)
                    cal_downtime += 1
                    continue

                avail_now += 1
            cal_hourly_avail.append(round((avail_now / n_machines) * 100.0, 1))

        # ---------------- POLICY 2: AGRO-TWIN AI CONDITION-BASED ----------------
        ai_parts = deepcopy(self.initial_parts)
        ai_tech_busy_until = []
        ai_repaired = set()
        ai_down_until = {m_id: -1 for m_id in machine_ids}
        ai_downtime = 0
        ai_unplanned_breakdowns = 0
        ai_preventive_services = 0
        ai_lead_times = []
        ai_noise_or_missing_holds = 0
        ai_hourly_avail = []

        for t in range(total_hours):
            ai_tech_busy_until = [end_t for end_t in ai_tech_busy_until if end_t > t]

            for m_id in machine_ids:
                if all_snaps[t][m_id]["sensor_status"] in ("SENSOR_NOISE_FILTERED", "MISSING_DATA_HOLD"):
                    ai_noise_or_missing_holds += 1

            candidates = []
            for m_id in machine_ids:
                if m_id in ai_repaired or t < ai_down_until[m_id]:
                    continue
                snap = all_snaps[t][m_id]
                if snap["sensor_status"] == "CLEAN" and snap["fault_probability"] >= 0.65:
                    crit = MACHINE_CRITICALITY.get(snap["type"], 1.0)
                    score = snap["fault_probability"] * snap["confidence"] * crit
                    candidates.append((score, m_id, snap))

            candidates.sort(key=lambda x: x[0], reverse=True)

            for _, m_id, snap in candidates:
                part = snap["part_needed"]
                if len(ai_tech_busy_until) < self.technicians_total and ai_parts.get(part, 0) > 0:
                    ai_parts[part] -= 1
                    end_t = t + PREVENTIVE_SERVICE_HOURS
                    ai_tech_busy_until.append(end_t)
                    ai_down_until[m_id] = end_t
                    ai_repaired.add(m_id)
                    ai_preventive_services += 1
                    b_step = snap["actual_breakdown_step"]
                    if b_step is not None and b_step > t:
                        ai_lead_times.append(b_step - t)

            avail_now = 0
            for m_id in machine_ids:
                snap = all_snaps[t][m_id]
                b_step = snap["actual_breakdown_step"]

                if t < ai_down_until[m_id]:
                    ai_downtime += 1
                    continue

                if b_step is not None and t == b_step and m_id not in ai_repaired:
                    ai_unplanned_breakdowns += 1
                    ai_down_until[m_id] = t + UNPLANNED_BREAKDOWN_HOURS
                    ai_repaired.add(m_id)
                    ai_downtime += 1
                    continue

                avail_now += 1
            ai_hourly_avail.append(round((avail_now / n_machines) * 100.0, 1))

        total_machine_hours = n_machines * total_hours
        cal_avail_pct = round(((total_machine_hours - cal_downtime) / total_machine_hours) * 100.0, 2)
        ai_avail_pct = round(((total_machine_hours - ai_downtime) / total_machine_hours) * 100.0, 2)
        avg_lead_time = round(sum(ai_lead_times) / len(ai_lead_times), 1) if ai_lead_times else 0.0

        hourly_series = [
            {
                "step": t,
                "calendar_availability_pct": cal_hourly_avail[t],
                "ai_twin_availability_pct": ai_hourly_avail[t],
            }
            for t in range(total_hours)
        ]

        return {
            "simulation_hours": total_hours,
            "calendar_interval_hours": calendar_interval,
            "constraints_used": {
                "technicians_total": self.technicians_total,
                "initial_parts_inventory": deepcopy(self.initial_parts),
            },
            "calendar_only": {
                "fleet_availability_pct": cal_avail_pct,
                "total_downtime_hours": cal_downtime,
                "unplanned_breakdowns": cal_unplanned_breakdowns,
                "unnecessary_services": cal_unnecessary_services,
                "avg_warning_lead_time_hours": 0.0,
            },
            "ai_twin": {
                "fleet_availability_pct": ai_avail_pct,
                "total_downtime_hours": ai_downtime,
                "unplanned_breakdowns": ai_unplanned_breakdowns,
                "preventive_services_completed": ai_preventive_services,
                "avg_warning_lead_time_hours": avg_lead_time,
                "noisy_or_missing_alerts_held": ai_noise_or_missing_holds,
            },
            "improvement": {
                "availability_gain_pct": round(ai_avail_pct - cal_avail_pct, 2),
                "downtime_hours_saved": cal_downtime - ai_downtime,
                "breakdowns_avoided": cal_unplanned_breakdowns - ai_unplanned_breakdowns,
                "avg_warning_lead_time_hours": avg_lead_time,
            },
            "hourly_series": hourly_series,
        }


if __name__ == "__main__":
    sched = FleetOperationsScheduler()
    comp = sched.compare_against_calendar_baseline()
    print("=== AGRO-TWIN FAIR BASELINE COMPARISON (120h HARVEST WINDOW) ===")
    print("Calendar-Only :", comp["calendar_only"])
    print("Agro-Twin AI  :", comp["ai_twin"])
    print("Net Gains     :", comp["improvement"])
