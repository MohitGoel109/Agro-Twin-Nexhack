"""
Agro-Twin: Predictive Maintenance Digital Twin Dashboard (De-Slopped Editorial UI)
Owner: Member 4 (Shashi) - Dashboard UI & Pitch Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery (NexHack 2.0)

Run from repo root:
    python -m streamlit run frontend/dashboard.py
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pandas as pd
import streamlit as st

from frontend.api_client import AgroTwinClient
from frontend.charts import (
    SENSOR_LABELS,
    STATUS_COLORS,
    STATUS_LABELS,
    build_availability_comparison_chart,
    build_downtime_bar_chart,
    build_risk_uncertainty_chart,
    build_telemetry_chart,
)

st.set_page_config(
    page_title="Agro-Twin — Fleet Maintenance Twin",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Editorial dark UI: Newsreader + IBM Plex Sans + IBM Plex Mono, strict 4pt grid, sharp 6px/4px corners,
# zero purple gradients, zero glows, zero emoji clutter, one warm harvest-amber focal accent.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');

    :root {
        --bg-canvas: #131311;
        --bg-surface: #1b1a17;
        --bg-elevated: #22211d;
        --border-subtle: #2c2a25;
        --text-primary: #f3efe6;
        --text-secondary: #a8a296;
        --text-muted: #787368;
        --accent-amber: #e59a32;
        --accent-amber-hover: #f0ab48;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-canvas) !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
    }

    /* Hide default Streamlit chrome clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: var(--bg-canvas) !important;
        border-bottom: 1px solid var(--border-subtle);
    }

    /* Clean left-aligned spacing on a 4pt grid */
    .block-container {
        padding-top: 24px !important;
        padding-bottom: 48px !important;
        max-width: 1320px !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161513 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 20px !important;
    }

    /* Editorial serif headline — says what the tool actually does */
    .hero-brand {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: var(--accent-amber);
        margin-bottom: 4px;
        letter-spacing: 0.01em;
    }
    .hero-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 36px;
        font-weight: 500;
        line-height: 1.15;
        color: var(--text-primary);
        margin: 0 0 8px 0;
        text-align: left;
    }
    .hero-sub {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 15px;
        line-height: 1.5;
        color: var(--text-secondary);
        max-width: 720px;
        margin: 0 0 24px 0;
        text-align: left;
    }

    /* Structured operational ledger strip (replaces generic floating stat banner) */
    .ledger-strip {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        margin-bottom: 24px;
    }
    .ledger-cell {
        padding: 16px 20px;
        border-right: 1px solid var(--border-subtle);
    }
    .ledger-cell:last-child {
        border-right: none;
    }
    .ledger-label {
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 4px;
    }
    .ledger-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .ledger-value.accent {
        color: var(--accent-amber);
    }
    .ledger-note {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
    }

    /* Section headings */
    .section-heading {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 22px;
        font-weight: 500;
        color: var(--text-primary);
        margin: 24px 0 4px 0;
    }
    .section-sub {
        font-size: 13px;
        color: var(--text-secondary);
        margin: 0 0 16px 0;
    }

    /* Machine cards: crisp 6px corners, no icon boxes, concrete operational headline */
    .unit-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .unit-card.urgent {
        border-color: #6b4c1e;
        border-left: 3px solid var(--accent-amber);
    }
    .unit-card.saved {
        border-left: 3px solid #5b9a6f;
    }
    .unit-card.hold {
        border-left: 3px solid #6e8898;
    }
    .unit-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 8px;
    }
    .unit-name {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
    }
    .unit-id {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: var(--text-muted);
        margin-right: 8px;
    }
    .status-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
    }
    .unit-headline {
        font-size: 14px;
        color: var(--text-primary);
        line-height: 1.45;
        margin-bottom: 12px;
    }
    .unit-telemetry {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: var(--text-secondary);
        padding: 8px 0;
        border-top: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 10px;
    }
    .unit-reason {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.45;
    }

    /* Buttons: crisp 6px corners, one warm amber primary CTA, calm dark secondary buttons */
    .stButton > button {
        border-radius: 6px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 14px !important;
        border: 1px solid var(--border-subtle) !important;
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }
    .stButton > button:hover {
        border-color: #4f4b42 !important;
        background-color: #2a2924 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--accent-amber) !important;
        border-color: var(--accent-amber) !important;
        color: #131311 !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--accent-amber-hover) !important;
        border-color: var(--accent-amber-hover) !important;
    }

    /* Clean text-only tabs with amber underline */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        padding: 8px 0 12px 0 !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent-amber) !important;
    }

    /* Sidebar headings */
    .sb-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 20px;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .sb-section {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 16px 0 8px 0;
    }
    .sb-conn {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: var(--text-secondary);
        padding: 6px 10px;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .dot-live {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #5b9a6f;
        margin-right: 6px;
    }
    .dot-local {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent-amber);
        margin-right: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Session State & Synced Callbacks ----------------

if "client" not in st.session_state:
    st.session_state.client = AgroTwinClient()
if "current_step" not in st.session_state:
    st.session_state.current_step = 35
if "flash_msg" not in st.session_state:
    st.session_state.flash_msg = None

client: AgroTwinClient = st.session_state.client


def _set_step(val: int):
    st.session_state.current_step = max(0, min(119, int(val)))


def _shift_step(delta: int):
    st.session_state.current_step = max(0, min(119, int(st.session_state.current_step) + int(delta)))


def _reset_demo():
    st.session_state.client.reset()
    st.session_state.current_step = 35
    st.session_state.flash_msg = ("success", "Simulation reset to Hour 35. All spare parts and work orders restored.")


def _unit_real_summary(m: dict, current_step: int) -> str:
    """Produces one concrete, honest operational sentence for each unit card."""
    st_code = m["status"]
    b_step = m.get("actual_breakdown_step")

    if st_code == "SERVICED_READY":
        return "4-hour preventive repair completed early — 18-hour harvest breakdown prevented."
    if st_code == "SERVICING":
        return m["recommended_action"]
    if st_code == "BROKEN_DOWN":
        return "Unplanned breakdown in field. Unit unavailable for 18 hours during harvest window."
    if m["sensor_status"] == "SENSOR_NOISE_FILTERED":
        return "Isolated 1-hour sensor spike rejected by rolling median filter. No technician dispatched."
    if m["sensor_status"] == "MISSING_DATA_HOLD":
        return "Telemetry dropout raised uncertainty band. Holding repair until clean sensor feed returns."
    if st_code in ("CRITICAL_WARNING", "EARLY_WARNING"):
        lead_txt = f"Breakdown in ~{max(1, b_step - current_step)} hrs if unserviced. " if b_step and b_step > current_step else ""
        stock_txt = f"{m['part_in_stock']}x {m['part_needed']} on shelf." if m["part_in_stock"] > 0 else f"{m['part_needed']} out of stock."
        return f"{lead_txt}{stock_txt}"
    return "Operating inside baseline tolerances across all four sensors."


# ---------------- Sidebar: Clean Navigationless Controls ----------------

with st.sidebar:
    st.markdown('<div class="sb-title">Agro-Twin Controls</div>', unsafe_allow_html=True)
    if client.mode == "FASTAPI_REST":
        st.markdown('<div class="sb-conn"><span class="dot-live"></span>FastAPI connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sb-conn"><span class="dot-local"></span>Local twin fallback</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Harvest timeline</div>', unsafe_allow_html=True)
    st.slider(
        "Simulation hour",
        min_value=0,
        max_value=119,
        key="current_step",
        label_visibility="collapsed",
    )

    c_prev, c_next = st.columns(2)
    c_prev.button("-1 hr", use_container_width=True, on_click=_shift_step, args=(-1,))
    c_next.button("+1 hr", use_container_width=True, on_click=_shift_step, args=(1,))

    st.caption("Scenario checkpoints")
    j1, j2 = st.columns(2)
    j1.button("Hr 35 · Alert", use_container_width=True, on_click=_set_step, args=(35,))
    j2.button("Hr 48 · Saved", use_container_width=True, on_click=_set_step, args=(48,))

    j3, j4 = st.columns(2)
    j3.button("Hr 55 · Multi", use_container_width=True, on_click=_set_step, args=(55,))
    j4.button("Hr 0 · Start", use_container_width=True, on_click=_set_step, args=(0,))

    st.divider()
    st.markdown('<div class="sb-section">Resource constraints</div>', unsafe_allow_html=True)
    fleet_preview = client.get_fleet(step=st.session_state.current_step)
    res_now = fleet_preview["resources"]
    parts_now = res_now["parts_inventory"]

    tech_input = st.number_input("Technicians on shift", min_value=1, max_value=5, value=int(res_now["technicians_total"]), step=1)
    cp_qty = st.number_input("Coolant pumps", min_value=0, max_value=5, value=int(parts_now.get("Coolant Pump", 1)))
    hv_qty = st.number_input("Hydraulic valves", min_value=0, max_value=5, value=int(parts_now.get("Hydraulic Valve", 1)))
    db_qty = st.number_input("Drive bearings", min_value=0, max_value=5, value=int(parts_now.get("Drive Bearing", 1)))

    if st.button("Update constraints", use_container_width=True):
        client.update_constraints(
            technicians_total=int(tech_input),
            parts_inventory={
                "Coolant Pump": int(cp_qty),
                "Hydraulic Valve": int(hv_qty),
                "Drive Bearing": int(db_qty),
            },
        )
        st.session_state.flash_msg = ("info", "Updated technician count and spare-parts inventory.")
        st.rerun()

    st.divider()
    st.markdown('<div class="sb-section">Live fault test</div>', unsafe_allow_html=True)
    machine_ids = [m["machine_id"] for m in fleet_preview["machines"]]
    inj_machine = st.selectbox("Unit", machine_ids, index=len(machine_ids) - 1)
    inj_type = st.selectbox("Fault mode", ["fault_bearing", "fault_engine", "fault_hydraulic"])
    if st.button("Inject fault now", use_container_width=True):
        res = client.inject_fault(
            machine_id=inj_machine,
            start_step=st.session_state.current_step,
            fault_type=inj_type,
        )
        st.session_state.flash_msg = ("warning", res.get("message", "Fault injected."))
        st.rerun()

    st.divider()
    st.button("Reset simulation", use_container_width=True, on_click=_reset_demo)

# ---------------- Fetch Live State ----------------

fleet = client.get_fleet(step=st.session_state.current_step)
health = client.get_health()
machines = fleet["machines"]
resources = fleet["resources"]

# ---------------- Left-Aligned Editorial Hero (Says What It Actually Does) ----------------

st.markdown('<div class="hero-brand">Agro-Twin · PS 08</div>', unsafe_allow_html=True)
st.markdown(
    '<h1 class="hero-title">Catch farm machinery faults before harvest stalls.</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-sub">Replays hourly telemetry across six field units, filters isolated sensor spikes '
    'and missing readings, and schedules scarce mechanics and spare parts before breakdowns happen.</p>',
    unsafe_allow_html=True,
)

if st.session_state.flash_msg:
    level, text = st.session_state.flash_msg
    getattr(st, level, st.info)(text)
    st.session_state.flash_msg = None

# Clean 5-cell operational ledger strip (replaces floating stat banner)
prevented_cls = "accent" if fleet["breakdowns_prevented"] > 0 else ""
st.markdown(
    f"""
    <div class="ledger-strip">
        <div class="ledger-cell">
            <div class="ledger-label">Harvest hour</div>
            <div class="ledger-value">Hr {fleet['step']}</div>
            <div class="ledger-note">of 119-hour window</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Fleet readiness</div>
            <div class="ledger-value">{fleet['fleet_readiness_pct']}%</div>
            <div class="ledger-note">{fleet['machines_available']} of {fleet['machines_total']} units active</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Breakdowns prevented</div>
            <div class="ledger-value {prevented_cls}">{fleet['breakdowns_prevented']}</div>
            <div class="ledger-note">{fleet['total_downtime_hours']} hrs total downtime</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Open work orders</div>
            <div class="ledger-value">{fleet['open_work_orders_count']}</div>
            <div class="ledger-note">{len(fleet['priority_queue'])} units flagged</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Technicians free</div>
            <div class="ledger-value">{resources['technicians_available']} / {resources['technicians_total']}</div>
            <div class="ledger-note">{resources['technicians_busy']} assigned to bay</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Navigation Tabs (Zero Emojis) ----------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Fleet & interventions",
        "Telemetry & noise proof",
        "Calendar vs. Agro-Twin",
        "Work orders & log",
    ]
)

# ================ TAB 1: FLEET & INTERVENTIONS ================
with tab1:
    # One bright focal moment: fault risk with uncertainty bands
    st.plotly_chart(build_risk_uncertainty_chart(machines), use_container_width=True)

    st.markdown('<div class="section-heading">Active fleet status</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Each unit shows its real operational state, uncertainty band, and single next action.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(2, gap="medium")
    for idx, m in enumerate(machines):
        col = cols[idx % 2]
        st_code = m["status"]
        st_label = STATUS_LABELS.get(st_code, st_code)
        st_color = STATUS_COLORS.get(st_code, "#524f47")
        feed_label = SENSOR_LABELS.get(m["sensor_status"], m["sensor_status"])

        card_class = "unit-card"
        if st_code in ("CRITICAL_WARNING", "EARLY_WARNING", "BROKEN_DOWN"):
            card_class += " urgent"
        elif st_code in ("SERVICED_READY", "SERVICING"):
            card_class += " saved"
        elif st_code == "DATA_CHECK":
            card_class += " hold"

        real_line = _unit_real_summary(m, fleet["step"])
        reason_text = " · ".join(m["reasons"])
        ack_suffix = " · Acknowledged" if m["acknowledged"] else ""

        with col:
            st.markdown(
                f"""
                <div class="{card_class}">
                    <div class="unit-header">
                        <div>
                            <span class="unit-id">{m['machine_id']}</span>
                            <span class="unit-name">{m['name']}</span>
                        </div>
                        <span class="status-tag" style="background-color:{st_color};">{st_label}</span>
                    </div>
                    <div class="unit-headline">{real_line}</div>
                    <div class="unit-telemetry">
                        Risk {m['fault_probability']*100:.0f}% (±{m['uncertainty']*100:.0f}%) &nbsp;|&nbsp;
                        Confidence {m['confidence']*100:.0f}% &nbsp;|&nbsp;
                        {feed_label}{ack_suffix}
                    </div>
                    <div class="unit-reason">{reason_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # One primary button rule: only show actionable controls on units that actually need operator input
            if st_code in ("CRITICAL_WARNING", "EARLY_WARNING"):
                if not m["acknowledged"]:
                    b_main, b_sec = st.columns([2, 1])
                    if b_main.button(
                        f"Schedule 4h service ({m['part_needed']})",
                        key=f"sched_{m['machine_id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        res = client.schedule_maintenance(m["machine_id"], step=fleet["step"])
                        lvl = "success" if res.get("ok") else "warning"
                        st.session_state.flash_msg = (lvl, res.get("message", "Scheduled."))
                        st.rerun()
                    if b_sec.button(
                        "Acknowledge",
                        key=f"ack_{m['machine_id']}",
                        use_container_width=True,
                    ):
                        res = client.acknowledge_alert(m["machine_id"], step=fleet["step"])
                        st.session_state.flash_msg = ("info", res.get("message", "Acknowledged."))
                        st.rerun()
                else:
                    if st.button(
                        f"Schedule 4h service ({m['part_needed']})",
                        key=f"sched_{m['machine_id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        res = client.schedule_maintenance(m["machine_id"], step=fleet["step"])
                        lvl = "success" if res.get("ok") else "warning"
                        st.session_state.flash_msg = (lvl, res.get("message", "Scheduled."))
                        st.rerun()
            elif st_code == "DATA_CHECK" and not m["acknowledged"]:
                if st.button(
                    "Log sensor check",
                    key=f"ack_{m['machine_id']}",
                    use_container_width=True,
                ):
                    res = client.acknowledge_alert(m["machine_id"], step=fleet["step"], note="Logged telemetry inspection")
                    st.session_state.flash_msg = ("info", res.get("message", "Logged."))
                    st.rerun()

    st.markdown('<div class="section-heading">Constrained priority queue</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Ranked by fault probability, model confidence, machine criticality, and spare-part availability.</div>',
        unsafe_allow_html=True,
    )
    if fleet["priority_queue"]:
        pq_df = pd.DataFrame(fleet["priority_queue"])[
            [
                "machine_id",
                "name",
                "status",
                "priority_score",
                "fault_probability",
                "confidence",
                "part_needed",
                "part_in_stock",
                "recommended_action",
            ]
        ].rename(
            columns={
                "machine_id": "Unit",
                "name": "Machine",
                "status": "Status",
                "priority_score": "Priority",
                "fault_probability": "Risk",
                "confidence": "Confidence",
                "part_needed": "Part",
                "part_in_stock": "Stock",
                "recommended_action": "Next step",
            }
        )
        pq_df["Status"] = pq_df["Status"].map(lambda s: STATUS_LABELS.get(s, s))
        st.dataframe(pq_df, use_container_width=True, hide_index=True)
    else:
        st.caption("No units require immediate maintenance at this hour.")

# ================ TAB 2: TELEMETRY & NOISE PROOF ================
with tab2:
    st.markdown('<div class="section-heading">Sensor replay & leak-free verification</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Inspect TR-101 (real wear before Hour 46), SD-304 (1-hour spike filtered at Hour 35), or TR-105 (missing readings raising uncertainty).</div>',
        unsafe_allow_html=True,
    )

    selected_label = st.selectbox(
        "Select unit",
        [f"{m['machine_id']} — {m['name']} ({STATUS_LABELS.get(m['status'], m['status'])})" for m in machines],
    )
    sel_machine_id = selected_label.split(" — ")[0]
    detail = client.get_machine_history(sel_machine_id, up_to_step=fleet["step"])

    if detail.get("ok"):
        st.plotly_chart(
            build_telemetry_chart(sel_machine_id, detail["history"]),
            use_container_width=True,
        )
        m_info = detail["machine"]
        info = health["model_info"]
        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            st.markdown('<div class="section-heading" style="font-size:18px;">Explainability readout</div>', unsafe_allow_html=True)
            st.write(
                f"**State:** {STATUS_LABELS.get(m_info['status'], m_info['status'])}  |  "
                f"**Feed:** {SENSOR_LABELS.get(m_info['sensor_status'], m_info['sensor_status'])}"
            )
            st.write(
                f"**Risk:** {m_info['fault_probability']*100:.1f}% (±{m_info['uncertainty']*100:.1f}%)  |  "
                f"**Confidence:** {m_info['confidence']*100:.0f}%"
            )
            for r in m_info["reasons"]:
                st.write(f"- {r}")
        with c_right:
            st.markdown('<div class="section-heading" style="font-size:18px;">Leak-free model rules</div>', unsafe_allow_html=True)
            st.write(f"**Model:** {info['model_type']}")
            st.write(f"**Noise filter:** {info['noise_filter']}")
            st.write(f"**Leakage rule:** {info['leak_free_guarantee']}")
            st.write(f"**Uncertainty:** {info['uncertainty_method']}")

# ================ TAB 3: CALENDAR VS AGRO-TWIN ================
with tab3:
    st.markdown('<div class="section-heading">Calendar-only vs. Agro-Twin replay</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Replays the exact same 120-hour harvest failures under identical technician and spare-parts limits.</div>',
        unsafe_allow_html=True,
    )

    cal_int = st.slider(
        "Calendar servicing interval (hours)",
        min_value=24,
        max_value=96,
        value=72,
        step=12,
    )
    comp = client.compare_baseline(calendar_interval=cal_int)
    cal = comp["calendar_only"]
    ai = comp["ai_twin"]
    imp = comp["improvement"]

    st.markdown(
        f"""
        <div class="ledger-strip" style="grid-template-columns: repeat(4, 1fr);">
            <div class="ledger-cell">
                <div class="ledger-label">Fleet availability</div>
                <div class="ledger-value accent">{ai['fleet_availability_pct']}%</div>
                <div class="ledger-note">+{imp['availability_gain_pct']}% over calendar ({cal['fleet_availability_pct']}%)</div>
            </div>
            <div class="ledger-cell">
                <div class="ledger-label">Downtime saved</div>
                <div class="ledger-value">{imp['downtime_hours_saved']} hrs</div>
                <div class="ledger-note">{ai['total_downtime_hours']}h AI vs. {cal['total_downtime_hours']}h calendar</div>
            </div>
            <div class="ledger-cell">
                <div class="ledger-label">Unplanned breakdowns</div>
                <div class="ledger-value">{ai['unplanned_breakdowns']}</div>
                <div class="ledger-note">{imp['breakdowns_avoided']} avoided (vs. {cal['unplanned_breakdowns']} calendar)</div>
            </div>
            <div class="ledger-cell">
                <div class="ledger-label">Avg. warning lead time</div>
                <div class="ledger-value">{ai['avg_warning_lead_time_hours']} hrs</div>
                <div class="ledger-note">{ai['noisy_or_missing_alerts_held']} noisy/missing alerts held</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns(2, gap="medium")
    with g1:
        st.plotly_chart(build_availability_comparison_chart(comp), use_container_width=True)
    with g2:
        st.plotly_chart(build_downtime_bar_chart(comp), use_container_width=True)

# ================ TAB 4: WORK ORDERS & AUDIT LOG ================
with tab4:
    st.markdown('<div class="section-heading">Work orders</div>', unsafe_allow_html=True)
    wos = fleet["work_orders"]
    if wos:
        st.dataframe(pd.DataFrame(wos), use_container_width=True, hide_index=True)
    else:
        st.caption("No work orders scheduled yet. Schedule a 4-hour repair on TR-101 in the first tab to track its lifecycle here.")

    st.markdown('<div class="section-heading">Operational audit log</div>', unsafe_allow_html=True)
    events = fleet["recent_events"]
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
    else:
        st.caption("Acknowledgements, work-order dispatches, and constraint changes are recorded here.")
