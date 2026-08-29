#!/usr/bin/env python3
"""
Upload grades from a Learning Suite CSV export to Canvas.

Usage:
    python3 scripts/upload_grades.py grades.csv              # dry run (default)
    python3 scripts/upload_grades.py grades.csv --commit      # actually push grades

Reads the CSV, maps students by Net ID to Canvas user IDs,
maps Learning Suite column names to Canvas assignment names,
and pushes grades via the Canvas Submissions API.

Handles special values:
    "5:dropped"  → score 5 (strip suffix)
    "x"          → excused
    " " or ""    → skip (no grade)
    "0"          → score 0
"""

import csv
import os
import re
import sys
import time
import requests
from dotenv import load_dotenv

# ── Configuration ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

load_dotenv(os.path.join(PROJECT_DIR, ".env.local"))

CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
CANVAS_API_URL = os.getenv("CANVAS_API_URL", "").strip().rstrip("/")
COURSE_ID = 34877

REQUEST_DELAY = 0.05


# ── Column name mapping: Learning Suite → Canvas ──────────────────────────

COLUMN_MAP = {
    "Reading Quiz 1": "Quiz 1",
    "Reading Quiz 2": "Quiz 2",
    "Reading Quiz 3": "Quiz 3",
    "Reading Quiz 4": "Quiz 4",
    "Reading Quiz 5": "Quiz 5",
    "Reading Quiz 6": "Quiz 6",
    "Reading Quiz 7": "Quiz 7",
    "Resume v1": "Resume v1",
    "Resume v2": "Resume v2",
    "Networking Tracker": "Networking Tracker",
    "Goals Chat": "Goals Chat",
    "TA Interview and Mentoring 1": "TA Interview and Mentoring 1",
    "TA Interview and Mentoring 2": "TA Interview and Mentoring 2",
    "TA Interview and Mentoring 3": "TA Interview and Mentoring 3",
    "P1: Intelligence Brief": "P1: Intelligence Brief",
    "P2: Point of View": "P2: Point of View",
    "Capstone: Conversation Deck": "Capstone: Conversation Deck",
    "Mid-Semester Feedback Survey": "Mid-Semester Feedback Survey (Bonus)",
    "Student Ratings": "Student Ratings (Bonus)",
}


# ── Helpers ────────────────────────────────────────────────────────────────

def parse_score(raw):
    """Parse a Learning Suite grade value.

    Returns:
        ("score", numeric_value)  — a normal grade
        ("excused", None)         — excused
        ("skip", None)            — blank / no grade
    """
    raw = raw.strip()
    if not raw or raw == " ":
        return ("skip", None)
    if raw.lower() == "x":
        return ("excused", None)

    # Strip ":dropped" or similar suffixes
    cleaned = re.sub(r":.*$", "", raw)
    try:
        return ("score", float(cleaned))
    except ValueError:
        return ("skip", None)


def get_canvas_roster(api_url, token, course_id):
    """Fetch all students, return {login_id: user_id} mapping."""
    roster = {}
    url = f"{api_url}/api/v1/courses/{course_id}/users"
    params = {"enrollment_type[]": "student", "per_page": 100}
    headers = {"Authorization": f"Bearer {token}"}

    while url:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        for user in resp.json():
            login = user.get("login_id", "")
            if login:
                roster[login] = user["id"]
        # Follow pagination
        url = None
        params = {}
        link_header = resp.headers.get("Link", "")
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
    return roster


def get_canvas_assignments(api_url, token, course_id):
    """Fetch all assignments, return {name: id} mapping."""
    assignments = {}
    url = f"{api_url}/api/v1/courses/{course_id}/assignments"
    params = {"per_page": 100}
    headers = {"Authorization": f"Bearer {token}"}

    while url:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        for a in resp.json():
            assignments[a["name"]] = a["id"]
        url = None
        params = {}
        link_header = resp.headers.get("Link", "")
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
    return assignments


def push_grade(api_url, token, course_id, assignment_id, user_id, score_type, score_value):
    """Push a single grade to Canvas."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{api_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"

    if score_type == "excused":
        data = {"submission": {"excuse": True}}
    else:
        data = {"submission": {"posted_grade": str(score_value)}}

    time.sleep(REQUEST_DELAY)
    resp = requests.put(url, headers=headers, json=data)
    return resp.ok, resp.status_code


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/upload_grades.py <grades.csv> [--commit]")
        sys.exit(1)

    csv_path = sys.argv[1]
    commit = "--commit" in sys.argv

    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)

    # Read CSV
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"Loaded {len(rows)} students from CSV")

    if not commit:
        print("\n*** DRY RUN — add --commit to actually push grades ***\n")

    # Get Canvas data
    if commit:
        if not CANVAS_API_TOKEN or not CANVAS_API_URL:
            print("ERROR: Set CANVAS_API_TOKEN and CANVAS_API_URL in .env.local")
            sys.exit(1)

        print("Fetching Canvas roster...")
        roster = get_canvas_roster(CANVAS_API_URL, CANVAS_API_TOKEN, COURSE_ID)
        print(f"  {len(roster)} students found")

        print("Fetching Canvas assignments...")
        assignments = get_canvas_assignments(CANVAS_API_URL, CANVAS_API_TOKEN, COURSE_ID)
        print(f"  {len(assignments)} assignments found")
    else:
        roster = None
        assignments = None

    # Process grades
    stats = {"pushed": 0, "skipped": 0, "excused": 0, "errors": 0, "not_found": 0}

    for csv_col, canvas_name in COLUMN_MAP.items():
        # Check if this column has any data
        has_data = any(
            parse_score(r.get(csv_col, ""))[0] != "skip" for r in rows
        )
        if not has_data:
            continue

        # Resolve Canvas assignment ID
        canvas_id = None
        if commit:
            canvas_id = assignments.get(canvas_name)
            if not canvas_id:
                print(f"\n  WARNING: Canvas assignment '{canvas_name}' not found — skipping")
                continue

        print(f"\n── {csv_col} → {canvas_name} ──")

        for row in rows:
            net_id = row["Net ID"]
            name = f"{row['First Name']} {row['Last Name']}"
            score_type, score_value = parse_score(row.get(csv_col, ""))

            if score_type == "skip":
                stats["skipped"] += 1
                continue

            if score_type == "excused":
                label = "excused"
                stats["excused"] += 1
            else:
                label = str(score_value)

            if commit:
                user_id = roster.get(net_id)
                if not user_id:
                    print(f"  {name:30s} ({net_id}) — NOT FOUND in Canvas")
                    stats["not_found"] += 1
                    continue

                ok, status = push_grade(
                    CANVAS_API_URL, CANVAS_API_TOKEN, COURSE_ID,
                    canvas_id, user_id, score_type, score_value
                )
                if ok:
                    stats["pushed"] += 1
                    print(f"  {name:30s} → {label}")
                else:
                    stats["errors"] += 1
                    print(f"  {name:30s} → ERROR ({status})")
            else:
                print(f"  {name:30s} → {label}")
                stats["pushed"] += 1

    # Summary
    print(f"\n── Summary ──")
    print(f"  {'Pushed' if commit else 'Would push'}: {stats['pushed']}")
    print(f"  Excused: {stats['excused']}")
    print(f"  Skipped (blank): {stats['skipped']}")
    if stats["not_found"]:
        print(f"  Not found in Canvas: {stats['not_found']}")
    if stats["errors"]:
        print(f"  Errors: {stats['errors']}")

    if not commit:
        print(f"\n  Run with --commit to push these grades to Canvas.")


if __name__ == "__main__":
    main()
