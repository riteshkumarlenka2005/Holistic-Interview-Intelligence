from app.core.celery_app import celery_app
import asyncio

@celery_app.task(bind=True, max_retries=2, queue="pipeline")
def run_full_pipeline(self, job_id: str, session_id: str, config: dict):
    """
    Post-session: orchestrate speech + vision + fusion + evaluation
    (This is a stub, actual pipeline will be implemented later)
    """
    # Logic to update DB would go here
    pass

@celery_app.task(bind=True, max_retries=2, queue="pipeline")
def generate_report_task(self, session_id: str):
    """
    Background task to generate candidate and recruiter reports at the end of the session.
    Emits a websocket event upon completion.
    """
    from app.core.database import AsyncSessionLocal
    from app.services.report_engine import ReportEngine
    import socketio
    from app.core.config import get_settings
    
    async def _run():
        async with AsyncSessionLocal() as db:
            engine = ReportEngine(db)
            success = await engine.generate_reports(session_id)
            if success:
                settings = get_settings()
                mgr = socketio.RedisManager(settings.REDIS_URL, write_only=True)
                mgr.emit('report_ready', data={"session_id": session_id}, room=session_id, namespace='/interview')
            return success
            
    return asyncio.run(_run())

@celery_app.task(bind=True, max_retries=2, queue="pipeline")
def cleanup_expired_tokens(self):
    pass

@celery_app.task(bind=True, max_retries=2, queue="pipeline")
def generate_analytics_snapshots(self):
    pass
