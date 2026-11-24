"""Shared state and presentation helpers for the Streamlit dashboard pages."""

import streamlit as st
from plotly.graph_objects import Figure

from frontend.api_client import AgroTwinClient


def get_client() -> AgroTwinClient:
    return st.session_state.client


def get_current_step() -> int:
    return int(st.session_state.current_step)


def apply_chart_theme(figure: Figure) -> Figure:
    """Applies the selected dashboard theme to a Plotly figure."""
    theme_colors = {
        "light": {
            "paper": "#f5f3ee",
            "plot": "#ffffff",
            "text": "#5f5a50",
            "title": "#24221d",
            "grid": "#e5e1d8",
            "axis": "#b9b2a6",
        },
        "harvest": {
            "paper": "#f4ebdc",
            "plot": "#fffaf1",
            "text": "#65533d",
            "title": "#30271c",
            "grid": "#e3d5bd",
            "axis": "#baa786",
        },
        "forest": {
            "paper": "#101b15",
            "plot": "#18251c",
            "text": "#bdcdbd",
            "title": "#edf5ec",
            "grid": "#2a4032",
            "axis": "#405a48",
        },
        "ocean": {
            "paper": "#101923",
            "plot": "#182432",
            "text": "#bccbd8",
            "title": "#edf4fa",
            "grid": "#2b3d4d",
            "axis": "#42576a",
        },
    }
    colors = theme_colors.get(st.session_state.get("theme_mode", "dark"))
    if colors:
        figure.update_layout(
            paper_bgcolor=colors["paper"],
            plot_bgcolor=colors["plot"],
            font_color=colors["text"],
            title_font_color=colors["title"],
        )
        figure.update_xaxes(
            gridcolor=colors["grid"],
            linecolor=colors["axis"],
            tickfont_color=colors["text"],
        )
        figure.update_yaxes(
            gridcolor=colors["grid"],
            linecolor=colors["axis"],
            tickfont_color=colors["text"],
        )
        figure.update_annotations(font_color=colors["text"])
    return figure


def render_page_intro(title: str, description: str) -> None:
    st.title(title)
    st.caption(description)


def show_flash_message() -> None:
    message = st.session_state.get("flash_msg")
    if not message:
        return

    level, text = message
    st.session_state.flash_msg = None
    message_method = getattr(st, level, st.info)
    message_method(text)


def unit_real_summary(machine: dict, current_step: int) -> str:
    """Produces one concrete, honest operational sentence for each unit card."""
    status = machine["status"]
    breakdown_step = machine.get("actual_breakdown_step")

    if status == "SERVICED_READY":
        return "4-hour preventive repair completed early — 18-hour harvest breakdown prevented."
    if status == "SERVICING":
        return machine["recommended_action"]
    if status == "BROKEN_DOWN":
        return "Unplanned breakdown in field. Unit unavailable for 18 hours during harvest window."
    if machine["sensor_status"] == "SENSOR_NOISE_FILTERED":
        return "Isolated 1-hour sensor spike rejected by rolling median filter. No technician dispatched."
    if machine["sensor_status"] == "MISSING_DATA_HOLD":
        return "Telemetry dropout raised uncertainty band. Holding repair until clean sensor feed returns."
    if status in ("CRITICAL_WARNING", "EARLY_WARNING"):
        lead = (
            f"Breakdown in ~{max(1, breakdown_step - current_step)} hrs if unserviced. "
            if breakdown_step and breakdown_step > current_step
            else ""
        )
        stock = (
            f"{machine['part_in_stock']}x {machine['part_needed']} on shelf."
            if machine["part_in_stock"] > 0
            else f"{machine['part_needed']} out of stock."
        )
        return f"{lead}{stock}"
    return "Operating inside baseline tolerances across all four sensors."


def render_fleet_ledger(fleet: dict) -> None:
    resources = fleet["resources"]
    prevented_class = "accent" if fleet["breakdowns_prevented"] > 0 else ""
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
                <div class="ledger-value {prevented_class}">{fleet['breakdowns_prevented']}</div>
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
