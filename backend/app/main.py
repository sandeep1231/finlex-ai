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

        # Re-index uploaded documents that are still on disk
        await _reindex_uploaded_documents(rag_service)
    except Exception as e:
        logger.warning(f"RAG service initialization failed: {e}. App will run without RAG context.")
        app.state.rag_service = None


async def _reindex_uploaded_documents(rag_service):
    """Re-index user-uploaded documents from disk into ChromaDB on startup.

    On Render (ephemeral filesystem), ChromaDB data is wiped on redeploy.
    This checks PostgreSQL for indexed documents and re-indexes any whose
    files still exist on disk.
    """
    import os
    from sqlalchemy import select, update
    from app.database import AsyncSessionLocal
    from app.models.document import Document

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Document).where(Document.is_indexed == True)  # noqa: E712
            )
            documents = result.scalars().all()

            if not documents:
                return

            reindexed = 0
            missing = 0
            for doc in documents:
                if doc.file_path and os.path.exists(doc.file_path):
                    try:
                        await rag_service.add_document(doc.file_path, doc.category or "general")
                        reindexed += 1
                    except Exception as e:
                        logger.warning(f"Failed to re-index {doc.filename}: {e}")
                else:
                    # File doesn't exist on disk (Render wiped it)
                    # Mark as not indexed so UI reflects reality
                    await db.execute(
                        update(Document)
                        .where(Document.id == doc.id)
                        .values(is_indexed=False)
                    )
                    missing += 1

            if missing > 0:
                await db.commit()

            logger.info(
                f"Document re-index complete: {reindexed} re-indexed, {missing} files missing"
            )
    except Exception as e:
        logger.warning(f"Document re-indexing failed: {e}")


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
