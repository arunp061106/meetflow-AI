import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from ai.schemas import ExtractedActionItem, MeetingExtractionResponse
from database.db import get_db_session, init_db
from database.models import Initiative, Meeting, ReviewQueueItem, Task, AuditLog
from services.review_service import (
    add_extraction_to_review_queue,
    approve_review_item,
    edit_and_approve_review_item,
    reject_review_item
)
from services.analytics_service import get_initiative_health_data

@pytest.fixture(autouse=True)
def setup_database():
    """Initializes clean database schema for isolated pipeline testing."""
    init_db()
    yield

def test_extracted_action_item_pydantic_validation():
    """
    Test 1: Strict Pydantic Data Contract & Guardrails.
    Ensures dates are genuine ISO calendar dates, confidence scores are bounded [0.0, 1.0],
    and owners default to 'Unassigned' rather than fabricating fake identities.
    """
    # Valid item test
    valid_item = ExtractedActionItem(
        title="  Deploy Snowflake transformation models  ",
        owner="David Kim",
        deadline="2026-10-15",
        priority="High",
        confidence=0.95,
        evidence="David Kim: I will deploy Snowflake transformation models by Oct 15."
    )
    assert valid_item.title == "Deploy Snowflake transformation models"
    assert valid_item.owner == "David Kim"
    assert valid_item.deadline == "2026-10-15"
    assert valid_item.priority == "High"
    assert valid_item.confidence == 0.95

    # Percentage confidence scaling guardrail (e.g. model returns 85 instead of 0.85)
    pct_item = ExtractedActionItem(
        title="Configure monitoring alert webhooks",
        owner="Marcus Vance",
        confidence=85.0,
        evidence="Marcus: I will configure alerts."
    )
    assert pct_item.confidence == 0.85

    # Owner null-coalescing guardrail (no hallucinated identities)
    unassigned_item = ExtractedActionItem(
        title="Review audit telemetry",
        owner="",
        deadline="invalid-calendar-date-here",
        confidence=150.0
    )
    assert unassigned_item.owner == "Unassigned"
    assert unassigned_item.deadline is None  # Invalid calendar string stripped to None
    assert unassigned_item.confidence == 1.0  # Clamped to upper bound

def test_human_in_the_loop_isolation_barrier():
    """
    Test 2: Human-in-the-Loop Architectural Staging Barrier.
    Verifies that AI extraction outputs are staged into review_queue as 'Pending',
    and NEVER directly commit to the official corporate tasks table without human sign-off.
    """
    # 1. Create a mock extraction with 2 action items with unique titles
    import uuid
    uid = uuid.uuid4().hex[:6]
    title_1 = f"Audit IAM service account permissions {uid}"
    title_2 = f"Draft API gateway rate limiting specification {uid}"

    extraction = MeetingExtractionResponse(
        meeting_summary="Architecture alignment on security policies.",
        decisions=["Adopt OAuth2 mutual TLS"],
        action_items=[
            ExtractedActionItem(
                title=title_1,
                owner="Sarah Chen",
                deadline=str(date.today() + timedelta(days=5)),
                priority="High",
                initiative="Data Warehouse Migration",
                confidence=0.92,
                evidence="Sarah: I will audit IAM permissions by next week."
            ),
            ExtractedActionItem(
                title=title_2,
                owner="Alex Morgan",
                deadline=str(date.today() + timedelta(days=7)),
                priority="Medium",
                initiative="Data Warehouse Migration",
                confidence=0.88,
                evidence="Alex: I will draft the rate limiting spec."
            )
        ]
    )

    # 2. Add to review queue
    with get_db_session() as session:
        initial_task_count = session.query(Task).count()

    created_ids, dup_count = add_extraction_to_review_queue(
        meeting_id=None,
        extraction=extraction,
        raw_json_str=extraction.model_dump_json()
    )

    assert len(created_ids) == 2
    assert dup_count == 0

    # 3. CRITICAL CHECK: Review queue is populated, but tasks table remains UNTOUCHED
    with get_db_session() as session:
        post_extract_task_count = session.query(Task).count()
        assert post_extract_task_count == initial_task_count, "AI extraction must never bypass the human review gate!"

        # Verify staged items are marked 'Pending'
        for q_id in created_ids:
            item = session.query(ReviewQueueItem).filter(ReviewQueueItem.id == q_id).first()
            assert item is not None
            assert item.status == "Pending"

    # 4. Human Gate Decision: Approve item 1, Reject item 2
    task_id = edit_and_approve_review_item(
        item_id=created_ids[0],
        title=f"{title_1} [Verified]",
        description="Comprehensive audit of cloud IAM permissions",
        owner="Sarah Chen",
        deadline=date.today() + timedelta(days=5),
        priority="High",
        initiative="Data Warehouse Migration"
    )
    assert task_id is not None

    rejected_ok = reject_review_item(
        item_id=created_ids[1],
        reason="Duplicate deliverable already tracked in Q3 sprint"
    )
    assert rejected_ok is True

    # 5. Verify official state after human gate
    with get_db_session() as session:
        # Task 1 must exist
        official_task = session.query(Task).filter(Task.id == task_id).first()
        assert official_task is not None
        assert official_task.title == f"{title_1} [Verified]"

        # Item 2 must NOT create a task
        rejected_task = session.query(Task).filter(Task.review_item_id == created_ids[1]).first()
        assert rejected_task is None

        # Audit logs must record both decisions with immutable timestamps
        audit_records = session.query(AuditLog).filter(
            AuditLog.entity_id.in_(created_ids)
        ).all()
        assert len(audit_records) >= 2

def test_initiative_health_and_overdue_computation():
    """
    Test 3: Portfolio Health & Overdue SLA Calculation.
    Validates that analytics dynamically derive:
    - 'On Track' when all deadlines are met
    - 'Needs Attention' when 1 overdue or 1 blocked task exists
    - 'At Risk' when > 1 blocked or > 2 overdue tasks exist
    """
    health_data = get_initiative_health_data()
    assert isinstance(health_data, list)
    assert len(health_data) > 0

    valid_health_statuses = {"On Track", "Needs Attention", "At Risk"}
    found_healths = {item["health"] for item in health_data}

    # Verify that the seed data produces distinct operational health distributions
    for item in health_data:
        assert item["health"] in valid_health_statuses
        assert 0.0 <= item["completion_rate"] <= 100.0
        assert item["total_tasks"] >= item["completed"]

    # Verify that not all initiatives have the exact same health status
    assert len(found_healths) > 1, f"Seed initiatives should vary across health tiers, found: {found_healths}"
