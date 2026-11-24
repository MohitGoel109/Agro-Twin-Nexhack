"""
Agro-Twin: Interactive Plotly Chart Builders
Owner: Member 4 (Shashi) - Dashboard UI & Pitch Lead
Problem Statement 08: Predictive Maintenance Twin for Farm Machinery
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASELINES = {
    "engine_temp": ("Engine Temp (C)", 82.0, "#ef4444"),
    "vibration": ("Vibration (mm/s)", 2.0, "#f59e0b"),
    "oil_pressure": ("Oil Pressure (PSI)", 45.0, "#3b82f6"),
    "rpm_variance": ("RPM Variance (RPM)", 15.0, "#a855f7"),
}

STATUS_COLORS = {
    "HEALTHY": "#22c55e",
    "SERVICED_READY": "#10b981",
    "SERVICING": "#06b6d4",
    "DATA_CHECK": "#3b82f6",
    "EARLY_WARNING": "#f59e0b",
    "CRITICAL_WARNING": "#ef4444",
    "BROKEN_DOWN": "#991b1b",
}


def build_risk_uncertainty_chart(machines: list) -> go.Figure:
    """Bar chart of fault probability with +/- uncertainty error bars across the fleet."""
    labels = [f"{m['machine_id']}" for m in machines]
    risks = [round(m["fault_probability"] * 100.0, 1) for m in machines]
    uncertainties = [round(m["uncertainty"] * 100.0, 1) for m in machines]
    colors = [STATUS_COLORS.get(m["status"], "#64748b") for m in machines]
    hover_texts = [
        (
            f"<b>{m['machine_id']} - {m['name']}</b><br>"
            f"Status: {m['status']}<br>"
            f"Risk: {m['fault_probability']*100:.1f}% (+/-{m['uncertainty']*100:.1f}%)<br>"
            f"Confidence: {m['confidence']*100:.0f}%<br>"
            f"Data Quality: {m['sensor_status']}<br>"
            f"Why: {m['reasons'][0]}"
        )
        for m in machines
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=risks,
            error_y=dict(type="data", array=uncertainties, visible=True, color="#e2e8f0", thickness=2),
            marker_color=colors,
            hovertext=hover_texts,
            hoverinfo="text",
            text=[f"{r:.0f}%" for r in risks],
            textposition="outside",
        )
    )
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Critical Threshold (70%)")
    fig.add_hline(y=40, line_dash="dot", line_color="#f59e0b", annotation_text="Early Warning (40%)")

    fig.update_layout(
        title="Live Fault Risk & Uncertainty Bands (+/- Std + Missing Penalty)",
        yaxis_title="Fault Risk (%)",
        yaxis_range=[0, 118],
        template="plotly_dark",
        height=360,
        margin=dict(l=40, r=20, t=55, b=40),
    )
    return fig


def build_telemetry_chart(machine_id: str, history: list) -> go.Figure:
    """4-panel sensor history plot showing raw spikes/dropouts against healthy baselines."""
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
                marker=dict(size=4),
                connectgaps=False,  # Visually exposes missing sensor dropouts!
            ),
            row=r,
            col=c,
        )
        fig.add_hline(
            y=base_val,
            line_dash="dot",
            line_color="#94a3b8",
            row=r,
            col=c,
        )

    fig.update_layout(
        title=f"Raw Sensor Telemetry Replay - {machine_id} (Gaps = Missing Data, Dotted = Healthy Baseline)",
        template="plotly_dark",
        height=470,
        showlegend=False,
        margin=dict(l=40, r=20, t=60, b=35),
    )
    fig.update_xaxes(title_text="Harvest Hour", row=2, col=1)
    fig.update_xaxes(title_text="Harvest Hour", row=2, col=2)
    return fig


def build_availability_comparison_chart(comparison: dict) -> go.Figure:
    """Hourly availability curve comparing Calendar-Only vs Agro-Twin AI."""
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
            name="Calendar-Only Servicing",
            line=dict(color="#f97316", width=2.5, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=ai,
            mode="lines",
            name="Agro-Twin AI (Condition-Based)",
            line=dict(color="#22c55e", width=3),
            fill="tonexty",
            fillcolor="rgba(34, 197, 94, 0.12)",
        )
    )

    fig.update_layout(
        title="Fleet Availability Over 120-Hour Harvest Window (Same Scenario & Constraints)",
        xaxis_title="Harvest Hour",
        yaxis_title="Fleet Available (%)",
        yaxis_range=[40, 105],
        template="plotly_dark",
        height=370,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def build_downtime_bar_chart(comparison: dict) -> go.Figure:
    """Grouped bar chart of Total Downtime Hours & Unplanned Breakdowns."""
    cal = comparison["calendar_only"]
    ai = comparison["ai_twin"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Calendar-Only",
            x=["Total Downtime (hrs)", "Unplanned Breakdowns", "Avg Warning Lead (hrs)"],
            y=[
                cal["total_downtime_hours"],
                cal["unplanned_breakdowns"],
                cal["avg_warning_lead_time_hours"],
            ],
            marker_color="#f97316",
            text=[
                f"{cal['total_downtime_hours']}h",
                f"{cal['unplanned_breakdowns']}",
                f"{cal['avg_warning_lead_time_hours']}h",
            ],
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Agro-Twin AI",
            x=["Total Downtime (hrs)", "Unplanned Breakdowns", "Avg Warning Lead (hrs)"],
            y=[
                ai["total_downtime_hours"],
                ai["unplanned_breakdowns"],
                ai["avg_warning_lead_time_hours"],
            ],
            marker_color="#22c55e",
            text=[
                f"{ai['total_downtime_hours']}h",
                f"{ai['unplanned_breakdowns']}",
                f"{ai['avg_warning_lead_time_hours']}h",
            ],
            textposition="outside",
        )
    )

    fig.update_layout(
        title="Measurable Harvest Impact: Calendar-Only vs Agro-Twin AI",
        barmode="group",
        template="plotly_dark",
        height=370,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig
