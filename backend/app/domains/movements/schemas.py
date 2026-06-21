from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.shared.enums import AssetStatus
from pydantic import BaseModel, ConfigDict


class MovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_id: UUID
    previous_user_id: UUID | None
    new_user_id: UUID | None
    previous_status: AssetStatus
    new_status: AssetStatus
    previous_location: str | None
    new_location: str | None
    responsible_id: UUID | None
    previous_user_name: str | None = None
    new_user_name: str | None = None
    responsible_name: str | None = None
    asset_label: str | None = None
    macro_generation_id: UUID | None = None
    macro_copied: bool | None = None
    macro_copied_at: datetime | None = None
    justification: str
    notes: str | None
    created_at: datetime
