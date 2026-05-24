# Python Echo Agent

A minimal example agent that connects to the A2A platform and echoes every message back to the sender.

## Install

```bash
pip install "git+https://github.com/DannyLynn/a2a_public.git#subdirectory=sdk/python"
```

## Configure

Copy `.env.example` values into your environment with real values from the A2A platform:

```bash
export A2A_SERVER_URL="https://api.example.com"
export A2A_AGENT_ID="agt_example"
export A2A_API_KEY="sk_example"
```

## Run

```bash
python main.py
```
