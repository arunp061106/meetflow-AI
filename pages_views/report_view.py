import streamlit as st
from services.report_service import generate_weekly_report
from utils.ui import render_page_header, render_workflow_indicator, render_custom_kpi_card

def render_report_page():
    render_page_header(
        title="Executive Weekly Status Report",
        subtitle="Automated synthesis of strategic milestones, deliverable progress, operational blockers, and executive escalations",
        badge_text="Executive Briefing",
        highlight_word="Report"
    )

    render_workflow_indicator("Weekly Report")

    col_ctrl1, col_ctrl2 = st.columns([8, 4])
    with col_ctrl1:
        st.markdown("<div style='font-size:13px; color:#64748B; padding-top:6px;'>Synthesized directly from persistent task progress, meeting decisions, and overdue workstreams.</div>", unsafe_allow_html=True)
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

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

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

    st.markdown("<hr style='margin: 20px 0 24px 0; border:0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Render Preview
    tab_view, tab_source = st.tabs(["Briefing Document Preview", "Markdown Source Code"])

    with tab_view:
        # Display Key Summary Cards
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            render_custom_kpi_card(
                label="Reporting Period",
                value=report["period_str"].split(" to ")[0][-5:] + " - " + report["period_str"].split(" to ")[1][-5:],
                subtext="Evaluation cycle",
                badge_text="Cycle",
                badge_color="blue",
                is_featured=False
            )
        with k2:
            render_custom_kpi_card(
                label="Delivered",
                value=f"{report['completed_count']}",
                subtext="Completed tasks in cycle",
                badge_text="Shipped",
                badge_color="green",
                is_featured=True
            )
        with k3:
            render_custom_kpi_card(
                label="In Progress",
                value=f"{report['in_progress_count']}",
                subtext="Active commitments",
                badge_text="In Flight",
                badge_color="blue"
            )
        with k4:
            render_custom_kpi_card(
                label="Overdue",
                value=f"{report['overdue_count']}",
                subtext="Action required",
                badge_text="Critical" if report['overdue_count'] > 0 else "Clean",
                badge_color="red" if report['overdue_count'] > 0 else "green"
            )
        with k5:
            render_custom_kpi_card(
                label="Blocked",
                value=f"{report['blocked_count']}",
                subtext="Dependencies pending",
                badge_text="Action" if report['blocked_count'] > 0 else "Clear",
                badge_color="amber" if report['blocked_count'] > 0 else "neutral"
            )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        # Render markdown content inside an elevated card container
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:24px 28px; box-shadow:0 2px 4px rgba(0,0,0,0.02); line-height:1.6;">
            {report['markdown']}
        </div>
        """, unsafe_allow_html=True)

    with tab_source:
        st.code(report["markdown"], language="markdown")
