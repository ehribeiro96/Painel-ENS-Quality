from __future__ import annotations

from app.shared.enums import Role, UserStatus
from app.shared.models import Base, EntityMixin
from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(EntityMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    job_title: Mapped[str | None] = mapped_column(String(160))
    department: Mapped[str | None] = mapped_column(String(160), index=True)
    business_unit: Mapped[str | None] = mapped_column(String(160), index=True)
    manager_name: Mapped[str | None] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(80))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, index=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.VIEWER, nullable=False)
    source: Mapped[str | None] = mapped_column(String(80))
    source_metadata: Mapped[dict | None] = mapped_column(JSONB)

    assets = relationship("Asset", back_populates="current_user", foreign_keys="Asset.current_user_id")
