import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_calculator_income_tax_unauthenticated(client: AsyncClient):
    response = await client.post(
        "/api/v1/calculator/income-tax",
        json={"gross_income": 1500000, "regime": "new"},
    )
    # Should require auth
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_calculator_gst_unauthenticated(client: AsyncClient):
    response = await client.post(
        "/api/v1/calculator/gst",
        json={"amount": 10000, "gst_rate": 18},
    )
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_chat_unauthenticated(client: AsyncClient):
    response = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello", "mode": "general"},
    )
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_documents_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/documents/")
    assert response.status_code in [401, 403]
