from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Message:
    message_id: str
    from_agent_id: str
    text: str
    created_at: Optional[str] = None
    from_agent_name: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            message_id=data["message_id"],
            from_agent_id=data["from_agent_id"],
            from_agent_name=data.get("from_agent_name"),
            text=data["text"],
            created_at=data.get("created_at"),
            raw=data,
        )
