"""
Agro-Twin: Predictive Maintenance Digital Twin Dashboard.

Run from the repository root:
    python -m streamlit run frontend/dashboard.py
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import streamlit as st

from frontend.api_client import AgroTwinClient
from frontend.dashboard_shared import show_flash_message

st.set_page_config(
    page_title="Agro-Twin — Fleet Maintenance Twin",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

THEME_COLORS = {
    "dark": {
        "BG_CANVAS": "#131311",
        "BG_SURFACE": "#1b1a17",
        "BG_ELEVATED": "#22211d",
        "BG_SIDEBAR": "#161513",
        "BORDER_SUBTLE": "#2c2a25",
        "TEXT_PRIMARY": "#f3efe6",
        "TEXT_SECONDARY": "#a8a296",
        "TEXT_MUTED": "#787368",
        "ACCENT_AMBER": "#e59a32",
        "ACCENT_AMBER_HOVER": "#f0ab48",
        "BORDER_HOVER": "#4f4b42",
        "BG_HOVER": "#2a2924",
        "PRIMARY_BUTTON_TEXT": "#131311",
    },
    "light": {
        "BG_CANVAS": "#f5f3ee",
        "BG_SURFACE": "#ffffff",
        "BG_ELEVATED": "#ebe8e1",
        "BG_SIDEBAR": "#eae7df",
        "BORDER_SUBTLE": "#d7d2c8",
        "TEXT_PRIMARY": "#24221d",
        "TEXT_SECONDARY": "#5f5a50",
        "TEXT_MUTED": "#756e62",
        "ACCENT_AMBER": "#a86912",
        "ACCENT_AMBER_HOVER": "#8f5708",
        "BORDER_HOVER": "#b9b2a6",
        "BG_HOVER": "#dfdbd2",
        "PRIMARY_BUTTON_TEXT": "#ffffff",
    },
    "harvest": {
        "BG_CANVAS": "#f4ebdc",
        "BG_SURFACE": "#fffaf1",
        "BG_ELEVATED": "#eee1ca",
        "BG_SIDEBAR": "#e8dbc4",
        "BORDER_SUBTLE": "#d5c3a5",
        "TEXT_PRIMARY": "#30271c",
        "TEXT_SECONDARY": "#65533d",
        "TEXT_MUTED": "#7e6a51",
        "ACCENT_AMBER": "#a05b12",
        "ACCENT_AMBER_HOVER": "#81450b",
        "BORDER_HOVER": "#b79f7e",
        "BG_HOVER": "#e4d4b8",
        "PRIMARY_BUTTON_TEXT": "#fffaf1",
    },
    "forest": {
        "BG_CANVAS": "#101b15",
        "BG_SURFACE": "#18251c",
        "BG_ELEVATED": "#22352a",
        "BG_SIDEBAR": "#142018",
        "BORDER_SUBTLE": "#344b3b",
        "TEXT_PRIMARY": "#edf5ec",
        "TEXT_SECONDARY": "#bdcdbd",
        "TEXT_MUTED": "#8fa391",
        "ACCENT_AMBER": "#a7bd73",
        "ACCENT_AMBER_HOVER": "#c0d28f",
        "BORDER_HOVER": "#526e5a",
        "BG_HOVER": "#2b4032",
        "PRIMARY_BUTTON_TEXT": "#142018",
    },
    "ocean": {
        "BG_CANVAS": "#101923",
        "BG_SURFACE": "#182432",
        "BG_ELEVATED": "#223345",
        "BG_SIDEBAR": "#141f2b",
        "BORDER_SUBTLE": "#31465b",
        "TEXT_PRIMARY": "#edf4fa",
        "TEXT_SECONDARY": "#bccbd8",
        "TEXT_MUTED": "#8fa0b0",
        "ACCENT_AMBER": "#e2a04b",
        "ACCENT_AMBER_HOVER": "#f0b666",
        "BORDER_HOVER": "#4d667c",
        "BG_HOVER": "#2c4052",
        "PRIMARY_BUTTON_TEXT": "#1a2530",
    },
}

THEME_LABELS = {
    "dark": "Dark",
    "light": "Light",
    "harvest": "Harvest",
    "forest": "Forest",
    "ocean": "Ocean",
}

theme_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');

    :root {
        --bg-canvas: __BG_CANVAS__;
        --bg-surface: __BG_SURFACE__;
        --bg-elevated: __BG_ELEVATED__;
        --bg-sidebar: __BG_SIDEBAR__;
        --border-subtle: __BORDER_SUBTLE__;
        --text-primary: __TEXT_PRIMARY__;
        --text-secondary: __TEXT_SECONDARY__;
        --text-muted: __TEXT_MUTED__;
        --accent-amber: __ACCENT_AMBER__;
        --accent-amber-hover: __ACCENT_AMBER_HOVER__;
        --border-hover: __BORDER_HOVER__;
        --bg-hover: __BG_HOVER__;
        --primary-button-text: __PRIMARY_BUTTON_TEXT__;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-canvas) !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: var(--bg-canvas) !important;
        border-bottom: 1px solid var(--border-subtle);
    }

    .block-container {
        padding-top: 24px !important;
        padding-bottom: 48px !important;
        max-width: 1320px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 20px !important;
    }

    .hero-brand {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: var(--accent-amber);
        margin-bottom: 4px;
        letter-spacing: 0.01em;
    }
    .hero-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 30px;
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
    .ledger-cell:last-child {border-right: none;}
    .ledger-label {font-size: 12px; color: var(--text-muted); margin-bottom: 4px;}
    .ledger-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.2;
    }
    .ledger-value.accent {color: var(--accent-amber);}
    .ledger-note {font-size: 12px; color: var(--text-secondary); margin-top: 4px;}

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

    .unit-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .unit-card.urgent {border-color: #6b4c1e; border-left: 3px solid var(--accent-amber);}
    .unit-card.saved {border-left: 3px solid #5b9a6f;}
    .unit-card.hold {border-left: 3px solid #6e8898;}
    .unit-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 8px;
    }
    .unit-name {font-size: 16px; font-weight: 600; color: var(--text-primary);}
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
    .unit-headline {font-size: 14px; color: var(--text-primary); line-height: 1.45; margin-bottom: 12px;}
    .unit-telemetry {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: var(--text-secondary);
        padding: 8px 0;
        border-top: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 10px;
    }
    .unit-reason {font-size: 13px; color: var(--text-secondary); line-height: 1.45;}

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
    .stButton > button:hover {border-color: var(--border-hover) !important; background-color: var(--bg-hover) !important;}
    .stButton > button[kind="primary"] {
        background-color: var(--accent-amber) !important;
        border-color: var(--accent-amber) !important;
        color: var(--primary-button-text) !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--accent-amber-hover) !important;
        border-color: var(--accent-amber-hover) !important;
    }

    .sb-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 20px;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .sb-section {font-size: 13px; font-weight: 600; color: var(--text-primary); margin: 16px 0 8px 0;}
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
    .dot-live {display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #5b9a6f; margin-right: 6px;}
    .dot-local {display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--accent-amber); margin-right: 6px;}
    </style>
"""
for color_name, color_value in THEME_COLORS[st.session_state.theme_mode].items():
    theme_css = theme_css.replace(f"__{color_name}__", color_value)
st.markdown(theme_css, unsafe_allow_html=True)

if "client" not in st.session_state:
    st.session_state.client = AgroTwinClient()
if "current_step" not in st.session_state:
    st.session_state.current_step = 35
if "flash_msg" not in st.session_state:
    st.session_state.flash_msg = None

client: AgroTwinClient = st.session_state.client


def _set_step(value: int) -> None:
    st.session_state.current_step = max(0, min(119, int(value)))


def _shift_step(delta: int) -> None:
    _set_step(st.session_state.current_step + delta)


def _reset_demo() -> None:
    client.reset()
    st.session_state.current_step = 35
    st.session_state.flash_msg = (
        "success",
        "Simulation reset to Hour 35. Spare parts and work orders restored.",
    )


pages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_pages")
page = st.navigation(
    [
        st.Page(
            os.path.join(pages_dir, "fleet.py"),
            title="Fleet",
            icon=":material/dashboard:",
            help="Fleet readiness, live fault risk, alerts, and maintenance actions.",
        ),
        st.Page(
            os.path.join(pages_dir, "telemetry.py"),
            title="Telemetry",
            icon=":material/sensors:",
            help="Explore sensor histories, model explanations, and data-quality handling.",
        ),
        st.Page(
            os.path.join(pages_dir, "performance.py"),
            title="Performance",
            icon=":material/compare_arrows:",
            help="Compare calendar servicing with condition-based maintenance outcomes.",
        ),
        st.Page(
            os.path.join(pages_dir, "work_orders.py"),
            title="Work orders",
            icon=":material/assignment:",
            help="Review work-order status and the latest operational audit events.",
        ),
        st.Page(
            os.path.join(pages_dir, "operations.py"),
            title="Operations",
            icon=":material/tune:",
            help="Configure technician and parts limits or inject a controlled test fault.",
        ),
    ],
    position="top",
)

with st.sidebar:
    st.markdown('<div class="sb-title">Agro-Twin controls</div>', unsafe_allow_html=True)
    if client.mode == "FASTAPI_REST":
        st.markdown(
            '<div class="sb-conn"><span class="dot-live"></span>FastAPI connected</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sb-conn"><span class="dot-local"></span>Local twin fallback</div>',
            unsafe_allow_html=True,
        )

    with st.sidebar.popover(
        f"Theme: {THEME_LABELS[st.session_state.theme_mode]}",
        icon=":material/palette:",
    ):
        st.radio(
            "Choose a dashboard theme",
            options=list(THEME_COLORS),
            format_func=THEME_LABELS.get,
            key="theme_mode",
        )

    st.markdown('<div class="sb-section">Harvest timeline</div>', unsafe_allow_html=True)
    st.slider(
        "Simulation hour",
        min_value=0,
        max_value=119,
        key="current_step",
        label_visibility="collapsed",
    )
    previous_col, next_col = st.columns(2)
    previous_col.button("-1 hr", width="stretch", on_click=_shift_step, args=(-1,))
    next_col.button("+1 hr", width="stretch", on_click=_shift_step, args=(1,))

    st.caption("Scenario checkpoints")
    first_row = st.columns(2)
    first_row[0].button("Hr 35 · Alert", width="stretch", on_click=_set_step, args=(35,))
    first_row[1].button("Hr 48 · Saved", width="stretch", on_click=_set_step, args=(48,))
    second_row = st.columns(2)
    second_row[0].button("Hr 55 · Multi", width="stretch", on_click=_set_step, args=(55,))
    second_row[1].button("Hr 0 · Start", width="stretch", on_click=_set_step, args=(0,))

    st.divider()
    st.button("Reset simulation", width="stretch", on_click=_reset_demo)

show_flash_message()
page.run()
