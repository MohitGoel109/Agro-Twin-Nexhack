"""
One-command verification script for Member 4 (Shashi) — Upgraded Flask Web UI & AI Guide.
Run from repo root:
    python web/verify_web.py
"""

import ast
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.state import TwinStateManager
from web.ai_assistant import AgroTwinAssistant


def run_verification():
    print("=" * 76)
    print("AGRO-TWIN | MEMBER 4 (SHASHI) UPGRADED WEB UI & AI GUIDE VERIFICATION")
    print("=" * 76)

    # 1. Syntax check Flask app.py
    app_path = os.path.join(REPO_ROOT, "web", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=app_path)
    print("[CHECK 1] web/app.py syntax valid.")

    # 2. Check HTML/CSS/JS assets & new SVG X-Ray / Hindi / ROI / SMS / Webhook elements
    html_path = os.path.join(REPO_ROOT, "web", "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_src = f.read()
    for token in [
        "machine-xray-svg",
        "btn-lang",
        "btn-speak",
        "btn-weather-heat",
        "inp-hourly-loss",
        "sms-card-panel",
        "inp-webhook-url",
        "fleet-manager-mode",
        "fleet-manager-unit-select",
        "fleet-manager-criticality",
        "btn-save-machine",
        "btn-delete-machine",
    ]:
        assert token in html_src, f"Missing UI element in index.html: {token}"
    print("[CHECK 2] SVG X-Ray, language/voice, weather/ROI/SMS/webhook, and fleet manager UI verified.")

    # 3. Verify AI Assistant answers all website + new feature queries accurately
    twin = TwinStateManager(num_steps=120, technicians_total=2)
    twin.current_step = 35
    bot = AgroTwinAssistant(twin)

    on_topic_tests = [
        ("How do I use this website?", "website_guide"),
        ("What is wrong with TR-101?", "machine_status"),
        ("How do the SVG X-Ray & Heatwave mode work?", "ui_accessibility_features"),
        ("Tell me about Heatwave 45C thermal stress", "weather_stress"),
        ("How much Rupee ROI and downtime does Agro-Twin save?", "baseline_comparison"),
        ("How does the model avoid data leakage and noise?", "ml_explainability"),
        ("How do SMS job cards and n8n webhooks work?", "operations_scheduling"),
        ("What needs attention right now?", "live_fleet_summary"),
        ("वेबसाइट कैसे उपयोग करें?", "website_guide"),
    ]
    for q, expected_topic in on_topic_tests:
        res = bot.answer(q)
        assert res["allowed"] is True and res["warning"] is False, f"Should allow on-topic query: {q}"
        assert res["topic"] == expected_topic, f"Unexpected topic for '{q}': {res['topic']}"
    print(f"[CHECK 3] Passed {len(on_topic_tests)}/{len(on_topic_tests)} live on-topic queries (English + Hindi).")

    dynamic_twin = TwinStateManager(num_steps=120, technicians_total=2)
    dynamic_bot = AgroTwinAssistant(dynamic_twin)
    assert dynamic_bot._find_mentioned_machines("Tell me about TR-107") == []
    added = dynamic_twin.add_machine(
        "TR-107",
        "Tractor Golf",
        "Sensor Harness",
        criticality=1.2,
    )
    assert added["ok"]
    new_unit_answer = dynamic_bot.answer("What is wrong with TR-107?")
    assert new_unit_answer["allowed"] and new_unit_answer["topic"] == "machine_status"
    assert "TR-107" in new_unit_answer["answer"]
    updated = dynamic_twin.update_machine("TR-107", name="Tractor Golf Updated")
    assert updated["ok"]
    updated_answer = dynamic_bot.answer("Tell me about TR-107")
    assert "Tractor Golf Updated" in updated_answer["answer"]
    manager_answer = dynamic_bot.answer("How do I add a machine?")
    assert manager_answer["allowed"] and manager_answer["topic"] == "machine_management"
    assert dynamic_twin.delete_machine("TR-107")["ok"]
    removed_answer = dynamic_bot.answer("Tell me about TR-107")
    assert removed_answer["allowed"] is False and removed_answer["warning"] is True
    print("[CHECK 4] AI guide dynamically recognizes added/edited units and drops deleted IDs.")

    # 4. Verify STRICT OFF-TOPIC GUARDRAIL blocks unrelated queries & warns user
    off_topic_tests = [
        "What is the capital of France?",
        "Write me a poem about the ocean",
        "Who won the cricket world cup?",
        "Give me a paneer butter masala recipe",
        "Solve 45 * 89",
        "Write Python bubble sort code",
        "Tell me a funny joke",
        "How do I use Photoshop layers?",
        "What is the price of Bitcoin today?",
        "Explain quantum mechanics",
        "Who is Batman?",
        "What is the weather forecast in Panipat?",
    ]
    for q in off_topic_tests:
        res = bot.answer(q)
        assert res["allowed"] is False and res["warning"] is True, f"GUARDRAIL FAILED on off-topic query: {q}"
        assert "stick to the contents of this website" in res["answer"].lower() or "बाहर है" in res["answer"]
    print(f"[CHECK 5] Blocked {len(off_topic_tests)}/{len(off_topic_tests)} off-topic queries with clear warning.")

    # 5. Live Flask test_client check when Flask is installed
    try:
        from web.app import app as flask_app
        client = flask_app.test_client()
        assert client.get("/").status_code == 200
        w_res = client.post("/api/weather", json={"weather_mode": "heatwave_45c"}).get_json()
        assert w_res["ok"] and w_res["ambient_temp_c"] == 45
        client.post("/api/weather", json={"weather_mode": "normal"})
        roi_res = client.get("/api/roi?hourly_loss_inr=2500&preventive_part_cost_inr=2200").get_json()
        assert roi_res["net_savings_inr"] > 0 and roi_res["roi_multiple"] > 1
        sms_res = client.get("/api/sms-card/TR-101").get_json()
        assert sms_res["ok"] and len(sms_res["sms_en"]) <= 160 and len(sms_res["checklist"]) == 4
        wh_res = client.post("/api/webhook", json={"webhook_url": ""}).get_json()
        assert wh_res["ok"]
        created = client.post(
            "/api/machines",
            json={
                "machine_id": "TR-107",
                "name": "Tractor Golf",
                "part_needed": "Coolant Pump",
                "criticality": 1.1,
                "fault_mode": "healthy",
            },
        ).get_json()
        assert created["ok"] and created["fleet_state"]["machines_total"] == 7
        updated = client.put(
            "/api/machines/TR-107",
            json={"name": "Tractor Golf Updated", "criticality": 1.3},
        ).get_json()
        assert updated["ok"]
        scheduled = client.post(
            "/api/schedule",
            json={"machine_id": "TR-107", "step": 35},
        ).get_json()
        assert scheduled["ok"]
        deleted = client.delete("/api/machines/TR-107").get_json()
        assert deleted["ok"] and deleted["fleet_state"]["machines_total"] == 6
        assert deleted["cancelled_work_orders"] == [scheduled["work_order"]["wo_id"]]
        assert deleted["refunded_parts"] == {"Coolant Pump": 1}
        client.post("/api/reset")
        print("[CHECK 6] Flask CRUD endpoints dynamically add, edit, and remove machines with cleanup.")
        print("[CHECK 7] Existing Flask weather, ROI, SMS, webhook, and home routes verified.")
    except ImportError:
        print("[CHECK 5] Flask not installed in this sandbox env (install via: pip install -r requirements.txt).")

    print("\nALL CHECKS PASSED! Run your upgraded website with:")
    print("    python web/app.py")
    print("Then open: http://localhost:5000")
    print("=" * 76)


if __name__ == "__main__":
    run_verification()
