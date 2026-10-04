import streamlit as st
from datetime import datetime, date
from services.review_service import (
    get_review_queue_items,
    approve_review_item,
    edit_and_approve_review_item,
    reject_review_item,
    get_audit_logs
)
from services.meeting_service import get_all_initiatives, get_meeting_by_id
from utils.ui import (
    render_page_header,
    render_workflow_indicator,
    render_governance_banner,
    render_empty_state,
    get_confidence_badge_html,
    get_priority_badge_html,
    get_status_badge_html
)
from utils.dates import format_date_str

def render_approval_page():
    render_page_header(
        title="Human-in-the-Loop Deliverables Authorization",
        subtitle="Mandatory verification gate for AI-extracted commitments before official system recording",
        badge_text="Governance Gate"
    )

    render_workflow_indicator("Approval Queue")

    # Prominent Required Governance Banner
    render_governance_banner()

    tab_queue, tab_history = st.tabs(["Verification Queue", "Governance Audit Trail"])

    with tab_queue:
        # Search & Filter Controls
        filter_col, spacer_col = st.columns([4, 8])
        with filter_col:
            status_filter = st.selectbox(
                "Filter by Review Status",
                ["Pending", "Approved", "Edited & Approved", "Rejected", "All Records"],
                index=0
            )

        filter_arg = None if status_filter == "All Records" else status_filter
        items = get_review_queue_items(status_filter=filter_arg)

        initiatives = get_all_initiatives()
        initiative_names = [i["name"] for i in initiatives]

        # Active Queue Count
        st.markdown(f"<div style='font-size:13px; color:#475569; margin: 4px 0 16px 0;'>Showing <b>{len(items)}</b> candidate commitment(s)</div>", unsafe_allow_html=True)

        if not items:
            if status_filter == "Pending":
                render_empty_state(
                    title="Review Queue Cleared",
                    description="No action items are currently awaiting your authorization. All proposed commitments have been verified."
                )
            else:
                render_empty_state(
                    title="No Items Found",
                    description=f"There are currently no deliverables matching status '{status_filter}'."
                )
            return

        for item in items:
            item_id = item["id"]
            is_pending = (item["status"] == "Pending")
            
            with st.container():
                st.markdown(f"""
                <div class="approval-card">
                    <div class="approval-card-header">
                        <div>
                            <span style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em;">CANDIDATE #{item_id}</span>
                            <div class="approval-card-title">{item['title']}</div>
                        </div>
                        <div style="display:flex; gap:6px;">
                            {get_status_badge_html(item['status'])}
                            {get_priority_badge_html(item['priority'])}
                            {get_confidence_badge_html(item['confidence'])}
                        </div>
                    </div>
                    
                    <div class="approval-meta-grid">
                        <div>
                            <div class="meta-item-label">Proposed Owner</div>
                            <div class="meta-item-val">{item['owner']}</div>
                        </div>
                        <div>
                            <div class="meta-item-label">Target Deadline</div>
                            <div class="meta-item-val">{format_date_str(item['deadline'])}</div>
                        </div>
                        <div>
                            <div class="meta-item-label">Strategic Initiative</div>
                            <div class="meta-item-val">{item['initiative'] or 'General'}</div>
                        </div>
                        <div>
                            <div class="meta-item-label">Source Meeting</div>
                            <div class="meta-item-val">Meeting #{item['meeting_id'] or 'Unlinked'}</div>
                        </div>
                    </div>

                    <div style="font-size:13px; color:#334155; margin: 8px 0;">
                        {item['description'] or 'No supplemental notes provided.'}
                    </div>

                    <div class="evidence-dossier">
                        <div class="evidence-label">Verbatim Transcript Evidence</div>
                        <div class="evidence-text">"{item['evidence']}"</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if is_pending:
                    # Action Buttons
                    btn_approve_col, btn_edit_col, btn_reject_col = st.columns([3, 4, 3])
                    with btn_approve_col:
                        if st.button("Approve As-Is", key=f"appr_{item_id}", type="primary", use_container_width=True):
                            new_task_id = approve_review_item(item_id)
                            if new_task_id:
                                st.toast(f"Item #{item_id} authorized into Official Task #{new_task_id}")
                                st.rerun()

                    with btn_edit_col:
                        show_edit = st.checkbox("Edit Details Before Approving", key=f"edit_chk_{item_id}")

                    with btn_reject_col:
                        if st.button("Reject Item", key=f"rej_{item_id}", use_container_width=True):
                            if reject_review_item(item_id, reason="Declined during human verification"):
                                st.toast(f"Candidate #{item_id} rejected and archived")
                                st.rerun()

                    # Inline Edit Form
                    if show_edit:
                        st.markdown("<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:16px; margin: 10px 0;'>", unsafe_allow_html=True)
                        st.markdown("<div style='font-size:13px; font-weight:700; color:#0f172a; margin-bottom:10px;'>Adjust Deliverable Parameters:</div>", unsafe_allow_html=True)
                        with st.form(f"edit_form_{item_id}"):
                            new_title = st.text_input("Deliverable Title", value=item["title"])
                            new_desc = st.text_area("Scope & Acceptance Notes", value=item["description"] or "", height=70)
                            
                            col_owner, col_deadline, col_priority = st.columns(3)
                            with col_owner:
                                new_owner = st.text_input("Assigned Owner", value=item["owner"])
                            with col_deadline:
                                current_dl = None
                                if item["deadline"]:
                                    try:
                                        current_dl = datetime.strptime(str(item["deadline"])[:10], "%Y-%m-%d").date()
                                    except Exception:
                                        current_dl = None
                                new_deadline = st.date_input("Deadline", value=current_dl)
                            with col_priority:
                                prio_options = ["High", "Medium", "Low"]
                                prio_idx = prio_options.index(item["priority"]) if item["priority"] in prio_options else 1
                                new_prio = st.selectbox("Priority", prio_options, index=prio_idx)

                            init_idx = initiative_names.index(item["initiative"]) if item["initiative"] in initiative_names else 0
                            new_init = st.selectbox("Strategic Initiative", initiative_names if initiative_names else [item["initiative"] or "General"], index=init_idx)

                            confirm_btn = st.form_submit_button("Save Changes & Authorize", type="primary", use_container_width=True)
                            if confirm_btn:
                                task_id = edit_and_approve_review_item(
                                    item_id=item_id,
                                    title=new_title,
                                    description=new_desc,
                                    owner=new_owner,
                                    deadline=new_deadline,
                                    priority=new_prio,
                                    initiative=new_init
                                )
                                if task_id:
                                    st.toast(f"Candidate #{item_id} updated and authorized as Task #{task_id}")
                                    st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

                else:
                    st.caption(f"Reviewed on {item.get('reviewed_at', 'N/A')} &bull; Decision: <b>{item.get('reviewer_action', item['status'])}</b>")
                
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)


    with tab_history:
        from services.analytics_service import get_full_lineage_audit_trail
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:6px;'>Governance Lineage & Audit Trail</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px; color:#64748b; margin-bottom:14px;'>Traceability lifecycle: <b>AI Generated &rarr; Human Edited &rarr; Approved / Rejected &rarr; Official Tracker</b>.</div>", unsafe_allow_html=True)

        sub_tab1, sub_tab2 = st.tabs(["Visual Data Lineage Pipeline", "Raw Event Audit Logs"])

        with sub_tab1:
            lineage_items = get_full_lineage_audit_trail(limit=25)
            if not lineage_items:
                render_empty_state("No Lineage Data", "Lineage records will populate once reviews take place.")
            else:
                for item in lineage_items:
                    is_edited = item["has_edits"]
                    has_task = item["task_id"] is not None
                    status = item["status"]

                    dec_color = "#059669" if status in ["Approved", "Edited & Approved"] else ("#dc2626" if status == "Rejected" else "#b45309")
                    dec_bg = "#ecfdf5" if status in ["Approved", "Edited & Approved"] else ("#fef2f2" if status == "Rejected" else "#fffbeb")
                    dec_border = "#a7f3d0" if status in ["Approved", "Edited & Approved"] else ("#fecaca" if status == "Rejected" else "#fde68a")
                    dec_label = "AUTHORIZED" if status in ["Approved", "Edited & Approved"] else (status.upper())

                    trk_label = f"Task #{item['task_id']} ({item['task_status']})" if has_task else ("Not in Tracker" if status == "Rejected" else "Pending Review")

                    st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; margin-bottom:12px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span style="font-size:12px; font-weight:700; color:#0f172a;">#{item['review_id']}. {item['ai_title']}</span>
                            <span style="font-size:11px; color:#64748b;">Source: {item['meeting_title']} &bull; {item['reviewed_at'] or 'Pending'}</span>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; align-items:center; gap:6px; font-size:11px;">
                            <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:8px;">
                                <div style="font-weight:700; color:#2563eb;">1. AI GENERATED</div>
                                <div style="color:#64748b; margin-top:2px;">Conf: <b>{item['ai_confidence']}%</b></div>
                                <div style="color:#64748b;">Owner: <b>{item['ai_owner']}</b></div>
                            </div>
                            <div style="color:#94a3b8; font-weight:700; text-align:center;">&rarr;</div>
                            <div style="background:{'#fefce8' if is_edited else '#f8fafc'}; border:1px solid {'#fde047' if is_edited else '#e2e8f0'}; border-radius:4px; padding:8px;">
                                <div style="font-weight:700; color:{'#a16207' if is_edited else '#64748b'};">2. HUMAN EDIT</div>
                                <div style="color:#0f172a; margin-top:2px;">{'Modified by Reviewer' if is_edited else 'Validated As-Is'}</div>
                            </div>
                            <div style="color:#94a3b8; font-weight:700; text-align:center;">&rarr;</div>
                            <div style="background:{dec_bg}; border:1px solid {dec_border}; border-radius:4px; padding:8px;">
                                <div style="font-weight:700; color:{dec_color};">3. GATE DECISION</div>
                                <div style="color:{dec_color}; font-weight:700; margin-top:2px;">{dec_label}</div>
                            </div>
                            <div style="color:#94a3b8; font-weight:700; text-align:center;">&rarr;</div>
                            <div style="background:#f1f5f9; border:1px solid #e2e8f0; border-radius:4px; padding:8px;">
                                <div style="font-weight:700; color:#1e293b;">4. TRACKER</div>
                                <div style="color:#2563eb; font-weight:600; margin-top:2px;">{trk_label}</div>
                            </div>
                        </div>
                        {f"<div style='font-size:11px; color:#92400e; margin-top:6px; background:#fffbeb; padding:4px 8px; border-radius:4px;'><b>Diff:</b> Before: {item['before_edit']} | After: {item['after_edit']}</div>" if is_edited else ""}
                    </div>
                    """, unsafe_allow_html=True)

        with sub_tab2:
            logs = get_audit_logs(limit=50)
            if not logs:
                render_empty_state("No Audit Records", "Governance decisions will be catalogued here as reviews are conducted.")
            else:
                for l in logs:
                    action_color = "#059669" if "APPROV" in l["action"] else ("#dc2626" if "REJECT" in l["action"] else "#2563eb")
                    st.markdown(f"""
                    <div style="background:#ffffff; border-left:3px solid {action_color}; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; border-radius:6px; padding:12px 16px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; color:#0f172a; font-size:13px;">
                                {l['action']} &bull; {l['entity_type'].upper()} #{l['entity_id']}
                            </span>
                            <span style="font-size:11px; color:#64748b;">{l['timestamp']}</span>
                        </div>
                        <div style="font-size:12px; color:#334155; margin-top:4px;">
                            <b>Record:</b> {l['new_value']}
                        </div>
                        {f"<div style='font-size:11px; color:#64748b; margin-top:2px;'><b>Previous State:</b> {l['old_value']}</div>" if l['old_value'] else ""}
                    </div>
                    """, unsafe_allow_html=True)

