import streamlit as st
from typing import Optional

def apply_custom_css():
    """Injects high-end modern enterprise SaaS styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global Typography & Canvas */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0f172a;
        background-color: #f8fafc;
    }

    /* Streamlit block container tuning */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
    }

    /* Hide default Streamlit footer */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* Page Header */
    .enterprise-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 4px 0 16px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .header-titles {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .page-title {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0f172a;
        margin: 0;
    }
    .page-subtitle {
        font-size: 13px;
        color: #64748b;
        margin: 0;
        font-weight: 400;
    }
    .header-badge {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
    }

    /* Stepper Workflow Navigation */
    .stepper-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    .stepper-label {
        font-size: 11px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stepper-items {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .step-node {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        padding: 4px 10px;
        border-radius: 6px;
    }
    .step-node.active {
        color: #1e40af;
        background: #eff6ff;
        font-weight: 600;
        border: 1px solid #bfdbfe;
    }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #475569;
        font-size: 10px;
        font-weight: 700;
    }
    .step-node.active .step-number {
        background: #2563eb;
        color: #ffffff;
    }
    .stepper-sep {
        color: #cbd5e1;
        font-size: 12px;
    }

    /* Enterprise Metric Card styling */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
    }

    /* Governance Banner */
    .governance-hero-banner {
        background: #ffffff;
        border-left: 4px solid #2563eb;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .gov-pill {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #1e40af;
        background: #eff6ff;
        border: 1px solid #dbeafe;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 6px;
    }
    .gov-heading {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .gov-subtext {
        font-size: 13px;
        color: #475569;
        line-height: 1.5;
    }

    /* Approval Queue Dossier Cards */
    .approval-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        transition: border-color 0.15s ease;
    }
    .approval-card:hover {
        border-color: #cbd5e1;
    }
    .approval-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .approval-card-title {
        font-size: 15px;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.4;
    }
    .approval-meta-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        background: #f8fafc;
        border: 1px solid #f1f5f9;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 10px 0;
        font-size: 12px;
    }
    .meta-item-label {
        font-size: 10px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }
    .meta-item-val {
        font-weight: 600;
        color: #1e293b;
    }
    .evidence-dossier {
        background: #f8fafc;
        border-left: 3px solid #64748b;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 10px 0 14px 0;
        font-size: 12px;
        color: #334155;
    }
    .evidence-label {
        font-size: 10px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .evidence-text {
        font-style: italic;
        line-height: 1.5;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }
    .badge-completed { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-in-progress { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .badge-not-started { background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; }
    .badge-blocked { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
    .badge-overdue { background: #fef2f2; color: #b91c1c; border: 1px solid #f87171; font-weight: 700; }

    .badge-high { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-medium { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
    .badge-low { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }

    .badge-confidence { background: #f5f3ff; color: #5b21b6; border: 1px solid #ddd6fe; font-weight: 600; }

    /* Empty State Box */
    .empty-state-box {
        background: #ffffff;
        border: 1px dashed #cbd5e1;
        border-radius: 8px;
        padding: 36px 20px;
        text-align: center;
        margin: 16px 0;
    }
    .empty-state-title {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .empty-state-desc {
        font-size: 13px;
        color: #64748b;
        max-width: 480px;
        margin: 0 auto;
    }

    /* Sidebar custom branding */
    .sidebar-brand-box {
        padding: 8px 0 16px 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 16px;
    }
    .sidebar-brand-title {
        font-size: 18px;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-brand-logo {
        background: #2563eb;
        color: #ffffff;
        padding: 3px 7px;
        border-radius: 5px;
        font-size: 13px;
        font-weight: 800;
    }
    .sidebar-brand-subtitle {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 4px;
        letter-spacing: 0.02em;
    }

    /* Clean Streamlit tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        padding: 8px 12px;
    }
    .stTabs [aria-selected="true"] {
        color: #1e40af !important;
        border-bottom-color: #2563eb !important;
    }
    /* Custom Initiative & Alert Cards */
    .initiative-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    .initiative-card:hover {
        border-color: #cbd5e1;
    }
    .task-alert-card {
        background: #ffffff;
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 8px;
        border: 1px solid #e2e8f0;
    }
    .task-alert-card.overdue {
        border-left: 4px solid #ef4444;
        border-top: 1px solid #fee2e2;
        border-right: 1px solid #fee2e2;
        border-bottom: 1px solid #fee2e2;
    }
    .task-alert-card.upcoming {
        border-left: 4px solid #3b82f6;
    }
    .task-alert-card.urgent {
        border-left: 4px solid #f59e0b;
    }
    .meeting-feed-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .meeting-feed-card:hover {
        border-color: #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, badge_text: Optional[str] = None):
    """Renders standardized high-end enterprise page header."""
    badge_html = f'<div class="header-badge">{badge_text}</div>' if badge_text else ''
    st.markdown(f"""
    <div class="enterprise-header">
        <div class="header-titles">
            <h1 class="page-title">{title}</h1>
            <p class="page-subtitle">{subtitle}</p>
        </div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

def render_workflow_indicator(current_step: str = "Dashboard"):
    """Renders the core human-in-the-loop product workflow pipeline."""
    steps = [
        ("AI Extraction", "1. AI Extraction"),
        ("Approval Queue", "2. Human Approval"),
        ("Initiative Tracker", "3. Official Tracker"),
        ("Analytics", "4. Analytics"),
        ("Weekly Report", "5. Weekly Report")
    ]
    
    html = '<div class="stepper-container">'
    html += '<span class="stepper-label">Execution Flow:</span>'
    html += '<div class="stepper-items">'
    for i, (name, label) in enumerate(steps, 1):
        is_active = (current_step == name)
        active_class = "active" if is_active else ""
        html += f'<div class="step-node {active_class}"><span class="step-number">{i}</span>{label.split(". ")[1]}</div>'
        if i < len(steps):
            html += '<span class="stepper-sep">→</span>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_governance_banner():
    """Renders the mandatory human-in-the-loop governance explanation banner."""
    st.markdown("""
    <div class="governance-hero-banner">
        <div class="gov-pill">Mandatory Governance Policy</div>
        <div class="gov-heading">Human Verification Required for All Deliverables</div>
        <div class="gov-subtext">
            <b>AI suggestions are never committed automatically. Every action item requires human verification.</b>
            Items staged below were inferred from meeting transcripts. Authorize deliverables to commit them to the official initiative tracker, or reject items to record them in the governance audit trail.
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_empty_state(title: str, description: str):
    """Renders clean corporate empty state."""
    st.markdown(f"""
    <div class="empty-state-box">
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def get_status_badge_html(status: str, is_overdue: bool = False) -> str:
    """Returns clean HTML badge for status."""
    if is_overdue and status != "Completed":
        return '<span class="badge badge-overdue">OVERDUE</span>'
    s_clean = status.lower().replace(" ", "-")
    return f'<span class="badge badge-{s_clean}">{status}</span>'

def get_priority_badge_html(priority: str) -> str:
    """Returns clean HTML badge for priority."""
    p_clean = priority.lower()
    return f'<span class="badge badge-{p_clean}">{priority} Priority</span>'

def get_confidence_badge_html(score: float) -> str:
    """Returns clean HTML badge for AI confidence score."""
    pct = int(score * 100) if score <= 1.0 else int(score)
    return f'<span class="badge badge-confidence">{pct}% Inferred Match</span>'

def render_initiative_card(item: dict):
    """Renders a structured, accessible card for an initiative."""
    health_styles = {
        "On Track": {"color": "#059669", "bg": "#ecfdf5", "border": "#a7f3d0"},
        "Needs Attention": {"color": "#d97706", "bg": "#fffbeb", "border": "#fde68a"},
        "At Risk": {"color": "#dc2626", "bg": "#fef2f2", "border": "#fca5a5"}
    }
    style = health_styles.get(item["health"], health_styles["On Track"])

    st.markdown(f"""
    <div class="initiative-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div>
                <span style="font-weight:700; color:#0f172a; font-size:14px;">{item['initiative']}</span>
                <span style="font-size:12px; color:#64748b; margin-left:8px;">Lead: <b>{item['owner']}</b></span>
            </div>
            <span style="background:{style['bg']}; color:{style['color']}; border:1px solid {style['border']}; padding:2px 8px; border-radius:4px; font-weight:700; font-size:10px; letter-spacing:0.04em;">
                {item['health'].upper()}
            </span>
        </div>
        <div style="display:flex; gap:16px; font-size:12px; color:#475569; margin-bottom:8px;">
            <span>Total: <b>{item['total_tasks']}</b></span>
            <span>Completed: <b style="color:#059669;">{item['completed']}</b></span>
            <span>In Progress: <b style="color:#2563eb;">{item['in_progress']}</b></span>
            <span>Blocked: <b style="color:#dc2626;">{item['blocked']}</b></span>
            <span>Overdue: <b style="color:#b91c1c;">{item['overdue']}</b></span>
        </div>
        <div style="background:#f1f5f9; border-radius:4px; height:6px; width:100%; overflow:hidden;">
            <div style="background:#10b981; height:100%; width:{item['completion_rate']}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748b; margin-top:4px;">
            <span>Current Sprint Commitment</span>
            <span><b>{item['completion_rate']}% Complete</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_task_alert_card(task: dict, is_overdue: bool = True):
    """Renders a single overdue or upcoming deadline task item."""
    if is_overdue:
        days_late = task.get("days_late", 0)
        badge = f'<span style="background:#fef2f2; color:#b91c1c; border:1px solid #fecaca; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; white-space:nowrap;">{days_late}D OVERDUE</span>'
        css_class = "task-alert-card overdue"
    else:
        days_left = task.get("days_left", 0)
        is_urgent = days_left <= 3
        badge_bg = "#fffbeb" if is_urgent else "#eff6ff"
        badge_color = "#92400e" if is_urgent else "#1e40af"
        badge_border = "#fde68a" if is_urgent else "#bfdbfe"
        badge = f'<span style="background:{badge_bg}; color:{badge_color}; border:1px solid {badge_border}; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; white-space:nowrap;">DUE IN {days_left}D</span>'
        css_class = "task-alert-card urgent" if is_urgent else "task-alert-card upcoming"

    date_label = "Due" if is_overdue else "Target"
    st.markdown(f"""
    <div class="{css_class}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
            <div>
                <span style="font-weight:600; color:#0f172a; font-size:13px;">#{task['id']}. {task['title']}</span>
                <div style="font-size:12px; color:#64748b; margin-top:2px;">
                    Owner: <b>{task['owner']}</b> &bull; Initiative: {task['initiative']} &bull; {date_label}: <b>{task['deadline']}</b>
                </div>
            </div>
            {badge}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_meeting_feed_card(meeting: dict):
    """Renders a concise, human-readable meeting intelligence summary."""
    summary_text = meeting['summary'] or 'Meeting notes recorded and indexed.'
    st.markdown(f"""
    <div class="meeting-feed-card">
        <div style="font-weight:600; color:#0f172a; font-size:13px;">{meeting['title']}</div>
        <div style="font-size:11px; color:#64748b; margin:2px 0 4px 0;">
            Date: {meeting['meeting_date']} &bull; Type: {meeting['meeting_type']} &bull; Organizer: {meeting['organizer']}
        </div>
        <div style="font-size:12px; color:#475569; line-height:1.4;">
            {summary_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
