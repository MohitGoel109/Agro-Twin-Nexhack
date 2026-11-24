"""Operational controls for resource constraints and live fault scenarios."""

import streamlit as st

from frontend.dashboard_shared import get_client, get_current_step, render_page_intro

client = get_client()
step = get_current_step()
fleet = client.get_fleet(step=step)
resources = fleet["resources"]
parts = resources["parts_inventory"]
machine_ids = [machine["machine_id"] for machine in fleet["machines"]]

render_page_intro(
    "Operations & scenarios",
    "Manage technician and spare-part limits, or inject a controlled fault for a live demonstration.",
)

with st.container(border=True):
    st.subheader("Resource constraints")
    st.caption("Set the available crew and spare parts used by maintenance scheduling.")
    with st.form("resource_constraints_form"):
        technicians = st.number_input(
            "Technicians on shift",
            min_value=1,
            max_value=5,
            value=int(resources["technicians_total"]),
            step=1,
            key="operations_technicians",
        )
        pump_qty = st.number_input(
            "Coolant pumps",
            min_value=0,
            max_value=5,
            value=int(parts.get("Coolant Pump", 1)),
            key="operations_coolant_pumps",
        )
        valve_qty = st.number_input(
            "Hydraulic valves",
            min_value=0,
            max_value=5,
            value=int(parts.get("Hydraulic Valve", 1)),
            key="operations_hydraulic_valves",
        )
        bearing_qty = st.number_input(
            "Drive bearings",
            min_value=0,
            max_value=5,
            value=int(parts.get("Drive Bearing", 1)),
            key="operations_drive_bearings",
        )
        update_constraints = st.form_submit_button("Update constraints", type="primary")

    if update_constraints:
        client.update_constraints(
            technicians_total=int(technicians),
            parts_inventory={
                "Coolant Pump": int(pump_qty),
                "Hydraulic Valve": int(valve_qty),
                "Drive Bearing": int(bearing_qty),
            },
        )
        st.session_state.flash_msg = ("info", "Technician count and spare-parts inventory updated.")
        st.rerun()

with st.container(border=True):
    st.subheader("Live fault test")
    st.caption(f"Faults begin at the selected simulation hour (currently Hour {step}).")
    with st.form("fault_injection_form"):
        machine_id = st.selectbox(
            "Unit",
            machine_ids,
            index=len(machine_ids) - 1,
            key="operations_fault_machine",
        )
        fault_type = st.selectbox(
            "Fault mode",
            ["fault_bearing", "fault_engine", "fault_hydraulic"],
            key="operations_fault_type",
        )
        inject_fault = st.form_submit_button("Inject fault", type="primary")

    if inject_fault:
        result = client.inject_fault(
            machine_id=machine_id,
            start_step=step,
            fault_type=fault_type,
        )
        st.session_state.flash_msg = (
            "warning" if result.get("ok") else "error",
            result.get("message", "Fault injection failed."),
        )
        st.rerun()
