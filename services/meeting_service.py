from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.db import get_db_session
from database.models import Meeting, Initiative, AuditLog

def get_all_meetings() -> List[Dict[str, Any]]:
    """Retrieve all meetings ordered by meeting_date descending."""
    with get_db_session() as session:
        meetings = session.query(Meeting).order_by(desc(Meeting.meeting_date), desc(Meeting.id)).all()
        return [m.to_dict() for m in meetings]

def get_meeting_by_id(meeting_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single meeting by ID."""
    with get_db_session() as session:
        meeting = session.query(Meeting).filter(Meeting.id == meeting_id).first()
        return meeting.to_dict() if meeting else None

def create_meeting(
    title: str,
    meeting_date: date,
    meeting_type: str,
    organizer: str,
    participants: str,
    initiative: Optional[str],
    transcript: str,
    summary: Optional[str] = None
) -> int:
    """Create a new meeting record in the database."""
    with get_db_session() as session:
        new_meeting = Meeting(
            title=title,
            meeting_date=meeting_date,
            meeting_type=meeting_type,
            organizer=organizer,
            participants=participants,
            initiative=initiative,
            transcript=transcript,
            summary=summary,
            created_at=datetime.utcnow()
        )
        session.add(new_meeting)
        session.flush()
        m_id = new_meeting.id

        audit = AuditLog(
            entity_type="meeting",
            entity_id=m_id,
            action="CREATED",
            old_value=None,
            new_value=f"Meeting '{title}' created on {meeting_date}",
            timestamp=datetime.utcnow()
        )
        session.add(audit)
        return m_id

def update_meeting_summary(meeting_id: int, summary: str):
    """Update executive summary of a meeting."""
    with get_db_session() as session:
        meeting = session.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.summary = summary

def get_all_initiatives() -> List[Dict[str, Any]]:
    """Retrieve all initiatives."""
    with get_db_session() as session:
        initiatives = session.query(Initiative).order_by(Initiative.name).all()
        return [i.to_dict() for i in initiatives]

def create_initiative(name: str, description: str, owner: str, status: str = "Active") -> int:
    """Create a new strategic initiative."""
    with get_db_session() as session:
        existing = session.query(Initiative).filter(Initiative.name == name).first()
        if existing:
            return existing.id
        init = Initiative(
            name=name,
            description=description,
            owner=owner,
            status=status,
            created_at=datetime.utcnow()
        )
        session.add(init)
        session.flush()
        return init.id
