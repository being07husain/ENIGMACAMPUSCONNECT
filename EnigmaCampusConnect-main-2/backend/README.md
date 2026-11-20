# CampusConnect Python + MongoDB Backend

## 1. Requirements
- Python 3.10+
- MongoDB running locally OR a MongoDB Atlas connection string

## 2. Setup
Create and activate a virtual environment:

Windows:
```
python -m venv venv
venv\Scripts\activate
```

Install:
```
pip install -r backend/requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and change `JWT_SECRET`.

## 3. Seed demo accounts
From the project root:
```
python backend/seed.py
```

Demo club account:
`codingclub@campusconnect.com`
`Club@12345`

Demo faculty account:
`faculty@campusconnect.com`
`Faculty@12345`

## 4. Start backend
From project root:
```
uvicorn backend.main:app --reload
```

Open:
`http://127.0.0.1:8000/Views/login.html`

API docs:
`http://127.0.0.1:8000/docs`

Health:
`http://127.0.0.1:8000/api/health`

## 5. Permissions
- student: read events/notices + register for events
- faculty: same + create notifications
- club: same + create events

The permission check happens on the Python API, so changing/hiding a button in the browser cannot bypass it.

## 6. MongoDB
Database name defaults to `campusconnect`.
Collections:
`users`, `clubs`, `events`, `notifications`, `registrations`, `opportunities`, `resources`.

Every successful event/notification creation writes a real MongoDB document.
