"""
KPI Metric Cards Component for RetailPulse Dashboard.
Renders responsive, styled executive metric cards with value formatting and deltas.
"""

from typing import Optional
import streamlit as st


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_type: str = "positive",
    subtitle: Optional[str] = None,
) -> None:
    """Renders a single KPI card with custom HTML and CSS."""
    delta_class = "delta-positive" if delta_type == "positive" else ("delta-negative" if delta_type == "negative" else "delta-neutral")
    delta_icon = "▲" if delta_type == "positive" else ("▼" if delta_type == "negative" else "●")

    delta_html = ""
    if delta:
        delta_html = f'<span class="{delta_class}">{delta_icon} {delta}</span>'

    footer_text = f'<span class="delta-neutral">{subtitle}</span>' if subtitle else ""

    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-footer">
            {delta_html}
            {footer_text}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def format_currency(val: float) -> str:
    """Formats numeric amount as abbreviated USD currency."""
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.1f}K"
    return f"${val:.2f}"


def format_number(val: int) -> str:
    """Formats integer with comma separation."""
    return f"{val:,}"
