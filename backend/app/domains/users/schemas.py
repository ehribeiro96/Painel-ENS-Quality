from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.shared.enums import Role, UserStatus
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    job_title: str | None = Field(default=None, max_length=160)
    department: str | None = Field(default=None, max_length=160)
    business_unit: str | None = Field(default=None, max_length=160)
    manager_name: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=80)
    status: UserStatus = UserStatus.ACTIVE
    role: Role = Role.VIEWER
    source: str | None = Field(default=None, max_length=80)
    source_metadata: dict[str, Any] | None = None


class UserCreate(UserBase):
    password: str | None = Field(default=None, min_length=10, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    email: EmailStr | None = None
    job_title: str | None = Field(default=None, max_length=160)
    department: str | None = Field(default=None, max_length=160)
    business_unit: str | None = Field(default=None, max_length=160)
    manager_name: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=80)
    status: UserStatus | None = None
    source: str | None = Field(default=None, max_length=80)
    source_metadata: dict[str, Any] | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str = Field(max_length=254)
    created_at: datetime
    updated_at: datetime
