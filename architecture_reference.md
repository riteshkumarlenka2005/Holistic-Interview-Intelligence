# Holistic Interview Intelligence - Complete Architecture Reference

This document serves as the master blueprint of the Holistic Interview Intelligence platform, detailing the structural, infrastructural, and behavioral architectures of the system.

---

## 1. Folder Architecture

The project follows a monorepo structure separating the frontend, backend, and infrastructure definitions.

```text
Holistic-Interview-Intelligence/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # REST and WebSocket route definitions
│   │   ├── core/           # Config, Security, Celery, and DB session logic
│   │   ├── models/         # SQLAlchemy ORM definitions
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Core Business Logic & AI Engines
│   │   └── tasks/          # Celery asynchronous background tasks
│   ├── tests/              # (Empty/Placeholder)
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend and Worker container image definition
├── frontend/
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── components/     # Reusable React components (UI/Interactive)
│   │   ├── hooks/          # Custom React hooks (useSpeechAnalysis)
│   │   ├── lib/            # Utilities (axios setup, tailwind merge)
│   │   ├── pages/          # Astro pages (Routing boundary)
│   │   └── store/          # Zustand global state management
│   ├── astro.config.*      # Astro build configurations
│   ├── tailwind.config.js  # Styling tokens
│   ├── package.json        # Node dependencies
│   └── Dockerfile          # Frontend container image definition
├── infrastructure/
│   ├── docker-compose.yml       # Local development stack
│   └── docker-compose.prod.yml  # Production deployment stack
├── scripts/                # CI/CD and load testing scripts
└── Makefile                # Developer workflow commands
```

---

## 2. Service Architecture

The system is a distributed micro-monolith:
1.  **Frontend Service (Astro + React):** Handles client-side rendering, WebRTC device capture, and WebSocket transmission.
2.  **API Gateway / Backend (FastAPI):** Handles REST routing, database CRUD, and active WebSocket streams. Integrates directly with synchronous ML models.
3.  **Task Worker (Celery):** Processes heavy background tasks (LLM report generation, async email sending).
4.  **Task Scheduler (Celery Beat):** Handles cron-based periodic cleanup tasks.
5.  **Database (PostgreSQL):** Primary persistent store.
6.  **Message Broker (Redis):** Handles Celery task queuing and Pub/Sub.

---

## 3. Database ER Diagram

```mermaid
erDiagram
    USERS ||--o{ INTERVIEW_SESSIONS : "has many"
    USERS {
        uuid id PK
        string email
        string password_hash
        string role
        string oauth_provider
        boolean is_verified
    }
    
    INTERVIEW_SESSIONS ||--o{ RESPONSES : "contains"
    INTERVIEW_SESSIONS ||--o{ INTEGRITY_EVENTS : "triggers"
    INTERVIEW_SESSIONS ||--o| REPORTS : "generates"
    INTERVIEW_SESSIONS {
        uuid id PK
        uuid user_id FK
        string status
        string current_state
        string target_job_role
        int difficulty_modifier
        datetime started_at
        datetime ended_at
    }

    RESPONSES {
        uuid id PK
        uuid session_id FK
        uuid question_id FK
        string transcript
        int technical_score
        int communication_score
        jsonb detailed_feedback
    }

    INTEGRITY_EVENTS {
        uuid id PK
        uuid session_id FK
        string event_type
        float timestamp
    }

    REPORTS {
        uuid id PK
        uuid session_id FK
        int readiness_score
        jsonb radar_data
        jsonb executive_summary
        jsonb learning_roadmap
    }
```

---

## 4. API Architecture
*   **Protocol:** HTTP/1.1 (REST) and HTTP/1.1 Upgrade (WebSockets).
*   **Framework:** FastAPI (Python).
*   **Documentation:** OpenAPI (Swagger UI) auto-generated at `/docs`.
*   **Authentication:** JWT Bearer tokens passed via `Authorization` header.

## 5. WebSocket Architecture
*   **Endpoints:** `/ws/speech/{session_id}` and `/ws/behavioral/{session_id}`.
*   **Data Flow:** Binary chunk streams (WebM for audio, base64 JPEGs for video).
*   **Event Loop:** Starlette handles connections asynchronously. Frames are pushed to a `deque` buffer and processed in a synchronous executor pool to prevent blocking the async loop.

## 6. Celery Architecture
*   **Broker:** Redis (Port 6379, DB 0).
*   **Result Backend:** Redis.
*   **Workers:** Dedicated Docker container running `celery -A app.core.celery_app worker`.
*   **Tasks:** `generate_post_interview_report`, `generate_dynamic_question`.

## 7. Redis Architecture
*   Currently used exclusively as the message queue for Celery.
*   *Limitation:* Not currently utilized for Application caching or cross-node WebSocket pub/sub (which prevents horizontal scaling of the FastAPI backend).

## 8. LLM Architecture
*   **Wrapper:** LiteLLM.
*   **Providers:** OpenAI (`gpt-4o`), Google (`gemini-1.5-pro`), Anthropic (`claude-3-5-sonnet`).
*   **Usage:** Semantic JSON generation for technical evaluation, communication evaluation, dynamic question creation, and final executive summaries.

## 9. Deployment & 10. Docker Architecture
*   **Containerization:** Multi-stage Dockerfiles for minimal image sizes.
*   **Orchestration:** Docker Compose (`infrastructure/docker-compose.yml`).
*   **Network:** Shared internal Docker network. Ports exposed only for Frontend (4321) and Backend API (8000). Databases are hidden from host network.

## 11. Kubernetes Architecture
*   *Missing:* Currently, there are no Helm charts or Kubernetes YAML manifests (`Deployment`, `Service`, `Ingress`) present in the repository.

## 12. CI/CD Architecture
*   **CI:** GitHub Actions (`.github/workflows/ci.yml`). Triggers on Pull Requests. Runs Ruff linting and PyTest (though tests are currently missing).
*   **CD:** `cd.yml` placeholder. Does not currently push images to a registry or trigger cloud deployments.

---

## Sequence Diagrams

### 1. Login
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB
    User->>Frontend: Enters Email & Password
    Frontend->>API: POST /api/v1/auth/login
    API->>DB: Query User by Email
    DB-->>API: User Record
    API->>API: Verify Password Hash
    API-->>Frontend: JWT Access Token
    Frontend->>Frontend: Store Token in Zustand/Storage
    Frontend-->>User: Redirect to Dashboard
```

### 2. Interview Start
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB
    User->>Frontend: Click "Start Practice"
    Frontend->>API: POST /api/v1/interviews
    API->>DB: Create InterviewSession (Status: DRAFT)
    DB-->>API: Session ID
    API-->>Frontend: Session ID
    Frontend->>Frontend: Request Camera/Mic Permissions
    Frontend->>API: GET /api/v1/interviews/{id}/start
    API->>DB: Update Status -> IN_PROGRESS
    API-->>Frontend: 200 OK
    Frontend-->>User: Display Video Feed & First Question
```

### 3. Audio Processing
```mermaid
sequenceDiagram
    participant Frontend
    participant API(WebSocket)
    participant SpeechEngine
    participant WhisperModel
    loop Every 3 seconds
        Frontend->>API(WebSocket): Send binary WebM audio chunk
        API(WebSocket)->>API(WebSocket): Buffer chunk
        API(WebSocket)->>SpeechEngine: Process Buffer
        SpeechEngine->>WhisperModel: Transcribe (int8 CPU)
        WhisperModel-->>SpeechEngine: Text Transcript
        SpeechEngine->>SpeechEngine: Calculate WPM, Filler Rate
        SpeechEngine-->>API(WebSocket): Acoustic Metrics JSON
        API(WebSocket)-->>Frontend: Send Live Metrics (UI Update)
    end
```

### 4. Video Processing
```mermaid
sequenceDiagram
    participant Frontend
    participant API(WebSocket)
    participant FaceEngine
    participant EyeEngine
    loop Every 500ms
        Frontend->>API(WebSocket): Send Base64 Video Frame
        API(WebSocket)->>FaceEngine: Detect Face & Pose
        FaceEngine-->>API(WebSocket): Engagement Score, Head Stability
        API(WebSocket)->>EyeEngine: Detect Iris (Gaze Ratio)
        EyeEngine-->>API(WebSocket): Eye Contact %
        API(WebSocket)-->>Frontend: Behavioral Metrics JSON
    end
```

### 5. Question Generation
```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant InterviewBrain
    participant LLM
    participant DB
    Frontend->>API: POST /api/v1/interviews/{id}/next-question
    API->>InterviewBrain: Request Question
    InterviewBrain->>DB: Fetch TopicMemory & Previous Answer
    InterviewBrain->>LLM: Generate adaptive question prompt
    LLM-->>InterviewBrain: JSON (Question, Topic, Difficulty)
    InterviewBrain->>DB: Save Question to Session
    InterviewBrain-->>API: Next Question String
    API-->>Frontend: Display & TTS Next Question
```

### 6. Answer Evaluation
```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant InterviewBrain
    participant TechEngine
    participant CommEngine
    participant DB
    Frontend->>API: POST /api/v1/interviews/{id}/answer
    API->>InterviewBrain: Evaluate(Transcript)
    par Parallel Engines
        InterviewBrain->>TechEngine: Eval Tech Correctness
        InterviewBrain->>CommEngine: Eval STAR / Clarity
    end
    TechEngine-->>InterviewBrain: Tech Score & Feedback
    CommEngine-->>InterviewBrain: Comm Score & Feedback
    InterviewBrain->>InterviewBrain: Weight & Aggregate Scores
    InterviewBrain->>DB: Save Response Record
    InterviewBrain-->>API: Success
    API-->>Frontend: Updated Progress Bar
```

### 7. Report Generation
```mermaid
sequenceDiagram
    participant API
    participant Celery
    participant ReportEngine
    participant LLM
    participant DB
    API->>Celery: Async Task (generate_report)
    Celery->>ReportEngine: Start Processing
    ReportEngine->>DB: Fetch all Responses & Integrity Events
    ReportEngine->>ReportEngine: Calculate Radar & Readiness Scores
    ReportEngine->>LLM: Generate Executive Summary
    LLM-->>ReportEngine: Summary String
    ReportEngine->>DB: Create Report Record
    ReportEngine-->>Celery: Task Complete
```

### 8. Dashboard Loading
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB
    User->>Frontend: Navigate to /dashboard
    Frontend->>API: GET /api/v1/interviews?status=COMPLETED
    API->>DB: Select Sessions where user_id=X
    DB-->>API: List of Sessions
    API-->>Frontend: JSON Array
    Frontend-->>User: Render Interview History List
```

### 9. Playback
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    Note right of Frontend: FEATURE MISSING IN CODEBASE
    User->>Frontend: Click "Watch Replay"
    Frontend-->>User: (Not Implemented - No S3 Integration)
```

### 10. Recruiter Review
```mermaid
sequenceDiagram
    participant Recruiter
    participant Frontend
    participant API
    participant DB
    Note right of Frontend: UI MISSING IN CODEBASE
    Recruiter->>Frontend: View Candidate
    Frontend->>API: GET /api/v1/recruiter/candidates/{id}/report
    API->>DB: Fetch Report Data
    DB-->>API: Report JSON
    API-->>Frontend: Report JSON
    Frontend-->>Recruiter: Display Hiring Recommendation
```

---

## Complete System Dependency Graph

```mermaid
graph TD
    %% Frontend Layer
    subgraph Frontend [Frontend SPA]
        AstroPages[Astro Routing]
        ReactUI[React UI Components]
        Zustand[Zustand State]
        Hooks[Custom Hooks e.g. useSpeechAnalysis]
        
        AstroPages --> ReactUI
        ReactUI --> Zustand
        ReactUI --> Hooks
    end

    %% API Layer
    subgraph BackendAPI [FastAPI Backend]
        AuthRouter[Auth API]
        InterviewRouter[Interview API]
        ReportRouter[Report API]
        WebSockets[WebSocket Routes]
        
        Hooks -->|REST| AuthRouter
        Hooks -->|REST| InterviewRouter
        Hooks -->|REST| ReportRouter
        Hooks -->|WS Binary| WebSockets
    end

    %% Services / Engines
    subgraph AIServices [AI Services & Engines]
        InterviewBrain[Interview Brain]
        TechEngine[Technical Engine]
        CommEngine[Communication Engine]
        SpeechEngine[Speech Engine]
        FaceEngine[Face Engine]
        EyeEngine[Eye Tracking]
        ConfidenceEngine[Confidence Engine]
        CoachingEngine[Coaching Engine]
        IntegrityEngine[Integrity Engine]
        ReportEngine[Report Engine]
        LiteLLM[LLM Service Wrapper]
        
        WebSockets --> SpeechEngine
        WebSockets --> FaceEngine
        WebSockets --> EyeEngine
        
        FaceEngine --> ConfidenceEngine
        EyeEngine --> ConfidenceEngine
        SpeechEngine --> ConfidenceEngine
        
        FaceEngine --> CoachingEngine
        EyeEngine --> CoachingEngine
        SpeechEngine --> CoachingEngine
        
        InterviewRouter --> InterviewBrain
        InterviewBrain --> TechEngine
        InterviewBrain --> CommEngine
        ConfidenceEngine --> InterviewBrain
        
        TechEngine --> LiteLLM
        CommEngine --> LiteLLM
        InterviewBrain --> LiteLLM
        ReportEngine --> LiteLLM
    end

    %% Background Processing
    subgraph AsyncTasks [Celery Background Workers]
        WorkerTasks[Celery Task Queue]
        BeatTasks[Celery Beat Scheduler]
        
        InterviewRouter -->|Queue Task| WorkerTasks
        WorkerTasks --> ReportEngine
    end

    %% Data & Infrastructure
    subgraph Infrastructure [Infrastructure & DB]
        Redis[(Redis Message Broker)]
        Postgres[(PostgreSQL DB)]
        ThirdPartyLLM((OpenAI/Gemini/Anthropic APIs))
        
        AuthRouter --> Postgres
        InterviewRouter --> Postgres
        ReportRouter --> Postgres
        ReportEngine --> Postgres
        InterviewBrain --> Postgres
        IntegrityEngine --> Postgres
        
        BackendAPI --> Redis
        Redis --> WorkerTasks
        BeatTasks --> Redis
        
        LiteLLM --> ThirdPartyLLM
    end
```
