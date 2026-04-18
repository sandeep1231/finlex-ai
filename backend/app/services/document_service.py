import os
import uuid
import shutil
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.document import Document
from app.models.user import User
from app.models.tenant import Tenant
from app.core.exceptions import DocumentLimitException, UnsupportedFileTypeException
from app.services.rag_service import RAGService

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


class DocumentService:
    """Service for managing user document uploads and indexing."""

    def __init__(self, db: AsyncSession, rag_service: RAGService | None):
        self.db = db
        self.rag_service = rag_service

    async def upload_document(
        self,
        user: User,
        filename: str,
        file_content: bytes,
        category: str = "general",
        description: str | None = None,
    ) -> Document:
        """Upload and index a document."""
        # Validate file type
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeException(ext)

        # Check document limit
        tenant = await self._get_tenant(user.tenant_id)
        doc_count = await self._get_document_count(user.tenant_id)
        if doc_count >= tenant.max_documents:
            raise DocumentLimitException()

        # Save file
        upload_dir = Path(settings.upload_dir) / str(user.tenant_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Use a unique filename to prevent collisions
        safe_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = upload_dir / safe_filename

        with open(file_path, "wb") as f:
            f.write(file_content)

        # Index document in vector store
        chunk_count = 0
        try:
            if self.rag_service:
                chunk_count = await self.rag_service.add_document(str(file_path), category)
        except Exception:
            # Clean up file if indexing fails
            file_path.unlink(missing_ok=True)
            raise

        # Save to database
        document = Document(
            tenant_id=user.tenant_id,
            uploaded_by=user.id,
            filename=filename,
            file_type=ext.lstrip("."),
            file_size=len(file_content),
            file_path=str(file_path),
            category=category,
            description=description,
            chunk_count=chunk_count,
            is_indexed=True,
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def get_documents(self, user: User) -> list[Document]:
        """Get all documents for the user's tenant."""
        result = await self.db.execute(
            select(Document)
            .where(Document.tenant_id == user.tenant_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_document(self, document_id: str, user: User) -> bool:
        """Delete a document and remove from vector store."""
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.tenant_id == user.tenant_id,
            )
        )
        document = result.scalar_one_or_none()
        if not document:
            return False

        # Remove from vector store
        if self.rag_service:
            await self.rag_service.delete_document(document.filename)

        # Remove file
        file_path = Path(document.file_path)
        file_path.unlink(missing_ok=True)

        # Remove from database
        await self.db.delete(document)
        await self.db.commit()

        return True

    async def _get_tenant(self, tenant_id: str) -> Tenant:
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one()

    async def _get_document_count(self, tenant_id: str) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).select_from(Document).where(Document.tenant_id == tenant_id)
        )
        return result.scalar()
