"""FastAPI web server for ViviDoc."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vividoc.planner import Planner, PlannerConfig
from vividoc.executor import Executor, ExecutorConfig
from vividoc.evaluator import Evaluator, EvaluatorConfig

from vividoc.entrypoint.services import JobManager, SpecService, DocumentService
from vividoc.entrypoint.api import router
from vividoc.entrypoint.api.routes import init_services


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="ViviDoc Web UI API",
        description="RESTful API for generating interactive educational documents",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize services
    job_manager = JobManager()

    planner_config = PlannerConfig()
    executor_config = ExecutorConfig()
    evaluator_config = EvaluatorConfig()

    planner = Planner(planner_config)
    executor = Executor(executor_config)
    evaluator = Evaluator(evaluator_config)

    spec_service = SpecService(planner, storage_base_dir="outputs")
    document_service = DocumentService(executor, evaluator, job_manager)

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

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
