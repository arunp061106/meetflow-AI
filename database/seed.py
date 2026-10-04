from datetime import datetime, date, timedelta
from database.db import get_db_session, init_db
from database.models import Initiative, Meeting, ReviewQueueItem, Task, AuditLog, AIExtraction

def seed_demo_data(force: bool = False):
    """
    Populates SQLite database with comprehensive enterprise demo data.
    If database already has records and force is False, skip seeding.
    """
    init_db()

    with get_db_session() as session:
        existing_init_count = session.query(Initiative).count()
        if existing_init_count > 0 and not force:
            return False  # Already seeded

        # Clear existing data if forced
        if force:
            session.query(AuditLog).delete()
            session.query(Task).delete()
            session.query(ReviewQueueItem).delete()
            session.query(AIExtraction).delete()
            session.query(Meeting).delete()
            session.query(Initiative).delete()
            session.flush()

        today = date.today()

        # Strategic programs and portfolio workstreams
        initiatives = [

            Initiative(
                name="Customer Analytics Platform",
                description="Consolidated customer intelligence engine providing real-time churn prediction, cohort retention, and lifetime value analytics.",
                owner="Sarah Chen",
                status="Active",
                created_at=datetime.utcnow() - timedelta(days=45)
            ),
            Initiative(
                name="Data Warehouse Migration",
                description="Enterprise-wide transition from legacy on-premise PostgreSQL to high-concurrency cloud Snowflake data warehouse.",
                owner="David Kim",
                status="Active",
                created_at=datetime.utcnow() - timedelta(days=60)
            ),
            Initiative(
                name="Mobile Application Launch",
                description="Cross-platform iOS and Android mobile app rollout with biometrics, instant sync, and offline task caching.",
                owner="Elena Rostova",
                status="Active",
                created_at=datetime.utcnow() - timedelta(days=40)
            ),
            Initiative(
                name="Marketing Automation",
                description="Omnichannel lifecycle marketing integration connecting Segment event streams with Braze campaign automation.",
                owner="Marcus Vance",
                status="Active",
                created_at=datetime.utcnow() - timedelta(days=35)
            ),
            Initiative(
                name="Customer Feedback Intelligence",
                description="Automated AI pipeline ingesting support Zendesk tickets, Trustpilot reviews, and NPS feedback into prioritized feature clusters.",
                owner="Priya Patel",
                status="Active",
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
        ]
        session.add_all(initiatives)
        session.flush()

        # Historical meetings and transcripts
        meetings_data = [
            {
                "title": "Weekly Product Review",
                "meeting_date": today - timedelta(days=2),
                "meeting_type": "Project Review",
                "organizer": "Sarah Chen",
                "participants": "Sarah Chen, Marcus Vance, Elena Rostova, David Kim, Priya Patel",
                "initiative": "Customer Analytics Platform",
                "transcript": """Sarah Chen: Thanks everyone for joining the weekly product review. Let's start with churn prediction v1.2. David, how is the model inference latency holding up?
David Kim: The latency is averaging 115ms on the staging cluster. We tested with 10k synthetic users and saw zero timeouts. I will deploy the v1.2 scoring endpoint to production by Friday.
Sarah Chen: Excellent. Marcus, once that's live, we need automated Slack alerts sent to the Customer Success pod whenever an enterprise tier account crosses the 75% risk threshold. Can you lead that?
Marcus Vance: Yes, I can take that on. I'll configure the webhook trigger and payload format by next Tuesday.
Elena Rostova: On the mobile front, we noticed some memory leaks when rendering live analytics charts on iOS devices. I've asked Alex to profile the SwiftUI render cycle before Thursday.
Priya Patel: We also gathered feedback from the VIP user cohort. They requested dark mode for the analytics dashboard. I will organize those design specifications into an RFC by end of week.""",
                "summary": "Reviewed churn prediction model latency benchmarks and approved production deployment. Assigned webhook alerts to Customer Success and initiated iOS chart memory profiling."
            },
            {
                "title": "Data Platform Sprint Planning",
                "meeting_date": today - timedelta(days=4),
                "meeting_type": "Sprint Planning",
                "organizer": "David Kim",
                "participants": "David Kim, Sarah Chen, Alex Morgan",
                "initiative": "Data Warehouse Migration",
                "transcript": """David Kim: Welcome to Sprint 34 planning for the data warehouse migration. Our primary goal this sprint is completing schema parity testing.
Alex Morgan: I've prepared the automated reconciliation script for the transaction tables. However, we have a mismatch in timestamp precision between the legacy DB and Snowflake.
David Kim: Good catch. Alex, please write a transformation adapter in dbt to standardize UTC microsecond timestamps by Wednesday.
Sarah Chen: What about the financial reporting tables? Finance needs sign-off before month-end close.
David Kim: I will personally run the reconciliation audit on the billing tables and share the validation summary with the Finance VP by Monday.""",
                "summary": "Sprint 34 kickoff prioritized timestamp precision standardization in dbt and billing table reconciliation ahead of Finance VP sign-off."
            },
            {
                "title": "Customer Analytics Review",
                "meeting_date": today - timedelta(days=6),
                "meeting_type": "Management Review",
                "organizer": "Sarah Chen",
                "participants": "Sarah Chen, David Kim, Marcus Vance, CFO",
                "initiative": "Customer Analytics Platform",
                "transcript": """Sarah Chen: Good morning. We're here to evaluate Q3 customer churn analytics metrics. Our predictive model successfully identified 82% of at-risk renewals last month.
Marcus Vance: Retention campaigns triggered by the churn warning yielded a 14% save rate across tier-2 accounts.
CFO: Impressive numbers. What are the key blockers to scaling this across the enterprise segment?
Sarah Chen: We need deeper integration with Salesforce account health records. David, can your team build the daily bidirectional sync connector?
David Kim: Yes. We will start work on the Salesforce REST API sync connector and aim for a sandbox demo in 10 days.""",
                "summary": "Validated 82% churn identification accuracy and 14% save rate. Commissioned bidirectional Salesforce CRM synchronization pipeline."
            },
            {
                "title": "Marketing Performance Review",
                "meeting_date": today - timedelta(days=8),
                "meeting_type": "Team Meeting",
                "organizer": "Marcus Vance",
                "participants": "Marcus Vance, Priya Patel, Alex Morgan",
                "initiative": "Marketing Automation",
                "transcript": """Marcus Vance: Let's review the onboarding email drip automation. Open rates increased from 24% to 38% following subject line personalization.
Priya Patel: We noticed drop-offs at step 4 (API key generation). Users get stuck waiting for verification emails.
Marcus Vance: That is critical. Priya, please draft revised copy and interactive guide tooltips for the API onboarding modal by Thursday.
Alex Morgan: I will inspect the transactional email deliverability logs to ensure SendGrid isn't queuing messages during peak hours.""",
                "summary": "Analyzed onboarding conversion funnel metrics. Action items created for UI tooltip copy and SendGrid delivery latency investigation."
            },
            {
                "title": "Mobile App Launch Readiness",
                "meeting_date": today - timedelta(days=10),
                "meeting_type": "Project Review",
                "organizer": "Elena Rostova",
                "participants": "Elena Rostova, Sarah Chen, David Kim, Alex Morgan",
                "initiative": "Mobile Application Launch",
                "transcript": """Elena Rostova: Team, we are 18 days from our public App Store and Google Play launch date. Here is the readiness checklist.
Alex Morgan: Build 2.4.0 passed the automated UI tests on 14 simulated device configurations. However, biometric login occasionally stalls on Android 12.
Elena Rostova: Alex, that cannot ship. Please isolate the Android biometric prompt deadlock and commit a hotfix by Wednesday.
David Kim: Backend push notification servers are provisioned with autoscaling policies up to 40 pods.
Sarah Chen: I will coordinate the customer communications blast and PR announcement schedule with our marketing director.""",
                "summary": "Reviewed 18-day countdown to app launch. Flagged Android biometric deadlock as high-priority blocker requiring hotfix."
            },
            {
                "title": "Executive Operations Review",
                "meeting_date": today - timedelta(days=12),
                "meeting_type": "Management Review",
                "organizer": "Sarah Chen",
                "participants": "Sarah Chen, Elena Rostova, Marcus Vance, David Kim, Priya Patel",
                "initiative": "Customer Analytics Platform",
                "transcript": """Sarah Chen: Looking at overall initiative velocity across the portfolio. Data Warehouse migration is currently pacing slightly ahead of schedule.
Elena Rostova: Mobile launch is 90% ready, pending the biometric patch.
Marcus Vance: We experienced a brief API rate limit on our customer feedback scraper last night. Priya has contacted Twitter and Reddit developer support.
Sarah Chen: Let's ensure all team leads review their overdue deliverables before the upcoming steering committee meeting next Tuesday.""",
                "summary": "Executive review of all 5 strategic initiatives. Overall delivery velocity healthy; monitored API rate limit incidents on social scrapers."
            },
            {
                "title": "Customer Feedback Workshop",
                "meeting_date": today - timedelta(days=14),
                "meeting_type": "Client Meeting",
                "organizer": "Priya Patel",
                "participants": "Priya Patel, Sarah Chen, 4 Enterprise Customers",
                "initiative": "Customer Feedback Intelligence",
                "transcript": """Priya Patel: Thank you to our enterprise steering group partners. Today we walked through the AI feedback clustering dashboard.
Customer Lead: We love the automated sentiment categorization, but we desperately need export capabilities to CSV and Tableau.
Priya Patel: Understood. I will submit a product requirement ticket for multi-format export and track it for Sprint 35.
Sarah Chen: We will also set up dedicated role-based permission tiers so external partners can view sanitized feedback trends.""",
                "summary": "Conducted feedback workshop with key enterprise partners. Identified high customer demand for Tableau connector and CSV export."
            },
            {
                "title": "Engineering Planning Meeting",
                "meeting_date": today - timedelta(days=16),
                "meeting_type": "Team Meeting",
                "organizer": "David Kim",
                "participants": "David Kim, Alex Morgan, Elena Rostova",
                "initiative": "Data Warehouse Migration",
                "transcript": """David Kim: Let's discuss infrastructure cost controls for the new Snowflake warehouse. Our query compute costs spiked by 22% during last week's backfill.
Alex Morgan: Some ad-hoc analyst queries were running full table scans on unpartitioned event tables.
David Kim: Alex, please implement automatic clustering keys on the event_timestamp column and configure query auto-suspension timeouts to 5 minutes.
Elena Rostova: We should also establish a cloud spend alert in Datadog when daily warehouse spend exceeds $400.""",
                "summary": "Formulated compute cost optimization plan for Snowflake. Mandated clustering keys, 5-minute auto-suspension, and Datadog budget alerting."
            }
        ]

        meetings = []
        for m_dict in meetings_data:
            m = Meeting(
                title=m_dict["title"],
                meeting_date=m_dict["meeting_date"],
                meeting_type=m_dict["meeting_type"],
                organizer=m_dict["organizer"],
                participants=m_dict["participants"],
                initiative=m_dict["initiative"],
                transcript=m_dict["transcript"],
                summary=m_dict["summary"],
                created_at=datetime.utcnow() - timedelta(days=(today - m_dict["meeting_date"]).days)
            )
            session.add(m)
            meetings.append(m)
        session.flush()

        # Official tasks and deliverables
        tasks_data = [
            # Customer Analytics Platform
            {
                "title": "Deploy churn prediction model v1.2 endpoint to production cluster",
                "description": "Expose REST inference endpoint behind Kubernetes ingress with automatic horizontal pod autoscaling.",
                "owner": "David Kim",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Customer Analytics Platform",
                "deadline": today + timedelta(days=3),
                "meeting_id": meetings[0].id,
                "days_ago_created": 3
            },
            {
                "title": "Configure Slack webhook notifications for enterprise churn risk scores > 75%",
                "description": "Send structured alert cards to #customer-success-alerts with account manager tag and retention playbook link.",
                "owner": "Marcus Vance",
                "priority": "High",
                "status": "Not Started",
                "initiative": "Customer Analytics Platform",
                "deadline": today + timedelta(days=5),
                "meeting_id": meetings[0].id,
                "days_ago_created": 3
            },
            {
                "title": "Compile Q3 Customer Churn cohort retrospective slide deck",
                "description": "Summarize churn drivers across SMB, Mid-Market, and Enterprise tiers for C-level presentation.",
                "owner": "Sarah Chen",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Customer Analytics Platform",
                "deadline": today - timedelta(days=2),
                "meeting_id": meetings[2].id,
                "days_ago_created": 10,
                "completed_days_ago": 1
            },
            {
                "title": "Build bidirectional Salesforce REST API sync connector",
                "description": "Sync customer health score and churn risk into Salesforce Account custom fields.",
                "owner": "David Kim",
                "priority": "High",
                "status": "Completed",
                "initiative": "Customer Analytics Platform",
                "deadline": today - timedelta(days=1),
                "meeting_id": meetings[2].id,
                "days_ago_created": 8,
                "completed_days_ago": 1
            },
            {
                "title": "Design executive churn retention dashboard mockups in Figma",
                "description": "Create high-fidelity executive views with weekly retention curves and drill-downs.",
                "owner": "Priya Patel",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Customer Analytics Platform",
                "deadline": today - timedelta(days=5),
                "meeting_id": meetings[0].id,
                "days_ago_created": 14,
                "completed_days_ago": 4
            },
            {
                "title": "Draft RFC for customer lifetime value (LTV) predictive model",
                "description": "Specify feature engineering requirements, training set cutoff dates, and evaluation metrics.",
                "owner": "Sarah Chen",
                "priority": "Low",
                "status": "In Progress",
                "initiative": "Customer Analytics Platform",
                "deadline": today + timedelta(days=12),
                "meeting_id": meetings[0].id,
                "days_ago_created": 2
            },
            {
                "title": "Audit churn training set for data leakage in cancellation event timestamps",
                "description": "Validate that features do not incorporate future data beyond the prediction observation window.",
                "owner": "David Kim",
                "priority": "High",
                "status": "Completed",
                "initiative": "Customer Analytics Platform",
                "deadline": today - timedelta(days=7),
                "meeting_id": meetings[2].id,
                "days_ago_created": 16,
                "completed_days_ago": 6
            },

            # Data Warehouse Migration
            {
                "title": "Standardize UTC microsecond timestamp transformations in dbt",
                "description": "Refactor dbt macros to cast all incoming staging timestamps to UTC timezone explicitly.",
                "owner": "Alex Morgan",
                "priority": "High",
                "status": "Completed",
                "initiative": "Data Warehouse Migration",
                "deadline": today - timedelta(days=1),
                "meeting_id": meetings[1].id,
                "days_ago_created": 6,
                "completed_days_ago": 1
            },
            {
                "title": "Execute automated reconciliation script across billing tables",
                "description": "Run checksum validation comparing PostgreSQL billing records with Snowflake mirror tables.",
                "owner": "David Kim",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Data Warehouse Migration",
                "deadline": today + timedelta(days=2),
                "meeting_id": meetings[1].id,
                "days_ago_created": 4
            },
            {
                "title": "Implement automatic clustering keys on event_timestamp column in Snowflake",
                "description": "Optimize partition pruning for 500M+ event rows to prevent full table scans and control compute costs.",
                "owner": "Alex Morgan",
                "priority": "Medium",
                "status": "In Progress",
                "initiative": "Data Warehouse Migration",
                "deadline": today + timedelta(days=4),
                "meeting_id": meetings[7].id,
                "days_ago_created": 5
            },
            {
                "title": "Configure 5-minute auto-suspension timeout on Snowflake development warehouses",
                "description": "Reduce warehouse idle runtime across engineering teams to prevent budget overruns.",
                "owner": "David Kim",
                "priority": "Low",
                "status": "Completed",
                "initiative": "Data Warehouse Migration",
                "deadline": today - timedelta(days=3),
                "meeting_id": meetings[7].id,
                "days_ago_created": 12,
                "completed_days_ago": 2
            },
            {
                "title": "Deliver signed-off Finance reconciliation audit report to CFO",
                "description": "Provide certified variance statement (<0.001% acceptable ledger delta) for Q2 financial records.",
                "owner": "David Kim",
                "priority": "High",
                "status": "Blocked",
                "initiative": "Data Warehouse Migration",
                "deadline": today - timedelta(days=3),  # Overdue & Blocked
                "meeting_id": meetings[1].id,
                "days_ago_created": 10
            },
            {
                "title": "Migrate marketing event stream Kafka consumer to Snowflake stage",
                "description": "Update Snowpipe ingest consumer to stream raw JSON web events continuously.",
                "owner": "Alex Morgan",
                "priority": "Medium",
                "status": "Blocked",
                "initiative": "Data Warehouse Migration",
                "deadline": today - timedelta(days=2),  # Overdue & Blocked
                "meeting_id": meetings[7].id,
                "days_ago_created": 4
            },
            {
                "title": "Publish warehouse cutover maintenance window advisory to business units",
                "description": "Send formal email notification regarding planned 2-hour BI dashboard downtime on cutover Sunday.",
                "owner": "Sarah Chen",
                "priority": "Low",
                "status": "Not Started",
                "initiative": "Data Warehouse Migration",
                "deadline": today - timedelta(days=1),  # Overdue
                "meeting_id": meetings[1].id,
                "days_ago_created": 3
            },

            # Mobile Application Launch
            {
                "title": "Isolate and commit hotfix for Android 12 biometric authentication deadlock",
                "description": "Resolve thread blocking race condition when BiometricPrompt callback fires before UI initialization.",
                "owner": "Alex Morgan",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Mobile Application Launch",
                "deadline": today + timedelta(days=1),
                "meeting_id": meetings[4].id,
                "days_ago_created": 5
            },
            {
                "title": "Profile and eliminate SwiftUI chart memory leak on iOS 17 devices",
                "description": "Instruments analysis of view redraw allocations on live streaming analytics canvas.",
                "owner": "Elena Rostova",
                "priority": "High",
                "status": "Completed",
                "initiative": "Mobile Application Launch",
                "deadline": today - timedelta(days=1),
                "meeting_id": meetings[0].id,
                "days_ago_created": 4,
                "completed_days_ago": 1
            },
            {
                "title": "Submit iOS Release Candidate build v2.4.0 to Apple TestFlight beta",
                "description": "Trigger fastlane release pipeline with release notes and invite internal employee testers.",
                "owner": "Elena Rostova",
                "priority": "High",
                "status": "Not Started",
                "initiative": "Mobile Application Launch",
                "deadline": today + timedelta(days=4),
                "meeting_id": meetings[4].id,
                "days_ago_created": 3
            },
            {
                "title": "Configure push notification backend load testing with 50k concurrent sessions",
                "description": "Locust stress test against Apple APNs and Firebase Cloud Messaging gateway.",
                "owner": "David Kim",
                "priority": "Medium",
                "status": "In Progress",
                "initiative": "Mobile Application Launch",
                "deadline": today + timedelta(days=6),
                "meeting_id": meetings[4].id,
                "days_ago_created": 6
            },
            {
                "title": "Prepare App Store and Google Play screenshots with localized captions",
                "description": "Generate marketing frames for 6.7-inch and 6.1-inch iPhone displays and modern Android viewports.",
                "owner": "Priya Patel",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Mobile Application Launch",
                "deadline": today - timedelta(days=4),
                "meeting_id": meetings[4].id,
                "days_ago_created": 15,
                "completed_days_ago": 3
            },
            {
                "title": "Complete GDPR consent banner audit for mobile analytics telemetry",
                "description": "Verify opt-out toggle completely halts Mixpanel and Datadog RUM network requests on launch.",
                "owner": "Elena Rostova",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Mobile Application Launch",
                "deadline": today - timedelta(days=2),  # Overdue
                "meeting_id": meetings[4].id,
                "days_ago_created": 9
            },
            {
                "title": "Finalize mobile crash reporting alerting rules in Sentry",
                "description": "Escalate alerts to on-call Slack channel when crash-free session rate falls below 99.5%.",
                "owner": "Alex Morgan",
                "priority": "Low",
                "status": "Completed",
                "initiative": "Mobile Application Launch",
                "deadline": today - timedelta(days=6),
                "meeting_id": meetings[4].id,
                "days_ago_created": 18,
                "completed_days_ago": 5
            },

            # Marketing Automation
            {
                "title": "Draft revised onboarding copy and interactive tooltips for API key modal",
                "description": "Provide clear step-by-step guidance on copying secret keys and webhook endpoints.",
                "owner": "Priya Patel",
                "priority": "Medium",
                "status": "In Progress",
                "initiative": "Marketing Automation",
                "deadline": today + timedelta(days=2),
                "meeting_id": meetings[3].id,
                "days_ago_created": 4
            },
            {
                "title": "Inspect SendGrid deliverability logs for high latency queuing events",
                "description": "Verify bounce rates and ISP throttling policies during morning 09:00 blast windows.",
                "owner": "Alex Morgan",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Marketing Automation",
                "deadline": today - timedelta(days=2),
                "meeting_id": meetings[3].id,
                "days_ago_created": 7,
                "completed_days_ago": 2
            },
            {
                "title": "Deploy Braze omnichannel push webhook connector for dormant user re-engagement",
                "description": "Trigger re-engagement emails after 14 days of inactivity with personalized recommendations.",
                "owner": "Marcus Vance",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Marketing Automation",
                "deadline": today + timedelta(days=7),
                "meeting_id": meetings[3].id,
                "days_ago_created": 5
            },
            {
                "title": "Set up UTM campaign parameter attribution tracking in Segment",
                "description": "Ensure incoming signups carry source, medium, and campaign tags through to customer DB.",
                "owner": "Marcus Vance",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Marketing Automation",
                "deadline": today - timedelta(days=8),
                "meeting_id": meetings[3].id,
                "days_ago_created": 20,
                "completed_days_ago": 7
            },
            {
                "title": "Resolve third-party tracking cookie deprecation warnings in Safari/Firefox",
                "description": "Migrate client-side pixel events to server-side Segment Connections pipeline.",
                "owner": "David Kim",
                "priority": "Low",
                "status": "Not Started",
                "initiative": "Marketing Automation",
                "deadline": today + timedelta(days=15),
                "meeting_id": meetings[3].id,
                "days_ago_created": 2
            },
            {
                "title": "A/B test subject lines for weekly executive digest newsletter",
                "description": "Compare open rates between metric-focused subject line vs curiosity-driven subject line.",
                "owner": "Marcus Vance",
                "priority": "Low",
                "status": "Completed",
                "initiative": "Marketing Automation",
                "deadline": today - timedelta(days=10),
                "meeting_id": meetings[3].id,
                "days_ago_created": 22,
                "completed_days_ago": 9
            },

            # Customer Feedback Intelligence
            {
                "title": "Submit product requirements ticket for CSV and Tableau feedback exports",
                "description": "Specify filtered data download schemas including cluster name, sentiment score, and raw quotes.",
                "owner": "Priya Patel",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today - timedelta(days=1),
                "meeting_id": meetings[6].id,
                "days_ago_created": 8,
                "completed_days_ago": 1
            },
            {
                "title": "Implement role-based access control for sanitized partner feedback trends",
                "description": "Ensure PII (customer email, phone, IP) is strictly masked for external collaborator accounts.",
                "owner": "Sarah Chen",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today + timedelta(days=5),
                "meeting_id": meetings[6].id,
                "days_ago_created": 6
            },
            {
                "title": "Resolve API rate limit backoff logic on Zendesk support ticket scraper",
                "description": "Implement exponential backoff and Redis-based rate limit token bucket to prevent HTTP 429 errors.",
                "owner": "David Kim",
                "priority": "High",
                "status": "Completed",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today - timedelta(days=3),
                "meeting_id": meetings[5].id,
                "days_ago_created": 10,
                "completed_days_ago": 2
            },
            {
                "title": "Fine-tune feedback sentiment classification model on domain specific vocabulary",
                "description": "Label 1,000 domain phrases to improve model recall on subtle enterprise usability feedback.",
                "owner": "Sarah Chen",
                "priority": "Medium",
                "status": "Not Started",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today + timedelta(days=11),
                "meeting_id": meetings[6].id,
                "days_ago_created": 3
            },
            {
                "title": "Automate weekly NPS summary digest email to department heads",
                "description": "Compile top 3 detractors and top 3 promoters with direct links to verbatim quotes.",
                "owner": "Priya Patel",
                "priority": "Low",
                "status": "In Progress",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today + timedelta(days=8),
                "meeting_id": meetings[6].id,
                "days_ago_created": 4
            },
            {
                "title": "Resolve Trustpilot webhook timeout when ingesting negative reviews",
                "description": "Offload review processing to Celery background task queue rather than synchronous HTTP handler.",
                "owner": "Alex Morgan",
                "priority": "High",
                "status": "In Progress",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today - timedelta(days=2),  # Overdue
                "meeting_id": meetings[5].id,
                "days_ago_created": 9
            },
            {
                "title": "Conduct user interview with Tier-1 customer success reps on feedback dashboard usability",
                "description": "Identify workflow bottlenecks and feature requests for upcoming Q4 roadmap.",
                "owner": "Priya Patel",
                "priority": "Low",
                "status": "Completed",
                "initiative": "Customer Feedback Intelligence",
                "deadline": today - timedelta(days=12),
                "meeting_id": meetings[6].id,
                "days_ago_created": 25,
                "completed_days_ago": 11
            },
            {
                "title": "Establish Datadog alert monitor for cloud spend exceeding $400/day threshold",
                "description": "Notify #finops-alerts and trigger automatic warning email to data engineering lead.",
                "owner": "Elena Rostova",
                "priority": "Medium",
                "status": "Completed",
                "initiative": "Data Warehouse Migration",
                "deadline": today - timedelta(days=5),
                "meeting_id": meetings[7].id,
                "days_ago_created": 14,
                "completed_days_ago": 4
            }
        ]

        created_tasks = []
        for t_dict in tasks_data:
            c_time = datetime.utcnow() - timedelta(days=t_dict["days_ago_created"])
            comp_time = None
            if t_dict["status"] == "Completed" and "completed_days_ago" in t_dict:
                comp_time = datetime.utcnow() - timedelta(days=t_dict["completed_days_ago"])
            elif t_dict["status"] == "Completed":
                comp_time = datetime.utcnow() - timedelta(days=1)

            task_obj = Task(
                review_item_id=None,
                meeting_id=t_dict.get("meeting_id"),
                title=t_dict["title"],
                description=t_dict["description"],
                owner=t_dict["owner"],
                deadline=t_dict["deadline"],
                priority=t_dict["priority"],
                initiative=t_dict["initiative"],
                status=t_dict["status"],
                created_at=c_time,
                updated_at=comp_time or c_time,
                completed_at=comp_time
            )
            session.add(task_obj)
            created_tasks.append(task_obj)
        session.flush()

        # Candidate action items extracted from recent meetings
        review_queue_data = [
            {
                "title": "Deploy churn prediction model v1.2 endpoint to production cluster",
                "description": "Expose REST inference endpoint behind Kubernetes ingress with automatic horizontal pod autoscaling.",
                "owner": "David Kim",
                "deadline": today + timedelta(days=3),
                "priority": "High",
                "initiative": "Customer Analytics Platform",
                "confidence": 0.95,
                "evidence": "David Kim: 'I will deploy the churn model v1.2 to the production cluster by Thursday.'",
                "meeting_id": meetings[0].id,
                "status": "Approved",
                "reviewer_action": "APPROVE",
                "reviewed_at": datetime.utcnow() - timedelta(days=3),
                "days_ago_created": 3,
                "linked_task_idx": 0
            },
            {
                "title": "Configure Slack webhook notifications for enterprise churn risk scores > 75%",
                "description": "Send structured alert cards to #customer-success-alerts with account manager tag and retention playbook link.",
                "owner": "Marcus Vance",
                "deadline": today + timedelta(days=5),
                "priority": "High",
                "initiative": "Customer Analytics Platform",
                "confidence": 0.91,
                "evidence": "Marcus Vance: 'I will set up the Slack alerts for high-risk accounts once the webhook is configured.'",
                "meeting_id": meetings[0].id,
                "status": "Edited & Approved",
                "reviewer_action": "EDIT & APPROVE",
                "reviewed_at": datetime.utcnow() - timedelta(days=3),
                "days_ago_created": 3,
                "linked_task_idx": 1
            },
            {
                "title": "Coordinate weekly lunch catering menu with local vendor for sprint demo",
                "description": "Collect dietary restrictions and submit weekly team lunch order for Thursday sprint demo session.",
                "owner": "Sarah Chen",
                "deadline": today - timedelta(days=2),
                "priority": "Low",
                "initiative": "Customer Analytics Platform",
                "confidence": 0.78,
                "evidence": "Someone mentioned ordering catering for Thursday's retrospective presentation.",
                "meeting_id": meetings[2].id,
                "status": "Rejected",
                "reviewer_action": "REJECT",
                "reviewed_at": datetime.utcnow() - timedelta(days=4),
                "days_ago_created": 4,
                "linked_task_idx": None
            },
            {
                "title": "Audit third-party JavaScript tracking scripts for GDPR consent compliance",
                "description": "Review Google Tag Manager and Segment client libraries to ensure no marketing pixels fire before user clicks 'Accept All'.",
                "owner": "Elena Rostova",
                "deadline": today + timedelta(days=4),
                "priority": "High",
                "initiative": "Mobile Application Launch",
                "confidence": 0.96,
                "evidence": "Elena Rostova: 'We also need an audit of all third-party tracking scripts to confirm compliance before the launch.'",
                "meeting_id": meetings[4].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Set up automated daily export of unhandled mobile exceptions from Sentry",
                "description": "Send daily digest of uncaught Swift and Kotlin exceptions to the mobile engineering lead.",
                "owner": "Alex Morgan",
                "deadline": today + timedelta(days=7),
                "priority": "Medium",
                "initiative": "Mobile Application Launch",
                "confidence": 0.92,
                "evidence": "Alex Morgan: 'I will configure Sentry to pipe unhandled exception summaries directly to our team channel.'",
                "meeting_id": meetings[4].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Create localized App Store metadata copy for German and Japanese launch regions",
                "description": "Coordinate with localization agency to deliver translated keywords, descriptions, and feature bullet points.",
                "owner": "Priya Patel",
                "deadline": today + timedelta(days=10),
                "priority": "Medium",
                "initiative": "Mobile Application Launch",
                "confidence": 0.89,
                "evidence": "Priya Patel: 'I will handle the translation agency hand-off for the German and Japanese app store packages.'",
                "meeting_id": meetings[4].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Configure Snowflake resource monitor to kill queries running longer than 30 minutes",
                "description": "Prevent runaway recursive CTEs and Cartesian joins from depleting monthly credit quotas.",
                "owner": "David Kim",
                "deadline": today + timedelta(days=3),
                "priority": "High",
                "initiative": "Data Warehouse Migration",
                "confidence": 0.95,
                "evidence": "David Kim: 'I'll put a hard 30-minute query termination threshold in place by Wednesday.'",
                "meeting_id": meetings[7].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Generate comprehensive data dictionary documenting all 84 migrated reporting tables",
                "description": "Publish markdown documentation in repository wiki detailing column definitions, primary keys, and SLA freshness expectations.",
                "owner": "Alex Morgan",
                "deadline": today + timedelta(days=14),
                "priority": "Low",
                "initiative": "Data Warehouse Migration",
                "confidence": 0.85,
                "evidence": "Alex Morgan: 'I will put together a data dictionary for the newly migrated tables once the verification passes.'",
                "meeting_id": meetings[1].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Organize dedicated Customer Success training session for churn prediction alerting",
                "description": "Conduct 45-minute live walkthrough showing account managers how to interpret risk indicators and trigger proactive outreach.",
                "owner": "Sarah Chen",
                "deadline": today + timedelta(days=8),
                "priority": "Medium",
                "initiative": "Customer Analytics Platform",
                "confidence": 0.93,
                "evidence": "Sarah Chen: 'I will run a workshop for the Customer Success leads as soon as the Slack bot is operational.'",
                "meeting_id": meetings[0].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Conduct security vulnerability scan on customer churn prediction API gateway",
                "description": "Run automated OWASP API vulnerability assessment and verify JWT expiration enforcement.",
                "owner": "David Kim",
                "deadline": today + timedelta(days=5),
                "priority": "High",
                "initiative": "Customer Analytics Platform",
                "confidence": 0.97,
                "evidence": "David Kim: 'We must run an OWASP vulnerability scan on the gateway before pointing production traffic.'",
                "meeting_id": meetings[0].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Set up automated weekly email digest of customer churn predictions for executive committee",
                "description": "Format high-level PDF summary containing enterprise retention curve and top 10 accounts with rising risk scores.",
                "owner": "Unassigned",
                "deadline": None,
                "priority": "Low",
                "initiative": "Customer Analytics Platform",
                "confidence": 0.81,
                "evidence": "Someone mentioned that executives might want a weekly email summary of the churn risk scores.",
                "meeting_id": meetings[2].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Investigate transactional email bounce rates for Yahoo and Outlook domains",
                "description": "Audit DMARC, DKIM, and SPF alignment records to ensure email provider authentication passes.",
                "owner": "Alex Morgan",
                "deadline": today + timedelta(days=6),
                "priority": "Medium",
                "initiative": "Marketing Automation",
                "confidence": 0.90,
                "evidence": "Alex Morgan: 'I will inspect whether the high bounce rates are tied to recent Yahoo DMARC policy updates.'",
                "meeting_id": meetings[3].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Design interactive customer journey flowcharts for onboarding drop-off points",
                "description": "Map customer progression from signup through first API call to identify drop-off cliffs.",
                "owner": "Priya Patel",
                "deadline": today + timedelta(days=9),
                "priority": "Low",
                "initiative": "Marketing Automation",
                "confidence": 0.86,
                "evidence": "Priya Patel: 'I will sketch out the full funnel map so we can pinpoint where users are abandoning setup.'",
                "meeting_id": meetings[3].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Benchmark sentiment classification latency between Claude 3.5 Sonnet and GPT-4o-mini",
                "description": "Evaluate response time and per-ticket token cost across a sample of 500 multilingual feedback comments.",
                "owner": "Sarah Chen",
                "deadline": today + timedelta(days=12),
                "priority": "Medium",
                "initiative": "Customer Feedback Intelligence",
                "confidence": 0.88,
                "evidence": "Sarah Chen: 'We should benchmark smaller models against larger ones to see if we can cut classification costs by 70%.'",
                "meeting_id": meetings[6].id,
                "status": "Pending",
                "days_ago_created": 1
            },
            {
                "title": "Establish automated regression tests for Zendesk ticket ingestion webhooks",
                "description": "Mock incoming customer support payloads to ensure ticket body sanitization correctly strips credit card numbers.",
                "owner": "David Kim",
                "deadline": today + timedelta(days=7),
                "priority": "High",
                "initiative": "Customer Feedback Intelligence",
                "confidence": 0.94,
                "evidence": "David Kim: 'I will write automated unit and integration tests to ensure our PII scrubber catches credit card patterns.'",
                "meeting_id": meetings[5].id,
                "status": "Pending",
                "days_ago_created": 1
            }
        ]

        seeded_rq_items = []
        for q_item in review_queue_data:
            rq = ReviewQueueItem(
                meeting_id=q_item["meeting_id"],
                title=q_item["title"],
                description=q_item["description"],
                owner=q_item["owner"],
                deadline=q_item["deadline"],
                priority=q_item["priority"],
                initiative=q_item["initiative"],
                confidence=q_item["confidence"],
                evidence=q_item["evidence"],
                status=q_item.get("status", "Pending"),
                reviewer_action=q_item.get("reviewer_action"),
                reviewed_at=q_item.get("reviewed_at"),
                created_at=datetime.utcnow() - timedelta(days=q_item.get("days_ago_created", 1))
            )
            session.add(rq)
            seeded_rq_items.append((rq, q_item.get("linked_task_idx")))
        session.flush()

        # Connect approved items to corresponding official task IDs
        for rq_obj, task_idx in seeded_rq_items:
            if task_idx is not None and task_idx < len(created_tasks):
                created_tasks[task_idx].review_item_id = rq_obj.id
        session.flush()

        # Governance decision audit log entries
        audit_records = [
            AuditLog(
                entity_type="review_queue",
                entity_id=seeded_rq_items[0][0].id,
                action="APPROVED",
                old_value="Pending",
                new_value=f"Approved into Official Task #{created_tasks[0].id}: '{created_tasks[0].title}'",
                timestamp=datetime.utcnow() - timedelta(days=3)
            ),
            AuditLog(
                entity_type="review_queue",
                entity_id=seeded_rq_items[1][0].id,
                action="EDIT_APPROVED",
                old_value="Title: Configure notifications | Owner: Unassigned | Deadline: None | Priority: Low | Initiative: General",
                new_value=f"Title: {created_tasks[1].title} | Owner: {created_tasks[1].owner} | Deadline: {created_tasks[1].deadline} | Priority: {created_tasks[1].priority} | Initiative: {created_tasks[1].initiative}",
                timestamp=datetime.utcnow() - timedelta(days=3)
            ),
            AuditLog(
                entity_type="review_queue",
                entity_id=seeded_rq_items[2][0].id,
                action="REJECTED",
                old_value="Pending",
                new_value="Declined during human verification: Non-strategic administrative task (catering coordination is outside initiative scope)",
                timestamp=datetime.utcnow() - timedelta(days=4)
            ),
            AuditLog(
                entity_type="task",
                entity_id=created_tasks[2].id,
                action="STATUS_CHANGE",
                old_value="In Progress",
                new_value="Completed",
                timestamp=datetime.utcnow() - timedelta(days=1)
            ),
            AuditLog(
                entity_type="task",
                entity_id=created_tasks[3].id,
                action="STATUS_CHANGE",
                old_value="In Progress",
                new_value="Blocked (Pending Salesforce OAuth permissions)",
                timestamp=datetime.utcnow() - timedelta(days=2)
            ),
        ]
        session.add_all(audit_records)
        return True

