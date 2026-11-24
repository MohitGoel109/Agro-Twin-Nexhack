"""
One-command verification script for the Animated Flask UI + On-Topic AI Assistant.
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
    print("AGRO-TWIN | FLASK ANIMATED UI & STRICT AI ASSISTANT VERIFICATION")
    print("=" * 76)

    # 1. Syntax check Flask app.py
    app_path = os.path.join(REPO_ROOT, "web", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=app_path)
    print("[CHECK 1] web/app.py syntax valid.")

    # 2. Check templates & static assets exist
    required_files = [
        "web/templates/index.html",
        "web/static/css/style.css",
        "web/static/js/app.js",
    ]
    for rel in required_files:
        full = os.path.join(REPO_ROOT, rel)
        assert os.path.exists(full) and os.path.getsize(full) > 500, f"Missing or empty: {rel}"
    print("[CHECK 2] All HTML/CSS/JS animated UI assets present.")

    # 3. Verify AI Assistant answers website questions accurately using LIVE twin state
    twin = TwinStateManager(num_steps=120, technicians_total=2)
    twin.current_step = 35
    bot = AgroTwinAssistant(twin)

    on_topic_tests = [
        ("How do I use this website?", "website_guide"),
        ("What is wrong with TR-101?", "machine_status"),
        ("Why are SD-304 and TR-105 on hold?", "machine_status"),
        ("How does the model avoid data leakage and noise?", "ml_explainability"),
        ("How much downtime does Agro-Twin save vs calendar?", "baseline_comparison"),
        ("How do I schedule maintenance when parts are scarce?", "operations_scheduling"),
        ("What needs attention right now?", "live_fleet_summary"),
        ("How does this fit AI in Agriculture scalability?", "track_and_architecture"),
    ]
    for q, expected_topic in on_topic_tests:
        res = bot.answer(q)
        assert res["allowed"] is True and res["warning"] is False, f"Should allow on-topic query: {q}"
        assert res["topic"] == expected_topic, f"Unexpected topic for '{q}': {res['topic']}"
    print(f"[CHECK 3] Passed {len(on_topic_tests)}/{len(on_topic_tests)} live on-topic website queries.")

    # 4. Verify STRICT OFF-TOPIC GUARDRAIL blocks unrelated questions & warns user
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
    ]
    for q in off_topic_tests:
        res = bot.answer(q)
        assert res["allowed"] is False and res["warning"] is True, f"GUARDRAIL FAILED on off-topic query: {q}"
        assert "stick to the contents of this website" in res["answer"].lower()
    print(f"[CHECK 4] Blocked {len(off_topic_tests)}/{len(off_topic_tests)} off-topic queries with clear warning.")

    # 5. Optional live Flask app import check if Flask is installed
    try:
        from web.app import app as flask_app
        client = flask_app.test_client()
        assert client.get("/").status_code == 200
        assert client.get("/api/fleet").status_code == 200
        bad = client.post("/api/assistant", json={"question": "Who is Batman?"}).get_json()
        assert bad["warning"] is True and bad["allowed"] is False
        print("[CHECK 5] Live Flask test_client verified (/, /api/fleet, /api/assistant).")
    except ImportError:
        print("[CHECK 5] Flask not installed in this test env (install via: pip install -r requirements.txt).")

    print("\nALL CHECKS PASSED! Run your animated Flask website with:")
    print("    python web/app.py")
    print("Then open: http://localhost:5000")
    print("=" * 76)


if __name__ == "__main__":
    run_verification()
