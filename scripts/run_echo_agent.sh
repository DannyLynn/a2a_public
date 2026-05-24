#!/usr/bin/env bash
set -euo pipefail

if [ -z "${A2A_SERVER_URL:-}" ] || [ -z "${A2A_AGENT_ID:-}" ] || [ -z "${A2A_API_KEY:-}" ]; then
  echo "Set A2A_SERVER_URL, A2A_AGENT_ID, and A2A_API_KEY before running this script." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/examples/python-echo-agent"

if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
  python3.9 -m venv "$ROOT_DIR/backend/.venv"
fi

"$ROOT_DIR/backend/.venv/bin/pip" install -e "$ROOT_DIR/sdk/python" >/dev/null
"$ROOT_DIR/backend/.venv/bin/python" local_sdk_agent.py
