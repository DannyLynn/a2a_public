# Local Scripts

Helper scripts for running and validating the local MVP.

## Start backend

```bash
./scripts/start_backend.sh
```

Backend URL:

```text
http://127.0.0.1:8010
```

## Start frontend

```bash
./scripts/start_frontend.sh
```

Frontend URL:

```text
http://127.0.0.1:5173
```

## Run echo SDK agent

Set values from the downloaded connection Markdown first:

```bash
export A2A_SERVER_URL="http://127.0.0.1:8010"
export A2A_AGENT_ID="agt_example"
export A2A_API_KEY="sk_example"
./scripts/run_echo_agent.sh
```

## Run automated SDK loop test

Start the backend first, then run:

```bash
source backend/.venv/bin/activate
pip install -e sdk/python
python scripts/e2e_sdk_loop.py
```

Expected output:

```json
{
  "ok": true,
  "messages": [
    "ping from web",
    "sdk auto reply: ping from web"
  ]
}
```
