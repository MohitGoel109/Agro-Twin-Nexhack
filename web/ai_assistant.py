"""
Agro-Twin: Strict On-Topic Website Guide & AI Assistant
Explains how to use every segment of the website and answers live questions
about the farm machinery fleet, telemetry, scheduling, baseline results, and
the AI in Agriculture track.

STRICT GUARDRAIL: Any query unrelated to the contents of this website is
blocked with a clear warning asking the user to stick to website topics.
"""

import re
from typing import List, Tuple

from backend.state import TwinStateManager

OUT_OF_SCOPE_WARNING = (
    "Warning — Out-of-scope query blocked. I am the Agro-Twin Website Assistant and "
    "can only answer questions about how to use this website, its farm machinery fleet, "
    "sensor telemetry, noise/uncertainty filtering, maintenance scheduling, Calendar vs. AI "
    "comparisons, and our AI in Agriculture solution. Please stick to the contents of this website."
)

DEFAULT_SUGGESTIONS = [
    "How do I use this website?",
    "What needs attention right now?",
    "Why are SD-304 and TR-105 on hold?",
    "How much downtime does Agro-Twin save?",
]

# Explicit website / Agro-Twin vocabulary required for a query to be considered on-topic
WEBSITE_KEYWORDS = {
    # Website & navigation
    "website", "site", "app", "dashboard", "page", "segment", "segments", "section", "sections",
    "tab", "tabs", "button", "buttons", "slider", "timeline", "replay", "checkpoint", "checkpoints",
    "sidebar", "navbar", "menu", "reset", "demo", "guide", "tutorial", "walkthrough", "navigate",
    "use", "using", "work", "works", "working", "feature", "features", "overview", "summary",
    "flask", "fastapi", "api", "endpoint", "endpoints", "backend", "frontend", "chart", "charts",
    "graph", "graphs", "animation", "assistant", "chatbot", "guardrail",
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
}

# Explicit off-topic patterns that should ALWAYS be blocked if no specific Agro-Twin entity is named
OFF_TOPIC_PATTERNS = [
    r"\b(capital of|president of|prime minister|population of|history of|world war)\b",
    r"\b(cricket|football|soccer|ipl|fifa|nba|movie|film|actor|actress|song|lyrics|anime|manga)\b",
    r"\b(recipe|cook|cooking|biryani|pizza|burger|cake|diet|workout|gym|deadlift)\b",
    r"\b(joke|poem|story|riddle|horoscope|astrology|love|dating|girlfriend|boyfriend)\b",
    r"\b(bitcoin|crypto|stock market|forex|weather forecast|news today|translate to)\b",
    r"\b(bubble sort|binary search|leetcode|html tutorial|java code|c\+\+ code|quantum|physics|chemistry|elon musk|batman|spiderman|chatgpt|openai)\b",
    r"^\s*\d+\s*[\+\-\*\/]\s*\d+\s*\??\s*$",
]

PURE_GREETINGS = {"hi", "hello", "hey", "hii", "hola", "namaste", "good morning", "good evening", "good afternoon"}
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
    """
    Deterministic, offline-safe, live-state-aware Website AI Assistant with
    strict off-topic blocking.
    """

    def __init__(self, twin: TwinStateManager):
        self.twin = twin

    def _tokenize(self, text: str) -> set:
        cleaned = re.sub(r"[^a-z0-9\-\s]", " ", text.lower())
        tokens = set(cleaned.split())
        # Also include hyphen-free tokens so "tr101" and "tr-101" both match
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
        """Returns (is_allowed, reason)."""
        raw = text.strip()
        lower = raw.lower()
        clean_punct = re.sub(r"[^a-z0-9\s\-]", "", lower).strip()

        if not clean_punct:
            return False, "empty"

        if clean_punct in PURE_GREETINGS:
            return True, "greeting"

        if clean_punct in HELP_PHRASES or any(p in lower for p in ["how to use", "how do i use", "walk me through", "guide me"]):
            # Still verify it's not asking "how to use photoshop / excel / blender"
            non_site_tools = ["photoshop", "excel", "blender", "instagram", "whatsapp", "chatgpt", "minecraft", "iphone", "android"]
            if any(tool in lower for tool in non_site_tools):
                return False, "off_topic_tool"
            return True, "how_to_use"

        tokens = self._tokenize(raw)
        mentioned_machines = self._find_mentioned_machines(lower)

        # Specific Agro-Twin anchors override generic words
        strong_anchors = {
            "agro", "agro-twin", "agrotwin", "website", "site", "dashboard", "segment", "segments",
            "fleet", "telemetry", "sensor", "sensors", "tractor", "harvester", "seeder",
            "maintenance", "scheduler", "work", "technician", "technicians", "coolant", "hydraulic",
            "bearing", "calendar", "baseline", "uncertainty", "leak-free", "leakage", "downtime",
            "readiness", "nexhack", "agriculture", "agricultural", "farm", "farming", "harvest",
            "vansh", "kunal", "mohit", "shashi",
        }

        has_strong_anchor = bool(mentioned_machines) or bool(tokens & strong_anchors)

        # Block obvious off-topic queries unless anchored to our website
        for pat in OFF_TOPIC_PATTERNS:
            if re.search(pat, lower) and not has_strong_anchor:
                return False, "off_topic_pattern"

        # Require overlap with website domain keywords
        overlap = tokens & WEBSITE_KEYWORDS
        if not overlap and not mentioned_machines:
            return False, "no_domain_overlap"

        # Prevent vague single-word false positives like "what is the time?" or "how does gravity work?"
        weak_only = {"use", "using", "work", "works", "working", "error", "hour", "hours", "step", "save", "saved", "order", "log", "lead", "part", "stock", "oil", "temp", "seed", "explain", "mechanics", "mechanic", "model", "band", "bands", "filter", "track"}
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

    def answer(self, question: str) -> dict:
        """Processes a user query and enforces strict website-only guardrails."""
        raw = (question or "").strip()
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
                "answer": OUT_OF_SCOPE_WARNING,
                "suggested_questions": DEFAULT_SUGGESTIONS,
            }

        lower = raw.lower()
        fleet = self.twin.get_fleet_state()
        step = fleet["step"]
        machines_by_id = {m["machine_id"]: m for m in fleet["machines"]}
        health = self.twin.get_health()
        comp = self.twin.get_baseline_comparison()

        # 1. Greeting / Onboarding walkthrough
        if reason in ("greeting", "how_to_use") or any(
            k in lower for k in ["how to use", "how do i use", "walkthrough", "tutorial", "segments", "sections", "guide", "navigate"]
        ):
            return {
                "allowed": True,
                "warning": False,
                "topic": "website_guide",
                "answer": (
                    "Welcome to **Agro-Twin** (AI in Agriculture — Predictive Maintenance Twin). "
                    "The website is organized into 5 clear segments you can browse or jump to from the top bar:\n"
                    "1. **Overview & Timeline Replay:** Use the Hour slider or quick checkpoints (**Hr 35 · Alert**, **Hr 48 · Saved**, **Hr 55 · Multi**) to step through a 120-hour harvest window.\n"
                    "2. **Live Fleet & Interventions:** View fault risk with uncertainty bands and click **Schedule 4h Service** or **Acknowledge** on flagged units (try **TR-101** at Hr 35, then jump to **Hr 48 · Saved**).\n"
                    "3. **Telemetry & Noise Proof:** Pick any machine to inspect all 4 raw sensors, see why single-hour spikes (**SD-304**) and dropouts (**TR-105**) are held, and read the leak-free ML rules.\n"
                    "4. **Calendar vs. Agro-Twin:** Slide the calendar interval to compare fixed servicing against AI condition-based servicing on identical faults.\n"
                    "5. **Scarcity, Fault Injection & Work Orders:** Adjust technicians or spare parts stock, inject a live fault into any healthy unit, and track work orders and the audit log."
                ),
                "suggested_questions": [
                    "What needs attention right now?",
                    "Tell me about TR-101",
                    "Why are SD-304 and TR-105 on hold?",
                    "How much downtime does Agro-Twin save?",
                ],
            }

        # 2. Specific machine inquiry
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
                    "Show me the Telemetry & Noise Proof rules",
                    "How much downtime does Agro-Twin save?",
                ],
            }

        # 3. Noise / Missing data / Uncertainty / Leak-free ML explanation
        if any(k in lower for k in ["noise", "noisy", "spike", "missing", "dropout", "uncertainty", "confidence", "leak", "random forest", "model", "median", "explain"]):
            info = health["model_info"]
            return {
                "allowed": True,
                "warning": False,
                "topic": "ml_explainability",
                "answer": (
                    f"**How Agro-Twin's AI Engine Works (Segment 3 — Telemetry & Noise Proof):**\n"
                    f"• **Model:** {info['model_type']}.\n"
                    f"• **Zero Data Leakage:** {info['leak_free_guarantee']}\n"
                    f"• **Noise vs. Real Faults:** Raw sensors pass through a **{info['noise_filter']}**, which automatically rejects isolated 1-hour glitches (like **SD-304** at Hour 35) so scarce mechanics aren't wasted.\n"
                    f"• **Uncertainty & Dropouts:** {info['uncertainty_method']} When readings drop out (like **TR-105** at Hour 35), uncertainty rises and the alert is held until clean data resumes.\n"
                    f"• **Plain-English Explainability:** Every flagged unit lists its top sensor deviations (Engine Temp, Vibration, Oil Pressure, RPM Variance) directly on its card."
                ),
                "suggested_questions": [
                    "Tell me about SD-304",
                    "Tell me about TR-105",
                    "What needs attention right now?",
                ],
            }

        # 4. Baseline comparison / Savings / ROI
        if any(k in lower for k in ["calendar", "baseline", "compare", "comparison", "save", "saved", "savings", "downtime", "lead time", "availability", "impact"]):
            cal = comp["calendar_only"]
            ai = comp["ai_twin"]
            imp = comp["improvement"]
            return {
                "allowed": True,
                "warning": False,
                "topic": "baseline_comparison",
                "answer": (
                    f"**Calendar-Only vs. Agro-Twin Results (Segment 4 — 120-Hour Harvest Window):**\n"
                    f"• **Fleet Availability:** Jumps from **{cal['fleet_availability_pct']}%** (Calendar-Only) to **{ai['fleet_availability_pct']}%** (Agro-Twin) — a **+{imp['availability_gain_pct']}%** gain.\n"
                    f"• **Downtime Saved:** **{imp['downtime_hours_saved']} hours saved** ({ai['total_downtime_hours']}h AI vs. {cal['total_downtime_hours']}h Calendar).\n"
                    f"• **Breakdowns Avoided:** **{ai['unplanned_breakdowns']} unplanned breakdowns** under Agro-Twin vs. **{cal['unplanned_breakdowns']}** under fixed calendar checks.\n"
                    f"• **Early Warning Lead Time:** Average **{ai['avg_warning_lead_time_hours']} hours** before breakdown, while holding **{ai['noisy_or_missing_alerts_held']}** noisy/missing telemetry intervals with zero false dispatches."
                ),
                "suggested_questions": [
                    "How do scarce technicians and parts work?",
                    "How does this scale for farmers?",
                    "What needs attention right now?",
                ],
            }

        # 5. Scheduling / Scarcity / Parts / Technicians / Work Orders
        if any(k in lower for k in ["schedule", "repair", "service", "work order", "technician", "mechanic", "part", "parts", "spare", "stock", "scarcity", "defer", "acknowledge", "priority"]):
            res = fleet["resources"]
            parts_str = ", ".join(f"{k}: {v}" for k, v in res["parts_inventory"].items())
            return {
                "allowed": True,
                "warning": False,
                "topic": "operations_scheduling",
                "answer": (
                    f"**Constrained Maintenance & Work Orders (Segments 2 & 5):**\n"
                    f"• **Current Resources (Hour {step}):** **{res['technicians_available']}/{res['technicians_total']}** technicians free. Spare parts in stock: **{parts_str}**.\n"
                    f"• **How to Schedule:** In **Segment 2 (Live Fleet)**, click **Acknowledge** or **Schedule 4h Service** on any flagged machine. This reserves 1 technician and 1 matching spare part for 4 hours, preventing an 18-hour field breakdown.\n"
                    f"• **Scarcity Handling:** Test scarcity in **Segment 5** by setting a part stock to `0` — Agro-Twin transparently logs the work order as `DEFERRED_SCARCITY` instead of double-booking.\n"
                    f"• **Open Work Orders:** Currently **{fleet['open_work_orders_count']}** open ({len(fleet['work_orders'])} total logged)."
                ),
                "suggested_questions": [
                    "What needs attention right now?",
                    "How do I test live fault injection?",
                    "How much downtime does Agro-Twin save?",
                ],
            }

        # 6. Fault Injection / Reset / Timeline Controls
        if any(k in lower for k in ["inject", "injection", "reset", "slider", "checkpoint", "replay"]):
            return {
                "allowed": True,
                "warning": False,
                "topic": "simulation_controls",
                "answer": (
                    "**Interactive Simulation Controls:**\n"
                    "• **Timeline Replay (Segment 1):** Drag the Simulation Hour slider (`0–119`), nudge `-1 hr / +1 hr`, or click quick checkpoints (**Hr 35 · Alert**, **Hr 48 · Saved**, **Hr 55 · Multi**).\n"
                    "• **Live Fault Injection (Segment 5):** Choose any healthy machine (like **HV-206**), pick a fault mode (`fault_bearing`, `fault_engine`, or `fault_hydraulic`), and click **Inject Fault Now**, then step forward ~10 hours to watch Agro-Twin catch it early.\n"
                    "• **Reset Simulation:** Click **Reset** in Segment 1 to restore Hour 35, spare parts inventory, and work orders cleanly between demos."
                ),
                "suggested_questions": [
                    "What needs attention right now?",
                    "How do I use this website?",
                    "Tell me about HV-206",
                ],
            }

        # 7. Agriculture track, Affordability, Scalability, Team & Architecture
        if any(k in lower for k in ["agriculture", "agricultural", "farm", "farmer", "scalable", "scalability", "affordable", "affordability", "track", "team", "vansh", "kunal", "mohit", "shashi", "flask", "api", "architecture", "nexhack", "criteria"]):
            return {
                "allowed": True,
                "warning": False,
                "topic": "track_and_architecture",
                "answer": (
                    "**Agro-Twin — AI in Agriculture Track Alignment & Architecture:**\n"
                    "• **Practical Farm Impact:** Shared rural tractor/harvester fleets face short sowing and harvest windows where one 18-hour breakdown stalls multiple farms.\n"
                    "• **Affordability & Accessibility:** Runs on ordinary existing machine telemetry (temp, vibration, oil pressure, RPM) with zero specialized hardware and plain-English operator explanations.\n"
                    "• **Scalability:** Modular 4-layer Python architecture — **Vansh (`ml/`)** leak-free ML engine, **Kunal (`ops/`)** constrained scheduler, **Mohit (`backend/`)** unified twin state & REST API, and **Shashi (`web/` & `frontend/`)** Flask animated UI & AI guide — designed to scale cleanly from a 6-unit village co-op to district-wide fleets."
                ),
                "suggested_questions": [
                    "How do I use this website?",
                    "How much downtime does Agro-Twin save?",
                    "How does the ML model avoid data leakage?",
                ],
            }

        # 8. Default live fleet briefing ("What needs attention right now?", "Fleet status", etc.)
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
                "How do I schedule a repair?",
                "How much downtime does Agro-Twin save?",
            ],
        }
