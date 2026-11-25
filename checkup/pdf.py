"""English PDF of the Machine Health Report (reportlab). Hindi PDF is NOT produced here: reportlab cannot shape
Devanagari (matras/conjuncts break), so the Hindi report uses the HTML print version instead."""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

COL = {"OK": "#2F7D4F", "WATCH": "#B88A00", "SERVICE_SOON": "#C25E00", "STOP_NOW": "#B3261E"}
LABEL = {"OK": "[OK]", "WATCH": "[WATCH]", "SERVICE_SOON": "[SERVICE SOON]", "STOP_NOW": "[STOP NOW]"}


def build_pdf(rep):
    buf = BytesIO()
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=11, leading=15)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=14, spaceBefore=10, spaceAfter=4)
    small = ParagraphStyle("s", parent=body, fontSize=9, textColor=colors.HexColor("#55655B"))
    e = lambda x: escape(str(x))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#55655B"))
        canvas.drawString(15 * mm, 9 * mm, "Generated %s | Report %s | %s | Page %d" % (
            rep["generated_at"], rep["report_id"], rep["demo_label"], doc.page))
        canvas.restoreState()

    col = colors.HexColor(COL[rep["urgency"]])
    banner = Table([[Paragraph("<font color='white'><b>%s %s</b><br/>%s</font>" % (
        LABEL[rep["urgency"]], e(rep["headline"]), e(rep["timeframe"])),
        ParagraphStyle("bn", parent=body, fontSize=15, leading=20))]], colWidths=[180 * mm])
    banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), col), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    f = [banner, Spacer(1, 6),
         Paragraph("%s (%s) - %s - %s" % (e(rep["machine"]["name"]), e(rep["machine"]["machine_id"]), e(rep["generated_at"]), e(rep["demo_label"])), small)]
    if rep["confidence"] == "LOW":
        f.append(Paragraph("<b>Few answers or many 'Not sure': treat this result as low confidence.</b>", body))
    f.append(Paragraph("What we found", h2))
    for x in rep["found"][:5] or ["-"]:
        f.append(Paragraph("&bull; " + e(x), body))
    rk = rep["risks"]
    pct = lambda v: "-" if v is None else "%d%%" % round(v * 100)
    f.append(Paragraph("Risk: sensors %s | your answers %s | owner form %s | combined %s" % (
        pct(rk["sensor_risk"]), pct(rk["symptom_risk"]), pct(rk["owner_risk"]), pct(rk["combined_risk"])), small))
    f.append(Paragraph("Placeholder service intervals vs current", h2))
    sc = {"OK": "#2F7D4F", "DUE_SOON": "#C25E00", "OVERDUE": "#B3261E", "CHECK": "#55655B", "NO_DATA": "#55655B"}
    rows = [[Paragraph(e(r["line"]), body), Paragraph("<font color='%s'><b>%s</b></font>" % (sc.get(r["status"], "#55655B"), e(r["status_label"])), body)]
            for r in rep["ideal_vs_current"]]
    if rows:
        t = Table(rows, colWidths=[150 * mm, 30 * mm])
        t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E6D0")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        f.append(t)
    f.append(Paragraph("What needs a mechanic", h2))
    f.append(Paragraph("<b>Suspected:</b> " + e(", ".join(rep["suspected"]) or "-"), body))
    for m in rep["needs_mechanic"]:
        f.append(Paragraph("&bull; <b>%s:</b> %s" % (e(m["system"]), e(m["text"])), body))
    if rep["self_checks"]:
        f.append(Paragraph("What you can safely check yourself", h2))
        for c in rep["self_checks"]:
            f.append(Paragraph("&bull; <b>%s:</b> %s" % (e(c["system"]), e(c["text"])), body))
    f.append(Paragraph("Do not do this", h2))
    for d in rep["do_not"] or ["-"]:
        f.append(Paragraph("&bull; " + e(d), body))
    f.append(Paragraph("Message for your mechanic", h2))
    f.append(Paragraph(e(rep["mechanic_message"]), body))
    f.append(Spacer(1, 10))
    f.append(Paragraph(e(rep["disclaimer"]), small))
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=18 * mm,
                      title="Machine Health Report " + rep["report_id"]).build(f, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
