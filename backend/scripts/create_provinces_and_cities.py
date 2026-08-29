import asyncio
import csv
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import insert, select  # noqa: E402

from src.frameworks.database.session import local_session  # noqa: E402
from src.frameworks.logging import get_logger  # noqa: E402
from src.interface_adapters.modules.city.models import City  # noqa: E402
from src.interface_adapters.modules.province.models import Province  # noqa: E402

logger = get_logger()

LOCATIONS_FILE = backend_dir / "data" / "seed" / "iran_locations.csv"
REQUIRED_COLUMNS = {"province_fa", "city_fa", "province_en", "city_en"}


def read_locations(csv_path: Path = LOCATIONS_FILE) -> list[dict[str, str]]:
    """Read and validate province and city records from the seed CSV file."""
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
            raise ValueError(f"Missing required CSV columns: {', '.join(sorted(missing_columns))}")

        locations: list[dict[str, str]] = []
        for line_number, row in enumerate(reader, start=2):
            location = {column: row[column].strip() for column in REQUIRED_COLUMNS}
            empty_columns = [column for column, value in location.items() if not value]
            if empty_columns:
                raise ValueError(f"Empty required value(s) at CSV line {line_number}: {', '.join(sorted(empty_columns))}")
            locations.append(location)

    return locations


async def create_provinces_and_cities() -> None:
    """Add missing Iranian provinces and cities without duplicating existing rows."""
    try:
        locations = read_locations()

        # Collapse accidental duplicate rows so a single seed run remains safe.
        provinces = {location["province_fa"]: location["province_en"] for location in locations}
        cities = {(location["province_fa"], location["city_fa"]): location["city_en"] for location in locations}

        async with local_session() as session:
            existing_provinces = {province.name: province for province in (await session.scalars(select(Province))).all()}
            missing_provinces = [
                {"name": name, "english_name": english_name}
                for name, english_name in provinces.items()
                if name not in existing_provinces
            ]
            if missing_provinces:
                await session.execute(insert(Province), missing_provinces)
                await session.flush()
                existing_provinces = {province.name: province for province in (await session.scalars(select(Province))).all()}

            existing_cities = set((await session.execute(select(City.province_id, City.name))).all())
            missing_cities = [
                {
                    "name": city_name,
                    "english_name": english_name,
                    "province_id": existing_provinces[province_name].id,
                }
                for (province_name, city_name), english_name in cities.items()
                if (existing_provinces[province_name].id, city_name) not in existing_cities
            ]
            if missing_cities:
                await session.execute(insert(City), missing_cities)

            await session.commit()

        logger.info(
            "Location seed complete: %d provinces and %d cities created",
            len(missing_provinces),
            len(missing_cities),
        )
    except Exception:
        logger.exception("Error creating provinces and cities")
        raise


async def main() -> None:
    await create_provinces_and_cities()


if __name__ == "__main__":
    asyncio.run(main())
