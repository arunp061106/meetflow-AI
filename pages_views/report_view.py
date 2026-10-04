import streamlit as st
from services.report_service import generate_weekly_report
from utils.ui import render_page_header, render_workflow_indicator

def render_report_page():
    render_page_header(
        title="Executive Weekly Status Report",
        subtitle="Automated synthesis of strategic milestones, deliverable progress, operational blockers, and executive escalations",
        badge_text="Executive Briefing"
    )

    render_workflow_indicator("Weekly Report")

    col_ctrl1, col_ctrl2 = st.columns([8, 4])
    with col_ctrl1:
        st.markdown("<div style='font-size:13px; color:#475569; padding-top:4px;'>Synthesized directly from persistent task progress, meeting decisions, and overdue workstreams.</div>", unsafe_allow_html=True)
    with col_ctrl2:
        days_back = st.selectbox("Lookback Window", [7, 14, 30], index=0, format_func=lambda x: f"Last {x} calendar days", label_visibility="collapsed")

    if st.button("Synthesize & Refresh Report", type="primary"):
        with st.spinner("Synthesizing portfolio metrics and generating executive narrative..."):
            report_data = generate_weekly_report(days_back=days_back)
            st.session_state["cached_report"] = report_data
            st.toast("Executive briefing successfully compiled.")

    # Load report from state or generate on first load
    if "cached_report" not in st.session_state:
        st.session_state["cached_report"] = generate_weekly_report(days_back=days_back)

    report = st.session_state["cached_report"]

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Download Buttons Toolbar
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            label="Download Markdown (.md)",
            data=report["markdown"],
            file_name=f"meetflow_weekly_report_{report['period_str'].replace(' to ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with d2:
        st.download_button(
            label="Export Deliverables (.csv)",
            data=report["csv"],
            file_name=f"meetflow_tasks_export_{report['period_str'].replace(' to ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d3:
        st.download_button(
            label="Download Briefing Document (.html)",
            data=report["html"],
            file_name=f"meetflow_executive_briefing_{report['period_str'].replace(' to ', '_')}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("<hr style='margin: 16px 0 20px 0; border:0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Render Preview
    tab_view, tab_source = st.tabs(["Briefing Document Preview", "Markdown Source Code"])

    with tab_view:
        # Display Key Summary Cards
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric("Reporting Period", report["period_str"].split(" to ")[0][-5:] + " - " + report["period_str"].split(" to ")[1][-5:])
        with k2:
            st.metric("Delivered In Cycle", f"{report['completed_count']}")
        with k3:
            st.metric("Active Workstreams", f"{report['in_progress_count']}")
        with k4:
            st.metric("Overdue Escalations", f"{report['overdue_count']}", delta="Action needed" if report['overdue_count'] > 0 else None, delta_color="inverse")
        with k5:
            st.metric("Blocked Items", f"{report['blocked_count']}", delta="Escalated" if report['blocked_count'] > 0 else None, delta_color="inverse")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        # Render markdown content
        st.markdown(report["markdown"])

    with tab_source:
        st.code(report["markdown"], language="markdown")
