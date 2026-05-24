import os
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "a2a_local.db"


def get_db_path() -> str:
    return os.getenv("A2A_DB_PATH", str(DEFAULT_DB_PATH))


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              name TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agents (
              id TEXT PRIMARY KEY,
              owner_user_id TEXT NOT NULL REFERENCES users(id),
              name TEXT NOT NULL,
              description TEXT,
              type TEXT NOT NULL DEFAULT 'python-sdk',
              api_key_hash TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'offline',
              last_seen_at TEXT,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS friendships (
              id TEXT PRIMARY KEY,
              agent_a_id TEXT NOT NULL REFERENCES agents(id),
              agent_b_id TEXT NOT NULL REFERENCES agents(id),
              status TEXT NOT NULL DEFAULT 'active',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              CHECK (agent_a_id <> agent_b_id),
              UNIQUE (agent_a_id, agent_b_id)
            );

            CREATE TABLE IF NOT EXISTS messages (
              id TEXT PRIMARY KEY,
              from_agent_id TEXT NOT NULL REFERENCES agents(id),
              to_agent_id TEXT NOT NULL REFERENCES agents(id),
              text TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'queued',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              delivered_at TEXT,
              acknowledged_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_agents_owner_user_id ON agents(owner_user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_to_status_created ON messages(to_agent_id, status, created_at);
            CREATE INDEX IF NOT EXISTS idx_messages_pair_created ON messages(from_agent_id, to_agent_id, created_at);
            """
        )
