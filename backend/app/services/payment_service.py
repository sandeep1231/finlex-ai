import hmac
import hashlib

import razorpay
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services.user_service import UserService

settings = get_settings()


class PaymentService:
    """Service for Razorpay payment integration."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        ) if settings.razorpay_key_id else None

    async def create_subscription(self, tenant_id, plan_id: str) -> dict:
        """Create a Razorpay subscription for a tenant."""
        if not self.client:
            return {"error": "Payment system not configured"}

        plan_map = {
            "professional": settings.razorpay_key_id and "plan_professional",
            "firm": settings.razorpay_key_id and "plan_firm",
        }

        razorpay_plan_id = plan_map.get(plan_id)
        if not razorpay_plan_id:
            return {"error": "Invalid plan"}

        subscription = self.client.subscription.create({
            "plan_id": razorpay_plan_id,
            "total_count": 12,
            "quantity": 1,
        })

        return {
            "subscription_id": subscription["id"],
            "short_url": subscription.get("short_url"),
            "status": subscription["status"],
        }

    async def verify_payment(self, payment_data: dict) -> bool:
        """Verify a Razorpay payment signature."""
        if not self.client:
            return False

        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": payment_data.get("razorpay_order_id", ""),
                "razorpay_payment_id": payment_data["razorpay_payment_id"],
                "razorpay_signature": payment_data["razorpay_signature"],
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    async def handle_webhook(self, payload: dict, signature: str) -> bool:
        """Handle Razorpay webhook events."""
        if not settings.razorpay_key_secret:
            return False

        # Verify webhook signature
        expected_signature = hmac.new(
            settings.razorpay_key_secret.encode(),
            str(payload).encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return False

        event = payload.get("event")
        if event == "subscription.activated":
            # Upgrade tenant plan
            pass
        elif event == "subscription.cancelled":
            # Downgrade tenant plan
            pass

        return True
