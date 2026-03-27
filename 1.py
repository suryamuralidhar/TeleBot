# ================================
# 🔧 CONFIG (FROM ENV)
# ================================

import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION_STRING")

SOURCE_GROUP_ID = -1001811887579 

ROUTES = {
-1003827068085: ["Sofa"],
-1003753218709: ["Pouf"],
-1003869331564: ["Lamp","Light","lighting","lights"],
-1003691605172: ["Chandelier" , "Pendant_light","Pendant_lighting"],
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
-1003606126385: ["Car","coupe","sedan","pickup","suv","Hatchback"], 
-1003779084703: ["Marble"], 
-1003750864556: ["Kitchen"], 
-1003727774043: ["Bathroom","Restroom","Toilet"],
-1003740796851: ["washbasin","Washbasin"], 
-1003773698730: ["Sink","Kitchensink"],
-1003566977180: ["Shower"],
-1003707812721: ["Faucet","tap","mixer","bidet","bidette"],
-1003780728078: ["Toilet" , "WC"],
-1003886868767: [["Track" , "Light"], ["Track", "Lighting"]],
}

TIME_WINDOW = 120
SEARCH_RANGE = 15
SCAN_LIMIT = None

DELAY_MIN = 1.5
DELAY_MAX = 2.5

DB_FILE = "files_db.json"


# ================================
# 🚀 IMPORTS
# ================================

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import asyncio
import re
import json
import random


# ================================
# 🔥 CLIENT (RAILWAY SAFE)
# ================================

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)


# ================================
# 🔥 LOAD DB
# ================================

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            data = f.read().strip()
            saved_files = set(json.loads(data)) if data else set()
    except:
        saved_files = set()
else:
    saved_files = set()

total_sent = len(saved_files)
print(f"📊 Already Sent: {total_sent}")


def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(list(saved_files), f)


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


async def safe_forward(dest, message):
    while True:
        try:
            await client.get_entity(dest)
            await client.forward_messages(dest, message)
            return
        except FloodWaitError as e:
            print(f"⏳ FloodWait: sleeping {e.seconds}s")
            await asyncio.sleep(e.seconds)


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
# 🔍 PROCESS MESSAGE
# ================================

async def process_message(msg):
    global total_sent

    if not msg or not msg.photo:
        return

    try:
        hashtags = extract_hashtags(msg)

        print(f"\n🔎 Msg ID: {msg.id}")
        print(f"   ➤ Hashtags: {hashtags}")

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
                    print("⚠️ No file found")
                    return

                filename = related_file.file.name.lower()

                if filename in saved_files:
                    print(f"⏭️ Duplicate: {filename}")
                    return

                print(f"📤 Sending → {filename}")

                await safe_forward(dest, msg)
                print("   🖼️ Image sent")

                await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                await safe_forward(dest, related_file)
                print("   📦 File sent")

                await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                saved_files.add(filename)
                save_db()

                total_sent = len(saved_files)
                print(f"✅ DONE → Total Sent: {total_sent}")

                break

    except Exception as e:
        print("❌ Error:", e)


# ================================
# 🔁 OLD + LIVE
# ================================

async def process_old():
    print("⏳ Scanning...\n")

    async for msg in client.iter_messages(SOURCE_GROUP_ID, limit=SCAN_LIMIT):
        await process_message(msg)

    print("✅ Done old")


@client.on(events.NewMessage(chats=SOURCE_GROUP_ID))
async def handler(event):
    await process_message(event.message)


# ================================
# ▶️ MAIN
# ================================

async def main():
    await process_old()
    print("\n🚀 Live started")
    await client.run_until_disconnected()


async def run():
    async with client:
        await main()


asyncio.run(run())
