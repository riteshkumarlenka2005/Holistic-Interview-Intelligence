"""
Demo 5: Gemini 2.5 Flash — Structured Interview Evaluation
Tests: Send question + answer → receive structured JSON with scores and feedback

Install:  pip install google-genai
Run:      python demos/5_gemini_demo.py
Requires: GEMINI_API_KEY environment variable
"""
import os
import json


def main():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY environment variable")
        print("  Windows:  set GEMINI_API_KEY=your-key-here")
        print("  Linux:    export GEMINI_API_KEY=your-key-here")
        return

    try:
        from google import genai
    except ImportError:
        print("ERROR: pip install google-genai")
        return

    client = genai.Client(api_key=api_key)

    print("=" * 60)
    print("  Gemini 2.5 Flash — Interview Evaluation Demo")
    print("=" * 60)

    # --- Test 1: Technical Evaluation ---
    print("\n--- Test 1: Technical Evaluation ---")

    question = "Explain the difference between a stack and a queue. Give a real-world example of each."
    answer = (
        "A stack is like a pile of plates, last in first out. You push on top and pop from top. "
        "A queue is like a line at a store, first in first out. You enqueue at back and dequeue from front. "
        "Stack is used in undo operations, queue is used in printer job scheduling."
    )

    tech_prompt = f"""
You are an expert technical interviewer evaluating a candidate for a Software Engineer position.

Question: {question}
Candidate Answer: {answer}

Evaluate the answer strictly on technical merit.
Respond ONLY with a valid JSON object matching this schema:
{{
    "technical_score": <int 0-100>,
    "technical_feedback": "<2-sentence feedback>",
    "strengths": ["<strength>", ...],
    "weaknesses": ["<weakness>", ...],
    "missing_technical_points": ["<missing concept>", ...],
    "is_technically_complete": <boolean>
}}
"""

    print(f"  Question: {question}")
    print(f"  Answer:   {answer[:80]}...")
    print(f"  Sending to Gemini 2.5 Flash...")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=tech_prompt,
    )

    raw = response.text.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]

    try:
        result = json.loads(raw.strip())
        print(f"\n  Technical Score:    {result.get('technical_score')}/100")
        print(f"  Feedback:          {result.get('technical_feedback')}")
        print(f"  Strengths:         {result.get('strengths')}")
        print(f"  Weaknesses:        {result.get('weaknesses')}")
        print(f"  Missing Points:    {result.get('missing_technical_points')}")
        print(f"  Complete:          {result.get('is_technically_complete')}")
    except json.JSONDecodeError:
        print(f"  Raw response (not JSON): {raw[:200]}")

    # --- Test 2: Communication Evaluation ---
    print("\n--- Test 2: Communication Evaluation ---")

    comm_prompt = f"""
You are an expert communication coach evaluating a candidate for a Software Engineer position.

Candidate Answer Transcript:
{answer}

Evaluate communication style. Respond ONLY with a valid JSON object:
{{
    "communication_score": <int 0-100>,
    "communication_feedback": "<2-sentence feedback>",
    "strengths": ["<strength>", ...],
    "weaknesses": ["<weakness>", ...],
    "confidence_score": <int 0-100>,
    "structure_used": "<e.g. STAR, Direct, Rambling, Unstructured>"
}}
"""

    response2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=comm_prompt,
    )

    raw2 = response2.text.strip()
    if raw2.startswith("```json"):
        raw2 = raw2[7:]
    if raw2.startswith("```"):
        raw2 = raw2[3:]
    if raw2.endswith("```"):
        raw2 = raw2[:-3]

    try:
        result2 = json.loads(raw2.strip())
        print(f"  Communication Score: {result2.get('communication_score')}/100")
        print(f"  Feedback:            {result2.get('communication_feedback')}")
        print(f"  Confidence:          {result2.get('confidence_score')}/100")
        print(f"  Structure:           {result2.get('structure_used')}")
    except json.JSONDecodeError:
        print(f"  Raw response (not JSON): {raw2[:200]}")

    # --- Test 3: Question Generation ---
    print("\n--- Test 3: Question Generation ---")

    gen_prompt = """
You are an expert interviewer for a Backend Engineer role.
Generate a single interview question.

Topics already covered: Arrays, Strings, SQL Basics.
Avoid repeating those topics.

Ask a moderately challenging question.

Respond ONLY with a valid JSON object:
{
    "question_text": "<the full question>",
    "topic": "<main topic>",
    "subtopic": "<specific subtopic>",
    "difficulty": "<beginner|intermediate|advanced|expert>"
}
"""

    response3 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=gen_prompt,
    )

    raw3 = response3.text.strip()
    if raw3.startswith("```json"):
        raw3 = raw3[7:]
    if raw3.startswith("```"):
        raw3 = raw3[3:]
    if raw3.endswith("```"):
        raw3 = raw3[:-3]

    try:
        result3 = json.loads(raw3.strip())
        print(f"  Question:   {result3.get('question_text')}")
        print(f"  Topic:      {result3.get('topic')}")
        print(f"  Subtopic:   {result3.get('subtopic')}")
        print(f"  Difficulty: {result3.get('difficulty')}")
    except json.JSONDecodeError:
        print(f"  Raw response (not JSON): {raw3[:200]}")

    print("\n" + "=" * 60)
    print("  All 3 Gemini tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
