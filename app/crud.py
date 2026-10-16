"""Data-access layer. Thin functions that take a Session and do one thing each.

Keeping SQL here (not in the route handlers) makes the endpoints readable and
the queries unit-testable in isolation.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def list_tasks(
    db: Session,
    *,
    status: models.Status | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[models.Task]:
    stmt = select(models.Task).order_by(models.Task.created_at.desc())
    if status is not None:
        stmt = stmt.where(models.Task.status == status)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.get(models.Task, task_id)


def create_task(db: Session, payload: schemas.TaskCreate) -> models.Task:
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(
    db: Session, task: models.Task, payload: schemas.TaskUpdate
) -> models.Task:
    # exclude_unset=True → only overwrite fields the client actually sent.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    db.delete(task)
    db.commit()
