from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Message:
    message_id: str
    from_agent_id: str
    text: str
    created_at: str | None = None
    from_agent_name: str | None = None
    raw: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        return cls(
            message_id=data["message_id"],
            from_agent_id=data["from_agent_id"],
            from_agent_name=data.get("from_agent_name"),
            text=data["text"],
            created_at=data.get("created_at"),
            raw=data,
        )
