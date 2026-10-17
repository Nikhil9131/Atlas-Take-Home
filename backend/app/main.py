"""FastAPI Application Entry Point for Project Atlas."""

import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import seed_database_if_empty
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.api.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown routines."""
    logger.info("Initializing Project Atlas AI Research Copilot service...")
    
    # 1. Initialize DB and seed assignment data
    try:
        seed_database_if_empty()
    except Exception as e:
        logger.error(f"Database initialization error on startup: {e}")

    # 2. Ingest synthetic market reports if vector store is empty
    try:
        from backend.app.rag.vector_store import vector_store
        if vector_store.count() == 0:
            logger.info("Vector database empty on startup. Triggering ingestion pipeline...")
            IngestionPipeline.run_ingestion()
    except Exception as e:
        logger.error(f"Vector store ingestion error on startup: {e}")

    logger.info("Project Atlas service successfully initialized and ready for inquiries.")
    yield
    logger.info("Shutting down Project Atlas service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Style Evidence-Grounded AI Research Copilot for Cognitive Market Research and Consulting.",
    lifespan=lifespan
)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows CodeIgniter 3 frontend and local test callers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_and_metrics_middleware(request: Request, call_next):
    """Adds correlation request IDs, execution timing, and structured request logging."""
    request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"
    start_time = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000.0
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} in {duration_ms:.2f}ms",
        extra={"duration_ms": duration_ms, "request_id": request_id}
    )

    return response


# Include API Endpoints
app.include_router(api_router, prefix=settings.API_PREFIX)
# Also include root-level route aliases matching assignment spec
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/health"
    }
