#!/usr/bin/env python3
"""
Sync course structure to Canvas via API.

Combines the functionality of generate_imscc.py (modules + reading links)
and generate_moodle.py (assignments + gradebook) into a single Canvas API push.

Workflow:
  1. Edit your course website (00-schedule.qmd, chapter files, etc.)
  2. Run: python3 scripts/sync_canvas.py
  3. Your Canvas course is updated — no import files needed.

Requires:
  - pip install requests python-dotenv
  - .env.local with CANVAS_API_TOKEN and CANVAS_API_URL
"""

import os
import re
import sys
import time
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# ── Configuration ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SCHEDULE_FILE = os.path.join(PROJECT_DIR, "00-schedule.qmd")

load_dotenv(os.path.join(PROJECT_DIR, ".env.local"))

CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
CANVAS_API_URL = os.getenv("CANVAS_API_URL", "").strip().rstrip("/")
COURSE_ID = 34871  # API-TESTING course

BASE_URL = "https://byu-strategy.github.io/management-consulting"
ASSESSMENTS_URL = f"{BASE_URL}/00-assessments.html"

# Mountain Time offset (UTC-7 for MDT)
MT_OFFSET = timedelta(hours=-7)

# Rate limiting
REQUEST_DELAY = 0.1  # seconds between API calls


# ── Assessment Data (shared with other generators) ────────────────────────

ASSIGNMENT_GROUPS = [
    {"id": "reading_quizzes", "title": "Reading Quizzes", "weight": 10.0, "position": 1},
    {"id": "resume_networking", "title": "Resume and Networking", "weight": 12.0, "position": 2},
    {"id": "practice_interviews", "title": "Practice Interviews", "weight": 42.0, "position": 3},
    {"id": "client_work", "title": "Client Work", "weight": 36.0, "position": 4},
    {"id": "surveys_bonus", "title": "Surveys (Bonus)", "weight": 0.0, "position": 5},
]

ASSESSMENTS = [
    # ── Reading Quizzes (10 × 5 pts = 50 pts) ──
    {"id": "quiz_01", "title": "Quiz 1", "group": "reading_quizzes", "points": 5,
     "due": "2026-01-15", "week": 2, "anchor": "#reading-quizzes"},
    {"id": "quiz_02", "title": "Quiz 2", "group": "reading_quizzes", "points": 5,
     "due": "2026-01-22", "week": 3, "anchor": "#reading-quizzes"},
    {"id": "quiz_03", "title": "Quiz 3", "group": "reading_quizzes", "points": 5,
     "due": "2026-01-29", "week": 4, "anchor": "#reading-quizzes"},
    {"id": "quiz_04", "title": "Quiz 4", "group": "reading_quizzes", "points": 5,
     "due": "2026-02-05", "week": 5, "anchor": "#reading-quizzes"},
    {"id": "quiz_05", "title": "Quiz 5", "group": "reading_quizzes", "points": 5,
     "due": "2026-02-12", "week": 6, "anchor": "#reading-quizzes"},
    {"id": "quiz_06", "title": "Quiz 6", "group": "reading_quizzes", "points": 5,
     "due": "2026-02-26", "week": 8, "anchor": "#reading-quizzes"},
    {"id": "quiz_07", "title": "Quiz 7", "group": "reading_quizzes", "points": 5,
     "due": "2026-03-05", "week": 9, "anchor": "#reading-quizzes"},
    {"id": "quiz_08", "title": "Quiz 8", "group": "reading_quizzes", "points": 5,
     "due": "2026-03-17", "week": 11, "anchor": "#reading-quizzes"},
    {"id": "quiz_09", "title": "Quiz 9", "group": "reading_quizzes", "points": 5,
     "due": "2026-04-02", "week": 13, "anchor": "#reading-quizzes"},
    {"id": "quiz_10", "title": "Quiz 10", "group": "reading_quizzes", "points": 5,
     "due": "2026-04-14", "week": 15, "anchor": "#reading-quizzes"},

    # ── Resume and Networking (60 pts) ──
    {"id": "resume_v1", "title": "Resume v1", "group": "resume_networking", "points": 15,
     "due": "2026-02-05", "week": 5, "anchor": "#resume-and-networking"},
    {"id": "resume_v2", "title": "Resume v2", "group": "resume_networking", "points": 20,
     "due": "2026-02-19", "week": 7, "anchor": "#resume-and-networking"},
    {"id": "networking_tracker", "title": "Networking Tracker", "group": "resume_networking", "points": 25,
     "due": "2026-04-14", "week": 15, "anchor": "#resume-and-networking"},

    # ── Practice Interviews (210 pts) ──
    {"id": "goals_chat", "title": "Goals Chat", "group": "practice_interviews", "points": 10,
     "due": "2026-01-24", "week": 3, "anchor": "#practice-interviews"},
    {"id": "peer_interview_1", "title": "Practice Interview: Peer 1", "group": "practice_interviews", "points": 20,
     "due": "2026-01-31", "week": 4, "anchor": "#practice-interviews"},
    {"id": "ta_interview_1", "title": "TA Interview and Mentoring 1", "group": "practice_interviews", "points": 20,
     "due": "2026-02-07", "week": 5, "anchor": "#practice-interviews"},
    {"id": "peer_interview_2", "title": "Practice Interview: Peer 2", "group": "practice_interviews", "points": 20,
     "due": "2026-02-14", "week": 6, "anchor": "#practice-interviews"},
    {"id": "peer_interview_3", "title": "Practice Interview: Peer 3", "group": "practice_interviews", "points": 20,
     "due": "2026-02-21", "week": 7, "anchor": "#practice-interviews"},
    {"id": "peer_interview_4", "title": "Practice Interview: Peer 4", "group": "practice_interviews", "points": 20,
     "due": "2026-02-28", "week": 8, "anchor": "#practice-interviews"},
    {"id": "ta_interview_2", "title": "TA Interview and Mentoring 2", "group": "practice_interviews", "points": 20,
     "due": "2026-03-07", "week": 9, "anchor": "#practice-interviews"},
    {"id": "peer_interview_5", "title": "Practice Interview: Peer 5", "group": "practice_interviews", "points": 20,
     "due": "2026-03-14", "week": 10, "anchor": "#practice-interviews"},
    {"id": "peer_interview_6", "title": "Practice Interview: Peer 6", "group": "practice_interviews", "points": 20,
     "due": "2026-03-21", "week": 11, "anchor": "#practice-interviews"},
    {"id": "peer_interview_7", "title": "Practice Interview: Peer 7", "group": "practice_interviews", "points": 20,
     "due": "2026-04-04", "week": 13, "anchor": "#practice-interviews"},
    {"id": "ta_interview_3", "title": "TA Interview and Mentoring 3", "group": "practice_interviews", "points": 20,
     "due": "2026-04-11", "week": 14, "anchor": "#practice-interviews"},

    # ── Client Work (180 pts) ──
    {"id": "p1_intel_brief", "title": "P1: Intelligence Brief", "group": "client_work", "points": 40,
     "due": "2026-02-21", "week": 7, "anchor": "#intelligence-brief"},
    {"id": "p2_point_of_view", "title": "P2: Point of View", "group": "client_work", "points": 40,
     "due": "2026-03-21", "week": 11, "anchor": "#point-of-view"},
    {"id": "capstone", "title": "Capstone: Conversation Deck", "group": "client_work", "points": 100,
     "due": "2026-04-14", "week": 15, "anchor": "#conversation-deck"},

    # ── Surveys / Bonus ──
    {"id": "mid_semester_feedback", "title": "Mid-Semester Feedback Survey (Bonus)", "group": "surveys_bonus", "points": 5,
     "due": "2026-02-24", "week": 8, "anchor": ""},
    {"id": "student_ratings", "title": "Student Ratings (Bonus)", "group": "surveys_bonus", "points": 5,
     "due": "2026-04-14", "week": 15, "anchor": ""},
]


# ── Canvas API Client ─────────────────────────────────────────────────────

class CanvasAPI:
    def __init__(self, base_url, token, course_id):
        self.base_url = base_url
        self.course_id = course_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def _url(self, path):
        return f"{self.base_url}/api/v1/courses/{self.course_id}{path}"

    def _request(self, method, path, **kwargs):
        time.sleep(REQUEST_DELAY)
        resp = self.session.request(method, self._url(path), **kwargs)
        if not resp.ok:
            print(f"  ERROR {resp.status_code}: {method} {path}")
            print(f"  {resp.text[:300]}")
            resp.raise_for_status()
        return resp.json()

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path):
        time.sleep(REQUEST_DELAY)
        resp = self.session.delete(self._url(path))
        return resp

    def get_all(self, path, **kwargs):
        """Paginate through all results."""
        results = []
        url = self._url(path)
        params = kwargs.get("params", {})
        params["per_page"] = 100
        while url:
            time.sleep(REQUEST_DELAY)
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            results.extend(resp.json())
            # Follow Link header for pagination
            url = None
            params = {}  # params are in the URL after first request
            link_header = resp.headers.get("Link", "")
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
        return results

    # ── High-level operations ──

    def clear_modules(self):
        """Delete all existing modules."""
        modules = self.get_all("/modules")
        for m in modules:
            print(f"  Deleting module: {m['name']}")
            self.delete(f"/modules/{m['id']}")
        return len(modules)

    def clear_assignments(self):
        """Delete all existing assignments."""
        assignments = self.get_all("/assignments")
        for a in assignments:
            print(f"  Deleting assignment: {a['name']}")
            self.delete(f"/assignments/{a['id']}")
        return len(assignments)

    def clear_assignment_groups(self):
        """Delete non-default assignment groups."""
        groups = self.get_all("/assignment_groups")
        for g in groups:
            print(f"  Deleting group: {g['name']}")
            self.delete(f"/assignment_groups/{g['id']}")
        return len(groups)

    def create_assignment_group(self, name, weight, position):
        """Create an assignment group (grade category)."""
        return self.post("/assignment_groups", json={
            "name": name,
            "group_weight": weight,
            "position": position,
        })

    def enable_weighted_grading(self):
        """Set course to use weighted assignment groups."""
        time.sleep(REQUEST_DELAY)
        resp = self.session.put(
            f"{self.base_url}/api/v1/courses/{self.course_id}",
            json={"course": {"apply_assignment_group_weights": True}}
        )
        resp.raise_for_status()
        return resp.json()

    def create_assignment(self, name, points, due_date, group_id, description=""):
        """Create an assignment."""
        # Convert date string to ISO 8601 with Mountain Time
        dt = datetime.strptime(due_date, "%Y-%m-%d")
        dt = dt.replace(hour=23, minute=59, second=0, tzinfo=timezone(MT_OFFSET))
        due_at = dt.isoformat()

        return self.post("/assignments", json={
            "assignment": {
                "name": name,
                "points_possible": points,
                "due_at": due_at,
                "assignment_group_id": group_id,
                "submission_types": ["online_upload"],
                "description": description,
                "published": True,
            }
        })

    def create_module(self, name, position):
        """Create a module."""
        return self.post("/modules", json={
            "module": {
                "name": name,
                "position": position,
            }
        })

    def publish_module(self, module_id):
        """Publish a module."""
        return self.put(f"/modules/{module_id}", json={
            "module": {"published": True}
        })

    def add_module_subheader(self, module_id, title, position, indent=0):
        """Add a sub-header to a module."""
        return self.post(f"/modules/{module_id}/items", json={
            "module_item": {
                "type": "SubHeader",
                "title": title,
                "position": position,
                "indent": indent,
            }
        })

    def add_module_external_url(self, module_id, title, url, position, indent=0, new_tab=True):
        """Add an external URL to a module."""
        return self.post(f"/modules/{module_id}/items", json={
            "module_item": {
                "type": "ExternalUrl",
                "title": title,
                "external_url": url,
                "position": position,
                "indent": indent,
                "new_tab": new_tab,
            }
        })

    def add_module_assignment(self, module_id, assignment_id, position, indent=0):
        """Add an assignment link to a module."""
        return self.post(f"/modules/{module_id}/items", json={
            "module_item": {
                "type": "Assignment",
                "content_id": assignment_id,
                "position": position,
                "indent": indent,
            }
        })

    def set_front_page(self):
        """Set the course home page to show modules."""
        time.sleep(REQUEST_DELAY)
        resp = self.session.put(
            f"{self.base_url}/api/v1/courses/{self.course_id}",
            json={"course": {"default_view": "modules"}}
        )
        resp.raise_for_status()
        return resp.json()


# ── Schedule Parser (from generate_imscc.py) ──────────────────────────────

def parse_schedule(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    return parse_daily_schedule(content), parse_phases(content)


def parse_daily_schedule(content):
    sessions = []
    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        if re.match(r"\|\s*Wk\s*\|", line):
            in_table = True
            continue
        if in_table and re.match(r"\|[-:]+\|", line):
            continue
        if in_table and line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 6:
                session = parse_session_row(cells)
                if session:
                    sessions.append(session)
        elif in_table and not line.startswith("|"):
            break
    return sessions


def parse_session_row(cells):
    week_str, num_str, date, topic_raw, assessments_raw, interviews_raw = cells[:6]
    try:
        week = int(week_str.strip())
        num = int(num_str.strip())
    except ValueError:
        return None

    links = []
    external_links = []
    guest = None

    guest_match = re.search(
        r"\*\*Guest:\s*\[([^\]]+)\]\(([^)]+)\)\s*\(([^)]+)\)\*\*", topic_raw
    )
    if guest_match:
        guest = f"{guest_match.group(1)} ({guest_match.group(3)})"

    # Parse external reading links (after "Readings:" marker)
    readings_match = re.search(r"—\s*Readings?:\s*(.+?)$", topic_raw)
    if readings_match:
        readings_text = readings_match.group(1)
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", readings_text):
            link_text = match.group(1)
            link_url = match.group(2)
            if not link_url.endswith(".qmd") and ".qmd#" not in link_url:
                external_links.append((link_text, link_url))

    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+\.qmd(?:#[^)]*)?)\)", topic_raw):
        link_text = match.group(1)
        link_target = match.group(2)
        if "#" in link_target:
            qmd_file, anchor = link_target.split("#", 1)
            anchor = "#" + anchor
        else:
            qmd_file = link_target
            anchor = None
        html_file = qmd_file.replace(".qmd", ".html")
        links.append((link_text, html_file, anchor))

    topic_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", topic_raw)
    topic_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", topic_text)
    topic_text = re.sub(r"\s*—\s*Guest:.*$", "", topic_text)
    # Also handle readings info after " — Readings:"
    topic_text = re.sub(r"\s*—\s*Readings:.*$", "", topic_text)
    topic_text = topic_text.strip().rstrip("—").strip()

    assessments = []
    if assessments_raw and assessments_raw != "–":
        for item in assessments_raw.split(";"):
            item = item.strip()
            item = re.sub(r"\*\*([^*]+)\*\*", r"\1", item)
            if item and item != "–":
                assessments.append(item)

    interviews = None
    if interviews_raw and interviews_raw != "–":
        interviews = interviews_raw.strip()

    return {
        "week": week, "num": num, "date": date.strip(),
        "topic": topic_text, "links": links, "external_links": external_links,
        "guest": guest, "assessments": assessments, "interviews": interviews,
    }


def parse_phases(content):
    phases = []
    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        if re.match(r"\|\s*Imperative\s*\|", line):
            in_table = True
            continue
        if in_table and re.match(r"\|[-:]+\|", line):
            continue
        if in_table and line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 4:
                name = re.sub(r"\*\*([^*]+)\*\*", r"\1", cells[0]).strip()
                week_range = cells[1].strip().replace("–", "-").replace("—", "-")
                desc = cells[3].strip()
                if "-" in week_range:
                    start, end = week_range.split("-")
                    phases.append((name, int(start), int(end), desc))
                else:
                    w = int(week_range)
                    phases.append((name, w, w, desc))
        elif in_table and not line.startswith("|"):
            break
    return phases


def get_phase_for_week(week, phases):
    for name, start, end, _ in phases:
        if start <= week <= end:
            return name
    return "Course"


def get_assessment_url(assessment):
    anchor = assessment.get("anchor", "")
    if anchor:
        return ASSESSMENTS_URL + anchor
    return ASSESSMENTS_URL


# ── Main Sync Logic ───────────────────────────────────────────────────────

def main():
    if not CANVAS_API_TOKEN or not CANVAS_API_URL:
        print("ERROR: Set CANVAS_API_TOKEN and CANVAS_API_URL in .env.local")
        sys.exit(1)

    api = CanvasAPI(CANVAS_API_URL, CANVAS_API_TOKEN, COURSE_ID)

    # Parse schedule
    print(f"Parsing: {SCHEDULE_FILE}")
    sessions, phases = parse_schedule(SCHEDULE_FILE)
    print(f"  {len(sessions)} sessions, {len(phases)} phases")

    # Group sessions by week
    weeks = {}
    for s in sessions:
        weeks.setdefault(s["week"], []).append(s)

    # Group assessments by week
    assessments_by_week = {}
    for a in ASSESSMENTS:
        assessments_by_week.setdefault(a["week"], []).append(a)

    # ── Step 1: Clear existing content ──
    print("\n── Clearing existing Canvas content ──")
    n = api.clear_modules()
    print(f"  Deleted {n} modules")
    n = api.clear_assignments()
    print(f"  Deleted {n} assignments")
    n = api.clear_assignment_groups()
    print(f"  Deleted {n} assignment groups")

    # ── Step 2: Set up course ──
    print("\n── Configuring course ──")
    api.enable_weighted_grading()
    print("  Enabled weighted grading")
    api.set_front_page()
    print("  Set home page to modules view")

    # ── Step 3: Create assignment groups ──
    print("\n── Creating assignment groups ──")
    group_canvas_ids = {}  # maps our group id -> Canvas group id
    for g in ASSIGNMENT_GROUPS:
        result = api.create_assignment_group(g["title"], g["weight"], g["position"])
        group_canvas_ids[g["id"]] = result["id"]
        print(f"  {g['title']}: {g['weight']}% (Canvas ID: {result['id']})")

    # ── Step 4: Create assignments ──
    print("\n── Creating assignments ──")
    assignment_canvas_ids = {}  # maps our assessment id -> Canvas assignment id
    for a in ASSESSMENTS:
        url = get_assessment_url(a)
        description = (
            f'<p>See full details: '
            f'<a href="{url}" target="_blank">{a["title"]} on course website</a></p>'
        )
        canvas_group_id = group_canvas_ids[a["group"]]
        result = api.create_assignment(
            a["title"], a["points"], a["due"], canvas_group_id, description
        )
        assignment_canvas_ids[a["id"]] = result["id"]
        print(f"  {a['title']} ({a['points']} pts, due {a['due']})")

    # ── Step 5: Create modules with content ──
    print("\n── Creating weekly modules ──")
    for week_num in sorted(weeks.keys()):
        week_sessions = weeks[week_num]
        phase = get_phase_for_week(week_num, phases)
        module_name = f"Week {week_num}: {phase}"

        module = api.create_module(module_name, week_num)
        module_id = module["id"]
        print(f"\n  {module_name}")

        pos = 1

        for s in week_sessions:
            # Session sub-header
            title = f"{s['date']} — {s['topic']}"
            if s.get("guest"):
                title += f" (Guest: {s['guest']})"
            api.add_module_subheader(module_id, title, pos)
            print(f"    [{pos}] {title}")
            pos += 1

            # Reading links (chapter sections)
            for text, page, anchor in s["links"]:
                url = f"{BASE_URL}/{page}"
                if anchor:
                    url += anchor
                api.add_module_external_url(module_id, text, url, pos, indent=1)
                print(f"    [{pos}]   → {text}")
                pos += 1

            # External reading links (non-.qmd URLs)
            for text, url in s.get("external_links", []):
                api.add_module_external_url(module_id, f"📖 {text}", url, pos, indent=1)
                print(f"    [{pos}]   → 📖 {text}")
                pos += 1

        # Assessments due this week
        week_assessments = assessments_by_week.get(week_num, [])
        if week_assessments:
            api.add_module_subheader(module_id, "Due This Week", pos)
            print(f"    [{pos}] Due This Week")
            pos += 1

            for a in week_assessments:
                canvas_id = assignment_canvas_ids[a["id"]]
                api.add_module_assignment(module_id, canvas_id, pos, indent=1)
                print(f"    [{pos}]   → {a['title']} ({a['points']} pts)")
                pos += 1

        # Publish the module
        api.publish_module(module_id)

    # ── Summary ──
    total_points = sum(a["points"] for a in ASSESSMENTS if a["group"] != "surveys_bonus")
    bonus_points = sum(a["points"] for a in ASSESSMENTS if a["group"] == "surveys_bonus")
    print(f"\n── Done ──")
    print(f"  {len(weeks)} weekly modules")
    print(f"  {len(ASSESSMENTS)} assignments ({total_points} pts + {bonus_points} bonus)")
    print(f"  {len(ASSIGNMENT_GROUPS)} assignment groups")
    print(f"  {sum(len(s['links']) for s in sessions)} reading links")
    print(f"\n  View: {CANVAS_API_URL}/courses/{COURSE_ID}/modules")


if __name__ == "__main__":
    main()
