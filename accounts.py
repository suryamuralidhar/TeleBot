from telethon import TelegramClient
from telethon.sessions import StringSession

clients = []
current_index = 0

async def init_clients(accounts):
    global clients
    for acc in accounts:
        client = TelegramClient(
            StringSession(acc["session"]),
            acc["api_id"],
            acc["api_hash"]
        )
        await client.connect()
        clients.append(client)

def get_client():
    global current_index
    client = clients[current_index]
    current_index = (current_index + 1) % len(clients)
    return client