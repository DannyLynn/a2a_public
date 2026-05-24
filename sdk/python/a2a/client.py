import os
import time
from collections.abc import Callable
from typing import Any

import requests

from .types import Message


class AgentClient:
    def __init__(
        self,
        agent_id: str,
        api_key: str,
        server_url: str,
        poll_interval: float = 3.0,
        timeout: float = 30.0,
    ) -> None:
        self.agent_id = agent_id
        self.api_key = api_key
        self.server_url = server_url.rstrip("/")
        self.poll_interval = poll_interval
        self.timeout = timeout
        self._handler: Callable[[Message], str | None] | None = None
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "a2a-python-sdk/0.1.0",
            }
        )

    @classmethod
    def from_env(cls) -> "AgentClient":
        return cls(
            server_url=os.environ["A2A_SERVER_URL"],
            agent_id=os.environ["A2A_AGENT_ID"],
            api_key=os.environ["A2A_API_KEY"],
            poll_interval=float(os.getenv("A2A_POLL_INTERVAL", "3")),
        )

    def on_message(self, handler: Callable[[Message], str | None]) -> Callable[[Message], str | None]:
        self._handler = handler
        return handler

    def heartbeat(self) -> None:
        self._post("/sdk/heartbeat", {"agent_id": self.agent_id})

    def get_pending_messages(self) -> list[Message]:
        response = self._session.get(
            f"{self.server_url}/sdk/messages/pending",
            params={"agent_id": self.agent_id},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return [Message.from_dict(item) for item in data.get("messages", data)]

    def send_message(self, to_agent_id: str, text: str) -> dict[str, Any]:
        return self._post(
            "/sdk/messages/send",
            {
                "from_agent_id": self.agent_id,
                "to_agent_id": to_agent_id,
                "text": text,
            },
        )

    def ack_message(self, message_id: str) -> None:
        self._post(f"/sdk/messages/{message_id}/ack", {"agent_id": self.agent_id})

    def run(self) -> None:
        if self._handler is None:
            raise RuntimeError("Register a message handler with @client.on_message before calling run().")

        while True:
            try:
                self.heartbeat()
                for message in self.get_pending_messages():
                    reply = self._handler(message)
                    if reply:
                        self.send_message(message.from_agent_id, reply)
                    self.ack_message(message.message_id)
            except Exception as exc:
                print(f"[a2a] {type(exc).__name__}: {exc}")
            time.sleep(self.poll_interval)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._session.post(f"{self.server_url}{path}", json=payload, timeout=self.timeout)
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()
