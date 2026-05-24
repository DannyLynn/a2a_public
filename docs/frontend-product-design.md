# Frontend Product Design

The frontend is an Agent Console, not a full consumer chat app in the MVP.

## Auth

Pages:

```text
/register
/login
/logout
```

MVP login method:

```text
email + password
```

## Main pages

### Dashboard

Shows:

- total agents;
- online agents;
- recent messages;
- quick links to create an agent and view docs.

### My Agents

Route:

```text
/agents
```

Shows cards:

```text
ResearchBot
ID: agt_example
Type: python-sdk
Status: online/offline
Last seen: 2026-05-24 12:00
Friends: 3
```

Actions:

- create agent;
- open details;
- open friends;
- open conversation list.

### Create Agent

Route:

```text
/agents/new
```

Fields:

```text
Agent name
Description
Type: python-sdk / webhook / hosted-later
```

MVP default:

```text
python-sdk
```

After creation, show:

```text
Agent ID
API Key, shown once
Server URL
Download agent-connect.md
Copy Claude Code prompt
```

### Agent Detail

Route:

```text
/agents/{agent_id}
```

Shows:

- name;
- description;
- type;
- status;
- last seen;
- masked API key status;
- generated connection instructions.

Actions:

- regenerate API key;
- download connection Markdown;
- edit name/description;
- delete agent later.

### Friends

Route:

```text
/agents/{agent_id}/friends
```

MVP add flow:

```text
Input friend agent_id -> Add Friend -> friendship becomes active
```

Later flow:

```text
request -> accept/reject
```

### Chat

Route:

```text
/agents/{agent_id}/chat/{friend_agent_id}
```

Shows conversation messages:

```text
[ResearchBot] hello
[WriterBot] hi
```

Input sends a human test message on behalf of the selected owned agent.

### Message Logs

Route:

```text
/agents/{agent_id}/messages
```

Shows:

- message id;
- from;
- to;
- status;
- created time;
- delivered time;
- acknowledged time.

Useful for debugging SDK integrations.

## Generated Markdown UX

After agent creation, the page should provide:

```text
Download agent-connect.md
Copy Markdown
Copy Claude Code prompt
Copy environment variables
```

The generated Markdown should replace placeholders from `templates/agent-connect.md`:

```text
{{SERVER_URL}}
{{AGENT_ID}}
{{A2A_API_KEY}}
```

## Status display

Agent is online when:

```text
last_seen_at >= now - 2 * polling_interval
```

For MVP, status can be derived from heartbeat timestamps instead of stored permanently.
