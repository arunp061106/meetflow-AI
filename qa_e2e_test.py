import sys
import os
import json
from datetime import date, datetime, timedelta

def run_qa_suite():
    print("======================================================================")
    print("MEETFLOW AI — COMPREHENSIVE QA E2E TEST SUITE")
    print("======================================================================")

    # ---------------------------------------------------------
    # 1. Start Application / Check DB Connection
    # ---------------------------------------------------------
    print("\n[Step 1 & 2] Initializing DB & Loading Enterprise Demo Data...")
    from database.db import init_db, get_db_session, engine
    from database.models import Initiative, Meeting, Task, ReviewQueueItem, AuditLog
    from database.seed import seed_demo_data

    init_db()
    seed_demo_data(force=True)

    with get_db_session() as s:
        init_count = s.query(Initiative).count()
        meet_count = s.query(Meeting).count()
        task_count = s.query(Task).count()
        rev_count = s.query(ReviewQueueItem).count()
        print(f"  -> Seeding verified: {init_count} Initiatives, {meet_count} Meetings, {task_count} Tasks, {rev_count} Review Items")
        assert init_count == 5, f"Expected 5 initiatives, got {init_count}"
        assert meet_count == 8, f"Expected 8 meetings, got {meet_count}"
        assert task_count >= 30, f"Expected 30+ tasks, got {task_count}"
        assert rev_count >= 10, f"Expected 10+ review queue items, got {rev_count}"

    # ---------------------------------------------------------
    # 3. Open Dashboard / Verify Metrics
    # ---------------------------------------------------------
    print("\n[Step 3] Verifying Executive Dashboard Metrics & Health Data...")
    from services.analytics_service import (
        get_executive_kpis,
        get_initiative_health_data,
        get_task_status_distribution,
        get_priority_distribution,
        get_owner_workload,
        get_overdue_tasks_list,
        get_upcoming_deadlines_list
    )
    kpis = get_executive_kpis()
    assert kpis["total_initiatives"] == 5
    assert kpis["total_tasks"] >= 30
    assert kpis["active_tasks"] > 0
    assert kpis["completed_tasks"] > 0
    assert kpis["overdue_tasks"] > 0
    assert kpis["pending_approvals"] >= 10
    assert 0.0 <= kpis["completion_rate"] <= 100.0

    init_health = get_initiative_health_data()
    assert len(init_health) == 5
    for ih in init_health:
        assert ih["health"] in ["On Track", "Needs Attention", "At Risk"]

    overdue_list = get_overdue_tasks_list()
    assert len(overdue_list) > 0
    for ot in overdue_list:
        assert ot["deadline"] < date.today().strftime("%Y-%m-%d")
        assert ot["status"] != "Completed"

    print(f"  -> Dashboard KPIs verified: {kpis['completion_rate']}% completion, {kpis['overdue_tasks']} overdue tasks, {kpis['pending_approvals']} pending approvals.")

    # ---------------------------------------------------------
    # 4 & 5. Open Meetings & Select Meeting
    # ---------------------------------------------------------
    print("\n[Step 4 & 5] Verifying Meetings Repository & Meeting Selection...")
    from services.meeting_service import get_all_meetings, get_meeting_by_id
    meetings = get_all_meetings()
    assert len(meetings) == 8
    target_meeting = meetings[0]
    print(f"  -> Selected Meeting #{target_meeting['id']}: '{target_meeting['title']}' ({target_meeting['meeting_date']})")
    assert target_meeting["transcript"] is not None
    assert len(target_meeting["transcript"]) > 50

    # ---------------------------------------------------------
    # 6 & 7. Run AI Extraction & Verify Extracted Action Items
    # ---------------------------------------------------------
    print("\n[Step 6 & 7] Running AI Extraction on Selected Meeting...")
    from ai.extractor import extract_meeting_intelligence
    extraction, is_demo, msg = extract_meeting_intelligence(
        transcript=target_meeting["transcript"],
        meeting_title=target_meeting["title"],
        initiative_hint=target_meeting["initiative"] or "General"
    )
    assert extraction is not None
    assert len(extraction.action_items) > 0
    print(f"  -> Extraction returned {len(extraction.action_items)} action item(s). Message: {msg}")

    # Verify extracted fields
    for ai in extraction.action_items:
        assert ai.title is not None and len(ai.title) > 0
        assert ai.owner is not None
        assert ai.priority in ["High", "Medium", "Low"]
        assert 0.0 <= ai.confidence <= 1.0
        assert ai.evidence is not None and len(ai.evidence) > 0
        print(f"     * Candidate: '{ai.title}' | Owner: {ai.owner} | Prio: {ai.priority} | Confidence: {ai.confidence}")

    # ---------------------------------------------------------
    # 8. Open Approval Queue & Verify Isolation
    # ---------------------------------------------------------
    print("\n[Step 8] Staging Extracted Items in Review Queue & Verifying Task Isolation...")
    from services.review_service import (
        add_extraction_to_review_queue,
        get_review_queue_items,
        approve_review_item,
        edit_and_approve_review_item,
        reject_review_item
    )

    with get_db_session() as s:
        tasks_before = s.query(Task).count()

    created_ids, dup_count = add_extraction_to_review_queue(
        meeting_id=target_meeting["id"],
        extraction=extraction
    )

    with get_db_session() as s:
        tasks_after = s.query(Task).count()
        # CRITICAL PRODUCT PRINCIPLE TEST
        assert tasks_before == tasks_after, "SECURITY VIOLATION: Tasks table changed before human approval!"

    print(f"  -> Staged {len(created_ids)} candidate(s) in review_queue. Official tasks table remained untouched ({tasks_after} tasks).")

    # ---------------------------------------------------------
    # 9 & 10. Edit One AI Item & Approve It
    # ---------------------------------------------------------
    print("\n[Step 9 & 10] Testing Edit & Approve Human Workflow...")
    item_to_edit = created_ids[0]
    edited_title = "DEPLOYMENT HOTFIX: Churn Pipeline Production Cutover"
    edited_owner = "Sarah Chen"
    edited_priority = "High"
    edited_deadline = date.today() + timedelta(days=2)

    approved_edited_task_id = edit_and_approve_review_item(
        item_id=item_to_edit,
        title=edited_title,
        description="Modified during human QA verification",
        owner=edited_owner,
        deadline=edited_deadline,
        priority=edited_priority,
        initiative="Customer Analytics Platform"
    )
    assert approved_edited_task_id is not None

    with get_db_session() as s:
        q_item = s.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_to_edit).first()
        assert q_item.status == "Edited & Approved"
        assert q_item.reviewer_action == "EDIT & APPROVE"
        
        task_obj = s.query(Task).filter(Task.id == approved_edited_task_id).first()
        assert task_obj is not None
        assert task_obj.title == edited_title
        assert task_obj.owner == edited_owner
        assert task_obj.priority == edited_priority
        assert task_obj.deadline == edited_deadline
        assert task_obj.status == "Not Started"

    print(f"  -> Item #{item_to_edit} edited and approved into Official Task #{approved_edited_task_id}.")

    # ---------------------------------------------------------
    # 11. Reject Another Item
    # ---------------------------------------------------------
    print("\n[Step 11] Testing Rejection Workflow...")
    assert len(created_ids) >= 2, "Expected at least 2 extracted items"
    item_to_reject = created_ids[1]

    with get_db_session() as s:
        task_count_before_reject = s.query(Task).count()

    rejected_ok = reject_review_item(item_to_reject, reason="Duplicate exploratory item")
    assert rejected_ok is True

    with get_db_session() as s:
        q_item_rej = s.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_to_reject).first()
        assert q_item_rej.status == "Rejected"
        assert q_item_rej.reviewer_action == "REJECT"

        task_count_after_reject = s.query(Task).count()
        # Verify rejected item was NEVER added to tasks table
        assert task_count_before_reject == task_count_after_reject, "Rejected item must not create a task!"

    print(f"  -> Item #{item_to_reject} rejected. Confirmed zero new tasks created.")

    # ---------------------------------------------------------
    # 12, 13 & 14. Initiative Tracker Verification
    # ---------------------------------------------------------
    print("\n[Step 12, 13, 14] Verifying Initiative Tracker Presence & Absence...")
    from services.task_service import get_all_tasks, update_task_status, get_task_by_id

    all_tasks = get_all_tasks()
    approved_found = any(t["id"] == approved_edited_task_id and t["title"] == edited_title for t in all_tasks)
    assert approved_found, f"Approved task #{approved_edited_task_id} not found in tracker!"

    # Verify rejected item does NOT exist in tracker
    rejected_task_found = any(t["review_item_id"] == item_to_reject for t in all_tasks)
    assert not rejected_task_found, f"Rejected item #{item_to_reject} illegally found in official task tracker!"

    print(f"  -> Confirmed: Approved task #{approved_edited_task_id} is present in tracker.")
    print(f"  -> Confirmed: Rejected item #{item_to_reject} is ABSENT from official tracker.")

    # ---------------------------------------------------------
    # 15 & 16. Change Task Status & Verify Dashboard Metrics Update
    # ---------------------------------------------------------
    print("\n[Step 15 & 16] Testing Status Lifecycle & Dashboard Metrics Reactive Update...")
    kpis_before_completion = get_executive_kpis()
    completed_before = kpis_before_completion["completed_tasks"]

    # Transition: Not Started -> In Progress
    ok1 = update_task_status(approved_edited_task_id, "In Progress")
    assert ok1 is True
    t_check = get_task_by_id(approved_edited_task_id)
    assert t_check["status"] == "In Progress"

    # Transition: In Progress -> Completed
    ok2 = update_task_status(approved_edited_task_id, "Completed")
    assert ok2 is True
    t_check = get_task_by_id(approved_edited_task_id)
    assert t_check["status"] == "Completed"
    assert t_check["completed_at"] is not None

    kpis_after_completion = get_executive_kpis()
    completed_after = kpis_after_completion["completed_tasks"]
    assert completed_after == completed_before + 1, f"Expected completed count {completed_before + 1}, got {completed_after}"

    print(f"  -> Status transitions verified. Completed tasks count correctly incremented from {completed_before} to {completed_after}.")

    # ---------------------------------------------------------
    # 17. Verify Overdue Calculation
    # ---------------------------------------------------------
    print("\n[Step 17] Verifying Overdue Calculation Precision...")
    from services.task_service import create_task_manually

    # Create task with yesterday deadline (status Not Started) -> must be overdue
    yesterday = date.today() - timedelta(days=1)
    overdue_test_id = create_task_manually(
        title="QA Overdue Detection Test Task",
        description="Testing deadline check",
        owner="Alex Morgan",
        deadline=yesterday,
        priority="High",
        initiative="Customer Analytics Platform"
    )
    t_overdue = [t for t in get_all_tasks() if t["id"] == overdue_test_id][0]
    assert t_overdue["is_overdue"] is True, "Yesterday's uncompleted task must be flagged as overdue!"
    assert t_overdue["days_remaining"] == -1

    # Mark it Completed -> must NO LONGER be overdue
    update_task_status(overdue_test_id, "Completed")
    t_overdue_resolved = [t for t in get_all_tasks() if t["id"] == overdue_test_id][0]
    assert t_overdue_resolved["is_overdue"] is False, "Completed task must never be overdue, even if deadline is past!"

    print("  -> Overdue calculations verified: Uncompleted past-due tasks = OVERDUE; Completed past-due tasks = NOT OVERDUE.")

    # ---------------------------------------------------------
    # 18. Open Analytics
    # ---------------------------------------------------------
    print("\n[Step 18] Verifying Analytics Governance Funnel & Workload...")
    from services.analytics_service import get_approval_acceptance_metrics, get_average_completion_time_days
    appr_metrics = get_approval_acceptance_metrics()
    assert appr_metrics["total_items"] > 0
    assert appr_metrics["reviewed_total"] > 0
    assert 0.0 <= appr_metrics["acceptance_rate"] <= 100.0

    avg_days = get_average_completion_time_days()
    assert avg_days >= 0.0
    print(f"  -> Analytics verified: Acceptance Rate = {appr_metrics['acceptance_rate']}%, Avg Completion Time = {avg_days} days.")

    # ---------------------------------------------------------
    # 19 & 20. Weekly Report Generation & Exports
    # ---------------------------------------------------------
    print("\n[Step 19 & 20] Generating Weekly Status Report & Verifying Multi-Format Downloads...")
    from services.report_service import generate_weekly_report
    report = generate_weekly_report(days_back=7)

    assert "period_str" in report
    assert len(report["markdown"]) > 500, "Markdown report incomplete"
    assert "# MEETFLOW AI" in report["markdown"]
    assert "## 1. Executive Summary" in report["markdown"]
    assert "## 2. High-Level Portfolio Health & KPIs" in report["markdown"]

    # CSV export
    assert len(report["csv"]) > 200
    assert "Task ID,Title,Initiative,Owner,Priority,Status,Deadline,Is Overdue" in report["csv"]

    # HTML export
    assert len(report["html"]) > 500
    assert "<!DOCTYPE html>" in report["html"]
    assert "MEETFLOW AI — WEEKLY INITIATIVE STATUS REPORT" in report["html"]

    print("  -> Weekly Report successfully generated with Markdown, CSV, and HTML formats.")

    # ---------------------------------------------------------
    # 21 & 22. Restart Application & Verify SQLite Persistence
    # ---------------------------------------------------------
    print("\n[Step 21 & 22] Simulating Process Restart & Verifying SQLite Persistence...")
    # Re-import DB and query afresh using a brand new engine session
    from database.db import SessionLocal
    new_session = SessionLocal()
    try:
        persisted_task = new_session.query(Task).filter(Task.id == approved_edited_task_id).first()
        assert persisted_task is not None, "Data loss on restart! Task not found in SQLite."
        assert persisted_task.title == edited_title
        assert persisted_task.status == "Completed"

        persisted_audit = new_session.query(AuditLog).filter(
            AuditLog.entity_type == "review_queue",
            AuditLog.entity_id == item_to_edit
        ).first()
        assert persisted_audit is not None, "Audit log lost on restart!"

        print(f"  -> SQLite Persistence Confirmed: Task #{approved_edited_task_id} and governance audit logs intact across sessions.")
    finally:
        new_session.close()

    # ---------------------------------------------------------
    # EDGE CASE TESTING
    # ---------------------------------------------------------
    print("\n----------------------------------------------------------------------")
    print("RUNNING EDGE CASE ROBUSTNESS TESTS")
    print("----------------------------------------------------------------------")

    # Edge Case 1: Missing API Key / Demo Mode
    print("\n[Edge Case 1] Missing API Key / Demo Mode Fallback...")
    from ai.extractor import get_ai_config
    cfg = get_ai_config()
    print(f"  -> Current config: has_api_key={cfg['has_api_key']}, is_demo_mode={cfg['is_demo_mode']}")
    sample_res, is_d, msg_d = extract_meeting_intelligence("Elena Rostova: Let's launch the mobile beta on TestFlight by Friday.")
    assert sample_res is not None
    assert is_d is True
    assert "Demo Mode" in msg_d
    print("  -> Passed: Operates safely with deterministic output when API key is missing.")

    # Edge Case 2: Empty Transcript
    print("\n[Edge Case 2] Empty Transcript Handling...")
    empty_res, _, empty_msg = extract_meeting_intelligence("   \n\t  ")
    assert empty_res is None
    assert "empty" in empty_msg.lower()
    print(f"  -> Passed: Handled gracefully without crash: '{empty_msg}'")

    # Edge Case 3: Invalid Date in Pydantic Schema & Utilities
    print("\n[Edge Case 3] Invalid Date Resilience...")
    from ai.schemas import ExtractedActionItem, MeetingExtractionResponse
    from utils.dates import format_date_str, get_relative_deadline_str

    item_bad_date = ExtractedActionItem(
        title="Check database indexing",
        evidence="Quote from call",
        deadline="2026-99-99"  # Impossible date
    )
    assert item_bad_date.deadline is None, "Invalid calendar date should be cleaned to None!"
    
    # Utilities must not crash on malformed dates
    fmt_res = format_date_str("invalid-date-string")
    rel_res = get_relative_deadline_str("invalid-date-string")
    assert isinstance(fmt_res, str)
    assert isinstance(rel_res, str)
    print("  -> Passed: Invalid date sanitized to None; date utilities never crash.")

    # Edge Case 4: Missing Owner
    print("\n[Edge Case 4] Missing Owner Sanitization...")
    item_no_owner = ExtractedActionItem(
        title="Refactor auth middleware",
        evidence="Discussion quote",
        owner=""  # Blank owner
    )
    assert item_no_owner.owner == "Unassigned", "Empty owner must normalize to 'Unassigned'!"

    item_null_owner = ExtractedActionItem(
        title="Refactor auth middleware",
        evidence="Discussion quote",
        owner="none"
    )
    assert item_null_owner.owner == "Unassigned"
    print("  -> Passed: Missing/none/blank owners correctly defaulted to 'Unassigned'.")

    # Edge Case 5: Invalid LLM Response / Malformed JSON
    print("\n[Edge Case 5] Malformed JSON / Invalid LLM Output...")
    from ai.extractor import clean_json_string
    malformed_json_str = "```json\n{ meeting_summary: 'broken json without quotes' \n```"
    cleaned = clean_json_string(malformed_json_str)
    assert not cleaned.startswith("```")

    # Test Pydantic model_validate resilience
    broken_payload = {
        "meeting_summary": "Test recap",
        "action_items": [
            {
                "title": "",  # Empty title
                "confidence": 95,  # Percentage format instead of 0.95
                "evidence": ""  # Missing evidence
            }
        ]
    }
    validated_broken = MeetingExtractionResponse.model_validate(broken_payload)
    assert validated_broken.action_items[0].confidence == 0.95
    assert validated_broken.action_items[0].title is not None
    assert len(validated_broken.action_items[0].evidence) > 0
    print("  -> Passed: Percentage confidence (95 -> 0.95) and missing fields safely recovered.")

    # Edge Case 6: Duplicate Extraction Prevention
    print("\n[Edge Case 6] Duplicate Extraction Prevention...")
    # Run duplicate extraction on the same meeting
    dup_created_ids, dup_count = add_extraction_to_review_queue(
        meeting_id=target_meeting["id"],
        extraction=extraction
    )
    assert dup_count > 0, f"Expected duplicate detection, got {dup_count} duplicates"
    print(f"  -> Passed: Successfully detected {dup_count} duplicate item(s) and prevented queue cluttering.")

    # Edge Case 7: Empty Database Operations (Zero Data State)
    print("\n[Edge Case 7] Empty Database Stability...")
    from database.models import AIExtraction
    with get_db_session() as s:
        # Temporarily wipe
        s.query(AuditLog).delete()
        s.query(Task).delete()
        s.query(ReviewQueueItem).delete()
        s.query(AIExtraction).delete()
        s.query(Meeting).delete()
        s.query(Initiative).delete()

    # Verify services on 0 records
    kpis_zero = get_executive_kpis()
    assert kpis_zero["total_tasks"] == 0
    assert kpis_zero["completion_rate"] == 0.0
    assert kpis_zero["overdue_rate"] == 0.0

    report_zero = generate_weekly_report(days_back=7)
    assert report_zero["completed_count"] == 0
    assert len(report_zero["markdown"]) > 100
    assert len(report_zero["csv"]) > 10
    assert "<!DOCTYPE html>" in report_zero["html"]

    tasks_zero = get_all_tasks()
    assert len(tasks_zero) == 0

    print("  -> Passed: All services, KPIs, and reports function smoothly with zero records without throwing exceptions.")

    # Restore clean demo data for end-user
    print("\n[Restoration] Re-seeding Pristine Enterprise Demo Dataset...")
    seed_demo_data(force=True)
    print("  -> Pristine state restored.")

    print("\n======================================================================")
    print("[SUCCESS] ALL 22 E2E STEPS AND 7 EDGE CASE TESTS PASSED WITH 100% SUCCESS!")
    print("======================================================================")

if __name__ == "__main__":
    run_qa_suite()
