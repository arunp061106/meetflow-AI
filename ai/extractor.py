import os
import json
import re
from typing import Tuple, Optional
from dotenv import load_dotenv
from pydantic import ValidationError
from openai import OpenAI

from ai.schemas import MeetingExtractionResponse
from ai.prompts import EXTRACTION_SYSTEM_PROMPT, REPORT_NARRATIVE_SYSTEM_PROMPT
from ai.demo_extractor import generate_demo_extraction

load_dotenv()

def get_ai_config():
    """Returns current AI configuration and demo mode status."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    demo_mode_env = os.getenv("DEMO_MODE", "").strip().lower()

    # If demo mode is explicitly enabled or no api key exists
    is_demo_mode = (demo_mode_env == "true") or not api_key

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name,
        "is_demo_mode": is_demo_mode,
        "has_api_key": bool(api_key)
    }

def clean_json_string(raw_str: str) -> str:
    """Extract clean JSON substring from potential markdown wrappers."""
    raw_str = raw_str.strip()
    # Strip markdown backticks
    if raw_str.startswith("```json"):
        raw_str = raw_str[7:]
    elif raw_str.startswith("```"):
        raw_str = raw_str[3:]
    if raw_str.endswith("```"):
        raw_str = raw_str[:-3]
    raw_str = raw_str.strip()

    # Find outermost braces
    start = raw_str.find("{")
    end = raw_str.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw_str[start:end+1]
    return raw_str

def extract_meeting_intelligence(
    transcript: str,
    meeting_title: str = "",
    initiative_hint: str = ""
) -> Tuple[Optional[MeetingExtractionResponse], bool, str]:
    """
    Extracts structured action items, decisions, and risks from a meeting transcript.
    Returns: (MeetingExtractionResponse, is_demo_mode, status_message)
    """
    if not transcript or not transcript.strip():
        return None, False, "Transcript content is empty. Please provide meeting notes or transcript text."

    config = get_ai_config()

    # Fallback to Demo Mode if configured or if API key is not present
    if config["is_demo_mode"]:
        demo_result = generate_demo_extraction(
            transcript=transcript,
            meeting_title=meeting_title,
            initiative_hint=initiative_hint
        )
        msg = "Demo Mode — AI extraction is simulated using deterministic sample outputs."
        return demo_result, True, msg

    # Real LLM API Execution
    try:
        client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )

        user_content = f"""MEETING METADATA:
Title: {meeting_title or 'Untitled Meeting'}
Initiative Context: {initiative_hint or 'General'}

MEETING TRANSCRIPT / NOTES:
{transcript}

Extract all genuine action items, decisions, risks, blockers, and next steps following the system guidelines strictly. Return valid JSON only."""

        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        raw_response = response.choices[0].message.content or "{}"
        cleaned_json = clean_json_string(raw_response)

        try:
            parsed = json.loads(cleaned_json)
        except json.JSONDecodeError as json_err:
            # Fallback to demo mode gracefully with explanation
            demo_result = generate_demo_extraction(transcript, meeting_title, initiative_hint)
            return demo_result, True, f"LLM returned malformed JSON ({str(json_err)}). Recovered safely using fallback extraction."

        # Validate with Pydantic
        try:
            validated = MeetingExtractionResponse.model_validate(parsed)
            return validated, False, f"Successfully extracted {len(validated.action_items)} action item(s) using {config['model_name']}."
        except ValidationError as val_err:
            # Safe recovery: try to fix missing fields
            if "action_items" in parsed and isinstance(parsed["action_items"], list):
                # Try cleaning items individually
                safe_items = []
                for item in parsed["action_items"]:
                    try:
                        safe_items.append(item)
                    except Exception:
                        continue
                parsed["action_items"] = safe_items
                parsed.setdefault("meeting_summary", "Extracted meeting recap.")
                parsed.setdefault("decisions", [])
                parsed.setdefault("risks", [])
                parsed.setdefault("blockers", [])
                parsed.setdefault("next_steps", [])
                try:
                    recovered = MeetingExtractionResponse.model_validate(parsed)
                    return recovered, False, f"Partially recovered {len(recovered.action_items)} action items after minor schema alignment."
                except Exception:
                    pass

            demo_result = generate_demo_extraction(transcript, meeting_title, initiative_hint)
            return demo_result, True, f"Validation warning: Schema error ({val_err.error_count()} issues). Recovered using fallback extraction."

    except Exception as e:
        # Graceful fallback on API key invalid, rate limit, quota, or network error
        demo_result = generate_demo_extraction(transcript, meeting_title, initiative_hint)
        err_msg = str(e)
        if "quota" in err_msg.lower() or "key" in err_msg.lower() or "auth" in err_msg.lower():
            err_msg = "LLM authentication/quota issue detected. Operating safely in Demo Mode."
        return demo_result, True, f"Demo Mode (Fallback): {err_msg}"

def generate_report_narrative(metrics_summary: str) -> Tuple[str, bool]:
    """
    Generates an executive narrative for the weekly report.
    Returns (narrative_markdown, is_ai_generated)
    """
    config = get_ai_config()

    if config["is_demo_mode"]:
        # High quality deterministic executive narrative
        narrative = f"""### Executive Narrative Summary
**Operational Momentum & Velocity:**
During this reporting window, initiative execution demonstrated steady forward velocity with core focus centered on system stabilization and cross-functional alignment. Engineering, analytics, and product teams maintained active delivery across 5 strategic workstreams.

**Key Accomplishments & Deliverables:**
- **Customer Analytics Platform:** Deployed predictive churn model scoring endpoints with strong accuracy metrics and initiated frontline alert integrations.
- **Data Warehouse Migration:** Completed automated validation runs with 85%+ table parity, maintaining low pipeline error rates.
- **Mobile Application Launch:** Finalized stabilization candidate builds and established staging load testing benchmarks.

**Critical Areas Requiring Leadership Attention:**
- **Overdue Task Remediation:** Overdue tasks are concentrated in external dependency items and third-party API configurations. Owners have been flagged for expedited resolution.
- **Blocker Resolution:** Immediate follow-ups are underway with Platform Infrastructure and Legal teams to unblock cloud sandbox limits and privacy policy approvals.

**Recommended Strategic Next Steps:**
1. Convene a dedicated 30-minute escalation triage on Tuesday for overdue items exceeding 7 days.
2. Complete staging cutover for the warehouse migration prior to peak month-end business reporting.
3. Lock production deployment candidates 72 hours before planned release schedules."""
        return narrative, False

    try:
        client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        prompt = f"""Review the following weekly operational metrics and create a concise, executive-level narrative report:

{metrics_summary}

Provide:
1. Executive Narrative Summary
2. Key Accomplishments
3. Critical Escalations & Blockers
4. Recommended Next Steps"""

        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {"role": "system", "content": REPORT_NARRATIVE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content or "", True
    except Exception as e:
        # Fallback to deterministic
        return f"""### Executive Narrative Summary (Offline Fallback)
Initiative progress remains disciplined across active engineering and business workstreams. Key deliverables are progressing steadily toward target release milestones. Overdue action items have been surfaced in the executive tracker for active stakeholder remediation.""", False
