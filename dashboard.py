from fastapi import FastAPI

app = FastAPI()

stats = {
    "processed": 0,
    "sent": 0
}

@app.get("/")
def home():
    return stats