"""Flask blueprint for the Farmer Check-up. Register in web/app.py:  app.register_blueprint(create_blueprint(twin))"""
import html as _html
import json

from flask import Blueprint, Response, jsonify, render_template, request
from jinja2 import TemplateNotFound

from checkup import service
from checkup.advice import render_html
from checkup.questions import GROUPS, OWNER_FIELDS, QUESTION_BANK, SYSTEMS

HI_PDF_NOTICE = ("<div style='background:#FFF3CD;border:2px solid #B88A00;padding:10px 14px;font-family:Arial,sans-serif;font-size:15px'>"
                 "Hindi PDF download is not available (Hindi text needs a font and shaping that the PDF tool does not have). "
                 "Use <b>Print / Save as PDF</b> below. / हिंदी PDF डाउनलोड उपलब्ध नहीं है। नीचे <b>प्रिंट / PDF सेव करें</b> का उपयोग करें।</div>")


def create_blueprint(twin):
    bp = Blueprint("checkup", __name__)

    def reply(res):
        status, payload = res
        return jsonify(payload), status

    @bp.route("/checkup")
    def page():
        try:
            return render_template("checkup.html")
        except TemplateNotFound:
            return "Farmer Check-up page not installed yet (web/templates/checkup.html missing).", 404

    @bp.route("/api/checkup/questions")
    def questions():
        return jsonify({
            "groups": [{"id": g[0], "en": g[1], "hi": g[2]} for g in GROUPS],
            "owner_fields": OWNER_FIELDS,
            "questions": QUESTION_BANK,
            "systems": {k: {"en": v[0], "hi": v[1]} for k, v in SYSTEMS.items()},
            "note": "Rule-based rules of thumb. Not a replacement for a mechanic.",
        })

    @bp.route("/api/checkup/machines")
    def machines():
        return jsonify(service.machines_list(twin))

    @bp.route("/api/checkup/<machine_id>/owner-profile", methods=["GET", "POST"])
    def owner_profile(machine_id):
        if request.method == "GET":
            return reply(service.get_owner_profile(twin, machine_id))
        return reply(service.save_owner_profile(twin, machine_id, request.get_json(silent=True) or {}))

    @bp.route("/api/checkup/<machine_id>/submit", methods=["POST"])
    def submit(machine_id):
        return reply(service.submit(twin, machine_id, request.get_json(silent=True) or {}))

    @bp.route("/api/checkup/<machine_id>")
    def latest(machine_id):
        return reply(service.latest(machine_id))

    @bp.route("/api/checkup/<machine_id>/report")
    def report(machine_id):
        lang = "hi" if request.args.get("lang") == "hi" else "en"
        fmt = request.args.get("format", "html")
        rep = service.report_data(machine_id, lang)
        if rep is None:
            return jsonify({"ok": False, "error": "Submit the check-up first"}), 404
        if fmt == "json":
            return jsonify(rep)
        if fmt == "pdf":
            if lang == "hi":
                return Response(HI_PDF_NOTICE + render_html(rep), mimetype="text/html")
            from checkup.pdf import build_pdf
            return Response(build_pdf(rep), mimetype="application/pdf",
                            headers={"Content-Disposition": "attachment; filename=machine-health-report-%s.pdf" % _html.escape(machine_id)})
        return Response(render_html(rep), mimetype="text/html")

    @bp.route("/api/checkup/bulk-report")
    def bulk_report():
        from ml import bulk_predict
        rep = bulk_predict.report()
        if rep is None:
            return jsonify({"ok": False, "error": "Bulk model report not found. Run: python ml/train_bulk.py"}), 404
        return jsonify({"ok": True, "label": "Trained on %d simulated machines (Synthetic data)" % rep["n_train_machines"], "report": rep,
                        "benchmark": bulk_predict.benchmark()})

    @bp.route("/api/checkup/<machine_id>/bulk-risk")
    def bulk_risk(machine_id):
        from checkup import store
        from ml import bulk_predict
        m = service.find_machine(twin, machine_id)
        if m is None:
            return jsonify({"ok": False, "error": "Unknown machine"}), 404
        rec = store.get(machine_id)
        if rec is None:
            return jsonify({"ok": False, "error": "Submit the check-up first"}), 404
        out = bulk_predict.predict(m["type"], rec["owner"], rec["answers"], m.get("raw_sensors"))
        if out is None:
            return jsonify({"ok": False, "error": "Bulk model not available"}), 404
        return jsonify({"ok": True, "ideal_vs_current": rec["result"]["ideal_vs_current"], **out})

    @bp.after_app_request
    def add_farmer_info_to_fleet(response):
        """Adds farmer check-up fields and priority-queue entries to GET /api/fleet. Baseline numbers are untouched."""
        if request.path == "/api/fleet" and request.method == "GET" and response.mimetype == "application/json":
            data = json.loads(response.get_data(as_text=True))
            data = service.annotate_fleet(data)
            response.set_data(json.dumps(data))
        return response

    return bp
