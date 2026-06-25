"""
Seed script: Populates interview_templates with all 8 standard templates.
Run once after applying Alembic migrations:

  python seed_templates.py
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.interview import InterviewTemplate


TEMPLATES = [
    {
        "title": "Frontend Developer",
        "target_job_role": "Frontend Developer",
        "technical_weight": 65,
        "communication_weight": 20,
        "speech_weight": 10,
        "confidence_weight": 5,
        "base_difficulty": "intermediate",
    },
    {
        "title": "Backend Developer",
        "target_job_role": "Backend Developer",
        "technical_weight": 70,
        "communication_weight": 15,
        "speech_weight": 10,
        "confidence_weight": 5,
        "base_difficulty": "intermediate",
    },
    {
        "title": "Full Stack Developer",
        "target_job_role": "Full Stack Developer",
        "technical_weight": 65,
        "communication_weight": 20,
        "speech_weight": 10,
        "confidence_weight": 5,
        "base_difficulty": "intermediate",
    },
    {
        "title": "Data Scientist",
        "target_job_role": "Data Scientist",
        "technical_weight": 70,
        "communication_weight": 15,
        "speech_weight": 10,
        "confidence_weight": 5,
        "base_difficulty": "advanced",
    },
    {
        "title": "AI Engineer",
        "target_job_role": "AI Engineer",
        "technical_weight": 75,
        "communication_weight": 15,
        "speech_weight": 5,
        "confidence_weight": 5,
        "base_difficulty": "advanced",
    },
    {
        "title": "HR Interview",
        "target_job_role": "Any",
        "technical_weight": 10,
        "communication_weight": 50,
        "speech_weight": 30,
        "confidence_weight": 10,
        "base_difficulty": "beginner",
    },
    {
        "title": "Behavioral Interview",
        "target_job_role": "Any",
        "technical_weight": 10,
        "communication_weight": 55,
        "speech_weight": 25,
        "confidence_weight": 10,
        "base_difficulty": "intermediate",
    },
    {
        "title": "System Design",
        "target_job_role": "Senior Engineer",
        "technical_weight": 60,
        "communication_weight": 30,
        "speech_weight": 5,
        "confidence_weight": 5,
        "base_difficulty": "advanced",
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        for data in TEMPLATES:
            template = InterviewTemplate(**data)
            db.add(template)
        await db.commit()
        print(f"Seeded {len(TEMPLATES)} interview templates.")


if __name__ == "__main__":
    asyncio.run(seed())
