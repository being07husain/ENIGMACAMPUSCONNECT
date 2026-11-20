from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    fullname: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str = "student"
    course: Optional[str] = None
    dob: Optional[str] = None
    rank: Optional[str] = None
    department: Optional[str] = None
    dateofjoin: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EventCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    category: str = "other"
    date: str
    time: str
    venue: str
    description: str = ""
    total_seats: int = Field(default=100, ge=1, le=100000)
    image: Optional[str] = None
    organizer: Optional[str] = None
    faculty_coordinator: Optional[str] = None
    highlights: Optional[list[str]] = None

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    category: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    description: Optional[str] = None
    total_seats: Optional[int] = Field(None, ge=1, le=100000)
    image: Optional[str] = None
    organizer: Optional[str] = None
    faculty_coordinator: Optional[str] = None
    highlights: Optional[list[str]] = None

class NotificationCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=2, max_length=2000)
    type: str = "faculty"

class EventRegistration(BaseModel):
    event_id: str

class OpportunityRegistration(BaseModel):
    opportunity_id: str
    statement: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    fullname: Optional[str] = Field(None, min_length=2, max_length=100)
    course: Optional[str] = None
    dob: Optional[str] = None
    rank: Optional[str] = None
    department: Optional[str] = None

class ClubApplicationRequest(BaseModel):
    club_name: str = Field(min_length=2, max_length=100)
    student_name: str = Field(min_length=2, max_length=100)
    rank: str = Field(min_length=1, max_length=50)
    course: str = Field(min_length=1, max_length=50)
    department: str = Field(min_length=2, max_length=100)
    role: str = Field(min_length=2, max_length=50)
    statement: Optional[str] = None

