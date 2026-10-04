from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Date, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Initiative(Base):
    __tablename__ = "initiatives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=False, default="Unassigned")
    status = Column(String(50), nullable=False, default="Active")  # Active, On Track, At Risk, Completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    meeting_date = Column(Date, nullable=False, default=date.today)
    meeting_type = Column(String(100), nullable=False, default="Project Review")
    organizer = Column(String(100), nullable=False, default="Unassigned")
    participants = Column(Text, nullable=True)
    initiative = Column(String(200), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    extractions = relationship("AIExtraction", back_populates="meeting", cascade="all, delete-orphan")
    review_items = relationship("ReviewQueueItem", back_populates="meeting")
    tasks = relationship("Task", back_populates="meeting")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "meeting_date": self.meeting_date.isoformat() if self.meeting_date else None,
            "meeting_type": self.meeting_type,
            "organizer": self.organizer,
            "participants": self.participants,
            "initiative": self.initiative,
            "transcript": self.transcript,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AIExtraction(Base):
    __tablename__ = "ai_extractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    raw_output = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    meeting = relationship("Meeting", back_populates="extractions")


class ReviewQueueItem(Base):
    __tablename__ = "review_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=False, default="Unassigned")
    deadline = Column(Date, nullable=True)
    priority = Column(String(50), nullable=False, default="Medium")  # High, Medium, Low
    initiative = Column(String(200), nullable=True)
    confidence = Column(Float, nullable=False, default=0.85)
    evidence = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="Pending")  # Pending, Approved, Rejected, Edited & Approved
    reviewer_action = Column(String(50), nullable=True)  # APPROVE, EDIT & APPROVE, REJECT
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    meeting = relationship("Meeting", back_populates="review_items")
    task = relationship("Task", back_populates="review_item", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "meeting_id": self.meeting_id,
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "initiative": self.initiative,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "status": self.status,
            "reviewer_action": self.reviewer_action,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_item_id = Column(Integer, ForeignKey("review_queue.id"), nullable=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=False, default="Unassigned")
    deadline = Column(Date, nullable=True)
    priority = Column(String(50), nullable=False, default="Medium")  # High, Medium, Low
    initiative = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="Not Started")  # Not Started, In Progress, Blocked, Completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    review_item = relationship("ReviewQueueItem", back_populates="task")
    meeting = relationship("Meeting", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "review_item_id": self.review_item_id,
            "meeting_id": self.meeting_id,
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "initiative": self.initiative,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(100), nullable=False)  # review_queue, task, meeting
    entity_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)  # APPROVED, EDIT_APPROVED, REJECTED, STATUS_CHANGE, CREATED
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
