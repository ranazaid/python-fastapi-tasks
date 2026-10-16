"""FastAPI application: a small but complete Tasks REST API.

Endpoints:
    GET    /tasks           list (filter by ?status=, paginate with ?skip=&limit=)
    POST   /tasks           create
    GET    /tasks/{id}      retrieve one
    PATCH  /tasks/{id}      partial update
    DELETE /tasks/{id}      delete
    GET    /health          liveness probe

Interactive docs are auto-generated at /docs (Swagger) and /redoc.
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

# For a demo we create tables on startup. In a real project use Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tasks API",
    version="1.0.0",
    summary="A minimal, production-shaped CRUD API built with FastAPI.",
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[schemas.TaskRead], tags=["tasks"])
def list_tasks(
    status: models.Status | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.list_tasks(db, status=status, skip=skip, limit=limit)


@app.post(
    "/tasks",
    response_model=schemas.TaskRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, payload)


def _get_or_404(db: Session, task_id: int) -> models.Task:
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.get("/tasks/{task_id}", response_model=schemas.TaskRead, tags=["tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, task_id)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskRead, tags=["tasks"])
def update_task(
    task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)
):
    task = _get_or_404(db, task_id)
    return crud.update_task(db, task, payload)


@app.delete(
    "/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"]
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    crud.delete_task(db, task)
