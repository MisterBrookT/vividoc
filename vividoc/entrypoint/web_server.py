"""FastAPI web server for ViviDoc."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vividoc.core import Evaluator, Planner, RunnerConfig
from vividoc.entrypoint.api import router
from vividoc.entrypoint.api.routes import init_services
from vividoc.entrypoint.services import DocumentService, JobManager, SpecService


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="ViviDoc Web UI API",
        description="RESTful API for generating interactive educational documents",
        version="1.0.0",
    )

    # Configure CORS — allow all origins (public demo)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize services
    job_manager = JobManager()

    # Create unified config with default model (can be changed via /config endpoint)
    default_model = "openrouter/google/gemini-3-flash-preview"
    config = RunnerConfig(llm_model=default_model)

    planner = Planner(config)
    evaluator = Evaluator(config)

    spec_service = SpecService(planner, storage_base_dir="outputs")
    document_service = DocumentService(config, evaluator, job_manager)

    # Initialize route dependencies
    init_services(job_manager, spec_service, document_service)

    # Include API routes
    app.include_router(router)

    @app.get("/")
    async def root():
        """Root endpoint for health check."""
        return {"message": "ViviDoc Web UI API", "status": "running"}

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


if __name__ == "__main__":
    import uvicorn

    # Run with hot reload in development mode
    uvicorn.run(
        "vividoc.entrypoint.web_server:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable hot reload
        reload_dirs=["vividoc", "prompts"],  # Watch these directories
    )
