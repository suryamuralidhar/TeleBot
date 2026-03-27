from config import DB_CHANNEL

async def load_db(client):
    db = set()

    messages = await client.get_messages(DB_CHANNEL, limit=5000)

    for msg in messages:
        if msg.text:
            db.add(msg.text.strip())

    print(f"📂 DB Loaded: {len(db)} entries")
    return db


async def save_db(client, key):
    await client.send_message(DB_CHANNEL, key)
