import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date

from services.analytics_service import (
    get_executive_kpis,
    get_initiative_health_data,
    get_task_status_distribution,
    get_priority_distribution,
    get_owner_workload,
    get_overdue_tasks_list,
    get_upcoming_deadlines_list,
    get_ai_quality_metrics
)
from services.meeting_service import get_all_meetings
from utils.ui import (
    render_page_header,
    render_workflow_indicator,
    get_status_badge_html,
    get_priority_badge_html,
    render_empty_state,
    render_initiative_card,
    render_task_alert_card,
    render_meeting_feed_card,
    render_custom_kpi_card,
    get_plotly_minimalist_layout
)

def render_dashboard_page():
    render_page_header(
        title="Executive Portfolio Dashboard",
        subtitle="Real-time visibility into strategic initiative health, delivery velocity, and operational blockers",
        badge_text="Operational View",
        highlight_word="Portfolio"
    )

    render_workflow_indicator("Dashboard")

    # Fetch foundational live data from database services
    kpis = get_executive_kpis()
    ai_metrics = get_ai_quality_metrics()
    initiative_health = get_initiative_health_data()
    status_distribution = get_task_status_distribution()
    priority_distribution = get_priority_distribution()
    owner_workload = get_owner_workload()
    overdue_tasks = get_overdue_tasks_list(limit=6)
    upcoming_tasks = get_upcoming_deadlines_list(days_ahead=14)
    recent_meetings = get_all_meetings()[:4]

    # 1. Headline Executive KPIs (4 prominent cards, featuring Completion Rate with gradient border)
    headline_cols = st.columns(4)
    with headline_cols[0]:
        render_custom_kpi_card(
            label="Active Tasks",
            value=f"{kpis['active_tasks']}",
            subtext=f"{kpis['total_tasks']} total portfolio commitments",
            badge_text="In Flight",
            badge_color="blue",
            is_featured=False
        )
    with headline_cols[1]:
        render_custom_kpi_card(
            label="Overdue Tasks",
            value=f"{kpis['overdue_tasks']}",
            subtext=f"{kpis['overdue_rate']}% of active commitments",
            badge_text="Critical" if kpis['overdue_tasks'] > 0 else "Clean",
            badge_color="red" if kpis['overdue_tasks'] > 0 else "green",
            is_featured=False
        )
    with headline_cols[2]:
        render_custom_kpi_card(
            label="Pending Review",
            value=f"{kpis['pending_approvals']}",
            subtext="AI suggestions awaiting verification",
            badge_text="Gate Active",
            badge_color="amber" if kpis['pending_approvals'] > 0 else "neutral",
            is_featured=False
        )
    with headline_cols[3]:
        render_custom_kpi_card(
            label="Completion Rate",
            value=f"{kpis['completion_rate']}%",
            subtext=f"{kpis['completed_tasks']} commitments delivered",
            badge_text="Velocity",
            badge_color="green",
            is_featured=True
        )

    # 2. Inverted Contrast Section: AI Extraction Quality & Human Oversight Telemetry
    st.markdown("""
    <div class="inverted-section">
        <div class="inverted-section-header">
            <div>
                <div class="inverted-section-title">AI Quality & Human Oversight Telemetry</div>
                <div class="inverted-section-subtitle">Real-time inference metrics and human verification gate audit statistics</div>
            </div>
            <div class="section-badge-pill" style="border-color: rgba(77, 124, 255, 0.4); background: rgba(0, 82, 255, 0.2);">
                <span class="section-badge-dot"></span>
                <span class="section-badge-text" style="color: #93C5FD;">HUMAN-IN-THE-LOOP</span>
            </div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; font-size: 11px; color: #94A3B8; margin-bottom: 16px;">
            <span style="font-weight: 600; color: #FFFFFF;">Audit Trail Lineage:</span> <i>Computed dynamically from SQLite review_queue and audit_log records. Zero unverified mutations permitted.</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tele_row1 = st.columns(3)
    with tele_row1[0]:
        render_custom_kpi_card(
            label="AI Extracted",
            value=f"{ai_metrics['total_extracted']}",
            subtext="Candidates parsed across transcripts",
            badge_text="Model Output",
            badge_color="blue"
        )
    with tele_row1[1]:
        total_authorized = ai_metrics['approved'] + ai_metrics['edited']
        render_custom_kpi_card(
            label="Approval Rate",
            value=f"{ai_metrics['approval_rate']}%",
            subtext=f"{total_authorized} candidates admitted to tracker",
            badge_text=f"{total_authorized} authorized",
            badge_color="green"
        )
    with tele_row1[2]:
        render_custom_kpi_card(
            label="Rejection Rate",
            value=f"{ai_metrics['rejection_rate']}%",
            subtext=f"{ai_metrics['rejected']} dismissed as out of scope",
            badge_text=f"{ai_metrics['rejected']} dismissed",
            badge_color="red"
        )

    tele_row2 = st.columns(3)
    with tele_row2[0]:
        render_custom_kpi_card(
            label="Edited Pre-Approval",
            value=f"{ai_metrics['edit_rate']}%",
            subtext=f"{ai_metrics['edited']} modified by reviewer before approval",
            badge_text=f"{ai_metrics['edited']} pre-edits",
            badge_color="amber"
        )
    with tele_row2[1]:
        render_custom_kpi_card(
            label="Avg Confidence",
            value=f"{ai_metrics['avg_confidence']}%",
            subtext="Mean model extraction confidence score",
            badge_text="Inference",
            badge_color="blue"
        )
    with tele_row2[2]:
        render_custom_kpi_card(
            label="Interventions",
            value=f"{ai_metrics['human_intervention_count']}",
            subtext=f"{ai_metrics['intervention_rate']}% required active edit or dismissal",
            badge_text=f"{ai_metrics['intervention_rate']}% rate",
            badge_color="neutral"
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Section 1: Strategic Initiatives & Deliverable Breakdown
    col_initiatives, col_breakdowns = st.columns([7, 5])

    with col_initiatives:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:14px;'>Strategic Initiative Health</h3>", unsafe_allow_html=True)
        if initiative_health:
            for item in initiative_health:
                render_initiative_card(item)
        else:
            render_empty_state("No Active Initiatives", "No strategic programs are currently configured in the database.")

    with col_breakdowns:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:14px;'>Deliverable Status Distribution</h3>", unsafe_allow_html=True)
        status_labels = list(status_distribution.keys())
        status_values = list(status_distribution.values())
        
        status_palette = {
            "Completed": "#10B981",
            "In Progress": "#0052FF",
            "Not Started": "#94A3B8",
            "Blocked": "#EF4444"
        }
        slice_colors = [status_palette.get(status, "#CBD5E1") for status in status_labels]

        if sum(status_values) > 0:
            donut_fig = go.Figure(data=[go.Pie(
                labels=status_labels,
                values=status_values,
                hole=.62,
                marker=dict(colors=slice_colors),
                textinfo='none',
                hoverinfo='label+percent+value',
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent:.1%}<extra></extra>"
            )])
            layout = get_plotly_minimalist_layout(height=260)
            layout["margin"] = dict(t=10, b=10, l=10, r=10)
            layout["showlegend"] = True
            layout["legend"] = dict(
                orientation="h",
                yanchor="top",
                y=-0.08,
                xanchor="center",
                x=0.5,
                font=dict(family='Inter', size=11, color='#475569')
            )
            donut_fig.update_layout(layout)
            st.plotly_chart(donut_fig, use_container_width=True)
        else:
            render_empty_state("No Task Data", "Task distribution chart will populate once tasks are authorized.")

        st.markdown("<h3 class='calistoga-heading' style='font-size:16px; margin: 16px 0 10px 0;'>Deliverables by Priority</h3>", unsafe_allow_html=True)
        prio_labels = list(priority_distribution.keys())
        prio_values = list(priority_distribution.values())
        prio_colors = ["#EF4444", "#F59E0B", "#10B981"]

        if sum(prio_values) > 0:
            prio_fig = go.Figure(data=[go.Bar(
                x=prio_labels,
                y=prio_values,
                marker=dict(color=prio_colors, cornerradius=6),
                text=prio_values,
                textposition='auto',
                textfont=dict(family='Inter', size=11, color='#FFFFFF')
            )])
            p_layout = get_plotly_minimalist_layout(height=160)
            p_layout["margin"] = dict(t=10, b=20, l=10, r=10)
            p_layout["xaxis"]["showgrid"] = False
            p_layout["yaxis"]["showgrid"] = True
            prio_fig.update_layout(p_layout)
            st.plotly_chart(prio_fig, use_container_width=True)

    st.markdown("<hr style='margin: 24px 0; border: 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Section 2: Overdue Escalations & Upcoming Deadlines
    col_overdue, col_upcoming = st.columns(2)

    with col_overdue:
        st.markdown(f"<h3 class='calistoga-heading' style='font-size:18px; color:#B91C1C; margin-bottom:14px;'>Critical Overdue Deliverables ({len(overdue_tasks)})</h3>", unsafe_allow_html=True)
        if overdue_tasks:
            for task in overdue_tasks:
                render_task_alert_card(task, is_overdue=True)
        else:
            st.success("All deliverables on schedule. No overdue items across active strategic initiatives.")

    with col_upcoming:
        st.markdown(f"<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:14px;'>Upcoming Milestones (Next 14 Days) ({len(upcoming_tasks)})</h3>", unsafe_allow_html=True)
        if upcoming_tasks:
            for task in upcoming_tasks[:6]:
                render_task_alert_card(task, is_overdue=False)
        else:
            st.info("No milestone deadlines scheduled in the next 14 calendar days.")

    st.markdown("<hr style='margin: 24px 0; border: 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Section 3: Owner Workload & Meeting Intelligence Feed
    col_workload, col_meetings = st.columns([7, 5])

    with col_workload:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:14px;'>Workload Distribution by Deliverable Owner</h3>", unsafe_allow_html=True)
        if owner_workload:
            df_work = pd.DataFrame(owner_workload)
            workload_fig = go.Figure()
            workload_fig.add_trace(go.Bar(name='Completed', y=df_work['owner'], x=df_work['completed'], orientation='h', marker_color='#10B981'))
            workload_fig.add_trace(go.Bar(name='In Progress', y=df_work['owner'], x=df_work['in_progress'], orientation='h', marker_color='#0052FF'))
            workload_fig.add_trace(go.Bar(name='Blocked', y=df_work['owner'], x=df_work['blocked'], orientation='h', marker_color='#EF4444'))
            workload_fig.add_trace(go.Bar(name='Not Started', y=df_work['owner'], x=df_work['not_started'], orientation='h', marker_color='#94A3B8'))

            w_layout = get_plotly_minimalist_layout(height=300)
            w_layout["barmode"] = "stack"
            w_layout["xaxis"]["title"] = "Deliverables"
            w_layout["yaxis"]["showgrid"] = False
            workload_fig.update_layout(w_layout)
            st.plotly_chart(workload_fig, use_container_width=True)
        else:
            render_empty_state("No Workload Records", "Owner distribution will populate as tasks are assigned.")

    with col_meetings:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:14px;'>Recent Meeting Intelligence Feed</h3>", unsafe_allow_html=True)
        if recent_meetings:
            for meeting in recent_meetings:
                render_meeting_feed_card(meeting)
        else:
            render_empty_state("No Meetings Logged", "Log meetings in the Meetings Repository to generate summaries.")
