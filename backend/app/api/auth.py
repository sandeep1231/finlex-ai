from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user, verify_clerk_token
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, TenantResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user after Clerk authentication."""
    # Extract Clerk token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = auth_header.split(" ", 1)[1]
    clerk_data = await verify_clerk_token(token)
    clerk_user_id = clerk_data.get("sub")

    if not clerk_user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    service = UserService(db)

    # Check if user already exists
    existing = await service.get_user_by_clerk_id(clerk_user_id)
    if existing:
        raise HTTPException(status_code=409, detail="User already registered")

    user = await service.create_user_and_tenant(user_data, clerk_user_id)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    service = UserService(db)
    updated = await service.update_user(
        user,
        full_name=update_data.full_name,
        profession=update_data.profession,
    )
    return updated


@router.get("/tenant", response_model=TenantResponse)
async def get_tenant_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's tenant/organization info."""
    service = UserService(db)
    tenant = await service.get_tenant(user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
