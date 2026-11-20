import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta
import random
from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pymongo.errors import DuplicateKeyError, PyMongoError
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from database import users, clubs, events, notifications, event_registrations, opportunity_registrations, registrations, opportunities, club_applications, ping_database, init_db
from schemas import RegisterRequest, LoginRequest, EventCreate, EventUpdate, NotificationCreate, EventRegistration, OpportunityRegistration, ProfileUpdateRequest, ClubApplicationRequest
from auth import hash_password, verify_password, create_access_token, require_roles, decode_token, bearer
from fastapi.security import HTTPAuthorizationCredentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Safely attempt to initialize database indexes on startup
    init_db()
    yield


app = FastAPI(title="CampusConnect API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = bearer


def oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


def serialize(doc: dict) -> dict:
    if not doc:
        return {}
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    for key, value in list(doc.items()):
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
    return doc


@app.get("/api/health")
def health():
    try:
        ping_database()
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {exc}")


@app.post("/api/auth/register")
def register(data: RegisterRequest):
    data.email = data.email.lower()
    if users.find_one({"email": data.email}):
        raise HTTPException(status_code=409, detail="Account with this email already exists")

    if data.role not in {"student", "faculty"}:
        raise HTTPException(status_code=400, detail="Public registration is only for student/faculty")

    user_doc = {
        "fullname": data.fullname,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "role": data.role,
        "created_at": datetime.now(timezone.utc),
    }

    if data.role == "student":
        user_doc.update({
            "course": data.course or "BCA",
            "dob": data.dob or "",
            "rank": data.rank or "",
        })
    elif data.role == "faculty":
        user_doc.update({
            "department": data.department or "Information Technology",
            "dateofjoin": data.dateofjoin or "",
        })

    try:
        result = users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Account with this email already exists")

    created = users.find_one({"_id": result.inserted_id})
    token = create_access_token(str(created["_id"]), created["role"], created["email"])
    return {"token": token, "user": serialize(created)}


@app.post("/api/auth/login")
def login(data: LoginRequest):
    data.email = data.email.lower()
    user = users.find_one({"email": data.email})
    if not user:
        club = clubs.find_one({"email": data.email})
        if not club:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        user = users.find_one({"email": data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user["_id"]), user["role"], user["email"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize(user),
    }


@app.get("/api/auth/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials)
    user = users.find_one({"_id": oid(payload["sub"])}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = serialize(user)
    try:
        user_oid = oid(payload["sub"])
        data["events_registered"] = event_registrations.count_documents({"user_id": user_oid})
        data["opportunities_registered"] = opportunity_registrations.count_documents({"user_id": user_oid})
        data["clubs_applied"] = club_applications.count_documents({"user_id": user_oid})
    except Exception:
        data["events_registered"] = 0
        data["opportunities_registered"] = 0
        data["clubs_applied"] = 0
    return data


@app.get("/api/dashboard/summary")
def get_dashboard_summary(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    user_id = None
    user_data = None
    if credentials:
        try:
            payload = decode_token(credentials)
            user_id = oid(payload.get("sub"))
            u = users.find_one({"_id": user_id}, {"password_hash": 0})
            if u:
                user_data = serialize(u)
        except Exception:
            pass

    registered_event_ids = set()
    events_registered_count = 0
    opps_registered_count = 0
    clubs_applied_count = 0
    applied_club_names = set()

    if user_id:
        events_registered_count = event_registrations.count_documents({"user_id": user_id})
        opps_registered_count = opportunity_registrations.count_documents({"user_id": user_id})
        clubs_applied_count = club_applications.count_documents({"user_id": user_id})
        registered_event_ids = {str(r["event_id"]) for r in event_registrations.find({"user_id": user_id}, {"event_id": 1})}
        applied_club_names = {r["club_name"] for r in club_applications.find({"user_id": user_id}, {"club_name": 1})}

    # Up to 4 upcoming events from MongoDB
    events_list = []
    for ev in events.find().sort("date", 1).limit(4):
        s = serialize(ev)
        s["is_registered"] = s["id"] in registered_event_ids
        events_list.append(s)

    # Latest 4 notices from MongoDB
    notices_list = []
    for n in notifications.find().sort("created_at", -1).limit(4):
        notices_list.append(serialize(n))

    # Standard clubs with student application status
    club_names = ["E-CELL", "NSS", "ROTARACT", "ENIGMA", "IIC", "UBA", "PRABHANDHAN"]
    clubs_list = []
    for name in club_names:
        is_app = any(name.lower() in applied.lower() for applied in applied_club_names)
        clubs_list.append({
            "name": name,
            "is_applied": is_app
        })

    return {
        "user": user_data,
        "stats": {
            "events_registered": events_registered_count,
            "clubs_applied": clubs_applied_count,
            "opportunities_registered": opps_registered_count,
            "notices_count": notifications.count_documents({}),
            "resources_count": db_collection("resources").count_documents({}),
        },
        "upcoming_events": events_list,
        "notices": notices_list,
        "recommended_clubs": clubs_list
    }


@app.put("/api/auth/profile")
def update_profile(data: ProfileUpdateRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")
    
    users.update_one({"_id": oid(payload["sub"])}, {"$set": update_data})
    updated_user = users.find_one({"_id": oid(payload["sub"])}, {"password_hash": 0})
    return {"message": "Profile updated successfully", "user": serialize(updated_user)}


@app.get("/api/events")
def get_events(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    user_id = None
    if credentials:
        try:
            payload = decode_token(credentials)
            user_id = oid(payload.get("sub"))
        except Exception:
            pass

    registered_event_ids = set()
    if user_id:
        regs = event_registrations.find({"user_id": user_id}, {"event_id": 1})
        registered_event_ids = {str(r["event_id"]) for r in regs}

    res = []
    for ev in events.find().sort("date", 1):
        s = serialize(ev)
        s["is_registered"] = s["id"] in registered_event_ids
        res.append(s)
    return res


@app.post("/api/events")
def create_event(data: EventCreate, current=Depends(require_roles("faculty", "club"))):
    if current.get("role") == "club":
        club = clubs.find_one({"email": current["email"]})
        organizer = data.organizer or (club.get("club_name") if club else "Campus Club")
        faculty_coordinator = data.faculty_coordinator or "Faculty Coordinator"
    else:
        # Faculty role
        user = users.find_one({"_id": oid(current["sub"])})
        faculty_name = f"Prof. {user['fullname']}" if user and user.get("fullname") else "Faculty Coordinator"
        faculty_coordinator = data.faculty_coordinator or faculty_name
        organizer = data.organizer or faculty_name

    document = data.model_dump()
    document.update({
        "organizer": organizer,
        "faculty_coordinator": faculty_coordinator,
        "created_by": current["email"],
        "created_at": datetime.now(timezone.utc),
        "registered_seats": 0,
    })
    result = events.insert_one(document)
    return {"message": "Event created", "event": serialize(events.find_one({"_id": result.inserted_id}))}


@app.put("/api/events/{event_id}")
def update_event(event_id: str, data: EventUpdate, current=Depends(require_roles("faculty", "club"))):
    event_oid = oid(event_id)
    existing = events.find_one({"_id": event_oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    events.update_one({"_id": event_oid}, {"$set": update_data})
    updated = events.find_one({"_id": event_oid})
    return {"message": "Event updated successfully", "event": serialize(updated)}


@app.delete("/api/events/{event_id}")
def delete_event(event_id: str, current=Depends(require_roles("faculty", "club"))):
    event_oid = oid(event_id)
    res = events.delete_one({"_id": event_oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    event_registrations.delete_many({"event_id": event_oid})
    return {"message": "Event deleted successfully"}


@app.post("/api/events/register")
def register_event(data: EventRegistration, current=Depends(require_roles("student"))):
    event_id = oid(data.event_id)
    event = events.find_one({"_id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user_id = oid(current["sub"])
    existing = event_registrations.find_one({"event_id": event_id, "user_id": user_id})
    if existing:
        event_registrations.delete_one({"_id": existing["_id"]})
        events.update_one({"_id": event_id}, {"$inc": {"registered_seats": -1}})
        return {"registered": False, "is_registered": False, "message": "Unregistered from event successfully"}

    if event.get("registered_seats", 0) >= event.get("total_seats", 100):
        raise HTTPException(status_code=409, detail="Event is already full")

    student = users.find_one({"_id": user_id}) or {}
    registration_doc = {
        "event_id": event_id,
        "event_title": event.get("title", ""),
        "event_category": event.get("category", ""),
        "event_date": event.get("date", ""),
        "event_time": event.get("time", ""),
        "event_venue": event.get("venue", ""),
        "organizer": event.get("organizer", ""),
        "faculty_coordinator": event.get("faculty_coordinator", ""),
        "user_id": user_id,
        "student_name": student.get("fullname", ""),
        "student_email": current["email"],
        "student_course": student.get("course", ""),
        "student_rank": student.get("rank", ""),
        "status": "Registered",
        "registered_at": datetime.now(timezone.utc),
    }

    try:
        event_registrations.insert_one(registration_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Already registered for this event")

    events.update_one({"_id": event_id}, {"$inc": {"registered_seats": 1}})
    return {
        "registered": True,
        "is_registered": True,
        "message": f"Successfully registered for {event.get('title')}",
        "registration": serialize(registration_doc)
    }


@app.get("/api/events/my-registrations")
def get_my_event_registrations(current=Depends(require_roles("student"))):
    user_id = oid(current["sub"])
    regs = event_registrations.find({"user_id": user_id}).sort("registered_at", -1)
    return [serialize(x) for x in regs]


@app.get("/api/events/registrations")
def get_all_event_registrations(event_id: Optional[str] = None, current=Depends(require_roles("faculty", "club"))):
    query = {}
    if event_id:
        query["event_id"] = oid(event_id)
    regs = event_registrations.find(query).sort("registered_at", -1)
    return [serialize(x) for x in regs]


@app.get("/api/notifications")
def get_notifications():
    return [serialize(x) for x in notifications.find().sort("created_at", -1)]


@app.post("/api/notifications")
def create_notification(data: NotificationCreate, current=Depends(require_roles("faculty"))):
    document = data.model_dump()
    document.update({
        "created_by": current["email"],
        "created_at": datetime.now(timezone.utc),
    })
    result = notifications.insert_one(document)
    return {"message": "Notification added", "notification": serialize(notifications.find_one({"_id": result.inserted_id}))}


@app.get("/api/clubs")
def get_clubs():
    return [serialize(x) for x in clubs.find({}, {"password_hash": 0})]


@app.post("/api/clubs/apply")
def apply_to_club(data: ClubApplicationRequest, current=Depends(require_roles("student"))):
    user_id = oid(current["sub"])

    # Generate interview date between 3 and 10 days in the future
    days_ahead = random.randint(3, 10)
    interview_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
    time_slot = random.choice([
        "10:30 AM - 11:15 AM",
        "11:30 AM - 12:15 PM",
        "02:00 PM - 02:45 PM",
        "03:00 PM - 03:45 PM",
        "04:00 PM - 04:45 PM"
    ])
    interview_date_str = f"{interview_date.strftime('%B %d, %Y')} at {time_slot}"
    interview_venue = random.choice([
        "Club Activity Room 204",
        "Innovation & Incubation Hub (Block 3)",
        "Conference Room B (Ground Floor)",
        "Tech Lab 4 Annex",
        "Student Council Secretariat"
    ])

    application_doc = {
        "user_id": user_id,
        "email": current["email"],
        "student_name": data.student_name,
        "club_name": data.club_name,
        "rank": data.rank,
        "course": data.course,
        "department": data.department,
        "role": data.role,
        "statement": data.statement or "",
        "interview_date": interview_date_str,
        "interview_venue": interview_venue,
        "status": "Interview Scheduled",
        "applied_at": datetime.now(timezone.utc),
    }

    club_applications.update_one(
        {"user_id": user_id, "club_name": data.club_name},
        {"$set": application_doc},
        upsert=True
    )
    saved = club_applications.find_one({"user_id": user_id, "club_name": data.club_name})
    return {
        "message": "Club application submitted successfully!",
        "application": serialize(saved)
    }


@app.get("/api/clubs/my-applications")
def get_my_club_applications(current=Depends(require_roles("student"))):
    user_id = oid(current["sub"])
    apps = club_applications.find({"user_id": user_id}).sort("applied_at", -1)
    return [serialize(x) for x in apps]


@app.get("/api/clubs/applications")
def get_all_club_applications(current=Depends(require_roles("faculty", "club"))):
    apps = club_applications.find().sort("applied_at", -1)
    return [serialize(x) for x in apps]


@app.get("/api/opportunities")
def get_opportunities(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    user_id = None
    if credentials:
        try:
            payload = decode_token(credentials)
            user_id = oid(payload.get("sub"))
        except Exception:
            pass

    applied_opp_ids = set()
    if user_id:
        regs = opportunity_registrations.find({"user_id": user_id}, {"opportunity_id": 1})
        applied_opp_ids = {str(r["opportunity_id"]) for r in regs}

    res = []
    for opp in opportunities.find().sort("created_at", -1):
        s = serialize(opp)
        opp_key = str(s.get("opp_id") or s.get("id"))
        s["isApplied"] = (opp_key in applied_opp_ids) or (str(s.get("id")) in applied_opp_ids)
        res.append(s)
    return res


@app.post("/api/opportunities/register")
def register_opportunity(data: OpportunityRegistration, current=Depends(require_roles("student"))):
    opp_key = data.opportunity_id
    opp = opportunities.find_one({"opp_id": opp_key})
    if not opp:
        try:
            opp = opportunities.find_one({"_id": oid(opp_key)})
        except Exception:
            opp = None
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    user_id = oid(current["sub"])
    student = users.find_one({"_id": user_id}) or {}
    matched_id = str(opp.get("opp_id") or opp["_id"])

    existing = opportunity_registrations.find_one({"opportunity_id": matched_id, "user_id": user_id})
    if existing:
        opportunity_registrations.delete_one({"_id": existing["_id"]})
        return {
            "registered": False,
            "isApplied": False,
            "message": f"Application withdrawn for {opp.get('title')}"
        }

    opp_reg_doc = {
        "opportunity_id": matched_id,
        "opportunity_title": opp.get("title", ""),
        "organization": opp.get("organization", ""),
        "category": opp.get("category", ""),
        "badge_label": opp.get("badgeLabel", ""),
        "location": opp.get("location", ""),
        "deadline": opp.get("deadline", ""),
        "perk": opp.get("perk", ""),
        "user_id": user_id,
        "student_name": student.get("fullname", ""),
        "student_email": current["email"],
        "student_course": student.get("course", ""),
        "student_rank": student.get("rank", ""),
        "statement": data.statement or "",
        "status": "Applied",
        "registered_at": datetime.now(timezone.utc),
    }

    try:
        opportunity_registrations.insert_one(opp_reg_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Already applied for this opportunity")

    return {
        "registered": True,
        "isApplied": True,
        "message": f"Application submitted successfully for {opp.get('title')}!",
        "registration": serialize(opp_reg_doc)
    }


@app.get("/api/opportunities/my-registrations")
def get_my_opportunity_registrations(current=Depends(require_roles("student"))):
    user_id = oid(current["sub"])
    regs = opportunity_registrations.find({"user_id": user_id}).sort("registered_at", -1)
    return [serialize(x) for x in regs]


@app.get("/api/opportunities/registrations")
def get_all_opportunity_registrations(opportunity_id: Optional[str] = None, current=Depends(require_roles("faculty", "club"))):
    query = {}
    if opportunity_id:
        query["opportunity_id"] = opportunity_id
    regs = opportunity_registrations.find(query).sort("registered_at", -1)
    return [serialize(x) for x in regs]


@app.get("/api/resources")
def get_resources():
    return [serialize(x) for x in db_collection("resources").find().sort("created_at", -1)]


def db_collection(name):
    from database import db
    return db[name]


# Serve your existing frontend. API routes remain under /api.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
