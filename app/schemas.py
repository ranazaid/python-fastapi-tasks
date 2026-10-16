"""Pydantic v2 schemas — the API's request/response contract.

Kept separate from ORM models so the wire format can evolve independently of
the database schema.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Status


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: Status = Status.todo


class TaskCreate(TaskBase):
    """Payload for POST /tasks."""


class TaskUpdate(BaseModel):
    """Payload for PATCH /tasks/{id} — every field optional (partial update)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: Status | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)  # read straight off ORM objects

    id: int
    created_at: datetime
    updated_at: datetime
