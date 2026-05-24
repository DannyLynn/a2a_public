from a2a import AgentClient


client = AgentClient.from_env()


@client.on_message
def handle_message(message):
    print(f"received from {message.from_agent_id}: {message.text}")
    return f"Echo reply from {client.agent_id}: {message.text}"


if __name__ == "__main__":
    print(f"starting echo agent {client.agent_id}")
    client.run()
