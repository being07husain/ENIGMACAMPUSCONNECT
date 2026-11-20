import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from database import users, clubs, events, notifications, event_registrations, opportunity_registrations, opportunities, db, init_db
from auth import hash_password

def run_seed():
    init_db()

    club_email = os.getenv("DEMO_CLUB_EMAIL", "codingclub@campusconnect.com").lower()
    club_password = os.getenv("DEMO_CLUB_PASSWORD", "Club@12345")
    club_name = os.getenv("DEMO_CLUB_NAME", "Coding Club")
    faculty_email = os.getenv("DEMO_FACULTY_EMAIL", "faculty@campusconnect.com").lower()
    faculty_password = os.getenv("DEMO_FACULTY_PASSWORD", "Faculty@12345")
    faculty_name = os.getenv("DEMO_FACULTY_NAME", "Campus Faculty")

    now = datetime.now(timezone.utc)

    try:
        users.update_one(
            {"email": club_email},
            {"$set": {
                "fullname": club_name,
                "email": club_email,
                "password_hash": hash_password(club_password),
                "role": "club",
                "created_at": now,
            }},
            upsert=True,
        )
        clubs.update_one(
            {"email": club_email},
            {"$set": {
                "club_name": club_name,
                "email": club_email,
                "description": "Technical club account for creating campus events.",
                "created_at": now,
            }},
            upsert=True,
        )

        users.update_one(
            {"email": faculty_email},
            {"$set": {
                "fullname": faculty_name,
                "email": faculty_email,
                "password_hash": hash_password(faculty_password),
                "role": "faculty",
                "created_at": now,
            }},
            upsert=True,
        )

        # Standard campus events to store in MongoDB
        campus_events = [
            {
                "title": "TechTalk 2026",
                "category": "workshops",
                "organizer": club_name,
                "faculty_coordinator": "Prof. Radhika Sharma",
                "date": "2026-04-25",
                "time": "10:00 AM - 12:00 PM",
                "venue": "Auditorium",
                "description": "An interactive session with industry experts on the future of technology. Learn about the latest trends, get career advice, and network with professionals.",
                "image": "../images/techtalk.jpg",
                "total_seats": 150,
                "registered_seats": 120,
                "highlights": [
                    "Industry Expert Speakers from Leading Tech Companies",
                    "Networking Opportunities with Alumni & Recruiters",
                    "Interactive Q&A Session & Live Demos",
                    "Certificate of Participation provided"
                ],
                "created_by": club_email,
                "created_at": now,
            },
            {
                "title": "Robotics Workshop",
                "category": "workshops",
                "organizer": "Robotics Club",
                "faculty_coordinator": "Prof. Radhika Sharma",
                "date": "2026-04-27",
                "time": "2:00 PM - 5:00 PM",
                "venue": "Lab 3",
                "description": "Hands-on workshop on building and programming robots. Learn microcontroller basics, sensor integration, motor drivers and autonomous navigation.",
                "image": "../images/robotics.jpg",
                "total_seats": 50,
                "registered_seats": 45,
                "highlights": [
                    "Hardware kits and microcontrollers provided",
                    "Hands-on robot assembly and calibration",
                    "Obstacle avoidance code walkthrough",
                    "Group mini-challenge with awards"
                ],
                "created_by": club_email,
                "created_at": now,
            },
            {
                "title": "Cultural Fest - Rangmanch",
                "category": "festivals",
                "organizer": "Cultural Club",
                "faculty_coordinator": "Prof. Radhika Sharma",
                "date": "2026-05-02",
                "time": "5:00 PM Onwards",
                "venue": "Open Ground",
                "description": "Music, dance, drama and more! A magnificent 3-day campus festival celebrating student creativity, live bands, stage theater and culinary stalls.",
                "image": "../images/cultural.jpg",
                "total_seats": 500,
                "registered_seats": 450,
                "highlights": [
                    "Live Battle of the Bands concert",
                    "Inter-college street play & drama competition",
                    "Celebrity guest musical performance",
                    "Food trucks and carnival games"
                ],
                "created_by": club_email,
                "created_at": now,
            },
            {
                "title": "HackCamp 2026",
                "category": "workshops",
                "organizer": "Enigma IT Club",
                "faculty_coordinator": "Prof. Radhika Sharma",
                "date": "2026-05-10",
                "time": "9:00 AM - 9:00 AM (24 Hrs)",
                "venue": "Tech Block 4",
                "description": "A fast-paced 24-hour hackathon where developers, designers and creators build innovative solutions, web apps, and AI tools for exciting cash prizes.",
                "image": "../images/hackathon.jpg",
                "total_seats": 100,
                "registered_seats": 82,
                "highlights": [
                    "₹150,000+ total prize pool and sponsor swag",
                    "Mentorship from experienced senior engineers",
                    "Unlimited snacks, energy drinks and refreshments",
                    "Direct fast-track interview opportunities"
                ],
                "created_by": club_email,
                "created_at": now,
            },
            {
                "title": "Annual Sports Meet 2026",
                "category": "sports",
                "organizer": "Sports Club",
                "faculty_coordinator": "Prof. Radhika Sharma",
                "date": "2026-05-15",
                "time": "8:00 AM - 6:00 PM",
                "venue": "College Sports Complex",
                "description": "Inter-department and intra-college championships featuring track & field athletics, basketball, football, volleyball and badminton tournaments.",
                "image": "../images/LANDING PAGE IMAGE.png",
                "total_seats": 300,
                "registered_seats": 215,
                "highlights": [
                    "15+ Individual and team track events",
                    "Trophies, medals and official university certificates",
                    "Professional referees and first-aid support",
                    "Opening & closing ceremony marches"
                ],
                "created_by": club_email,
                "created_at": now,
            },
            {
                "title": "Career Guidance Seminar",
                "category": "seminars",
                "organizer": "Placement Cell",
                "faculty_coordinator": "Prof. Radhika Sharma",
                "date": "2026-05-20",
                "time": "11:00 AM - 1:00 PM",
                "venue": "Seminar Hall",
                "description": "Learn proven strategies for cracking technical interviews, building industry-ready resumes, acing coding assessments, and exploring global career pathways.",
                "image": "../images/SIDEIMAGE.jfif",
                "total_seats": 200,
                "registered_seats": 188,
                "highlights": [
                    "Keynote by Senior Director of Engineering",
                    "Resume review and ATS optimization workshop",
                    "Mock technical interview breakdown",
                    "Q&A and personal placement roadmap guide"
                ],
                "created_by": faculty_email,
                "created_at": now,
            },
        ]

        for ev in campus_events:
            events.update_one({"title": ev["title"]}, {"$set": ev}, upsert=True)

        events.update_many(
            {"faculty_coordinator": {"$exists": False}},
            {"$set": {"faculty_coordinator": "Prof. Radhika Sharma"}}
        )

        # Standard campus opportunities to store in MongoDB
        campus_opportunities = [
            {
                "opp_id": "google-internship",
                "title": "Google Summer Internship",
                "category": "internships",
                "badgeLabel": "Internship",
                "badgeClass": "internship",
                "avatarType": "google",
                "avatarLetter": "G",
                "organization": "Google",
                "location": "Remote",
                "deadline": "Apr 28, 2025",
                "perk": "₹45,000 / month",
                "description": "Join Google for an exciting 10-week summer software engineering internship. Work on scalable backend systems, AI tools, and collaborate with world-class engineers.",
                "requirements": [
                    "B.Tech / M.Tech students graduating in 2026 or 2027",
                    "Strong problem solving and algorithms in C++, Java, or Python",
                    "Understanding of operating systems, databases and web protocols",
                    "Good communication skills and team mindset"
                ],
                "created_at": now,
            },
            {
                "opp_id": "sih-2025",
                "title": "SIH 2025",
                "category": "hackathons",
                "badgeLabel": "Hackathon",
                "badgeClass": "hackathon",
                "avatarType": "sih",
                "avatarLetter": "🇮🇳",
                "organization": "Ministry of Education",
                "location": "Pan India",
                "deadline": "May 10, 2025",
                "perk": "₹1,00,000 Prize Pool",
                "description": "Smart India Hackathon 2025 is a nationwide initiative to provide students with a platform to solve real pressing problems faced by ministries and industries.",
                "requirements": [
                    "Team of 6 students with at least 1 female member",
                    "Selection through internal college screening round",
                    "Hardware & Software editions available",
                    "Direct mentorship from government & industry officials"
                ],
                "created_at": now,
            },
            {
                "opp_id": "tcs-hiring-drive",
                "title": "TCS & Co. Hiring Drive",
                "category": "internships",
                "badgeLabel": "Placement",
                "badgeClass": "placement",
                "avatarType": "tcs",
                "avatarLetter": "T",
                "organization": "TCS",
                "location": "Pan India",
                "deadline": "May 15, 2025",
                "perk": "7.5 - 11.5 LPA Package",
                "description": "Annual campus placement and fast-track hiring drive for Digital and Prime software engineering positions across TCS innovation hubs.",
                "requirements": [
                    "B.Tech Computer Science / IT / ECE 2025 batch candidates",
                    "Minimum 65% aggregate with no active backlogs",
                    "National Qualifier Test (NQT) score qualification",
                    "Aptitude & Technical interview rounds"
                ],
                "created_at": now,
            },
            {
                "opp_id": "microsoft-internship",
                "title": "Microsoft SWE Internship",
                "category": "internships",
                "badgeLabel": "Internship",
                "badgeClass": "internship",
                "avatarType": "microsoft",
                "avatarLetter": "M",
                "organization": "Microsoft",
                "location": "Hyderabad / Bangalore",
                "deadline": "May 18, 2025",
                "perk": "₹80,000 / month",
                "description": "Design, build, and deliver the next generation of cloud experiences, Azure services, and developer tools alongside Microsoft engineers.",
                "requirements": [
                    "Pre-final year students pursuing B.Tech / M.Tech in CS/IT",
                    "Expertise in Data Structures, Algorithms, and Object-Oriented Design",
                    "Experience with C#, Java, Python, or TypeScript",
                    "Passion for high-impact cloud architectures"
                ],
                "created_at": now,
            },
            {
                "opp_id": "national-coding-championship",
                "title": "National Coding Championship",
                "category": "competitions",
                "badgeLabel": "Competition",
                "badgeClass": "hackathon",
                "avatarType": "sih",
                "avatarLetter": "🏆",
                "organization": "Coding Ninjas",
                "location": "Online",
                "deadline": "May 22, 2025",
                "perk": "₹50,000 + Job Referrals",
                "description": "Compete against 20,000+ top college programmers in an adrenaline-packed 3-hour competitive programming showdown.",
                "requirements": [
                    "Open to all university undergraduate and postgraduate students",
                    "3 rounds: Speed Round, Algorithm Arena, and Optimization Challenge",
                    "Supported languages: C++, Java, Python3, Kotlin",
                    "Top 100 receive direct referral passes to top product firms"
                ],
                "created_at": now,
            },
            {
                "opp_id": "reliance-scholarship",
                "title": "Reliance Foundation Scholarship",
                "category": "scholarships",
                "badgeLabel": "Scholarship",
                "badgeClass": "scholarship",
                "avatarType": "scholarship",
                "avatarLetter": "R",
                "organization": "Reliance Foundation",
                "location": "All India",
                "deadline": "May 30, 2025",
                "perk": "Up to ₹2,00,000 Grant",
                "description": "Financial assistance and leadership mentorship grant for meritorious students pursuing undergraduate studies in technology and sciences.",
                "requirements": [
                    "First-year students enrolled in full-time degree programs",
                    "Minimum 60% marks in 12th standard board exams",
                    "Household annual income criteria as per foundation guidelines",
                    "Online aptitude test and essay submission"
                ],
                "created_at": now,
            },
            {
                "opp_id": "aws-cloud-challenge",
                "title": "AWS Cloud Practitioner Challenge",
                "category": "certifications",
                "badgeLabel": "Certification",
                "badgeClass": "certification",
                "avatarType": "aws",
                "avatarLetter": "☁️",
                "organization": "Amazon Web Services",
                "location": "Self-Paced / Online",
                "deadline": "Jun 5, 2025",
                "perk": "100% Free Exam Voucher",
                "description": "Complete hands-on AWS Cloud training modules and earn an official voucher for the AWS Certified Cloud Practitioner examination.",
                "requirements": [
                    "Must complete 20 hours of curated AWS Skill Builder courses",
                    "Pass 2 practice assessments with >= 80% score",
                    "Official college email address required for verification",
                    "Certificate and digital badge upon passing"
                ],
                "created_at": now,
            },
            {
                "opp_id": "ai-data-science-bootcamp",
                "title": "Full Stack AI Bootcamp",
                "category": "workshops",
                "badgeLabel": "Workshop",
                "badgeClass": "hackathon",
                "avatarType": "google",
                "avatarLetter": "⚡",
                "organization": "Enigma IT Club",
                "location": "Tech Block 4",
                "deadline": "Jun 10, 2025",
                "perk": "Project Portfolio + Certificate",
                "description": "A 4-week intensive hands-on bootcamp covering LLMs, LangChain, vector databases, and deploying generative AI web apps into production.",
                "requirements": [
                    "Basic Python programming knowledge",
                    "Laptop with minimum 8GB RAM",
                    "Commitment of 6 hours per week for live sessions & projects",
                    "Capstone group project presentation"
                ],
                "created_at": now,
            }
        ]

        for opp in campus_opportunities:
            opportunities.update_one({"opp_id": opp["opp_id"]}, {"$set": opp}, upsert=True)

        # Migrate any documents in old generic registrations into event_registrations
        old_regs = db["registrations"].find()
        for r in old_regs:
            ev = events.find_one({"_id": r.get("event_id")})
            u = users.find_one({"_id": r.get("user_id")})
            event_registrations.update_one(
                {"event_id": r.get("event_id"), "user_id": r.get("user_id")},
                {"$set": {
                    "event_id": r.get("event_id"),
                    "event_title": ev.get("title", "") if ev else "",
                    "event_category": ev.get("category", "") if ev else "",
                    "event_date": ev.get("date", "") if ev else "",
                    "event_time": ev.get("time", "") if ev else "",
                    "event_venue": ev.get("venue", "") if ev else "",
                    "organizer": ev.get("organizer", "") if ev else "",
                    "user_id": r.get("user_id"),
                    "student_name": u.get("fullname", "") if u else "",
                    "student_email": u.get("email", r.get("email", "")) if u else r.get("email", ""),
                    "student_course": u.get("course", "") if u else "",
                    "student_rank": u.get("rank", "") if u else "",
                    "status": "Registered",
                    "registered_at": r.get("registered_at", now)
                }},
                upsert=True
            )

        campus_notices = [
            {
                "title": "EXAMINATION NOTICE - Spring 2026",
                "message": "End-term theory and practical examination schedules for BCA, B.Tech and MCA have been released.",
                "type": "faculty",
                "created_by": faculty_email,
                "created_at": now,
            },
            {
                "title": "CULTURAL FEST - Rangmanch Auditions",
                "message": "Auditions for dance, music and drama club contingents start next Monday at the Student Activity Center.",
                "type": "faculty",
                "created_by": faculty_email,
                "created_at": now,
            },
            {
                "title": "SPORTS QUOTA ADMISSIONS & TRIALS",
                "message": "Annual trials for football, basketball, and track & field teams scheduled at the Sports Complex ground.",
                "type": "faculty",
                "created_by": faculty_email,
                "created_at": now,
            },
            {
                "title": "ACADEMIC CALENDAR 2026",
                "message": "Official university holiday list, semester break dates and midterm schedules updated.",
                "type": "faculty",
                "created_by": faculty_email,
                "created_at": now,
            },
        ]
        for cn in campus_notices:
            notifications.update_one({"title": cn["title"]}, {"$set": cn}, upsert=True)

        campus_resources = [
            {
                "title": "Data Structures & Algorithms Handbook",
                "category": "Computer Science",
                "format": "PDF",
                "size": "4.2 MB",
                "link": "#",
                "created_at": now,
            },
            {
                "title": "Full Stack Web Development Architecture Notes",
                "category": "Web Dev",
                "format": "PDF",
                "size": "2.8 MB",
                "link": "#",
                "created_at": now,
            },
            {
                "title": "Database Management Systems & MongoDB Guide",
                "category": "Databases",
                "format": "Cheatsheet",
                "size": "1.5 MB",
                "link": "#",
                "created_at": now,
            },
            {
                "title": "Computer Networks & OS Lecture Notes",
                "category": "Systems",
                "format": "PDF",
                "size": "3.6 MB",
                "link": "#",
                "created_at": now,
            },
        ]
        for cr in campus_resources:
            db["resources"].update_one({"title": cr["title"]}, {"$set": cr}, upsert=True)

        print("Seed complete.")
        print(f"Opportunities seeded: {opportunities.count_documents({})}")
        print(f"Event registrations count: {event_registrations.count_documents({})}")
        print(f"Club login:    {club_email} / {club_password}")
        print(f"Faculty login: {faculty_email} / {faculty_password}")
    except Exception as exc:
        print(f"Error seeding database: {exc}")
        print("Please check that MongoDB is running and your connection string in backend/.env is valid.")


if __name__ == "__main__":
    run_seed()

