import streamlit as st
from datetime import datetime, date
import pandas as pd
from services.task_service import (
    get_all_tasks,
    update_task_status,
    update_task_details,
    create_task_manually
)
from services.meeting_service import get_all_initiatives
from utils.ui import (
    render_page_header,
    render_workflow_indicator,
    get_status_badge_html,
    get_priority_badge_html,
    render_empty_state
)
from utils.dates import format_date_str, get_relative_deadline_str

def render_tracker_page():
    render_page_header(
        title="Official Initiative & Deliverable Tracker",
        subtitle="Persistent system of record for authorized action items, operational owners, and delivery status",
        badge_text="System of Record",
        highlight_word="Tracker"
    )

    render_workflow_indicator("Initiative Tracker")

    tab_tracker, tab_manual = st.tabs(["Active Deliverables", "Log Manual Task"])

    initiatives = get_all_initiatives()
    initiative_names = [i["name"] for i in initiatives]

    with tab_manual:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:6px;'>Create Authorized Task Directly</h3>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px; color:#64748B; margin-bottom:18px;'>Manual creation bypasses AI extraction while preserving complete audit logging and governance accountability.</div>", unsafe_allow_html=True)

        with st.form("manual_task_form", clear_on_submit=True):
            title_col, owner_col = st.columns([7, 5])
            with title_col:
                title = st.text_input("Deliverable Title*", placeholder="e.g. Conduct latency benchmark on ingest API")
            with owner_col:
                owner = st.text_input("Assigned Owner*", placeholder="e.g. Sarah Chen")

            init_col, prio_col, deadline_col = st.columns(3)
            with init_col:
                initiative = st.selectbox("Strategic Initiative", initiative_names if initiative_names else ["General"])
            with prio_col:
                priority = st.selectbox("Priority Level", ["High", "Medium", "Low"], index=1)
            with deadline_col:
                deadline = st.date_input("Target Deadline", value=None)

            description = st.text_area("Scope & Acceptance Criteria", placeholder="Provide context, acceptance criteria, or relevant technical links...")

            submit_btn = st.form_submit_button("Record Task in Tracker", type="primary", use_container_width=True)
            if submit_btn:
                if not title.strip() or not owner.strip():
                    st.error("Please provide both a Title and an Owner.")
                else:
                    new_id = create_task_manually(
                        title=title,
                        description=description,
                        owner=owner,
                        deadline=deadline,
                        priority=priority,
                        initiative=initiative
                    )
                    st.success(f"Official Task #{new_id} recorded in persistent tracker.")
                    st.rerun()

    with tab_tracker:
        # Search & Filter Controls
        col_init, col_status, col_prio, col_search = st.columns([3, 3, 2, 4])
        with col_init:
            init_filter = st.selectbox("Filter Initiative", ["All Initiatives"] + initiative_names)
        with col_status:
            status_filter = st.selectbox("Filter Status", ["All Statuses", "Overdue", "In Progress", "Blocked", "Not Started", "Completed"])
        with col_prio:
            prio_filter = st.selectbox("Priority", ["All Priorities", "High", "Medium", "Low"])
        with col_search:
            search_query = st.text_input("Search Deliverables", placeholder="Search title, owner, or keyword...")

        tasks = get_all_tasks(
            initiative=None if init_filter == "All Initiatives" else init_filter,
            priority=None if prio_filter == "All Priorities" else prio_filter,
            status=None if status_filter == "All Statuses" else status_filter,
            search_query=search_query
        )

        # Overview Telemetry
        total_count = len(tasks)
        overdue_count = sum(1 for t in tasks if t["is_overdue"])
        completed_count = sum(1 for t in tasks if t["status"] == "Completed")
        in_progress_count = sum(1 for t in tasks if t["status"] == "In Progress")
        blocked_count = sum(1 for t in tasks if t["status"] == "Blocked")

        stat_cols = st.columns(5)
        with stat_cols[0]:
            st.metric("Total Filtered", total_count)
        with stat_cols[1]:
            st.metric("In Progress", in_progress_count)
        with stat_cols[2]:
            st.metric("Completed", completed_count)
        with stat_cols[3]:
            st.metric("Blocked", blocked_count, delta="Requires action" if blocked_count > 0 else None, delta_color="inverse")
        with stat_cols[4]:
            st.metric("Overdue", overdue_count, delta="Escalate" if overdue_count > 0 else None, delta_color="inverse")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        if not tasks:
            render_empty_state("No Tasks Match Active Filters", "Adjust your search filters or create new tasks to populate the tracker.")
            return

        # Render Task Cards
        for task in tasks:
            task_id = task["id"]
            is_overdue = task["is_overdue"]

            border_accent = "border-left: 4px solid #EF4444;" if is_overdue else ("border-left: 4px solid #10B981;" if task["status"] == "Completed" else "border-left: 4px solid #0052FF;")

            with st.container():
                st.markdown(f"""
                <div style="background:#FFFFFF; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0; {border_accent} border-radius:12px; padding:18px 20px; margin-bottom:12px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <span style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:#0052FF; text-transform:uppercase; letter-spacing:0.06em;">TASK #{task_id}</span>
                            <div style="font-size:15px; font-weight:600; color:#0F172A; margin-top:2px;">{task['title']}</div>
                            <div style="font-size:12px; color:#64748B; margin:4px 0 6px 0;">
                                Owner: <b>{task['owner']}</b> &bull; 
                                Initiative: <b>{task['initiative']}</b> &bull; 
                                Target: <b>{format_date_str(task['deadline'])}</b> ({get_relative_deadline_str(task['deadline'], task['status'])}) &bull;
                                Source: {task['meeting_title']}
                            </div>
                        </div>
                        <div style="display:flex; gap:6px;">
                            {get_status_badge_html(task['status'], is_overdue)}
                            {get_priority_badge_html(task['priority'])}
                        </div>
                    </div>
                    {f"<div style='font-size:13px; color:#334155; margin-top:6px; line-height:1.45;'>{task['description']}</div>" if task['description'] else ""}
                </div>
                """, unsafe_allow_html=True)

                col_stat_toggle, col_edit_toggle = st.columns([7, 5])
                with col_stat_toggle:
                    current_status = task["status"]
                    status_choices = ["Not Started", "In Progress", "Blocked", "Completed"]
                    idx_current = status_choices.index(current_status) if current_status in status_choices else 0
                    
                    new_status = st.selectbox(
                        "Status Transition",
                        options=status_choices,
                        index=idx_current,
                        key=f"status_sel_{task_id}",
                        label_visibility="collapsed"
                    )
                    if new_status != current_status:
                        update_task_status(task_id, new_status)
                        st.toast(f"Task #{task_id} moved to {new_status}")
                        st.rerun()

                with col_edit_toggle:
                    show_edit_drawer = st.checkbox("Edit Details", key=f"edit_drawer_{task_id}")

                if show_edit_drawer:
                    st.markdown("<div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:18px; margin-top:10px; box-shadow:0 4px 12px rgba(0,0,0,0.03);'>", unsafe_allow_html=True)
                    st.markdown("<h4 class='calistoga-heading' style='font-size:15px; margin-bottom:12px;'>Edit Task Details</h4>", unsafe_allow_html=True)
                    with st.form(f"edit_task_form_{task_id}"):
                        edit_title = st.text_input("Title", value=task["title"])
                        edit_desc = st.text_area("Scope & Details", value=task["description"] or "", height=70)
                        
                        edit_col1, edit_col2, edit_col3 = st.columns(3)
                        with edit_col1:
                            edit_owner = st.text_input("Owner", value=task["owner"])
                        with edit_col2:
                            curr_deadline = None
                            if task["deadline"]:
                                try:
                                    curr_deadline = datetime.strptime(str(task["deadline"])[:10], "%Y-%m-%d").date()
                                except Exception:
                                    curr_deadline = None
                            edit_deadline = st.date_input("Deadline", value=curr_deadline)
                        with edit_col3:
                            prio_opts = ["High", "Medium", "Low"]
                            edit_prio = st.selectbox("Priority", prio_opts, index=prio_opts.index(task["priority"]) if task["priority"] in prio_opts else 1)

                        init_opts = initiative_names if initiative_names else [task["initiative"]]
                        init_curr_idx = init_opts.index(task["initiative"]) if task["initiative"] in init_opts else 0
                        edit_init = st.selectbox("Strategic Initiative", init_opts, index=init_curr_idx)

                        status_opts = ["Not Started", "In Progress", "Blocked", "Completed"]
                        status_curr_idx = status_opts.index(task["status"]) if task["status"] in status_opts else 0
                        edit_status = st.selectbox("Status", status_opts, index=status_curr_idx)

                        save_btn = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                        if save_btn:
                            update_task_details(
                                task_id=task_id,
                                title=edit_title,
                                description=edit_desc,
                                owner=edit_owner,
                                deadline=edit_deadline,
                                priority=edit_prio,
                                initiative=edit_init,
                                status=edit_status
                            )
                            st.toast(f"Task #{task_id} parameters saved")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
