import asyncio
import random
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, RPCError

# ================== CONFIG ==================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # example: -100xxxxxxxxxx

# Upload tuning (SAFE MODE)
MIN_DELAY = 3
MAX_DELAY = 6
MAX_RETRIES = 5

# ============================================

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


# ================== QUEUE ==================
upload_queue = asyncio.Queue()


async def uploader():
    while True:
        file_path = await upload_queue.get()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"📤 Uploading: {file_path}")

                await client.send_file(
                    CHANNEL_ID,
                    file_path,
                    caption="DB channel"
                )

                print(f"✅ Done: {file_path}")
                break

            except FloodWaitError as e:
                print(f"⏳ FloodWait: sleeping {e.seconds}s")
                await asyncio.sleep(e.seconds)

            except RPCError as e:
                print(f"⚠️ RPC Error: {e}")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                await asyncio.sleep(5)

        else:
            print(f"🚫 Failed after retries: {file_path}")

        # 🔥 Human-like delay
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(f"😴 Sleeping {delay}s before next upload\n")
        await asyncio.sleep(delay)

        upload_queue.task_done()


# ================== PRODUCER ==================
async def add_files_from_folder(folder_path):
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        if os.path.isfile(full_path):
            await upload_queue.put(full_path)


# ================== MAIN ==================
async def main():
    await client.start()
    print("🚀 Client started")

    # Start uploader worker
    asyncio.create_task(uploader())

    # Add your files
    await add_files_from_folder("files")  # folder name

    # Wait until all uploads done
    await upload_queue.join()

    print("🎉 All uploads completed")


if __name__ == "__main__":
    asyncio.run(main())
