"""
Main FastAPI application for the Decomposition Pipeline.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from decomposition_pipeline.config.settings import settings
from decomposition_pipeline.errors.handlers import register_error_handlers
from decomposition_pipeline.middleware import ErrorHandlingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.api_title} v{settings.api_version}")
    print(f"Debug mode: {settings.debug}")

    # Create checkpoint directory if it doesn't exist
    import os

    os.makedirs(os.path.dirname(settings.checkpoint_db_path), exist_ok=True)

    yield

    # Shutdown
    print("Shutting down Decomposition Pipeline API")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add error handling middleware
app.add_middleware(
    ErrorHandlingMiddleware,
    enable_request_logging=settings.debug,
)

# Register error handlers
register_error_handlers(app)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": settings.api_title,
            "version": settings.api_version,
        },
    )


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint with configuration information."""
    return {
        "api_version": settings.api_version,
        "llm_provider": settings.default_llm_provider,
        "model": settings.default_model,
        "approval_gates": {
            "paradigm": settings.require_approval_paradigm,
            "technique": settings.require_approval_technique,
            "decomposition": settings.require_approval_decomposition,
            "solution": settings.require_approval_solution,
        },
        "limits": {
            "max_concurrent_agents": settings.max_concurrent_agents,
            "recursion_limit": settings.recursion_limit,
            "agent_timeout": settings.agent_timeout,
        },
    }


# Include routers (will be added in future tasks)
# from decomposition_pipeline.api.routers import pipeline, sse
# app.include_router(pipeline.router, prefix="/api/v1")
# app.include_router(sse.router, prefix="/api/v1")
