# Architecture Overview

Holistic Interview Intelligence is a modular AI system designed to conduct, evaluate, and provide feedback on technical and behavioral interviews.

## High-Level Topology

```text
                    Holistic Interview Intelligence

                     Candidate / Recruiter Portal
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
 Candidate Dashboard   Recruiter Dashboard     Playback
        │                     │                     │
        └─────────────── Report Engine ─────────────┘
                              │
                  Interview Brain & Orchestrator
                              │
      ┌────────────┬──────────┼──────────┬────────────┐
      │            │          │          │            │
 Speech      Technical   Communication  Vision   Integrity
 Engine        Engine        Engine      Engines    Engine
                                           │
                                   Face / Eye Tracking
                                           │
                                   Confidence Engine
                                           │
                                   Coaching Engine
                                           │
                     PostgreSQL + Redis + Celery + Socket.IO
```

## Tech Stack
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Backend API**: FastAPI (Python), SQLAlchemy, Alembic
- **Asynchronous Tasks**: Celery, Redis
- **Database**: PostgreSQL (pgvector for embeddings)
- **WebSockets**: Native FastAPI WebSockets for high-frequency video/audio streaming
- **Infrastructure**: Docker, Docker Compose, Nginx Reverse Proxy

## Key Design Principles
1. **Decoupled AI Engines**: Heavy AI evaluations run asynchronously in Celery workers.
2. **Stateless WebSockets**: WebSockets proxy frames directly to services; connection loss does not destroy the interview state.
3. **Observability**: Structured JSON logging and contextvars-based Request IDs.
4. **Feature Flags**: Critical subsystems can be disabled at runtime via configuration.
