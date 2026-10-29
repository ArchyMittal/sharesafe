# app/db/seed.py
"""
Idempotent database seeding for ShareSafe demo.
Seeds fictional demo users, resources (GPU workstation hero, camera kit, 3D printer, meeting room),
past bookings with conditions, and initial audit entries.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from app.db.session import get_connection, init_db

def seed_database(db_path: Optional[Path] = None) -> None:
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()

        # 1. Clear existing rows for idempotent reset
        cur.execute("DELETE FROM audit;")
        cur.execute("DELETE FROM notifications;")
        cur.execute("DELETE FROM waitlist;")
        cur.execute("DELETE FROM holds;")
        cur.execute("DELETE FROM incidents;")
        cur.execute("DELETE FROM conditions;")
        cur.execute("DELETE FROM bookings;")
        cur.execute("DELETE FROM resources;")
        cur.execute("DELETE FROM users;")

        # 2. Seed Users
        users = [
            (
                "u1",
                "Maya Lin",
                "maya.lin@univ.edu",
                "borrower",
                "human",
                json.dumps(["gpu_safety", "lab_safety_lvl1", "laser_cutter"]),
                3,
                "team_robotics",
                "https://lh3.googleusercontent.com/aida-public/AB6AXuBVKFNxHU8HR34pRc709VsMtWumElSaLspP4dFW3yQirc5MWOY6qSMSs5bZDMSw-q3aNu5DCxdGLqDJ4tcEWRvUNPysfYiQv4XhU5SuOxC53m54xTHkP7DD-eq2x-1rOYtg65_dOy-PoyDnu-kFmpk4kHNz8eh1tlDh-O_rlfzFvxYruv0oHSSrVhOl3zAWuWX1ubVYFuSRKDBaJuMMQKy2C2BtDHGsE4R0ug0UcOg",
                "Bioengineering '25 (Eligible Borrower)",
                "demo123"
            ),
            (
                "u2",
                "Marcus Vance",
                "marcus.vance@univ.edu",
                "owner",
                "human",
                json.dumps(["gpu_safety", "lab_safety_lvl1", "inspector_cert"]),
                5,
                "lab_staff",
                None,
                "Lab Custodian & Manager (Resource Owner)",
                "demo123"
            ),
            (
                "u3",
                "Dr. Aris Thorne",
                "aris.thorne@univ.edu",
                "inspector",
                "human",
                json.dumps(["gpu_safety", "inspector_cert", "electrical_safety"]),
                10,
                "safety_board",
                None,
                "Robotics Lab Director (Authorized Safety Inspector)",
                "demo123"
            ),
            (
                "u4",
                "Sarah Admin",
                "sarah.admin@univ.edu",
                "admin",
                "human",
                json.dumps(["gpu_safety", "inspector_cert"]),
                10,
                "administration",
                None,
                "Makerspace Director (Campus Admin)",
                "demo123"
            ),
            (
                "u5",
                "David Kim",
                "david.kim@univ.edu",
                "borrower",
                "human",
                json.dumps(["lab_safety_lvl1"]),
                2,
                "team_robotics",
                None,
                "CS Sophomore '26 (Year 2 - Needs GPU Training)",
                "demo123"
            ),
            (
                "agent:custodian",
                "ShareSafe Custodian Agent",
                "agent.custodian@sharesafe.internal",
                "agent",
                "agent",
                json.dumps([]),
                0,
                "system",
                None,
                "Autonomous Custodian Agent (Bounded Authority)",
                "agent_secret"
            ),
        ]

        cur.executemany(
            """
            INSERT INTO users (id, name, email, role, kind, training, year, team_id, avatar, title, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            users
        )

        # 3. Seed Resources
        now_iso = datetime.utcnow().isoformat()
        gpu_rules = {
            "min_year": 3,
            "required_training": ["gpu_safety"],
            "max_hours_per_booking": 4,
            "min_notice_hours": 1,
            "weekend_requires_supervisor": False,
            "max_consecutive_bookings": 2,
            "recent_usage_cap_hours_30d": 20,
            "requires_inspection_within_days": 30
        }
        camera_rules = {
            "min_year": 1,
            "required_training": ["camera_safety"],
            "max_hours_per_booking": 24,
            "min_notice_hours": 2,
            "requires_inspection_within_days": 14
        }
        printer_rules = {
            "min_year": 1,
            "required_training": ["lab_safety_lvl1"],
            "max_hours_per_booking": 8,
            "min_notice_hours": 1,
            "requires_inspection_within_days": 30
        }
        space_rules = {
            "min_year": 1,
            "required_training": [],
            "max_hours_per_booking": 4,
            "min_notice_hours": 0,
            "requires_inspection_within_days": 60
        }

        resources = [
            (
                "r1",
                "NVIDIA RTX 4090 Workstation Pod",
                "lab-equipment",
                "Robotics Lab • Pod 1",
                "Dual RTX 4090 24GB, AMD Threadripper PRO 64-core, 256GB ECC RAM, Ubuntu 22.04 LTS, CUDA 12.4. Hero resource for campus AI workloads.",
                "u2",
                "available",
                "ready",
                None,
                json.dumps(gpu_rules),
                "https://lh3.googleusercontent.com/aida-public/AB6AXuDZo7cnWmnsJSRf51nf5E9V8HyhtUFrrY5eQRsCp3Atx-Mj29l6dLYfa6l8P4itM0qeLP2lAGUq_KQeVc_jLRBUZJwx-n51nTNa8yHSdEHIOzkGVURBLQRGt085UcSfC-tT5tpIJ-RQ4kCTRsEJrBE_LXFL_WPxdiGrB_uCHsaUTMsN18Qiy8S9n5wSLvCuwI1npObSExIzODb7swqpyAgrcqFSz7q2ZElFYzpi2Xs",
                1,
                "Req: GPU Safety & Thermal Clearance (Level 2)",
                "4h max session • Do not tamper with cooling • Report thermal faults",
                1,
                "Pod A-01 Ready",
                "GPU-NODE-4090",
                now_iso
            ),
            (
                "r2",
                "Sony FX3 Cinema Rig Package",
                "av-equipment",
                "Film & Media Cage • Rm 108",
                "Full-Frame 4K, 24-70mm GM II f/2.8 lens, top XLR audio handle, 2x 160GB CFexpress cards, and Pelican hard case.",
                "u2",
                "available",
                "ready",
                None,
                json.dumps(camera_rules),
                "https://lh3.googleusercontent.com/aida-public/AB6AXuALg42inhtKk6Lrt91XFH-2ptMDBSOXTl83y-eUsPoa-ifiEFZfCTNeBxeYhPwQ0Dnm9wLiPiAfcHQb4wPqZSIdKjrY0DZFqov3nR465d4u0NCXOyfapO1GabNDevryCHOSoVZdA5GC123lm7cdnWQzrgSLh7Al_RN_QtXAxPJXGydgXW8cvaiMWFLxvD8rndFUK2DrfbtKty-0NeVYFUuN4cr2oWmzFYuSZka7sS0",
                1,
                "Req: Film Cage Clearance",
                "Overnight loan • Return with lenses capped & battery charged",
                1,
                "Cage Locker #12",
                "CINE-FX3-01",
                now_iso
            ),
            (
                "r3",
                "Bambu Lab X1-Carbon Combo",
                "lab-equipment",
                "Maker Commons • Bay 4",
                "Dual-nozzle high-temp bed, AMS 4-filament unit, hardened steel 0.4mm nozzle with carbon-fiber reinforced printing.",
                "u2",
                "available",
                "ready",
                None,
                json.dumps(printer_rules),
                "https://lh3.googleusercontent.com/aida-public/AB6AXuAmxXq8J2i-qcGn3Sfi6PeE40BZ0lNAUEzBduCuuegSwW-O5EZqiB6udmX3Q2I-QYIshdM3VCYbA3UNRb3znwref2sRX9aa3cnmRFNEARnSytkupL85csltSChTVHMJtWW56d3pW09HWzWCVTeasjroHqTTA88WngfQr4_DTNeMeFBGMIuO-MXrF1TKwMTcAoXEQWG1UzVxJ8IpQ8i-auH-qyUSOHGVkoJL2Yd7gjg",
                1,
                "Req: Lab Safety Lvl 1",
                "48h max loan • Multi-Color AMS • Clean bed after printing",
                2,
                "Bay A-04 Ready",
                "BAMBU-X1-04",
                now_iso
            ),
            (
                "r4",
                "Maker Space Project Room",
                "spaces",
                "Engineering Wing • Rm 204",
                "Seats 10, dual 65-inch 4K collaboration displays, digital whiteboard, soldering fume extraction station.",
                "u3",
                "available",
                "ready",
                None,
                json.dumps(space_rules),
                None,
                0,
                None,
                "4h max booking • Clean up workbench after session",
                1,
                "Room 204",
                "SPACE-RM-204",
                now_iso
            ),
        ]

        cur.executemany(
            """
            INSERT INTO resources (
                id, name, category, location, description, owner_id,
                status, readiness_state, hold_id, rules_json, image_url,
                training_required, training_description, usage_rules,
                max_duration_days, bay_tag, item_code, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            resources
        )

        # 4. Seed Past Bookings (for historical readiness & fairness tracking)
        t_past_start = (datetime.utcnow() - timedelta(days=3)).replace(hour=10, minute=0, second=0).isoformat()
        t_past_end = (datetime.utcnow() - timedelta(days=3)).replace(hour=14, minute=0, second=0).isoformat()
        past_trace = {
            "verdict": "recommend_approve",
            "rule_results": [
                {"rule_id": "min_year", "passed": True, "severity": "block", "message": "Year 3 meets min year 3"},
                {"rule_id": "required_training", "passed": True, "severity": "block", "message": "Training 'gpu_safety' verified"},
                {"rule_id": "duration", "passed": True, "severity": "block", "message": "Duration 4h within 4h cap"}
            ],
            "explanation": "All safety and eligibility rules passed."
        }

        bookings = [
            (
                "b-hist-001",
                "r1",
                "u1",
                "u2",
                t_past_start,
                t_past_end,
                "returned",
                "Vision transformer training run for senior design thesis.",
                "Capstone Research",
                "Academic project with Prof. Thorne",
                1,
                t_past_start,
                t_past_start,
                None,
                None,
                t_past_start,
                t_past_end,
                None,
                "Approved - valid academic training project",
                json.dumps(past_trace),
                0,
                0,
                "team_robotics"
            )
        ]

        cur.executemany(
            """
            INSERT INTO bookings (
                id, resource_id, user_id, owner_id, start, end, status,
                message, purpose, justification, training_acknowledged,
                created_at, approved_at, rejected_at, waitlisted_at,
                checked_in_at, returned_at, cancelled_at, owner_reason,
                decision_trace_json, returned_late, no_show, team_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            bookings
        )

        # 5. Seed Conditions for the past booking
        conditions = [
            (
                "c-001-before",
                "b-hist-001",
                "before",
                "Clean boot, GPUs idle at 34C, chassis fans spinning normally.",
                None,
                "u1",
                t_past_start
            ),
            (
                "c-001-after",
                "b-hist-001",
                "after",
                "Run complete, workspace left clean, normal temperatures.",
                None,
                "u1",
                t_past_end
            )
        ]

        cur.executemany(
            """
            INSERT INTO conditions (id, booking_id, phase, notes, photo_hash, recorded_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            conditions
        )

        # 6. Seed initial audit log entry
        from app.core.audit import append_audit
        append_audit("system", "seed_database", {"status": "initialized", "resource_count": len(resources)})

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
    print("Database successfully seeded!")
