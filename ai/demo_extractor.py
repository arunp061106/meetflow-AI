from datetime import date, timedelta
from typing import Dict, Any, List
import re
from ai.schemas import MeetingExtractionResponse, ExtractedActionItem

def generate_demo_extraction(transcript: str, meeting_title: str = "", initiative_hint: str = "") -> MeetingExtractionResponse:
    """
    Deterministic fallback extractor when LLM API key is absent or DEMO_MODE is active.
    Extracts realistic, high-quality structured data from the transcript.
    """
    today = date.today()
    in_3_days = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    in_7_days = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    in_14_days = (today + timedelta(days=14)).strftime("%Y-%m-%d")

    text_lower = transcript.lower()
    title_lower = meeting_title.lower()

    # Determine default initiative
    initiative = "General Initiative"
    if "customer analytics" in text_lower or "analytics" in title_lower or "churn" in text_lower:
        initiative = "Customer Analytics Platform"
    elif "warehouse" in text_lower or "migration" in title_lower or "snowflake" in text_lower:
        initiative = "Data Warehouse Migration"
    elif "mobile" in text_lower or "ios" in text_lower or "android" in text_lower or "app" in title_lower:
        initiative = "Mobile Application Launch"
    elif "marketing" in text_lower or "campaign" in text_lower:
        initiative = "Marketing Automation"
    elif "feedback" in text_lower or "nps" in text_lower or "survey" in text_lower:
        initiative = "Customer Feedback Intelligence"
    elif initiative_hint:
        initiative = initiative_hint

    # Look for name mentions in common enterprise contexts
    potential_names = ["Sarah Chen", "Marcus Vance", "Elena Rostova", "David Kim", "Priya Patel", "Alex Morgan", "Rahul", "Jessica"]
    found_names = [name for name in potential_names if name.split()[0].lower() in text_lower]

    owner_1 = found_names[0] if len(found_names) > 0 else "Sarah Chen"
    owner_2 = found_names[1] if len(found_names) > 1 else "David Kim"
    owner_3 = found_names[2] if len(found_names) > 2 else "Marcus Vance"

    # Match sentences from transcript for realistic evidence
    sentences = [s.strip() for s in re.split(r'[.\n]+', transcript) if len(s.strip()) > 20]
    
    evidence_1 = next((s for s in sentences if any(k in s.lower() for k in ["will", "action", "prepare", "deliver", "lead"])), 
                      sentences[0] if sentences else "Action item agreed upon during working session.")
    evidence_2 = next((s for s in reversed(sentences) if any(k in s.lower() for k in ["deadline", "by", "schedule", "finalize", "review"])), 
                      sentences[min(1, len(sentences)-1)] if sentences else "Confirmed deliverable milestone during sync.")
    evidence_3 = next((s for s in sentences if any(k in s.lower() for k in ["audit", "test", "security", "deploy", "sync"])),
                      "Documented alignment on technical rollout.")

    # Tailored action items based on context
    action_items: List[ExtractedActionItem] = []

    if "mobile" in text_lower or "launch" in text_lower:
        action_items = [
            ExtractedActionItem(
                title="Finalize iOS release candidate and submit to TestFlight",
                description="Ensure release candidate v2.4 build passes all automated end-to-end regression tests before submitting to external beta.",
                owner=owner_1,
                deadline=in_3_days,
                priority="High",
                initiative="Mobile Application Launch",
                status="Not Started",
                confidence=0.96,
                evidence=evidence_1
            ),
            ExtractedActionItem(
                title="Conduct load testing for push notification service",
                description="Simulate peak load of 50,000 concurrent push events to verify message queue latency remains under 500ms.",
                owner=owner_2,
                deadline=in_7_days,
                priority="Medium",
                initiative="Mobile Application Launch",
                status="Not Started",
                confidence=0.91,
                evidence=evidence_2
            ),
            ExtractedActionItem(
                title="Prepare App Store metadata, localized screenshots, and release notes",
                description="Coordinate with design and product marketing to bundle finalized marketing assets.",
                owner="Unassigned",
                deadline=in_14_days,
                priority="Low",
                initiative="Mobile Application Launch",
                status="Not Started",
                confidence=0.84,
                evidence=evidence_3
            )
        ]
        decisions = [
            "Approved the release target date for v2.4 mobile app rollout.",
            "Agreed that push notification backend must support at least 50k concurrent requests before launch."
        ]
        risks = [
            "App Store review turnaround time may take 48-72 hours during peak holiday submission windows."
        ]
        blockers = [
            "Pending final sign-off on GDPR privacy policy disclosure from legal counsel."
        ]
        next_steps = [
            "Internal staging smoke test scheduled for Wednesday.",
            "Executive demo with Product VP on Friday."
        ]
        summary = f"The team reviewed readiness for the {initiative}. Core architectural work is largely on track, with high-priority focus centered on finalizing the iOS test build and validating push notification scalability."

    elif "warehouse" in text_lower or "migration" in text_lower or "data" in text_lower:
        action_items = [
            ExtractedActionItem(
                title="Complete schema parity audit across legacy DB and target warehouse",
                description="Execute automated row-level and column-type hash comparisons to detect discrepancies before cutting over ingestion pipelines.",
                owner=owner_1,
                deadline=in_7_days,
                priority="High",
                initiative="Data Warehouse Migration",
                status="Not Started",
                confidence=0.95,
                evidence=evidence_1
            ),
            ExtractedActionItem(
                title="Migrate remaining dbt transformation models to new cluster",
                description="Refactor custom SQL UDFs and optimize materialization strategies to control warehouse compute credits.",
                owner=owner_2,
                deadline=in_14_days,
                priority="Medium",
                initiative="Data Warehouse Migration",
                status="Not Started",
                confidence=0.92,
                evidence=evidence_2
            ),
            ExtractedActionItem(
                title="Publish migration downtime maintenance window notice to business stakeholders",
                description="Draft clear maintenance advisory outlining expected 2-hour reporting downtime.",
                owner=owner_3,
                deadline=in_3_days,
                priority="Low",
                initiative="Data Warehouse Migration",
                status="Not Started",
                confidence=0.88,
                evidence=evidence_3
            )
        ]
        decisions = [
            "Agreed to deprecate legacy nightly ETL pipeline by end of current sprint.",
            "Selected automated validation scripts over manual sampling to guarantee data integrity."
        ]
        risks = [
            "Increased query latency during dual-write reconciliation period."
        ]
        blockers = [
            "Temporary API rate limits on third-party SaaS connectors."
        ]
        next_steps = [
            "Trigger secondary backfill verification batch tonight at 02:00 UTC.",
            "Sign-off sync with BI leadership on Thursday."
        ]
        summary = f"Comprehensive review of the {initiative}. The migration pipeline has achieved 85% table coverage. Primary focus is on executing final schema parity checks and scheduling stakeholder cutover notifications."

    elif "customer" in text_lower or "churn" in text_lower or "analytics" in text_lower:
        action_items = [
            ExtractedActionItem(
                title="Deploy churn prediction model v1.2 to production scoring endpoint",
                description="Verify inference latency stays below 150ms and hook prediction scores directly into executive retention dashboard.",
                owner=owner_1,
                deadline=in_3_days,
                priority="High",
                initiative="Customer Analytics Platform",
                status="Not Started",
                confidence=0.97,
                evidence=evidence_1
            ),
            ExtractedActionItem(
                title="Configure automated Slack alerts for enterprise accounts exceeding 75% churn probability",
                description="Set up webhook integration in the Customer Success channel to prompt proactive account manager outreach.",
                owner=owner_2,
                deadline=in_7_days,
                priority="Medium",
                initiative="Customer Analytics Platform",
                status="Not Started",
                confidence=0.90,
                evidence=evidence_2
            ),
            ExtractedActionItem(
                title="Review churn cohort analysis with Customer Success Leadership",
                description="Prepare presentation slides comparing renewal trends across mid-market and enterprise tiers.",
                owner=owner_3,
                deadline=in_14_days,
                priority="Medium",
                initiative="Customer Analytics Platform",
                status="Not Started",
                confidence=0.86,
                evidence=evidence_3
            )
        ]
        decisions = [
            "Model v1.2 validated with 91.4% precision on historical customer churn test sets.",
            "Customer Success managers will receive instant high-risk alert escalations."
        ]
        risks = [
            "Possible false positives in early warning scores for newly onboarded clients."
        ]
        blockers = [
            "Awaiting write permissions on Salesforce Customer Object from CRM team."
        ]
        next_steps = [
            "Complete end-to-end integration test of alerting webhooks tomorrow morning.",
            "Run weekly cohort sync with Customer Success VP on Friday."
        ]
        summary = f"The team reviewed key deliverables for the {initiative}. Predictive modeling is showing strong validation numbers, with critical focus on deploying the real-time scoring endpoint and wiring alerts to frontline account teams."

    else:
        # Default enterprise scenario
        action_items = [
            ExtractedActionItem(
                title="Synthesize stakeholder feedback and publish revised technical requirements",
                description="Incorporate input from product management and infrastructure leads into final architectural RFC document.",
                owner=owner_1,
                deadline=in_7_days,
                priority="High",
                initiative=initiative,
                status="Not Started",
                confidence=0.94,
                evidence=evidence_1
            ),
            ExtractedActionItem(
                title="Establish operational KPI monitoring dashboard and error tracking",
                description="Configure metric collection for system throughput, latency percentiles, and failure alerting thresholds.",
                owner=owner_2,
                deadline=in_14_days,
                priority="Medium",
                initiative=initiative,
                status="Not Started",
                confidence=0.89,
                evidence=evidence_2
            ),
            ExtractedActionItem(
                title="Draft executive progress summary for monthly operations steering committee",
                description="Highlight sprint velocity, budget burn-down, and major milestones delivered this quarter.",
                owner="Unassigned",
                deadline=None,
                priority="Low",
                initiative=initiative,
                status="Not Started",
                confidence=0.82,
                evidence=evidence_3
            )
        ]
        decisions = [
            f"Approved scope and resource allocation for current {initiative} sprint cycle.",
            "Standardized team reporting on weekly executive dashboard metrics."
        ]
        risks = [
            "Cross-team dependency on platform security team for architectural review sign-off."
        ]
        blockers = [
            "Pending approval for cloud compute sandbox expansion."
        ]
        next_steps = [
            "Circulate finalized technical RFC by Thursday close of business.",
            "Reconvene for bi-weekly milestone check-in next Monday."
        ]
        summary = f"Working session on {meeting_title or initiative}. The team aligned on deliverable milestones, finalized key technical trade-offs, and agreed on explicit assignments for upcoming delivery targets."

    return MeetingExtractionResponse(
        meeting_summary=summary,
        decisions=decisions,
        risks=risks,
        blockers=blockers,
        next_steps=next_steps,
        action_items=action_items
    )
