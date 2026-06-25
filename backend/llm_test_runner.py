import asyncio
import os
from app.services.interview_brain import InterviewBrain

async def run_llm_test():
    brain = InterviewBrain()
    try:
        res = await brain.generate_next_main_question("Software Engineer", [])
        print("SUCCESS:", res)
    except Exception as e:
        print("ERROR:", str(e))

if __name__ == "__main__":
    asyncio.run(run_llm_test())
