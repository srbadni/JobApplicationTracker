from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


def build_client(settings: Settings | None = None) -> TestClient:
    application = create_app()
    if settings is not None:
        application.dependency_overrides[get_settings] = lambda: settings
    return TestClient(application)


def test_health_check_returns_service_status():
    settings = Settings()
    response = build_client(settings).get(f"{settings.api_v1_prefix}/health")

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
    response = build_client().get("/unknown-route")

    assert response.status_code == 404


def test_health_check_uses_injected_settings():
    settings = Settings(
        app_name="Test Tracker",
        app_version="9.9.9",
        api_v1_prefix="/test-api",
    )

    response = build_client(settings).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["result"] == {
        "status": "ok",
        "service": "Test Tracker",
        "version": "9.9.9",
    }
