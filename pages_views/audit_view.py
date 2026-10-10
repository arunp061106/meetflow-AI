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
    get_confidence_badge_html,
    render_custom_kpi_card
)

def render_lineage_item(item: dict):
    """Renders a single end-to-end data lineage pipeline card with Minimalist Modern styling."""
    review_id = item["review_id"]
    status = item["status"]
    is_edited = item["has_edits"]
    has_task = item["task_id"] is not None

    # Step 3 Decision Styling (Minimalist Palette)
    if status in ["Approved", "Edited & Approved"]:
        dec_badge_bg = "#ECFDF5"
        dec_badge_color = "#10B981"
        dec_badge_border = "#A7F3D0"
        dec_label = "AUTHORIZED"
    elif status == "Rejected":
        dec_badge_bg = "#FEF2F2"
        dec_badge_color = "#EF4444"
        dec_badge_border = "#FCA5A5"
        dec_label = "REJECTED"
    else:
        dec_badge_bg = "#FFFBEB"
        dec_badge_color = "#D97706"
        dec_badge_border = "#FDE68A"
        dec_label = "PENDING REVIEW"

    # Step 4 Official Tracker State
    if has_task:
        trk_badge_bg = "rgba(0,82,255,0.06)"
        trk_badge_color = "#0052FF"
        trk_badge_border = "rgba(0,82,255,0.25)"
        trk_label = f"Task #{item['task_id']} ({item['task_status']})"
        trk_subtext = "Live commitment in tracker"
    elif status == "Rejected":
        trk_badge_bg = "#F8FAFC"
        trk_badge_color = "#64748B"
        trk_badge_border = "#E2E8F0"
        trk_label = "Excluded from Tracker"
        trk_subtext = "Zero database task mutation"
    else:
        trk_badge_bg = "#FFFBEB"
        trk_badge_color = "#D97706"
        trk_badge_border = "#FDE68A"
        trk_label = "Awaiting Verification"
        trk_subtext = "Staged in candidate queue"

    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:20px 22px; margin-bottom:16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <!-- Card Header -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; border-bottom:1px solid #F1F5F9; padding-bottom:10px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-family:var(--font-mono); font-size:11px; font-weight:700; color:#0052FF; text-transform:uppercase; letter-spacing:0.06em; background:rgba(0,82,255,0.06); padding:3px 9px; border-radius:6px; border:1px solid rgba(0,82,255,0.2);">
                    CANDIDATE #{review_id}
                </span>
                <span style="font-size:13px; color:#0F172A; font-weight:600;">{item['meeting_title']}</span>
            </div>
            <div style="font-family:var(--font-mono); font-size:11px; color:#64748B;">
                Audit Log: <b>{item['reviewed_at'] or 'Pending Human Verification'}</b>
            </div>
        </div>

        <!-- 4-Stage Visual Lineage Pipeline -->
        <div style="display:grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; align-items:center; gap:8px; margin-bottom:14px;">
            
            <!-- Step 1: AI Extracted -->
            <div style="background:#FAFAFA; border:1px solid #E2E8F0; border-radius:10px; padding:12px; min-height:85px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:#0052FF; text-transform:uppercase; letter-spacing:0.06em;">1. AI INFERRED</span>
                    <span style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:#475569;">{item['ai_confidence']}% Conf.</span>
                </div>
                <div style="font-size:12px; font-weight:600; color:#0F172A; line-height:1.35;">
                    {item['ai_title'][:55]}{'...' if len(item['ai_title']) > 55 else ''}
                </div>
                <div style="font-size:11px; color:#64748B; margin-top:4px;">
                    Assignee: <b>{item['ai_owner']}</b> &bull; Prio: <b>{item['ai_priority']}</b>
                </div>
            </div>

            <!-- Arrow 1 -->
            <div style="font-size:16px; color:#94A3B8; font-weight:700; text-align:center;">&rarr;</div>

            <!-- Step 2: Human Verification / Edits -->
            <div style="background:{'#FFFBEB' if is_edited else '#FAFAFA'}; border:1px solid {'#FDE68A' if is_edited else '#E2E8F0'}; border-radius:10px; padding:12px; min-height:85px;">
                <div style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:{'#D97706' if is_edited else '#64748B'}; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">
                    2. HUMAN EDIT
                </div>
                <div style="font-size:12px; font-weight:600; color:#0F172A;">
                    {'Adjusted by Reviewer' if is_edited else 'Validated As-Is'}
                </div>
                <div style="font-size:11px; color:#64748B; margin-top:4px;">
                    {'Parameters updated before signoff' if is_edited else 'AI metadata accepted without changes'}
                </div>
            </div>

            <!-- Arrow 2 -->
            <div style="font-size:16px; color:#94A3B8; font-weight:700; text-align:center;">&rarr;</div>

            <!-- Step 3: Governance Gate Decision -->
            <div style="background:{dec_badge_bg}; border:1px solid {dec_badge_border}; border-radius:10px; padding:12px; min-height:85px;">
                <div style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:{dec_badge_color}; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">
                    3. GATE DECISION
                </div>
                <div style="font-size:12px; font-weight:700; color:{dec_badge_color};">
                    {dec_label}
                </div>
                <div style="font-size:11px; color:#64748B; margin-top:4px;">
                    {item['reviewer_action']}
                </div>
            </div>

            <!-- Arrow 3 -->
            <div style="font-size:16px; color:#94A3B8; font-weight:700; text-align:center;">&rarr;</div>

            <!-- Step 4: Official Tracker Record -->
            <div style="background:{trk_badge_bg}; border:1px solid {trk_badge_border}; border-radius:10px; padding:12px; min-height:85px;">
                <div style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:{trk_badge_color}; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">
                    4. TRACKER RECORD
                </div>
                <div style="font-size:12px; font-weight:700; color:{trk_badge_color};">
                    {trk_label}
                </div>
                <div style="font-size:11px; color:#64748B; margin-top:4px;">
                    {trk_subtext}
                </div>
            </div>
        </div>

        <!-- Evidence Citation & Audit Explanations -->
        <div style="background:#F8FAFC; border-left:3px solid #0052FF; border-radius:0 8px 8px 0; padding:10px 14px; margin-top:10px; font-size:12px; color:#334155;">
            <span style="font-family:var(--font-mono); font-weight:700; color:#0052FF; font-size:10px; text-transform:uppercase;">Verbatim Transcript Citation:</span>
            <span style="font-style:italic; margin-left:6px;">"{item['evidence']}"</span>
        </div>
        {f'''
        <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:12px; color:#92400E;">
            <b>Human Modification Diff:</b><br>
            <b>Before:</b> {item['before_edit'] or 'Original suggestion'}<br>
            <b>After:</b> {item['after_edit'] or item['ai_title']}
        </div>
        ''' if is_edited else ''}
        {f'''
        <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:12px; color:#B91C1C;">
            <b>Rejection Rationale:</b> {item['rejection_reason']}
        </div>
        ''' if item.get('rejection_reason') else ''}
    </div>
    """, unsafe_allow_html=True)


def render_audit_trail_page():
    render_page_header(
        title="Governance & Data Lineage Audit Trail",
        subtitle="End-to-end operational traceability: AI Generation → Human Verification → Authorization Decision → Official Tracker",
        badge_text="Data Lineage",
        highlight_word="Lineage"
    )

    render_workflow_indicator("Approval Queue")

    render_governance_banner()

    # Query persistent lineage records and telemetry from database
    lineage_records = get_full_lineage_audit_trail(limit=100)
    ai_metrics = get_ai_quality_metrics()

    # High-Level Governance Telemetry Summary
    summary_cols = st.columns(5)
    with summary_cols[0]:
        render_custom_kpi_card(
            label="Total Lineage",
            value=f"{len(lineage_records)}",
            subtext="Tracked pipeline items",
            badge_text="Audit Pool",
            badge_color="blue",
            is_featured=True
        )
    with summary_cols[1]:
        render_custom_kpi_card(
            label="Approved As-Is",
            value=f"{ai_metrics['approved']}",
            subtext="Direct model authorizations",
            badge_text="Direct Pass",
            badge_color="green"
        )
    with summary_cols[2]:
        render_custom_kpi_card(
            label="Edited & Approved",
            value=f"{ai_metrics['edited']}",
            subtext="Human refined before entry",
            badge_text="Supervised",
            badge_color="amber"
        )
    with summary_cols[3]:
        render_custom_kpi_card(
            label="Rejected",
            value=f"{ai_metrics['rejected']}",
            subtext="Blocked from entering tracker",
            badge_text="Dismissed",
            badge_color="red"
        )
    with summary_cols[4]:
        render_custom_kpi_card(
            label="Pending Review",
            value=f"{ai_metrics['pending']}",
            subtext="In review verification gate",
            badge_text="Staged",
            badge_color="neutral"
        )

    st.markdown("<hr style='margin: 20px 0 16px 0; border:0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

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

    st.markdown(f"<div style='font-family:var(--font-mono); font-size:12px; color:#64748B; margin: 4px 0 16px 0;'>Showing <b>{len(filtered_records)}</b> lineage path(s)</div>", unsafe_allow_html=True)

    if not filtered_records:
        render_empty_state("No Lineage Records Found", "No records matched your search or status filter criteria.")
        return

    # Render Lineage Pipeline
    for item in filtered_records:
        render_lineage_item(item)
