from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.shared.enums import AssetStatus, AssetType
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AssetUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str


class AssetBase(BaseModel):
    hostname: str | None = Field(default=None, max_length=120)
    patrimony: str | None = Field(default=None, max_length=120)
    serial: str | None = Field(default=None, max_length=160)
    manufacturer: str | None = Field(default=None, max_length=160)
    model: str | None = Field(default=None, max_length=160)
    asset_type: AssetType
    status: AssetStatus = AssetStatus.STOCK
    location: str | None = Field(default=None, max_length=160)
    operating_system: str | None = Field(default=None, max_length=160)
    ip_address: str | None = Field(default=None, max_length=64)
    last_login: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    current_user_id: UUID | None = None


class AssetCreate(AssetBase):
    @model_validator(mode="after")
    def require_manual_identity(self) -> AssetCreate:
        if not any((self.hostname, self.patrimony, self.serial)):
            raise ValueError("Ativo manual precisa ter hostname, patrimonio ou serial.")
        return self


class AssetUpdate(BaseModel):
    hostname: str | None = Field(default=None, max_length=120)
    patrimony: str | None = Field(default=None, max_length=120)
    serial: str | None = Field(default=None, max_length=160)
    manufacturer: str | None = Field(default=None, max_length=160)
    model: str | None = Field(default=None, max_length=160)
    asset_type: AssetType | None = None
    status: AssetStatus | None = None
    location: str | None = Field(default=None, max_length=160)
    operating_system: str | None = Field(default=None, max_length=160)
    ip_address: str | None = Field(default=None, max_length=64)
    last_login: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    current_user_id: UUID | None = None


class AssetMove(BaseModel):
    new_user_id: UUID | None = None
    new_status: AssetStatus
    new_location: str | None = Field(default=None, max_length=160)
    justification: str = Field(min_length=5, max_length=500)
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_operational_consistency(self) -> AssetMove:
        if self.new_status == AssetStatus.IN_USE and self.new_user_id is None:
            raise ValueError("new_user_id is required when moving an asset to IN_USE")
        return self


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    current_user: AssetUserSummary | None = None
