import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import auth, chat, documents, calculator, admin
from app.core.middleware import RateLimitMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)


async def _init_rag_background(app: FastAPI):
    """Initialize RAG service in background so server starts immediately."""
    try:
        from app.services.rag_service import RAGService
        rag_service = RAGService()
        await rag_service.initialize()
        app.state.rag_service = rag_service
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.warning(f"RAG service initialization failed: {e}. App will run without RAG context.")
        app.state.rag_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create database tables
    from app.database import engine, Base
    from app.models import tenant, user, conversation, document  # noqa: F401 - import to register models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    # Start RAG initialization in background (non-blocking)
    app.state.rag_service = None
    rag_task = asyncio.create_task(_init_rag_background(app))
    yield
    # Shutdown - cancel RAG init if still running
    if not rag_task.done():
        rag_task.cancel()


app = FastAPI(
    title=settings.app_name,
    description="AI-powered assistant for Accounting & Law professionals in India",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.add_middleware(RateLimitMiddleware)

# Routes
app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["Authentication"])
app.include_router(chat.router, prefix=f"{settings.api_prefix}/chat", tags=["AI Chat"])
app.include_router(documents.router, prefix=f"{settings.api_prefix}/documents", tags=["Documents"])
app.include_router(calculator.router, prefix=f"{settings.api_prefix}/calculator", tags=["Calculators"])
app.include_router(admin.router, prefix=f"{settings.api_prefix}/admin", tags=["Admin"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}
