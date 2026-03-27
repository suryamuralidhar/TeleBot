
import asyncio
from telethon import events

from accounts import get_client
from config import SOURCE_CHANNEL
from db import load_db, save_db
from router import get_destinations
from ai import extract_tags
from dashboard import log, error, success


client = get_client()


async def process_message(event, db):
    msg = event.message

    if not msg.text:
        return

    text = msg.text.strip()

    tags = extract_tags(text)
    log(f"Tags: {tags}")

    destinations = get_destinations(tags)

    for dest in destinations:
        key = f"{msg.id}|{dest}"

        if key in db:
            log(f"Duplicate skipped → {dest}")
            continue

        try:
            await client.forward_messages(dest, msg)

            await save_db(client, key)
            db.add(key)

            success(f"Forwarded → {dest}")

        except Exception as e:
            error(f"Failed → {dest} | {e}")


async def main():
    await client.start()

    log("🚀 System started")

    db = await load_db(client)

    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handler(event):
        await process_message(event, db)

    log("👀 Listening...")
    await client.run_until_disconnected()


asyncio.run(main())
