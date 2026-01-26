"""
UI Components for Vizion.
Provides styled helper functions for consistent UI across the app.
"""

import streamlit as st


def app_header(title: str, subtitle: str = None):
    """Render app header with icon and optional subtitle."""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <div style="
                width: 2.5rem;
                height: 2.5rem;
                background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 1.25rem;
            ">V</div>
            <div>
                <h1 style="margin: 0; font-size: 1.5rem; font-weight: 700; font-family: 'Inter', sans-serif;">{title}</h1>
                {f'<p style="margin: 0; font-size: 0.875rem; color: #64748B;">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_header(title: str, icon: str = None):
    """Render a section header with optional icon."""
    icon_html = ""
    if icon:
        icon_html = f"""
            <div style="
                width: 2rem;
                height: 2rem;
                background-color: #0D9488;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.875rem;
            ">{icon}</div>
        """

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; margin-top: 1.5rem;">
            {icon_html}
            <h2 style="margin: 0; font-size: 1.125rem; font-weight: 700; font-family: 'Inter', sans-serif;">{title}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(text: str):
    """Simple section title (for backwards compatibility)."""
    st.markdown(f"### {text}")


def stat_card(label: str, value: str, trend: str = None, trend_positive: bool = True):
    """
    Render a styled statistics card (theme-aware).

    Args:
        label: The metric label (e.g., "Total Rows")
        value: The metric value (e.g., "16.6k")
        trend: Optional trend text (e.g., "+3.1% vs last month")
        trend_positive: Whether the trend is positive (green) or negative (red)
    """
    trend_html = ""
    if trend:
        trend_color = "#10B981" if trend_positive else "#EF4444"
        trend_html = f'<p style="font-size: 0.625rem; font-weight: 500; color: {trend_color}; margin: 0.25rem 0 0 0;">{trend}</p>'

    st.markdown(
        f"""
        <div style="
            background-color: var(--bg-card, white);
            border: 1px solid var(--border-color, #E2E8F0);
            border-radius: 16px;
            padding: 1.25rem;
            box-shadow: var(--shadow, 0 1px 3px rgba(0,0,0,0.1));
        ">
            <p style="
                font-size: 0.625rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-secondary, #64748B);
                margin: 0 0 0.5rem 0;
                font-family: 'Inter', sans-serif;
            ">{label}</p>
            <p style="
                font-size: 1.75rem;
                font-weight: 700;
                color: var(--text-primary, #0F172A);
                margin: 0;
                font-family: 'Inter', sans-serif;
            ">{value}</p>
            {trend_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def card_start():
    """Start a card container (theme-aware). Use with card_end()."""
    st.markdown(
        """
        <div style="
            background-color: var(--bg-card, white);
            border: 1px solid var(--border-color, #E2E8F0);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow, 0 1px 3px rgba(0,0,0,0.1));
            margin-bottom: 1rem;
        ">
        """,
        unsafe_allow_html=True
    )


def card_end():
    """End a card container. Use with card_start()."""
    st.markdown("</div>", unsafe_allow_html=True)


def action_button_row(buttons: list):
    """
    Render a row of action buttons.

    Args:
        buttons: List of tuples (label, icon, is_primary)
                 e.g., [("Share", "share", True), ("Export", "download", False)]
    """
    buttons_html = ""
    for label, icon, is_primary in buttons:
        if is_primary:
            style = """
                background-color: #0D9488;
                color: white;
                border: none;
            """
        else:
            style = """
                background-color: white;
                color: #0F172A;
                border: 1px solid #E2E8F0;
            """

        buttons_html += f"""
            <button style="
                {style}
                display: inline-flex;
                align-items: center;
                gap: 0.375rem;
                padding: 0.5rem 1rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                cursor: pointer;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            ">{label}</button>
        """

    st.markdown(
        f"""
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
            {buttons_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def info_badge(text: str, color: str = "teal"):
    """
    Render a small info badge.

    Args:
        text: Badge text
        color: Color name (teal, green, amber, red, gray)
    """
    colors = {
        "teal": ("#0D9488", "#CCFBF1"),
        "green": ("#10B981", "#D1FAE5"),
        "amber": ("#F59E0B", "#FEF3C7"),
        "red": ("#EF4444", "#FEE2E2"),
        "gray": ("#64748B", "#F1F5F9"),
    }
    text_color, bg_color = colors.get(color, colors["gray"])

    st.markdown(
        f"""
        <span style="
            display: inline-block;
            background-color: {bg_color};
            color: {text_color};
            font-size: 0.625rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-family: 'Inter', sans-serif;
        ">{text}</span>
        """,
        unsafe_allow_html=True
    )


def divider():
    """Render a styled divider (theme-aware)."""
    st.markdown(
        '<hr style="border: none; border-top: 1px solid var(--border-color, #E2E8F0); margin: 1.5rem 0;">',
        unsafe_allow_html=True
    )


def sidebar_nav():
    """Sidebar navigation (for backwards compatibility)."""
    return st.sidebar.radio("Navigation", ["Upload & Analyze", "History", "Profile", "Settings"])
