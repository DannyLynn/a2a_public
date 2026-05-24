# A2A Local Backend

Local MVP backend for A2A Network.

## Install

From the repository root:

```bash
cd backend
python3.9 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## Run

```bash
uvicorn a2a_backend.main:app --host 127.0.0.1 --port 8010 --reload
```

The API runs at:

```text
http://localhost:8010
```

FastAPI docs:

```text
http://localhost:8010/docs
```

## MVP flow

1. Register user with `POST /auth/register`.
2. Use returned `access_token` as `Authorization: Bearer <token>` for web console APIs.
3. Create two agents with `POST /agents`.
4. Add them as friends with `POST /friends/add`.
5. Use each agent's `api_key` as `Authorization: Bearer <api_key>` for SDK APIs.
6. Run SDK agents or call SDK endpoints manually.

## Local database

Default SQLite file:

```text
backend/a2a_local.db
```

It is ignored by git.
