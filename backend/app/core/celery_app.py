from celery import Celery
from kombu import Queue, Exchange
from app.core.config import get_settings

settings = get_settings()

CELERY_QUEUES = [
    Queue("speech",    Exchange("speech"),    routing_key="speech"),
    Queue("vision",    Exchange("vision"),    routing_key="vision"),
    Queue("pipeline",  Exchange("pipeline"),  routing_key="pipeline"),
    Queue("reports",   Exchange("reports"),   routing_key="reports"),
    Queue("questions", Exchange("questions"), routing_key="questions"),
]

celery_app = Celery(
    "hii",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.speech_tasks",
        "app.tasks.vision_tasks",
        "app.tasks.pipeline_tasks",
        "app.tasks.report_tasks",
        "app.tasks.question_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.speech_tasks.*":   {"queue": "speech"},
        "app.tasks.vision_tasks.*":   {"queue": "vision"},
        "app.tasks.pipeline_tasks.*": {"queue": "pipeline"},
        "app.tasks.report_tasks.*":   {"queue": "reports"},
        "app.tasks.question_tasks.*": {"queue": "questions"},
    },
    beat_schedule={
        "cleanup-expired-tokens": {
            "task": "app.tasks.pipeline_tasks.cleanup_expired_tokens",
            "schedule": 3600.0,
        },
        "analytics-daily-snapshot": {
            "task": "app.tasks.pipeline_tasks.generate_analytics_snapshots",
            "schedule": 86400.0,
        },
    }
)
