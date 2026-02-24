"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.services.scheduler_service import SchedulerService
from app.routers import auth, users, leads, dashboard, audit_logs

settings = get_settings()
scheduler_service = SchedulerService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    scheduler_service.start()
    yield
    # Shutdown
    scheduler_service.scheduler.shutdown()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Lead Management & Assignment Tool",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(leads.router)
app.include_router(dashboard.router)
app.include_router(audit_logs.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
