"""
Main application entry point for Vision Insurance Extractor service.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import extract, health
from app.api.auth import get_api_key
from app.api.test_interface import router as test_router
from app.config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Vision Insurance Extractor",
    description="API service for extracting structured benefit information from vision insurance documents",
    version="0.1.0",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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