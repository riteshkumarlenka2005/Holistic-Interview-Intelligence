# Lessons Learned: Holistic Interview Intelligence

This document is a living retrospective of the engineering decisions, challenges, and user feedback collected throughout the lifecycle of the Holistic Interview Intelligence platform.

## 1. Architectural Decisions

### What Worked Well
- **Decoupling AI Engines from the API**: Moving Speech, Vision, and Text evaluations into Celery asynchronous queues prevented the FastAPI main thread from blocking. This was critical for scaling.
- **Dedicated WebSocket Handlers**: Isolating real-time streaming (audio/video frames) into lightweight WebSocket endpoints kept the REST API clean and state-independent.
- **Modular Evaluator Design**: Breaking down the "AI Interviewer" into specialized engines (Technical, Communication, Integrity, Confidence, Coaching) allowed us to test, refine, and prompt-engineer each component independently.
- **Structured Observability**: Implementing JSON logging and passing `request_id` across FastAPI and Celery boundaries from day one saved countless hours during debugging.

### What Could Be Improved
- **State Management**: Initially, too much state was managed in the frontend. Shifting session state and memory entirely to the backend (`Interview Brain`) proved more reliable, but doing it earlier would have saved refactoring time.
- **Database Schema Agility**: The schema evolved rapidly as new AI metrics were added. Adopting Alembic migrations earlier on would have prevented some database wipe-and-reloads during local development.

## 2. AI and Latency Observations

### Latency Bottlenecks
- **Whisper Transcription**: Real-time transcription is incredibly sensitive. We learned that sending smaller, 3-second audio chunks was better for perceived latency than waiting for long pauses.
- **LLM Token Generation**: The `Technical Engine` evaluations took significantly longer than simple coaching hints. We learned to stream responses via WebSockets for perceived speed rather than waiting for massive JSON blobs to generate.

### Prompt Refinement
- **The "Overly Harsh" Interviewer**: Early versions of the `Communication Engine` were too penalizing on filler words ("um", "like"). Prompts had to be aggressively tuned to be *constructive* rather than *critical*.
- **JSON Formatting**: Forcing LLMs to return strict JSON arrays for reports required extensive prompt tuning (and eventually leveraging structured output features) to prevent backend parsing crashes.

## 3. Engineering Metrics (To Be Updated)

Keep track of quantifiable improvements to measure progress objectively:

| Metric | Before | After | Notes |
| :--- | :--- | :--- | :--- |
| Question generation latency | *[e.g., 3.2 s]* | *[e.g., 1.7 s]* | *[e.g., Prompt optimization + caching]* |
| Report generation | *[e.g., 18 s]* | *[e.g., 8.4 s]* | *[e.g., Parallel engine execution]* |
| Avg WebSocket reconnects | *[e.g., 6/session]* | *[e.g., 0.8/session]* | *[e.g., Heartbeat tuning]* |
| Speech chunk latency | *[e.g., 900 ms]* | *[e.g., 340 ms]* | *[e.g., 3-second chunks]* |

## 4. Decision Log

Use this log to remember *why* an architectural decision was made.

**Decision #001: Celery over FastAPI BackgroundTasks**
- **Reason**: Speech, vision, and report generation are CPU/LLM intensive and require retry handling.
- **Alternatives considered**: FastAPI BackgroundTasks, asyncio.create_task.
- **Outcome**: Celery selected because tasks must survive process restarts and can be distributed across workers.

**Decision #002: Modular AI Engines over Monolithic Prompt**
- **Reason**: Passing a 20-minute transcript to a single LLM call is prone to failure, context limits, and high latency.
- **Outcome**: Created separate Technical, Communication, and Coaching engines that evaluate specific segments asynchronously.

## 5. Real-World User Feedback (To Be Updated Post-Beta)

Organize the feedback from the first 20-30 real users to prioritize Version 2:

| Category | Frequency | Action to Take |
| :--- | :--- | :--- |
| *[e.g., Eye tracking too strict]* | *[e.g., 11]* | *[e.g., Increase distraction threshold]* |
| *[e.g., Report too long]* | *[e.g., 8]* | *[e.g., Add concise summary at top]* |
| *[e.g., Coaching helpful]* | *[e.g., 17]* | *[e.g., Keep current thresholds]* |
| *[e.g., Dashboard confusing]* | *[e.g., 5]* | *[e.g., Redesign navigation]* |

## 6. Postmortem & Next Steps

*The formal v1.0 Engineering Retrospective will be written here after the staging deployment and beta phase concludes.*

## 7. What We Would Do Differently Starting From Scratch

- Keep session orchestration server-side from day one.
- Introduce Alembic migrations before adding the complex AI metrics.
- Design the final Report schemas *before* dashboard implementation to prevent API rewrites.
- Add structured observability and JSON logging before integrating multiple independent AI engines.
- Begin real user testing earlier with mock AI rather than waiting for full backend feature completion.
