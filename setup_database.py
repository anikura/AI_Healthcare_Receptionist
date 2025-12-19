import os
import certifi
from pymongo import MongoClient, ASCENDING
from datetime import datetime
from cryptography.fernet import Fernet
from config import MONGO_URI, DB_NAME, ENCRYPTION_KEY_FILE

def load_key():
    if not os.path.exists(ENCRYPTION_KEY_FILE):
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, "wb") as f:
            f.write(key)
        return key
    with open(ENCRYPTION_KEY_FILE, "rb") as f:
        return f.read()

def generate_token():
    today = datetime.utcnow().strftime("%Y%m%d")
    return f"{today}{int(datetime.utcnow().timestamp()) % 100000}"

def setup():
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )
    db = client[DB_NAME]

    client.admin.command("ping")

    db.appointments.create_index(
        [("doctor_name", ASCENDING), ("date", ASCENDING), ("time", ASCENDING)],
        unique=True,
        name="doctor_slot_unique"
    )

    db.appointments.create_index(
        [("status", ASCENDING)],
        name="status_index"
    )

    db.appointments.create_index(
        [("created_at", ASCENDING)],
        name="created_at_index"
    )

    db.patient_reports.create_index(
        [("created_at", ASCENDING)],
        name="reports_created_index"
    )

    print("Database indexes created successfully")

if __name__ == "__main__":
    setup()
