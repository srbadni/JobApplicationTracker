import io
import tempfile
import unittest
from pathlib import Path
from typing import cast

from sqlalchemy import Table, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.interface_adapters.modules  # noqa: F401 - register every relationship target before mapper configuration
from src.frameworks.database.session import Base
from src.frameworks.storage import LocalStorage
from src.interface_adapters.modules.applicant_profile.models import ApplicantProfile
from src.interface_adapters.modules.media.enums import MediaCategory
from src.interface_adapters.modules.media.exceptions import MediaAccessDeniedError
from src.interface_adapters.modules.media.models import Media
from src.interface_adapters.modules.media.service import MediaService
from src.interface_adapters.modules.user.enums import UserType
from src.interface_adapters.modules.user.models import User


class UploadStub:
    def __init__(self, content: bytes, filename: str = "resume.pdf") -> None:
        self._content = io.BytesIO(content)
        self.filename: str | None = filename
        self.content_type: str | None = "application/pdf"
        self.size: int | None = len(content)

    async def read(self, size: int = -1) -> bytes:
        return self._content.read(size)

    async def seek(self, offset: int) -> None:
        self._content.seek(offset)


class MediaServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.storage_root = Path(self._temporary_directory.name)
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

        tables = [
            cast(Table, User.__table__),
            cast(Table, Media.__table__),
            cast(Table, ApplicantProfile.__table__),
        ]
        async with self.engine.begin() as connection:
            await connection.run_sync(lambda sync_connection: Base.metadata.create_all(sync_connection, tables=tables))

        async with self.session_factory() as session:
            applicant = User(
                name="Applicant",
                last_name="User",
                phone_number="09123456789",
                email="applicant@example.com",
                hashed_password="not-used-in-this-test",
                user_type=UserType.APPLICANT.value,
            )
            session.add(applicant)
            await session.flush()
            session.add(ApplicantProfile(applicant_id=applicant.id))
            await session.commit()
            self.applicant_id = applicant.id

        self.service = MediaService(LocalStorage(self.storage_root, chunk_size_bytes=4))
        self.current_user = {
            "id": self.applicant_id,
            "user_type": UserType.APPLICANT.value,
            "is_superuser": False,
        }

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()

    async def test_new_resume_replaces_database_record_and_local_file(self) -> None:
        async with self.session_factory() as session:
            first = await self.service.upload(
                db=session,
                current_user=self.current_user,
                category=MediaCategory.RESUME,
                upload=UploadStub(b"%PDF-1.7\nfirst resume"),
            )
            first_key = first.storage_key

        self.assertTrue((self.storage_root / first_key).is_file())

        async with self.session_factory() as session:
            second = await self.service.upload(
                db=session,
                current_user=self.current_user,
                category=MediaCategory.RESUME,
                upload=UploadStub(b"%PDF-1.7\nsecond resume"),
            )
            profile = await session.scalar(select(ApplicantProfile).where(ApplicantProfile.applicant_id == self.applicant_id))
            media_count = await session.scalar(select(func.count(Media.id)))

        self.assertIsNotNone(profile)
        assert profile is not None
        self.assertEqual(profile.attached_resume_id, second.id)
        self.assertEqual(media_count, 1)
        self.assertFalse((self.storage_root / first_key).exists())
        self.assertTrue((self.storage_root / second.storage_key).is_file())

    async def test_delete_resume_clears_profile_reference_and_local_file(self) -> None:
        async with self.session_factory() as session:
            media = await self.service.upload(
                db=session,
                current_user=self.current_user,
                category=MediaCategory.RESUME,
                upload=UploadStub(b"%PDF-1.7\nresume"),
            )
            storage_key = media.storage_key
            await self.service.delete(
                db=session,
                current_user=self.current_user,
                media_id=media.id,
            )

        async with self.session_factory() as session:
            profile = await session.scalar(select(ApplicantProfile).where(ApplicantProfile.applicant_id == self.applicant_id))
            media_count = await session.scalar(select(func.count(Media.id)))

        self.assertIsNotNone(profile)
        assert profile is not None
        self.assertIsNone(profile.attached_resume_id)
        self.assertEqual(media_count, 0)
        self.assertFalse((self.storage_root / storage_key).exists())

    async def test_employer_cannot_upload_resume(self) -> None:
        employer = {
            "id": self.applicant_id,
            "user_type": UserType.EMPLOYER.value,
            "is_superuser": False,
        }

        async with self.session_factory() as session:
            with self.assertRaises(MediaAccessDeniedError):
                await self.service.upload(
                    db=session,
                    current_user=employer,
                    category=MediaCategory.RESUME,
                    upload=UploadStub(b"%PDF-1.7\nresume"),
                )

        self.assertEqual(list(self.storage_root.iterdir()), [])
