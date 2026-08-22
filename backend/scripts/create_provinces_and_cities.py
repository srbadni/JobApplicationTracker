import asyncio
import csv
from src.infrastructure.logging import get_logger

logger = get_logger()


async def create_provinces_and_cities():
    try:
        with open(
                "../data/seed/iran_locations.csv",
                encoding="utf-8-sig",
                newline=""
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(row)
    except Exception as e:
        logger.error(f"Error creating provinces and cities: {e}")


async def main() -> None:
    await create_provinces_and_cities()


if __name__ == "__main__":
    asyncio.run(main())
