import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from scripts.create_first_superuser import create_first_superuser  # noqa: E402
from scripts.create_first_tier import create_first_tier  # noqa: E402
from scripts.create_provinces_and_cities import create_provinces_and_cities  # noqa: E402
from src.infrastructure.logging import get_logger  # noqa: E402

logger = get_logger()


async def setup_initial_data() -> None:
    """
    Setup initial data for the application, including:
    - Seed Iranian provinces and cities
    - Create default tier
    - Create admin superuser
    """
    logger.info("Setting up initial data...")

    logger.info("Creating provinces and cities...")
    await create_provinces_and_cities()

    logger.info("Creating first tier...")
    await create_first_tier()

    logger.info("Creating superuser...")
    await create_first_superuser()

    logger.info("Initial data setup complete")


if __name__ == "__main__":
    asyncio.run(setup_initial_data())
