# System Architecture

## Overview
Holistic Interview Intelligence is a comprehensive interview preparation and analysis platform.

## High-Level Architecture

```mermaid
graph TB
    subgraph Frontend
        UI[React/Next.js UI]
        WC[WebRTC Client]
    end
    
    subgraph Backend
        API[FastAPI Server]
        Auth[Auth Service]
        WS[WebSocket Handler]
    end
    
    subgraph AI Services
        SA[Speech Analysis]
        VA[Vision Analysis]
        MR[Multimodal Reasoning]
    end
    
    subgraph Storage
        DB[(PostgreSQL)]
        S3[(Object Storage)]
    end
    
    UI --> API
    WC --> WS
    API --> Auth
    API --> SA
    API --> VA
    SA --> MR
    VA --> MR
    API --> DB
    API --> S3
```

## Components

### Frontend
- React-based SPA with SSR support
- WebRTC for real-time video/audio streaming
- Zustand for state management

### Backend
- FastAPI for REST API
- WebSocket for real-time communication
- JWT-based authentication

### AI Services
- Speech analysis using Whisper
- Vision analysis for facial expressions
- Multimodal fusion for comprehensive assessment

### Storage
- PostgreSQL for structured data
- Object storage for media files
