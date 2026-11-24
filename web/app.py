"""
Agro-Twin: Animated Flask Web Server & Live Twin API
Track: AI in Agriculture (NexHack 2.0)

Integrates:
- Member 1 (Vansh): ml/ml_engine.py (Leak-free ML, noise/missing filter, uncertainty & explainability)
- Member 2 (Kunal): ops/scheduler.py (Constrained scheduler, work orders & fair baseline comparison)
- Member 3 (Mohit): backend/state.py (Unified TwinStateManager)
- Member 4 (Shashi): web/ (Animated segmented Flask UI + strict on-topic AI Website Assistant)

Run from repository root:
    python web/app.py
Then open:
    http://localhost:5000
"""

import os
import sys

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

# Unified Digital Twin state (starts on Hour 35 so the live fault + noise + dropout showcase is immediate)
twin = TwinStateManager(num_steps=120, technicians_total=2)
twin.current_step = 35
assistant = AgroTwinAssistant(twin)


# ---------------- Main Page ----------------

@app.route("/")
def index():
    """Serves the segmented, animated Agro-Twin Flask web application."""
    return render_template("index.html")


# ---------------- Digital Twin REST Endpoints ----------------

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify(twin.get_health())


@app.route("/api/fleet", methods=["GET"])
def api_fleet():
    step = request.args.get("step", default=None, type=int)
    return jsonify(twin.get_fleet_state(step=step))


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
    return jsonify(twin.schedule_maintenance(machine_id=machine_id, step=step))


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


@app.route("/api/reset", methods=["POST"])
def api_reset():
    twin.reset()
    twin.current_step = 35
    return jsonify(
        {
            "ok": True,
            "message": "Simulation reset cleanly to Hour 35.",
            "fleet_state": twin.get_fleet_state(step=35),
        }
    )


# ---------------- Strict On-Topic Website AI Assistant Endpoint ----------------

@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    return jsonify(assistant.answer(question))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Agro-Twin Flask Server at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
