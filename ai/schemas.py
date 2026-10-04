from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
import re

class ExtractedActionItem(BaseModel):
    title: str = Field(default="Action Item", description="Concise, actionable task title starting with a verb")
    description: Optional[str] = Field(default="", description="Detailed context or requirements for the task")
    owner: str = Field(default="Unassigned", description="Specific person assigned, or 'Unassigned' if unknown")
    deadline: Optional[str] = Field(default=None, description="Target date in YYYY-MM-DD format or null if not explicitly stated")
    priority: Literal["High", "Medium", "Low"] = Field(default="Medium", description="Task priority (High, Medium, Low)")
    initiative: Optional[str] = Field(default="General", description="Relevant strategic project or initiative name")
    status: Literal["Not Started", "In Progress", "Blocked", "Completed"] = Field(default="Not Started", description="Initial status")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    evidence: str = Field(default="Referenced deliverable commitment in meeting discussion.", description="Exact supporting quotation from the meeting text")

    @field_validator("title", mode="before")
    @classmethod
    def clean_title(cls, v):
        if not v or not str(v).strip():
            return "Action Item (Title unassigned)"
        return str(v).strip()

    @field_validator("deadline", mode="before")
    @classmethod
    def clean_deadline(cls, v):
        if not v or v in ["null", "None", "", "N/A", "TBD", "unknown"]:
            return None
        # Check standard YYYY-MM-DD and verify real calendar date
        if isinstance(v, str):
            match = re.search(r"(\d{4}-\d{2}-\d{2})", v)
            if match:
                candidate = match.group(1)
                try:
                    datetime.strptime(candidate, "%Y-%m-%d")
                    return candidate
                except ValueError:
                    return None
        return None

    @field_validator("owner", mode="before")
    @classmethod
    def clean_owner(cls, v):
        if not v or str(v).strip().lower() in ["null", "none", "unknown", "n/a", "tbd", ""]:
            return "Unassigned"
        return str(v).strip()

    @field_validator("confidence", mode="before")
    @classmethod
    def clean_confidence(cls, v):
        if v is None:
            return 0.85
        try:
            val = float(v)
            if 1.0 < val <= 100.0:
                return round(val / 100.0, 2)
            elif val < 0.0:
                return 0.5
            elif val > 1.0:
                return 1.0
            return round(val, 2)
        except Exception:
            return 0.85

    @field_validator("evidence", mode="before")
    @classmethod
    def clean_evidence(cls, v):
        if not v or not str(v).strip():
            return "Agreed deliverable during meeting discussion."
        return str(v).strip()

    @field_validator("priority", mode="before")
    @classmethod
    def clean_priority(cls, v):
        if not v:
            return "Medium"
        v_str = str(v).capitalize()
        if v_str in ["High", "Medium", "Low"]:
            return v_str
        return "Medium"


class MeetingExtractionResponse(BaseModel):
    meeting_summary: str = Field(default="Meeting discussion recorded.", description="Executive summary of the meeting, 2-4 sentences")
    decisions: List[str] = Field(default_factory=list, description="Key decisions agreed upon in the meeting")
    risks: List[str] = Field(default_factory=list, description="Identified operational or technical risks")
    blockers: List[str] = Field(default_factory=list, description="Any immediate blockers stalling progress")
    next_steps: List[str] = Field(default_factory=list, description="Broader milestone next steps")
    action_items: List[ExtractedActionItem] = Field(default_factory=list, description="Extracted actionable commitments")
