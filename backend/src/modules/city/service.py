from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceExistsError, ResourceNotFoundError, ValidationError
from ..province.models import Province
from .models import City
from .schemas import CityCreate, CityUpdate


class CityService:
    async def get_cities(self, db: AsyncSession, query: str | None = None, province_id: int | None = None) -> Sequence[City]:
        stmt = select(City).order_by(City.id)
        if query:
            stmt = stmt.where(or_(City.name.ilike(f"%{query}%"), City.english_name.ilike(f"%{query}%")))
        if province_id is not None:
            stmt = stmt.where(City.province_id == province_id)
        return (await db.scalars(stmt)).all()

    async def get_city(self, db: AsyncSession, city_id: int) -> City:
        return await self._get_by_id(db, city_id)

    async def create_city(self, db: AsyncSession, city: CityCreate) -> City:
        await self._ensure_province_exists(db, city.province_id)
        await self._ensure_unique_names(db, city.name, city.english_name, city.province_id)
        db_city = City(name=city.name, english_name=city.english_name, province_id=city.province_id)  # type: ignore[call-arg]
        db.add(db_city)
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ResourceExistsError("A city with one of these names already exists in the province") from error
        await db.refresh(db_city)
        return db_city

    async def update_city(self, db: AsyncSession, city_id: int, city: CityUpdate) -> City:
        db_city = await self._get_by_id(db, city_id)
        await self._ensure_province_exists(db, city.province_id)
        await self._ensure_unique_names(db, city.name, city.english_name, city.province_id, exclude_id=city_id)
        db_city.name = city.name
        db_city.english_name = city.english_name
        db_city.province_id = city.province_id
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ResourceExistsError("A city with one of these names already exists in the province") from error
        await db.refresh(db_city)
        return db_city

    async def delete_city(self, db: AsyncSession, city_id: int) -> None:
        city = await self._get_by_id(db, city_id)
        await db.delete(city)
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ValidationError("City is in use and cannot be deleted") from error

    async def _get_by_id(self, db: AsyncSession, city_id: int) -> City:
        city = await db.get(City, city_id)
        if city is None:
            raise ResourceNotFoundError(f"City with ID {city_id} not found")
        return city

    async def _ensure_province_exists(self, db: AsyncSession, province_id: int) -> None:
        if await db.get(Province, province_id) is None:
            raise ResourceNotFoundError(f"Province with ID {province_id} not found")

    async def _ensure_unique_names(
        self,
        db: AsyncSession,
        name: str,
        english_name: str,
        province_id: int,
        exclude_id: int | None = None,
    ) -> None:
        stmt = select(City.id).where(
            City.province_id == province_id,
            or_(City.name.ilike(name), City.english_name.ilike(english_name)),
        )
        if exclude_id is not None:
            stmt = stmt.where(City.id != exclude_id)
        if await db.scalar(stmt) is not None:
            raise ResourceExistsError("A city with one of these names already exists in the province")
