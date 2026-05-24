import json
import time
import urllib.request

from a2a import AgentClient

BASE = "http://127.0.0.1:8010"


def request(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=10) as res:
        raw = res.read().decode()
        return json.loads(raw) if raw else {}


def main():
    email = f"e2e-{int(time.time())}@example.com"
    user = request("POST", "/auth/register", {"email": email, "password": "password123", "name": "E2E User"})
    user_token = user["access_token"]

    web_agent = request("POST", "/agents", {"name": "Web Agent", "description": "Sends from web"}, user_token)
    sdk_agent = request("POST", "/agents", {"name": "SDK Echo Agent", "description": "Replies from SDK"}, user_token)

    request("POST", "/friends/add", {"agent_id": web_agent["agent_id"], "friend_agent_id": sdk_agent["agent_id"]}, user_token)

    key_result = request("POST", f"/agents/{sdk_agent['agent_id']}/regenerate-key", token=user_token)
    assert key_result["api_key"] in key_result["connection_md"]
    assert BASE in key_result["connection_md"]

    request(
        "POST",
        "/messages/send",
        {"from_agent_id": web_agent["agent_id"], "to_agent_id": sdk_agent["agent_id"], "text": "ping from web"},
        user_token,
    )

    client = AgentClient(agent_id=sdk_agent["agent_id"], api_key=key_result["api_key"], server_url=BASE)
    client.heartbeat()
    pending = client.get_pending_messages()
    assert len(pending) == 1, pending

    reply = f"sdk auto reply: {pending[0].text}"
    client.send_message(pending[0].from_agent_id, reply)
    client.ack_message(pending[0].message_id)

    conversation = request(
        "GET",
        f"/agents/{web_agent['agent_id']}/conversations/{sdk_agent['agent_id']}/messages",
        token=user_token,
    )
    texts = [message["text"] for message in conversation["messages"]]
    assert "ping from web" in texts, texts
    assert reply in texts, texts

    print(json.dumps({"ok": True, "web_agent": web_agent["agent_id"], "sdk_agent": sdk_agent["agent_id"], "messages": texts}, indent=2))


if __name__ == "__main__":
    main()
