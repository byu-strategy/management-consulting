#!/usr/bin/env python3
"""Surgically upload Capstone deck grades to Canvas from grades/capstone_canvas_upload.csv.

Usage:
    python3 scripts/upload_capstone_grades.py                  # dry run
    python3 scripts/upload_capstone_grades.py --commit          # actually push

Only touches the "Capstone: Conversation Deck" assignment. CSV must have
columns: user_id, score_out_of_100.
"""

import csv
import os
import sys
import time
import requests
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
load_dotenv(os.path.join(PROJECT_DIR, ".env.local"))

CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
CANVAS_API_URL = os.getenv("CANVAS_API_URL", "").strip().rstrip("/")
COURSE_ID = 34877
ASSIGNMENT_NAME = "Capstone: Conversation Deck"
CSV_PATH = os.path.join(PROJECT_DIR, "grades", "capstone_canvas_upload.csv")
SCORE_COL = "score_out_of_100"
REQUEST_DELAY = 0.05


def find_assignment_id(name):
    url = f"{CANVAS_API_URL}/api/v1/courses/{COURSE_ID}/assignments"
    params = {"per_page": 100, "search_term": name}
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    for a in resp.json():
        if a["name"] == name:
            return a["id"], a.get("points_possible")
    return None, None


def push_grade(assignment_id, user_id, score):
    url = f"{CANVAS_API_URL}/api/v1/courses/{COURSE_ID}/assignments/{assignment_id}/submissions/{user_id}"
    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}", "Content-Type": "application/json"}
    data = {"submission": {"posted_grade": str(score)}}
    time.sleep(REQUEST_DELAY)
    resp = requests.put(url, headers=headers, json=data)
    return resp.ok, resp.status_code, resp.text


def main():
    commit = "--commit" in sys.argv

    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {CSV_PATH}")

    if not commit:
        print("\n*** DRY RUN — add --commit to actually push grades ***\n")

    if not CANVAS_API_TOKEN or not CANVAS_API_URL:
        print("ERROR: Set CANVAS_API_TOKEN and CANVAS_API_URL in .env.local")
        sys.exit(1)

    assignment_id, pts = find_assignment_id(ASSIGNMENT_NAME)
    if not assignment_id:
        print(f"ERROR: Assignment '{ASSIGNMENT_NAME}' not found")
        sys.exit(1)
    print(f"Assignment: {ASSIGNMENT_NAME}  (id={assignment_id}, points_possible={pts})\n")

    pushed = errors = skipped = 0
    for r in rows:
        name = r.get("student", "?")
        user_id = r.get("user_id", "").strip()
        raw = r.get(SCORE_COL, "").strip()
        if not user_id or not raw:
            print(f"  SKIP   {name:40s} (missing user_id or score)")
            skipped += 1
            continue
        try:
            score = float(raw)
        except ValueError:
            print(f"  SKIP   {name:40s} (bad score: {raw!r})")
            skipped += 1
            continue

        if commit:
            ok, status, body = push_grade(assignment_id, user_id, score)
            if ok:
                print(f"  OK     {name:40s} → {score}")
                pushed += 1
            else:
                print(f"  ERROR  {name:40s} → {score}  [{status}] {body[:120]}")
                errors += 1
        else:
            print(f"  WOULD  {name:40s} → {score}  (user_id={user_id})")
            pushed += 1

    print(f"\n── Summary ──")
    print(f"  {'Pushed' if commit else 'Would push'}: {pushed}")
    print(f"  Skipped: {skipped}")
    if errors:
        print(f"  Errors: {errors}")
    if not commit:
        print("\n  Run with --commit to push.")


if __name__ == "__main__":
    main()
