import streamlit as st
from dotenv import load_dotenv

# Set page config at the very top
st.set_page_config(
    page_title="MeetFlow AI — Enterprise Meeting & Initiative Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# Initialize DB and seed demo data on initial startup
from database.db import init_db
from database.seed import seed_demo_data
from services.review_service import get_review_queue_items
from ai.extractor import get_ai_config
from utils.ui import apply_custom_css

# Ensure database exists and seed demo data
init_db()
seed_demo_data(force=False)

# Apply custom enterprise SaaS styles
apply_custom_css()

# Import page views
from pages_views.dashboard_view import render_dashboard_page
from pages_views.meetings_view import render_meetings_page
from pages_views.extraction_view import render_extraction_page
from pages_views.approval_view import render_approval_page
from pages_views.audit_view import render_audit_trail_page
from pages_views.tracker_view import render_tracker_page
from pages_views.analytics_view import render_analytics_page
from pages_views.report_view import render_report_page
from pages_views.settings_view import render_settings_page

# Count pending items for sidebar badge
pending_items = get_review_queue_items(status_filter="Pending")
pending_count = len(pending_items)

# Navigation setup (clean enterprise typography)
PAGES = {
    "Executive Dashboard": ("Executive Dashboard", render_dashboard_page),
    "Meetings": ("Meetings Repository", render_meetings_page),
    "AI Extraction": ("AI Extraction Engine", render_extraction_page),
    "Approval Queue": (f"Approval Queue [{pending_count}]", render_approval_page),
    "Audit Trail": ("Audit Trail & Lineage", render_audit_trail_page),
    "Initiative Tracker": ("Initiative & Task Tracker", render_tracker_page),
    "Analytics": ("Portfolio Analytics", render_analytics_page),
    "Weekly Report": ("Weekly Status Report", render_report_page),
    "Settings": ("System & Governance Settings", render_settings_page)
}


# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-title">
            <span class="sidebar-brand-logo">MF</span>
            MEETFLOW AI
        </div>
        <div class="sidebar-brand-subtitle">
            Enterprise Initiative & Meeting Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Manage programmatic navigation
    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = "Executive Dashboard"

    # Find index
    page_keys = list(PAGES.keys())
    current_idx = page_keys.index(st.session_state["nav_selection"]) if st.session_state["nav_selection"] in page_keys else 0

    st.markdown("<div style='font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;'>Navigation</div>", unsafe_allow_html=True)
    selected_page_key = st.radio(
        "Navigation",
        options=page_keys,
        index=current_idx,
        format_func=lambda k: PAGES[k][0],
        label_visibility="collapsed"
    )

    # Update session state if user clicks directly in sidebar radio
    st.session_state["nav_selection"] = selected_page_key

    # Mandatory Human-in-the-Loop Callout in Sidebar
    st.markdown("""
    <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 12px 14px; margin-top: 24px;">
        <div style="color: #60a5fa; font-weight: 700; font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;">
            Governance Policy
        </div>
        <div style="font-size: 11px; color: #94a3b8; line-height: 1.5;">
            <b>AI suggestions are never committed automatically.</b> Every action item requires explicit human verification before tracker entry.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Engine Status in Sidebar
    ai_cfg = get_ai_config()
    if ai_cfg["is_demo_mode"]:
        st.markdown("""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 8px 12px; font-size: 11px; color: #94a3b8;">
            <div style="color: #38bdf8; font-weight: 600;">Engine: Offline Demo Engine</div>
            <div style="color: #64748b; font-size: 10px; margin-top: 2px;">Zero-setup deterministic extraction</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: #064e3b; border: 1px solid #059669; border-radius: 6px; padding: 8px 12px; font-size: 11px; color: #a7f3d0;">
            <div style="color: #34d399; font-weight: 600;">Engine: Live LLM Connected</div>
            <div style="color: #6ee7b7; font-size: 10px; margin-top: 2px;">Model: <code>{ai_cfg['model_name']}</code></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 20px; font-size: 10px; color: #475569; text-align: center; border-top: 1px solid #1e293b; padding-top: 12px;">
        MeetFlow AI &bull; Production v2.4 &bull; SQLite Persistence
    </div>
    """, unsafe_allow_html=True)

# Render selected page
page_render_fn = PAGES[st.session_state["nav_selection"]][1]
page_render_fn()
