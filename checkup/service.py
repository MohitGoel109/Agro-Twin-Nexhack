"""Framework-neutral logic shared by the Flask blueprint and the FastAPI router. Returns (http_status, payload)."""
from checkup import store
from checkup.advice import build_report
from checkup.scoring import score_report, validate_answers, validate_owner

URGENT = ("SERVICE_SOON", "STOP_NOW")


def find_machine(twin, machine_id):
    for m in twin.get_fleet_state()["machines"]:
        if m["machine_id"] == machine_id:
            return m
    return None


def _worst(saved):
    if not saved:
        return None
    order = {"OVERDUE": 3, "DUE_SOON": 2, "OK": 1}
    rows = [r["status"] for r in saved["result"].get("ideal_vs_current", []) if r["status"] in order]
    return max(rows, key=lambda x: order[x]) if rows else None


def machines_list(twin):
    out = []
    for m in twin.get_fleet_state()["machines"]:
        saved = store.get(m["machine_id"])
        out.append({"machine_id": m["machine_id"], "name": m["name"], "type": m["type"],
                    "sensor_status": m["status"], "sensor_risk": m["fault_probability"],
                    "checkup_urgency": saved["result"]["urgency"] if saved else None,
                    "owner_form_filled": bool(store.get_owner(m["machine_id"])) or bool(saved and saved.get("owner")),
                    "report_ready": saved is not None,
                    "worst_system_status": _worst(saved)})
    return {"machines": out}


def get_owner_profile(twin, machine_id):
    if find_machine(twin, machine_id) is None:
        return 404, {"ok": False, "error": "Unknown machine"}
    rec = store.get_owner(machine_id)
    if rec is None:
        return 404, {"ok": False, "error": "No owner profile yet"}
    return 200, {"ok": True, "owner": rec["profile"], "saved_at": rec["saved_at"]}


def save_owner_profile(twin, machine_id, data):
    if find_machine(twin, machine_id) is None:
        return 404, {"ok": False, "error": "Unknown machine"}
    owner, errors = validate_owner((data or {}).get("owner", data or {}))
    if errors:
        return 400, {"ok": False, "errors": errors[:10]}
    store.save_owner(machine_id, owner)
    return 200, {"ok": True, "owner": owner}


def submit(twin, machine_id, data):
    m = find_machine(twin, machine_id)
    if m is None:
        return 404, {"ok": False, "error": "Unknown machine"}
    data = data or {}
    owner_in = data.get("owner")
    if owner_in is None:  # fall back to the saved owner profile
        rec = store.get_owner(machine_id)
        owner_in = rec["profile"] if rec else {}
    owner, e1 = validate_owner(owner_in)
    answers, e2 = validate_answers(data.get("answers", {}))
    if e1 or e2:
        return 400, {"ok": False, "errors": (e1 + e2)[:10]}
    sensor = {"fault_probability": m["fault_probability"], "status": m["status"], "sensor_status": m["sensor_status"]}
    result = score_report(m["type"], owner, answers, sensor)
    if owner:
        store.save_owner(machine_id, owner)
    store.save(machine_id, {"owner": owner, "answers": answers, "result": result,
                            "machine": {"machine_id": machine_id, "name": m["name"], "type": m["type"]}})
    return 200, {"ok": True, "machine_id": machine_id, "result": result}


def latest(machine_id):
    rec = store.get(machine_id)
    if rec is None:
        return 404, {"ok": False, "error": "No check-up yet"}
    return 200, {"ok": True, **{k: rec[k] for k in ("owner", "answers", "result")}}


def report_data(machine_id, lang):
    rec = store.get(machine_id)
    if rec is None:
        return None
    return build_report(rec["machine"], rec["result"], lang)


def annotate_fleet(state):
    """Add farmer check-up info to a fleet-state dict (used by /api/fleet). Does not touch any baseline numbers."""
    queue = state.get("priority_queue")
    if queue is None:
        return state
    by_id = {p["machine_id"]: p for p in queue}
    for m in state.get("machines", []):
        rec = store.get(m["machine_id"])
        if not rec:
            continue
        res = rec["result"]
        m["farmer_urgency"] = res["urgency"]
        m["farmer_report_ready"] = True
        m["owner_form_filled"] = bool(rec.get("owner"))
        if res["urgency"] not in URGENT:
            continue
        reason = res["reasons"][0]["en"] if res["reasons"] else ""
        note = "FARMER REPORT (%s): %s" % (res["urgency"].replace("_", " "), reason)
        if m["machine_id"] in by_id:
            by_id[m["machine_id"]]["recommended_action"] = note + " | " + by_id[m["machine_id"]]["recommended_action"]
        else:
            queue.append({"machine_id": m["machine_id"], "name": m["name"], "status": m["status"],
                          "priority_score": round(100.0 * res["combined_risk"], 1),
                          "fault_probability": res["combined_risk"], "confidence": m.get("confidence", 0.5),
                          "part_needed": m.get("part_needed", "-"), "part_in_stock": m.get("part_in_stock", 0),
                          "acknowledged": m.get("acknowledged", False), "recommended_action": note})
    return state
