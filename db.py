from config import DB_CHANNEL

async def load_db(client):
    db = set()

    entity = await client.get_entity(DB_CHANNEL)

    messages = await client.get_messages(entity, limit=None)

    for msg in messages:
        if msg.text:
            db.add(msg.text.strip())

    print(f"📂 DB Loaded: {len(db)} entries")
    return db


async def save_db(client, key):
    entity = await client.get_entity(DB_CHANNEL)
    await client.send_message(entity, key)
