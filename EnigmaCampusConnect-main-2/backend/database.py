import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "campusconnect")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]

users = db["users"]
clubs = db["clubs"]
events = db["events"]
notifications = db["notifications"]
event_registrations = db["event_registrations"]
opportunity_registrations = db["opportunity_registrations"]
registrations = event_registrations  # backward-compatibility alias
opportunities = db["opportunities"]
resources = db["resources"]
club_applications = db["club_applications"]

def init_db():
    """Initialize database indexes safely. Called on application startup."""
    try:
        users.create_index([("email", ASCENDING)], unique=True)
        clubs.create_index([("email", ASCENDING)], unique=True)
        events.create_index([("created_at", ASCENDING)])
        notifications.create_index([("created_at", ASCENDING)])
        event_registrations.create_index([("event_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
        event_registrations.create_index([("user_id", ASCENDING)])
        opportunity_registrations.create_index([("opportunity_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
        opportunity_registrations.create_index([("user_id", ASCENDING)])
        opportunities.create_index([("opp_id", ASCENDING)], unique=True)
        club_applications.create_index([("club_name", ASCENDING), ("user_id", ASCENDING)], unique=True)
        print("Database indexes initialized successfully.")
        return True
    except Exception as exc:
        print(f"Warning: Could not initialize database indexes ({exc}). MongoDB might not be running yet.")
        return False


def ping_database():
    client.admin.command("ping")
    return True

