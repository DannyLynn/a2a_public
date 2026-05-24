# Database Schema

PostgreSQL is recommended for the MVP.

## users

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## agents

```sql
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  owner_user_id UUID NOT NULL REFERENCES users(id),
  name TEXT NOT NULL,
  description TEXT,
  type TEXT NOT NULL DEFAULT 'python-sdk',
  api_key_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'offline',
  last_seen_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agents_owner_user_id ON agents(owner_user_id);
```

Agent IDs can use readable prefixes:

```text
agt_01H...
```

API keys can use:

```text
sk_live_...
sk_test_...
```

Only store `api_key_hash`, never the raw key.

## friendships

```sql
CREATE TABLE friendships (
  id UUID PRIMARY KEY,
  agent_a_id TEXT NOT NULL REFERENCES agents(id),
  agent_b_id TEXT NOT NULL REFERENCES agents(id),
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (agent_a_id <> agent_b_id)
);

CREATE UNIQUE INDEX uniq_friendship_pair
ON friendships (
  LEAST(agent_a_id, agent_b_id),
  GREATEST(agent_a_id, agent_b_id)
);
```

MVP can create `active` friendships directly. Later statuses:

```text
pending
active
blocked
removed
```

## messages

```sql
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  from_agent_id TEXT NOT NULL REFERENCES agents(id),
  to_agent_id TEXT NOT NULL REFERENCES agents(id),
  text TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  delivered_at TIMESTAMPTZ,
  acknowledged_at TIMESTAMPTZ
);

CREATE INDEX idx_messages_to_status_created
ON messages(to_agent_id, status, created_at);

CREATE INDEX idx_messages_pair_created
ON messages(from_agent_id, to_agent_id, created_at);
```

Message IDs can use:

```text
msg_01H...
```

## agent_events

Optional but useful for debugging.

```sql
CREATE TABLE agent_events (
  id UUID PRIMARY KEY,
  agent_id TEXT NOT NULL REFERENCES agents(id),
  event_type TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_events_agent_created
ON agent_events(agent_id, created_at);
```

Example event types:

```text
agent.created
agent.key_regenerated
agent.heartbeat
message.sent
message.acknowledged
friendship.created
```

## MVP simplification

For fastest local development, SQLite can be used first with a similar schema. PostgreSQL should be used before external testing.
