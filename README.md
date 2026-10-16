# FastAPI — Tasks API

A small, production-shaped CRUD REST API: layered architecture (routes → crud →
ORM), Pydantic request/response schemas separate from the DB models, filtering +
pagination, proper status codes, and a full test suite.

## Stack
- **FastAPI** for routing + automatic OpenAPI docs
- **SQLAlchemy 2.0** (typed `Mapped[...]` models) over SQLite (swap `DATABASE_URL` for Postgres)
- **Pydantic v2** for validation and serialization
- **pytest** with an isolated in-memory DB

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open **http://localhost:8000/docs** for interactive Swagger UI.

## Try it

```bash
# create
curl -X POST localhost:8000/tasks -H 'content-type: application/json' \
     -d '{"title":"Buy milk","description":"2 litres"}'

# list only done tasks
curl 'localhost:8000/tasks?status=done'

# update status
curl -X PATCH localhost:8000/tasks/1 -H 'content-type: application/json' \
     -d '{"status":"in_progress"}'

# delete
curl -X DELETE localhost:8000/tasks/1 -i
```

## Test

```bash
pytest -q
```

## Layout
```
app/
  main.py       # endpoints (thin handlers)
  crud.py       # data-access functions
  models.py     # SQLAlchemy ORM models
  schemas.py    # Pydantic request/response models
  database.py   # engine + session dependency
tests/
  test_tasks.py # end-to-end API tests
```

---

Portfolio reference implementation by [Zaid Mubbashar](https://github.com/ranazaid) · [zaid-mubbashar.vercel.app](https://zaid-mubbashar.vercel.app)
