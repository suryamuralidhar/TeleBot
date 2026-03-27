from telethon import TelegramClient
from config import API_ID, API_HASH

def get_client(session_name="mysession"):
    return TelegramClient(session_name, API_ID, API_HASH)
