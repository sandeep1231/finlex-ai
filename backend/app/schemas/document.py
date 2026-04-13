from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    category: str
    chunk_count: int
    is_indexed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentUploadResponse]
    total: int
