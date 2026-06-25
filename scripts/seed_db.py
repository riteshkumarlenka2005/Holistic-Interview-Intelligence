"""
Database seeding script
Populate database with initial data
"""
import asyncio
from datetime import datetime


async def seed_users():
    """Seed demo users"""
    users = [
        {
            "email": "demo@example.com",
            "name": "Demo User",
            "password_hash": "hashed_password"
        },
        {
            "email": "admin@example.com", 
            "name": "Admin User",
            "password_hash": "hashed_password"
        }
    ]
    print(f"Seeding {len(users)} users...")
    # TODO: Insert into database


async def seed_interview_questions():
    """Seed common interview questions"""
    questions = [
        {"category": "behavioral", "text": "Tell me about yourself"},
        {"category": "behavioral", "text": "What are your strengths?"},
        {"category": "behavioral", "text": "What are your weaknesses?"},
        {"category": "technical", "text": "Explain your experience with..."},
    ]
    print(f"Seeding {len(questions)} questions...")
    # TODO: Insert into database


async def main():
    print("🌱 Starting database seeding...")
    await seed_users()
    await seed_interview_questions()
    print("✅ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
