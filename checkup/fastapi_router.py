"""FastAPI mirror of the check-up API. In backend/app.py add, after `twin = ...` is created:
    from checkup.fastapi_router import create_router
    app.include_router(create_router(twin))
NOTE: written to match the Flask version; test it with `uvicorn backend.app:app` and open /docs."""
from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response

from checkup import service
from checkup.advice import render_html
from checkup.questions import GROUPS, OWNER_FIELDS, QUESTION_BANK, SYSTEMS


def create_router(twin):
    r = APIRouter(tags=["farmer-checkup"])

    def out(res):
        status, payload = res
        return JSONResponse(payload, status_code=status)

    @r.get("/questions")
    def questions():
        return {"groups": [{"id": g[0], "en": g[1], "hi": g[2]} for g in GROUPS], "owner_fields": OWNER_FIELDS,
                "questions": QUESTION_BANK, "systems": {k: {"en": v[0], "hi": v[1]} for k, v in SYSTEMS.items()}}

    @r.get("/machines/{machine_id}/owner-profile")
    def get_owner(machine_id: str):
        return out(service.get_owner_profile(twin, machine_id))

    @r.post("/machines/{machine_id}/owner-profile")
    def post_owner(machine_id: str, body: dict = Body(default={})):
        return out(service.save_owner_profile(twin, machine_id, body))

    @r.post("/machines/{machine_id}/farmer-report")
    def post_report(machine_id: str, body: dict = Body(default={})):
        return out(service.submit(twin, machine_id, body))

    @r.get("/machines/{machine_id}/farmer-report")
    def get_report(machine_id: str):
        return out(service.latest(machine_id))

    @r.get("/machines/{machine_id}/report")
    def report(machine_id: str, lang: str = Query("en"), format: str = Query("html")):
        lang = "hi" if lang == "hi" else "en"
        rep = service.report_data(machine_id, lang)
        if rep is None:
            raise HTTPException(status_code=404, detail="Submit the check-up first")
        if format == "json":
            return rep
        if format == "pdf" and lang == "en":
            from checkup.pdf import build_pdf
            return Response(build_pdf(rep), media_type="application/pdf")
        return HTMLResponse(render_html(rep))

    return r
