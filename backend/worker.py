"""
Celery worker entry point
Run with: celery -A worker.celery_app worker --loglevel=info
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the celery app instance
from app.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()
