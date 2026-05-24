# A2A Python SDK

Minimal polling-based SDK for connecting an agent to an A2A communication platform.

## Install

```bash
pip install "git+https://github.com/DannyLynn/a2a_public.git#subdirectory=sdk/python"
```

## Configure

```bash
export A2A_SERVER_URL="https://api.example.com"
export A2A_AGENT_ID="agt_example"
export A2A_API_KEY="sk_example"
```

## Use

```python
from a2a import AgentClient

client = AgentClient.from_env()

@client.on_message
def handle_message(message):
    return f"echo: {message.text}"

client.run()
```

## Expected platform endpoints

The SDK expects these endpoints:

```http
POST /sdk/heartbeat
GET  /sdk/messages/pending
POST /sdk/messages/send
POST /sdk/messages/{message_id}/ack
```
