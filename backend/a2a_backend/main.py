from pathlib import Path
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from .db import connect, init_db
from .security import hash_secret, new_api_key, new_id, verify_secret

app = FastAPI(title="A2A Network Local MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER_URL = "http://127.0.0.1:8010"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AgentCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    type: str = "python-sdk"


class FriendAddRequest(BaseModel):
    agent_id: str
    friend_agent_id: str


class WebMessageSendRequest(BaseModel):
    from_agent_id: str
    to_agent_id: str
    text: str = Field(min_length=1, max_length=8000)


class SdkMessageSendRequest(BaseModel):
    to_agent_id: Optional[str] = None
    from_agent_id: Optional[str] = None
    text: str = Field(min_length=1, max_length=8000)


class HeartbeatRequest(BaseModel):
    agent_id: Optional[str] = None


class AckRequest(BaseModel):
    agent_id: Optional[str] = None


@app.on_event("startup")
def startup() -> None:
    init_db()


def row_to_dict(row):
    return dict(row) if row else None


def require_user(authorization: Annotated[Optional[str], Header()] = None) -> dict:
    token = bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="missing bearer token")
    with connect() as db:
        row = db.execute("SELECT id, email, name, created_at FROM users WHERE id = ?", (token,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="invalid user token")
    return dict(row)


def require_agent(authorization: Annotated[Optional[str], Header()] = None) -> dict:
    api_key = bearer_token(authorization)
    if not api_key:
        raise HTTPException(status_code=401, detail="missing api key")
    with connect() as db:
        rows = db.execute("SELECT * FROM agents").fetchall()
    for row in rows:
        agent = dict(row)
        if verify_secret(api_key, agent["api_key_hash"]):
            return agent
    raise HTTPException(status_code=401, detail="invalid api key")


def bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip()


def assert_owns_agent(user_id: str, agent_id: str) -> None:
    with connect() as db:
        row = db.execute(
            "SELECT id FROM agents WHERE id = ? AND owner_user_id = ?",
            (agent_id, user_id),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=403, detail="agent is not owned by current user")


def assert_agents_are_friends(agent_a_id: str, agent_b_id: str) -> None:
    a, b = sorted([agent_a_id, agent_b_id])
    with connect() as db:
        row = db.execute(
            "SELECT id FROM friendships WHERE agent_a_id = ? AND agent_b_id = ? AND status = 'active'",
            (a, b),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=403, detail="agents are not friends")


def render_connection_md(agent_id: str, api_key: str) -> str:
    template_path = Path(__file__).resolve().parents[2] / "templates" / "agent-connect.md"
    template = template_path.read_text()
    return template.replace("{{SERVER_URL}}", SERVER_URL).replace("{{AGENT_ID}}", agent_id).replace("{{A2A_API_KEY}}", api_key)


def create_message(from_agent_id: str, to_agent_id: str, text: str) -> dict:
    assert_agents_are_friends(from_agent_id, to_agent_id)
    message_id = new_id("msg")
    with connect() as db:
        receiver = db.execute("SELECT id FROM agents WHERE id = ?", (to_agent_id,)).fetchone()
        if not receiver:
            raise HTTPException(status_code=404, detail="receiver agent not found")
        db.execute(
            "INSERT INTO messages (id, from_agent_id, to_agent_id, text) VALUES (?, ?, ?, ?)",
            (message_id, from_agent_id, to_agent_id, text),
        )
        row = db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    return dict(row)


@app.post("/auth/register")
def register(request: RegisterRequest) -> dict:
    user_id = new_id("usr")
    with connect() as db:
        try:
            db.execute(
                "INSERT INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)",
                (user_id, request.email.lower(), hash_secret(request.password), request.name),
            )
        except Exception:
            raise HTTPException(status_code=409, detail="email already registered")
    return {"user_id": user_id, "email": request.email.lower(), "name": request.name, "access_token": user_id}


@app.post("/auth/login")
def login(request: LoginRequest) -> dict:
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (request.email.lower(),)).fetchone()
    if not row or not verify_secret(request.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid email or password")
    return {"user_id": row["id"], "email": row["email"], "name": row["name"], "access_token": row["id"]}


@app.get("/auth/me")
def me(user: Annotated[dict, Depends(require_user)]) -> dict:
    return user


@app.post("/agents")
def create_agent(request: AgentCreateRequest, user: Annotated[dict, Depends(require_user)]) -> dict:
    agent_id = new_id("agt")
    api_key = new_api_key()
    with connect() as db:
        db.execute(
            """
            INSERT INTO agents (id, owner_user_id, name, description, type, api_key_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (agent_id, user["id"], request.name, request.description, request.type, hash_secret(api_key)),
        )
    return {
        "agent_id": agent_id,
        "api_key": api_key,
        "server_url": SERVER_URL,
        "name": request.name,
        "description": request.description,
        "type": request.type,
    }


@app.get("/agents")
def list_agents(user: Annotated[dict, Depends(require_user)]) -> dict:
    with connect() as db:
        rows = db.execute(
            "SELECT id, name, description, type, status, last_seen_at, created_at FROM agents WHERE owner_user_id = ? ORDER BY created_at DESC",
            (user["id"],),
        ).fetchall()
    return {"agents": [dict(row) for row in rows]}


@app.post("/friends/add")
def add_friend(request: FriendAddRequest, user: Annotated[dict, Depends(require_user)]) -> dict:
    assert_owns_agent(user["id"], request.agent_id)
    a, b = sorted([request.agent_id, request.friend_agent_id])
    friendship_id = new_id("frd")
    with connect() as db:
        if not db.execute("SELECT id FROM agents WHERE id = ?", (request.friend_agent_id,)).fetchone():
            raise HTTPException(status_code=404, detail="friend agent not found")
        db.execute(
            "INSERT OR IGNORE INTO friendships (id, agent_a_id, agent_b_id) VALUES (?, ?, ?)",
            (friendship_id, a, b),
        )
    return {"agent_id": request.agent_id, "friend_agent_id": request.friend_agent_id, "status": "active"}


@app.get("/agents/{agent_id}/friends")
def list_friends(agent_id: str, user: Annotated[dict, Depends(require_user)]) -> dict:
    assert_owns_agent(user["id"], agent_id)
    with connect() as db:
        rows = db.execute(
            """
            SELECT agents.id, agents.name, agents.description, agents.type, agents.status, agents.last_seen_at
            FROM friendships
            JOIN agents ON agents.id = CASE
              WHEN friendships.agent_a_id = ? THEN friendships.agent_b_id
              ELSE friendships.agent_a_id
            END
            WHERE (friendships.agent_a_id = ? OR friendships.agent_b_id = ?) AND friendships.status = 'active'
            ORDER BY agents.name
            """,
            (agent_id, agent_id, agent_id),
        ).fetchall()
    return {"friends": [dict(row) for row in rows]}


@app.post("/messages/send")
def send_web_message(request: WebMessageSendRequest, user: Annotated[dict, Depends(require_user)]) -> dict:
    assert_owns_agent(user["id"], request.from_agent_id)
    return create_message(request.from_agent_id, request.to_agent_id, request.text)


@app.get("/agents/{agent_id}/conversations/{friend_agent_id}/messages")
def list_conversation(agent_id: str, friend_agent_id: str, user: Annotated[dict, Depends(require_user)]) -> dict:
    assert_owns_agent(user["id"], agent_id)
    with connect() as db:
        rows = db.execute(
            """
            SELECT * FROM messages
            WHERE (from_agent_id = ? AND to_agent_id = ?) OR (from_agent_id = ? AND to_agent_id = ?)
            ORDER BY created_at ASC
            """,
            (agent_id, friend_agent_id, friend_agent_id, agent_id),
        ).fetchall()
    return {"messages": [dict(row) for row in rows]}


@app.post("/agents/{agent_id}/regenerate-key")
def regenerate_agent_key(agent_id: str, user: Annotated[dict, Depends(require_user)]) -> dict:
    assert_owns_agent(user["id"], agent_id)
    api_key = new_api_key()
    with connect() as db:
        db.execute("UPDATE agents SET api_key_hash = ? WHERE id = ?", (hash_secret(api_key), agent_id))
    return {"agent_id": agent_id, "api_key": api_key, "server_url": SERVER_URL, "connection_md": render_connection_md(agent_id, api_key)}


@app.post("/agents/{agent_id}/connection-md")
def generate_connection_md(agent_id: str, user: Annotated[dict, Depends(require_user)]) -> Response:
    assert_owns_agent(user["id"], agent_id)
    return Response(content=render_connection_md(agent_id, "<regenerate-api-key-to-view>"), media_type="text/markdown")


@app.post("/sdk/heartbeat")
def sdk_heartbeat(request: HeartbeatRequest, agent: Annotated[dict, Depends(require_agent)]) -> dict:
    if request.agent_id and request.agent_id != agent["id"]:
        raise HTTPException(status_code=403, detail="agent_id does not match api key")
    with connect() as db:
        db.execute(
            "UPDATE agents SET status = 'online', last_seen_at = CURRENT_TIMESTAMP WHERE id = ?",
            (agent["id"],),
        )
    return {"ok": True, "agent_id": agent["id"]}


@app.get("/sdk/messages/pending")
def sdk_pending_messages(agent: Annotated[dict, Depends(require_agent)]) -> dict:
    with connect() as db:
        rows = db.execute(
            """
            SELECT id AS message_id, from_agent_id, text, created_at
            FROM messages
            WHERE to_agent_id = ? AND status = 'queued'
            ORDER BY created_at ASC
            LIMIT 20
            """,
            (agent["id"],),
        ).fetchall()
        db.execute(
            "UPDATE messages SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP WHERE to_agent_id = ? AND status = 'queued'",
            (agent["id"],),
        )
    return {"messages": [dict(row) for row in rows]}


@app.post("/sdk/messages/send")
def sdk_send_message(request: SdkMessageSendRequest, agent: Annotated[dict, Depends(require_agent)]) -> dict:
    if request.from_agent_id and request.from_agent_id != agent["id"]:
        raise HTTPException(status_code=403, detail="from_agent_id does not match api key")
    if not request.to_agent_id:
        raise HTTPException(status_code=422, detail="to_agent_id is required")
    return create_message(agent["id"], request.to_agent_id, request.text)


@app.post("/sdk/messages/{message_id}/ack")
def sdk_ack_message(message_id: str, request: AckRequest, agent: Annotated[dict, Depends(require_agent)]) -> dict:
    if request.agent_id and request.agent_id != agent["id"]:
        raise HTTPException(status_code=403, detail="agent_id does not match api key")
    with connect() as db:
        row = db.execute("SELECT id FROM messages WHERE id = ? AND to_agent_id = ?", (message_id, agent["id"])).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="message not found")
        db.execute(
            "UPDATE messages SET status = 'acknowledged', acknowledged_at = CURRENT_TIMESTAMP WHERE id = ?",
            (message_id,),
        )
    return {"ok": True, "message_id": message_id}
