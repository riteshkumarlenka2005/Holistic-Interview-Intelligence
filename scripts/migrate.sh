#!/bin/bash
# Database migration script

set -e

echo "🗄️ Running database migrations..."

cd backend

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Run migrations
alembic upgrade head

echo "✅ Migrations complete!"
