# Local Development Setup

## Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-org/holistic-interview-intelligence.git
cd holistic-interview-intelligence
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Services with Docker
```bash
docker-compose up -d
```

### 4. Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### 5. Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Ports
- Frontend: http://localhost:4321
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
