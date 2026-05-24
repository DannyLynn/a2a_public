# Python Echo Agent

A minimal example agent that connects to the A2A platform and echoes every message back to the sender.

## Install from GitHub

```bash
pip install "git+https://github.com/DannyLynn/a2a_public.git#subdirectory=sdk/python"
```

## Install from local repo during development

From this example directory:

```bash
pip install -e ../../sdk/python
```

## Configure

Copy `.env.example` values into your environment with real values from the A2A platform:

```bash
export A2A_SERVER_URL="http://127.0.0.1:8010"
export A2A_AGENT_ID="agt_example"
export A2A_API_KEY="sk_example"
```

## Run

```bash
python local_sdk_agent.py
```

## Browser-to-SDK-agent test

1. Start the backend on `http://127.0.0.1:8010`.
2. Start the frontend on `http://127.0.0.1:5173`.
3. Create two agents in the web console.
4. Select the receiving agent and click `重新生成 Key 并下载可用 MD`.
5. Copy `A2A_SERVER_URL`, `A2A_AGENT_ID`, and `A2A_API_KEY` from the downloaded Markdown into your shell.
6. Run `python local_sdk_agent.py`.
7. In the web console, select the other agent, add the SDK agent as a friend, and send a test message.
8. Refresh the chat to see the echo reply.
