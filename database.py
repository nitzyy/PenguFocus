from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=3000)
db = client["pengufocus"]
collection = db["sessions"]

def ping_db():
    client.admin.command("ping")

def save_session(task, time_spent, status, started_at=None, ended_at=None, ended_reason="timer"):
    if started_at is None:
        started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if ended_at is None:
        ended_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    doc = {
        "task": task,
        "time": int(time_spent),
        "status": status,
        "ended_reason": ended_reason,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "started_at": started_at,
        "ended_at": ended_at
    }

    return collection.insert_one(doc).inserted_id

def get_all_sessions():
    data = list(collection.find({}, {"_id": 0}))
    for item in data:
        item["time"] = int(item.get("time", 0))
    return data

def get_today_sessions():
    today = datetime.now().strftime("%Y-%m-%d")
    data = list(collection.find({"date": today}, {"_id": 0}))
    for item in data:
        item["time"] = int(item.get("time", 0))
    return data

def get_last_session():
    return collection.find_one({}, {"_id": 0}, sort=[("_id", -1)])

def clear_all_sessions():
    collection.delete_many({})