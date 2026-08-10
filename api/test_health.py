from fastapi.testclient import TestClient

from core.config import settings
from main import app

client = TestClient(app)


def test_health_check_returns_service_status():
    response = client.get(f"{settings.api_v1_prefix}/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Service is healthy",
        "result": {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
        },
    }


def test_unknown_route_returns_404():
    response = client.get("/unknown-route")

    assert response.status_code == 404

