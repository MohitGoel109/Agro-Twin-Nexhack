"""Fleet status and alert intervention page."""

import pandas as pd
import streamlit as st

from frontend.charts import (
    SENSOR_LABELS,
    STATUS_COLORS,
    STATUS_LABELS,
    build_risk_uncertainty_chart,
)
from frontend.dashboard_shared import (
    apply_chart_theme,
    get_client,
    get_current_step,
    render_fleet_ledger,
    render_page_intro,
    unit_real_summary,
)

client = get_client()
step = get_current_step()
fleet = client.get_fleet(step=step)
machines = fleet["machines"]

render_page_intro(
    "Fleet overview",
    "Live risk, readiness, and intervention controls for the six field units.",
)
st.markdown(
    '<div class="hero-brand">Agro-Twin · PS 08</div>'
    '<h2 class="hero-title">Catch farm machinery faults before harvest stalls.</h2>'
    '<p class="hero-sub">Hourly telemetry, reliable alerts, and constrained maintenance '
    'planning across the active fleet.</p>',
    unsafe_allow_html=True,
)
render_fleet_ledger(fleet)

st.plotly_chart(
    apply_chart_theme(build_risk_uncertainty_chart(machines)),
    width="stretch",
)

st.markdown('<div class="section-heading">Active fleet status</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Each unit shows its operational state, uncertainty band, and next action.</div>',
    unsafe_allow_html=True,
)

columns = st.columns(2, gap="medium")
for index, machine in enumerate(machines):
    status = machine["status"]
    status_label = STATUS_LABELS.get(status, status)
    status_color = STATUS_COLORS.get(status, "#524f47")
    feed_label = SENSOR_LABELS.get(machine["sensor_status"], machine["sensor_status"])

    card_class = "unit-card"
    if status in ("CRITICAL_WARNING", "EARLY_WARNING", "BROKEN_DOWN"):
        card_class += " urgent"
    elif status in ("SERVICED_READY", "SERVICING"):
        card_class += " saved"
    elif status == "DATA_CHECK":
        card_class += " hold"

    real_line = unit_real_summary(machine, fleet["step"])
    reason_text = " · ".join(machine["reasons"])
    acknowledged = " · Acknowledged" if machine["acknowledged"] else ""

    with columns[index % 2]:
        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="unit-header">
                    <div>
                        <span class="unit-id">{machine['machine_id']}</span>
                        <span class="unit-name">{machine['name']}</span>
                    </div>
                    <span class="status-tag" style="background-color:{status_color};">{status_label}</span>
                </div>
                <div class="unit-headline">{real_line}</div>
                <div class="unit-telemetry">
                    Risk {machine['fault_probability']*100:.0f}% (±{machine['uncertainty']*100:.0f}%) &nbsp;|&nbsp;
                    Confidence {machine['confidence']*100:.0f}% &nbsp;|&nbsp;
                    {feed_label}{acknowledged}
                </div>
                <div class="unit-reason">{reason_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if status in ("CRITICAL_WARNING", "EARLY_WARNING"):
            if not machine["acknowledged"]:
                schedule_col, acknowledge_col = st.columns([2, 1])
                if schedule_col.button(
                    f"Schedule 4h service ({machine['part_needed']})",
                    key=f"sched_{machine['machine_id']}",
                    type="primary",
                    width="stretch",
                ):
                    result = client.schedule_maintenance(machine["machine_id"], step=fleet["step"])
                    st.session_state.flash_msg = (
                        "success" if result.get("ok") else "warning",
                        result.get("message", "Maintenance request completed."),
                    )
                    st.rerun()
                if acknowledge_col.button(
                    "Acknowledge",
                    key=f"ack_{machine['machine_id']}",
                    width="stretch",
                ):
                    result = client.acknowledge_alert(machine["machine_id"], step=fleet["step"])
                    st.session_state.flash_msg = ("info", result.get("message", "Alert acknowledged."))
                    st.rerun()
            elif st.button(
                f"Schedule 4h service ({machine['part_needed']})",
                key=f"sched_{machine['machine_id']}",
                type="primary",
                width="stretch",
            ):
                result = client.schedule_maintenance(machine["machine_id"], step=fleet["step"])
                st.session_state.flash_msg = (
                    "success" if result.get("ok") else "warning",
                    result.get("message", "Maintenance request completed."),
                )
                st.rerun()
        elif status == "DATA_CHECK" and not machine["acknowledged"]:
            if st.button(
                "Log sensor check",
                key=f"ack_{machine['machine_id']}",
                width="stretch",
            ):
                result = client.acknowledge_alert(
                    machine["machine_id"],
                    step=fleet["step"],
                    note="Logged telemetry inspection",
                )
                st.session_state.flash_msg = ("info", result.get("message", "Inspection logged."))
                st.rerun()

st.markdown('<div class="section-heading">Constrained priority queue</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Ranked by fault probability, model confidence, machine criticality, and parts availability.</div>',
    unsafe_allow_html=True,
)
if fleet["priority_queue"]:
    priority_queue = pd.DataFrame(fleet["priority_queue"])[
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
    priority_queue["Status"] = priority_queue["Status"].map(lambda value: STATUS_LABELS.get(value, value))
    st.dataframe(priority_queue, width="stretch", hide_index=True)
else:
    st.caption("No units require immediate maintenance at this hour.")
