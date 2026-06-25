"""
Phase 2 end-to-end mock test.

Tests the full updated pipeline:
  InterviewBrain (orchestrating TechnicalEngine + CommunicationEngine)
  → InterviewOrchestrator (dynamic weights, difficulty_modifier, Response persistence)
  → InterviewState transitions

Runs against an in-memory SQLite DB, mocking LLM calls.
"""
import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock

# --- Mock litellm before any import ---
sys.modules["litellm"] = MagicMock()

from app.services.interview_brain import InterviewBrain
from app.services.technical_engine import TechnicalEngine
from app.services.communication_engine import CommunicationEngine
from app.services.orchestrator import InterviewOrchestrator
from app.models.base import Base
from app.models.user import User
from app.models.interview import InterviewSession, InterviewState, InterviewTemplate
from app.models.questions import InterviewQuestion
from app.models.responses import Response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# --- Mock engine responses ---
async def mock_technical_evaluate(question, candidate_answer, job_role):
    if "virtual dom" in candidate_answer.lower():
        return {
            "technical_score": 92,
            "technical_feedback": "Excellent explanation of the Virtual DOM reconciliation.",
            "missing_technical_points": [],
            "is_technically_complete": True,
        }
    return {
        "technical_score": 58,
        "technical_feedback": "Correct at a high level but missing Virtual DOM and reconciliation details.",
        "missing_technical_points": ["Virtual DOM", "Reconciliation algorithm"],
        "is_technically_complete": False,
    }

async def mock_comm_evaluate(candidate_answer, job_role):
    return {
        "communication_score": 78,
        "communication_feedback": "Clear and well-structured answer.",
        "confidence_score": 72,
        "structure_used": "Direct",
    }

async def mock_generate_main(job_role, interview_context, difficulty_modifier, topic_memory=None):
    topic_num = len(topic_memory.covered_topics) + 1 if topic_memory else 1
    return {
        "question_text": f"What is React Core {topic_num}? [difficulty={difficulty_modifier}]",
        "topic": f"React Concept {topic_num}",
        "subtopic": "Virtual DOM",
        "difficulty": "intermediate"
    }

async def mock_generate_adaptive(job_role, previous_question, previous_answer, missing_points, difficulty_modifier, topic_memory=None):
    return f"Can you explain {missing_points[0]} in detail? [difficulty={difficulty_modifier}]"


async def run():
    print("=" * 60)
    print("PHASE 2 END-TO-END MOCK TEST")
    print("=" * 60)

    # --- Setup in-memory SQLite ---
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        # --- Seed user, template, session ---
        user = User(id="u1", email="test@example.com", password_hash="x")
        db.add(user)

        template = InterviewTemplate(
            id="tmpl_1",
            title="Frontend Developer",
            target_job_role="Frontend Developer",
            technical_weight=65,
            communication_weight=20,
            speech_weight=10,
            confidence_weight=5,
            base_difficulty="intermediate",
        )
        db.add(template)

        session = InterviewSession(
            id="sess_1",
            user_id="u1",
            target_job_role="Frontend Developer",
            current_state=InterviewState.WAITING.value,
            difficulty_modifier=0,
        )
        # Link template (if field exists on model; fallback graceful)
        try:
            session.template_id = "tmpl_1"
        except AttributeError:
            pass
        db.add(session)
        await db.commit()

        # --- Patch engines ---
        orchestrator = InterviewOrchestrator(db)
        orchestrator.brain.technical_engine.evaluate = mock_technical_evaluate
        orchestrator.brain.communication_engine.evaluate = mock_comm_evaluate
        orchestrator.brain.generate_next_main_question = mock_generate_main
        orchestrator.brain.generate_adaptive_question = mock_generate_adaptive

        # ── STEP 1: Start Session ──────────────────────────────────────
        print("\n[1] start_session()")
        r1 = await orchestrator.start_session("sess_1")
        await db.refresh(session)
        print(f"    State : {session.current_state}")
        print(f"    Q1 text: {r1['question']['text']}")
        assert session.current_state == "question_asked", "Expected question_asked"
        q1_id = r1["question"]["id"]

        # -- STEP 2: Submit incomplete answer -> expect FOLLOW_UP --
        print("\n[2] process_answer() -> Incomplete answer")
        r2 = await orchestrator.process_answer(
            session_id="sess_1",
            question_id=q1_id,
            transcript="React is a JavaScript library for building user interfaces.",
            speech_metrics={"fluency_score": 75, "wpm": 130, "filler_count": 2},
            vision_metrics={"eye_contact_percent": 30, "head_stability_score": 40, "avg_engagement": 50},
        )
        await db.refresh(session)
        print(f"    Overall score      : {r2['evaluation']['overall_score']}")
        print(f"    Technical score    : {r2['evaluation']['technical_score']}")
        print(f"    Communication score: {r2['evaluation']['communication_score']}")
        print(f"    Confidence score   : {r2['evaluation']['confidence_score']} ({r2['evaluation']['confidence_band']})")
        print(f"    Weights used       : {r2['evaluation']['weights_used']}")
        print(f"    Next action        : {r2['next_action']}")
        print(f"    Follow-up Q        : {r2['next_question']['text']}")
        print(f"    difficulty_modifier: {r2['difficulty_modifier']}")
        print(f"    State              : {session.current_state}")
        assert r2["next_action"] == "follow_up", "Expected follow_up"
        assert session.current_state == "question_asked", "Expected question_asked"
        q2_id = r2["next_question"]["id"]

        # -- STEP 3: Submit complete follow-up -> expect NEXT_QUESTION --
        print("\n[3] process_answer() -> Complete answer")
        r3 = await orchestrator.process_answer(
            session_id="sess_1",
            question_id=q2_id,
            transcript="The Virtual DOM is a lightweight in-memory representation of the real DOM. React uses a reconciliation algorithm to diff the virtual and real DOM trees and apply minimal updates.",
            speech_metrics={"fluency_score": 90, "wpm": 145, "filler_count": 0},
            vision_metrics={"eye_contact_percent": 95, "head_stability_score": 90, "avg_engagement": 85},
        )
        await db.refresh(session)
        print(f"    Overall score      : {r3['evaluation']['overall_score']}")
        print(f"    Next action        : {r3['next_action']}")
        print(f"    Next main Q        : {r3['next_question']['text']}")
        print(f"    difficulty_modifier: {r3['difficulty_modifier']}")
        print(f"    State              : {session.current_state}")
        print(f"    Covered topics     : {r3['covered_topics']}")
        assert r3["next_action"] == "next_question", "Expected next_question"
        assert len(r3["covered_topics"]) == 2, "Expected 2 covered topics"

        # -- Verify Response records stored --
        from sqlalchemy import select
        result = await db.execute(select(Response).where(Response.session_id == "sess_1"))
        responses = result.scalars().all()
        print(f"\n[4] Response records persisted: {len(responses)}")
        for i, resp in enumerate(responses, 1):
            print(f"    [{i}] technical={resp.technical_score}  "
                  f"communication={resp.communication_score}  "
                  f"speech={resp.speech_metrics}")
        assert len(responses) == 2, f"Expected 2 Response records, got {len(responses)}"

        # ── STEP 5: Phase 5 - Report Generation ─────────────────────────
        from app.services.report_engine import ReportEngine
        from app.models.integrity import IntegrityEvent
        from app.models.reports import Report

        print("\n[5] Phase 5: Generating Final Audit Reports")
        # Inject some fake Integrity Events to test deductions
        db.add(IntegrityEvent(session_id="sess_1", event_type="tab_switch", details="Switched to Google"))
        db.add(IntegrityEvent(session_id="sess_1", event_type="multiple_faces", details="Second face detected"))
        await db.commit()

        # Mock the LLM Summary generation
        report_engine = ReportEngine(db)
        report_engine.llm.generate_text = AsyncMock(return_value="The candidate demonstrated excellent React knowledge and strong communication. They struggled initially with Virtual DOM concepts but recovered well.")

        # Simulate end of session
        session.status = "completed"
        from datetime import datetime, timezone
        session.ended_at = datetime.now(timezone.utc)
        await db.commit()

        await report_engine.generate_reports("sess_1")

        # Fetch reports
        result = await db.execute(select(Report).where(Report.session_id == "sess_1"))
        reports = result.scalars().all()
        
        print(f"\n    Report records generated: {len(reports)}")
        candidate_report = next((r for r in reports if r.report_type == "candidate"), None)
        recruiter_report = next((r for r in reports if r.report_type == "recruiter"), None)

        assert candidate_report is not None, "Candidate report missing"
        assert recruiter_report is not None, "Recruiter report missing"

        print("\n--- Recruiter Report Snippet ---")
        import json
        print(json.dumps(recruiter_report.data, indent=2))

        print("\n" + "=" * 60)
        print("ALL ASSERTIONS PASSED [OK]")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run())
