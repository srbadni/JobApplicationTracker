from app.core.config import Settings
from app.features.health.schemas import HealthResult


def get_health(settings: Settings) -> HealthResult:
    """Describe the current process without coupling domain logic to HTTP."""
    return HealthResult(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )
