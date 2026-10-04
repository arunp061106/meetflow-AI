from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import desc, asc
from database.db import get_db_session
from database.models import Task, AuditLog, Meeting

def get_all_tasks(
    initiative: Optional[str] = None,
    owner: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve tasks with dynamic filtering, deadline calculations, and meeting info.
    """
    today = date.today()
    with get_db_session() as session:
        query = session.query(Task)

        if initiative and initiative != "All":
            query = query.filter(Task.initiative == initiative)
        if owner and owner != "All":
            query = query.filter(Task.owner == owner)
        if priority and priority != "All":
            query = query.filter(Task.priority == priority)
        if status and status != "All":
            if status == "Overdue":
                query = query.filter(Task.status != "Completed", Task.deadline < today, Task.deadline != None)
            else:
                query = query.filter(Task.status == status)

        if search_query:
            pattern = f"%{search_query.strip()}%"
            query = query.filter(
                (Task.title.ilike(pattern)) |
                (Task.description.ilike(pattern)) |
                (Task.owner.ilike(pattern))
            )

        tasks = query.order_by(asc(Task.deadline), desc(Task.created_at)).all()

        results = []
        for t in tasks:
            d = t.to_dict()
            # Calculate dynamic fields
            is_overdue = False
            days_remaining = None
            if t.deadline:
                days_diff = (t.deadline - today).days
                days_remaining = days_diff
                if t.status != "Completed" and days_diff < 0:
                    is_overdue = True

            d["is_overdue"] = is_overdue
            d["days_remaining"] = days_remaining
            d["meeting_title"] = t.meeting.title if t.meeting else "Direct / Unlinked"
            results.append(d)

        return results

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve single task by ID."""
    with get_db_session() as session:
        t = session.query(Task).filter(Task.id == task_id).first()
        return t.to_dict() if t else None

def update_task_status(task_id: int, new_status: str) -> bool:
    """Update task status and manage completed_at timestamp + audit log."""
    valid_statuses = ["Not Started", "In Progress", "Blocked", "Completed"]
    if new_status not in valid_statuses:
        return False

    now = datetime.utcnow()
    with get_db_session() as session:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        old_status = task.status
        if old_status == new_status:
            return True

        task.status = new_status
        task.updated_at = now
        if new_status == "Completed":
            task.completed_at = now
        else:
            task.completed_at = None

        audit = AuditLog(
            entity_type="task",
            entity_id=task.id,
            action="STATUS_CHANGE",
            old_value=old_status,
            new_value=new_status,
            timestamp=now
        )
        session.add(audit)
        return True

def update_task_details(
    task_id: int,
    title: str,
    description: str,
    owner: str,
    deadline: Optional[date],
    priority: str,
    initiative: str,
    status: str
) -> bool:
    """Update editable details of an official task."""
    now = datetime.utcnow()
    with get_db_session() as session:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        old_val = f"Status: {task.status}, Priority: {task.priority}, Owner: {task.owner}"
        
        owner_clean = owner.strip() if owner and owner.strip() else "Unassigned"
        title_clean = title.strip() if title and title.strip() else task.title

        task.title = title_clean
        task.description = description
        task.owner = owner_clean
        task.deadline = deadline
        task.priority = priority or "Medium"
        task.initiative = initiative or "General"
        if task.status != status:
            task.status = status
            if status == "Completed":
                task.completed_at = now
            else:
                task.completed_at = None
        task.updated_at = now

        new_val = f"Status: {task.status}, Priority: {task.priority}, Owner: {task.owner}"

        audit = AuditLog(
            entity_type="task",
            entity_id=task.id,
            action="TASK_UPDATED",
            old_value=old_val,
            new_value=new_val,
            timestamp=now
        )
        session.add(audit)
        return True

def create_task_manually(
    title: str,
    description: str,
    owner: str,
    deadline: Optional[date],
    priority: str,
    initiative: str,
    meeting_id: Optional[int] = None
) -> int:
    """Allow direct manual task creation if necessary."""
    now = datetime.utcnow()
    owner_clean = owner.strip() if owner and owner.strip() else "Unassigned"
    title_clean = title.strip() if title and title.strip() else "Untitled Task"

    with get_db_session() as session:
        t = Task(
            review_item_id=None,
            meeting_id=meeting_id,
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
        session.add(t)
        session.flush()

        audit = AuditLog(
            entity_type="task",
            entity_id=t.id,
            action="MANUAL_CREATED",
            old_value=None,
            new_value=f"Task #{t.id} '{t.title}' created manually",
            timestamp=now
        )
        session.add(audit)
        return t.id
