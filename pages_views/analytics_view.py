import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

from services.analytics_service import (
    get_executive_kpis,
    get_initiative_health_data,
    get_owner_workload,
    get_task_status_distribution,
    get_priority_distribution,
    get_approval_acceptance_metrics,
    get_average_completion_time_days
)
from services.task_service import get_all_tasks
from services.meeting_service import get_all_initiatives
from utils.ui import (
    render_page_header,
    render_workflow_indicator,
    render_empty_state,
    render_custom_kpi_card,
    get_plotly_minimalist_layout
)

def render_analytics_page():
    render_page_header(
        title="Initiative & Operations Analytics",
        subtitle="Executive performance intelligence, delivery throughput, and human approval funnel analytics",
        badge_text="Portfolio Intelligence",
        highlight_word="Analytics"
    )

    render_workflow_indicator("Analytics")

    # Fetch foundational metrics
    kpis = get_executive_kpis()
    approval_metrics = get_approval_acceptance_metrics()
    avg_completion_days = get_average_completion_time_days()

    # Top KPI Metrics Cards using Minimalist Modern cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_custom_kpi_card("Completion Rate", f"{kpis['completion_rate']}%", "Delivered commitments", "Velocity", "green", is_featured=True)
    with c2:
        render_custom_kpi_card("Overdue Rate", f"{kpis['overdue_rate']}%", f"{kpis['overdue_tasks']} tasks overdue", "Critical" if kpis['overdue_tasks'] > 0 else "Clean", "red" if kpis['overdue_tasks'] > 0 else "green")
    with c3:
        render_custom_kpi_card("Avg Turnaround", f"{avg_completion_days} days", "Lifecycle throughput", "Speed", "blue")
    with c4:
        render_custom_kpi_card("Blocked Tasks", f"{kpis['blocked_tasks']}", "Escalations required", "Action" if kpis['blocked_tasks'] > 0 else "None", "amber" if kpis['blocked_tasks'] > 0 else "neutral")
    with c5:
        render_custom_kpi_card("Approval Rate", f"{approval_metrics['acceptance_rate']}%", "Human gate verification", "Gate", "blue")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Filter Bar for deep dive
    initiatives = get_all_initiatives()
    init_names = [i["name"] for i in initiatives]

    all_tasks = get_all_tasks()
    all_owners = sorted(list(set(t["owner"] for t in all_tasks if t["owner"])))

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sel_init = st.selectbox("Strategic Initiative", ["All Initiatives"] + init_names)
    with fc2:
        sel_owner = st.selectbox("Task Owner", ["All Owners"] + all_owners)
    with fc3:
        sel_prio = st.selectbox("Priority Level", ["All Priorities", "High", "Medium", "Low"])

    # Filtered dataset
    filtered_tasks = all_tasks
    if sel_init != "All Initiatives":
        filtered_tasks = [t for t in filtered_tasks if t["initiative"] == sel_init]
    if sel_owner != "All Owners":
        filtered_tasks = [t for t in filtered_tasks if t["owner"] == sel_owner]
    if sel_prio != "All Priorities":
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == sel_prio]

    st.markdown(f"<div style='font-family:var(--font-mono); font-size:11px; color:#64748B; margin: 4px 0 16px 0;'>Analyzing <b>{len(filtered_tasks)}</b> deliverable record(s) matching selected parameters.</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 8px 0 20px 0; border:0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Visualization Row 1: Initiative Throughput & Approval Funnel
    col1, col2 = st.columns([7, 5])

    with col1:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:12px;'>Initiative Throughput & Execution Status</h3>", unsafe_allow_html=True)
        init_health = get_initiative_health_data()
        if init_health:
            df_init = pd.DataFrame(init_health)
            fig_init = go.Figure()
            fig_init.add_trace(go.Bar(
                name='Completed',
                x=df_init['initiative'],
                y=df_init['completed'],
                marker_color='#10B981'
            ))
            fig_init.add_trace(go.Bar(
                name='In Progress',
                x=df_init['initiative'],
                y=df_init['in_progress'],
                marker_color='#0052FF'
            ))
            fig_init.add_trace(go.Bar(
                name='Blocked',
                x=df_init['initiative'],
                y=df_init['blocked'],
                marker_color='#EF4444'
            ))
            layout1 = get_plotly_minimalist_layout(height=320)
            layout1["barmode"] = "stack"
            layout1["xaxis"]["showgrid"] = False
            layout1["xaxis"]["tickangle"] = -20
            fig_init.update_layout(layout1)
            st.plotly_chart(fig_init, use_container_width=True)
        else:
            render_empty_state("No Initiative Data", "Initiative throughput will be charted once tasks are recorded.")

    with col2:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:12px;'>Governance Approval Funnel</h3>", unsafe_allow_html=True)
        funnel_labels = ["Extracted Candidates", "Approved As-Is", "Edited & Approved", "Rejected", "Pending Review"]
        funnel_vals = [
            approval_metrics["total_items"],
            approval_metrics["approved"],
            approval_metrics["edited_and_approved"],
            approval_metrics["rejected"],
            approval_metrics["pending"]
        ]
        funnel_colors = ["#0F172A", "#10B981", "#0052FF", "#EF4444", "#F59E0B"]

        if sum(funnel_vals) > 0:
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_labels,
                x=funnel_vals,
                textinfo="value+percent initial",
                textfont=dict(family='Inter', size=11, color='#FFFFFF'),
                marker=dict(colors=funnel_colors)
            ))
            layout_f = get_plotly_minimalist_layout(height=320)
            layout_f["margin"] = dict(t=10, b=10, l=10, r=10)
            fig_funnel.update_layout(layout_f)
            st.plotly_chart(fig_funnel, use_container_width=True)
        else:
            render_empty_state("No Review Queue Data", "Governance funnel will populate as AI items are staged and reviewed.")

    st.markdown("<hr style='margin: 20px 0; border:0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Visualization Row 2: Owner Workload & Priority Breakdown
    c_w1, c_w2 = st.columns([7, 5])

    with c_w1:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:12px;'>Deliverable Workload by Owner</h3>", unsafe_allow_html=True)
        workload = get_owner_workload()
        if workload:
            df_work = pd.DataFrame(workload)
            fig_w = px.bar(
                df_work,
                y="owner",
                x=["completed", "in_progress", "blocked", "not_started"],
                orientation="h",
                labels={"value": "Task Count", "owner": "Owner", "variable": "Status"},
                color_discrete_map={
                    "completed": "#10B981",
                    "in_progress": "#0052FF",
                    "blocked": "#EF4444",
                    "not_started": "#94A3B8"
                }
            )
            layout_w = get_plotly_minimalist_layout(height=300)
            layout_w["yaxis"]["showgrid"] = False
            fig_w.update_layout(layout_w)
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            render_empty_state("No Owner Workload", "Workload distribution will appear when tasks are assigned to team members.")

    with c_w2:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:12px;'>Deliverables by Priority</h3>", unsafe_allow_html=True)
        p_dist = get_priority_distribution()
        if sum(p_dist.values()) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(p_dist.keys()),
                values=list(p_dist.values()),
                hole=0.58,
                marker_colors=["#EF4444", "#F59E0B", "#10B981"],
                textinfo="label+percent",
                textfont=dict(family='Inter', size=11)
            )])
            layout_pie = get_plotly_minimalist_layout(height=300)
            layout_pie["showlegend"] = True
            layout_pie["legend"] = dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(family='Inter', size=11)
            )
            fig_pie.update_layout(layout_pie)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            render_empty_state("No Priority Data", "Priority distribution will be computed from recorded tasks.")
