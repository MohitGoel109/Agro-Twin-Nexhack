"""
Agro-Twin: Animated Flask Web Server & Live Twin API
Owner: Member 4 (Shashi) - Dashboard UI & Pitch Lead
Track: AI in Agriculture (NexHack 2.0)

Features:
- Segmented animated Flask UI with calm agricultural contour background
- Interactive SVG Machine X-Ray Blueprint highlighting failing subsystems
- Bilingual English / Hindi (EN / हिंदी) + Browser Speech Synthesis readout
- Weather Stress Mode (Normal 30°C vs. 45°C Harvest Heatwave)
- Rupee (₹) Harvest-Loss ROI Calculator & Low-Bandwidth SMS Mechanic Job Cards
- n8n-compatible Alert Webhook dispatcher & strict On-Topic Website AI Assistant

Run from repository root:
    python web/app.py
Then open:
    http://localhost:5000
"""

import os
import sys
from copy import deepcopy
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from flask import Flask, jsonify, render_template, request

from backend.state import TwinStateManager
from web.ai_assistant import AgroTwinAssistant

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

# Unified Digital Twin state (starts on Hour 35 so fault + noise + dropout showcase is immediate)
twin = TwinStateManager(num_steps=120, technicians_total=2)
twin.current_step = 35
assistant = AgroTwinAssistant(twin)
from checkup.routes import create_blueprint as create_checkup_blueprint  # noqa: E402
app.register_blueprint(create_checkup_blueprint(twin))

# Fallback state used only if backend/state.py hasn't pulled Member 3's latest update yet
_fallback_weather = {"weather_mode": "normal", "ambient_temp_c": 30}
_fallback_webhook = {"url": "", "log": []}


def _emit_fallback_webhook(event_type: str, payload: dict):
    target = _fallback_webhook["url"]
    delivered = False
    status = "LOGGED_LOCALLY"
    if target.startswith("http://") or target.startswith("https://"):
        try:
            resp = requests.post(
                target,
                json={"event": event_type, "step": twin.current_step, "payload": payload},
                timeout=2.0,
            )
            delivered = 200 <= resp.status_code < 300
            status = f"HTTP_{resp.status_code}"
        except Exception as exc:
            status = f"FAILED ({type(exc).__name__})"

    _fallback_webhook["log"].append(
        {
            "step": twin.current_step,
            "event_type": event_type,
            "target": target or "SIMULATED_LOCAL",
            "delivered": delivered,
            "status": status,
        }
    )


def _apply_weather_fallback(mode: str) -> dict:
    clean_mode = "heatwave_45c" if mode == "heatwave_45c" else "normal"
    _fallback_weather["weather_mode"] = clean_mode
    _fallback_weather["ambient_temp_c"] = 45 if clean_mode == "heatwave_45c" else 30

    # Rebuild base telemetry cleanly first, then apply thermal stress if heatwave is active
    twin.ml_engine.reset_fleet()
    if clean_mode == "heatwave_45c":
        for m in twin.ml_engine.fleet_meta:
            m_id = m["id"]
            df = twin.ml_engine.telemetry[m_id]
            df["engine_temp"] = df["engine_temp"] + 8.0
            df["oil_pressure"] = df["oil_pressure"] - 2.5
            b_step = int(df["breakdown_step"].iloc[0])
            if b_step != -1 and m["fault_start"] is not None:
                earlier_b = max(int(m["fault_start"]) + 12, b_step - 4)
                df["breakdown_step"] = earlier_b
            from ml.ml_engine import _extract_leak_free_features
            twin.ml_engine.features[m_id] = _extract_leak_free_features(df)

    return {
        "ok": True,
        "weather_mode": clean_mode,
        "ambient_temp_c": _fallback_weather["ambient_temp_c"],
        "stress_note": (
            "45°C heatwave active: +8°C thermal load, -2.5 PSI oil pressure, 4h tighter failure window."
            if clean_mode == "heatwave_45c"
            else "Normal 30°C harvest operating conditions."
        ),
        "fleet_state": twin.get_fleet_state(step=twin.current_step),
    }


def _compute_roi_fallback(hourly_loss_inr: float, preventive_part_cost_inr: float, calendar_interval: int) -> dict:
    comp = twin.get_baseline_comparison(calendar_interval=calendar_interval)
    downtime_hours_saved = comp["improvement"]["downtime_hours_saved"]
    preventive_services = comp["ai_twin"]["preventive_services_completed"]
    gross = round(downtime_hours_saved * float(hourly_loss_inr), 2)
    spend = round(preventive_services * float(preventive_part_cost_inr), 2)
    net = round(gross - spend, 2)
    roi_mult = round(gross / max(1.0, spend), 1)
    return {
        "hourly_loss_inr": float(hourly_loss_inr),
        "preventive_part_cost_inr": float(preventive_part_cost_inr),
        "downtime_hours_saved": downtime_hours_saved,
        "preventive_services": preventive_services,
        "breakdowns_avoided": comp["improvement"]["breakdowns_avoided"],
        "gross_harvest_protected_inr": gross,
        "preventive_spend_inr": spend,
        "net_savings_inr": net,
        "roi_multiple": roi_mult,
    }


def _build_sms_card_fallback(machine_id: str, step: int) -> dict:
    fleet = twin.get_fleet_state(step=step)
    m = next((item for item in fleet["machines"] if item["machine_id"] == machine_id), None)
    if m is None:
        return {"ok": False, "message": f"Unknown machine_id: {machine_id}"}

    risk_pct = int(round(m["fault_probability"] * 100))
    wo_id = m["open_work_order"]["wo_id"] if m.get("open_work_order") else "PENDING"
    part = m["part_needed"]

    sms_en = f"AGRO-TWIN {wo_id}: {machine_id} {part} | Risk {risk_pct}% | 4h bay service | Prevents 18h harvest stop"[:160]
    sms_hi = f"एग्रो-ट्विन {wo_id}: {machine_id} ({part}) | जोखिम {risk_pct}% | 4 घंटे की अग्रिम सर्विस करें, 18 घंटे का नुकसान बचाएं।"[:160]

    checklist_map = {
        "Coolant Pump": [
            "Isolate battery and depressurize radiator cap safely.",
            "Inspect Coolant Pump impeller seal and belt tension.",
            "Install replacement Coolant Pump and flush coolant loop.",
            "Run 10-min idle thermal check (<88°C) before field release.",
        ],
        "Hydraulic Valve": [
            "Lower all hydraulic implements and relieve line pressure.",
            "Check Hydraulic Valve spool for pressure leak or blockage.",
            "Install spare Hydraulic Valve and torque manifold fittings.",
            "Verify steady 45 PSI operating pressure under load.",
        ],
        "Drive Bearing": [
            "Chock wheels and lock PTO / drive shaft before inspection.",
            "Check Drive Bearing housing play and acoustic vibration.",
            "Press-fit replacement Drive Bearing and pack high-temp grease.",
            "Verify vibration <2.2 mm/s at rated harvest RPM.",
        ],
    }
    checklist = checklist_map.get(
        part,
        [
            "Inspect wiring harness connectors and sensor seating.",
            "Clean dust/moisture from transducer terminals.",
            "Verify steady telemetry stream for 3 consecutive readings.",
            "Clear data-check hold and release unit to harvest.",
        ],
    )

    return {
        "ok": True,
        "machine_id": machine_id,
        "machine_name": m["name"],
        "part_needed": part,
        "status": m["status"],
        "wo_id": wo_id,
        "sms_en": sms_en,
        "sms_hi": sms_hi,
        "checklist": checklist,
    }


def _machine_operation(operation: str, **kwargs) -> dict:
    """Uses the state-manager CRUD bridge, falling back to ML/scheduler methods."""
    state_method = getattr(twin, operation, None)
    if callable(state_method):
        return state_method(**kwargs)

    engine_operation = "remove_machine" if operation == "delete_machine" else operation
    engine_method = getattr(twin.ml_engine, engine_operation, None)
    if not callable(engine_method):
        return {"ok": False, "message": "Machine management is unavailable."}

    result = engine_method(**kwargs)
    if result.get("ok"):
        if operation == "delete_machine" and hasattr(twin.scheduler, "remove_machine_records"):
            twin.scheduler.remove_machine_records(
                machine_id=result["machine_id"],
                current_step=twin.current_step,
            )
        elif operation == "update_machine":
            machine_name = result["machine"]["name"]
            canonical_id = result["machine"]["id"]
            for work_order in twin.scheduler.work_orders:
                if work_order["machine_id"] == canonical_id:
                    work_order["machine_name"] = machine_name
        result["fleet_state"] = twin.get_fleet_state()
    return result


# ---------------- Main Page ----------------

PAGE_ROUTES = {
    "home": ("/", "Agro-Twin — Easy Farm Machine Helper"),
    "machines": ("/machines", "Agro-Twin — Your Farm Machines"),
    "picture": ("/picture", "Agro-Twin — Machine Picture & Parts"),
    "savings": ("/savings", "Agro-Twin — Money Saved (₹)"),
    "repairs": ("/repairs", "Agro-Twin — Repairs & Mechanic SMS"),
}


@app.route("/")
def index():
    """Serves the Home overview page."""
    return render_template("index.html", active_page="home", page_title=PAGE_ROUTES["home"][1])


@app.route("/machines")
def page_machines():
    """Serves the dedicated Farm Machines status & booking page."""
    return render_template("index.html", active_page="machines", page_title=PAGE_ROUTES["machines"][1])


@app.route("/picture")
def page_picture():
    """Serves the dedicated Interactive Machine Picture (X-Ray) & Sensors page."""
    return render_template("index.html", active_page="picture", page_title=PAGE_ROUTES["picture"][1])


@app.route("/savings")
def page_savings():
    """Serves the dedicated Money Saved (₹) ROI & Comparison page."""
    return render_template("index.html", active_page="savings", page_title=PAGE_ROUTES["savings"][1])


@app.route("/repairs")
def page_repairs():
    """Serves the dedicated Booked Repairs, SMS Cards & Fleet Manager page."""
    return render_template("index.html", active_page="repairs", page_title=PAGE_ROUTES["repairs"][1])


# ---------------- Digital Twin REST Endpoints ----------------

@app.route("/api/health", methods=["GET"])
def api_health():
    health = twin.get_health()
    if "weather_mode" not in health:
        health["weather_mode"] = _fallback_weather["weather_mode"]
        health["ambient_temp_c"] = _fallback_weather["ambient_temp_c"]
    return jsonify(health)


@app.route("/api/fleet", methods=["GET"])
def api_fleet():
    step = request.args.get("step", default=None, type=int)
    state = twin.get_fleet_state(step=step)
    if "weather_mode" not in state:
        state["weather_mode"] = _fallback_weather["weather_mode"]
        state["ambient_temp_c"] = _fallback_weather["ambient_temp_c"]
    return jsonify(state)


@app.route("/api/step", methods=["POST"])
def api_step():
    data = request.get_json(silent=True) or {}
    delta = data.get("delta", 1)
    target_step = data.get("step", None)
    return jsonify(twin.advance_step(delta=delta, target_step=target_step))


@app.route("/api/machines/<machine_id>/history", methods=["GET"])
def api_machine_history(machine_id):
    up_to_step = request.args.get("up_to_step", default=None, type=int)
    res = twin.get_machine_detail(machine_id=machine_id, up_to_step=up_to_step)
    if not res.get("ok"):
        return jsonify(res), 404
    return jsonify(res)


@app.route("/api/machines", methods=["POST"])
def api_add_machine():
    data = request.get_json(silent=True) or {}
    res = _machine_operation(
        "add_machine",
        machine_id=data.get("machine_id"),
        name=data.get("name"),
        part_needed=data.get("part_needed"),
        criticality=data.get("criticality", 1.0),
        fault_mode=data.get("fault_mode", "healthy"),
        fault_start=data.get("fault_start"),
    )
    if not res.get("ok"):
        message = res.get("message", "Machine could not be added.")
        status_code = 409 if "already exists" in message.lower() else 400
        return jsonify(res), status_code
    return jsonify(res)


@app.route("/api/machines/<machine_id>", methods=["PUT"])
def api_update_machine(machine_id):
    data = request.get_json(silent=True) or {}
    fields = {
        key: data[key]
        for key in ("name", "part_needed", "criticality", "fault_mode", "fault_start")
        if key in data
    }
    res = _machine_operation("update_machine", machine_id=machine_id, **fields)
    if not res.get("ok"):
        message = res.get("message", "Machine could not be updated.")
        status_code = 404 if "not found" in message.lower() else 400
        return jsonify(res), status_code
    return jsonify(res)


@app.route("/api/machines/<machine_id>", methods=["DELETE"])
def api_delete_machine(machine_id):
    res = _machine_operation("delete_machine", machine_id=machine_id)
    if not res.get("ok"):
        message = res.get("message", "Machine could not be removed.")
        status_code = 404 if "not found" in message.lower() else 400
        return jsonify(res), status_code
    return jsonify(res)


@app.route("/api/acknowledge", methods=["POST"])
def api_acknowledge():
    data = request.get_json(silent=True) or {}
    machine_id = data.get("machine_id", "")
    step = data.get("step", None)
    note = data.get("note", "Alert acknowledged via Agro-Twin Web UI")
    res = twin.acknowledge_alert(machine_id=machine_id, step=step, note=note)
    status_code = 200 if res.get("ok") else 400
    return jsonify(res), status_code


@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    data = request.get_json(silent=True) or {}
    machine_id = data.get("machine_id", "")
    step = data.get("step", None)
    res = twin.schedule_maintenance(machine_id=machine_id, step=step)
    if res.get("ok") and not hasattr(twin, "get_webhook_log"):
        _emit_fallback_webhook("WORK_ORDER_SCHEDULED", {"machine_id": machine_id, "work_order": res.get("work_order")})
    return jsonify(res)


@app.route("/api/inject-fault", methods=["POST"])
def api_inject_fault():
    data = request.get_json(silent=True) or {}
    machine_id = data.get("machine_id", "")
    start_step = data.get("start_step", None)
    fault_type = data.get("fault_type", "fault_bearing")
    res = twin.inject_fault(
        machine_id=machine_id,
        start_step=start_step,
        fault_type=fault_type,
    )
    if res.get("ok") and not hasattr(twin, "get_webhook_log"):
        _emit_fallback_webhook("FAULT_INJECTED", {"machine_id": machine_id, "fault_type": fault_type})
    status_code = 200 if res.get("ok") else 404
    return jsonify(res), status_code


@app.route("/api/constraints", methods=["POST"])
def api_constraints():
    data = request.get_json(silent=True) or {}
    return jsonify(
        twin.update_constraints(
            technicians_total=data.get("technicians_total"),
            parts_inventory=data.get("parts_inventory"),
        )
    )


@app.route("/api/work-orders", methods=["GET"])
def api_work_orders():
    step = request.args.get("step", default=None, type=int)
    return jsonify(twin.get_work_orders(step=step))


@app.route("/api/compare", methods=["GET"])
def api_compare():
    up_to_step = request.args.get("up_to_step", default=None, type=int)
    calendar_interval = request.args.get("calendar_interval", default=72, type=int)
    return jsonify(
        twin.get_baseline_comparison(
            up_to_step=up_to_step,
            calendar_interval=calendar_interval,
        )
    )


@app.route("/api/weather", methods=["POST"])
def api_weather():
    data = request.get_json(silent=True) or {}
    mode = data.get("weather_mode", "normal")
    if hasattr(twin, "set_weather_mode"):
        return jsonify(twin.set_weather_mode(mode))
    return jsonify(_apply_weather_fallback(mode))


@app.route("/api/roi", methods=["GET"])
def api_roi():
    hourly_loss = request.args.get("hourly_loss_inr", default=2500.0, type=float)
    part_cost = request.args.get("preventive_part_cost_inr", default=2200.0, type=float)
    cal_int = request.args.get("calendar_interval", default=72, type=int)
    if hasattr(twin, "get_roi_summary"):
        return jsonify(
            twin.get_roi_summary(
                hourly_loss_inr=hourly_loss,
                preventive_part_cost_inr=part_cost,
                calendar_interval=cal_int,
            )
        )
    return jsonify(_compute_roi_fallback(hourly_loss, part_cost, cal_int))


@app.route("/api/sms-card/<machine_id>", methods=["GET"])
def api_sms_card(machine_id):
    step = request.args.get("step", default=twin.current_step, type=int)
    if hasattr(twin, "get_sms_job_card"):
        res = twin.get_sms_job_card(machine_id=machine_id, step=step)
    else:
        res = _build_sms_card_fallback(machine_id=machine_id, step=step)
    status_code = 200 if res.get("ok") else 404
    return jsonify(res), status_code


@app.route("/api/webhook", methods=["POST"])
def api_webhook():
    data = request.get_json(silent=True) or {}
    url = (data.get("webhook_url") or data.get("url") or "").strip()
    if hasattr(twin, "set_webhook_url"):
        return jsonify(twin.set_webhook_url(url))
    _fallback_webhook["url"] = url
    _emit_fallback_webhook("WEBHOOK_CONFIGURED", {"url": url or "LOCAL_LOG_ONLY"})
    return jsonify(
        {
            "ok": True,
            "webhook_url": url,
            "message": f"n8n webhook configured ({url or 'local audit mode'}).",
            "log": deepcopy(_fallback_webhook["log"][-10:]),
        }
    )


@app.route("/api/webhook/log", methods=["GET"])
def api_webhook_log():
    if hasattr(twin, "get_webhook_log"):
        return jsonify({"log": twin.get_webhook_log()})
    return jsonify({"log": deepcopy(_fallback_webhook["log"][-10:])})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    twin.reset()
    _fallback_weather["weather_mode"] = "normal"
    _fallback_weather["ambient_temp_c"] = 30
    twin.current_step = 35
    return jsonify(
        {
            "ok": True,
            "message": "Simulation reset cleanly to Hour 35 (Normal 30°C).",
            "fleet_state": twin.get_fleet_state(step=35),
        }
    )


# ---------------- Strict On-Topic Website AI Assistant Endpoint ----------------

@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    lang = data.get("lang", "en")
    return jsonify(assistant.answer(question, lang=lang))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Agro-Twin Flask Server at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
