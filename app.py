import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import json

from db import get_session, engine, Base
from models import User, Dataset, AnalysisHistory
from analyzer import analyze_csv, display_column_types, detect_column_types
from cleaner import clean_data
from notebook_generator import generate_ml_notebook, suggest_ml_task
from notebook_runner import execute_notebook, get_execution_summary, convert_notebook_to_python, convert_notebook_to_html
from report_generator import generate_model_card_pdf, generate_html_report
from components.auth import render_auth_sidebar
from components.notifications import (
    send_welcome_email, 
    send_analysis_complete_email, 
    send_ml_notebook_ready_email,
    can_send_notification,
    mark_notification_sent
)

def inject_pro_theme_css():
    """Inject comprehensive theme CSS with light/dark mode support."""

    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

    theme = st.session_state.theme

    # Define colors based on theme
    if theme == 'dark':
        bg_primary = "#0F172A"
        bg_secondary = "#1E293B"
        bg_card = "#1E293B"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        border_color = "#334155"
        shadow = "0 1px 3px rgba(0,0,0,0.3)"
        shadow_lg = "0 10px 25px rgba(0,0,0,0.3)"
    else:
        bg_primary = "#F8FAFC"
        bg_secondary = "#F1F5F9"
        bg_card = "#FFFFFF"
        text_primary = "#0F172A"
        text_secondary = "#64748B"
        text_muted = "#94A3B8"
        border_color = "#E2E8F0"
        shadow = "0 1px 3px rgba(0,0,0,0.08)"
        shadow_lg = "0 10px 25px rgba(0,0,0,0.1)"

    st.markdown(
        f"""
        <style>
        /* Import Inter font and Material Icons */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');

        /* CSS Variables - Using actual values for better compatibility */
        :root {{
            --primary: #0D9488;
            --primary-light: #14B8A6;
            --primary-dark: #0F766E;
            --primary-50: rgba(13, 148, 136, 0.1);
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            --info: #3B82F6;
            --bg-primary: {bg_primary};
            --bg-secondary: {bg_secondary};
            --bg-card: {bg_card};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --text-muted: {text_muted};
            --border-color: {border_color};
            --shadow: {shadow};
            --shadow-lg: {shadow_lg};
        }}

        /* Global font - apply to the root and let it inherit */
        html, body, .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }}

        /* Text elements inherit from body */
        p, h1, h2, h3, h4, h5, h6, label, input, textarea, a,
        .stMarkdown, .stText, [data-testid="stMarkdownContainer"] p {{
            font-family: inherit !important;
        }}

        /* Ensure Material Icons render correctly */
        .material-icons,
        .material-icons-outlined {{
            font-family: 'Material Icons Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 24px !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
        }}

        /* Preserve Streamlit's icon fonts - critical fix for icon rendering */
        [data-baseweb] *,
        [data-testid] svg,
        [role="listbox"],
        [role="option"],
        button svg,
        summary svg {{
            font-family: inherit !important;
        }}

        /* Fix expander toggle icon - hide text, show only SVG */
        [data-testid="stExpander"] summary {{
            display: flex !important;
            align-items: center !important;
        }}

        /* Hide text in icon-only containers, show only SVG */
        [data-testid="stExpanderToggleIcon"] {{
            overflow: hidden !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 24px !important;
            height: 24px !important;
        }}

        /* Ensure SVG icons are visible and properly sized */
        [data-testid="stExpanderToggleIcon"] svg {{
            color: {text_primary} !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            min-height: 18px !important;
            display: block !important;
        }}

        /* Fix selectbox/dropdown icons */
        [data-baseweb="select"] [data-baseweb="icon"] svg {{
            width: 18px !important;
            height: 18px !important;
        }}

        /* Fix header link icons (the chain link icon next to headers) */
        [data-testid="StyledLinkIconContainer"] {{
            color: transparent !important;
            font-size: 0 !important;
            text-indent: -9999px !important;
            display: inline-flex !important;
            align-items: center !important;
            width: 20px !important;
            height: 20px !important;
            overflow: hidden !important;
        }}

        [data-testid="StyledLinkIconContainer"] svg {{
            color: {text_secondary} !important;
            font-size: initial !important;
            text-indent: 0 !important;
            width: 16px !important;
            height: 16px !important;
            display: block !important;
        }}

        /* Hide broken image placeholders in sidebar */
        [data-testid="stSidebar"] img[src=""] {{
            display: none !important;
        }}

        /* Fix dataframe/table toolbar icon buttons */
        [data-testid="stDataFrame"] [data-testid="stBaseButton-icon"],
        [data-testid="stDataFrameResizable"] [data-testid="stBaseButton-icon"] {{
            color: transparent !important;
            font-size: 0 !important;
            text-indent: -9999px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: hidden !important;
        }}

        [data-testid="stDataFrame"] [data-testid="stBaseButton-icon"] svg,
        [data-testid="stDataFrameResizable"] [data-testid="stBaseButton-icon"] svg {{
            color: {text_primary} !important;
            font-size: initial !important;
            text-indent: 0 !important;
            width: 16px !important;
            height: 16px !important;
            display: block !important;
        }}

        /* Fix icon-only buttons throughout the app */
        [data-testid="stBaseButton-icon"],
        [data-testid="stBaseButton-elementToolbar"] {{
            color: transparent !important;
            font-size: 0 !important;
            text-indent: -9999px !important;
            overflow: hidden !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        [data-testid="stBaseButton-icon"] svg,
        [data-testid="stBaseButton-elementToolbar"] svg {{
            color: {text_primary} !important;
            font-size: initial !important;
            text-indent: 0 !important;
            width: 18px !important;
            height: 18px !important;
            display: block !important;
        }}

        /* Fix glide data grid icon buttons (used in dataframes) */
        .dvn-scroller button svg,
        .gdg-button svg {{
            color: {text_primary} !important;
            width: 16px !important;
            height: 16px !important;
        }}

        /* Main app background */
        .stApp {{
            background-color: {bg_primary} !important;
        }}

        /* Main container */
        .block-container {{
            max-width: 1200px;
            padding: 2rem 1rem 4rem 1rem;
        }}

        /* All text elements */
        p, span, label, div {{
            color: {text_primary};
        }}

        /* Headers */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            font-weight: 700 !important;
            color: {text_primary} !important;
            letter-spacing: -0.025em;
        }}

        h1 {{ font-size: 2rem !important; }}
        h2 {{ font-size: 1.5rem !important; }}
        h3 {{ font-size: 1.25rem !important; }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {bg_card} !important;
            border-right: 1px solid {border_color} !important;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem;
        }}

        [data-testid="stSidebarHeader"] {{
            padding: 1rem 1rem 0 1rem;
        }}

        /* Sidebar text */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {{
            color: {text_primary} !important;
        }}

        /* Buttons - Modern pill style */
        .stButton > button {{
            border-radius: 10px !important;
            padding: 0.625rem 1.25rem !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            border: 1.5px solid #0D9488 !important;
            background-color: transparent !important;
            color: #0D9488 !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: none !important;
            min-height: 42px !important;
        }}

        .stButton > button:hover {{
            background-color: #0D9488 !important;
            color: white !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3) !important;
        }}

        .stButton > button:active {{
            transform: translateY(0) !important;
        }}

        /* Primary buttons */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%) !important;
            color: white !important;
            border: none !important;
        }}

        .stButton > button[kind="primary"]:hover,
        .stButton > button[data-testid="baseButton-primary"]:hover {{
            background: linear-gradient(135deg, #0F766E 0%, #0D9488 100%) !important;
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.4) !important;
        }}

        /* Download buttons */
        .stDownloadButton > button {{
            border-radius: 10px !important;
            padding: 0.625rem 1.25rem !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%) !important;
            color: white !important;
            border: none !important;
            transition: all 0.2s ease !important;
        }}

        .stDownloadButton > button:hover {{
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.4) !important;
            transform: translateY(-1px) !important;
        }}

        /* Expanders / Cards */
        .stExpander, [data-testid="stExpander"] {{
            background-color: {bg_card} !important;
            border: 1px solid {border_color} !important;
            border-radius: 16px !important;
            box-shadow: {shadow} !important;
            overflow: hidden;
            margin-bottom: 1rem;
        }}

        .streamlit-expanderHeader {{
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            color: {text_primary} !important;
            padding: 1rem 1.25rem !important;
        }}

        .streamlit-expanderContent {{
            padding: 0 1.25rem 1.25rem 1.25rem !important;
        }}

        /* Metrics */
        [data-testid="metric-container"] {{
            background-color: {bg_card} !important;
            border: 1px solid {border_color} !important;
            border-radius: 16px !important;
            padding: 1.25rem !important;
            box-shadow: {shadow} !important;
        }}

        [data-testid="stMetricValue"] {{
            font-weight: 800 !important;
            font-size: 1.75rem !important;
            color: #0D9488 !important;
        }}

        [data-testid="stMetricLabel"] {{
            font-weight: 600 !important;
            text-transform: uppercase !important;
            font-size: 0.7rem !important;
            letter-spacing: 0.05em !important;
            color: {text_secondary} !important;
        }}

        /* File uploader */
        [data-testid="stFileUploader"] {{
            background-color: {bg_card} !important;
            border: 2px dashed {border_color} !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            transition: all 0.2s ease !important;
        }}

        [data-testid="stFileUploader"]:hover {{
            border-color: #0D9488 !important;
            background-color: rgba(13, 148, 136, 0.02) !important;
        }}

        /* Data frames / tables */
        .stDataFrame, [data-testid="stDataFrame"] {{
            border-radius: 16px !important;
            overflow: hidden !important;
            box-shadow: {shadow} !important;
            border: 1px solid {border_color} !important;
        }}

        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            border-radius: 10px !important;
            border: 1.5px solid {border_color} !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            background-color: {bg_card} !important;
            color: {text_primary} !important;
            transition: all 0.2s ease !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: #0D9488 !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
            outline: none !important;
        }}

        /* Selectbox */
        .stSelectbox > div > div {{
            border-radius: 10px !important;
            border: 1.5px solid {border_color} !important;
            background-color: {bg_card} !important;
        }}

        .stSelectbox > div > div:focus-within {{
            border-color: #0D9488 !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background-color: {bg_secondary};
            padding: 0.375rem;
            border-radius: 12px;
        }}

        .stTabs [data-baseweb="tab"] {{
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            border-radius: 8px !important;
            padding: 0.625rem 1rem !important;
            color: {text_secondary} !important;
            background-color: transparent !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%) !important;
            color: white !important;
            box-shadow: 0 2px 8px rgba(13, 148, 136, 0.3) !important;
        }}

        /* Alerts */
        .stAlert {{
            border-radius: 12px !important;
            border: none !important;
            padding: 1rem 1.25rem !important;
        }}

        [data-testid="stAlert"] > div {{
            padding: 0 !important;
        }}

        /* Info alert */
        .stAlert[data-baseweb="notification"] {{
            background-color: rgba(13, 148, 136, 0.1) !important;
            border-left: 4px solid #0D9488 !important;
        }}

        /* Checkbox */
        .stCheckbox label {{
            font-size: 0.95rem !important;
            color: {text_primary} !important;
        }}

        .stCheckbox label span {{
            color: {text_primary} !important;
        }}

        /* Progress bar */
        .stProgress > div > div {{
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%) !important;
            border-radius: 999px !important;
        }}

        /* Dividers */
        hr {{
            border: none !important;
            border-top: 1px solid {border_color} !important;
            margin: 2rem 0 !important;
        }}

        /* Links */
        a {{
            color: #0D9488 !important;
            text-decoration: none !important;
            font-weight: 500 !important;
        }}

        a:hover {{
            color: #0F766E !important;
            text-decoration: underline !important;
        }}

        /* Feature cards for landing page */
        .feature-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
        }}

        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: {shadow_lg};
            border-color: #0D9488;
        }}

        .feature-card .icon {{
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, rgba(13, 148, 136, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.25rem auto;
            color: #0D9488;
            font-size: 1.75rem;
        }}

        .feature-card h3 {{
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.75rem !important;
            color: {text_primary} !important;
        }}

        .feature-card p {{
            font-size: 0.95rem !important;
            color: {text_secondary} !important;
            line-height: 1.6 !important;
            margin: 0 !important;
        }}

        /* Hero section */
        .hero-section {{
            text-align: center;
            padding: 3rem 1rem;
            margin-bottom: 2rem;
        }}

        .hero-section h1 {{
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            margin-bottom: 1rem !important;
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .hero-section p {{
            font-size: 1.125rem !important;
            color: {text_secondary} !important;
            max-width: 600px;
            margin: 0 auto !important;
        }}

        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* Hide the header toolbar but keep space */
        [data-testid="stHeader"] {{
            background: transparent !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
        }}

        .block-container {{
            padding-top: 2rem !important;
            margin-top: 0 !important;
        }}

        /* Fix Streamlit sidebar collapse button icon */
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}

        /* Fix any icon rendering issues */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span.material-icons-outlined {{
            font-family: 'Material Icons Outlined' !important;
            font-weight: normal;
            font-style: normal;
            font-size: 24px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-smoothing: antialiased;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    """Render theme toggle button in sidebar."""
    current_theme = st.session_state.get('theme', 'light')

    # Use custom HTML for a nicer theme toggle
    if current_theme == 'light':
        icon = "dark_mode"
        label = "Dark Mode"
        new_theme = "dark"
    else:
        icon = "light_mode"
        label = "Light Mode"
        new_theme = "light"

    st.sidebar.markdown(
        f"""
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            .theme-toggle-btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                width: 100%;
                padding: 10px 16px;
                background: var(--bg-card, white);
                border: 1px solid var(--border-color, #E2E8F0);
                border-radius: 8px;
                color: var(--text-primary, #0F172A);
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                margin-bottom: 16px;
            }}
            .theme-toggle-btn:hover {{
                border-color: #0D9488;
                background: rgba(13, 148, 136, 0.05);
            }}
            .theme-toggle-btn .material-icons {{
                font-size: 18px;
                color: #0D9488;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button(f"{label}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = new_theme
        st.rerun()

# intial setup
# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# streamlit page setup
st.set_page_config(page_title="Vizion", page_icon=None, layout="wide")
inject_pro_theme_css()

# Styled header with logo
theme = st.session_state.get('theme', 'light')
text_secondary = "#94A3B8" if theme == 'dark' else "#64748B"

st.markdown(
    f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid var(--border-color, #E2E8F0);
    ">
        <div style="
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 1.5rem;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
        ">V</div>
        <div>
            <h1 style="
                margin: 0;
                font-size: 1.875rem;
                font-weight: 800;
                font-family: 'Inter', sans-serif;
                letter-spacing: -0.025em;
            ">Vizion</h1>
            <p style="
                margin: 0;
                font-size: 0.9rem;
                color: {text_secondary};
                font-family: 'Inter', sans-serif;
            ">Data Analysis & ML Platform</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

session = get_session()

# Render theme toggle and authentication sidebar
render_theme_toggle()
user = render_auth_sidebar(session, User)

# Only show main app if user is logged in
if user:

    with st.container():
        st.markdown(
            """
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, rgba(13, 148, 136, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #0D9488;
                ">
                    <span class="material-icons-outlined">history</span>
                </div>
                <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700;">Your Analysis History</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        user_analyses = (
            session.query(AnalysisHistory)
            .filter_by(user_id=user.id)
            .order_by(AnalysisHistory.created_at.desc())
            .all()
        )

        cleaned_analyses = []
        dirty = False
        for a in user_analyses:
            if a.dataset is None or not os.path.exists(getattr(a.dataset, "storage_path", "")):
                session.delete(a)
                dirty = True
            else:
                cleaned_analyses.append(a)
        if dirty:
            session.commit()
        user_analyses = cleaned_analyses

        col_hist_left, col_hist_right = st.columns([1, 1])
        with col_hist_left:
            if st.button("Clear All History") and user_analyses:
                session.query(AnalysisHistory).filter_by(user_id=user.id).delete()
                session.query(Dataset).filter_by(user_id=user.id).delete()
                session.commit()
                st.success("All analysis history deleted.")
                st.rerun()
        with col_hist_right:
            pass

        if user_analyses:
            for a in user_analyses:
                ds = a.dataset
                label = ds.filename if ds else "[Missing dataset]"
                with st.expander(f"{label} — {a.created_at.strftime('%Y-%m-%d %H:%M:%S')}"):
                    st.markdown(f"**Summary:** {a.summary}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Open / Edit", key=f"open_{a.id}"):
                            st.session_state.editing_analysis_id = a.id
                            st.rerun()
                    with c2:
                        if st.button("Delete", key=f"delete_{a.id}"):
                            session.delete(a)
                            session.commit()
                            st.success("Analysis deleted.")
                            st.rerun()
        else:
            st.info("No analysis history found. Upload and analyze a dataset to get started!")
    with st.container():
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.75rem; margin: 2rem 0 1rem 0;">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, rgba(13, 148, 136, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #0D9488;
                ">
                    <span class="material-icons-outlined">upload_file</span>
                </div>
                <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700;">Upload CSV File</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded is not None:
            filename = uploaded.name

            try:
                uploaded.seek(0)
            except Exception:
                pass
            try:
                df = pd.read_csv(uploaded)
            except UnicodeDecodeError:
                uploaded.seek(0)
                df = pd.read_csv(uploaded, encoding="latin-1")
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.stop()

            st.success(f"File '{filename}' uploaded successfully!")
            st.write("Preview of your file:")
            st.dataframe(df.head())

            original_csv_bytes = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Original CSV",
                data=original_csv_bytes,
                file_name=filename,
                mime="text/csv"
            )

            # Display column type detection
            display_column_types(df)
            
            st.header("Analyze this Dataset (Original)")
            current_config_initial = st.session_state.get("current_viz_config")
            current_config = analyze_csv(
                df.copy(),
                key_prefix="current",
                initial_config=current_config_initial
            )
            st.session_state.current_viz_config = current_config

            if st.button("Save this Analysis"):
                dataset_id = str(uuid.uuid4())
                os.makedirs("data", exist_ok=True)
                dataset_dir = os.path.join("data", dataset_id)
                os.makedirs(dataset_dir, exist_ok=True)
                csv_path = os.path.join(dataset_dir, "original.csv")
                df.to_csv(csv_path, index=False)

                dataset = Dataset(
                    id=dataset_id,
                    user_id=user.id,
                    filename=filename,
                    storage_path=csv_path,
                    row_count=len(df),
                    column_count=len(df.columns),
                    status="Saved",
                    uploaded_at=datetime.utcnow()
                )
                session.add(dataset)

                insights_json = json.dumps(current_config) if current_config else None
                analysis = AnalysisHistory(
                    id=str(uuid.uuid4()),
                    dataset_id=dataset.id,
                    user_id=user.id,
                    created_at=datetime.utcnow(),
                    summary=f"Analyzed '{filename}' with {len(df)} rows and {len(df.columns)} columns.",
                    insights=insights_json
                )
                session.add(analysis)
                session.commit()
                st.success("Analysis history saved.")
                
                # Send email notification
                if can_send_notification(user):
                    summary_html = f"<ul><li><strong>Rows:</strong> {len(df)}</li><li><strong>Columns:</strong> {len(df.columns)}</li></ul>"
                    if send_analysis_complete_email(user, filename, summary_html):
                        mark_notification_sent(session, user)
                
                st.session_state.editing_analysis_id = analysis.id
                st.rerun()

            # ML NOTEBOOK SECTION
            st.markdown("---")
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        background: linear-gradient(135deg, rgba(13, 148, 136, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #0D9488;
                    ">
                        <span class="material-icons-outlined">psychology</span>
                    </div>
                    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700;">Generate ML Notebook & Analysis</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.info("**New Feature!** Automatically generate a Jupyter notebook with ML analysis, train models, and get professional reports.")
            
            with st.expander("What is this?", expanded=False):
                st.markdown("""
                This feature automatically:
                - Generates a complete Jupyter notebook with ML code
                - Performs advanced exploratory data analysis
                - Trains and evaluates machine learning models
                - Extracts feature importance
                - Provides professional PDF and HTML reports
                - Allows you to download the notebook for further customization
                """)
            
            # Column for target selection
            col_types = detect_column_types(df)
            all_columns = df.columns.tolist()
            
            # Target column selection
            st.subheader("Step 1: Select Target Column (Optional)")
            target_column = st.selectbox(
                "Choose the column you want to predict (leave as 'None' for EDA only):",
                options=["None (EDA Only)"] + all_columns,
                key="ml_target_column",
                help="Select the variable you want to predict. If you're not sure, choose 'None' for exploratory analysis."
            )
            
            target_column = None if target_column == "None (EDA Only)" else target_column
            
            # Suggest ML task
            if target_column:
                task_suggestion = suggest_ml_task(df, target_column)
                st.info(f"**Suggested Task:** {task_suggestion['task_type'].replace('_', ' ').title()}")
                st.caption(f"Reason: {task_suggestion['reason']}")
                task_type = task_suggestion['task_type']
            else:
                task_type = 'eda'
                st.info("**Mode:** Exploratory Data Analysis (No ML model training)")
            
            # Model selection (only if not EDA)
            model_type = None
            if task_type != 'eda':
                st.subheader("Step 2: Select Model (Optional)")
                
                if 'classification' in task_type:
                    model_options = {
                        "Auto-select (Recommended)": None,
                        "Logistic Regression": "logistic_regression",
                        "Random Forest": "random_forest",
                        "Gradient Boosting": "gradient_boosting",
                        "K-Nearest Neighbors": "knn"
                    }
                else:
                    model_options = {
                        "Auto-select (Recommended)": None,
                        "Linear Regression": "linear_regression",
                        "Ridge Regression": "ridge",
                        "Random Forest": "random_forest",
                        "Gradient Boosting": "gradient_boosting"
                    }
                
                selected_model = st.selectbox(
                    "Choose a model or let the system auto-select:",
                    options=list(model_options.keys()),
                    key="ml_model_selection"
                )
                model_type = model_options[selected_model]
                
                if model_type is None:
                    st.caption("Multiple models will be trained and the best one will be selected automatically.")
                else:
                    st.caption(f"Will use {selected_model}")
            
            # Generate and Execute button
            st.subheader("Step 3: Generate & Execute ML Notebook")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                generate_button = st.button("Generate & Run ML Analysis", type="primary", use_container_width=True)
            
            with col2:
                generate_only = st.button("Generate Notebook Only (Don't Execute)", use_container_width=True)
            
            if generate_button or generate_only:
                # Save CSV temporarily
                temp_dataset_id = str(uuid.uuid4())
                os.makedirs("data", exist_ok=True)
                temp_dataset_dir = os.path.join("data", temp_dataset_id)
                os.makedirs(temp_dataset_dir, exist_ok=True)
                temp_csv_path = os.path.join(temp_dataset_dir, "data.csv")
                df.to_csv(temp_csv_path, index=False)
                
                # Generate notebook
                notebook_path = os.path.join(temp_dataset_dir, "ml_analysis.ipynb")
                
                with st.spinner("Generating ML notebook..."):
                    try:
                        generate_ml_notebook(
                            csv_path=temp_csv_path,
                            output_path=notebook_path,
                            target_column=target_column,
                            model_type=model_type,
                            task_type=task_type
                        )
                        st.success("Notebook generated successfully!")
                        
                        # Provide download for generated notebook
                        with open(notebook_path, 'rb') as nb_file:
                            st.download_button(
                                label="Download Generated Notebook (.ipynb)",
                                data=nb_file,
                                file_name="ml_analysis.ipynb",
                                mime="application/x-ipynb+json",
                                key="download_generated_notebook"
                            )
                        
                        if generate_button:
                            # Execute notebook
                            st.subheader("Executing Notebook...")
                            executed_notebook_path = os.path.join(temp_dataset_dir, "ml_analysis_executed.ipynb")
                            
                            with st.spinner("Training models and analyzing data... This may take a minute."):
                                try:
                                    result = execute_notebook(
                                        notebook_path=notebook_path,
                                        output_notebook_path=executed_notebook_path
                                    )
                                    
                                    if result['success']:
                                        st.success("Analysis completed successfully!")
                                        
                                        # Display results
                                        st.markdown("---")
                                        st.header("Analysis Results")
                                        
                                        metrics = result.get('metrics', {})
                                        
                                        if task_type != 'eda':
                                            # Display metrics in cards
                                            st.subheader("Model Performance")
                                            
                                            if 'classification' in task_type:
                                                col1, col2, col3, col4 = st.columns(4)
                                                
                                                with col1:
                                                    acc = metrics.get('accuracy', 0)
                                                    st.metric("Accuracy", f"{acc:.2%}" if acc else "N/A")
                                                
                                                with col2:
                                                    prec = metrics.get('precision', 0)
                                                    st.metric("Precision", f"{prec:.2%}" if prec else "N/A")
                                                
                                                with col3:
                                                    rec = metrics.get('recall', 0)
                                                    st.metric("Recall", f"{rec:.2%}" if rec else "N/A")
                                                
                                                with col4:
                                                    f1 = metrics.get('f1_score', 0)
                                                    st.metric("F1-Score", f"{f1:.2%}" if f1 else "N/A")
                                            
                                            else:  # Regression
                                                col1, col2, col3 = st.columns(3)
                                                
                                                with col1:
                                                    r2 = metrics.get('r2_score', 0)
                                                    st.metric("R² Score", f"{r2:.4f}" if r2 else "N/A")
                                                
                                                with col2:
                                                    mae = metrics.get('mae', 0)
                                                    st.metric("MAE", f"{mae:.4f}" if mae else "N/A")
                                                
                                                with col3:
                                                    rmse = metrics.get('rmse', 0)
                                                    st.metric("RMSE", f"{rmse:.4f}" if rmse else "N/A")
                                            
                                            if metrics.get('model_name'):
                                                st.info(f"**Best Model:** {metrics['model_name']}")
                                        
                                        # Execution summary
                                        st.subheader("Summary")
                                        summary = get_execution_summary(metrics)
                                        st.markdown(summary)
                                        
                                        # Generate reports
                                        st.markdown("---")
                                        st.subheader("Download Results")
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            # Download executed notebook
                                            with open(executed_notebook_path, 'rb') as nb_file:
                                                st.download_button(
                                                    label="Executed Notebook",
                                                    data=nb_file,
                                                    file_name="ml_analysis_executed.ipynb",
                                                    mime="application/x-ipynb+json",
                                                    key="download_executed_notebook"
                                                )
                                        
                                        with col2:
                                            # Convert to Python script
                                            py_script_path = os.path.join(temp_dataset_dir, "ml_analysis.py")
                                            if convert_notebook_to_python(executed_notebook_path, py_script_path):
                                                with open(py_script_path, 'rb') as py_file:
                                                    st.download_button(
                                                        label="Python Script",
                                                        data=py_file,
                                                        file_name="ml_analysis.py",
                                                        mime="text/x-python",
                                                        key="download_python_script"
                                                    )
                                        
                                        with col3:
                                            # Generate HTML report
                                            html_report_path = os.path.join(temp_dataset_dir, "model_report.html")
                                            dataset_info = {
                                                'rows': len(df),
                                                'columns': len(df.columns),
                                                'missing_values': df.isnull().sum().sum(),
                                                'numeric_features': len(col_types['numeric']),
                                                'categorical_features': len(col_types['categorical'])
                                            }
                                            ml_config = {
                                                'task_type': task_type,
                                                'target_column': target_column,
                                                'model_type': metrics.get('model_name', 'Auto-selected')
                                            }
                                            
                                            if generate_html_report(html_report_path, filename, dataset_info, ml_config, metrics, summary):
                                                with open(html_report_path, 'rb') as html_file:
                                                    st.download_button(
                                                        label="HTML Report",
                                                        data=html_file,
                                                        file_name="model_report.html",
                                                        mime="text/html",
                                                        key="download_html_report"
                                                    )
                                        
                                        with col4:
                                            # Generate PDF report
                                            pdf_report_path = os.path.join(temp_dataset_dir, "model_card.pdf")
                                            if generate_model_card_pdf(pdf_report_path, filename, dataset_info, ml_config, metrics):
                                                with open(pdf_report_path, 'rb') as pdf_file:
                                                    st.download_button(
                                                        label="PDF Model Card",
                                                        data=pdf_file,
                                                        file_name="model_card.pdf",
                                                        mime="application/pdf",
                                                        key="download_pdf_report"
                                                    )
                                        
                                        st.success("Complete ML pipeline executed successfully! Download your results above.")
                                        
                                        # Send email notification
                                        if can_send_notification(user):
                                            accuracy = metrics.get('accuracy') or metrics.get('r2_score')
                                            if send_ml_notebook_ready_email(user, filename, metrics.get('model_name', 'ML Model'), accuracy):
                                                mark_notification_sent(session, user)
                                    
                                    else:
                                        st.error(f"Notebook execution failed: {result.get('error', 'Unknown error')}")
                                        st.info("You can still download the generated notebook above and run it manually.")
                                
                                except Exception as e:
                                    st.error(f"Error during execution: {str(e)}")
                                    st.info("You can still download the generated notebook above and run it manually.")
                        
                    except Exception as e:
                        st.error(f"Error generating notebook: {str(e)}")
            
            st.markdown("---")
            
            st.header("Clean your Data (Optional)")
            cleaned_df = clean_data(df.copy())
            if not cleaned_df.equals(df):
                st.header("Analyze Cleaned Data")
                analyze_csv(cleaned_df, key_prefix="cleaned")
            else:
                st.info("Cleaning did not change the data.")

            cleaned_csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cleaned CSV",
                data=cleaned_csv_bytes,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )

    editing_id = st.session_state.get("editing_analysis_id")
    if editing_id:
        a = session.query(AnalysisHistory).filter_by(id=editing_id, user_id=user.id).first()
        if not a or not a.dataset or not os.path.exists(a.dataset.storage_path):
            st.warning("Saved dataset not found for this analysis.")
        else:
            st.header(f"Edit Saved Analysis: {a.dataset.filename}")
            df_edit = pd.read_csv(a.dataset.storage_path)
            try:
                initial_config = json.loads(a.insights) if a.insights else None
            except Exception:
                initial_config = None
            new_config = analyze_csv(
                df_edit,
                key_prefix=f"edit_{a.id}",
                initial_config=initial_config
            )
            if st.button("Save Changes", key=f"save_changes_{a.id}"):
                a.insights = json.dumps(new_config)
                session.commit()
                st.success("Analysis updated.")
                st.rerun()

else:
    # User not logged in - show beautiful landing page

    # Hero section
    st.markdown(
        """
        <div class="hero-section">
            <h1>Welcome to Vizion</h1>
            <p>Transform your data into actionable insights with powerful analysis tools,
            machine learning notebooks, and professional reports.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Call to action
    st.info("Please log in or register using the sidebar to start analyzing your data!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">
                    <span class="material-icons-outlined">analytics</span>
                </div>
                <h3>Data Analysis</h3>
                <p>Upload CSV files and get instant insights with interactive visualizations and comprehensive statistics.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">
                    <span class="material-icons-outlined">psychology</span>
                </div>
                <h3>ML Notebooks</h3>
                <p>Generate complete Jupyter notebooks with machine learning models automatically tailored to your data.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">
                    <span class="material-icons-outlined">description</span>
                </div>
                <h3>Professional Reports</h3>
                <p>Export your analyses as polished PDF and HTML reports ready for presentations and sharing.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
