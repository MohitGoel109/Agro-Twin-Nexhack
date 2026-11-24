"""Work-order lifecycle and operational audit page."""

import pandas as pd
import streamlit as st

from frontend.dashboard_shared import get_client, get_current_step, render_page_intro

client = get_client()
fleet = client.get_fleet(step=get_current_step())

render_page_intro(
    "Work orders & activity",
    "Track maintenance lifecycle status and review recent operational events.",
)

st.markdown('<div class="section-heading">Work orders</div>', unsafe_allow_html=True)
if fleet["work_orders"]:
    st.dataframe(pd.DataFrame(fleet["work_orders"]), width="stretch", hide_index=True)
else:
    st.caption("No work orders are scheduled. Use the Fleet page to schedule a 4-hour service.")

st.markdown('<div class="section-heading">Operational audit log</div>', unsafe_allow_html=True)
if fleet["recent_events"]:
    st.dataframe(pd.DataFrame(fleet["recent_events"]), width="stretch", hide_index=True)
else:
    st.caption("Acknowledgements, work-order dispatches, and constraint changes will appear here.")
