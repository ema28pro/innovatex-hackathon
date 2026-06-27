import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Pre-warm AI provider on startup
    try:
        from app.ai import get_ai_provider
        get_ai_provider()
    except Exception:
        logger.warning("AI provider not available at startup")
    yield
    # Gracefully close AI provider HTTP clients
    try:
        from app.ai import close_ai_provider
        await close_ai_provider()
    except Exception:
        logger.warning("Failed to close AI provider cleanly")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


from app.routers import auth
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

from app.routers import companies
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])

from app.routers import questions
app.include_router(questions.router, prefix="/api", tags=["Questions"])

from app.routers import assessments
app.include_router(assessments.router, prefix="/api", tags=["Assessments"])

from app.routers import reports
app.include_router(reports.router, prefix="/api", tags=["Reports"])


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}
