from __future__ import annotations

import uuid

from app.shared.enums import AssetStatus
from app.shared.models import Base, EntityMixin
from sqlalchemy import Enum, ForeignKey, Index, String, Text, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AssetMovement(EntityMixin, Base):
    __tablename__ = "asset_movements"
    __table_args__ = (
        Index("ix_asset_movements_asset_created_at", "asset_id", "created_at"),
        Index("ix_asset_movements_responsible_created_at", "responsible_id", "created_at"),
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    previous_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    new_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    previous_status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), nullable=False)
    new_status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), nullable=False)
    previous_location: Mapped[str | None] = mapped_column(String(160))
    new_location: Mapped[str | None] = mapped_column(String(160))
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    justification: Mapped[str] = mapped_column(String(500), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    asset = relationship("Asset", back_populates="movements")


@event.listens_for(AssetMovement, "before_update")
def prevent_movement_update(*_: object) -> None:
    raise ValueError("asset_movements_are_immutable")


@event.listens_for(AssetMovement, "before_delete")
def prevent_movement_delete(*_: object) -> None:
    raise ValueError("asset_movements_are_immutable")
