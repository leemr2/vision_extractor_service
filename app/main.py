"""
Main application entry point for Vision Insurance Extractor service.
"""
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api import extract, health
from app.api.auth import get_api_key
from app.api.test_interface import router as test_router
from app.config.settings import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

# Initialize FastAPI app
app = FastAPI(
    title="Vision Insurance Extractor",
    description="API service for extracting structured benefit information from vision insurance documents",
    version="0.1.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Relaxed CSP for test interface (allows inline scripts/styles), strict for API
    if request.url.path.startswith("/test"):
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    # Add rate limit info to headers
    if hasattr(request.state, "view_rate_limit"):
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
    return response

# Include routers
app.include_router(
    extract.router,
    prefix="/api",
    dependencies=[Depends(get_api_key)],
    tags=["extraction"],
)

app.include_router(
    test_router,
    prefix="",
    tags=["testing"],
)

app.include_router(
    health.router,
    prefix="",
    tags=["health"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 