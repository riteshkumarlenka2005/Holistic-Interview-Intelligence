"""
Database Seeding Script

Seeds the database with demo data for development and testing.
Idempotent: Safe to run multiple times without duplicating data.

Usage:
    cd backend
    python scripts/seed_data.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import (
    User, UserRole, OAuthProvider,
    LearningResource, ResourceType, DifficultyLevel,
    ResourceProgress,
    InterviewSession, SessionType, SessionStatus,
    InterviewAnalysis
)
from app.core.security import get_password_hash


# ============= Demo Data =============

DEMO_USERS = [
    {
        "email": "admin@interviewai.example.com",
        "password": "Admin123!",
        "first_name": "Admin",
        "last_name": "User",
        "role": UserRole.ADMIN.value,
        "is_verified": True,
    },
    {
        "email": "coach@interviewai.example.com",
        "password": "Coach123!",
        "first_name": "Interview",
        "last_name": "Coach",
        "role": UserRole.RECRUITER.value,
        "is_verified": True,
    },
    {
        "email": "student@interviewai.example.com",
        "password": "Student123!",
        "first_name": "Demo",
        "last_name": "Student",
        "role": UserRole.CANDIDATE.value,
        "is_verified": True,
    },
    {
        "email": "newuser@interviewai.example.com",
        "password": "Newuser123!",
        "first_name": "New",
        "last_name": "User",
        "role": UserRole.CANDIDATE.value,
        "is_verified": False,
    },
]

DEMO_RESOURCES = [
    {
        "title": "Mastering the STAR Method",
        "description": "Learn how to structure your behavioral interview answers using the Situation, Task, Action, Result framework.",
        "resource_type": ResourceType.ARTICLE.value,
        "tags": ["behavioral", "star-method", "interview-prep"],
        "difficulty_level": DifficultyLevel.BEGINNER.value,
        "estimated_duration": 15,
        "content_body": """# The STAR Method

The STAR method is a structured approach to answering behavioral interview questions.

## Components

- **Situation**: Set the context for your story
- **Task**: Describe what your responsibility was
- **Action**: Explain what steps you took
- **Result**: Share what outcomes your actions achieved

## Tips

1. Be specific and provide concrete examples
2. Focus on YOUR contributions
3. Quantify results when possible
4. Practice common questions beforehand
""",
        "slug": "mastering-star-method",
        "is_published": True,
    },
    {
        "title": "Body Language Essentials",
        "description": "Understanding and improving your non-verbal communication during interviews.",
        "resource_type": ResourceType.VIDEO.value,
        "tags": ["body-language", "non-verbal", "communication"],
        "difficulty_level": DifficultyLevel.BEGINNER.value,
        "estimated_duration": 20,
        "video_url": "https://example.com/videos/body-language",
        "thumbnail_url": "https://via.placeholder.com/400x225?text=Body+Language",
        "slug": "body-language-essentials",
        "is_published": True,
    },
    {
        "title": "Technical Interview Deep Dive",
        "description": "Comprehensive guide to acing technical interviews in software engineering roles.",
        "resource_type": ResourceType.GUIDE.value,
        "tags": ["technical", "coding", "algorithms", "software-engineering"],
        "difficulty_level": DifficultyLevel.ADVANCED.value,
        "estimated_duration": 45,
        "content_body": """# Technical Interview Deep Dive

## Data Structures & Algorithms

Master the fundamentals:
- Arrays and Strings
- Linked Lists
- Trees and Graphs
- Hash Tables
- Dynamic Programming

## System Design

For senior roles, prepare for:
- Scalability concepts
- Database design
- Caching strategies
- Load balancing

## Coding Best Practices

1. Think out loud
2. Ask clarifying questions
3. Start with brute force, then optimize
4. Test your code with examples
""",
        "slug": "technical-interview-deep-dive",
        "is_published": True,
    },
    {
        "title": "Handling Stress Interview Questions",
        "description": "Strategies for staying calm and composed when facing challenging questions.",
        "resource_type": ResourceType.TUTORIAL.value,
        "tags": ["stress", "mindset", "psychology"],
        "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
        "estimated_duration": 25,
        "content_body": """# Handling Stress Interview Questions

## Common Stress Questions

- "What is your biggest weakness?"
- "Tell me about a time you failed"
- "Why should we hire you over other candidates?"

## Strategies

### 1. Pause Before Answering
Take a breath. It's okay to think.

### 2. Reframe Negatives
Every "weakness" is an area of growth.

### 3. Stay Authentic
Interviewers can detect rehearsed answers.

### 4. Practice Mindfulness
Prepare mentally before the interview.
""",
        "slug": "handling-stress-questions",
        "is_published": True,
    },
    {
        "title": "Salary Negotiation Masterclass",
        "description": "Learn how to confidently negotiate your compensation package.",
        "resource_type": ResourceType.VIDEO.value,
        "tags": ["salary", "negotiation", "career"],
        "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
        "estimated_duration": 30,
        "video_url": "https://example.com/videos/salary-negotiation",
        "thumbnail_url": "https://via.placeholder.com/400x225?text=Salary+Negotiation",
        "slug": "salary-negotiation-masterclass",
        "is_published": True,
    },
]


async def seed_users(session) -> dict:
    """Seed demo users. Returns dict mapping email to user object."""
    users = {}
    for user_data in DEMO_USERS:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  ⏭️  User {user_data['email']} already exists")
            users[user_data["email"]] = existing
        else:
            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_verified=user_data["is_verified"],
                is_active=True,
                oauth_provider=OAuthProvider.LOCAL.value,
            )
            session.add(user)
            await session.flush()
            users[user_data["email"]] = user
            print(f"  ✅ Created user: {user_data['email']} ({user_data['role']})")
    
    return users


async def seed_resources(session) -> dict:
    """Seed demo resources. Returns dict mapping slug to resource object."""
    resources = {}
    for resource_data in DEMO_RESOURCES:
        # Check if resource already exists by slug
        result = await session.execute(
            select(LearningResource).where(LearningResource.slug == resource_data["slug"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  ⏭️  Resource '{resource_data['title']}' already exists")
            resources[resource_data["slug"]] = existing
        else:
            resource = LearningResource(**resource_data)
            session.add(resource)
            await session.flush()
            resources[resource_data["slug"]] = resource
            print(f"  ✅ Created resource: {resource_data['title']}")
    
    return resources


async def seed_progress(session, users: dict, resources: dict):
    """Seed demo progress for the student user."""
    student = users.get("student@interviewai.example.com")
    if not student:
        print("  Student user not found, skipping progress seeding")
        return

    progress_data = [
        {"slug": "mastering-star-method", "percentage": 100.0, "time_spent": 900},
        {"slug": "body-language-essentials", "percentage": 65.0, "time_spent": 780},
        {"slug": "technical-interview-deep-dive", "percentage": 25.0, "time_spent": 675},
    ]
    
    for data in progress_data:
        resource = resources.get(data["slug"])
        if not resource:
            continue
        
        # Check if progress exists
        result = await session.execute(
            select(ResourceProgress).where(
                ResourceProgress.user_id == student.id,
                ResourceProgress.resource_id == resource.id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  ⏭️  Progress for '{resource.title}' already exists")
        else:
            progress = ResourceProgress(
                user_id=student.id,
                resource_id=resource.id,
                progress_percentage=data["percentage"],
                is_completed=data["percentage"] >= 100,
                time_spent_seconds=data["time_spent"],
            )
            session.add(progress)
            print(f"  ✅ Created progress: {resource.title} ({data['percentage']}%)")


async def seed_interview_sessions(session, users: dict):
    """Seed demo interview sessions."""
    student = users.get("student@interviewai.example.com")
    if not student:
        print("  Student user not found, skipping session seeding")
        return

    # Check if sessions exist
    result = await session.execute(
        select(InterviewSession).where(InterviewSession.user_id == student.id)
    )
    existing_count = len(result.scalars().all())
    
    if existing_count > 0:
        print(f"  ⏭️  {existing_count} interview sessions already exist for student")
        return
    
    sessions_data = [
        {
            "title": "Product Manager Interview Practice",
            "session_type": SessionType.BEHAVIORAL.value,
            "status": SessionStatus.COMPLETED.value,
            "target_job_role": "Product Manager",
            "target_company": "Tech Startup",
            "duration_minutes": 30,
            "questions": [
                "Tell me about yourself",
                "Describe a product you managed from conception to launch",
                "How do you prioritize features?"
            ],
            "responses": [
                {"question_index": 0, "response_text": "I'm a product manager with 5 years of experience..."},
                {"question_index": 1, "response_text": "I led the development of our mobile app..."},
            ],
            "started_at": datetime.utcnow() - timedelta(days=3),
            "ended_at": datetime.utcnow() - timedelta(days=3, minutes=-25),
        },
        {
            "title": "Technical Screen Practice",
            "session_type": SessionType.TECHNICAL.value,
            "status": SessionStatus.ANALYZED.value,
            "target_job_role": "Software Engineer",
            "target_company": "FAANG",
            "duration_minutes": 45,
            "questions": [
                "Explain how you would design a URL shortener",
                "Write a function to find the longest palindromic substring"
            ],
            "responses": [],
            "started_at": datetime.utcnow() - timedelta(days=7),
            "ended_at": datetime.utcnow() - timedelta(days=7, minutes=-40),
        },
    ]
    
    for data in sessions_data:
        interview_session = InterviewSession(
            user_id=student.id,
            **data
        )
        session.add(interview_session)
        await session.flush()
        print(f"  ✅ Created session: {data['title']}")
        
        # Add analysis for analyzed session
        if data["status"] == SessionStatus.ANALYZED.value:
            analysis = InterviewAnalysis(
                session_id=interview_session.id,
                verbal_metrics={
                    "transcription": {"text": "Sample transcription...", "duration": 2400},
                    "prosody": {"pace": {"wpm": 145, "assessment": "good"}},
                    "confidence": {"overall_score": 0.78}
                },
                nonverbal_metrics={
                    "gaze": {"eye_contact_percentage": 72},
                    "posture": {"dominant_posture": "upright", "engagement_score": 0.80}
                },
                multimodal_score={
                    "combined_confidence": 0.76,
                    "communication_score": 0.78,
                    "presence_score": 0.80,
                    "engagement_score": 0.74
                },
                recommendations={
                    "overall_assessment": {"score": 76, "grade": "B+"},
                    "strengths": ["Clear communication", "Good technical knowledge"],
                    "improvements": ["More eye contact", "Slow down when explaining"]
                }
            )
            session.add(analysis)
            print(f"  ✅ Created analysis for session: {data['title']}")


async def main():
    """Main seeding function."""
    print("\n Starting database seeding...\n")

    # Create all tables if they don't exist
    from app.core.database import init_db
    await init_db()

    async with AsyncSessionLocal() as session:
        try:
            print("📋 Seeding users...")
            users = await seed_users(session)
            
            print("\n📚 Seeding learning resources...")
            resources = await seed_resources(session)
            
            print("\n📈 Seeding progress data...")
            await seed_progress(session, users, resources)
            
            print("\n🎤 Seeding interview sessions...")
            await seed_interview_sessions(session, users)
            
            await session.commit()
            print("\n✨ Database seeding completed successfully!\n")
            
            # Print summary
            print("=" * 50)
            print("Demo Accounts:")
            print("=" * 50)
            for user_data in DEMO_USERS:
                print(f"  Email: {user_data['email']}")
                print(f"  Password: {user_data['password']}")
                print(f"  Role: {user_data['role']}")
                print()
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
