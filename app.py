import asyncio
import re
import random

from accounts import init_clients, get_client
from config import *
from db import is_duplicate, save
from router import get_destinations
from ai import auto_tags

def extract_hashtags(msg):
    text = (msg.message or "").lower()
    tags = re.findall(r"#\w+", text)
    return [t.replace("#", "") for t in tags]

async def process_message(msg):

    hashtags = extract_hashtags(msg)

    # 🔥 AI TAGGING (fallback)
    if not hashtags:
        hashtags = auto_tags(msg.message)

    if not hashtags:
        return

    dests = get_destinations(hashtags)
    if not dests:
        return

    client = get_client()

    for dest in dests:

        filename = "unknown"

        if msg.file and msg.file.name:
            filename = msg.file.name.lower()

        if is_duplicate(dest, filename):
            continue

        try:
            await client.forward_messages(dest, msg)
            save(dest, filename)

            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

        except Exception as e:
            print("Error:", e)

async def main():
    await init_clients(API_ACCOUNTS)

    client = get_client()

    async for msg in client.iter_messages(SOURCE_GROUP_ID):
        await process_message(msg)

asyncio.run(main())