"""
Report builder + printable HTML. Advice is GENERAL, safe, no-tools guidance written as rules of thumb.
It must be reviewed by a qualified mechanic, and the Hindi by a native speaker, before real use.
"""

import html
from datetime import datetime, timezone

from checkup.questions import SYSTEMS

TIMEFRAME = {
    "OK": ("Routine service as per your schedule.", "तय कार्यक्रम के अनुसार सामान्य सर्विस।"),
    "WATCH": ("Have it checked within 1 week.", "1 हफ्ते के अंदर जांच कराएं।"),
    "SERVICE_SOON": ("Service within 2-3 days, or before the next heavy use.", "2-3 दिन में या अगले भारी काम से पहले सर्विस कराएं।"),
    "STOP_NOW": ("Stop using the machine and call a mechanic today.", "मशीन चलाना बंद करें और आज ही मैकेनिक बुलाएं।"),
}
HEADLINE = {
    "OK": ("No repair needed right now", "अभी मरम्मत की ज़रूरत नहीं"),
    "WATCH": ("Keep an eye on this machine", "इस मशीन पर नज़र रखें"),
    "SERVICE_SOON": ("This machine needs repair soon", "इस मशीन को जल्द मरम्मत चाहिए"),
    "STOP_NOW": ("Stop: this machine needs a mechanic now", "रुकें: इस मशीन को अभी मैकेनिक चाहिए"),
}
COLOR = {"OK": "#2F7D4F", "WATCH": "#B98200", "SERVICE_SOON": "#C25E00", "STOP_NOW": "#B8452F"}
ICON = {"OK": "✔", "WATCH": "!", "SERVICE_SOON": "⚠", "STOP_NOW": "⛔"}
STATUS_COLOR = {"OK": "#2F7D4F", "DUE_SOON": "#B98200", "OVERDUE": "#B8452F", "CHECK": "#55655B", "NO_DATA": "#55655B"}
STATUS_LABEL = {"OK": ("OK", "ठीक"), "DUE_SOON": ("Due soon", "जल्द"), "OVERDUE": ("Overdue", "देर"),
                "CHECK": ("Check", "जांचें"), "NO_DATA": ("No data", "डेटा नहीं")}

A = {
    "engine": {
        "checks": [("With the engine off and the machine on level ground, check the oil level on the dipstick.", "इंजन बंद करके और समतल जगह पर डिपस्टिक से ऑयल का स्तर देखें।"),
                   ("Look under the machine for fresh oil drips.", "मशीन के नीचे ताज़े तेल की बूंदें देखें।"),
                   ("Note the smoke colour and when the noise happens, so you can tell the mechanic.", "धुएं का रंग और आवाज़ कब आती है, नोट करें ताकि मैकेनिक को बता सकें।")],
        "dont": [("Do not keep running the engine if it is knocking or the oil warning light is on.", "इंजन ठक-ठक कर रहा हो या ऑयल लाइट जल रही हो तो चलाते न रहें।")],
        "mech": ("Please check engine oil pressure, oil level, belts and injectors.", "कृपया इंजन ऑयल प्रेशर, ऑयल स्तर, बेल्ट और इंजेक्टर जांचें।")},
    "cooling": {
        "checks": [("When the engine is COLD, check the coolant level in the tank.", "इंजन ठंडा होने पर टंकी में कूलेंट का स्तर देखें।"),
                   ("Look for wet patches or drips near the radiator and hoses.", "रेडिएटर और पाइपों के पास गीलापन या बूंदें देखें।"),
                   ("With the engine off, check the radiator fins for blocked dust or straw.", "इंजन बंद करके रेडिएटर में धूल या भूसा जमा तो नहीं, देखें।")],
        "dont": [("Never open the radiator cap on a hot engine. Steam can burn badly.", "गरम इंजन पर रेडिएटर का ढक्कन कभी न खोलें। भाप से बुरी तरह जल सकते हैं।")],
        "mech": ("Please check the radiator, hoses, water pump, thermostat and coolant level.", "कृपया रेडिएटर, पाइप, वॉटर पंप, थर्मोस्टेट और कूलेंट जांचें।")},
    "brakes": {
        "checks": [("With the machine parked and the engine off, look for wet fluid near the wheels.", "मशीन खड़ी करके और इंजन बंद करके पहियों के पास गीलापन देखें।"),
                   ("Check that the brake fluid reservoir is at the correct level (level ground, engine off).", "ब्रेक फ्लूइड टंकी में सही स्तर है या नहीं देखें (समतल जगह, इंजन बंद)।"),
                   ("Note whether the pedal feels soft, goes far down or pulls to one side. Do not test at speed.", "नोट करें कि पैडल नरम है, बहुत नीचे जाता है या एक तरफ खींचता है। तेज़ चलाकर टेस्ट न करें।")],
        "dont": [("Do not keep working or drive on roads with soft, spongy or weak brakes.", "नरम, स्पंजी या कमज़ोर ब्रेक के साथ काम या सड़क पर चलाना बंद करें।")],
        "mech": ("Please check brake fluid, lines, pads or linings and the master cylinder.", "कृपया ब्रेक फ्लूइड, लाइनें, पैड/लाइनिंग और मास्टर सिलेंडर जांचें।")},
    "hydraulics": {
        "checks": [("Look at hoses and joints for wet, oily patches.", "पाइप और जोड़ों पर तेल या गीलापन देखें।"),
                   ("Check the hydraulic oil level as shown in the manual, with the machine level.", "मैनुअल के अनुसार, मशीन समतल करके हाइड्रोलिक ऑयल का स्तर देखें।"),
                   ("Notice if the lift is slow or jerky when raising and lowering without load.", "बिना लोड के उठाते-गिराते समय लिफ्ट धीमी या झटके वाली तो नहीं, देखें।")],
        "dont": [("Never touch or loosen a hydraulic hose or fitting. Oil under pressure can pierce the skin.", "हाइड्रोलिक पाइप या फिटिंग को कभी न छुएं न खोलें। दबाव वाला तेल त्वचा में घुस सकता है।")],
        "mech": ("Please check hydraulic oil, filter, pump, hoses and seals.", "कृपया हाइड्रोलिक ऑयल, फ़िल्टर, पंप, पाइप और सील जांचें।")},
    "drivetrain": {
        "checks": [("Check the gearbox or rear axle oil level and look for leaks, as per the manual.", "मैनुअल के अनुसार गियरबॉक्स/रियर एक्सल ऑयल का स्तर और रिसाव देखें।"),
                   ("Note when the grinding or shaking happens: starting, under load or while turning.", "नोट करें कि घिसने या कांपने की आवाज़ कब आती है: स्टार्ट, लोड या मोड़ते समय।"),
                   ("Check the clutch pedal free play as given in the manual.", "मैनुअल के अनुसार क्लच पैडल का फ्री प्ले देखें।")],
        "dont": [("Do not keep working under load if you hear grinding or smell a burning clutch.", "घिसने की आवाज़ या जलते क्लच की गंध हो तो लोड में काम न करें।")],
        "mech": ("Please check the clutch, gearbox oil, bearings and drive shafts.", "कृपया क्लच, गियरबॉक्स ऑयल, बेयरिंग और ड्राइव शाफ्ट जांचें।")},
    "electrical": {
        "checks": [("Look at the battery terminals for white or green crust and loose clamps.", "बैटरी टर्मिनल पर सफेद/हरी परत और ढीले क्लैंप देखें।"),
                   ("Look under the bonnet for chewed or loose wires (engine off).", "बोनट के नीचे कुतरे या ढीले तार देखें (इंजन बंद)।"),
                   ("Check if the lights are dim, and whether the engine cranks slowly.", "लाइट मद्धम है या इंजन धीरे घूमता है, देखें।")],
        "dont": [("Do not repair burnt or chewed wiring yourself. Do not jump-start a swollen or leaking battery.", "जले या कुतरे तार खुद ठीक न करें। फूली या रिसती बैटरी को जंप-स्टार्ट न करें।")],
        "mech": ("Please do a battery load test and check the alternator, starter and wiring.", "कृपया बैटरी लोड टेस्ट करें और अल्टरनेटर, सेल्फ और वायरिंग जांचें।")},
    "tyres": {
        "checks": [("Check tyre pressure against the manual and look for cracks, bulges and cuts.", "मैनुअल के अनुसार टायर प्रेशर देखें और दरार, उभार, कट देखें।"),
                   ("Look for uneven wear, which can mean wrong pressure or alignment.", "असमान घिसाव देखें, इसका मतलब गलत प्रेशर या अलाइनमेंट हो सकता है।"),
                   ("Check that wheel nuts look tight (your mechanic should torque them).", "देखें कि व्हील नट कसे दिखते हैं (कसना मैकेनिक का काम)।")],
        "dont": [("Do not drive on a bulging or cut tyre.", "उभरे या कटे टायर पर न चलाएं।")],
        "mech": ("Please check the tyres, wheel alignment, steering joints and tie rods.", "कृपया टायर, व्हील अलाइनमेंट, स्टीयरिंग जोड़ और टाई रॉड जांचें।")},
    "fuel": {
        "checks": [("Look for diesel drips at the filter, lines and tank.", "फ़िल्टर, पाइप और टंकी पर डीज़ल की बूंदें देखें।"),
                   ("Check how old the fuel is. Fuel stored longer than about 6 months can go stale.", "ईंधन कितना पुराना है, देखें। लगभग 6 महीने से पुराना ईंधन खराब हो सकता है।"),
                   ("Note black smoke or loss of power and when it happens.", "काला धुआं या ताकत कम होना और यह कब होता है, नोट करें।")],
        "dont": [("Do not check or top up fuel near flames or on a hot engine.", "आग के पास या गरम इंजन पर ईंधन न जांचें, न भरें।")],
        "mech": ("Please check the fuel filter, injectors and water in fuel. Drain stale fuel if needed.", "कृपया फ्यूल फ़िल्टर, इंजेक्टर और ईंधन में पानी जांचें। ज़रूरत हो तो पुराना ईंधन निकालें।")},
}

DISCLAIMER = ("Based on your answers and simulated demo data. Service intervals shown are placeholders; follow the machine manual. This is not a mechanic's inspection. When in doubt, stop and ask a mechanic.",
              "यह आपके जवाबों और डेमो (नकली) डेटा पर आधारित है। दिखाए गए सर्विस अंतराल नमूना हैं; मशीन का मैनुअल मानें। यह मैकेनिक की जांच नहीं है। शक हो तो रुकें और मैकेनिक से पूछें।")


def _pick(pair, lang):
    return pair[1] if lang == "hi" else pair[0]


def build_report(machine, result, lang="en", report_id=None):
    """machine: dict(machine_id, name, type). result: output of scoring.score_report."""
    lang = "hi" if lang == "hi" else "en"
    urgency = result["urgency"]
    suspected = result["suspected_systems"]
    stop = urgency == "STOP_NOW"
    checks, donts, mech_lines = [], [], []
    for s in suspected:
        adv = A[s]
        sysname = _pick(SYSTEMS[s], lang)
        mech_lines.append({"system": sysname, "text": _pick(adv["mech"], lang)})
        for d in adv["dont"]:
            donts.append(_pick(d, lang))
        if not stop:
            for c in adv["checks"]:
                checks.append({"system": sysname, "text": _pick(c, lang)})
    if stop:
        checks = []
        donts.insert(0, _pick(("Do not try to repair it yourself. Park it safely on level ground, switch off, and keep people away.",
                               "खुद मरम्मत की कोशिश न करें। मशीन को समतल जगह पर सुरक्षित खड़ी करें, बंद करें और लोगों को दूर रखें।"), lang))
    sys_names = ", ".join(_pick(SYSTEMS[s], lang) for s in suspected) or ("none identified" if lang == "en" else "कोई नहीं")
    if lang == "hi":
        msg = "नमस्ते, मेरी %s (%s) में समस्या है। संदिग्ध हिस्से: %s। जल्दी: %s। %s" % (
            machine["name"], machine["machine_id"], sys_names, _pick(TIMEFRAME[urgency], lang),
            " ".join(m["text"] for m in mech_lines))
    else:
        msg = "Hello, my %s (%s) may need repair. Suspected: %s. How soon: %s %s" % (
            machine["name"], machine["machine_id"], sys_names, _pick(TIMEFRAME[urgency], lang),
            " ".join(m["text"] for m in mech_lines))
    return {
        "report_id": report_id or datetime.now(timezone.utc).strftime("AT-%Y%m%d-%H%M%S"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "lang": lang,
        "machine": machine,
        "urgency": urgency,
        "needs_repair": urgency in ("SERVICE_SOON", "STOP_NOW"),
        "headline": _pick(HEADLINE[urgency], lang),
        "timeframe": _pick(TIMEFRAME[urgency], lang),
        "confidence": result["confidence"],
        "found": [r[lang] for r in result["reasons"]],
        "risks": {k: result[k] for k in ("sensor_risk", "symptom_risk", "owner_risk", "combined_risk")},
        "ideal_vs_current": [{"item": r["item_" + lang], "line": r["line_" + lang], "status": r["status"],
                              "status_label": _pick(STATUS_LABEL[r["status"]], lang)} for r in result["ideal_vs_current"]],
        "suspected": [_pick(SYSTEMS[s], lang) for s in suspected],
        "self_checks": checks,
        "needs_mechanic": mech_lines,
        "do_not": donts,
        "mechanic_message": msg,
        "disclaimer": _pick(DISCLAIMER, lang),
        "demo_label": "Demo data" if lang == "en" else "डेमो डेटा",
    }


def render_html(rep):
    """Self-contained, print-friendly A4 report. Use the browser's Print > Save as PDF."""
    e = html.escape
    hi = rep["lang"] == "hi"
    T = (lambda en, h: h if hi else en)
    col = COLOR[rep["urgency"]]

    def li(items):
        return "".join("<li>%s</li>" % e(i) for i in items) or "<li>-</li>"

    rows = "".join(
        "<tr><td>%s</td><td style='color:%s;font-weight:700'>%s</td></tr>" % (e(r["line"]), STATUS_COLOR[r["status"]], e(r["status_label"]))
        for r in rep["ideal_vs_current"])
    checks = "".join("<li><b>%s:</b> %s</li>" % (e(c["system"]), e(c["text"])) for c in rep["self_checks"])
    mech = "".join("<li><b>%s:</b> %s</li>" % (e(m["system"]), e(m["text"])) for m in rep["needs_mechanic"])
    rk = rep["risks"]
    pct = lambda v: "-" if v is None else "%d%%" % round(v * 100)
    low = ("<p class='note'>%s</p>" % e(T("Few answers or many 'Not sure': treat this result as low confidence.",
                                          "जवाब कम या बहुत 'पता नहीं': इस नतीजे पर कम भरोसा करें।"))) if rep["confidence"] == "LOW" else ""
    wa = "https://wa.me/?text=" + __import__("urllib.parse").parse.quote(rep["mechanic_message"])
    return """<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Machine Health Report %(rid)s</title><style>
body{font-family:Calibri,Arial,"Noto Sans Devanagari",sans-serif;margin:0;padding:16px;color:#1B2A22;background:#fff;max-width:820px;margin:auto;font-size:17px;line-height:1.45}
.banner{background:%(col)s;color:#fff;border-radius:12px;padding:18px 20px}.banner h1{margin:0;font-size:26px}.banner p{margin:6px 0 0}
h2{font-size:19px;margin:22px 0 6px;color:#14301F}table{border-collapse:collapse;width:100%%}td{border-bottom:1px solid #D9E6D0;padding:7px 4px;font-size:15px}
.meta{color:#55655B;font-size:14px;margin:8px 0}.box{background:#EEF3E8;border-radius:10px;padding:10px 14px}.note{color:#B8452F;font-weight:700}
.msg{background:#fff;border:1px dashed #55655B;border-radius:10px;padding:10px 14px}.btn{display:inline-block;background:#2F7D4F;color:#fff;border:0;border-radius:8px;padding:10px 16px;font-size:16px;margin:6px 6px 0 0;text-decoration:none;cursor:pointer}
.foot{font-size:13px;color:#55655B;margin-top:22px;border-top:1px solid #D9E6D0;padding-top:8px}li{margin:4px 0}
@media print{.noprint{display:none}body{padding:0;font-size:14px}}
</style></head><body>
<div class="banner"><h1>%(icon)s %(headline)s</h1><p>%(tf)s</p></div>
<p class="meta">%(mname)s (%(mid)s) · %(gen)s · %(rid)s · <b>%(demo)s</b></p>
<p class="noprint"><button class="btn" onclick="window.print()">%(print)s</button><a class="btn" href="%(wa)s" target="_blank" rel="noopener">%(share)s</a></p>
%(low)s
<h2>%(h_found)s</h2><ul>%(found)s</ul>
<p class="meta">%(risk_l)s: %(sr)s · %(sy)s %(syv)s · %(ow)s %(owv)s · %(cb)s %(cbv)s</p>
<h2>%(h_ideal)s</h2><table>%(rows)s</table>
<h2>%(h_mech)s</h2><div class="box"><b>%(susp_l)s</b> %(susp)s<ul>%(mech)s</ul></div>
%(checks_block)s
<h2>%(h_dont)s</h2><ul>%(dont)s</ul>
<h2>%(h_msg)s</h2><div class="msg">%(msg)s</div>
<p class="foot">%(disc)s</p></body></html>""" % dict(
        lang=rep["lang"], rid=e(rep["report_id"]), col=col, icon=ICON[rep["urgency"]], headline=e(rep["headline"]), tf=e(rep["timeframe"]),
        mname=e(rep["machine"]["name"]), mid=e(rep["machine"]["machine_id"]), gen=e(rep["generated_at"]), demo=e(rep["demo_label"]),
        print=e(T("Print / Save as PDF", "प्रिंट / PDF सेव करें")), share=e(T("Share on WhatsApp", "व्हाट्सऐप पर भेजें")), wa=e(wa),
        low=low, h_found=e(T("What we found", "हमें क्या मिला")), found=li(rep["found"]),
        risk_l=e(T("Risk", "जोखिम")), sr=e(T("Sensors", "सेंसर") + " " + pct(rk["sensor_risk"])),
        sy=e(T("Your answers", "आपके जवाब")), syv=pct(rk["symptom_risk"]), ow=e(T("Owner form", "मालिक फॉर्म")), owv=pct(rk["owner_risk"]),
        cb=e(T("Combined", "कुल")), cbv=pct(rk["combined_risk"]),
        h_ideal=e(T("Placeholder service intervals vs current", "नमूना सर्विस अंतराल बनाम मौजूदा")), rows=rows,
        h_mech=e(T("What needs a mechanic", "मैकेनिक को क्या देखना है")), susp_l=e(T("Suspected:", "संदिग्ध:")),
        susp=e(", ".join(rep["suspected"]) or "-"), mech=mech or "<li>-</li>",
        checks_block=("<h2>%s</h2><ul>%s</ul>" % (e(T("What you can safely check yourself", "आप खुद सुरक्षित रूप से क्या देख सकते हैं")), checks)) if checks else "",
        h_dont=e(T("Do not do this", "यह न करें")), dont=li(rep["do_not"]),
        h_msg=e(T("Message for your mechanic", "आपके मैकेनिक के लिए संदेश")), msg=e(rep["mechanic_message"]), disc=e(rep["disclaimer"]))
