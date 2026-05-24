from a2a import AgentClient


client = AgentClient.from_env()


@client.on_message
def handle_message(message):
    return f"Echo from {client.agent_id}: {message.text}"


if __name__ == "__main__":
    client.run()
