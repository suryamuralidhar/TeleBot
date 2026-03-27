# ================================
# 🔧 CONFIG
# ================================

import os
import asyncio
import re
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION_STRING")

SOURCE_GROUP_ID = -1001811887579
DB_CHANNEL_ID = -1003799490964

SCAN_LIMIT = None

TIME_WINDOW = 120
SEARCH_RANGE = 15

# 🔥 SAFE DELAY SETTINGS
MIN_DELAY = 2.5
MAX_DELAY = 4.5

IS_SCANNING = True

# 🔥 GLOBAL RATE CONTROL
LAST_ACTION_TIME = 0

ROUTES = {
-1003827068085: ["Sofa"],
-1003753218709: ["Pouf","poof"],
-1003772273357: ["Lamp","Light","lighting","lights"],
-1003691605172: ["Chandelier" , "Pendent" ,["Pendent","light"]],
-1003557082671: ["Table"],
-1003752015548: ["Vase","flower"],
-1003754983761: ["Decor"],
-1003809497514: ["Armchair" , "Chair"],
-1003862450569: ["Carpet"], 
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
# 🔥 CLIENT
# ================================

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ================================
# 🔥 GLOBAL DELAY
# ================================

async def global_delay():
    global LAST_ACTION_TIME

    now = asyncio.get_event_loop().time()
    diff = now - LAST_ACTION_TIME

    min_wait = random.uniform(MIN_DELAY, MAX_DELAY)

    if diff < min_wait:
        wait_time = min_wait - diff
        print(f"😴 Delay: {wait_time:.2f}s")
        await asyncio.sleep(wait_time)

    LAST_ACTION_TIME = asyncio.get_event_loop().time()

# ================================
# 📦 DB
# ================================

saved_files = set()

async def load_db():
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
            await global_delay()

            if not client.is_connected():
                await client.connect()

            await client.forward_messages(dest, message)
            return

        except FloodWaitError as e:
            print(f"⏳ FloodWait {e.seconds}s")
            await asyncio.sleep(e.seconds + 2)

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

            await safe_forward(dest, related_file)
            print("📦 File sent")

            await save_to_db(filename)

            print(f"✅ Saved → {len(saved_files)}")
            break

# ================================
# 🔁 SCAN
# ================================

async def process_old():
    global IS_SCANNING

    print("⚡ Scanning...")
    IS_SCANNING = True

    async for msg in client.iter_messages(SOURCE_GROUP_ID, limit=SCAN_LIMIT):
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
# ▶️ MAIN
# ================================

async def main():
    await client.start()
    print("🚀 Started")

    await load_db()
    await process_old()

    print("🚀 Live running...")
    await client.run_until_disconnected()

asyncio.run(main())
