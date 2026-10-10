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
        badge_text="Inference Engine",
        highlight_word="Extraction"
    )

    render_workflow_indicator("AI Extraction")

    ai_config = get_ai_config()
    with st.expander("🔍 Architecture & Verification: System Prompt, Schema & Isolation Barrier", expanded=False):
        tab_prompt, tab_schema, tab_sql = st.tabs(["Extraction Prompt & Guardrails", "Pydantic JSON Schema", "SQLite Tables & Isolation"])
        
        with tab_prompt:
            st.markdown("<h4 class='calistoga-heading' style='font-size:15px;'>System Prompt Sent to LLM (with Verbatim Guardrails)</h4>", unsafe_allow_html=True)
            st.code("""You are an expert Enterprise Meeting Intelligence Extraction Assistant for MEETFLOW AI.
Your purpose is to analyze executive meeting transcripts, sprint planning notes, and team syncs,
and extract genuine actionable commitments with extreme precision.

Extraction Rules:
1. PRECISION OVER RECALL: Only extract genuine, actionable commitments where someone has agreed or was assigned to execute a specific deliverable.
2. DO NOT INVENT OWNERS: Extract the real person responsible. If ambiguous or unknown, set 'Unassigned'. Never invent fake names.
3. DO NOT INVENT DEADLINES: Only extract deadlines if explicitly stated (e.g. 'by Friday', 'by Oct 15'). Format as YYYY-MM-DD or null.
4. PRESERVE SOURCE EVIDENCE: For EVERY action item, quote the exact supporting verbatim text from the transcript in 'evidence'.
5. DISTINGUISH DECISIONS FROM ACTION ITEMS: Decisions go into 'decisions', commitments go into 'action_items'.
6. FILTER OUT CASUAL DISCUSSION: Do not convert brainstorms or casual banter into tasks.
7. ASSIGN PRIORITY CONSERVATIVELY: High (urgent blocker), Medium (standard deliverable), Low (documentation/minor).
8. ASSIGN CONFIDENCE: Provide a realistic confidence score (0.0 to 1.0) reflecting explicit commitment clarity.
9. STRICT JSON ONLY: Return ONLY a valid JSON object matching the requested schema. No markdown fences outside the JSON.""", language="markdown")

        with tab_schema:
            st.markdown("<h4 class='calistoga-heading' style='font-size:15px;'>Strict Type Validation via Pydantic v2</h4>", unsafe_allow_html=True)
            st.code("""class ExtractedActionItem(BaseModel):
    title: str = Field(description="Actionable task title starting with a verb")
    description: Optional[str] = Field(default="", description="Contextual details")
    owner: str = Field(default="Unassigned", description="Specific person assigned")
    deadline: Optional[str] = Field(default=None, description="YYYY-MM-DD or null")
    priority: Literal["High", "Medium", "Low"] = Field(default="Medium")
    initiative: Optional[str] = Field(default="General")
    status: Literal["Not Started", "In Progress", "Blocked", "Completed"] = Field(default="Not Started")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    evidence: str = Field(description="Exact verbatim quotation from transcript")

class MeetingExtractionResponse(BaseModel):
    meeting_summary: str = Field(description="Executive recap of discussion")
    decisions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    action_items: List[ExtractedActionItem] = Field(default_factory=list)""", language="python")

        with tab_sql:
            st.markdown("<h4 class='calistoga-heading' style='font-size:15px;'>Relational Schema & Staging Isolation Barrier</h4>", unsafe_allow_html=True)
            st.code("""-- 1. Meetings Repository
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    meeting_date DATE NOT NULL,
    transcript TEXT NOT NULL,
    summary TEXT,
    initiative TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Human-in-the-Loop Isolation Barrier (Raw LLM Output Staged Here)
CREATE TABLE review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER REFERENCES meetings(id),
    title TEXT NOT NULL,
    owner TEXT NOT NULL,
    deadline DATE,
    priority TEXT NOT NULL,
    initiative TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence TEXT NOT NULL,
    status TEXT DEFAULT 'Pending', -- Pending | Approved | Edited & Approved | Rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Official Corporate Tracker (Only Populated After Human Gate Authorization)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_queue_id INTEGER REFERENCES review_queue(id),
    title TEXT NOT NULL,
    owner TEXT NOT NULL,
    deadline DATE,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,          -- Not Started | In Progress | Blocked | Completed
    initiative TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Immutable Compliance Audit Trail
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_queue_id INTEGER REFERENCES review_queue(id),
    action TEXT NOT NULL,          -- Approved | Edited & Approved | Rejected
    before_state TEXT,             -- JSON snapshot before human edit
    after_state TEXT,              -- JSON snapshot after human edit
    reviewer_notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""", language="sql")

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
        st.markdown("<div style='font-size:12px; color:#64748B; padding-top:8px;'>Inferred tasks are staged in the Approval Queue with verbatim evidence. AI suggestions are never committed automatically.</div>", unsafe_allow_html=True)

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

        st.markdown("<hr style='margin: 24px 0 16px 0; border:0; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)
        st.success(f"{msg}")
        if dup_count > 0:
            st.info(f"{dup_count} duplicate item(s) already existed in the review queue and were skipped.")

        # Governance Staging Box
        st.markdown(f"""
        <div style="background:#FFFFFF; border-left:4px solid #0052FF; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0; border-radius:12px; padding:16px 20px; margin-bottom:20px; box-shadow:0 4px 12px rgba(0,82,255,0.04);">
            <div style="font-family:var(--font-display); font-size:16px; color:#0F172A; margin-bottom:4px;">
                Human Verification Gate: {count} Action Item(s) Staged in Review Queue
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.55;">
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
            st.markdown("<h4 class='calistoga-heading' style='font-size:15px; margin-bottom:6px;'>Executive Summary</h4>", unsafe_allow_html=True)
            st.info(ext.meeting_summary)

            st.markdown("<h4 class='calistoga-heading' style='font-size:15px; margin: 14px 0 6px 0;'>Key Decisions</h4>", unsafe_allow_html=True)
            if ext.decisions:
                for d in ext.decisions:
                    st.markdown(f"- {d}")
            else:
                st.caption("No explicit strategic decisions recorded.")

        with col_s2:
            st.markdown("<h4 class='calistoga-heading' style='font-size:15px; margin-bottom:6px;'>Identified Risks & Blockers</h4>", unsafe_allow_html=True)
            if ext.risks or ext.blockers:
                for r in ext.risks:
                    st.markdown(f"- **Risk:** {r}")
                for b in ext.blockers:
                    st.markdown(f"- **Blocker:** {b}")
            else:
                st.caption("No critical operational risks or blockers detected.")

            st.markdown("<h4 class='calistoga-heading' style='font-size:15px; margin: 14px 0 6px 0;'>Milestone Next Steps</h4>", unsafe_allow_html=True)
            if ext.next_steps:
                for ns in ext.next_steps:
                    st.markdown(f"- {ns}")
            else:
                st.caption("Standard operational rhythm applies.")

        # Display Extracted Action Items
        st.markdown(f"<h3 class='calistoga-heading' style='font-size:18px; margin: 24px 0 12px 0;'>Extracted Candidate Deliverables ({len(ext.action_items)})</h3>", unsafe_allow_html=True)
        for i, item in enumerate(ext.action_items, 1):
            is_high_conf = item.confidence >= 0.90
            card_class = "approval-card"
            if is_high_conf:
                # 2px gradient stroke technique for high-confidence items
                card_html = f"""
                <div class="kpi-card-featured" style="margin-bottom:14px;">
                    <div class="kpi-card-featured-inner">
                        <div class="approval-card-header">
                            <div>
                                <span style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:#0052FF; text-transform:uppercase; letter-spacing:0.06em;">CANDIDATE #{i} &bull; HIGH CONFIDENCE MATCH</span>
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
                        <div style="font-size:13px; color:#334155; margin: 8px 0;">
                            {item.description}
                        </div>
                        <div class="evidence-dossier">
                            <div class="evidence-label">Verbatim Supporting Evidence</div>
                            <div class="evidence-text">"{item.evidence}"</div>
                        </div>
                    </div>
                </div>
                """
            else:
                card_html = f"""
                <div class="approval-card">
                    <div class="approval-card-header">
                        <div>
                            <span style="font-family:var(--font-mono); font-size:10px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.06em;">CANDIDATE #{i}</span>
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
                    <div style="font-size:13px; color:#334155; margin: 8px 0;">
                        {item.description}
                    </div>
                    <div class="evidence-dossier">
                        <div class="evidence-label">Verbatim Supporting Evidence</div>
                        <div class="evidence-text">"{item.evidence}"</div>
                    </div>
                </div>
                """
            with st.container():
                st.markdown(card_html, unsafe_allow_html=True)
