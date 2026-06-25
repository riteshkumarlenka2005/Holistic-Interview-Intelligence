# Holistic Interview Intelligence — Full Project Audit Report
**Date:** June 24, 2026  
**Auditor:** GitHub Copilot (Claude Sonnet 4.6)

---

## 1. What Is This Project?

**Holistic Interview Intelligence (HII)** is an AI-powered interview preparation and performance assessment platform. It records a user during a mock interview (via webcam + microphone), then analyzes both what they say (verbal) and how they appear (non-verbal) to produce a holistic score with actionable feedback.

### Core Value Proposition
- Practice job interviews in a simulated environment
- Get real-time AI feedback on confidence, eye contact, posture, speech rate, and emotions
- Receive explainable scores (not just a number — WHY you scored that way)
- Track improvement over multiple sessions
- Learn from curated resources (articles, videos, guides)

---

## 2. Who Are the Users?

| User Type | Description |
|-----------|-------------|
| **Student / Job Seeker** | Primary user. Practices mock interviews, reviews scores, tracks progress |
| **Coach** | Elevated role. Can manage resources and view student data |
| **Admin** | Full platform access. Can manage all users, resources, and settings |
| **Unverified User** | Registered but email not yet verified. Restricted access |

---

## 3. Full Tech Stack

### Frontend
| Layer | Technology | Version |
|-------|-----------|---------|
| Meta-framework | **Astro** | 5.17.1 |
| UI Library | **React** | 18 |
| Language | **TypeScript** | Latest |
| Styling | **Tailwind CSS** | v4 |
| Components | **shadcn/ui** (Radix UI) | Latest |
| Routing | **React Router** | v7 |
| Animations | **Framer Motion** | Latest |
| Forms | **React Hook Form** + **Zod** | Latest |
| State | **Zustand** | Latest |
| Drag & Drop | **@hello-pangea/dnd** | 18.0.1 |
| Date Utils | **date-fns** | Latest |
| AI (chatbot/questions) | **Google Gemini AI** | Latest |
| AI (question gen) | **OpenRouter API** | REST |
| Deployment adapter | **Vercel** | Latest |
| Testing | **Vitest** | Latest |
| Linting | **ESLint** + custom rules | Latest |

### Backend
| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | **FastAPI** | 0.138.0 |
| Language | **Python** | 3.13 |
| ASGI Server | **Uvicorn** | 0.49.0 |
| ORM | **SQLAlchemy** (async) | 2.0.51 |
| DB (dev) | **SQLite** via aiosqlite | Latest |
| DB (prod) | **PostgreSQL** via asyncpg | Latest |
| Migrations | **Alembic** | 1.18.4 |
| Auth | **JWT** (python-jose) + **bcrypt** (passlib) | Latest |
| OAuth | **Google OAuth 2.0**, **GitHub OAuth** | via authlib |
| Email | **aiosmtplib** (SMTP) | Latest |
| Task Queue | **Celery** | 5.6.3 |
| Broker/Cache | **Redis** | 6.4.0 |
| Validation | **Pydantic v2** + pydantic-settings | 2.13.4 |
| HTTP Client | **httpx** (async) | 0.28.1 |

### AI Microservices (`ai-services/`)
| Module | Technology | Purpose |
|--------|-----------|---------|
| Speech Transcription | **Whisper** (faster-whisper) | Speech-to-text |
| Prosody Analysis | **librosa** | Speech rate, volume, pitch |
| Filler Detection | Custom NLP | Detect "um", "uh", "like", etc. |
| Confidence Scoring | Custom ML | Vocal confidence metrics |
| Face Landmarks | **MediaPipe** | 468-point face mesh |
| Gaze Tracking | **MediaPipe** Iris | Eye contact percentage |
| Posture Detection | **MediaPipe** Pose | Upright/slouch posture |
| Micro-Expressions | **FER** + OpenCV | 7-emotion facial analysis |
| Multimodal Fusion | Custom weighted model | Combine speech + vision signals |
| LLM Reasoning | **GPT-4 / OpenRouter** | Generate natural language feedback |
| Explainability | **SHAP** + **LIME** | Why each score was given |
| Counterfactuals | Custom | "What-if" improvement scenarios |

### Infrastructure
| Layer | Technology |
|-------|-----------|
| Containerization | **Docker** + **Docker Compose** |
| Orchestration | **Kubernetes** (k8s manifests present) |
| IaC | **Terraform** |
| CI | **GitHub Actions** (build + lint) |
| CD | Docker images → **GitHub Container Registry** |
| Monitoring | **Prometheus** + **Grafana** (configured) |

### Realtime
| Layer | Technology |
|-------|-----------|
| Live video analysis | **WebSocket** (FastAPI backend) |
| Live speech analysis | **WebSocket** (FastAPI backend) |
| WebRTC signaling | Custom signaling server (`realtime/signaling-server/`) |
| Media routing | `realtime/media-router/` (stub) |

---

## 4. How the System Works — End to End

```
User (Browser)
     │
     ▼
Frontend (Astro + React)  ←──── http://localhost:4321
     │  ├── REST API calls ──────────────────────────────► Backend (FastAPI)
     │  │                                                        │
     │  ├── WebSocket (video frames) ─────────────────────►     │ ← behavioral_ws.py
     │  │                                                        │   (OpenCV + FER)
     │  └── WebSocket (audio chunks) ─────────────────────►     │ ← speech_ws.py
     │                                                           │   (Whisper + grammar)
     │                                                           │
     │                                                     SQLite DB
     │                                                     (interview.db)
     │
     ├── Gemini AI (direct from browser)  ← AI chatbot + question generation
     └── OpenRouter API (server-side)     ← Astro API route /api/generate-questions
```

### Session Flow
1. User logs in (email/password or OAuth)
2. User starts a **Live Session** → webcam + mic activated
3. **Gemini AI** generates interview questions contextually
4. Every video frame → WebSocket → backend `behavioral_ws` → FER/OpenCV → returns confidence, emotions, gaze, eye boxes
5. Audio chunks → WebSocket → backend `speech_ws` → Whisper → transcription, grammar, fillers, speech rate
6. Results displayed in real-time overlay panels (face box, gaze arrows, speech rate meter)
7. Session saved to DB (`InterviewSession` + `InterviewAnalysis` models)
8. User views **Session Detail** page with full scores and recommendations
9. **Progress page** tracks improvement over time

---

## 5. Current Folder Structure

```
Holistic-Interview-Intelligence-main/
│
├── frontend/                    ← Astro + React SPA
│   ├── astro.config.mjs         ← Vercel adapter, Tailwind, React integrations
│   ├── src/
│   │   ├── pages/
│   │   │   ├── [...slug].astro  ← Catch-all SPA shell
│   │   │   └── api/
│   │   │       ├── chatbot.ts         ← Gemini chatbot endpoint
│   │   │       └── generate-questions.ts ← OpenRouter question gen
│   │   ├── components/
│   │   │   ├── pages/           ← 18 page components (all implemented)
│   │   │   ├── ui/              ← shadcn/ui component library
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── FaceTrackingOverlay.tsx
│   │   │   ├── GazeDirectionPanel.tsx
│   │   │   ├── SpeechRatePanel.tsx
│   │   │   └── EnvironmentWarningPanel.tsx
│   │   ├── hooks/
│   │   │   ├── useBehavioralAnalysis.ts  ← WebSocket video analysis
│   │   │   ├── useSpeechAnalysis.ts      ← WebSocket audio analysis
│   │   │   ├── useThemeStore.ts
│   │   │   └── use-toast.tsx
│   │   ├── entities/            ← TypeScript interfaces (CMS schema types)
│   │   ├── services/
│   │   │   ├── geminiService.ts      ← Gemini AI integration
│   │   │   └── chatbotService.ts
│   │   └── styles/global.css
│   ├── integrations/
│   │   ├── auth/                ← Full JWT auth context + provider
│   │   ├── data/                ← localStorage-based CRUD service
│   │   └── errorHandlers/
│   └── eslint-rules/            ← 3 custom ESLint rules
│
├── backend/                     ← FastAPI Python API
│   ├── .env                     ← ✅ Created (local dev config)
│   ├── interview.db             ← ✅ SQLite database (seeded)
│   ├── app/
│   │   ├── main.py              ← App entry, CORS, router registration
│   │   ├── api/v1/
│   │   │   ├── auth.py          ← Full auth: register, login, OTP, OAuth
│   │   │   ├── users.py         ← ✅ Fixed: /me GET/PUT/DELETE
│   │   │   ├── interview.py     ← Interview session CRUD (in-memory)
│   │   │   ├── analysis.py      ← Analysis jobs (in-memory)
│   │   │   ├── reports.py       ← Report generation (in-memory)
│   │   │   ├── resources.py     ← Full DB-backed resources + progress
│   │   │   ├── behavioral_ws.py ← WebSocket: video frame analysis
│   │   │   └── speech_ws.py     ← WebSocket: audio chunk analysis
│   │   ├── core/
│   │   │   ├── config.py        ← Pydantic settings (reads .env)
│   │   │   ├── database.py      ← Async SQLAlchemy engine + session
│   │   │   ├── security.py      ← JWT + password hashing
│   │   │   └── logging.py
│   │   ├── models/
│   │   │   ├── base.py          ← BaseModel (UUID + timestamps)
│   │   │   ├── user.py          ← User, OTPToken, RefreshToken
│   │   │   ├── interview.py     ← InterviewSession, InterviewAnalysis
│   │   │   └── resource.py      ← LearningResource, ResourceProgress
│   │   ├── schemas/             ← Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── email_service.py ← SMTP email (dev: prints to console)
│   │   │   ├── otp_service.py   ← 6-digit OTP generation/verification
│   │   │   ├── oauth_service.py ← Google + GitHub OAuth handlers
│   │   │   ├── speech_analysis.py  ← Lazy-loaded Whisper analyzer
│   │   │   ├── behavioral_analysis.py ← Lazy-loaded FER + OpenCV
│   │   │   └── crud/            ← Full CRUD for all models
│   │   └── models_legacy.py     ← Renamed (was conflicting models.py)
│   ├── scripts/
│   │   └── seed_data.py         ← ✅ Seeding script (run successfully)
│   └── alembic/                 ← DB migrations (configured, not run)
│
├── ai-services/                 ← Standalone AI microservice
│   ├── speech-analysis/
│   │   ├── whisper_transcriber.py
│   │   ├── prosody_analysis.py
│   │   ├── filler_detection.py
│   │   ├── confidence_scoring.py
│   │   └── pipeline.py
│   ├── vision-analysis/
│   │   ├── face_landmarks.py
│   │   ├── gaze_tracking.py
│   │   ├── posture_detection.py
│   │   ├── micro_expressions.py
│   │   └── pipeline.py
│   ├── multimodal-reasoning/
│   │   ├── fusion.py            ← Weighted multimodal score fusion
│   │   ├── timeline_builder.py
│   │   ├── llm_reasoner.py      ← GPT-4 / OpenRouter feedback
│   │   └── pipeline.py
│   └── explainability/
│       ├── shap_explainer.py
│       ├── lime_explainer.py
│       ├── counterfactual.py
│       └── pipeline.py
│
├── realtime/
│   ├── signaling-server/        ← WebSocket signaling (stub, no Dockerfile)
│   └── media-router/            ← WebRTC config (stub)
│
├── infrastructure/
│   ├── docker-compose.yml       ← Full stack compose (requires Docker)
│   ├── kubernetes/              ← K8s YAML manifests
│   ├── terraform/               ← Infrastructure as Code
│   └── monitoring/              ← Prometheus + Grafana configs
│
├── docs/                        ← Architecture, API, ethics, deployment docs
├── live_speech/                 ← LanguageTool 6.6 (Java grammar checker)
├── eyeDetect/                   ← Standalone eye detection module (stub)
├── scripts/                     ← Root-level seed + setup scripts (stubs)
└── .github/workflows/           ← CI/CD (build + push Docker images)
```

---

## 6. Completion Status — Feature by Feature

### Overall: **~58% Complete**

---

### 6.1 Authentication & User Management — **90% ✅**

| Feature | Status | Notes |
|---------|--------|-------|
| Email + password registration | ✅ 100% | Full validation, bcrypt hashing |
| Email OTP verification | ✅ 100% | 6-digit code, 5-min expiry |
| Login with JWT tokens | ✅ 100% | Access + refresh tokens |
| Token refresh | ✅ 100% | Auto-refresh in frontend |
| Forgot password / reset | ✅ 100% | OTP-based reset flow |
| Google OAuth login | ⚠️ 80% | Backend ready, needs credentials |
| GitHub OAuth login | ⚠️ 80% | Backend ready, needs credentials |
| User profile (GET/PUT/DELETE) | ✅ 100% | Fixed and working |
| Role-based access (admin/coach/student) | ✅ 90% | Models done, middleware partial |
| Email sending | ⚠️ 70% | Dev: console print, prod: needs SMTP config |

---

### 6.2 Frontend UI & Pages — **85% ✅**

| Page | Status | Notes |
|------|--------|-------|
| Home / Landing | ✅ 100% | Animations, testimonials, features |
| Login | ✅ 100% | Email + OAuth buttons with error handling |
| Register | ✅ 100% | Full form with validation |
| Verify Email | ✅ 100% | OTP input page |
| Forgot Password | ✅ 100% | Request + reset flow |
| Dashboard | ✅ 90% | Shows sessions + stats from localStorage |
| Live Session | ✅ 85% | Webcam, real-time analysis panels, AI questions |
| Practice (session list) | ✅ 80% | Reads from localStorage |
| Session Detail | ✅ 80% | Shows scores from localStorage |
| Progress | ✅ 80% | Charts from localStorage data |
| Resources | ✅ 100% | Static data (30+ resources, gallery, search) |
| Resource Detail | ✅ 90% | Content view with progress |
| Profile | ✅ 85% | Edit profile, avatar |
| About | ✅ 100% | Static |
| Contact | ✅ 100% | Form (saves to localStorage) |
| Privacy / Terms | ✅ 100% | Static |
| OAuth Callback | ✅ 90% | Handles Google/GitHub redirect |

---

### 6.3 Backend API Endpoints — **70% ✅**

| Module | Status | Notes |
|--------|--------|-------|
| `POST /v1/auth/register` | ✅ 100% | Full implementation |
| `POST /v1/auth/login` | ✅ 100% | Returns `{ user, tokens }` |
| `POST /v1/auth/verify-email` | ✅ 100% | OTP verification |
| `POST /v1/auth/refresh` | ✅ 100% | Token refresh |
| `POST /v1/auth/forgot-password` | ✅ 100% | |
| `POST /v1/auth/reset-password` | ✅ 100% | |
| `GET /v1/auth/google` | ⚠️ 80% | Needs credentials |
| `GET /v1/auth/github` | ⚠️ 80% | Needs credentials |
| `GET /v1/users/me` | ✅ 100% | Fixed |
| `PUT /v1/users/me` | ✅ 100% | Fixed |
| `DELETE /v1/users/me` | ✅ 100% | Fixed |
| `GET /v1/resources/` | ✅ 100% | DB-backed, filtering, pagination |
| `GET /v1/resources/{id}` | ✅ 100% | |
| `POST /v1/resources/progress` | ✅ 100% | Track user progress |
| `GET /v1/interviews/` | ⚠️ 50% | In-memory only (not persisted to DB) |
| `POST /v1/interviews/` | ⚠️ 50% | In-memory only |
| `GET /v1/analysis/{id}` | ⚠️ 50% | In-memory only |
| `POST /v1/analysis/start` | ⚠️ 50% | Simulated background task |
| `GET /v1/reports/` | ⚠️ 50% | In-memory only |
| `POST /v1/reports/` | ⚠️ 50% | In-memory only |
| `WS /v1/behavioral/ws/{id}` | ✅ 85% | Real-time video analysis (lazy ML) |
| `WS /v1/speech/ws/{id}` | ✅ 85% | Real-time audio analysis (lazy ML) |

---

### 6.4 AI / ML Modules — **65% ✅**

| Module | Status | Notes |
|--------|--------|-------|
| **Whisper transcription** | ✅ 90% | Code complete, needs `faster-whisper` installed |
| **Prosody analysis** (speech rate, volume) | ✅ 85% | Needs `librosa` installed |
| **Filler word detection** | ✅ 90% | Pattern-based, fully coded |
| **Confidence scoring** | ✅ 85% | Vocal confidence metrics |
| **Face landmark detection** (MediaPipe) | ✅ 85% | 468-point mesh, code complete |
| **Gaze tracking** (iris position) | ✅ 85% | Eye contact %, gaze direction |
| **Posture detection** | ✅ 80% | Upright/slouch classification |
| **Micro-expression analysis** (FER) | ✅ 80% | 7 emotions, confidence scores |
| **Multimodal fusion** | ✅ 75% | Weighted score combination |
| **LLM reasoning** (GPT-4) | ⚠️ 60% | Code complete, needs `OPENAI_API_KEY` |
| **SHAP explainability** | ⚠️ 55% | Code complete, needs heavy deps |
| **LIME explainability** | ⚠️ 55% | Code complete, needs heavy deps |
| **Counterfactual generation** | ⚠️ 50% | Code complete, untested |
| **ML deps installed locally** | ❌ 0% | tensorflow, mediapipe, FER, librosa not yet pip-installed |
| **ai-services microservice running** | ❌ 0% | Separate service, no local startup |

---

### 6.5 Real-time Features — **60% ✅**

| Feature | Status | Notes |
|---------|--------|-------|
| Webcam capture in browser | ✅ 100% | MediaDevices API |
| Microphone capture in browser | ✅ 100% | MediaRecorder API |
| Video frame → WebSocket → backend | ✅ 90% | Base64 frame streaming |
| Audio chunk → WebSocket → backend | ✅ 90% | Base64 audio streaming |
| Real-time emotion overlay | ✅ 90% | Face box, emotion labels |
| Real-time gaze direction panel | ✅ 90% | Arrow indicators |
| Real-time speech rate meter | ✅ 90% | WPM display |
| WebRTC peer connection | ❌ 10% | Signaling server is a stub, no Dockerfile |
| Media router | ❌ 5% | Completely stubbed |

---

### 6.6 Data Persistence — **55% ✅**

| Feature | Status | Notes |
|---------|--------|-------|
| User accounts in SQLite | ✅ 100% | Seeded, working |
| Learning resources in SQLite | ✅ 100% | Seeded, working |
| Resource progress in SQLite | ✅ 100% | Seeded, working |
| Interview sessions in SQLite | ⚠️ 60% | DB model exists, but interview API still uses in-memory dict |
| Interview analysis in SQLite | ⚠️ 60% | DB model exists, but analysis API uses in-memory dict |
| Practice sessions (frontend) | ⚠️ 40% | Stored in **localStorage only** — lost on browser clear |
| Alembic migrations | ⚠️ 30% | Configured but never run, tables created via `init_db()` |

---

### 6.7 Infrastructure & DevOps — **30% ✅**

| Feature | Status | Notes |
|---------|--------|-------|
| Docker Compose (local) | ⚠️ 60% | Configured but Docker not installed |
| GitHub Actions CI | ✅ 80% | Builds Docker images to ghcr.io |
| Kubernetes manifests | ⚠️ 40% | YAML files present, never deployed |
| Terraform IaC | ⚠️ 20% | Files present, not configured |
| Monitoring (Prometheus/Grafana) | ⚠️ 20% | Config files present, not running |
| Actual cloud deployment | ❌ 0% | Not deployed anywhere |
| Redis (for Celery tasks) | ❌ 0% | Not running locally |
| PostgreSQL (production DB) | ❌ 0% | SQLite used locally |

---

## 7. What Is Working Right Now (Locally)

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:4321 | ✅ Running |
| Backend API | http://localhost:8000 | ✅ Running |
| API Docs (Swagger) | http://localhost:8000/docs | ✅ Running |
| SQLite Database | `backend/interview.db` | ✅ Seeded |
| Auth (email/password) | `/v1/auth/*` | ✅ Working |
| Resources API | `/v1/resources/` | ✅ Working |
| WebSocket endpoints | `/v1/behavioral/ws/`, `/v1/speech/ws/` | ✅ Ready (ML loads lazily) |

---

## 8. What Needs to Be Done to Fully Complete

### High Priority
1. **Wire interview + analysis APIs to database** — replace in-memory dicts in `interview.py`, `analysis.py`, `reports.py` with the DB-backed CRUD services that already exist
2. **Connect frontend sessions to backend** — `PracticePage`, `DashboardPage`, `ProgressPage`, `SessionDetailPage` all read from `localStorage` via `BaseCrudService` instead of calling the backend REST API
3. **Install ML dependencies** — `pip install mediapipe fer tensorflow librosa faster-whisper` in the venv (heavy, ~3–5 GB)
4. **Set up Redis** — needed for Celery task queue (background AI analysis jobs)

### Medium Priority
5. **Configure SMTP** — fill in Gmail app password in `backend/.env` for real OTP emails
6. **Configure Google/GitHub OAuth** — add credentials to `backend/.env`
7. **Set up OpenAI API key** — for LLM feedback generation (`OPENAI_API_KEY`)
8. **Run Alembic migrations** — replace the `init_db()` table-creation approach with proper migration history

### Lower Priority
9. **Deploy to cloud** — Railway/Render for backend, Vercel for frontend
10. **Build signaling server** — complete the WebRTC `realtime/signaling-server/` for peer video calls
11. **Run ai-services as separate microservice** — currently the ML logic is embedded in the backend; the `ai-services/` folder is a separate service that needs Docker to run

---

## 9. Summary Scorecard

| Category | Completion |
|----------|-----------|
| Authentication & Security | **90%** |
| Frontend UI | **85%** |
| Backend API | **70%** |
| AI / ML Modules (code) | **75%** |
| AI / ML Modules (running) | **10%** |
| Real-time Analysis | **60%** |
| Data Persistence | **55%** |
| Infrastructure / DevOps | **30%** |
| Cloud Deployment | **0%** |
| **Overall Project** | **~58%** |

---

*Report generated by automated audit. All percentages reflect code completeness + local runnability, not production readiness.*
