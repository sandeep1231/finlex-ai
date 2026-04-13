from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.document import DocumentUploadResponse, DocumentListResponse
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService

settings = get_settings()
router = APIRouter()


def _get_rag_service(request: Request) -> RAGService | None:
    return request.app.state.rag_service


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="general"),
    description: str = Form(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """Upload a document for AI-powered analysis and search."""
    # Validate file size
    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_upload_size_mb}MB.",
        )

    service = DocumentService(db, rag_service)
    document = await service.upload_document(
        user=user,
        filename=file.filename,
        file_content=content,
        category=category,
        description=description,
    )
    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """List all documents for the current user's tenant."""
    service = DocumentService(db, rag_service)
    documents = await service.get_documents(user)
    return DocumentListResponse(documents=documents, total=len(documents))


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """Delete a document and remove it from the knowledge base."""
    service = DocumentService(db, rag_service)
    deleted = await service.delete_document(document_id, user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted"}
