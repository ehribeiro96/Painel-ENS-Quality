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
    justification: str
    notes: str | None
    created_at: datetime
