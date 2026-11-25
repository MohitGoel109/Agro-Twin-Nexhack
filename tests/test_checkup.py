import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from flask import Flask
from backend.state import TwinStateManager
from checkup import store
from checkup.advice import build_report, render_html
from checkup.routes import create_blueprint
from checkup.scoring import compare_to_ideal, score_report, validate_answers, validate_owner

M = {"machine_id": "TR-101", "name": "Tractor Alpha", "type": "Tractor"}


def test_no_symptoms_is_ok():
    assert score_report("Tractor", {}, {})["urgency"] == "OK"


def test_spongy_brake_is_stop_now_and_no_self_repair():
    r = score_report("Tractor", {}, {"brake_feel": ["brake_spongy"]})
    assert r["urgency"] == "STOP_NOW" and "brakes" in r["suspected_systems"]
    rep = build_report(M, r)
    assert rep["self_checks"] == [] and rep["needs_repair"]


def test_smoke_plus_burning_smell_is_stop_now():
    r = score_report("Tractor", {}, {"smoke": ["smoke_black"], "smell": ["smell_rubber"]})
    assert r["urgency"] == "STOP_NOW"


def test_idle_outdoor_battery_rule():
    r = score_report("Tractor", {"days_idle_30": 25, "storage": "outdoors"}, {"starting": ["start_slow"]})
    assert "electrical" in r["suspected_systems"] and r["urgency"] != "STOP_NOW"


def test_overdue_oil_service():
    rows = compare_to_ideal("Tractor", {"hours_since_service": 310})
    eng = [x for x in rows if x["system"] == "engine"][0]
    assert eng["status"] == "OVERDUE" and "60 h" in eng["line_en"]
    assert "placeholder interval" in eng["line_en"]


def test_all_not_sure_is_low_confidence():
    r = score_report("Tractor", {}, {"sound": ["unsure"], "smell": ["unsure"], "smoke": ["unsure"]})
    assert r["confidence"] == "LOW"


def test_deterministic():
    a = score_report("Tractor", {"hours_since_service": 120}, {"sound": ["grinding"]})
    b = score_report("Tractor", {"hours_since_service": 120}, {"sound": ["grinding"]})
    assert a == b


def test_validation_rejects_bad_input():
    assert validate_owner({"hours_since_service": -5})[1]
    assert validate_owner({"storage": "moon"})[1]
    assert validate_answers({"nope": ["x"]})[1]
    assert validate_answers({"sound": ["bad"]})[1]


def test_ownership_form_validates_choice_specific_answers():
    owned, errors = validate_owner({"ownership_status": "purchased", "year": 2020})
    assert not errors and owned["year"] == 2020
    rented, errors = validate_owner({"ownership_status": "rented", "rental_duration_months": 18})
    assert not errors and rented["rental_duration_months"] == 18
    assert validate_owner({"ownership_status": "rented", "year": 2020})[1]
    assert validate_owner({"ownership_status": "purchased", "rental_duration_months": 18})[1]


def test_report_languages_and_words():
    r = score_report("Tractor", {"hours_since_service": 310}, {"sound": ["knocking"]})
    for lang in ("en", "hi"):
        report = build_report(M, r, lang)
        html = render_html(report).lower()
        assert len(html) > 3000 and "guaranteed" not in html and "certain" not in html
        if lang == "en":
            assert "placeholder" in report["disclaimer"].lower()
        else:
            assert "नमूना" in report["disclaimer"]


@pytest.fixture()
def client():
    store.clear()
    twin = TwinStateManager(num_steps=120, technicians_total=2)
    twin.current_step = 35
    app = Flask(__name__)
    app.register_blueprint(create_blueprint(twin))
    return app.test_client(), twin


def test_api_flow_and_baseline_unchanged(client):
    c, twin = client
    assert c.get("/api/checkup/questions").status_code == 200
    assert c.post("/api/checkup/NOPE/submit", json={}).status_code == 404
    assert c.post("/api/checkup/TR-101/submit", json={"answers": {"zzz": ["a"]}}).status_code == 400
    r = c.post("/api/checkup/TR-101/submit", json={"owner": {"hours_since_service": 310}, "answers": {"sound": ["knocking"]}})
    assert r.status_code == 200 and r.get_json()["result"]["urgency"] in ("SERVICE_SOON", "STOP_NOW")
    html = c.get("/api/checkup/TR-101/report?lang=hi")
    assert html.status_code == 200 and "text/html" in html.content_type
    assert c.get("/api/checkup/TR-101/report?format=json").get_json()["needs_repair"] is True
    comp = twin.get_baseline_comparison()
    assert comp["calendar_only"]["fleet_availability_pct"] == 92.22 and comp["ai_twin"]["fleet_availability_pct"] == 98.33
    assert comp["calendar_only"]["total_downtime_hours"] == 56 and comp["ai_twin"]["total_downtime_hours"] == 12
