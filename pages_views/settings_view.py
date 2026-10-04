import streamlit as st
import os
from ai.extractor import get_ai_config
from database.db import get_db_session, DEFAULT_DB_PATH
from database.models import Initiative, Meeting, Task, ReviewQueueItem, AuditLog
from database.seed import seed_demo_data
from utils.ui import render_page_header

def mask_key(k: str) -> str:
    """Mask sensitive API key."""
    if not k:
        return "Not Set"
    if len(k) <= 8:
        return "********"
    return f"{k[:4]}...{k[-4:]}"

def render_settings_page():
    render_page_header(
        title="System & Governance Settings",
        subtitle="AI model provider configurations, database persistence diagnostics, and platform lifecycle controls",
        badge_text="System Configuration"
    )

    config = get_ai_config()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:10px;'>AI Inference Configuration</div>", unsafe_allow_html=True)
        
        status_color = "#2563eb" if config["is_demo_mode"] else "#059669"
        status_label = "Offline Demo Engine (Deterministic)" if config["is_demo_mode"] else "Live LLM Engine Active"
        
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:16px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
            <div style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">Operational Mode</div>
            <div style="font-size:16px; font-weight:700; color:{status_color}; margin:4px 0 12px 0;">{status_label}</div>
            
            <table style="width:100%; font-size:13px; color:#334155; border-collapse:collapse;">
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Provider Architecture:</b></td><td>OpenAI / OpenAI-Compatible</td></tr>
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Target Inference Model:</b></td><td><code>{config['model_name']}</code></td></tr>
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>API Key Status:</b></td><td><code>{mask_key(config['api_key'])}</code></td></tr>
                <tr><td style="padding:6px 0; color:#64748b;"><b>Base URL Endpoint:</b></td><td>{config['base_url'] or 'Default (https://api.openai.com/v1)'}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:14px; font-weight:700; color:#0f172a; margin-bottom:6px;'>Environment Configuration</div>", unsafe_allow_html=True)
        st.markdown("""
        To connect OpenAI or an OpenAI-compatible provider (Groq, DeepSeek, Azure, or Ollama):
        1. Open `.env` in the application root:
        ```bash
        OPENAI_API_KEY=your_actual_key_here
        OPENAI_MODEL=gpt-4o-mini
        DEMO_MODE=false
        ```
        2. Optional custom endpoint configuration:
        ```bash
        OPENAI_BASE_URL=https://api.groq.com/openai/v1
        OPENAI_MODEL=llama-3.3-70b-versatile
        ```
        3. If no key is set, MeetFlow AI seamlessly falls back to the **Offline Demo Engine**.
        """)

    with col2:
        st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:10px;'>Database & Storage Diagnostics</div>", unsafe_allow_html=True)

        # Query database counts
        with get_db_session() as session:
            init_c = session.query(Initiative).count()
            meet_c = session.query(Meeting).count()
            task_c = session.query(Task).count()
            rev_c = session.query(ReviewQueueItem).count()
            aud_c = session.query(AuditLog).count()

        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:16px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
            <div style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">Database Engine</div>
            <div style="font-size:16px; font-weight:700; color:#0f172a; margin:4px 0 12px 0;">SQLite via SQLAlchemy 2.0 ORM</div>
            
            <table style="width:100%; font-size:13px; color:#334155; border-collapse:collapse;">
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Storage File:</b></td><td><code>{DEFAULT_DB_PATH.name}</code></td></tr>
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Strategic Initiatives:</b></td><td><b>{init_c}</b> records</td></tr>
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Recorded Meetings:</b></td><td><b>{meet_c}</b> sessions</td></tr>
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Authorized Deliverables:</b></td><td><b>{task_c}</b> tasks</td></tr>
                <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; color:#64748b;"><b>Review Queue Items:</b></td><td><b>{rev_c}</b> candidates</td></tr>
                <tr><td style="padding:6px 0; color:#64748b;"><b>Governance Audit Records:</b></td><td><b>{aud_c}</b> logs</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:14px; font-weight:700; color:#0f172a; margin-bottom:6px;'>Platform Reset & Seeding</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px; color:#64748b; margin-bottom:10px;'>Restore clean enterprise demo data across initiatives, meetings, tasks, and review queue items.</div>", unsafe_allow_html=True)
        if st.button("Reset & Re-Seed Enterprise Demo Data", type="secondary"):
            seed_demo_data(force=True)
            st.toast("Database reset and re-seeded with pristine enterprise demo data.")
            st.rerun()

    st.markdown("<hr style='margin: 20px 0; border:0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:8px;'>Architectural Governance Principles</div>", unsafe_allow_html=True)
    st.markdown("""
    - **Human-in-the-Loop Isolation:** AI suggestions are never committed automatically. Every action item requires explicit human verification before official system recording.
    - **Verbatim Evidence Attribution:** Extraction requires direct textual evidence quotes from the source transcript to eliminate hallucinated commitments.
    - **End-to-End Governance Auditability:** Every authorization, modification, and rejection is permanently recorded in the immutable audit log.
    """)
