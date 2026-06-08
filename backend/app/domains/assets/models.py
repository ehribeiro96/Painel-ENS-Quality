from __future__ import annotations

import uuid

from app.shared.enums import AssetStatus, AssetType
from app.shared.models import Base, EntityMixin
from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Asset(EntityMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (
        Index("ix_assets_identity", "serial", "patrimony", "hostname"),
        Index("ix_assets_status_type", "status", "asset_type"),
    )

    hostname: Mapped[str | None] = mapped_column(String(120), index=True)
    patrimony: Mapped[str | None] = mapped_column(String(120), unique=True, index=True)
    serial: Mapped[str | None] = mapped_column(String(160), unique=True, index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(160))
    model: Mapped[str | None] = mapped_column(String(160))
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False, index=True)
    status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), default=AssetStatus.STOCK, nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(160), index=True)
    operating_system: Mapped[str | None] = mapped_column(String(160))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    last_login: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
    current_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    current_user = relationship("User", back_populates="assets", foreign_keys=[current_user_id], lazy="selectin")
    movements = relationship("AssetMovement", back_populates="asset", order_by="desc(AssetMovement.created_at)")
