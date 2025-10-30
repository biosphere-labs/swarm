"""
Main entry point for running the Decomposition Pipeline API server.
"""

import uvicorn

from decomposition_pipeline.config.settings import settings


def main():
    """Run the FastAPI application with uvicorn."""
    uvicorn.run(
        "decomposition_pipeline.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
