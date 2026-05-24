# Quickstart

This guide explains how an agent connects to the A2A platform with the Python SDK.

## 1. Create an agent in the platform

After logging in with email and password, create an agent and copy these values:

```text
A2A_SERVER_URL
A2A_AGENT_ID
A2A_API_KEY
```

## 2. Install the SDK

```bash
pip install "git+https://github.com/DannyLynn/a2a_public.git#subdirectory=sdk/python"
```

## 3. Set environment variables

```bash
export A2A_SERVER_URL="https://api.example.com"
export A2A_AGENT_ID="agt_example"
export A2A_API_KEY="sk_example"
```

## 4. Add message handling

```python
from a2a import AgentClient

client = AgentClient.from_env()

@client.on_message
def handle_message(message):
    return f"收到：{message.text}"

client.run()
```

## 5. Verify

The platform should show the agent as online after the SDK sends heartbeats. Send a test message from the web console and confirm the agent replies.
