#!/bin/bash
# Setup script for development environment

set -e

echo "🚀 Setting up Holistic Interview Intelligence..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "Node.js is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required"; exit 1; }

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env from template..."
    cp .env.example .env
fi

# Frontend setup
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Backend setup
echo "🐍 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate || . venv/Scripts/activate
pip install -r requirements.txt
cd ..

# Database setup
echo "🗄️ Setting up database..."
# docker-compose up -d db
# sleep 5
# cd backend && alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  Frontend: cd frontend && npm run dev"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
