from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import desc, func
from database.db import get_db_session
from database.models import ReviewQueueItem, Task, AuditLog, AIExtraction
from ai.schemas import MeetingExtractionResponse, ExtractedActionItem

def add_extraction_to_review_queue(
    meeting_id: Optional[int],
    extraction: MeetingExtractionResponse,
    raw_json_str: str = ""
) -> Tuple[List[int], int]:
    """
    Inserts extracted action items into review_queue with duplicate detection.
    NEVER automatically adds items to tasks table.
    Returns: (created_ids, duplicate_count)
    """
    created_ids = []
    duplicate_count = 0

    with get_db_session() as session:
        # Store extraction log
        if not raw_json_str:
            raw_json_str = extraction.model_dump_json()

        ai_log = AIExtraction(
            meeting_id=meeting_id,
            raw_output=raw_json_str,
            created_at=datetime.utcnow()
        )
        session.add(ai_log)

        for item in extraction.action_items:
            clean_title = item.title.strip() if item.title else "Action Item"

            # Duplicate check: check if same title exists for this meeting in review_queue or tasks
            query_rq = session.query(ReviewQueueItem).filter(
                func.lower(ReviewQueueItem.title) == clean_title.lower()
            )
            query_task = session.query(Task).filter(
                func.lower(Task.title) == clean_title.lower()
            )

            if meeting_id is not None:
                query_rq = query_rq.filter(ReviewQueueItem.meeting_id == meeting_id)
                query_task = query_task.filter(Task.meeting_id == meeting_id)
            else:
                query_rq = query_rq.filter(ReviewQueueItem.meeting_id == None)
                query_task = query_task.filter(Task.meeting_id == None)

            existing_item = query_rq.first()
            existing_task = query_task.first()

            if existing_item or existing_task:
                duplicate_count += 1
                continue

            # Parse deadline safely
            parsed_deadline = None
            if item.deadline:
                try:
                    parsed_deadline = datetime.strptime(str(item.deadline)[:10], "%Y-%m-%d").date()
                except Exception:
                    parsed_deadline = None

            owner_clean = item.owner.strip() if item.owner and item.owner.strip() else "Unassigned"

            q_item = ReviewQueueItem(
                meeting_id=meeting_id,
                title=clean_title,
                description=item.description or "",
                owner=owner_clean,
                deadline=parsed_deadline,
                priority=item.priority or "Medium",
                initiative=item.initiative or "General",
                confidence=float(item.confidence) if item.confidence is not None else 0.85,
                evidence=item.evidence or "Referenced in meeting.",
                status="Pending",
                reviewer_action=None,
                reviewed_at=None,
                created_at=datetime.utcnow()
            )
            session.add(q_item)
            session.flush()
            created_ids.append(q_item.id)

            # Audit log
            audit = AuditLog(
                entity_type="review_queue",
                entity_id=q_item.id,
                action="AI_EXTRACTED",
                old_value=None,
                new_value=f"AI extracted task candidate: '{clean_title}' (confidence: {item.confidence})",
                timestamp=datetime.utcnow()
            )
            session.add(audit)

    return created_ids, duplicate_count

def get_review_queue_items(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve review queue items, optionally filtered by status."""
    with get_db_session() as session:
        query = session.query(ReviewQueueItem)
        if status_filter:
            query = query.filter(ReviewQueueItem.status == status_filter)
        items = query.order_by(desc(ReviewQueueItem.created_at)).all()
        return [item.to_dict() for item in items]

def approve_review_item(item_id: int) -> Optional[int]:
    """
    Approve an item as-is.
    Moves item from AI review queue into official task tracker.
    """
    with get_db_session() as session:
        item = session.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_id).first()
        if not item or item.status in ["Approved", "Edited & Approved"]:
            return None

        item.status = "Approved"
        item.reviewer_action = "APPROVE"
        item.reviewed_at = datetime.utcnow()

        # Create official task
        now = datetime.utcnow()
        new_task = Task(
            review_item_id=item.id,
            meeting_id=item.meeting_id,
            title=item.title,
            description=item.description,
            owner=item.owner or "Unassigned",
            deadline=item.deadline,
            priority=item.priority or "Medium",
            initiative=item.initiative or "General",
            status="Not Started",
            created_at=now,
            updated_at=now,
            completed_at=None
        )
        session.add(new_task)
        session.flush()

        audit = AuditLog(
            entity_type="review_queue",
            entity_id=item.id,
            action="APPROVED",
            old_value="Pending",
            new_value=f"Approved into Official Task #{new_task.id}: '{new_task.title}'",
            timestamp=now
        )
        session.add(audit)
        return new_task.id

def edit_and_approve_review_item(
    item_id: int,
    title: str,
    description: str,
    owner: str,
    deadline: Optional[date],
    priority: str,
    initiative: str
) -> Optional[int]:
    """
    Save edited version as official task in tasks table and update review item.
    """
    with get_db_session() as session:
        item = session.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_id).first()
        if not item or item.status in ["Approved", "Edited & Approved"]:
            return None

        old_val = f"Title: {item.title} | Owner: {item.owner} | Deadline: {item.deadline} | Priority: {item.priority} | Initiative: {item.initiative}"

        owner_clean = owner.strip() if owner and owner.strip() else "Unassigned"
        title_clean = title.strip() if title and title.strip() else item.title

        # Update item
        item.title = title_clean
        item.description = description
        item.owner = owner_clean
        item.deadline = deadline
        item.priority = priority or "Medium"
        item.initiative = initiative or "General"
        item.status = "Edited & Approved"
        item.reviewer_action = "EDIT & APPROVE"
        item.reviewed_at = datetime.utcnow()

        new_val = f"Title: {title_clean} | Owner: {owner_clean} | Deadline: {deadline} | Priority: {priority} | Initiative: {initiative}"

        # Create official task
        now = datetime.utcnow()
        new_task = Task(
            review_item_id=item.id,
            meeting_id=item.meeting_id,
            title=title_clean,
            description=description,
            owner=owner_clean,
            deadline=deadline,
            priority=priority or "Medium",
            initiative=initiative or "General",
            status="Not Started",
            created_at=now,
            updated_at=now,
            completed_at=None
        )
        session.add(new_task)
        session.flush()

        audit = AuditLog(
            entity_type="review_queue",
            entity_id=item.id,
            action="EDIT_APPROVED",
            old_value=old_val,
            new_value=f"Edited & Approved into Official Task #{new_task.id}: {new_val}",
            timestamp=now
        )
        session.add(audit)
        return new_task.id

def reject_review_item(item_id: int, reason: str = "") -> bool:
    """
    Reject an item.
    Marks review queue item as Rejected.
    DOES NOT add item to official tasks table!
    """
    with get_db_session() as session:
        item = session.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_id).first()
        if not item:
            return False

        item.status = "Rejected"
        item.reviewer_action = "REJECT"
        item.reviewed_at = datetime.utcnow()

        audit = AuditLog(
            entity_type="review_queue",
            entity_id=item.id,
            action="REJECTED",
            old_value="Pending",
            new_value=f"Rejected item '{item.title}'. Reason: {reason or 'Not actionable / redundant'}",
            timestamp=datetime.utcnow()
        )
        session.add(audit)
        return True

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve audit trail records."""
    with get_db_session() as session:
        logs = session.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).all()
        return [l.to_dict() for l in logs]
