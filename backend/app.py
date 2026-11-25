"""
Agro-Twin: FastAPI REST Server
Owner: Member 3 (Mohit) - Backend & Twin State Architect
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery

Run locally from repo root:
    uvicorn backend.app:app --reload --port 8000
Or:
    python backend/app.py
"""

import os
import sys
from typing import Dict, Optional

# Ensure repo root is on sys.path even if executed directly as `python backend/app.py`
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.state import TwinStateManager

app = FastAPI(
    title="Agro-Twin Predictive Maintenance API",
    description=(
        "Digital Twin REST API for farm machinery predictive maintenance "
        "(NexHack 2.0 - PS 08). Integrates leak-free ML predictions with "
        "constrained technician/spare-parts scheduling."
    ),
    version="1.0.0",
)

# Allow Streamlit, React, or Render-hosted frontends to connect seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single live Twin State Manager shared across API requests
twin = TwinStateManager(num_steps=120, technicians_total=2)
from checkup.fastapi_router import create_router as create_checkup_router  # noqa: E402
app.include_router(create_checkup_router(twin))


# ---------------- Request Schemas ----------------

class StepRequest(BaseModel):
    delta: int = Field(default=1, description="Hours to advance (can be negative to rewind).")
    step: Optional[int] = Field(default=None, description="Optional exact hour to jump to (0-119).")


class AcknowledgeRequest(BaseModel):
    machine_id: str = Field(..., examples=["TR-101"])
    step: Optional[int] = Field(default=None, description="Current simulation hour.")
    note: str = Field(default="Alert acknowledged by fleet manager")


class ScheduleRequest(BaseModel):
    machine_id: str = Field(..., examples=["TR-101"])
    step: Optional[int] = Field(default=None, description="Current simulation hour.")


class FaultInjectionRequest(BaseModel):
    machine_id: str = Field(..., examples=["HV-206"])
    start_step: Optional[int] = Field(default=None, description="Hour when degradation begins.")
    fault_type: str = Field(
        default="fault_engine",
        description="One of: fault_engine, fault_hydraulic, fault_bearing",
    )


class ConstraintsRequest(BaseModel):
    technicians_total: Optional[int] = Field(default=None, ge=1, le=10)
    parts_inventory: Optional[Dict[str, int]] = Field(default=None)


class WeatherRequest(BaseModel):
    mode: str = Field(..., examples=["heatwave_45c"])


class WebhookRequest(BaseModel):
    url: str = Field(default="", description="HTTP(S) webhook URL; empty disables delivery.")


class MachineCreateRequest(BaseModel):
    machine_id: str = Field(..., examples=["TR-107"])
    name: str = Field(..., min_length=1, max_length=80)
    part_needed: str = Field(..., examples=["Coolant Pump"])
    criticality: float = Field(default=1.0, ge=0.8, le=1.5)
    fault_mode: str = Field(default="healthy")
    fault_start: Optional[int] = Field(default=None, ge=0, le=119)


class MachineUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    part_needed: Optional[str] = Field(default=None)
    criticality: Optional[float] = Field(default=None, ge=0.8, le=1.5)
    fault_mode: Optional[str] = Field(default=None)
    fault_start: Optional[int] = Field(default=None, ge=0, le=119)


# ---------------- API Endpoints ----------------

@app.get("/")
@app.get("/health")
def health_check():
    """Health check + leak-free ML metadata and current clock hour."""
    return twin.get_health()


@app.get("/fleet")
def get_fleet(
    step: Optional[int] = Query(default=None, ge=0, le=119, description="Optional simulation hour (0-119)")
):
    """Returns full fleet readiness, risk, uncertainty, explanations, and priority queue."""
    return twin.get_fleet_state(step=step)


@app.post("/step")
def step_simulation(req: StepRequest):
    """Advances or jumps the simulation clock and returns updated fleet state."""
    return twin.advance_step(delta=req.delta, target_step=req.step)


@app.get("/machines/{machine_id}/history")
def get_machine_history(
    machine_id: str,
    up_to_step: Optional[int] = Query(default=None, ge=0, le=119),
):
    """Returns single-machine operational state + hourly telemetry series for plotting."""
    res = twin.get_machine_detail(machine_id=machine_id, up_to_step=up_to_step)
    if not res.get("ok"):
        raise HTTPException(status_code=404, detail=res.get("error", "Machine not found"))
    return res


@app.post("/machines")
def add_machine(req: MachineCreateRequest):
    """Adds a machine to the active fleet and returns the updated state."""
    res = twin.add_machine(**req.dict())
    if not res.get("ok"):
        message = res.get("message", "Machine could not be added.")
        status_code = 409 if "already exists" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message)
    return res


@app.put("/machines/{machine_id}")
def update_machine(machine_id: str, req: MachineUpdateRequest):
    """Updates the supplied metadata for an existing fleet machine."""
    res = twin.update_machine(machine_id, **req.dict(exclude_unset=True))
    if not res.get("ok"):
        message = res.get("message", "Machine could not be updated.")
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message)
    return res


@app.delete("/machines/{machine_id}")
def delete_machine(machine_id: str):
    """Removes a machine and releases its active work-order resources."""
    res = twin.delete_machine(machine_id)
    if not res.get("ok"):
        message = res.get("message", "Machine could not be removed.")
        status_code = 404 if "not found" in message.lower() else 400
        raise HTTPException(status_code=status_code, detail=message)
    return res


@app.post("/acknowledge")
def acknowledge_alert(req: AcknowledgeRequest):
    """Records operator acknowledgement of a developing fault alert."""
    res = twin.acknowledge_alert(
        machine_id=req.machine_id,
        step=req.step,
        note=req.note,
    )
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("message", "Acknowledgement failed"))
    return res


@app.post("/schedule")
def schedule_maintenance(req: ScheduleRequest):
    """Schedules constrained preventive maintenance (checks technicians & spare parts)."""
    return twin.schedule_maintenance(machine_id=req.machine_id, step=req.step)


@app.post("/inject-fault")
def inject_fault(req: FaultInjectionRequest):
    """Injects a new developing fault live during judge demonstrations."""
    res = twin.inject_fault(
        machine_id=req.machine_id,
        start_step=req.start_step,
        fault_type=req.fault_type,
    )
    if not res.get("ok"):
        raise HTTPException(status_code=404, detail=res.get("message", "Fault injection failed"))
    return res


@app.post("/constraints")
def update_constraints(req: ConstraintsRequest):
    """Live-updates technician count or spare-parts inventory to test scarcity."""
    return twin.update_constraints(
        technicians_total=req.technicians_total,
        parts_inventory=req.parts_inventory,
    )


@app.get("/work-orders")
def list_work_orders(
    step: Optional[int] = Query(default=None, ge=0, le=119),
):
    """Returns all maintenance work orders with live lifecycle status."""
    return twin.get_work_orders(step=step)


@app.get("/compare")
def compare_baseline(
    up_to_step: Optional[int] = Query(default=None, ge=1, le=119),
    calendar_interval: int = Query(default=72, ge=12, le=120),
):
    """Compares Calendar-Only Servicing vs. Agro-Twin AI on the exact same fleet scenario."""
    return twin.get_baseline_comparison(
        up_to_step=up_to_step,
        calendar_interval=calendar_interval,
    )


@app.post("/reset")
def reset_simulation():
    """Resets fleet telemetry, work orders, parts inventory, and clock back to Hour 0."""
    return twin.reset()


@app.post("/weather")
def set_weather_mode(req: WeatherRequest):
    """Changes the fleet weather scenario and returns the updated state."""
    return twin.set_weather_mode(mode=req.mode)


@app.get("/roi")
def get_roi_summary(
    hourly_loss_inr: float = Query(default=2500.0, ge=0),
    preventive_part_cost_inr: float = Query(default=2200.0, ge=0),
    calendar_interval: int = Query(default=72, ge=12, le=120),
):
    """Returns estimated harvest protection and preventive-maintenance ROI."""
    return twin.get_roi_summary(
        hourly_loss_inr=hourly_loss_inr,
        preventive_part_cost_inr=preventive_part_cost_inr,
        calendar_interval=calendar_interval,
    )


@app.get("/sms-card/{machine_id}")
def get_sms_job_card(
    machine_id: str,
    step: Optional[int] = Query(default=None, ge=0, le=119),
):
    """Returns a bilingual mechanic dispatch SMS card for a machine."""
    return twin.get_sms_job_card(machine_id=machine_id, step=step)


@app.post("/webhook")
def configure_webhook(req: WebhookRequest):
    """Configures or disables the n8n-compatible event webhook."""
    return twin.set_webhook_url(req.url)


@app.get("/webhook/log")
def get_webhook_log():
    """Returns recorded webhook delivery attempts."""
    return twin.get_webhook_log()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
