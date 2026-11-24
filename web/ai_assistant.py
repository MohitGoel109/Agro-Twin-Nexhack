"""\nAgro-Twin: Strict On-Topic Website Guide & AI Assistant\nExplains how to use every segment of the website and answers live questions\nabout the farm machinery fleet, SVG X-Ray blueprint, Hindi voice mode,\n45°C heatwave stress mode, Rupee ROI, SMS job cards, n8n webhooks, and\nthe AI in Agriculture track.\n\nSTRICT GUARDRAIL: Any query unrelated to the contents of this website is\nblocked with a clear warning asking the user to stick to website topics.\n"""

import re
from typing import List, Tuple

from backend.state import TwinStateManager

OUT_OF_SCOPE_WARNING_EN = (
    "Warning — Out-of-scope query blocked. I am the Agro-Twin Website Assistant and "
    "can only answer questions about how to use this website, its farm machinery fleet, "
    "sensor telemetry, the SVG X-Ray blueprint, Hindi voice readout, 45°C heatwave mode, "
    "maintenance scheduling, Rupee ROI, SMS job cards, n8n webhooks, and Calendar vs. AI "
    "comparisons. Please stick to the contents of this website."
)

OUT_OF_SCOPE_WARNING_HI = (
    "चेतावनी — यह प्रश्न इस वेबसाइट के विषय से बाहर है। मैं केवल Agro-Twin वेबसाइट, "
    "कृषि मशीनरी (ट्रैक्टर/हार्वेस्टर), सेंसर टेलीमेट्री, मेंटेनेंस शेड्यूल, और रुपये (₹) बचत से "
    "जुड़े प्रश्नों का उत्तर दे सकता हूँ। कृपया केवल इस वेबसाइट से संबंधित प्रश्न पूछें।"
)

DEFAULT_SUGGESTIONS = [
    "How do I use this website?",
    "What needs attention right now?",
    "How do the SVG X-Ray & Heatwave mode work?",
    "How much Rupee ROI and downtime does Agro-Twin save?",
]

WEBSITE_KEYWORDS = {
    # Website & navigation
    "website", "site", "app", "dashboard", "page", "segment", "segments", "section", "sections",
    "tab", "tabs", "button", "buttons", "slider", "timeline", "replay", "checkpoint", "checkpoints",
    "sidebar", "navbar", "menu", "reset", "demo", "guide", "tutorial", "walkthrough", "navigate",
    "use", "using", "work", "works", "working", "feature", "features", "overview", "summary",
    "flask", "fastapi", "api", "endpoint", "endpoints", "backend", "frontend", "chart", "charts",
    "graph", "graphs", "animation", "assistant", "chatbot", "guardrail",
    # New Shashi/Team showcase features
    "svg", "xray", "x-ray", "blueprint", "diagram", "subsystem", "subsystems",
    "hindi", "english", "language", "bilingual", "voice", "speak", "speech", "audio",
    "heatwave", "weather", "30c", "45c", "ambient", "thermal", "stress",
    "rupee", "rupees", "inr", "roi", "cost", "money", "profit", "revenue", "financial",
    "sms", "job", "card", "checklist", "bandwidth", "offline", "whatsapp",
    "webhook", "webhooks", "n8n", "notification", "notifications",
    # Agro-Twin domain & machines
    "agro", "agro-twin", "agrotwin", "twin", "fleet", "machine", "machines", "machinery", "unit",
    "units", "tractor", "tractors", "harvester", "harvesters", "seeder", "seed", "drill",
    "tr-101", "tr101", "hv-202", "hv202", "tr-103", "tr103", "sd-304", "sd304", "tr-105", "tr105",
    "hv-206", "hv206", "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
    # Telemetry, ML & Explainability
    "telemetry", "sensor", "sensors", "temperature", "temp", "engine", "vibration", "oil", "pressure",
    "rpm", "variance", "fault", "faults", "failure", "failures", "breakdown", "breakdowns",
    "risk", "probability", "uncertainty", "confidence", "band", "bands", "error", "spike", "spikes",
    "noise", "noisy", "missing", "dropout", "dropouts", "median", "filter", "filtering",
    "model", "random", "forest", "ml", "leak", "leakage", "leak-free", "explain", "explainability",
    "explainable", "reason", "reasons", "predict", "prediction", "predictive", "inject", "injection",
    # Operations, Scheduling & Baseline
    "maintenance", "service", "servicing", "repair", "repairs", "schedule", "scheduler", "scheduling",
    "acknowledge", "acknowledgement", "work", "order", "orders", "wo-001", "wo", "audit", "log",
    "priority", "queue", "readiness", "availability", "downtime", "technician", "technicians",
    "attention", "urgent", "status", "flagged", "alert", "alerts", "warning", "critical", "healthy", "hold",
    "mechanic", "mechanics", "part", "parts", "spare", "spares", "inventory", "stock", "scarcity",
    "coolant", "pump", "hydraulic", "valve", "bearing", "harness", "defer", "deferred", "prevent",
    "prevented", "preventive", "calendar", "calendar-only", "baseline", "compare", "comparison",
    "lead", "saved", "save", "savings", "hour", "hours", "hr", "step",
    # Track, Agriculture & Team
    "agriculture", "agricultural", "farm", "farming", "farmer", "farmers", "harvest", "sowing",
    "plowing", "wheat", "cooperative", "co-op", "rural", "affordability", "affordable", "scalable",
    "scalability", "impact", "track", "nexhack", "hackathon", "ps", "08", "team", "vansh",
    "kunal", "mohit", "shashi", "deadline", "dominators", "criteria", "evaluation",
    # Hindi domain keywords (Devanagari)
    "वेबसाइट", "ट्रैक्टर", "हार्वेस्टर", "सेंसर", "मशीन", "सर्विस", "मरम्मत", "खराबी", "कृषि", "किसान", "बचत", "रुपये",
}

OFF_TOPIC_PATTERNS = [
    r"\b(capital of|president of|prime minister|population of|history of|world war)\b",
    r"\b(cricket|football|soccer|ipl|fifa|nba|movie|film|actor|actress|song|lyrics|anime|manga)\b",
    r"\b(recipe|cook|cooking|biryani|pizza|burger|cake|diet|workout|gym|deadlift)\b",
    r"\b(joke|poem|story|riddle|horoscope|astrology|love|dating|girlfriend|boyfriend)\b",
    r"\b(bitcoin|crypto|stock market|forex|weather forecast|news today|translate to)\b",
    r"\b(bubble sort|binary search|leetcode|html tutorial|java code|c\+\+ code|quantum|physics|chemistry|elon musk|batman|spiderman|chatgpt|openai)\b",
    r"^\s*\d+\s*[\+\-\*\/]\s*\d+\s*\??\s*$",
]

PURE_GREETINGS = {"hi", "hello", "hey", "hii", "hola", "namaste", "नमस्ते", "good morning", "good evening", "good afternoon"}
HELP_PHRASES = {"help", "start", "guide", "how to use", "how do i use", "what can you do", "instructions", "what should i do"}

MACHINE_ALIASES = {
    "TR-101": ["tr-101", "tr101", "101", "alpha"],
    "HV-202": ["hv-202", "hv202", "202", "bravo"],
    "TR-103": ["tr-103", "tr103", "103", "charlie"],
    "SD-304": ["sd-304", "sd304", "304", "delta", "seed drill", "seeder"],
    "TR-105": ["tr-105", "tr105", "105", "echo"],
    "HV-206": ["hv-206", "hv206", "206", "foxtrot"],
}


class AgroTwinAssistant:
    """\nDeterministic, offline-safe, live-state-aware Website AI Assistant with\nstrict off-topic blocking and English/Hindi support.\n"""

    def __init__(self, twin: TwinStateManager):
        self.twin = twin

    def _tokenize(self, text: str) -> set:
        cleaned = re.sub(r"[^\w\-\s]", " ", text.lower(), flags=re.UNICODE)
        tokens = set(cleaned.split())
        extra = {t.replace("-", "") for t in tokens if "-" in t}
        return tokens | extra

    def _find_mentioned_machines(self, text_lower: str) -> List[str]:
        found = []
        for m_id, aliases in MACHINE_ALIASES.items():
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                    found.append(m_id)
                    break
        return found

    def _is_on_topic(self, text: str) -> Tuple[bool, str]:
        raw = text.strip()
        lower = raw.lower()
        clean_punct = re.sub(r"[^\w\s\-]", "", lower, flags=re.UNICODE).strip()

        if not clean_punct:
            return False, "empty"

        if clean_punct in PURE_GREETINGS:
            return True, "greeting"

        if clean_punct in HELP_PHRASES or any(p in lower for p in ["how to use", "how do i use", "walk me through", "guide me", "कैसे उपयोग"]):
            non_site_tools = ["photoshop", "excel", "blender", "instagram", "whatsapp", "chatgpt", "minecraft", "iphone", "android"]
            if any(tool in lower for tool in non_site_tools):
                return False, "off_topic_tool"
            return True, "how_to_use"

        tokens = self._tokenize(raw)
        mentioned_machines = self._find_mentioned_machines(lower)

        strong_anchors = {
            "agro", "agro-twin", "agrotwin", "website", "site", "dashboard", "segment", "segments",
            "fleet", "telemetry", "sensor", "sensors", "tractor", "harvester", "seeder",
            "maintenance", "scheduler", "technician", "technicians", "coolant", "hydraulic",
            "bearing", "calendar", "baseline", "uncertainty", "leak-free", "leakage", "downtime",
            "readiness", "nexhack", "agriculture", "agricultural", "farm", "farming", "harvest",
            "vansh", "kunal", "mohit", "shashi", "svg", "xray", "x-ray", "blueprint", "heatwave",
            "rupee", "rupees", "inr", "roi", "sms", "webhook", "n8n", "hindi", "voice",
            "वेबसाइट", "ट्रैक्टर", "हार्वेस्टर", "सेंसर", "मशीन", "सर्विस", "मरम्मत", "खराबी", "कृषि", "किसान",
        }

        has_strong_anchor = bool(mentioned_machines) or bool(tokens & strong_anchors)

        for pat in OFF_TOPIC_PATTERNS:
            if re.search(pat, lower) and not has_strong_anchor:
                return False, "off_topic_pattern"

        overlap = tokens & WEBSITE_KEYWORDS
        if not overlap and not mentioned_machines:
            return False, "no_domain_overlap"

        weak_only = {
            "use", "using", "work", "works", "working", "error", "hour", "hours", "step",
            "save", "saved", "order", "log", "lead", "part", "stock", "oil", "temp", "seed",
            "explain", "mechanics", "mechanic", "model", "band", "bands", "filter", "track",
            "cost", "money", "weather", "card", "voice", "audio",
        }
        if overlap.issubset(weak_only) and not mentioned_machines and "website" not in lower and "site" not in lower and "app" not in lower:
            return False, "weak_ambiguous_only"

        return True, "on_topic"

    def _format_machine_brief(self, m: dict, step: int) -> str:
        reasons = "; ".join(m["reasons"])
        b_step = m.get("actual_breakdown_step")
        extra = ""
        if b_step is not None and not m["breakdown_prevented"] and step < b_step:
            extra = f" Projected breakdown at Hour {b_step} ({b_step - step}h away)."
        elif m["breakdown_prevented"]:
            extra = " Preventive service has already neutralized its breakdown risk."
        return (
            f"**{m['machine_id']} ({m['name']})** at Hour {step}: "
            f"Status is **{m['status']}** | Fault Risk **{m['fault_probability']*100:.1f}% (±{m['uncertainty']*100:.1f}%)** | "
            f"Confidence **{m['confidence']*100:.0f}%** | Telemetry Feed: **{m['sensor_status']}** | "
            f"Part Needed: **{m['part_needed']}** (Stock: {m['part_in_stock']}).{extra} "
            f"Finding: {reasons}. Next step: {m['recommended_action']}"
        )

    def answer(self, question: str, lang: str = "en") -> dict:
        raw = (question or "").strip()
        is_hindi = (lang == "hi") or bool(re.search(r"[ऀ-ॿ]", raw))

        if not raw:
            return {
                "allowed": False,
                "warning": True,
                "topic": "empty",
                "answer": "Please enter a question about the Agro-Twin website, fleet status, or how to use any section.",
                "suggested_questions": DEFAULT_SUGGESTIONS,
            }

        allowed, reason = self._is_on_topic(raw)
        if not allowed:
            return {
                "allowed": False,
                "warning": True,
                "topic": "out_of_scope",
                "answer": OUT_OF_SCOPE_WARNING_HI if is_hindi else OUT_OF_SCOPE_WARNING_EN,
                "suggested_questions": DEFAULT_SUGGESTIONS,
            }

        lower = raw.lower()
        fleet = self.twin.get_fleet_state()
        step = fleet["step"]
        machines_by_id = {m["machine_id"]: m for m in fleet["machines"]}
        health = self.twin.get_health()
        comp = self.twin.get_baseline_comparison()

        # 1. Website Walkthrough
        if reason in ("greeting", "how_to_use") or any(
            k in lower for k in ["how to use", "how do i use", "walkthrough", "tutorial", "segments", "sections", "guide", "navigate", "कैसे उपयोग"]
        ):
            if is_hindi:
                ans = (
                    "**Agro-Twin वेबसाइट उपयोग गाइड:**\n"
                    "1. **Overview & Heatwave Mode:** ऊपर दिए गए स्लाइडर या **Hr 35 · Alert / Hr 48 · Saved** बटन से हार्वेस्ट घंटे बदलें और **Normal 30°C / Heatwave 45°C** मौसम तनाव जांचें।\n"
                    "2. **Segment 01 (Fleet):** जोखिम और अनिश्चितता बैंड देखें, और **TR-101** पर **Schedule 4h service** दबाकर 18 घंटे का ब्रेकडाउन रोकें।\n"
                    "3. **Segment 02 (SVG X-Ray & Telemetry):** मशीन के इंटरैक्टिव X-Ray ब्लूप्रिंट पर खराब पुर्जे (Coolant Pump, Hydraulic Valve, Drive Bearing) पर क्लिक करें।\n"
                    "4. **Segment 03 (Rupee ROI & Impact):** प्रति घंटा नुकसान (₹) दर्ज करें और Calendar बनाम AI बचत देखें।\n"
                    "5. **Segment 04 (SMS Job Card & n8n):** प्रत्येक वर्क ऑर्डर के लिए हिंदी/अंग्रेज़ी **SMS Job Card** और **n8n Webhook** अलर्ट देखें।"
                )
            else:
                ans = (
                    "Welcome to **Agro-Twin** (AI in Agriculture — Predictive Maintenance Twin). "
                    "The website is divided into 5 clean segments:\n"
                    "1. **Overview, Weather Stress & Timeline:** Toggle **Normal 30°C** vs. **Heatwave 45°C**, or use the hour slider and checkpoints (**Hr 35 · Alert**, **Hr 48 · Saved**, **Hr 55 · Multi**).\n"
                    "2. **Segment 01 — Live Fleet & Interventions:** View fault risk with uncertainty bands and click **Schedule 4h service** on flagged units (try **TR-101** at Hr 35, then jump to **Hr 48 · Saved**).\n"
                    "3. **Segment 02 — SVG X-Ray Blueprint & Telemetry:** Click any subsystem on the interactive machine X-Ray blueprint (**Coolant Pump**, **Hydraulic Valve**, **Drive Bearing**, **Sensor Harness**) and inspect the 4 raw sensor charts.\n"
                    "4. **Segment 03 — Impact & Rupee (₹) ROI:** Adjust hourly harvest loss (`₹/hr`) and part cost (`₹`) to see net Rupee savings and Calendar vs. AI availability.\n"
                    "5. **Segment 04 — Operations, SMS Job Cards & n8n Webhooks:** Open bilingual **SMS Job Cards** with 4-step mechanic checklists, configure an **n8n Webhook URL**, or inject live faults."
                )
            return {
                "allowed": True,
                "warning": False,
                "topic": "website_guide",
                "answer": ans,
                "suggested_questions": [
                    "What needs attention right now?",
                    "How do the SVG X-Ray & Heatwave mode work?",
                    "How much Rupee ROI and downtime does Agro-Twin save?",
                    "How do SMS job cards and n8n webhooks work?",
                ],
            }

        # 2. Specific machine query
        mentioned = self._find_mentioned_machines(lower)
        if mentioned:
            lines = [self._format_machine_brief(machines_by_id[m_id], step) for m_id in mentioned if m_id in machines_by_id]
            return {
                "allowed": True,
                "warning": False,
                "topic": "machine_status",
                "answer": "\n\n".join(lines),
                "suggested_questions": [
                    "How do I schedule a repair?",
                    "How does the SVG X-Ray blueprint work?",
                    "How much Rupee ROI and downtime does Agro-Twin save?",
                ],
            }

        # 3. SVG X-Ray Blueprint & Hindi/English Voice Mode
        if any(k in lower for k in ["svg", "xray", "x-ray", "blueprint", "diagram", "subsystem", "hindi", "voice", "speak", "speech", "bilingual", "language"]):
            return {
                "allowed": True,
                "warning": False,
                "topic": "ui_accessibility_features",
                "answer": (
                    "**Interactive SVG X-Ray Blueprint & Bilingual Voice Mode:**\n"
                    "• **SVG Machine X-Ray Blueprint (Segment 02):** Displays a clean vector schematic of the selected farm unit with 4 clickable subsystems (**Coolant Pump**, **Hydraulic Valve**, **Drive Bearing**, **Sensor Harness**). When a unit has a developing fault (`>=40%` risk), its target component highlights in warm harvest amber (`#e59a32`); on missing telemetry it highlights in muted slate (`#6e8898`).\n"
                    "• **EN / हिंदी Toggle & Speak Alert (Top Bar):** Click **EN / हिंदी** to switch key operational labels and AI responses into Hindi, and click **Speak Alert** to hear the top priority dispatch read aloud via browser Speech Synthesis (`hi-IN` / `en-IN`) with zero external API keys."
                ),
                "suggested_questions": [
                    "Tell me about TR-101",
                    "How does Heatwave 45°C mode affect the fleet?",
                    "How do SMS job cards and n8n webhooks work?",
                ],
            }

        # 4. Heatwave 45°C Weather Stress Mode
        if any(k in lower for k in ["heatwave", "weather", "30c", "45c", "ambient", "thermal", "stress"]):
            return {
                "allowed": True,
                "warning": False,
                "topic": "weather_stress",
                "answer": (
                    "**45°C Harvest Heatwave Stress Mode (Segment 00):**\n"
                    "• **Why It Matters:** Peak North Indian wheat/paddy harvest frequently hits 42–45°C, straining cooling loops and hydraulic oil viscosity.\n"
                    "• **What Toggling Heatwave 45°C Does:** Shifts ambient engine temperatures up by `+8.0°C`, drops oil pressure by `-2.5 PSI`, and tightens fault breakdown lead times by ~4 hours so judges can verify that Agro-Twin's scheduler adapts dynamically under severe field stress."
                ),
                "suggested_questions": [
                    "What needs attention right now?",
                    "How much Rupee ROI and downtime does Agro-Twin save?",
                    "How do I use this website?",
                ],
            }

        # 5. Rupee ROI & Baseline Comparison
        if any(k in lower for k in ["rupee", "rupees", "inr", "roi", "cost", "money", "profit", "revenue", "financial", "calendar", "baseline", "compare", "comparison", "save", "saved", "savings", "downtime", "lead time", "availability", "impact"]):
            cal = comp["calendar_only"]
            ai = comp["ai_twin"]
            imp = comp["improvement"]
            hours_saved = imp["downtime_hours_saved"]
            gross_inr = int(round(hours_saved * 2500))
            spend_inr = int(round(ai["preventive_services_completed"] * 2200))
            net_inr = gross_inr - spend_inr
            roi_x = round(gross_inr / max(1, spend_inr), 1)
            return {
                "allowed": True,
                "warning": False,
                "topic": "baseline_comparison",
                "answer": (
                    f"**Calendar-Only vs. Agro-Twin & Rupee (₹) ROI (Segment 03):**\n"
                    f"• **Fleet Availability:** Rises from **{cal['fleet_availability_pct']}%** (Calendar) to **{ai['fleet_availability_pct']}%** (Agro-Twin) — a **+{imp['availability_gain_pct']}%** gain.\n"
                    f"• **Downtime Saved:** **{hours_saved} hours saved** ({ai['total_downtime_hours']}h AI vs. {cal['total_downtime_hours']}h Calendar), avoiding **{imp['breakdowns_avoided']}** unplanned breakdowns with **{ai['avg_warning_lead_time_hours']}h** average early warning.\n"
                    f"• **Rupee (₹) Harvest ROI (at ₹2,500/hr loss & ₹2,200/part):** Protects **₹{gross_inr:,}** in harvest value for **₹{spend_inr:,}** in preventive parts — **₹{net_inr:,} net savings ({roi_x}x ROI)**."
                ),
                "suggested_questions": [
                    "How do SMS job cards and n8n webhooks work?",
                    "How does Heatwave 45°C mode affect the fleet?",
                    "What needs attention right now?",
                ],
            }

        # 6. Noise / Missing data / Uncertainty / Leak-free ML explanation
        if any(k in lower for k in ["noise", "noisy", "spike", "missing", "dropout", "uncertainty", "confidence", "leak", "random forest", "model", "median", "explain"]):
            info = health["model_info"]
            return {
                "allowed": True,
                "warning": False,
                "topic": "ml_explainability",
                "answer": (
                    f"**How Agro-Twin's AI Engine Works (Segment 02):**\n"
                    f"• **Model:** {info['model_type']}.\n"
                    f"• **Zero Data Leakage:** {info['leak_free_guarantee']}\n"
                    f"• **Noise vs. Real Faults:** Raw sensors pass through a **{info['noise_filter']}**, rejecting isolated 1-hour spikes (like **SD-304** at Hour 35) so scarce mechanics aren't wasted.\n"
                    f"• **Uncertainty & Dropouts:** {info['uncertainty_method']} Missing readings (like **TR-105** at Hour 35) raise uncertainty and hold dispatch until clean telemetry resumes."
                ),
                "suggested_questions": [
                    "Tell me about SD-304",
                    "Tell me about TR-105",
                    "How do the SVG X-Ray & Heatwave mode work?",
                ],
            }

        # 7. Scheduling, SMS Job Cards, n8n Webhooks, Scarcity & Work Orders
        if any(k in lower for k in ["sms", "job", "card", "checklist", "bandwidth", "webhook", "webhooks", "n8n", "schedule", "repair", "service", "work order", "technician", "mechanic", "part", "parts", "spare", "stock", "scarcity", "defer", "acknowledge", "priority"]):
            res = fleet["resources"]
            parts_str = ", ".join(f"{k}: {v}" for k, v in res["parts_inventory"].items())
            return {
                "allowed": True,
                "warning": False,
                "topic": "operations_scheduling",
                "answer": (
                    f"**Constrained Maintenance, SMS Job Cards & n8n Webhooks (Segments 01 & 04):**\n"
                    f"• **Live Resources (Hour {step}):** **{res['technicians_available']}/{res['technicians_total']}** technicians free | Parts: **{parts_str}**.\n"
                    f"• **Low-Bandwidth SMS Job Cards:** After clicking **Schedule 4h service** on a unit, open Segment 04 and click **View SMS Card** on the work order to inspect a `<=160`-character English + Hindi SMS dispatch and 4-step mechanic checklist built for rural connectivity.\n"
                    f"• **n8n Alert Webhooks:** Paste an n8n webhook URL in Segment 04 to fire live JSON alerts whenever work orders are scheduled or faults are injected."
                ),
                "suggested_questions": [
                    "What needs attention right now?",
                    "How much Rupee ROI and downtime does Agro-Twin save?",
                    "How do I use this website?",
                ],
            }

        # 8. Fault Injection / Reset / Timeline Controls
        if any(k in lower for k in ["inject", "injection", "reset", "slider", "checkpoint", "replay"]):
            return {
                "allowed": True,
                "warning": False,
                "topic": "simulation_controls",
                "answer": (
                    "**Interactive Simulation Controls:**\n"
                    "• **Timeline Replay (Segment 00):** Drag the Simulation Hour slider (`0–119`), nudge `-1 hr / +1 hr`, or click quick checkpoints (**Hr 35 · Alert**, **Hr 48 · Saved**, **Hr 55 · Multi**).\n"
                    "• **Live Fault Injection (Segment 04):** Pick any healthy machine (like **HV-206**), select a fault mode, click **Inject fault at current hour**, and step forward 10 hours to watch early detection.\n"
                    "• **Reset:** Click **Reset** in Segment 00 to restore Hour 35, Normal 30°C weather, spare parts, and work orders."
                ),
                "suggested_questions": [
                    "What needs attention right now?",
                    "How do I use this website?",
                    "Tell me about HV-206",
                ],
            }

        # 9. Agriculture track, Affordability, Scalability, Team & Architecture
        if any(k in lower for k in ["agriculture", "agricultural", "farm", "farmer", "scalable", "scalability", "affordable", "affordability", "track", "team", "vansh", "kunal", "mohit", "shashi", "flask", "api", "architecture", "nexhack", "criteria"]):
            return {
                "allowed": True,
                "warning": False,
                "topic": "track_and_architecture",
                "answer": (
                    "**Agro-Twin — AI in Agriculture Track & 4-Member Architecture:**\n"
                    "• **Practical Rural Fit:** Protects shared tractor/harvester cooperatives during short harvest windows using existing sensors, Hindi voice/SMS alerts, and Rupee ROI clarity.\n"
                    "• **4-Member Modular Stack:** **Vansh (`ml/`)** leak-free ML & 45°C heatwave engine, **Kunal (`ops/`)** constrained scheduler, Rupee ROI & SMS job cards, **Mohit (`backend/`)** unified twin state, FastAPI & n8n webhooks, and **Shashi (`web/`)** segmented Flask UI, SVG X-Ray blueprint & on-topic AI guide."
                ),
                "suggested_questions": [
                    "How do I use this website?",
                    "How much Rupee ROI and downtime does Agro-Twin save?",
                    "How do the SVG X-Ray & Heatwave mode work?",
                ],
            }

        # 10. Default live fleet briefing
        pq = fleet["priority_queue"]
        if pq:
            top = pq[0]
            pq_summary = (
                f"Top priority unit right now is **{top['machine_id']} ({top['name']})** "
                f"(Priority Score **{top['priority_score']}**, Risk **{top['fault_probability']*100:.0f}%**, "
                f"Part: **{top['part_needed']}**, Stock: {top['part_in_stock']}). {top['recommended_action']}"
            )
        else:
            pq_summary = "No urgent maintenance dispatches are needed at this hour."

        held_units = [m["machine_id"] for m in fleet["machines"] if m["sensor_status"] != "CLEAN"]
        held_text = f" Data-quality holds active on: **{', '.join(held_units)}** (noise/dropout protection)." if held_units else ""

        return {
            "allowed": True,
            "warning": False,
            "topic": "live_fleet_summary",
            "answer": (
                f"**Live Fleet Status at Harvest Hour {step} / 119:**\n"
                f"• **Readiness:** **{fleet['fleet_readiness_pct']}%** ({fleet['machines_available']}/{fleet['machines_total']} units active) | "
                f"**Breakdowns Prevented:** **{fleet['breakdowns_prevented']}** | "
                f"**Downtime So Far:** **{fleet['total_downtime_hours']} hrs**.\n"
                f"• **Priority Action:** {pq_summary}{held_text}"
            ),
            "suggested_questions": [
                "Tell me about TR-101",
                "Why are SD-304 and TR-105 on hold?",
                "How much Rupee ROI and downtime does Agro-Twin save?",
                "How do SMS job cards and n8n webhooks work?",
            ],
        }
