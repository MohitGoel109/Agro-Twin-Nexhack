"""
Agro-Twin: Interactive Predictive Maintenance Digital Twin Dashboard
Owner: Member 4 (Shashi) - Dashboard UI & Pitch Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery (NexHack 2.0)

Run from repo root:
    streamlit run frontend/dashboard.py
"""

import os
import sys

# Ensure repo root is importable when launched via `streamlit run frontend/dashboard.py`
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pandas as pd
import streamlit as st

from frontend.api_client import AgroTwinClient
from frontend.charts import (
    STATUS_COLORS,
    build_availability_comparison_chart,
    build_downtime_bar_chart,
    build_risk_uncertainty_chart,
    build_telemetry_chart,
)

st.set_page_config(
    page_title="Agro-Twin | Predictive Maintenance Twin",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Subtle dark agricultural-tech polish
st.markdown(
    """
    <style>
    .machine-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #ffffff;
    }
    .reason-box {
        background-color: #1e293b;
        border-left: 3px solid #38bdf8;
        padding: 8px 10px;
        border-radius: 6px;
        font-size: 0.86rem;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Session State Initialization ----------------

if "client" not in st.session_state:
    st.session_state.client = AgroTwinClient()
if "current_step" not in st.session_state:
    st.session_state.current_step = 35  # Opens directly on the rich Hour-35 harvest scenario!
if "flash_msg" not in st.session_state:
    st.session_state.flash_msg = None

client: AgroTwinClient = st.session_state.client

# ---------------- Sidebar: Replay, Scarcity & Fault Injection ----------------

with st.sidebar:
    st.title("🚜 Agro-Twin Control")
    mode_badge = "🟢 FastAPI Connected" if client.mode == "FASTAPI_REST" else "🟡 Direct Twin Mode (Offline-Safe)"
    st.caption(f"Backend: **{mode_badge}**")
    if st.button("Reconnect FastAPI", use_container_width=True):
        client.refresh_connection()
        st.rerun()

    st.divider()
    st.subheader("⏱️ Harvest Timeline Replay")

    step = st.slider(
        "Simulation Hour (0 - 119)",
        min_value=0,
        max_value=119,
        value=st.session_state.current_step,
        key="step_slider",
    )
    if step != st.session_state.current_step:
        st.session_state.current_step = step

    c_prev, c_next = st.columns(2)
    if c_prev.button("◀ -1 hr", use_container_width=True):
        st.session_state.current_step = max(0, st.session_state.current_step - 1)
        st.rerun()
    if c_next.button("+1 hr ▶", use_container_width=True):
        st.session_state.current_step = min(119, st.session_state.current_step + 1)
        st.rerun()

    st.caption("Quick Judge Demo Jump Points:")
    j1, j2 = st.columns(2)
    if j1.button("Hr 35: Fault+Noise", use_container_width=True):
        st.session_state.current_step = 35
        st.rerun()
    if j2.button("Hr 48: Saved!", use_container_width=True):
        st.session_state.current_step = 48
        st.rerun()

    j3, j4 = st.columns(2)
    if j3.button("Hr 55: Multi-Risk", use_container_width=True):
        st.session_state.current_step = 55
        st.rerun()
    if j4.button("Hr 0: Start", use_container_width=True):
        st.session_state.current_step = 0
        st.rerun()

    st.divider()
    st.subheader("🔧 Resource Scarcity Controls")
    fleet_preview = client.get_fleet(step=st.session_state.current_step)
    res_now = fleet_preview["resources"]
    parts_now = res_now["parts_inventory"]

    tech_input = st.number_input(
        "Technicians Available",
        min_value=1,
        max_value=5,
        value=int(res_now["technicians_total"]),
        step=1,
    )
    cp_qty = st.number_input("Coolant Pump Stock", min_value=0, max_value=5, value=int(parts_now.get("Coolant Pump", 1)))
    hv_qty = st.number_input("Hydraulic Valve Stock", min_value=0, max_value=5, value=int(parts_now.get("Hydraulic Valve", 1)))
    db_qty = st.number_input("Drive Bearing Stock", min_value=0, max_value=5, value=int(parts_now.get("Drive Bearing", 1)))

    if st.button("Apply Scarcity Constraints", use_container_width=True):
        client.update_constraints(
            technicians_total=int(tech_input),
            parts_inventory={
                "Coolant Pump": int(cp_qty),
                "Hydraulic Valve": int(hv_qty),
                "Drive Bearing": int(db_qty),
            },
        )
        st.session_state.flash_msg = ("info", "Updated technician and spare-parts scarcity constraints.")
        st.rerun()

    st.divider()
    st.subheader("⚡ Live Fault Injection")
    machine_ids = [m["machine_id"] for m in fleet_preview["machines"]]
    inj_machine = st.selectbox("Target Machine", machine_ids, index=len(machine_ids) - 1)
    inj_type = st.selectbox("Fault Type", ["fault_bearing", "fault_engine", "fault_hydraulic"])
    if st.button("Inject Fault at Current Hour", use_container_width=True):
        res = client.inject_fault(
            machine_id=inj_machine,
            start_step=st.session_state.current_step,
            fault_type=inj_type,
        )
        st.session_state.flash_msg = ("warning", res.get("message", "Fault injected."))
        st.rerun()

    st.divider()
    if st.button("🔄 Reset Entire Demo", type="primary", use_container_width=True):
        client.reset()
        st.session_state.current_step = 35
        st.session_state.flash_msg = ("success", "Demo reset cleanly! Ready for next pitch.")
        st.rerun()

# ---------------- Fetch Live Unified Twin State ----------------

fleet = client.get_fleet(step=st.session_state.current_step)
health = client.get_health()
machines = fleet["machines"]
resources = fleet["resources"]

# ---------------- Header & KPI Command Bar ----------------

st.title("🌾 Agro-Twin: Predictive Maintenance Twin for Farm Machinery")
st.caption(
    "Leak-free fault forecasting • Sensor noise & missing-data filtering • "
    "Constrained technician/parts scheduling • Fair Calendar-Only comparison (PS 08)"
)

if st.session_state.flash_msg:
    level, text = st.session_state.flash_msg
    getattr(st, level, st.info)(text)
    st.session_state.flash_msg = None

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Harvest Hour", f"Hr {fleet['step']} / 119")
k2.metric("Fleet Readiness", f"{fleet['fleet_readiness_pct']}%", f"{fleet['machines_available']}/{fleet['machines_total']} Active")
k3.metric("Downtime So Far", f"{fleet['total_downtime_hours']} hrs")
k4.metric("Breakdowns Prevented", f"{fleet['breakdowns_prevented']}")
k5.metric("Open Work Orders", f"{fleet['open_work_orders_count']}")
k6.metric(
    "Free Technicians",
    f"{resources['technicians_available']} / {resources['technicians_total']}",
)

# ---------------- Main Navigation Tabs ----------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🚜 Live Fleet & Interventions",
        "📈 Telemetry & Noise Proof",
        "⚖️ Calendar-Only vs AI Twin",
        "📋 Work Orders & Audit Log",
    ]
)

# ================ TAB 1: LIVE FLEET & INTERVENTIONS ================
with tab1:
    st.plotly_chart(build_risk_uncertainty_chart(machines), use_container_width=True)

    st.subheader("Live Fleet Health Cards & Operator Controls")
    cols = st.columns(2)

    for idx, m in enumerate(machines):
        col = cols[idx % 2]
        badge_color = STATUS_COLORS.get(m["status"], "#475569")
        reasons_html = "<br>".join(f"• {r}" for r in m["reasons"])
        ack_tag = " ✅ Acknowledged" if m["acknowledged"] else ""

        with col:
            st.markdown(
                f"""
                <div class="machine-card" style="border-left: 5px solid {badge_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="font-size:1.05rem;">{m['machine_id']} — {m['name']}</strong>
                        <span class="status-pill" style="background:{badge_color};">{m['status']}</span>
                    </div>
                    <div style="margin-top:6px; font-size:0.9rem; color:#cbd5e1;">
                        Risk: <b>{m['fault_probability']*100:.1f}%</b> (±{m['uncertainty']*100:.1f}%) &nbsp;|&nbsp;
                        Confidence: <b>{m['confidence']*100:.0f}%</b> &nbsp;|&nbsp;
                        Data: <b>{m['sensor_status']}</b>{ack_tag}
                    </div>
                    <div style="margin-top:4px; font-size:0.86rem; color:#94a3b8;">
                        Priority Score: <b>{m['priority_score']}</b> &nbsp;|&nbsp;
                        Part: <b>{m['part_needed']}</b> (Stock: {m['part_in_stock']}) &nbsp;|&nbsp;
                        State: <b>{m['availability_state']}</b>
                    </div>
                    <div class="reason-box">
                        <b>Why Flagged:</b><br>{reasons_html}<br>
                        <b>Recommended Action:</b> {m['recommended_action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            b1, b2 = st.columns(2)
            ack_disabled = m["acknowledged"] or m["status"] in ("HEALTHY", "SERVICED_READY", "SERVICING")
            sched_disabled = m["status"] in ("SERVICED_READY", "SERVICING")

            if b1.button(
                "Acknowledge Alert",
                key=f"ack_{m['machine_id']}",
                disabled=ack_disabled,
                use_container_width=True,
            ):
                res = client.acknowledge_alert(m["machine_id"], step=fleet["step"])
                st.session_state.flash_msg = ("info", res.get("message", "Acknowledged."))
                st.rerun()

            if b2.button(
                "Schedule 4h Service",
                key=f"sched_{m['machine_id']}",
                disabled=sched_disabled,
                type="primary" if m["status"] in ("CRITICAL_WARNING", "EARLY_WARNING") else "secondary",
                use_container_width=True,
            ):
                res = client.schedule_maintenance(m["machine_id"], step=fleet["step"])
                lvl = "success" if res.get("ok") else "warning"
                st.session_state.flash_msg = (lvl, res.get("message", "Scheduled."))
                st.rerun()

    st.divider()
    st.subheader("Constrained Maintenance Priority Queue")
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
                "acknowledged",
                "recommended_action",
            ]
        ]
        st.dataframe(pq_df, use_container_width=True, hide_index=True)
    else:
        st.success("No urgent maintenance interventions required at this hour.")

# ================ TAB 2: TELEMETRY & NOISE/UNCERTAINTY PROOF ================
with tab2:
    st.subheader("Sensor Telemetry Replay — Noise vs. Missing Data vs. Real Degradation")
    st.info(
        "Tip for Judges: Select **TR-101** (real engine fault before Hour 46), "
        "**SD-304** (single-hour spike filtered as noise at Hour 35), or "
        "**TR-105** (missing sensor dropout raising uncertainty at Hour 35)."
    )

    selected_id = st.selectbox(
        "Inspect Machine Telemetry",
        [f"{m['machine_id']} - {m['name']} ({m['status']})" for m in machines],
    )
    sel_machine_id = selected_id.split(" - ")[0]
    detail = client.get_machine_history(sel_machine_id, up_to_step=fleet["step"])

    if detail.get("ok"):
        st.plotly_chart(
            build_telemetry_chart(sel_machine_id, detail["history"]),
            use_container_width=True,
        )
        m_info = detail["machine"]
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### Current Explainability Summary")
            st.write(f"**Status:** `{m_info['status']}` | **Data Quality:** `{m_info['sensor_status']}`")
            st.write(
                f"**Fault Probability:** `{m_info['fault_probability']*100:.1f}%` "
                f"(±`{m_info['uncertainty']*100:.1f}%` uncertainty | `{m_info['confidence']*100:.0f}%` confidence)"
            )
            for r in m_info["reasons"]:
                st.write(f"- {r}")
        with c_right:
            st.markdown("#### Leak-Free Model Guarantee (Member 1)")
            info = health["model_info"]
            st.write(f"**Model:** {info['model_type']}")
            st.write(f"**Noise Filter:** {info['noise_filter']}")
            st.write(f"**Leak-Free Rule:** {info['leak_free_guarantee']}")
            st.write(f"**Uncertainty Method:** {info['uncertainty_method']}")

# ================ TAB 3: FAIR BASELINE COMPARISON ================
with tab3:
    st.subheader("Fair Replay Comparison: Calendar-Only Servicing vs. Agro-Twin AI")
    cal_int = st.slider(
        "Calendar-Only Servicing Interval (Hours)",
        min_value=24,
        max_value=96,
        value=72,
        step=12,
        help="Adjust the fixed calendar schedule to test fairness under identical fault scenarios.",
    )
    comp = client.compare_baseline(calendar_interval=cal_int)
    cal = comp["calendar_only"]
    ai = comp["ai_twin"]
    imp = comp["improvement"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "AI Fleet Availability",
        f"{ai['fleet_availability_pct']}%",
        f"+{imp['availability_gain_pct']}% vs Calendar ({cal['fleet_availability_pct']}%)",
    )
    m2.metric(
        "Downtime Hours Saved",
        f"{imp['downtime_hours_saved']} hrs",
        f"{ai['total_downtime_hours']}h AI vs {cal['total_downtime_hours']}h Cal",
    )
    m3.metric(
        "Breakdowns Avoided",
        f"{imp['breakdowns_avoided']}",
        f"{ai['unplanned_breakdowns']} AI vs {cal['unplanned_breakdowns']} Cal",
    )
    m4.metric(
        "Avg Warning Lead Time",
        f"{ai['avg_warning_lead_time_hours']} hrs",
        f"{ai['noisy_or_missing_alerts_held']} noisy/missing holds",
    )

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(build_availability_comparison_chart(comp), use_container_width=True)
    with g2:
        st.plotly_chart(build_downtime_bar_chart(comp), use_container_width=True)

# ================ TAB 4: WORK ORDERS & AUDIT LOG ================
with tab4:
    st.subheader("Maintenance Work Orders")
    wos = fleet["work_orders"]
    if wos:
        st.dataframe(pd.DataFrame(wos), use_container_width=True, hide_index=True)
    else:
        st.info("No work orders created yet. Go to Tab 1 and click 'Schedule 4h Service' on TR-101 to see live intervention tracking!")

    st.subheader("Chronological Operational Event Log")
    events = fleet["recent_events"]
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
    else:
        st.caption("Operator acknowledgements, scheduled work orders, and constraint changes appear here in real time.")
