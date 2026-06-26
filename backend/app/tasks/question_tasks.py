"""
Question generation Celery tasks
"""
from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.question_tasks.generate_questions", queue="questions")
def generate_questions(session_id: str, job_role: str, difficulty: str = "medium", count: int = 5):
    """Generate interview questions based on job role and difficulty using AI."""
    # TODO: Implement AI-powered question generation with Gemini
    return {"session_id": session_id, "status": "questions_generated", "count": count}


@celery_app.task(name="app.tasks.question_tasks.generate_followup", queue="questions")
def generate_followup(session_id: str, previous_answer: str):
    """Generate a follow-up question based on the candidate's previous answer."""
    # TODO: Implement contextual follow-up generation
    return {"session_id": session_id, "status": "followup_generated"}
