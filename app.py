# ================================
# 🚀 MAIN WORKER
# ================================

import asyncio
import re
import random

from accounts import init_clients, get_client
from config import *
from db import is_duplicate, save
from router import get_destinations

# ================================
# 🔌 CONNECTION GUARD
# ================================

async def ensure_connection():
    while True:
        client = get_client()
        if not client.is_connected():
            print("🔌 Reconnecting...")
            try:
                await client.connect()
            except Exception as e:
                print("Reconnect failed:", e)
        await asyncio.sleep(10)

# ================================
# 🧠 HASHTAG EXTRACT
# ================================

def extract_hashtags(msg):
    text = (msg.message or "").lower()
    tags = re.findall(r"#\w+", text)

    clean = [t.replace("#", "") for t in tags]

    expanded = set(clean)
    for tag in clean:
        if "_" in tag:
            expanded.update(tag.split("_"))

    return list(expanded)

# ================================
# 🔐 SAFE GET MESSAGES
# ================================

async def safe_get_message(chat_id, msg_id):
    while True:
        try:
            client = get_client()
            if not client.is_connected():
                await client.connect()

            return await client.get_messages(chat_id, ids=msg_id)

        except Exception as e:
            print("⚠️ get_message retry:", e)
            await asyncio.sleep(2)

# ================================
# 📦 FIND RELATED FILE (FIXED)
# ================================

async def find_related_file(msg):
    """
    Strong pairing logic:
    1. Look forward (most reliable)
    2. Then backward
    """

    try:
        chat_id = msg.chat_id

        # 🔥 1. search FORWARD (priority)
        for i in range(msg.id + 1, msg.id + 25):
            m = await safe_get_message(chat_id, i)

            if not m:
                continue

            if m.file and m.file.name:
                name = m.file.name.lower()

                if name.endswith(".zip") or name.endswith(".rar"):
                    return m

        # 🔥 2. search BACKWARD (fallback)
        for i in range(msg.id - 1, msg.id - 25, -1):
            m = await safe_get_message(chat_id, i)

            if not m:
                continue

            if m.file and m.file.name:
                name = m.file.name.lower()

                if name.endswith(".zip") or name.endswith(".rar"):
                    return m

        print(f"❌ No file found for msg {msg.id}")
        return None

    except Exception as e:
        print("❌ File search error:", e)
        return None

# ================================
# ⏱ SAFE DELAY
# ================================

async def safe_delay():
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"😴 Delay: {delay:.2f}s")
    await asyncio.sleep(delay)

# ================================
# 📤 SAFE FORWARD
# ================================

async def safe_forward(dest, message):
    while True:
        try:
            client = get_client()

            if not client.is_connected():
                await client.connect()

            await safe_delay()

            entity = await client.get_entity(dest)
            await client.forward_messages(entity, message)

            return

        except Exception as e:
            print("⚠️ Forward retry:", e)
            await asyncio.sleep(5)

# ================================
# 🔍 PROCESS MESSAGE
# ================================

async def process_message(msg):

    if not msg or not msg.photo:
        return

    hashtags = extract_hashtags(msg)

    if not hashtags:
        return

    print(f"\n🔎 {msg.id} → {hashtags}")

    # 🔥 find file ONCE (optimized)
    related_file = await find_related_file(msg)

    if not related_file:
        return

    filename = (
        related_file.file.name.lower()
        if related_file.file and related_file.file.name
        else "unknown"
    )

    # 🔥 get destinations
    dests = get_destinations(hashtags)

    if not dests:
        return

    for dest in dests:

        # 🚫 duplicate check (per channel)
        if is_duplicate(dest, filename):
            print(f"⏭️ Duplicate in {dest}: {filename}")
            continue

        print(f"📤 Sending → {filename} → {dest}")

        # 🖼️ send image
        await safe_forward(dest, msg)

        # 📦 send model file
        await safe_forward(dest, related_file)

        # 💾 save DB
        save(dest, filename)

# ================================
# 🔁 SCAN OLD MESSAGES
# ================================

async def process_old():
    print("⚡ Scanning old messages...")

    client = get_client()

    async for msg in client.iter_messages(SOURCE_GROUP_ID):
        await process_message(msg)

    print("✅ Scan complete")

# ================================
# 🔴 LIVE LISTENER
# ================================

async def live_listener():
    client = get_client()

    async for msg in client.iter_messages(SOURCE_GROUP_ID, reverse=True):
        await process_message(msg)

# ================================
# ▶️ MAIN
# ================================

async def main():
    print("🚀 Starting system...")

    await init_clients(API_ACCOUNTS)

    asyncio.create_task(ensure_connection())

    await process_old()

    print("🚀 Live mode started...")

    await live_listener()

# ================================
# 🚀 RUN
# ================================

if __name__ == "__main__":
    asyncio.run(main())
