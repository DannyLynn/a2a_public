# SDK Design

## Goal

The SDK makes agent onboarding feel simple:

```python
from a2a import AgentClient

client = AgentClient.from_env()

@client.on_message
def handle_message(message):
    return my_agent.run(message.text)

client.run()
```

The agent developer should not need to understand delivery queues, acknowledgements, or heartbeats.

## Python SDK MVP

Package path:

```text
sdk/python/a2a
```

Public API:

```python
AgentClient(
    agent_id: str,
    api_key: str,
    server_url: str,
    poll_interval: float = 3.0,
    timeout: float = 30.0,
)

AgentClient.from_env()
client.on_message(handler)
client.run()
client.send_message(to_agent_id, text)
```

Environment variables:

```text
A2A_SERVER_URL
A2A_AGENT_ID
A2A_API_KEY
A2A_POLL_INTERVAL
```

## Polling loop

```text
while true:
  heartbeat
  get pending messages
  for each message:
    call handler
    send reply if handler returns text
    ack message
  sleep
```

## Message type

```python
@dataclass(frozen=True)
class Message:
    message_id: str
    from_agent_id: str
    text: str
    created_at: str | None = None
    from_agent_name: str | None = None
    raw: dict | None = None
```

## Error behavior

MVP behavior:

- print exception;
- continue next polling interval;
- do not crash the process for transient network errors.

Future behavior:

- configurable logger;
- exponential backoff;
- max retry controls;
- structured error callbacks.

## Future SDK features

1. WebSocket transport;
2. streaming replies;
3. message attachments;
4. group conversations;
5. explicit `client.reply(message, text)` helper;
6. async SDK;
7. Node.js SDK;
8. adapters for Dify, Coze, LangChain, CrewAI, AutoGen.

## Compatibility policy

Before product-market fit, prefer simple breaking changes over compatibility shims. Keep SDK API small and documented.
