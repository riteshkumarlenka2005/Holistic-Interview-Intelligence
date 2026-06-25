# Holistic Interview Intelligence

AI-powered interview preparation and analysis platform for holistic interview performance assessment.

## 🚀 Features

- **AI-Powered Analysis** - Speech, visual, and multimodal analysis
- **Real-time Feedback** - WebRTC-based live interview sessions
- **Comprehensive Reports** - Detailed feedback with explainable AI
- **Progress Tracking** - Track improvement over time
- **Practice Sessions** - Simulated interview environments

## 📁 Project Structure

```
holistic-interview-intelligence/
├── docs/                    # Documentation
│   ├── architecture/        # System design docs
│   ├── api/                 # API specifications
│   ├── ethics/              # Bias & privacy docs
│   └── deployment/          # Deployment guides
│
├── frontend/                # React/Astro Frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Astro pages
│   │   ├── hooks/           # Custom hooks
│   │   ├── styles/          # CSS styles
│   │   └── entities/        # Type definitions
│   └── public/              # Static assets
│
├── backend/                 # FastAPI Backend
│   └── app/
│       ├── api/v1/          # API endpoints
│       ├── core/            # Config & security
│       ├── models/          # Database models
│       └── services/        # Business logic
│
├── ai-services/             # AI Microservices
│   ├── speech-analysis/     # Audio processing
│   ├── vision-analysis/     # Video processing
│   ├── multimodal-reasoning/# Fusion & LLM
│   └── explainability/      # XAI modules
│
├── realtime/                # WebRTC Services
│   ├── signaling-server/    # WebSocket signaling
│   └── media-router/        # WebRTC config
│
├── infrastructure/          # DevOps
│   ├── kubernetes/          # K8s manifests
│   ├── terraform/           # IaC
│   └── monitoring/          # Observability
│
├── scripts/                 # Automation
├── tests/                   # Test suites
└── .github/workflows/       # CI/CD
```

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Astro, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, PostgreSQL, Redis |
| AI | Whisper, MediaPipe, GPT-4, SHAP/LIME |
| Realtime | WebRTC, WebSocket |
| DevOps | Docker, Kubernetes, Terraform |

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/holistic-interview-intelligence.git
cd holistic-interview-intelligence

# Setup environment
cp .env.example .env

# Start all services with Docker
docker-compose -f infrastructure/docker-compose.yml up -d

# Or run individually:

# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📚 Documentation

- [System Architecture](docs/architecture/system-architecture.md)
- [AI Pipeline](docs/architecture/ai-pipeline.md)
- [API Specification](docs/api/api-specification.md)
- [Local Development](docs/deployment/local.md)

## 🧪 Testing

```bash
# Frontend tests
cd frontend && npm run test:run

# Backend tests
cd backend && pytest

# E2E tests
cd tests/e2e && npx playwright test
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ for better interview preparation.
