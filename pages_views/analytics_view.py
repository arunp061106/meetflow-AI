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
from utils.ui import render_page_header, render_workflow_indicator, render_empty_state

def render_analytics_page():
    render_page_header(
        title="Initiative & Operations Analytics",
        subtitle="Executive performance intelligence, delivery throughput, and human approval funnel analytics",
        badge_text="Portfolio Intelligence"
    )

    render_workflow_indicator("Analytics")

    # Fetch foundational metrics
    kpis = get_executive_kpis()
    approval_metrics = get_approval_acceptance_metrics()
    avg_completion_days = get_average_completion_time_days()

    # Top KPI Metrics Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Completion Rate", f"{kpis['completion_rate']}%", help="% of all tracked tasks completed")
    with c2:
        st.metric("Overdue Rate", f"{kpis['overdue_rate']}%", delta=f"{kpis['overdue_tasks']} tasks", delta_color="inverse", help="% of active tasks overdue")
    with c3:
        st.metric("Avg Turnaround", f"{avg_completion_days} days", help="Average turnaround time from creation to completion")
    with c4:
        st.metric("Blocked Tasks", f"{kpis['blocked_tasks']}", delta="Requires escalation" if kpis['blocked_tasks'] > 0 else "Clear", delta_color="inverse")
    with c5:
        st.metric("Approval Rate", f"{approval_metrics['acceptance_rate']}%", help="% of AI suggestions approved or edited & approved")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

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

    st.caption(f"Analyzing {len(filtered_tasks)} deliverable record(s) matching selected parameters.")
    st.markdown("<hr style='margin: 12px 0 20px 0; border:0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Visualization Row 1: Initiative Throughput & Approval Funnel
    col1, col2 = st.columns([7, 5])

    with col1:
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:12px;'>Initiative Throughput & Execution Status</div>", unsafe_allow_html=True)
        init_health = get_initiative_health_data()
        if init_health:
            df_init = pd.DataFrame(init_health)
            fig_init = go.Figure()
            fig_init.add_trace(go.Bar(
                name='Completed',
                x=df_init['initiative'],
                y=df_init['completed'],
                marker_color='#10b981'
            ))
            fig_init.add_trace(go.Bar(
                name='In Progress',
                x=df_init['initiative'],
                y=df_init['in_progress'],
                marker_color='#3b82f6'
            ))
            fig_init.add_trace(go.Bar(
                name='Blocked',
                x=df_init['initiative'],
                y=df_init['blocked'],
                marker_color='#ef4444'
            ))
            fig_init.update_layout(
                barmode='stack',
                margin=dict(t=10, b=30, l=10, r=10),
                height=320,
                xaxis=dict(showgrid=False, tickangle=-20),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family='Inter', size=11))
            )
            st.plotly_chart(fig_init, use_container_width=True)
        else:
            render_empty_state("No Initiative Data", "Initiative throughput will be charted once tasks are recorded.")

    with col2:
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:12px;'>Governance Approval Funnel</div>", unsafe_allow_html=True)
        funnel_labels = ["Extracted Candidates", "Approved As-Is", "Edited & Approved", "Rejected", "Pending Review"]
        funnel_vals = [
            approval_metrics["total_items"],
            approval_metrics["approved"],
            approval_metrics["edited_and_approved"],
            approval_metrics["rejected"],
            approval_metrics["pending"]
        ]
        funnel_colors = ["#475569", "#10b981", "#3b82f6", "#ef4444", "#f59e0b"]

        if sum(funnel_vals) > 0:
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_labels,
                x=funnel_vals,
                textinfo="value+percent initial",
                textfont=dict(family='Inter', size=11),
                marker=dict(colors=funnel_colors)
            ))
            fig_funnel.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=320,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
        else:
            render_empty_state("No Review Queue Data", "Governance funnel will populate as AI items are staged and reviewed.")

    st.markdown("<hr style='margin: 16px 0 24px 0; border:0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Visualization Row 2: Owner Workload & Priority Breakdown
    c_w1, c_w2 = st.columns([7, 5])

    with c_w1:
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:12px;'>Deliverable Workload by Owner</div>", unsafe_allow_html=True)
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
                    "completed": "#10b981",
                    "in_progress": "#3b82f6",
                    "blocked": "#ef4444",
                    "not_started": "#94a3b8"
                }
            )
            fig_w.update_layout(
                margin=dict(t=10, b=20, l=10, r=10),
                height=300,
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family='Inter', size=11))
            )
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            render_empty_state("No Owner Workload", "Workload distribution will appear when tasks are assigned to team members.")

    with c_w2:
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:12px;'>Deliverables by Priority</div>", unsafe_allow_html=True)
        p_dist = get_priority_distribution()
        if sum(p_dist.values()) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(p_dist.keys()),
                values=list(p_dist.values()),
                hole=0.55,
                marker_colors=["#ef4444", "#f59e0b", "#10b981"],
                textinfo="label+percent",
                textfont=dict(family='Inter', size=11)
            )])
            fig_pie.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(font=dict(family='Inter', size=11))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            render_empty_state("No Priority Data", "Priority distribution will be computed from recorded tasks.")
