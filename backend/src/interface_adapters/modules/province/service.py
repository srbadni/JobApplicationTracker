from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.exceptions import ResourceExistsError, ResourceNotFoundError, ValidationError
from .models import Province
from .schemas import ProvinceCreate, ProvinceUpdate


class ProvinceService:
    async def get_provinces(self, db: AsyncSession, query: str | None = None) -> Sequence[Province]:
        stmt = select(Province).order_by(Province.id)
        if query:
            stmt = stmt.where(or_(Province.name.ilike(f"%{query}%"), Province.english_name.ilike(f"%{query}%")))
        return (await db.scalars(stmt)).all()

    async def get_province(self, db: AsyncSession, province_id: int) -> Province:
        return await self._get_by_id(db, province_id)

    async def create_province(self, db: AsyncSession, province: ProvinceCreate) -> Province:
        await self._ensure_unique_names(db, province.name, province.english_name)
        db_province = Province(name=province.name, english_name=province.english_name)  # type: ignore[call-arg]
        db.add(db_province)
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ResourceExistsError("A province with one of these names already exists") from error
        await db.refresh(db_province)
        return db_province

    async def update_province(self, db: AsyncSession, province_id: int, province: ProvinceUpdate) -> Province:
        db_province = await self._get_by_id(db, province_id)
        await self._ensure_unique_names(db, province.name, province.english_name, exclude_id=province_id)
        db_province.name = province.name
        db_province.english_name = province.english_name
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ResourceExistsError("A province with one of these names already exists") from error
        await db.refresh(db_province)
        return db_province

    async def delete_province(self, db: AsyncSession, province_id: int) -> None:
        province = await self._get_by_id(db, province_id)
        await db.delete(province)
        try:
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise ValidationError("Province is in use and cannot be deleted") from error

    async def _get_by_id(self, db: AsyncSession, province_id: int) -> Province:
        province = await db.get(Province, province_id)
        if province is None:
            raise ResourceNotFoundError(f"Province with ID {province_id} not found")
        return province

    async def _ensure_unique_names(
        self,
        db: AsyncSession,
        name: str,
        english_name: str,
        exclude_id: int | None = None,
    ) -> None:
        stmt = select(Province.id).where(or_(Province.name.ilike(name), Province.english_name.ilike(english_name)))
        if exclude_id is not None:
            stmt = stmt.where(Province.id != exclude_id)
        if await db.scalar(stmt) is not None:
            raise ResourceExistsError("A province with one of these names already exists")
