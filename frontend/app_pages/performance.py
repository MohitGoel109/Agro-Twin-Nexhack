"""Calendar-versus-condition-based maintenance analysis page."""

import streamlit as st

from frontend.charts import (
    build_availability_comparison_chart,
    build_downtime_bar_chart,
)
from frontend.dashboard_shared import apply_chart_theme, get_client, render_page_intro

client = get_client()

render_page_intro(
    "Performance analysis",
    "Compare calendar-only servicing with the Agro-Twin strategy under the same fleet constraints.",
)

calendar_interval = st.slider(
    "Calendar servicing interval (hours)",
    min_value=24,
    max_value=96,
    value=72,
    step=12,
    key="calendar_servicing_interval",
)
comparison = client.compare_baseline(calendar_interval=calendar_interval)
calendar = comparison["calendar_only"]
ai_twin = comparison["ai_twin"]
improvement = comparison["improvement"]

st.markdown(
    f"""
    <div class="ledger-strip" style="grid-template-columns: repeat(4, 1fr);">
        <div class="ledger-cell">
            <div class="ledger-label">Fleet availability</div>
            <div class="ledger-value accent">{ai_twin['fleet_availability_pct']}%</div>
            <div class="ledger-note">+{improvement['availability_gain_pct']}% over calendar ({calendar['fleet_availability_pct']}%)</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Downtime saved</div>
            <div class="ledger-value">{improvement['downtime_hours_saved']} hrs</div>
            <div class="ledger-note">{ai_twin['total_downtime_hours']}h AI vs. {calendar['total_downtime_hours']}h calendar</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Unplanned breakdowns</div>
            <div class="ledger-value">{ai_twin['unplanned_breakdowns']}</div>
            <div class="ledger-note">{improvement['breakdowns_avoided']} avoided (vs. {calendar['unplanned_breakdowns']} calendar)</div>
        </div>
        <div class="ledger-cell">
            <div class="ledger-label">Avg. warning lead time</div>
            <div class="ledger-value">{ai_twin['avg_warning_lead_time_hours']} hrs</div>
            <div class="ledger-note">{ai_twin['noisy_or_missing_alerts_held']} noisy/missing alerts held</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

availability_col, downtime_col = st.columns(2, gap="medium")
with availability_col:
    st.plotly_chart(
        apply_chart_theme(build_availability_comparison_chart(comparison)),
        width="stretch",
    )
with downtime_col:
    st.plotly_chart(
        apply_chart_theme(build_downtime_bar_chart(comparison)),
        width="stretch",
    )
