# ================================
# 🔧 CONFIG
# ================================

import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION_STRING")

SOURCE_GROUP_ID = -1001811887579
DB_CHANNEL_ID = -1003799490964   # 🔥 PUT YOUR PRIVATE DB CHANNEL ID

SCAN_LIMIT = None   # ✅ full scan for first run

TIME_WINDOW = 120
SEARCH_RANGE = 15

DELAY_MIN = 1.5
DELAY_MAX = 2.5

IS_SCANNING = True


ROUTES = {
-1003827068085: ["Sofa"],
-1003753218709: ["Pouf","poof"],
-1003772273357: ["Lamp","Light","lighting","lights"],
-1003691605172: ["Chandelier" , "Pendent" ,["Pendent","light"]],
-1003557082671: ["Table"],
-1003752015548: ["Vase","flower"],
-1003754983761: ["Decor"],
-1003809497514: ["Armchair" , "Chair"],
-1003858996511: ["Carpet"], 
-1003835504670: ["Rug"], 
-1003794820459: ["Bed","matress"],
-1003815972764: ["Shrubs" , "Bush" , "Bushes","plants","plant"], 
-1003861364666: ["Grass"], 
-1003891088964: ["Trees" , "Tree" , "Palm"], 
-1003718603443: ["Water", "Liquid"], 
-1003757370342: ["Fabric"], 
-1003319756110: ["Metal"], 
-1003751276058: ["Windows" , "Window","Frame"], 
-1003537174392: ["Doors" , "Door"],   
-1003514048910: ["Curtains" , "Curtain"],
-1003606126385: ["Car" ,["car","vintage"],"coupe","sedan","pickup","suv","Hatchback"], 
-1003779084703: ["Marble"], 
-1003750864556: ["Kitchen"], 
-1003727774043: ["Bathroom","Restroom","Toilet"],
-1003740796851: ["washbasin","Washbasin"], 
-1003773698730: ["Sink","Kitchensink"],
-1003566977180: ["Shower"],
-1003707812721: ["Faucet","tap","mixer","bidet","bidette"],
-1003780728078: ["Toilet" , "WC"],
-1003886868767: [["Track" , "Light"],["Track" , "Lighting"]],



    
   
}

# ================================
# 🚀 IMPORTS
# ================================

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import asyncio
import re
import random


# ================================
# 🔥 CLIENT
# ================================

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)


# ================================
# 🔥 TELEGRAM DB
# ================================

saved_files = set()

async def load_db():
    global saved_files
    print("📥 Loading DB...")

    async for msg in client.iter_messages(DB_CHANNEL_ID):
        if msg.text:
            saved_files.add(msg.text.strip())

    print(f"📊 Loaded {len(saved_files)} items")


async def save_to_db(filename):
    saved_files.add(filename)
    await client.send_message(DB_CHANNEL_ID, filename)


# ================================
# 🔍 HELPERS
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


def extract_filename_hint(msg):
    text = (msg.message or "").lower()
    match = re.search(r"[a-z0-9]{6,}", text)
    return match.group(0) if match else None


# ================================
# 🔥 SAFE FORWARD
# ================================

async def safe_forward(dest, message):
    while True:
        try:
            if not client.is_connected():
                print("🔌 Reconnecting...")
                await client.connect()

            await client.get_entity(dest)
            await client.forward_messages(dest, message)
            return

        except FloodWaitError as e:
            print(f"⏳ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print(f"⚠️ Retry: {e}")
            await asyncio.sleep(5)


# ================================
# 🔍 FIND FILE
# ================================

async def find_related_file(msg):
    nearby = await client.get_messages(
        SOURCE_GROUP_ID,
        ids=range(msg.id - SEARCH_RANGE, msg.id + SEARCH_RANGE)
    )

    hint = extract_filename_hint(msg)

    best_match = None
    best_score = 999999

    for m in nearby:
        if not m:
            continue

        if m.file and m.file.name:
            name = m.file.name.lower()

            if ".zip" in name or ".rar" in name:
                time_diff = abs((m.date - msg.date).total_seconds())
                score = time_diff

                if hint and hint in name:
                    score -= 100

                if time_diff <= TIME_WINDOW and score < best_score:
                    best_score = score
                    best_match = m

    return best_match


# ================================
# 🔍 PROCESS
# ================================

async def process_message(msg):
    if not msg or not msg.photo:
        return

    try:
        hashtags = extract_hashtags(msg)

        if not hashtags:
            return

        print(f"\n🔎 {msg.id} → {hashtags}")

        for dest, tags in ROUTES.items():

            matched = False

            for group in tags:
                if isinstance(group, list):
                    if all(g.lower() in hashtags for g in group):
                        matched = True
                        break
                else:
                    if group.lower() in hashtags:
                        matched = True
                        break

            if matched:

                related_file = await find_related_file(msg)

                if not related_file:
                    return

                filename = related_file.file.name.lower()

                if filename in saved_files:
                    print(f"⏭️ Duplicate: {filename}")
                    return

                print(f"📤 Sending → {filename}")

                await safe_forward(dest, msg)
                print("🖼️ Image sent")

                if not IS_SCANNING:
                    await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                await safe_forward(dest, related_file)
                print("📦 File sent")

                if not IS_SCANNING:
                    await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                await save_to_db(filename)

                print(f"✅ Saved → Total: {len(saved_files)}")

                break

    except Exception as e:
        print("❌ Error:", e)


# ================================
# 🔁 SCAN
# ================================

async def process_old():
    global IS_SCANNING

    print("⚡ Full scanning...\n")
    IS_SCANNING = True

    async for msg in client.iter_messages(
        SOURCE_GROUP_ID,
        limit=SCAN_LIMIT,
        wait_time=0
    ):
        await process_message(msg)

    IS_SCANNING = False
    print("✅ Scan done")


# ================================
# 🔴 LIVE
# ================================

@client.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    await process_message(event.message)


# ================================
# 🔌 KEEP ALIVE
# ================================

async def ensure_connection():
    while True:
        if not client.is_connected():
            print("🔌 Lost → reconnecting...")
            try:
                await client.connect()
            except Exception as e:
                print("Reconnect failed:", e)

        await asyncio.sleep(10)


# ================================
# ▶️ MAIN
# ================================

async def main():
    await client.connect()

    await load_db()

    asyncio.create_task(ensure_connection())

    await process_old()

    print("\n🚀 Live started")
    await client.run_until_disconnected()


async def run():
    async with client:
        await main()


asyncio.run(run())
