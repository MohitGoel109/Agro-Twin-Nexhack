"""
Rule-based scoring for the Farmer Check-up. Deterministic, no randomness, no machine learning.
All rules are expert rules of thumb and have NOT been validated on real machines.
"""

import json
import os
from datetime import date

from checkup.questions import OWNER_FIELDS, QUESTION_BANK, SYSTEMS

URGENCY_ORDER = ["OK", "WATCH", "SERVICE_SOON", "STOP_NOW"]
_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "service_intervals.json"), encoding="utf-8") as _fh:
    INTERVALS = json.load(_fh)

_QBY = {q["id"]: q for q in QUESTION_BANK}
_FBY = {f["id"]: f for f in OWNER_FIELDS}
SERVICE_MAP = {"oil": ["engine"], "filters": ["engine", "fuel"], "coolant": ["cooling"],
               "brakes": ["brakes"], "hydraulics": ["hydraulics"]}
SENSOR_URGENCY = {"CRITICAL_WARNING": "SERVICE_SOON", "EARLY_WARNING": "WATCH"}


def max_urgency(a, b):
    return a if URGENCY_ORDER.index(a) >= URGENCY_ORDER.index(b) else b


# ---------------- validation ----------------

def validate_owner(owner):
    """Returns (clean_dict, errors). Unknown keys are dropped; blanks are skipped."""
    clean, errors = {}, []
    if not isinstance(owner, dict):
        return {}, ["owner must be an object"]
    for fid, val in owner.items():
        f = _FBY.get(fid)
        if f is None or val in (None, "", []):
            continue
        t = f["type"]
        if t == "number":
            try:
                num = float(val)
            except (TypeError, ValueError):
                errors.append("%s must be a number" % fid)
                continue
            if num < f["min"] or num > f["max"]:
                errors.append("%s must be between %s and %s" % (fid, f["min"], f["max"]))
                continue
            clean[fid] = num
        elif t == "select":
            if val not in [o[0] for o in f["options"]]:
                errors.append("%s has an unknown option" % fid)
                continue
            clean[fid] = val
        elif t == "multi":
            vals = val if isinstance(val, list) else [val]
            allowed = [o[0] for o in f["options"]]
            if any(v not in allowed for v in vals) or len(vals) > 10:
                errors.append("%s has an unknown option" % fid)
                continue
            clean[fid] = vals
        elif t == "date":
            try:
                d = date.fromisoformat(str(val)[:10])
            except ValueError:
                errors.append("%s must be a date (YYYY-MM-DD)" % fid)
                continue
            clean[fid] = d.isoformat()
    if clean.get("ownership_status") == "rented" and "year" in clean:
        errors.append("year is only applicable to owned or purchased machines")
    if clean.get("ownership_status") == "purchased" and "rental_duration_months" in clean:
        errors.append("rental_duration_months is only applicable to rented machines")
    return clean, errors


def validate_answers(answers):
    clean, errors = {}, []
    if not isinstance(answers, dict):
        return {}, ["answers must be an object"]
    for qid, val in answers.items():
        q = _QBY.get(qid)
        if q is None:
            errors.append("unknown question: %s" % str(qid)[:40])
            continue
        vals = val if isinstance(val, list) else [val]
        if val in (None, "", []):
            continue
        allowed = [o["id"] for o in q["options"]]
        if len(vals) > 12 or any(v not in allowed for v in vals):
            errors.append("%s has an unknown option" % qid)
            continue
        if q["type"] == "single" and len(vals) > 1:
            errors.append("%s accepts one option" % qid)
            continue
        clean[qid] = vals
    return clean, errors


# ---------------- ideal vs current ----------------

def compare_to_ideal(machine_type, owner):
    """Per-system ideal vs current table from the owner's service hours."""
    table = INTERVALS.get(machine_type) or INTERVALS["Tractor"]
    hrs = owner.get("hours_since_service")
    done = owner.get("service_done") or []
    serviced = set()
    for d in done:
        serviced.update(SERVICE_MAP.get(d, []))
    if not serviced and hrs is not None:
        serviced = {"engine"}  # assume at least the oil was changed
    rows = []
    for sysid, spec in table.items():
        row = {"system": sysid, "item_en": spec["item_en"], "item_hi": spec["item_hi"],
               "ideal_hours": spec["hours"], "current_hours": None, "pct": None}
        if spec["hours"] is None:
            row.update(status="CHECK", line_en="%s: no hour interval. Check it this season and follow the manual." % spec["item_en"],
                       line_hi="%s: घंटे का नियम नहीं। इस सीज़न देखें और मैनुअल मानें।" % spec["item_hi"])
        elif hrs is None:
            row.update(status="NO_DATA", line_en="%s: enter hours since service to compare." % spec["item_en"],
                       line_hi="%s: तुलना के लिए सर्विस के बाद घंटे भरें।" % spec["item_hi"])
        elif sysid not in serviced:
            row.update(status="CHECK", line_en="%s: not part of your last service. Ask your mechanic when it was last done." % spec["item_en"],
                       line_hi="%s: पिछली सर्विस में नहीं हुआ। मैकेनिक से पूछें कब हुआ था।" % spec["item_hi"])
        else:
            pct = hrs / float(spec["hours"])
            row["current_hours"], row["pct"] = hrs, round(pct, 2)
            if pct > 1.0:
                over = int(round(hrs - spec["hours"]))
                row.update(status="OVERDUE",
                           line_en="%s: %d h since service, placeholder interval %d h. Beyond it by %d h." % (spec["item_en"], hrs, spec["hours"], over),
                           line_hi="%s: सर्विस के बाद %d घंटे, नमूना अंतराल %d घंटे। इससे %d घंटे अधिक।" % (spec["item_hi"], hrs, spec["hours"], over))
            elif pct >= 0.8:
                row.update(status="DUE_SOON",
                           line_en="%s: %d h since service, placeholder interval %d h. Near this interval." % (spec["item_en"], hrs, spec["hours"]),
                           line_hi="%s: सर्विस के बाद %d घंटे, नमूना अंतराल %d घंटे। इस अंतराल के करीब।" % (spec["item_hi"], hrs, spec["hours"]))
            else:
                row.update(status="OK",
                           line_en="%s: %d h since service, placeholder interval %d h. Below this interval." % (spec["item_en"], hrs, spec["hours"]),
                           line_hi="%s: सर्विस के बाद %d घंटे, नमूना अंतराल %d घंटे। इस अंतराल से कम।" % (spec["item_hi"], hrs, spec["hours"]))
        rows.append(row)
    return rows


def _owner_system_risk(owner, ideal_rows):
    """Owner-form contribution per system (0-1) plus plain reasons. Rules of thumb."""
    risk = {s: 0.0 for s in SYSTEMS}
    reasons = []

    def add(sysid, v):
        risk[sysid] = 1 - (1 - risk[sysid]) * (1 - v)

    for row in ideal_rows:
        if row["status"] == "OVERDUE":
            pct = row["pct"] or 1.0
            add(row["system"], min(0.6, 0.3 + 0.2 * (pct - 1.0)))
            reasons.append((0.6, row["line_en"], row["line_hi"]))
        elif row["status"] == "DUE_SOON":
            add(row["system"], 0.12)
    idle = owner.get("days_idle_30")
    storage = owner.get("storage")
    if idle is not None and idle >= 20:
        if storage in ("outdoors", "rain"):
            add("electrical", 0.25); add("tyres", 0.15)
            reasons.append((0.4, "Idle %d of the last 30 days and stored outdoors: battery, tyres, wiring and rubber seals can go bad (rule of thumb)." % idle,
                            "पिछले 30 में से %d दिन खड़ी रही और खुले में रखी: बैटरी, टायर, तार और रबर सील खराब हो सकते हैं (अनुभव का नियम)।" % idle))
        else:
            add("electrical", 0.1)
            reasons.append((0.2, "Idle %d of the last 30 days: check the battery before heavy use (rule of thumb)." % idle,
                            "पिछले 30 में से %d दिन खड़ी रही: भारी काम से पहले बैटरी जांचें (अनुभव का नियम)।" % idle))
    fuel = owner.get("fuel_age_months")
    if fuel is not None and fuel >= 6:
        add("fuel", 0.3)
        reasons.append((0.5, "Fuel is about %d months old; old fuel can clog filters and injectors (rule of thumb)." % fuel,
                        "ईंधन लगभग %d महीने पुराना है; पुराना ईंधन फ़िल्टर और इंजेक्टर जाम कर सकता है (अनुभव का नियम)।" % fuel))
    elif fuel is not None and fuel >= 3:
        add("fuel", 0.1)
    season = owner.get("hours_season") or owner.get("hours_this_season")
    if season is not None and season > 400:
        add("drivetrain", 0.15); add("hydraulics", 0.15)
        reasons.append((0.3, "%d hours this season is heavy use; bearings and hydraulics wear faster (assumption: heavy above 400 h)." % season,
                        "इस सीज़न %d घंटे भारी उपयोग है; बेयरिंग और हाइड्रोलिक जल्दी घिसते हैं (मान्यता: 400 घंटे से ऊपर भारी)।" % season))
    if owner.get("work_type") == "road" and owner.get("hours_this_week", 0) > 40:
        add("brakes", 0.1); add("tyres", 0.1)
    return risk, reasons


# ---------------- main scoring ----------------

def _aggregate(sys_risk):
    r = sorted(sys_risk.values(), reverse=True) + [0.0, 0.0, 0.0]
    return 1 - (1 - r[0]) * (1 - 0.5 * r[1]) * (1 - 0.25 * r[2])


CRITICAL_SYSTEMS = {"engine", "brakes", "cooling", "drivetrain", "hydraulics"}


def _urgency_from_risk(risk, top_system=None):
    """STOP_NOW from risk alone only when the main suspect is a safety-critical system."""
    if risk >= 0.70:
        return "STOP_NOW" if top_system in CRITICAL_SYSTEMS else "SERVICE_SOON"
    if risk >= 0.45:
        return "SERVICE_SOON"
    if risk >= 0.20:
        return "WATCH"
    return "OK"


def _selected(answers):
    out = set()
    for vals in answers.values():
        out.update(vals)
    return out


def score_report(machine_type, owner, answers, sensor=None):
    """
    owner / answers must already be validated. sensor = optional dict with
    fault_probability (0-1), status and sensor_status from the twin.
    """
    owner = owner or {}
    answers = answers or {}
    sel = _selected(answers)
    answered, unsure = 0, 0
    sym_score = {s: 0.0 for s in SYSTEMS}
    reason_items = []

    for q in QUESTION_BANK:
        vals = answers.get(q["id"])
        if not vals:
            continue
        if "unsure" in vals:
            unsure += 1
            continue
        answered += 1
        for opt in q["options"]:
            if opt["id"] in vals and opt["weight"] > 0 and opt["systems"]:
                share = float(opt["weight"])
                for s in opt["systems"]:
                    sym_score[s] += share
                names = " / ".join(SYSTEMS[s][0] for s in opt["systems"])
                names_hi = " / ".join(SYSTEMS[s][1] for s in opt["systems"])
                reason_items.append((opt["weight"] / 3.0 + 0.5,
                                     "You reported: %s. This points to the %s." % (opt["en"].lower(), names.lower()),
                                     "आपने बताया: %s। यह %s की ओर इशारा करता है।" % (opt["hi"], names_hi)))
    # "when" context boosts, only if a sound was reported
    if sel & {"knocking", "grinding", "squealing", "whining", "rattling", "clicking"}:
        if "when_brake" in sel:
            sym_score["brakes"] += 1
        if "when_turn" in sel:
            sym_score["hydraulics"] += 0.5; sym_score["tyres"] += 0.5
        if "when_start" in sel:
            sym_score["electrical"] += 0.5
    sym_risk_sys = {s: min(1.0, v / 6.0) for s, v in sym_score.items()}
    worsening = "worse_yes" in sel
    if worsening and any(v > 0 for v in sym_risk_sys.values()):
        sym_risk_sys = {s: min(1.0, v * 1.15) for s, v in sym_risk_sys.items()}
        reason_items.append((0.7, "You said it is getting worse, so we treat it more seriously.",
                             "आपने बताया कि यह बढ़ रही है, इसलिए हम इसे गंभीरता से ले रहे हैं।"))

    ideal_rows = compare_to_ideal(machine_type, owner)
    own_risk_sys, own_reasons = _owner_system_risk(owner, ideal_rows)
    reason_items.extend(own_reasons)

    merged = {s: 1 - (1 - sym_risk_sys[s]) * (1 - own_risk_sys[s]) for s in SYSTEMS}
    symptom_risk = round(_aggregate(sym_risk_sys), 3)
    owner_risk = round(_aggregate(own_risk_sys), 3)
    field_risk = round(_aggregate(merged), 3)
    top_sys = max(merged, key=lambda k: merged[k])
    urgency = _urgency_from_risk(field_risk, top_sys)

    # safety overrides -> STOP_NOW
    safety = []
    if "brake_spongy" in sel or "leak_brake" in sel:
        safety.append(("Soft/spongy brakes or a brake fluid leak can mean the brakes fail.", "नरम/स्पंजी ब्रेक या ब्रेक फ्लूइड रिसाव का मतलब ब्रेक फेल हो सकते हैं।"))
    if (sel & {"smoke_black", "smoke_white", "smoke_blue"}) and (sel & {"smell_rubber", "smell_oil", "smell_elec"}):
        safety.append(("Smoke together with a burning smell can be a fire risk.", "धुआं और जलने की गंध साथ हो तो आग का खतरा हो सकता है।"))
    if "smell_elec" in sel:
        safety.append(("An electrical burning smell can mean a wiring fire.", "बिजली के तार जलने की गंध का मतलब वायरिंग में आग हो सकती है।"))
    if ("temp_red" in sel or "wl_temp" in sel) and "steam_yes" in sel:
        safety.append(("Overheating with steam can damage the engine and burn you.", "ज़्यादा गरम और भाप से इंजन खराब हो सकता है और जलने का खतरा है।"))
    if safety:
        urgency = "STOP_NOW"
        for en, hi in safety:
            reason_items.append((2.0, en, hi))

    sensor_note = None
    sensor_risk = None
    if sensor:
        sensor_risk = float(sensor.get("fault_probability") or 0.0)
        st = sensor.get("status")
        urgency = max_urgency(urgency, SENSOR_URGENCY.get(st, "OK"))
        if st in SENSOR_URGENCY:
            sensor_note = ("Machine sensors show %s (risk %d%%)." % (st.replace("_", " ").lower(), round(sensor_risk * 100)),
                           "मशीन के सेंसर %s दिखा रहे हैं (जोखिम %d%%)।" % (st.replace("_", " "), round(sensor_risk * 100)))
            reason_items.append((1.5, sensor_note[0], sensor_note[1]))
        elif sensor.get("sensor_status") not in (None, "CLEAN"):
            reason_items.append((0.3, "Sensor data looks unreliable right now, so we rely on your answers more.",
                                 "सेंसर डेटा अभी भरोसेमंद नहीं दिखता, इसलिए हम आपके जवाबों पर ज़्यादा भरोसा कर रहे हैं।"))
    combined = round(1 - (1 - field_risk) * (1 - (sensor_risk or 0.0)), 3)

    suspected = [s for s, v in sorted(merged.items(), key=lambda kv: -kv[1]) if v >= 0.25][:3]
    if urgency in ("SERVICE_SOON", "STOP_NOW") and not suspected:
        top = max(merged, key=lambda s: merged[s])
        suspected = [top] if merged[top] > 0 else []

    reason_items.sort(key=lambda r: -r[0])
    seen, reasons = set(), []
    for _, en, hi in reason_items:
        if en not in seen:
            seen.add(en)
            reasons.append({"en": en, "hi": hi})
        if len(reasons) == 5:
            break

    low_conf = (answered + unsure) > 0 and unsure > (answered + unsure) / 2.0
    confidence = "LOW" if (low_conf or (answered + unsure) < 3) else "OK"

    return {
        "urgency": urgency,
        "symptom_risk": symptom_risk,
        "owner_risk": owner_risk,
        "field_risk": field_risk,
        "sensor_risk": None if sensor_risk is None else round(sensor_risk, 3),
        "combined_risk": combined,
        "suspected_systems": suspected,
        "system_risk": {s: round(v, 3) for s, v in merged.items()},
        "reasons": reasons,
        "ideal_vs_current": ideal_rows,
        "answered_count": answered,
        "unsure_count": unsure,
        "confidence": confidence,
        "safety_override": bool(safety),
    }
