import streamlit as st
import pandas as pd
from services.analytics_service import get_full_lineage_audit_trail, get_ai_quality_metrics
from utils.ui import (
    render_page_header,
    render_workflow_indicator,
    render_governance_banner,
    render_empty_state,
    get_status_badge_html,
    get_priority_badge_html,
    get_confidence_badge_html
)

def render_lineage_item(item: dict):
    """Renders a single end-to-end data lineage pipeline card."""
    review_id = item["review_id"]
    status = item["status"]
    is_edited = item["has_edits"]
    has_task = item["task_id"] is not None

    # Step 3 Decision Styling
    if status in ["Approved", "Edited & Approved"]:
        dec_badge_bg = "#ecfdf5"
        dec_badge_color = "#059669"
        dec_badge_border = "#a7f3d0"
        dec_label = "AUTHORIZED"
    elif status == "Rejected":
        dec_badge_bg = "#fef2f2"
        dec_badge_color = "#dc2626"
        dec_badge_border = "#fecaca"
        dec_label = "REJECTED"
    else:
        dec_badge_bg = "#fffbeb"
        dec_badge_color = "#b45309"
        dec_badge_border = "#fde68a"
        dec_label = "PENDING REVIEW"

    # Step 4 Official Tracker State
    if has_task:
        trk_badge_bg = "#eff6ff"
        trk_badge_color = "#1d4ed8"
        trk_badge_border = "#bfdbfe"
        trk_label = f"Task #{item['task_id']} ({item['task_status']})"
        trk_subtext = "Live commitment in initiative tracker"
    elif status == "Rejected":
        trk_badge_bg = "#f8fafc"
        trk_badge_color = "#94a3b8"
        trk_badge_border = "#e2e8f0"
        trk_label = "Excluded from Tracker"
        trk_subtext = "Zero database task mutation"
    else:
        trk_badge_bg = "#fffbeb"
        trk_badge_color = "#b45309"
        trk_badge_border = "#fde68a"
        trk_label = "Awaiting Verification"
        trk_subtext = "Staged in candidate queue"

    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px 20px; margin-bottom:16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
        <!-- Card Header -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; border-bottom:1px solid #f1f5f9; padding-bottom:8px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.04em;">CANDIDATE #{review_id}</span>
                <span style="font-size:12px; color:#475569;">Source: <b>{item['meeting_title']}</b></span>
            </div>
            <div style="font-size:11px; color:#64748b;">
                Audit Log: <b>{item['reviewed_at'] or 'Pending Human Verification'}</b>
            </div>
        </div>

        <!-- 4-Stage Visual Lineage Pipeline -->
        <div style="display:grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; align-items:center; gap:8px; margin-bottom:14px;">
            
            <!-- Step 1: AI Extracted -->
            <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:10px 12px; min-height:85px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:10px; font-weight:700; color:#3b82f6; text-transform:uppercase; letter-spacing:0.04em;">1. AI INFERRED</span>
                    <span style="font-size:10px; font-weight:700; color:#475569;">{item['ai_confidence']}% Conf.</span>
                </div>
                <div style="font-size:12px; font-weight:600; color:#0f172a; line-height:1.3;">
                    {item['ai_title'][:55]}{'...' if len(item['ai_title']) > 55 else ''}
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">
                    Assignee: <b>{item['ai_owner']}</b> &bull; Prio: <b>{item['ai_priority']}</b>
                </div>
            </div>

            <!-- Arrow 1 -->
            <div style="font-size:16px; color:#94a3b8; font-weight:700; text-align:center;">&rarr;</div>

            <!-- Step 2: Human Verification / Edits -->
            <div style="background:{'#fefce8' if is_edited else '#f8fafc'}; border:1px solid {'#fde047' if is_edited else '#e2e8f0'}; border-radius:6px; padding:10px 12px; min-height:85px;">
                <div style="font-size:10px; font-weight:700; color:{'#a16207' if is_edited else '#64748b'}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">
                    2. HUMAN EDIT
                </div>
                <div style="font-size:12px; font-weight:600; color:#0f172a;">
                    {'Adjusted by Reviewer' if is_edited else 'Validated As-Is'}
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">
                    {'Parameters updated before signoff' if is_edited else 'AI metadata accepted without changes'}
                </div>
            </div>

            <!-- Arrow 2 -->
            <div style="font-size:16px; color:#94a3b8; font-weight:700; text-align:center;">&rarr;</div>

            <!-- Step 3: Governance Gate Decision -->
            <div style="background:{dec_badge_bg}; border:1px solid {dec_badge_border}; border-radius:6px; padding:10px 12px; min-height:85px;">
                <div style="font-size:10px; font-weight:700; color:{dec_badge_color}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">
                    3. GATE DECISION
                </div>
                <div style="font-size:12px; font-weight:700; color:{dec_badge_color};">
                    {dec_label}
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">
                    {item['reviewer_action']}
                </div>
            </div>

            <!-- Arrow 3 -->
            <div style="font-size:16px; color:#94a3b8; font-weight:700; text-align:center;">&rarr;</div>

            <!-- Step 4: Official Tracker Record -->
            <div style="background:{trk_badge_bg}; border:1px solid {trk_badge_border}; border-radius:6px; padding:10px 12px; min-height:85px;">
                <div style="font-size:10px; font-weight:700; color:{trk_badge_color}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">
                    4. TRACKER RECORD
                </div>
                <div style="font-size:12px; font-weight:700; color:{trk_badge_color};">
                    {trk_label}
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">
                    {trk_subtext}
                </div>
            </div>
        </div>

        <!-- Evidence Citation & Audit Explanations -->
        <div style="background:#f1f5f9; border-radius:6px; padding:8px 12px; margin-top:10px; font-size:12px; color:#334155;">
            <span style="font-weight:700; color:#475569;">Verbatim Transcript Citation:</span>
            <span style="font-style:italic;">"{item['evidence']}"</span>
        </div>
        {f'''
        <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:6px; padding:8px 12px; margin-top:8px; font-size:12px; color:#92400e;">
            <b>Human Modification Diff:</b><br>
            <b>Before:</b> {item['before_edit'] or 'Original suggestion'}<br>
            <b>After:</b> {item['after_edit'] or item['ai_title']}
        </div>
        ''' if is_edited else ''}
        {f'''
        <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:8px 12px; margin-top:8px; font-size:12px; color:#991b1b;">
            <b>Rejection Rationale:</b> {item['rejection_reason']}
        </div>
        ''' if item.get('rejection_reason') else ''}
    </div>
    """, unsafe_allow_html=True)


def render_audit_trail_page():
    render_page_header(
        title="Governance & Data Lineage Audit Trail",
        subtitle="End-to-end operational traceability: AI Generation → Human Verification → Authorization Decision → Official Tracker",
        badge_text="Data Lineage"
    )

    render_workflow_indicator("Approval Queue")

    render_governance_banner()

    # Query persistent lineage records and telemetry from database
    lineage_records = get_full_lineage_audit_trail(limit=100)
    ai_metrics = get_ai_quality_metrics()

    # High-Level Governance Telemetry Summary
    summary_cols = st.columns(5)
    with summary_cols[0]:
        st.metric("Total Lineage Records", f"{len(lineage_records)}", help="Total records tracked from meeting extraction through review")
    with summary_cols[1]:
        st.metric("Approved As-Is", f"{ai_metrics['approved']}", help="AI candidates authorized without human changes")
    with summary_cols[2]:
        st.metric("Human-Edited & Approved", f"{ai_metrics['edited']}", help="AI candidates modified by reviewers prior to tracker entry")
    with summary_cols[3]:
        st.metric("Rejected / Filtered", f"{ai_metrics['rejected']}", help="AI candidates flagged as noise or out of scope")
    with summary_cols[4]:
        st.metric("Pending Authorization", f"{ai_metrics['pending']}", help="Candidates currently staged in review queue")

    st.markdown("<hr style='margin: 18px 0 16px 0; border:0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Filtering, Search, and Compliance Export Toolbar
    filter_col, search_col, export_col = st.columns([4, 5, 3])
    with filter_col:
        status_choice = st.selectbox(
            "Filter by Governance Gate Decision",
            ["All Records", "Approved", "Edited & Approved", "Rejected", "Pending"],
            index=0
        )
    with search_col:
        search_query = st.text_input("Search Title, Evidence, Owner, or Initiative", placeholder="e.g., Snowflake, Elena, GDPR, Churn...")
    with export_col:
        if lineage_records:
            df_export = pd.DataFrame([{
                "Review_ID": record["review_id"],
                "Meeting": record["meeting_title"],
                "AI_Title": record["ai_title"],
                "AI_Owner": record["ai_owner"],
                "AI_Deadline": record["ai_deadline"],
                "AI_Priority": record["ai_priority"],
                "AI_Confidence": f"{record['ai_confidence']}%",
                "Human_Edited": "YES" if record["has_edits"] else "NO",
                "Decision": record["status"],
                "Reviewed_At": record["reviewed_at"] or "Pending",
                "Tracker_Task_ID": record["task_id"] or "N/A",
                "Tracker_Task_Status": record["task_status"] or "N/A",
                "Verbatim_Evidence": record["evidence"]
            } for record in lineage_records])
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Export Lineage CSV",
                data=csv_data,
                file_name="meetflow_governance_lineage_audit.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Filter Pipeline Records
    filtered_records = lineage_records
    if status_choice != "All Records":
        filtered_records = [record for record in filtered_records if record["status"] == status_choice]

    if search_query.strip():
        query_text = search_query.strip().lower()
        filtered_records = [
            record for record in filtered_records if (
                query_text in record["ai_title"].lower() or
                query_text in record["ai_owner"].lower() or
                query_text in record["evidence"].lower() or
                query_text in (record.get("meeting_title") or "").lower() or
                query_text in (record.get("task_title") or "").lower()
            )
        ]

    st.markdown(f"<div style='font-size:13px; color:#475569; margin: 4px 0 16px 0;'>Showing <b>{len(filtered_records)}</b> lineage path(s)</div>", unsafe_allow_html=True)

    if not filtered_records:
        render_empty_state("No Lineage Records Found", "No records matched your search or status filter criteria.")
        return

    # Render Lineage Pipeline
    for item in filtered_records:
        render_lineage_item(item)
