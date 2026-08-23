from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...infrastructure.database.models import TimestampMixin
from ...infrastructure.database.session import Base
from .enums import MediaCategory

if TYPE_CHECKING:
    from ..user.models import User


class Media(Base, TimestampMixin):
    """Metadata for a file whose bytes live in the configured storage backend."""

    __tablename__ = "media"
    __table_args__ = (
        CheckConstraint(
            "category IN ('company_logo', 'user_avatar', 'resume', 'attachment')",
            name="ck_media_category",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uploaded_by_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
    )
    uploaded_by: Mapped["User | None"] = relationship("User", init=False)

    @property
    def media_category(self) -> MediaCategory:
        return MediaCategory(self.category)
