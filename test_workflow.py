import sys
from datetime import date, datetime, timedelta

def test_full_pipeline():
    print("--- 1. Testing Database & Seeding ---")
    from database.db import init_db, get_db_session
    from database.models import Initiative, Meeting, Task, ReviewQueueItem, AuditLog
    from database.seed import seed_demo_data

    init_db()
    seed_demo_data(force=True)

    with get_db_session() as s:
        init_cnt = s.query(Initiative).count()
        meet_cnt = s.query(Meeting).count()
        task_cnt = s.query(Task).count()
        rev_cnt = s.query(ReviewQueueItem).count()
        print(f"Initial State: {init_cnt} Initiatives, {meet_cnt} Meetings, {task_cnt} Tasks, {rev_cnt} Review Items")
        assert init_cnt >= 5, "Expected at least 5 initiatives"
        assert meet_cnt >= 8, "Expected at least 8 meetings"
        assert task_cnt >= 30, "Expected at least 30 tasks"
        assert rev_cnt >= 10, "Expected at least 10 review items"

    print("\n--- 2. Testing AI Extraction Engine (Demo Mode) ---")
    from ai.extractor import extract_meeting_intelligence
    sample_text = """Sarah Chen: Let's finalize the churn prediction model deployment by Friday.
David Kim: I will deploy the v1.2 scoring endpoint to production by Friday.
Marcus Vance: I'll configure the webhook trigger and payload format for Slack alerts by next Tuesday."""

    result, is_demo, msg = extract_meeting_intelligence(
        transcript=sample_text,
        meeting_title="Churn Deployment Sync",
        initiative_hint="Customer Analytics Platform"
    )
    assert result is not None, "Extraction result should not be None"
    assert len(result.action_items) > 0, "Expected extracted action items"
    print(f"Extraction successful: {len(result.action_items)} action items extracted. Mode: {'Demo' if is_demo else 'Live LLM'}")
    print(f"Sample extracted item: '{result.action_items[0].title}' | Owner: {result.action_items[0].owner} | Confidence: {result.action_items[0].confidence}")

    print("\n--- 3. Testing Review Queue Staging (Human-in-the-Loop Isolation) ---")
    from services.review_service import add_extraction_to_review_queue, get_review_queue_items
    with get_db_session() as s:
        pre_tasks = s.query(Task).count()

    created_ids = add_extraction_to_review_queue(
        meeting_id=1,
        extraction=result
    )
    assert len(created_ids) == len(result.action_items), "Review queue items created count mismatch"

    with get_db_session() as s:
        post_tasks = s.query(Task).count()
        # CRITICAL TEST: tasks table must NOT increase upon AI extraction!
        assert pre_tasks == post_tasks, f"VIOLATION: Tasks table changed from {pre_tasks} to {post_tasks} before human approval!"
    print(f"Verified Human-in-the-loop isolation: {len(created_ids)} items staged into Review Queue. Task count remained strictly at {post_tasks}.")

    print("\n--- 4. Testing Quick Approval Workflow ---")
    from services.review_service import approve_review_item
    item_to_approve = created_ids[0]
    approved_task_id = approve_review_item(item_to_approve)
    assert approved_task_id is not None, "Expected task id after approval"

    with get_db_session() as s:
        q_item = s.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_to_approve).first()
        assert q_item.status == "Approved", f"Expected Approved status, got {q_item.status}"
        assert q_item.reviewer_action == "APPROVE"
        
        official_task = s.query(Task).filter(Task.id == approved_task_id).first()
        assert official_task is not None, "Official task should exist in DB"
        assert official_task.title == q_item.title
    print(f"Verified Quick Approval: Item #{item_to_approve} converted to Official Task #{approved_task_id}.")

    print("\n--- 5. Testing Edit & Approve Workflow ---")
    from services.review_service import edit_and_approve_review_item
    item_to_edit = created_ids[1] if len(created_ids) > 1 else created_ids[0]
    edited_task_id = edit_and_approve_review_item(
        item_id=item_to_edit,
        title="Custom Edited High Priority Task",
        description="Modified by senior engineer",
        owner="Elena Rostova",
        deadline=date.today() + timedelta(days=5),
        priority="High",
        initiative="Customer Analytics Platform"
    )
    assert edited_task_id is not None
    with get_db_session() as s:
        q_item = s.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_to_edit).first()
        assert q_item.status == "Edited & Approved"
        official_task = s.query(Task).filter(Task.id == edited_task_id).first()
        assert official_task.title == "Custom Edited High Priority Task"
        assert official_task.owner == "Elena Rostova"
        assert official_task.priority == "High"
    print(f"Verified Edit & Approve: Item #{item_to_edit} updated and authorized as Task #{edited_task_id}.")

    print("\n--- 6. Testing Reject Workflow ---")
    from services.review_service import reject_review_item
    if len(created_ids) > 2:
        item_to_reject = created_ids[2]
        with get_db_session() as s:
            pre_tasks_count = s.query(Task).count()

        ok = reject_review_item(item_to_reject, reason="Not a priority for this quarter")
        assert ok is True

        with get_db_session() as s:
            q_item = s.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_to_reject).first()
            assert q_item.status == "Rejected"
            post_tasks_count = s.query(Task).count()
            # Must NOT enter tasks table!
            assert pre_tasks_count == post_tasks_count, "Rejected item must not create a task!"
        print(f"Verified Reject: Item #{item_to_reject} rejected and successfully excluded from official tracker.")

    print("\n--- 7. Testing Task Status Updates & Overdue Calculations ---")
    from services.task_service import update_task_status, get_all_tasks
    update_task_status(approved_task_id, "In Progress")
    update_task_status(approved_task_id, "Completed")
    with get_db_session() as s:
        t = s.query(Task).filter(Task.id == approved_task_id).first()
        assert t.status == "Completed"
        assert t.completed_at is not None

    tasks_list = get_all_tasks()
    overdue_found = [t for t in tasks_list if t["is_overdue"]]
    assert len(overdue_found) > 0, "Expected overdue tasks in demo dataset"
    print(f"Verified Overdue calculations: Found {len(overdue_found)} overdue tasks correctly detected.")

    print("\n--- 8. Testing Weekly Status Report Generation & Exports ---")
    from services.report_service import generate_weekly_report
    report = generate_weekly_report(days_back=7)
    assert "period_str" in report
    assert len(report["markdown"]) > 200, "Markdown report too short"
    assert len(report["csv"]) > 50, "CSV export too short"
    assert "<!DOCTYPE html>" in report["html"], "HTML export missing DOCTYPE"
    print("Verified Weekly Report generation: Markdown, CSV, and HTML exports successfully generated.")

    print("[SUCCESS] ALL PIPELINE VERIFICATIONS PASSED WITH 100% SUCCESS!")
    print("========================================================")

if __name__ == "__main__":
    test_full_pipeline()
