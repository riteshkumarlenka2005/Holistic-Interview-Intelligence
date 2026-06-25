# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0-rc1] - 2026-06-25
### Added
- **Core Orchestrator**: Interview Brain memory and context management.
- **AI Engines**:
  - Speech Engine (Transcription, Filler Words, Grammar).
  - Vision Engines (Face Tracking, Eye Tracking).
  - Behavioral Engines (Confidence, Nervousness, Emotion Mapping).
  - Technical & Communication Evaluators.
  - Coaching Engine (Real-time actionable hints).
  - Integrity Engine (Multi-person detection, context matching).
- **Backend Infrastructure**: 
  - FastAPI with async database operations (SQLAlchemy 2.0).
  - Celery workers with Redis broker for heavy AI inferences.
  - Live WebSocket streaming for Video and Audio chunks with exponential backoff reconnections.
- **Observability**: 
  - Structured JSON Logging.
  - Contextvars `request_id` propagation.
  - LLM Cost Tracking (Tokens, Latency, Models).
- **Product Interfaces**: 
  - Candidate Dashboard (Progress tracking, Interview Launcher).
  - Report Engine (Detailed Post-interview analytics).
  - Playback Timeline (Synchronized video with event markers).
  - Recruiter Dashboard (Aggregated candidate views).
- **Privacy & Security**:
  - JWT Auth with refresh token rotation.
  - Pre-interview Consent Screens.
  - Frictionless Demo Mode (no auth required).
  - Data Deletion API endpoints.
- **DevOps**:
  - `docker-compose.prod.yml` configuration.
  - Nginx Reverse proxy with SSL termination layout, security headers, and rate limiting.

### Changed
- Refactored all background tasks from `FastAPI BackgroundTasks` to robust `Celery` workers.
- Migrated legacy frontend `create-react-app` structures to Vite for speed.

### Fixed
- Fixed WebSocket dropping connection under heavy load by chunking audio every 3 seconds.
- Resolved synchronous blocking issues in API by isolating LLM calls.
