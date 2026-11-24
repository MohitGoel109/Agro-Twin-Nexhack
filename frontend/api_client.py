"""
Agro-Twin: Smart Dual-Mode API Client
Owner: Member 4 (Shashi) - Dashboard UI & Pitch Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery

Connects to Mohit's FastAPI server (backend/app.py) when running, and
automatically falls back to direct in-process TwinStateManager if the API
server is offline — guaranteeing a 100% crash-proof live judge demo.
"""

import os
from typing import Dict, Optional
import requests

from backend.state import TwinStateManager


class AgroTwinClient:
    """Unified client used by frontend/dashboard.py."""

    def __init__(self, api_url: Optional[str] = None, timeout: float = 2.0):
        self.api_url = (api_url or os.environ.get("AGRO_TWIN_API_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = float(timeout)
        self._local_twin: Optional[TwinStateManager] = None
        self.mode = "DIRECT_LOCAL"
        self.refresh_connection()

    def refresh_connection(self) -> str:
        """Checks whether Mohit's FastAPI backend is reachable."""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=self.timeout)
            if resp.status_code == 200:
                self.mode = "FASTAPI_REST"
                return self.mode
        except requests.RequestException:
            pass

        self.mode = "DIRECT_LOCAL"
        if self._local_twin is None:
            self._local_twin = TwinStateManager(num_steps=120, technicians_total=2)
        return self.mode

    def _ensure_local(self) -> TwinStateManager:
        if self._local_twin is None:
            self._local_twin = TwinStateManager(num_steps=120, technicians_total=2)
        return self._local_twin

    def _get(self, path: str, params: Optional[dict] = None, fallback_fn=None):
        if self.mode == "FASTAPI_REST":
            try:
                resp = requests.get(
                    f"{self.api_url}{path}",
                    params={k: v for k, v in (params or {}).items() if v is not None},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException:
                self.mode = "DIRECT_LOCAL"
        return fallback_fn()

    def _post(self, path: str, payload: Optional[dict] = None, fallback_fn=None):
        if self.mode == "FASTAPI_REST":
            try:
                resp = requests.post(
                    f"{self.api_url}{path}",
                    json=payload or {},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException:
                self.mode = "DIRECT_LOCAL"
        return fallback_fn()

    # ---------------- Core Operations ----------------

    def get_health(self) -> dict:
        return self._get("/health", fallback_fn=lambda: self._ensure_local().get_health())

    def get_fleet(self, step: Optional[int] = None) -> dict:
        return self._get(
            "/fleet",
            params={"step": step},
            fallback_fn=lambda: self._ensure_local().get_fleet_state(step=step),
        )

    def step_simulation(self, delta: int = 1, target_step: Optional[int] = None) -> dict:
        return self._post(
            "/step",
            payload={"delta": delta, "step": target_step},
            fallback_fn=lambda: self._ensure_local().advance_step(delta=delta, target_step=target_step),
        )

    def get_machine_history(self, machine_id: str, up_to_step: Optional[int] = None) -> dict:
        return self._get(
            f"/machines/{machine_id}/history",
            params={"up_to_step": up_to_step},
            fallback_fn=lambda: self._ensure_local().get_machine_detail(
                machine_id=machine_id, up_to_step=up_to_step
            ),
        )

    def acknowledge_alert(
        self,
        machine_id: str,
        step: Optional[int] = None,
        note: str = "Alert acknowledged via Agro-Twin Dashboard",
    ) -> dict:
        return self._post(
            "/acknowledge",
            payload={"machine_id": machine_id, "step": step, "note": note},
            fallback_fn=lambda: self._ensure_local().acknowledge_alert(
                machine_id=machine_id, step=step, note=note
            ),
        )

    def schedule_maintenance(self, machine_id: str, step: Optional[int] = None) -> dict:
        return self._post(
            "/schedule",
            payload={"machine_id": machine_id, "step": step},
            fallback_fn=lambda: self._ensure_local().schedule_maintenance(
                machine_id=machine_id, step=step
            ),
        )

    def inject_fault(
        self,
        machine_id: str,
        start_step: Optional[int] = None,
        fault_type: str = "fault_engine",
    ) -> dict:
        return self._post(
            "/inject-fault",
            payload={
                "machine_id": machine_id,
                "start_step": start_step,
                "fault_type": fault_type,
            },
            fallback_fn=lambda: self._ensure_local().inject_fault(
                machine_id=machine_id, start_step=start_step, fault_type=fault_type
            ),
        )

    def update_constraints(
        self,
        technicians_total: Optional[int] = None,
        parts_inventory: Optional[Dict[str, int]] = None,
    ) -> dict:
        return self._post(
            "/constraints",
            payload={
                "technicians_total": technicians_total,
                "parts_inventory": parts_inventory,
            },
            fallback_fn=lambda: self._ensure_local().update_constraints(
                technicians_total=technicians_total, parts_inventory=parts_inventory
            ),
        )

    def get_work_orders(self, step: Optional[int] = None) -> dict:
        return self._get(
            "/work-orders",
            params={"step": step},
            fallback_fn=lambda: self._ensure_local().get_work_orders(step=step),
        )

    def compare_baseline(
        self,
        up_to_step: Optional[int] = None,
        calendar_interval: int = 72,
    ) -> dict:
        return self._get(
            "/compare",
            params={"up_to_step": up_to_step, "calendar_interval": calendar_interval},
            fallback_fn=lambda: self._ensure_local().get_baseline_comparison(
                up_to_step=up_to_step, calendar_interval=calendar_interval
            ),
        )

    def reset(self) -> dict:
        return self._post("/reset", fallback_fn=lambda: self._ensure_local().reset())
