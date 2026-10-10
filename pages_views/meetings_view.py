import streamlit as st
from datetime import date
from services.meeting_service import get_all_meetings, create_meeting, get_all_initiatives
from utils.ui import render_page_header, render_workflow_indicator, render_empty_state

def render_meetings_page():
    render_page_header(
        title="Meetings & Intelligence Repository",
        subtitle="Centralized management of executive synopses, discussion notes, and verbatim transcripts",
        badge_text="Repository",
        highlight_word="Repository"
    )

    render_workflow_indicator("AI Extraction")

    tab_list, tab_create = st.tabs(["Meeting Records", "Log New Meeting"])

    initiatives_data = get_all_initiatives()
    init_names = [i["name"] for i in initiatives_data]
    meeting_types = ["Project Review", "Sprint Planning", "Client Meeting", "Management Review", "Team Meeting", "Other"]

    with tab_create:
        st.markdown("<h3 class='calistoga-heading' style='font-size:18px; margin-bottom:6px;'>Record Meeting & Ingest Transcript</h3>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px; color:#64748B; margin-bottom:18px;'>Ingest meeting notes or audio transcripts for automated intelligence extraction and commitment tracking.</div>", unsafe_allow_html=True)

        with st.form("new_meeting_form", clear_on_submit=True):
            col_t1, col_t2 = st.columns([7, 5])
            with col_t1:
                title = st.text_input("Meeting Subject / Title*", placeholder="e.g. Q4 Executive Operations Alignment")
            with col_t2:
                meeting_date = st.date_input("Meeting Date*", value=date.today())

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                m_type = st.selectbox("Meeting Classification*", meeting_types)
            with col_m2:
                organizer = st.text_input("Meeting Organizer*", placeholder="e.g. Sarah Chen")
            with col_m3:
                initiative_choice = st.selectbox("Primary Initiative Context", ["None / General"] + init_names)

            participants = st.text_input("Meeting Attendees / Participants", placeholder="e.g. Sarah Chen, David Kim, Marcus Vance, Elena Rostova")

            uploaded_file = st.file_uploader("Upload Transcript File (.txt, .md)", type=["txt", "md"])
            file_content = ""
            if uploaded_file is not None:
                try:
                    file_content = uploaded_file.read().decode("utf-8")
                    st.info(f"Loaded {len(file_content)} characters from uploaded file.")
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            transcript_text = st.text_area(
                "Notes & Verbatim Transcript Content*",
                value=file_content,
                height=220,
                placeholder="Paste discussion notes, speaker dialogues, or raw meeting transcript here..."
            )

            submit_btn = st.form_submit_button("Record Meeting in Repository", type="primary", use_container_width=True)
            if submit_btn:
                if not title.strip() or not organizer.strip() or not transcript_text.strip():
                    st.error("Please provide Title, Organizer, and Transcript content.")
                else:
                    selected_init = initiative_choice if initiative_choice != "None / General" else None
                    new_id = create_meeting(
                        title=title.strip(),
                        meeting_date=meeting_date,
                        meeting_type=m_type,
                        organizer=organizer.strip(),
                        participants=participants.strip(),
                        initiative=selected_init,
                        transcript=transcript_text.strip(),
                        summary=None
                    )
                    st.success(f"Meeting record #{new_id} ('{title}') successfully created.")
                    st.rerun()

    with tab_list:
        meetings = get_all_meetings()

        col_f1, col_f2 = st.columns([7, 5])
        with col_f1:
            search_query = st.text_input("Filter Records", placeholder="Search title, organizer, or transcript keywords...", label_visibility="collapsed")
        with col_f2:
            type_filter = st.selectbox("Meeting Classification Filter", ["All Classifications"] + meeting_types, label_visibility="collapsed")

        filtered = meetings
        if type_filter != "All Classifications":
            filtered = [m for m in filtered if m["meeting_type"] == type_filter]
        if search_query.strip():
            sq = search_query.strip().lower()
            filtered = [
                m for m in filtered
                if sq in m["title"].lower()
                or sq in m["organizer"].lower()
                or (m["transcript"] and sq in m["transcript"].lower())
            ]

        st.markdown(f"<div style='font-size:12px; color:#64748B; margin: 4px 0 16px 0; font-family:var(--font-mono);'>Showing <b>{len(filtered)}</b> recorded meeting session(s)</div>", unsafe_allow_html=True)

        if not filtered:
            render_empty_state("No Meetings Found", "No meeting records match your search criteria. Log a meeting or reset filters.")
        else:
            for m in filtered:
                with st.expander(f"Meeting #{m['id']}: {m['title']} — {m['meeting_date']} ({m['meeting_type']})", expanded=False):
                    c_info1, c_info2 = st.columns([8, 4])
                    with c_info1:
                        st.markdown(f"**Organizer:** {m['organizer']}")
                        st.markdown(f"**Strategic Initiative:** `{m['initiative'] or 'General'}`")
                        st.markdown(f"**Participants:** {m['participants'] or 'Not specified'}")
                    with c_info2:
                        st.markdown(f"**Record ID:** `#{m['id']}`")
                        st.markdown(f"**Ingested On:** {m['created_at'][:10] if m['created_at'] else 'N/A'}")

                        if st.button("Extract Action Items", key=f"extract_btn_{m['id']}", type="primary", use_container_width=True):
                            st.session_state["extract_meeting_id"] = m["id"]
                            st.session_state["extract_transcript"] = m["transcript"]
                            st.session_state["extract_title"] = m["title"]
                            st.session_state["extract_initiative"] = m["initiative"] or "General"
                            st.session_state["nav_selection"] = "AI Extraction"
                            st.rerun()

                    if m.get("summary"):
                        st.markdown("**Executive Summary:**")
                        st.info(m["summary"])

                    st.markdown("**Transcript Content:**")
                    st.text_area("Transcript", value=m["transcript"] or "", height=140, disabled=True, key=f"view_transcript_{m['id']}", label_visibility="collapsed")
