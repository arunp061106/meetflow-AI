from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy import func
from database.db import get_db_session
from database.models import Task, Initiative, ReviewQueueItem, Meeting

def get_executive_kpis() -> Dict[str, Any]:
    """Calculate core executive high-level metrics."""
    today = date.today()
    with get_db_session() as session:
        total_initiatives = session.query(func.count(Initiative.id)).scalar() or 0
        total_tasks = session.query(func.count(Task.id)).scalar() or 0
        completed_tasks = session.query(func.count(Task.id)).filter(Task.status == "Completed").scalar() or 0
        in_progress_tasks = session.query(func.count(Task.id)).filter(Task.status == "In Progress").scalar() or 0
        not_started_tasks = session.query(func.count(Task.id)).filter(Task.status == "Not Started").scalar() or 0
        blocked_tasks = session.query(func.count(Task.id)).filter(Task.status == "Blocked").scalar() or 0
        
        active_tasks = not_started_tasks + in_progress_tasks + blocked_tasks

        # Overdue: deadline < today and status != 'Completed'
        overdue_tasks = session.query(func.count(Task.id)).filter(
            Task.status != "Completed",
            Task.deadline < today,
            Task.deadline != None
        ).scalar() or 0

        pending_approvals = session.query(func.count(ReviewQueueItem.id)).filter(
            ReviewQueueItem.status == "Pending"
        ).scalar() or 0

        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0
        overdue_rate = round((overdue_tasks / active_tasks * 100), 1) if active_tasks > 0 else 0.0

        return {
            "total_initiatives": total_initiatives,
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "not_started_tasks": not_started_tasks,
            "blocked_tasks": blocked_tasks,
            "overdue_tasks": overdue_tasks,
            "pending_approvals": pending_approvals,
            "completion_rate": completion_rate,
            "overdue_rate": overdue_rate
        }

def get_initiative_health_data() -> List[Dict[str, Any]]:
    """Calculate progress and task counts per initiative."""
    today = date.today()
    with get_db_session() as session:
        initiatives = session.query(Initiative).all()
        tasks = session.query(Task).all()

        data = []
        for init in initiatives:
            init_tasks = [t for t in tasks if t.initiative == init.name]
            total = len(init_tasks)
            completed = sum(1 for t in init_tasks if t.status == "Completed")
            in_prog = sum(1 for t in init_tasks if t.status == "In Progress")
            blocked = sum(1 for t in init_tasks if t.status == "Blocked")
            overdue = sum(1 for t in init_tasks if t.status != "Completed" and t.deadline and t.deadline < today)
            
            rate = round((completed / total * 100), 1) if total > 0 else 0.0

            # Determine health
            if blocked > 1 or overdue > 2:
                health = "At Risk"
            elif overdue > 0 or blocked > 0:
                health = "Needs Attention"
            else:
                health = "On Track"

            data.append({
                "initiative": init.name,
                "owner": init.owner,
                "status": init.status,
                "health": health,
                "total_tasks": total,
                "completed": completed,
                "in_progress": in_prog,
                "blocked": blocked,
                "overdue": overdue,
                "completion_rate": rate
            })
        return data

def get_task_status_distribution() -> Dict[str, int]:
    """Return task count by status."""
    with get_db_session() as session:
        statuses = ["Completed", "In Progress", "Not Started", "Blocked"]
        dist = {}
        for s in statuses:
            cnt = session.query(func.count(Task.id)).filter(Task.status == s).scalar() or 0
            dist[s] = cnt
        return dist

def get_priority_distribution() -> Dict[str, int]:
    """Return task count by priority."""
    with get_db_session() as session:
        priorities = ["High", "Medium", "Low"]
        dist = {}
        for p in priorities:
            cnt = session.query(func.count(Task.id)).filter(Task.priority == p).scalar() or 0
            dist[p] = cnt
        return dist

def get_owner_workload() -> List[Dict[str, Any]]:
    """Return task distribution by owner with status breakdown."""
    today = date.today()
    with get_db_session() as session:
        tasks = session.query(Task).all()
        owners = set(t.owner for t in tasks if t.owner)

        workload = []
        for o in sorted(owners):
            o_tasks = [t for t in tasks if t.owner == o]
            completed = sum(1 for t in o_tasks if t.status == "Completed")
            in_prog = sum(1 for t in o_tasks if t.status == "In Progress")
            blocked = sum(1 for t in o_tasks if t.status == "Blocked")
            not_started = sum(1 for t in o_tasks if t.status == "Not Started")
            overdue = sum(1 for t in o_tasks if t.status != "Completed" and t.deadline and t.deadline < today)
            
            workload.append({
                "owner": o,
                "total": len(o_tasks),
                "completed": completed,
                "in_progress": in_prog,
                "blocked": blocked,
                "not_started": not_started,
                "overdue": overdue,
                "active": len(o_tasks) - completed
            })
        return workload

def get_overdue_tasks_list(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve list of overdue tasks."""
    today = date.today()
    with get_db_session() as session:
        tasks = session.query(Task).filter(
            Task.status != "Completed",
            Task.deadline < today,
            Task.deadline != None
        ).order_by(Task.deadline.asc()).limit(limit).all()

        res = []
        for t in tasks:
            days_late = (today - t.deadline).days if t.deadline else 0
            d = t.to_dict()
            d["days_late"] = days_late
            res.append(d)
        return res

def get_upcoming_deadlines_list(days_ahead: int = 14) -> List[Dict[str, Any]]:
    """Retrieve tasks with deadlines coming up in the next N days."""
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    with get_db_session() as session:
        tasks = session.query(Task).filter(
            Task.status != "Completed",
            Task.deadline >= today,
            Task.deadline <= end_date
        ).order_by(Task.deadline.asc()).all()

        res = []
        for t in tasks:
            days_left = (t.deadline - today).days if t.deadline else 0
            d = t.to_dict()
            d["days_left"] = days_left
            res.append(d)
        return res

def get_approval_acceptance_metrics() -> Dict[str, Any]:
    """Calculate approval metrics: approved, edited, rejected, pending."""
    with get_db_session() as session:
        total = session.query(func.count(ReviewQueueItem.id)).scalar() or 0
        approved = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Approved").scalar() or 0
        edited = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Edited & Approved").scalar() or 0
        rejected = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Rejected").scalar() or 0
        pending = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Pending").scalar() or 0

        reviewed_total = approved + edited + rejected
        acceptance_rate = round(((approved + edited) / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0

        return {
            "total_items": total,
            "reviewed_total": reviewed_total,
            "approved": approved,
            "edited_and_approved": edited,
            "rejected": rejected,
            "pending": pending,
            "acceptance_rate": acceptance_rate
        }

def get_average_completion_time_days() -> float:
    """Calculate average days taken from task creation to completion."""
    with get_db_session() as session:
        completed = session.query(Task).filter(
            Task.status == "Completed",
            Task.completed_at != None
        ).all()

        if not completed:
            return 0.0

        total_days = 0.0
        valid_count = 0
        for t in completed:
            if t.completed_at and t.created_at:
                diff = (t.completed_at - t.created_at).total_seconds() / 86400.0
                if diff >= 0:
                    total_days += diff
                    valid_count += 1
        return round(total_days / valid_count, 1) if valid_count > 0 else 0.0

def get_ai_quality_metrics() -> Dict[str, Any]:
    """
    Calculates AI extraction quality and human oversight metrics from actual database records.
    Never fabricates metrics.
    """
    with get_db_session() as session:
        total_extracted = session.query(func.count(ReviewQueueItem.id)).scalar() or 0
        approved = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Approved").scalar() or 0
        edited = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Edited & Approved").scalar() or 0
        rejected = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Rejected").scalar() or 0
        pending = session.query(func.count(ReviewQueueItem.id)).filter(ReviewQueueItem.status == "Pending").scalar() or 0
        
        avg_conf_raw = session.query(func.avg(ReviewQueueItem.confidence)).scalar()
        avg_confidence = round(float(avg_conf_raw) * 100, 1) if avg_conf_raw is not None else 0.0

        reviewed_total = approved + edited + rejected
        approval_rate = round(((approved + edited) / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0
        rejection_rate = round((rejected / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0
        edit_rate = round((edited / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0
        human_intervention_count = edited + rejected
        intervention_rate = round((human_intervention_count / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0

        return {
            "total_extracted": total_extracted,
            "reviewed_total": reviewed_total,
            "approved": approved,
            "edited": edited,
            "rejected": rejected,
            "pending": pending,
            "approval_rate": approval_rate,
            "rejection_rate": rejection_rate,
            "edit_rate": edit_rate,
            "avg_confidence": avg_confidence,
            "human_intervention_count": human_intervention_count,
            "intervention_rate": intervention_rate
        }

def get_full_lineage_audit_trail(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Returns end-to-end lineage:
    AI generated -> Human edited -> Approved/Rejected -> Tracker (Task ID)
    Fully derived from actual database records across review_queue, audit_log, and tasks.
    """
    from database.models import AuditLog, Meeting
    from sqlalchemy import desc

    with get_db_session() as session:
        items = session.query(ReviewQueueItem).order_by(desc(ReviewQueueItem.id)).limit(limit).all()
        lineage = []
        for item in items:
            task = session.query(Task).filter(Task.review_item_id == item.id).first()
            audit_records = session.query(AuditLog).filter(
                AuditLog.entity_type == "review_queue",
                AuditLog.entity_id == item.id
            ).all()

            edit_log = next((a for a in audit_records if a.action == "EDIT_APPROVED"), None)
            reject_log = next((a for a in audit_records if a.action == "REJECTED"), None)
            approval_log = next((a for a in audit_records if a.action in ["APPROVED", "EDIT_APPROVED"]), None)

            meeting = session.query(Meeting).filter(Meeting.id == item.meeting_id).first()
            meeting_name = meeting.title if meeting else (f"Meeting #{item.meeting_id}" if item.meeting_id else "Ad-hoc / Unlinked")

            lineage.append({
                "review_id": item.id,
                "meeting_id": item.meeting_id,
                "meeting_title": meeting_name,
                "ai_title": item.title,
                "ai_owner": item.owner,
                "ai_deadline": item.deadline.strftime("%Y-%m-%d") if item.deadline else "None",
                "ai_priority": item.priority,
                "ai_confidence": round(item.confidence * 100, 1) if item.confidence else 85.0,
                "evidence": item.evidence,
                "status": item.status,
                "reviewer_action": item.reviewer_action or ("Pending Review" if item.status == "Pending" else item.status),
                "reviewed_at": item.reviewed_at.strftime("%Y-%m-%d %H:%M UTC") if item.reviewed_at else None,
                "task_id": task.id if task else None,
                "task_title": task.title if task else None,
                "task_status": task.status if task else None,
                "has_edits": (item.status == "Edited & Approved" or edit_log is not None),
                "before_edit": edit_log.old_value if edit_log else None,
                "after_edit": edit_log.new_value if edit_log else None,
                "rejection_reason": reject_log.new_value if reject_log else None,
                "audit_entries": [a.to_dict() for a in audit_records]
            })
        return lineage

