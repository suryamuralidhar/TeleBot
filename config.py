import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))
DB_CHANNEL = int(os.getenv("DB_CHANNEL"))

# 🔁 Routing rules (can also move to ENV later if needed)
ROUTES = {
    -1003728548283: ["sofa"],
    -1003790433327: ["sofa"],
    
}








