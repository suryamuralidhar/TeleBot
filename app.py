import asyncio
from telethon import events

from accounts import get_client
from config import SOURCE_CHANNEL
from db import load_db, save_db
from router import get_destinations
from ai import extract_tags
from dashboard import log, success, error


client = get_client()


async def process_message(event, db):
    msg = event.message

    if not msg.text:
        return

    text = msg.text.strip()
    tags = extract_tags(text)

    log(f"📦 Message: {text}")
    log(f"🏷 Tags: {tags}")

    destinations = get_destinations(tags)

    if not destinations:
        log("❌ No matching routes")
        return

    for dest in destinations:
        key = f"{msg.id}|{dest}"

        if key in db:
            log(f"⚠️ Duplicate skipped → {dest}")
            continue

        try:
            await client.forward_messages(dest, msg)

            await save_db(client, key)
            db.add(key)

            success(f"🚀 Forwarded → {dest}")

        except Exception as e:
            error(f"❌ Error → {dest} | {e}")


async def main():
    await client.start()

    log("🚀 System started")

    # 🔥 FORCE RESOLVE SOURCE CHANNEL
    source_entity = await client.get_entity(SOURCE_CHANNEL)
    log(f"🎯 Listening to: {source_entity.title} ({source_entity.id})")

    db = await load_db(client)

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            chat = await event.get_chat()

            log(f"📩 Incoming from: {chat.id}")

            # 🔥 STRICT MATCH
            if int(chat.id) != int(SOURCE_CHANNEL):
                return

            await process_message(event, db)

        except Exception as e:
            error(f"Handler error: {e}")

    log("👀 Listening for messages...")
    await client.run_until_disconnected()


asyncio.run(main())
