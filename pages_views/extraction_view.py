import streamlit as st
import json
from services.meeting_service import get_all_meetings, get_meeting_by_id, update_meeting_summary
from services.review_service import add_extraction_to_review_queue
from ai.extractor import extract_meeting_intelligence, get_ai_config
from utils.ui import (
    render_page_header,
    render_workflow_indicator,
    get_confidence_badge_html,
    get_priority_badge_html
)

def render_extraction_page():
    render_page_header(
        title="AI Action Item & Intelligence Extraction",
        subtitle="Automated extraction of commitments, owners, deadlines, and verbatim evidence quotes",
        badge_text="Inference Engine"
    )

    render_workflow_indicator("AI Extraction")

    ai_config = get_ai_config()
    if ai_config["is_demo_mode"]:
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:10px 14px; margin-bottom:18px; font-size:12px; color:#475569;">
            <b style="color:#0f172a;">Engine Mode:</b> Offline Deterministic Demo Engine. Operates without requiring an external API key.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:10px 14px; margin-bottom:18px; font-size:12px; color:#475569;">
            <b style="color:#0f172a;">Engine Mode:</b> Live LLM Provider Connected (<code>{ai_config['model_name']}</code>).
        </div>
        """, unsafe_allow_html=True)

    meetings = get_all_meetings()
    meeting_titles = ["-- Custom / Standalone Discussion Notes --"] + [f"Meeting #{m['id']}: {m['title']} ({m['meeting_date']})" for m in meetings]

    # Pre-selection from Meetings page if navigated here
    preselected_id = st.session_state.get("extract_meeting_id")
    default_idx = 0
    if preselected_id:
        for idx, m in enumerate(meetings, start=1):
            if m["id"] == preselected_id:
                default_idx = idx
                break

    selected_meeting_option = st.selectbox(
        "Source Meeting Record",
        options=meeting_titles,
        index=default_idx
    )

    selected_meeting_id = None
    default_transcript = st.session_state.get("extract_transcript", "")
    default_title = st.session_state.get("extract_title", "")
    default_initiative = st.session_state.get("extract_initiative", "General")

    if selected_meeting_option != "-- Custom / Standalone Discussion Notes --":
        m_id_str = selected_meeting_option.split(":")[0].replace("Meeting #", "").strip()
        selected_meeting_id = int(m_id_str)
        m_obj = get_meeting_by_id(selected_meeting_id)
        if m_obj:
            default_transcript = m_obj.get("transcript") or ""
            default_title = m_obj.get("title") or ""
            default_initiative = m_obj.get("initiative") or "General"

    col_meta1, col_meta2 = st.columns([7, 5])
    with col_meta1:
        meeting_title_input = st.text_input("Meeting Reference Title", value=default_title, placeholder="e.g. Sprint 34 Architecture Review")
    with col_meta2:
        initiative_input = st.text_input("Strategic Initiative Context", value=default_initiative, placeholder="e.g. Customer Analytics Platform")

    # File upload option
    uploaded_file = st.file_uploader("Upload Meeting Transcript (.txt, .md)", type=["txt", "md"], key="extract_file_uploader")
    if uploaded_file is not None:
        try:
            default_transcript = uploaded_file.read().decode("utf-8")
            st.info(f"Loaded {len(default_transcript)} characters from uploaded file.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    transcript_input = st.text_area(
        "Meeting Transcript & Notes Content*",
        value=default_transcript,
        height=220,
        placeholder="Paste discussion notes, speaker dialogues, or raw meeting transcript..."
    )

    col_btn, col_info = st.columns([4, 8])
    with col_btn:
        extract_button = st.button("Extract Action Items", type="primary", use_container_width=True)
    with col_info:
        st.markdown("<div style='font-size:12px; color:#64748b; padding-top:6px;'>Inferred tasks are staged in the Approval Queue with verbatim evidence. AI suggestions are never committed automatically.</div>", unsafe_allow_html=True)

    if extract_button:
        if not transcript_input or not transcript_input.strip():
            st.error("Please provide transcript content before executing extraction.")
        else:
            with st.spinner("Extracting commitments, owners, and evidence using intelligence engine..."):
                extraction_result, is_demo, message = extract_meeting_intelligence(
                    transcript=transcript_input,
                    meeting_title=meeting_title_input,
                    initiative_hint=initiative_input
                )

            if not extraction_result:
                st.error(f"Extraction failed: {message}")
            else:
                st.session_state["latest_extraction"] = extraction_result
                st.session_state["latest_extraction_message"] = message
                st.session_state["latest_extraction_is_demo"] = is_demo

                # Push to Review Queue (NOT tasks table!)
                created_ids, dup_count = add_extraction_to_review_queue(
                    meeting_id=selected_meeting_id,
                    extraction=extraction_result,
                    raw_json_str=extraction_result.model_dump_json()
                )

                # Update meeting summary if linked
                if selected_meeting_id and extraction_result.meeting_summary:
                    update_meeting_summary(selected_meeting_id, extraction_result.meeting_summary)

                st.session_state["last_extracted_count"] = len(created_ids)
                st.session_state["last_duplicate_count"] = dup_count

    # Display Extracted Intelligence if present
    if "latest_extraction" in st.session_state:
        ext = st.session_state["latest_extraction"]
        msg = st.session_state.get("latest_extraction_message", "")
        count = st.session_state.get("last_extracted_count", len(ext.action_items))
        dup_count = st.session_state.get("last_duplicate_count", 0)

        st.markdown("<hr style='margin: 24px 0 16px 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.success(f"{msg}")
        if dup_count > 0:
            st.info(f"{dup_count} duplicate item(s) already existed in the review queue and were skipped.")

        # Governance Staging Box
        st.markdown(f"""
        <div style="background:#ffffff; border-left:4px solid #2563eb; border-top:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; border-radius:6px; padding:14px 18px; margin-bottom:18px;">
            <div style="font-weight:700; color:#0f172a; font-size:14px; margin-bottom:4px;">
                Human Verification Gate: {count} Action Item(s) Staged in Review Queue
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.5;">
                <b>AI suggestions are never committed automatically. Every action item requires human verification.</b>
                Please review, modify, or authorize these items in the Approval Queue before they enter official initiative tracking.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Approval Queue →", type="primary"):
            st.session_state["nav_selection"] = "Approval Queue"
            st.rerun()

        # Display Meeting Synthesis
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("<div style='font-size:14px; font-weight:700; color:#0f172a; margin-bottom:6px;'>Executive Summary</div>", unsafe_allow_html=True)
            st.info(ext.meeting_summary)

            st.markdown("<div style='font-size:14px; font-weight:700; color:#0f172a; margin: 12px 0 6px 0;'>Key Decisions</div>", unsafe_allow_html=True)
            if ext.decisions:
                for d in ext.decisions:
                    st.markdown(f"- {d}")
            else:
                st.caption("No explicit strategic decisions recorded.")

        with col_s2:
            st.markdown("<div style='font-size:14px; font-weight:700; color:#0f172a; margin-bottom:6px;'>Identified Risks & Blockers</div>", unsafe_allow_html=True)
            if ext.risks or ext.blockers:
                for r in ext.risks:
                    st.markdown(f"- **Risk:** {r}")
                for b in ext.blockers:
                    st.markdown(f"- **Blocker:** {b}")
            else:
                st.caption("No critical operational risks or blockers detected.")

            st.markdown("<div style='font-size:14px; font-weight:700; color:#0f172a; margin: 12px 0 6px 0;'>Milestone Next Steps</div>", unsafe_allow_html=True)
            if ext.next_steps:
                for ns in ext.next_steps:
                    st.markdown(f"- {ns}")
            else:
                st.caption("Standard operational rhythm applies.")

        # Display Extracted Action Items
        st.markdown(f"<div style='font-size:16px; font-weight:700; color:#0f172a; margin: 20px 0 10px 0;'>Extracted Candidate Deliverables ({len(ext.action_items)})</div>", unsafe_allow_html=True)
        for i, item in enumerate(ext.action_items, 1):
            with st.container():
                st.markdown(f"""
                <div class="approval-card">
                    <div class="approval-card-header">
                        <div>
                            <span style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase;">CANDIDATE #{i}</span>
                            <div class="approval-card-title">{item.title}</div>
                        </div>
                        <div style="display:flex; gap:6px;">
                            {get_priority_badge_html(item.priority)}
                            {get_confidence_badge_html(item.confidence)}
                        </div>
                    </div>
                    <div class="approval-meta-grid">
                        <div>
                            <div class="meta-item-label">Owner</div>
                            <div class="meta-item-val">{item.owner}</div>
                        </div>
                        <div>
                            <div class="meta-item-label">Deadline</div>
                            <div class="meta-item-val">{item.deadline or 'None'}</div>
                        </div>
                        <div>
                            <div class="meta-item-label">Initiative</div>
                            <div class="meta-item-val">{item.initiative or 'General'}</div>
                        </div>
                        <div>
                            <div class="meta-item-label">Status</div>
                            <div class="meta-item-val">Pending Authorization</div>
                        </div>
                    </div>
                    <div style="font-size:13px; color:#334155; margin: 6px 0;">
                        {item.description}
                    </div>
                    <div class="evidence-dossier">
                        <div class="evidence-label">Verbatim Supporting Evidence</div>
                        <div class="evidence-text">"{item.evidence}"</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
