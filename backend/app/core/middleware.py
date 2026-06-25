from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import uuid

from app.core.logging import logger, set_request_id

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract or generate request ID
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        set_request_id(req_id)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                f"{request.method} {request.url.path} completed in {process_time:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": int(process_time * 1000)
                }
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"{request.method} {request.url.path} failed after {process_time:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": int(process_time * 1000),
                    "error": str(e)
                },
                exc_info=True
            )
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, redis_client=None, rate_limit: int = 100, window: int = 60):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = rate_limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        if not self.redis_client:
            return await call_next(request)
            
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = await self.redis_client.get(key)
            if current and int(current) > self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"}
                )
            
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window)
            await pipe.execute()
        except Exception as e:
            pass
            
        return await call_next(request)

def setup_middlewares(app: FastAPI, redis_client=None):
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    if redis_client:
        app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
