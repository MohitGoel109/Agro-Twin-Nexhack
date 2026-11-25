import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web"))
from web.app import app


def test_checkup_page_and_assets():
    c = app.test_client()
    r = c.get("/checkup")
    assert r.status_code == 200 and b"Farmer Check-up" in r.data
    assert c.get("/static/js/checkup.js").status_code == 200
    assert c.get("/static/css/checkup.css").status_code == 200
    assert b"/checkup" in c.get("/").data


def test_submit_then_machines_list_shows_urgency():
    c = app.test_client()
    mid = c.get("/api/checkup/machines").get_json()["machines"][0]["machine_id"]
    r = c.post("/api/checkup/%s/submit" % mid, json={"owner": {}, "answers": {"brake_feel": ["brake_spongy"]}})
    assert r.status_code == 200 and r.get_json()["result"]["urgency"] == "STOP_NOW"
    ms = c.get("/api/checkup/machines").get_json()["machines"]
    assert [m for m in ms if m["machine_id"] == mid][0]["checkup_urgency"] == "STOP_NOW"
    assert c.get("/api/checkup/NOPE/report").status_code == 404


def test_pdf_report_english_and_hindi_fallback_and_404():
    c = app.test_client()
    mid = c.get("/api/checkup/machines").get_json()["machines"][0]["machine_id"]
    c.post("/api/checkup/%s/submit" % mid, json={"owner": {"hours_since_service": 310}, "answers": {"sound": ["knocking"]}})
    r = c.get("/api/checkup/%s/report?lang=en&format=pdf" % mid)
    assert r.status_code == 200 and r.mimetype == "application/pdf" and r.data[:4] == b"%PDF" and len(r.data) > 2000
    h = c.get("/api/checkup/%s/report?lang=hi&format=pdf" % mid)
    assert h.status_code == 200 and h.mimetype == "text/html" and "PDF" in h.get_data(as_text=True)
    assert c.get("/api/checkup/NOPE/report?format=pdf").status_code == 404
    body = c.get("/api/checkup/%s/report?lang=en&format=json" % mid).get_json()
    txt = str(body).lower()
    assert "guaranteed" not in txt and "certain" not in txt.replace("uncertain", "")


def test_owner_profile_endpoints_and_validation():
    c = app.test_client()
    mid = c.get("/api/checkup/machines").get_json()["machines"][0]["machine_id"]
    assert c.post("/api/checkup/%s/owner-profile" % mid, json={"owner": {"hours_since_service": -5}}).status_code == 400
    assert c.post("/api/checkup/%s/owner-profile" % mid, json={"owner": {"hours_since_service": 310, "storage": "outdoors"}}).status_code == 200
    g = c.get("/api/checkup/%s/owner-profile" % mid).get_json()
    assert g["owner"]["hours_since_service"] == 310
    assert c.get("/api/checkup/NOPE/owner-profile").status_code == 404
    m = [x for x in c.get("/api/checkup/machines").get_json()["machines"] if x["machine_id"] == mid][0]
    assert m["owner_form_filled"] is True


def test_priority_queue_includes_farmer_urgent_machine_and_baseline_unchanged():
    c = app.test_client()
    mid = c.get("/api/checkup/machines").get_json()["machines"][0]["machine_id"]
    c.post("/api/checkup/%s/submit" % mid, json={"owner": {}, "answers": {"brake_feel": ["brake_spongy"]}})
    fleet = c.get("/api/fleet?step=0").get_json()
    assert any(p["machine_id"] == mid and "FARMER REPORT" in p["recommended_action"] for p in fleet["priority_queue"])
    cmp_ = c.get("/api/compare").get_json()
    s = str(cmp_)
    assert "92.22" in s and "98.33" in s
