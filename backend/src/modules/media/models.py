"""Database metadata for privately stored files."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base

if TYPE_CHECKING:
    from ..applicant_profile.models import ApplicantProfile
    from ..user.models import User


class Media(Base, TimestampMixin):
    """Metadata for bytes persisted by the configured storage backend."""

    __tablename__ = "media"
    __table_args__ = (
        CheckConstraint(
            "category IN ('company_logo', 'user_avatar', 'resume', 'attachment')",
            name="ck_media_category",
        ),
        CheckConstraint("size_bytes > 0", name="ck_media_size_bytes_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="media_files", init=False)
    attached_resume_profile: Mapped["ApplicantProfile | None"] = relationship(
        "ApplicantProfile",
        back_populates="attached_resume",
        uselist=False,
        passive_deletes=True,
        init=False,
    )
