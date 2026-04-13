from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    profession: str | None = None
    tenant_name: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    profession: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    profession: str | None
    tenant_id: str
    queries_this_month: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    max_users: int
    max_documents: int
    max_queries_per_month: int
    created_at: datetime

    model_config = {"from_attributes": True}
