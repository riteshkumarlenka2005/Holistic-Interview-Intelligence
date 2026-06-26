"""
Holistic Interview Intelligence - Backend API
FastAPI application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, interview, analysis, reports, resources, recruiter, config, privacy, system
from app.core.config import get_settings
from app.core.database import init_db, check_db_health, dispose_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup: Initialize database tables
    await init_db()
    yield
    # Shutdown: Dispose engine connections
    await dispose_engine()


app = FastAPI(
    title="Holistic Interview Intelligence API",
    description="Backend API for interview analysis platform with AI-powered feedback",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.middleware import setup_middlewares
from app.core.redis_client import get_redis_client
redis_client = get_redis_client()
setup_middlewares(app, redis_client=redis_client)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Holistic Interview Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database, redis, and celery status"""
    from app.core.redis_client import get_redis_client
    from app.core.celery_app import celery_app
    
    db_status = await check_db_health()
    
    # Check Redis
    redis_client = get_redis_client()
    redis_up = False
    if redis_client:
        try:
            redis_up = await redis_client.ping()
        except Exception:
            pass
            
    # Check Celery
    celery_up = False
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats() if inspect else None
        celery_up = stats is not None
    except Exception:
        pass
        
    return {
        "api": "healthy",
        "database": "healthy" if db_status.get("status") == "healthy" else "degraded",
        "redis": "healthy" if redis_up else "degraded",
        "celery": "healthy" if celery_up else "degraded",
        "storage": "healthy", # Assuming healthy if API is up
        "llm_provider": "healthy" # Assuming healthy if API is up
    }


# Include API routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(interview.router, prefix="/v1/interviews", tags=["Interviews"])
app.include_router(analysis.router, prefix="/v1/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/v1/reports", tags=["Reports"])
app.include_router(recruiter.router, prefix="/v1/recruiter", tags=["Recruiter"])
app.include_router(resources.router, prefix="/v1/resources", tags=["Learning Resources"])
app.include_router(config.router, prefix="/v1/config", tags=["Configuration"])
app.include_router(privacy.router, prefix="/v1/privacy", tags=["Privacy"])
app.include_router(system.router, prefix="/v1/system", tags=["System"])

# WebSocket routers
from app.api.v1 import speech_ws, behavioral_ws
app.include_router(speech_ws.router, prefix="/v1/speech", tags=["Speech Analysis WS"])
app.include_router(behavioral_ws.router, prefix="/v1/behavioral", tags=["Behavioral Analysis WS"])

from app.api.v1 import metrics
app.include_router(metrics.router, prefix="/metrics", tags=["Monitoring"])

# Mount Socket.IO application
from app.core.socketio_server import sio_app
app.mount("/", sio_app)
