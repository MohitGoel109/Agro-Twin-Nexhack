"""
Agro-Twin: Editorial Industrial Plotly Charts (De-Slopped UI)
Owner: Member 4 (Shashi) - Dashboard UI & Pitch Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Restrained palette: warm charcoal surfaces, quiet stone neutrals, one signature harvest-amber accent
BG_SURFACE = "#1b1a17"
GRID_LINE = "#2a2823"
TEXT_PRIMARY = "#f3efe6"
TEXT_MUTED = "#9c968a"
ACCENT_AMBER = "#e59a32"
ACCENT_BRICK = "#d9534f"
ACCENT_SAGE = "#5b9a6f"
ACCENT_SLATE = "#6e8898"
NEUTRAL_STONE = "#3f3d37"

BASELINES = {
    "engine_temp": ("Engine temp (C)", 82.0, ACCENT_AMBER),
    "vibration": ("Vibration (mm/s)", 2.0, "#d97736"),
    "oil_pressure": ("Oil pressure (PSI)", 45.0, ACCENT_SLATE),
    "rpm_variance": ("RPM variance (RPM)", 15.0, ACCENT_SAGE),
}

# Kept compatible with verify_frontend.py while using refined, non-neon colors
STATUS_COLORS = {
    "HEALTHY": "#4e7a5c",
    "SERVICED_READY": "#5b9a6f",
    "SERVICING": "#6e8898",
    "DATA_CHECK": "#6e8898",
    "EARLY_WARNING": "#e59a32",
    "CRITICAL_WARNING": "#d9534f",
    "BROKEN_DOWN": "#a83834",
}

STATUS_LABELS = {
    "HEALTHY": "Healthy",
    "SERVICED_READY": "Serviced & ready",
    "SERVICING": "In service",
    "DATA_CHECK": "Data hold",
    "EARLY_WARNING": "Early warning",
    "CRITICAL_WARNING": "Critical fault",
    "BROKEN_DOWN": "Broken down",
}

SENSOR_LABELS = {
    "CLEAN": "Clean feed",
    "SENSOR_NOISE_FILTERED": "Spike filtered",
    "MISSING_DATA_HOLD": "Missing telemetry",
}


def _apply_editorial_layout(fig: go.Figure, title: str, height: int = 340) -> go.Figure:
    fig.update_layout(
        title=dict(
            text=title,
            x=0.0,
            xanchor="left",
            font=dict(family="IBM Plex Sans, sans-serif", size=15, color=TEXT_PRIMARY),
        ),
        paper_bgcolor=BG_SURFACE,
        plot_bgcolor=BG_SURFACE,
        font=dict(family="IBM Plex Mono, monospace", size=11, color=TEXT_MUTED),
        height=height,
        margin=dict(l=48, r=24, t=52, b=40),
        xaxis=dict(
            showgrid=False,
            linecolor=GRID_LINE,
            tickfont=dict(color=TEXT_MUTED),
        ),
        yaxis=dict(
            gridcolor=GRID_LINE,
            zerolinecolor=GRID_LINE,
            tickfont=dict(color=TEXT_MUTED),
        ),
    )
    return fig


def build_risk_uncertainty_chart(machines: list) -> go.Figure:
    """
    Signature focal chart: quiet stone for healthy units, muted slate for data holds,
    and warm amber / brick red ONLY for confirmed developing faults.
    """
    labels = [m["machine_id"] for m in machines]
    risks = [round(m["fault_probability"] * 100.0, 1) for m in machines]
    uncertainties = [round(m["uncertainty"] * 100.0, 1) for m in machines]

    bar_colors = []
    for m in machines:
        st_code = m["status"]
        if st_code in ("CRITICAL_WARNING", "BROKEN_DOWN"):
            bar_colors.append(ACCENT_AMBER)  # One bright moment on confirmed urgent fault
        elif st_code == "EARLY_WARNING":
            bar_colors.append("#b87b28")
        elif st_code == "DATA_CHECK":
            bar_colors.append(ACCENT_SLATE)
        elif st_code in ("SERVICED_READY", "SERVICING"):
            bar_colors.append(ACCENT_SAGE)
        else:
            bar_colors.append(NEUTRAL_STONE)

    hover_texts = [
        (
            f"<b>{m['machine_id']} — {m['name']}</b><br>"
            f"State: {STATUS_LABELS.get(m['status'], m['status'])}<br>"
            f"Fault risk: {m['fault_probability']*100:.1f}% (±{m['uncertainty']*100:.1f}%)<br>"
            f"Confidence: {m['confidence']*100:.0f}%<br>"
            f"Feed: {SENSOR_LABELS.get(m['sensor_status'], m['sensor_status'])}<br>"
            f"Finding: {m['reasons'][0]}"
        )
        for m in machines
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=risks,
            width=0.52,
            error_y=dict(
                type="data",
                array=uncertainties,
                visible=True,
                color="#d6d0c4",
                thickness=1.6,
                width=5,
            ),
            marker=dict(color=bar_colors, line=dict(width=0)),
            hovertext=hover_texts,
            hoverinfo="text",
            text=[f"{r:.0f}%" for r in risks],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11, color=TEXT_PRIMARY),
        )
    )

    fig.add_hline(
        y=70,
        line_dash="dot",
        line_color=ACCENT_AMBER,
        line_width=1.2,
        annotation_text="Dispatch threshold (70%)",
        annotation_position="top right",
        annotation_font=dict(size=10, color=ACCENT_AMBER),
    )
    fig.add_hline(
        y=40,
        line_dash="dot",
        line_color="#5c5850",
        line_width=1,
        annotation_text="Early watch (40%)",
        annotation_position="top right",
        annotation_font=dict(size=10, color=TEXT_MUTED),
    )

    _apply_editorial_layout(
        fig,
        title="Fault risk by unit, with ensemble + missing-data uncertainty bands",
        height=340,
    )
    fig.update_yaxes(title_text="Risk (%)", range=[0, 118])
    return fig


def build_telemetry_chart(machine_id: str, history: list) -> go.Figure:
    """4-panel sensor history exposing real degradation, isolated spikes, and missing gaps."""
    steps = [h["step"] for h in history]

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[meta[0] for meta in BASELINES.values()],
        vertical_spacing=0.18,
        horizontal_spacing=0.10,
    )

    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    for (key, (label, base_val, color)), (r, c) in zip(BASELINES.items(), positions):
        values = [h[key] for h in history]
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=values,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=3.5),
                connectgaps=False,
            ),
            row=r,
            col=c,
        )
        fig.add_hline(
            y=base_val,
            line_dash="dot",
            line_color="#6b665c",
            line_width=1,
            row=r,
            col=c,
        )

    _apply_editorial_layout(
        fig,
        title=f"Raw hourly telemetry — {machine_id} (gaps = missing readings, dotted = healthy baseline)",
        height=460,
    )
    fig.update_layout(showlegend=False, margin=dict(l=48, r=24, t=60, b=40))
    fig.update_xaxes(showgrid=False, linecolor=GRID_LINE)
    fig.update_yaxes(gridcolor=GRID_LINE, zerolinecolor=GRID_LINE)
    fig.update_xaxes(title_text="Harvest hour", row=2, col=1)
    fig.update_xaxes(title_text="Harvest hour", row=2, col=2)
    return fig


def build_availability_comparison_chart(comparison: dict) -> go.Figure:
    """Side-by-side hourly availability curve: Calendar-only vs Agro-Twin."""
    series = comparison.get("hourly_series", [])
    steps = [p["step"] for p in series]
    cal = [p["calendar_availability_pct"] for p in series]
    ai = [p["ai_twin_availability_pct"] for p in series]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=cal,
            mode="lines",
            name="Calendar-only servicing",
            line=dict(color="#8c867a", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=ai,
            mode="lines",
            name="Agro-Twin (condition-based)",
            line=dict(color=ACCENT_AMBER, width=2.8),
            fill="tonexty",
            fillcolor="rgba(229, 154, 50, 0.12)",
        )
    )

    _apply_editorial_layout(
        fig,
        title="Fleet availability across 120 harvest hours (identical faults & parts)",
        height=360,
    )
    fig.update_xaxes(title_text="Harvest hour")
    fig.update_yaxes(title_text="Available (%)", range=[45, 105])
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="IBM Plex Sans, sans-serif", size=11, color=TEXT_PRIMARY),
        )
    )
    return fig


def build_downtime_bar_chart(comparison: dict) -> go.Figure:
    """Grouped bar chart comparing downtime hours, breakdowns, and warning lead time."""
    cal = comparison["calendar_only"]
    ai = comparison["ai_twin"]

    categories = ["Downtime (hrs)", "Unplanned breakdowns", "Warning lead (hrs)"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Calendar-only",
            x=categories,
            y=[
                cal["total_downtime_hours"],
                cal["unplanned_breakdowns"],
                cal["avg_warning_lead_time_hours"],
            ],
            marker_color="#524f47",
            text=[
                f"{cal['total_downtime_hours']}h",
                f"{cal['unplanned_breakdowns']}",
                f"{cal['avg_warning_lead_time_hours']}h",
            ],
            textposition="outside",
            textfont=dict(color=TEXT_MUTED),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Agro-Twin",
            x=categories,
            y=[
                ai["total_downtime_hours"],
                ai["unplanned_breakdowns"],
                ai["avg_warning_lead_time_hours"],
            ],
            marker_color=ACCENT_AMBER,
            text=[
                f"{ai['total_downtime_hours']}h",
                f"{ai['unplanned_breakdowns']}",
                f"{ai['avg_warning_lead_time_hours']}h",
            ],
            textposition="outside",
            textfont=dict(color=TEXT_PRIMARY),
        )
    )

    _apply_editorial_layout(
        fig,
        title="Measured outcome comparison",
        height=360,
    )
    fig.update_layout(
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="IBM Plex Sans, sans-serif", size=11, color=TEXT_PRIMARY),
        ),
    )
    return fig
