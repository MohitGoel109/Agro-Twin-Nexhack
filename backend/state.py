"""
Agro-Twin: Unified Digital Twin State Manager
Owner: Member 3 (Mohit) - Backend & Twin State Architect
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery

Bridges Member 1's leak-free ML engine (ml/) and Member 2's constrained
maintenance scheduler (ops/) into a single stateful simulation controller.
"""

from typing import Dict, Optional

import requests

from ml.ml_engine import FleetTelemetryEngine
from ops.scheduler import FleetOperationsScheduler


class TwinStateManager:
    """
    Maintains the live replay clock (`current_step`) and coordinates all
    telemetry, prediction, scheduling, fault-injection, and comparison calls.
    """

    def __init__(self, num_steps: int = 120, technicians_total: int = 2):
        self.num_steps = int(num_steps)
        self.ml_engine = FleetTelemetryEngine(num_steps=self.num_steps)
        self.scheduler = FleetOperationsScheduler(
            ml_engine=self.ml_engine,
            technicians_total=technicians_total,
        )
        self.current_step = 0
        self.webhook_url = ""
        self.webhook_log = []

    def _clamp_step(self, step: Optional[int]) -> int:
        if step is None:
            return self.current_step
        return max(0, min(int(step), self.num_steps - 1))

    def get_health(self) -> dict:
        """Returns service health, active replay hour, and leak-free ML metadata."""
        return {
            "status": "ok",
            "service": "Agro-Twin Predictive Maintenance API",
            "current_step": self.current_step,
            "max_step": self.num_steps - 1,
            "machine_ids": self.ml_engine.get_all_machine_ids(),
            "model_info": self.ml_engine.get_model_info(),
        }

    def get_fleet_state(self, step: Optional[int] = None) -> dict:
        """Returns unified operational fleet state; syncs clock if `step` is provided."""
        if step is not None:
            self.current_step = self._clamp_step(step)
        return self.scheduler.get_operational_fleet_state(self.current_step)

    def advance_step(self, delta: int = 1, target_step: Optional[int] = None) -> dict:
        """Advances or jumps the simulation clock and returns the updated fleet state."""
        if target_step is not None:
            self.current_step = self._clamp_step(target_step)
        else:
            self.current_step = self._clamp_step(self.current_step + int(delta))
        return self.scheduler.get_operational_fleet_state(self.current_step)

    def get_machine_detail(self, machine_id: str, up_to_step: Optional[int] = None) -> dict:
        """Returns live operational state + hourly sensor telemetry history for one machine."""
        if machine_id not in self.ml_engine.get_all_machine_ids():
            return {"ok": False, "error": f"Machine '{machine_id}' not found."}

        step = self._clamp_step(up_to_step)
        fleet = self.scheduler.get_operational_fleet_state(step)
        machine_info = next(
            (m for m in fleet["machines"] if m["machine_id"] == machine_id),
            None,
        )
        history = self.ml_engine.get_machine_history(machine_id, up_to_step=step)
        return {
            "ok": True,
            "machine_id": machine_id,
            "step": step,
            "machine": machine_info,
            "history": history,
        }

    def acknowledge_alert(
        self,
        machine_id: str,
        step: Optional[int] = None,
        note: str = "Alert acknowledged by fleet manager",
    ) -> dict:
        """Acknowledges an active alert and returns updated fleet readiness."""
        use_step = self._clamp_step(step)
        self.current_step = use_step
        res = self.scheduler.acknowledge_alert(machine_id, current_step=use_step, note=note)
        return {
            **res,
            "fleet_state": self.scheduler.get_operational_fleet_state(use_step),
        }

    def schedule_maintenance(
        self,
        machine_id: str,
        step: Optional[int] = None,
    ) -> dict:
        """Schedules constrained preventive maintenance and returns updated readiness."""
        use_step = self._clamp_step(step)
        self.current_step = use_step
        res = self.scheduler.schedule_maintenance(machine_id, current_step=use_step)
        if res.get("ok"):
            self._emit_webhook(
                "maintenance_scheduled",
                {"machine_id": machine_id, "result": res},
            )
        return {
            **res,
            "fleet_state": self.scheduler.get_operational_fleet_state(use_step),
        }

    def inject_fault(
        self,
        machine_id: str,
        start_step: Optional[int] = None,
        fault_type: str = "fault_engine",
    ) -> dict:
        """Injects a developing fault into any machine for live judge testing."""
        use_step = self._clamp_step(start_step)
        ok = self.ml_engine.inject_fault(
            machine_id=machine_id,
            start_step=use_step,
            fault_type=fault_type,
        )
        if not ok:
            return {"ok": False, "message": f"Unknown machine_id: {machine_id}"}

        self._emit_webhook(
            "fault_injected",
            {
                "machine_id": machine_id,
                "start_step": use_step,
                "fault_type": fault_type,
            },
        )
        return {
            "ok": True,
            "message": f"Injected '{fault_type}' into {machine_id} starting at Hour {use_step}.",
            "machine_id": machine_id,
            "start_step": use_step,
            "fault_type": fault_type,
            "fleet_state": self.scheduler.get_operational_fleet_state(self.current_step),
        }

    def set_webhook_url(self, url: str) -> dict:
        """Sets the optional HTTP webhook destination; an empty URL simulates locally."""
        self.webhook_url = str(url).strip()
        return {
            "ok": True,
            "webhook_url": self.webhook_url,
            "target": self.webhook_url or "SIMULATED_LOCAL",
        }

    def get_webhook_log(self) -> list:
        """Returns a copy of webhook delivery outcomes recorded during this session."""
        return [dict(entry) for entry in self.webhook_log]

    def _emit_webhook(self, event_type: str, payload: dict) -> dict:
        """Attempts webhook delivery and records the outcome without disrupting operations."""
        target = self.webhook_url or "SIMULATED_LOCAL"
        delivered = False
        status = "simulated locally"

        if self.webhook_url.startswith(("http://", "https://")):
            try:
                response = requests.post(
                    self.webhook_url,
                    json={
                        "event": event_type,
                        "step": self.current_step,
                        "payload": payload,
                    },
                    timeout=2.0,
                )
                response.raise_for_status()
                delivered = True
                status = f"HTTP {response.status_code}"
            except requests.RequestException as exc:
                status = str(exc)
        elif self.webhook_url:
            status = "webhook URL must start with http:// or https://"

        entry = {
            "step": self.current_step,
            "event_type": event_type,
            "target": target,
            "delivered": delivered,
            "status": status,
        }
        self.webhook_log.append(entry)
        return dict(entry)

    def set_weather_mode(self, mode: str) -> dict:
        """Sets ML weather mode when supported and returns the resulting fleet state."""
        if hasattr(self.ml_engine, "set_weather_mode"):
            result = self.ml_engine.set_weather_mode(mode)
        else:
            result = {"ok": False, "message": "Weather mode is unavailable."}
        return {
            **result,
            "fleet_state": self.scheduler.get_operational_fleet_state(self.current_step),
        }

    def get_roi_summary(
        self,
        hourly_loss_inr: float = 2500.0,
        preventive_part_cost_inr: float = 2200.0,
        calendar_interval: int = 72,
    ) -> dict:
        """Returns scheduler ROI metrics when the scheduler supports the calculation."""
        if not hasattr(self.scheduler, "compute_roi_summary"):
            return {"ok": False, "message": "ROI summary is unavailable."}
        return self.scheduler.compute_roi_summary(
            hourly_loss_inr=hourly_loss_inr,
            preventive_part_cost_inr=preventive_part_cost_inr,
            calendar_interval=calendar_interval,
        )

    def get_sms_job_card(self, machine_id: str, step: Optional[int] = None) -> dict:
        """Returns a scheduler-generated SMS job card when supported."""
        if not hasattr(self.scheduler, "generate_sms_job_card"):
            return {"ok": False, "message": "SMS job cards are unavailable."}
        return self.scheduler.generate_sms_job_card(
            machine_id,
            current_step=self._clamp_step(step),
        )

    def update_constraints(
        self,
        technicians_total: Optional[int] = None,
        parts_inventory: Optional[Dict[str, int]] = None,
    ) -> dict:
        """Updates technician count or spare-parts stock live to demonstrate scarcity."""
        self.scheduler.update_constraints(
            technicians_total=technicians_total,
            parts_inventory=parts_inventory,
        )
        return {
            "ok": True,
            "message": "Operational constraints updated.",
            "resources": self.scheduler.get_resource_status(self.current_step),
            "fleet_state": self.scheduler.get_operational_fleet_state(self.current_step),
        }

    def get_work_orders(self, step: Optional[int] = None) -> dict:
        """Returns all work orders with live status at `step`."""
        use_step = self._clamp_step(step)
        return {
            "step": use_step,
            "work_orders": self.scheduler.get_all_work_orders(use_step),
        }

    def get_baseline_comparison(
        self,
        up_to_step: Optional[int] = None,
        calendar_interval: int = 72,
    ) -> dict:
        """Runs fair Calendar-Only vs. Agro-Twin AI replay comparison."""
        use_step = None if up_to_step is None else self._clamp_step(up_to_step)
        return self.scheduler.compare_against_calendar_baseline(
            up_to_step=use_step,
            calendar_interval=max(12, int(calendar_interval)),
        )

    def reset(self) -> dict:
        """Resets telemetry, work orders, inventory, and replay clock to Hour 0."""
        self.ml_engine.reset_fleet()
        self.scheduler.reset_operations()
        self.current_step = 0
        return {
            "ok": True,
            "message": "Agro-Twin simulation reset to Hour 0.",
            "fleet_state": self.scheduler.get_operational_fleet_state(0),
        }
