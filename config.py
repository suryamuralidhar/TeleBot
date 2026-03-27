import os

API_ACCOUNTS = [
    {
        "api_id": int(os.getenv("API_ID_1")),
        "api_hash": os.getenv("API_HASH_1"),
        "session": os.getenv("SESSION_1")
    },
    # add more accounts here
]

SOURCE_GROUP_ID = -1001811887579
DB_CHANNEL_ID = -1003591739715

MIN_DELAY = 3
MAX_DELAY = 6
