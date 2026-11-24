"""Sensor replay and model explainability page."""

import streamlit as st

from frontend.charts import (
    SENSOR_LABELS,
    STATUS_LABELS,
    build_telemetry_chart,
)
from frontend.dashboard_shared import (
    apply_chart_theme,
    get_client,
    get_current_step,
    render_page_intro,
)

client = get_client()
step = get_current_step()
fleet = client.get_fleet(step=step)
health = client.get_health()
machines = fleet["machines"]

render_page_intro(
    "Telemetry & model",
    "Inspect sensor histories, see filtered anomalies, and understand each prediction.",
)

machine_ids = [machine["machine_id"] for machine in machines]
machine_names = {machine["machine_id"]: machine["name"] for machine in machines}
selected_machine = st.selectbox(
    "Select unit",
    machine_ids,
    format_func=lambda machine_id: (
        f"{machine_id} — {machine_names[machine_id]} "
        f"({STATUS_LABELS.get(next(m['status'] for m in machines if m['machine_id'] == machine_id))})"
    ),
    key="telemetry_selected_unit",
)
detail = client.get_machine_history(selected_machine, up_to_step=fleet["step"])

if detail.get("ok"):
    st.plotly_chart(
        apply_chart_theme(build_telemetry_chart(selected_machine, detail["history"])),
        width="stretch",
    )
    machine = detail["machine"]
    model_info = health["model_info"]
    explainability_col, model_col = st.columns(2, gap="large")
    with explainability_col:
        with st.container(border=True):
            st.subheader("Explainability readout")
            st.write(
                f"**State:** {STATUS_LABELS.get(machine['status'], machine['status'])}  |  "
                f"**Feed:** {SENSOR_LABELS.get(machine['sensor_status'], machine['sensor_status'])}"
            )
            st.write(
                f"**Risk:** {machine['fault_probability']*100:.1f}% "
                f"(±{machine['uncertainty']*100:.1f}%)  |  "
                f"**Confidence:** {machine['confidence']*100:.0f}%"
            )
            for reason in machine["reasons"]:
                st.write(f"- {reason}")
    with model_col:
        with st.container(border=True):
            st.subheader("Leak-free model rules")
            st.write(f"**Model:** {model_info['model_type']}")
            st.write(f"**Noise filter:** {model_info['noise_filter']}")
            st.write(f"**Leakage rule:** {model_info['leak_free_guarantee']}")
            st.write(f"**Uncertainty:** {model_info['uncertainty_method']}")
else:
    st.warning(detail.get("error", "Telemetry history is unavailable."))
