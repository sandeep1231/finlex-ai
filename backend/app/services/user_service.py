import uuid
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.user import UserCreate


PLAN_LIMITS = {
    "free": {"max_users": 1, "max_documents": 5, "max_queries_per_month": 50},
    "professional": {"max_users": 1, "max_documents": 100, "max_queries_per_month": 1000},
    "firm": {"max_users": 20, "max_documents": 500, "max_queries_per_month": 5000},
    "enterprise": {"max_users": 100, "max_documents": 5000, "max_queries_per_month": 50000},
}


class UserService:
    """Service for user and tenant management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_and_tenant(self, user_data: UserCreate, clerk_user_id: str) -> User:
        """Create a new user with a tenant (called after Clerk signup)."""
        # Generate tenant slug
        tenant_name = user_data.tenant_name or f"{user_data.full_name}'s Workspace"
        slug = self._generate_slug(tenant_name)

        # Check for existing slug
        existing = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        if existing.scalar_one_or_none():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        # Create tenant
        limits = PLAN_LIMITS["free"]
        tenant = Tenant(
            name=tenant_name,
            slug=slug,
            plan="free",
            max_users=limits["max_users"],
            max_documents=limits["max_documents"],
            max_queries_per_month=limits["max_queries_per_month"],
        )
        self.db.add(tenant)
        await self.db.flush()

        # Create user
        user = User(
            tenant_id=tenant.id,
            clerk_user_id=clerk_user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            role="admin",
            profession=user_data.profession,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_tenant(self, tenant_id: str) -> Tenant | None:
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def upgrade_plan(self, tenant_id: str, plan: str) -> Tenant:
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError("Tenant not found")

        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        tenant.plan = plan
        tenant.max_users = limits["max_users"]
        tenant.max_documents = limits["max_documents"]
        tenant.max_queries_per_month = limits["max_queries_per_month"]

        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant

    def _generate_slug(self, name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug[:100].strip("-")
