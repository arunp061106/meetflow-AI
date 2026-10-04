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

# Define pages with icons and URLs for native Streamlit navigation
dashboard_page = st.Page(render_dashboard_page, title="Executive Dashboard", icon=":material/dashboard:", default=True)
meetings_page = st.Page(render_meetings_page, title="Meetings Repository", icon=":material/meeting_room:", url_path="meetings")
extraction_page = st.Page(render_extraction_page, title="AI Extraction Engine", icon=":material/psychology:", url_path="extraction")
approval_page = st.Page(render_approval_page, title=f"Approval Queue ({pending_count})", icon=":material/verified_user:", url_path="approval-queue")
audit_page = st.Page(render_audit_trail_page, title="Audit Trail & Lineage", icon=":material/history_edu:", url_path="audit-trail")
tracker_page = st.Page(render_tracker_page, title="Initiative & Task Tracker", icon=":material/task_alt:", url_path="tracker")
analytics_page = st.Page(render_analytics_page, title="Portfolio Analytics", icon=":material/analytics:", url_path="analytics")
report_page = st.Page(render_report_page, title="Weekly Status Report", icon=":material/summarize:", url_path="weekly-report")
settings_page = st.Page(render_settings_page, title="System Settings", icon=":material/settings:", url_path="settings")

# Map human-readable names for programmatic page routing
page_routing_map = {
    "Executive Dashboard": dashboard_page,
    "Meetings": meetings_page,
    "AI Extraction": extraction_page,
    "Approval Queue": approval_page,
    "Audit Trail": audit_page,
    "Initiative Tracker": tracker_page,
    "Analytics": analytics_page,
    "Weekly Report": report_page,
    "Settings": settings_page
}

# Support cross-page programmatic switching
if "nav_selection" in st.session_state and st.session_state["nav_selection"] in page_routing_map:
    target_page = page_routing_map[st.session_state.pop("nav_selection")]
    st.switch_page(target_page)

# Initialize modern native Streamlit icon navigation with enterprise sections
current_page = st.navigation(
    {
        "Portfolio & Overview": [dashboard_page, analytics_page, report_page],
        "Human-in-the-Loop AI": [meetings_page, extraction_page, approval_page, audit_page],
        "Delivery & Governance": [tracker_page, settings_page]
    },
    position="sidebar"
)

# Sidebar Supporting Widgets & Governance Branding
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

    # Mandatory Human-in-the-Loop Callout in Sidebar
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 3px solid #2563eb; border-radius: 8px; padding: 12px 14px; margin-top: 14px; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.03);">
        <div style="color: #2563eb; font-weight: 700; font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;">
            Governance Policy
        </div>
        <div style="font-size: 11px; color: #475569; line-height: 1.5;">
            <b>AI suggestions are never committed automatically.</b> Every action item requires explicit human verification before tracker entry.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Engine Status in Sidebar
    ai_cfg = get_ai_config()
    if ai_cfg["is_demo_mode"]:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #475569; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.02);">
            <div style="color: #2563eb; font-weight: 600;">Engine: Offline Demo Engine</div>
            <div style="color: #64748b; font-size: 10px; margin-top: 2px;">Zero-setup deterministic extraction</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #065f46;">
            <div style="color: #059669; font-weight: 600;">Engine: Live LLM Connected</div>
            <div style="color: #047857; font-size: 10px; margin-top: 2px;">Model: <code>{ai_cfg['model_name']}</code></div>
        </div>
        """, unsafe_allow_html=True)

    # Credibility footer: v1.0 · Demo build
    st.markdown("""
    <div style="margin-top: 20px; font-size: 10px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 12px;">
        MeetFlow AI &bull; v1.0 &middot; Demo build &bull; SQLite Persistence
    </div>
    """, unsafe_allow_html=True)

# Run active routed page
current_page.run()
