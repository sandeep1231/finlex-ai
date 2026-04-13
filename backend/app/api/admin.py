from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.tenant import Tenant
from app.models.document import Document
from app.models.conversation import Conversation, Message
from app.schemas.user import UserResponse, TenantResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard statistics."""
    tenant_id = user.tenant_id

    # User count
    user_count = await db.scalar(
        select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
    )

    # Document count
    doc_count = await db.scalar(
        select(func.count()).select_from(Document).where(Document.tenant_id == tenant_id)
    )

    # Conversation count
    conv_count = await db.scalar(
        select(func.count()).select_from(Conversation).where(Conversation.tenant_id == tenant_id)
    )

    # Message count
    msg_count = await db.scalar(
        select(func.count()).select_from(Message).join(Conversation).where(
            Conversation.tenant_id == tenant_id
        )
    )

    # Total queries this month
    total_queries = await db.scalar(
        select(func.sum(User.queries_this_month)).where(User.tenant_id == tenant_id)
    )

    # Tenant info
    tenant = await db.scalar(select(Tenant).where(Tenant.id == tenant_id))

    return {
        "tenant": {
            "name": tenant.name,
            "plan": tenant.plan,
            "max_queries_per_month": tenant.max_queries_per_month,
        },
        "stats": {
            "users": user_count or 0,
            "documents": doc_count or 0,
            "conversations": conv_count or 0,
            "messages": msg_count or 0,
            "queries_this_month": total_queries or 0,
        },
    }


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users in the tenant."""
    result = await db.execute(
        select(User).where(User.tenant_id == user.tenant_id).order_by(User.created_at)
    )
    return list(result.scalars().all())


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's role (admin only)."""
    if role not in ("admin", "member", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")

    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == admin.tenant_id)
    )
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user.role = role
    await db.commit()
    return {"status": "updated", "user_id": str(target_user.id), "role": role}


@router.post("/upgrade")
async def upgrade_plan(
    plan: str,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upgrade the tenant's plan."""
    if plan not in ("professional", "firm", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid plan")

    service = UserService(db)
    tenant = await service.upgrade_plan(user.tenant_id, plan)
    return {"status": "upgraded", "plan": tenant.plan}
