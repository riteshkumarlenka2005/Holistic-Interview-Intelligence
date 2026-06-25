from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

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
            # Bypass if redis is not available
            return await call_next(request)
            
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = await self.redis_client.get(key)
            if current and int(current) > self.rate_limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"}
                )
            
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window)
            await pipe.execute()
        except Exception as e:
            # Fallback open if redis fails
            pass
            
        return await call_next(request)

def setup_middlewares(app: FastAPI, redis_client=None):
    app.add_middleware(SecurityHeadersMiddleware)
    if redis_client:
        app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
