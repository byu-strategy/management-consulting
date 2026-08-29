#!/usr/bin/env python3
"""Preview the effect of the planned capstone grade push on each student's
weighted course grade — before vs. after — without writing anything to Canvas.

Reads grades/capstone_canvas_upload.csv, fetches each student's current
submissions and the assignment-group weights, then simulates the weighted
final grade with the new capstone score in place.
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

TOKEN = os.getenv("CANVAS_API_TOKEN")
URL = os.getenv("CANVAS_API_URL", "").rstrip("/")
COURSE_ID = 34877
CAPSTONE_ID = 1322679
CSV_PATH = os.path.join(PROJECT_DIR, "grades", "capstone_canvas_upload.csv")
H = {"Authorization": f"Bearer {TOKEN}"}


def get_all(path, params=None):
    out, url = [], f"{URL}/api/v1/courses/{COURSE_ID}{path}"
    params = dict(params or {}); params.setdefault("per_page", 100)
    while url:
        r = requests.get(url, headers=H, params=params); r.raise_for_status()
        out.extend(r.json())
        url = None; params = {}
        for part in r.headers.get("Link", "").split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
        time.sleep(0.05)
    return out


def letter(p):
    # BYU-style scale (rough); used only for display.
    for cut, l in [(93,"A"),(90,"A-"),(87,"B+"),(83,"B"),(80,"B-"),
                   (77,"C+"),(73,"C"),(70,"C-"),(67,"D+"),(63,"D"),(60,"D-")]:
        if p >= cut: return l
    return "E"


def weighted_grade(submissions_by_aid, assignments, groups):
    """Weighted % across groups, ignoring missing/ungraded (Canvas default)."""
    by_group = {}  # gid -> [earned, possible]
    for a in assignments:
        if a.get("omit_from_final_grade"): continue
        pts = a.get("points_possible") or 0
        if pts <= 0: continue
        sub = submissions_by_aid.get(a["id"])
        if not sub: continue
        if sub.get("excused"): continue
        score = sub.get("score")
        if score is None: continue
        gid = a["assignment_group_id"]
        eg = by_group.setdefault(gid, [0.0, 0.0])
        eg[0] += score; eg[1] += pts

    total_w = 0.0; weighted = 0.0
    for g in groups:
        eg = by_group.get(g["id"])
        if not eg or eg[1] == 0: continue
        w = g.get("group_weight") or 0
        weighted += (eg[0] / eg[1]) * w
        total_w += w
    if total_w == 0: return None
    return weighted / total_w * 100  # rescale if some groups had no data


def main():
    if not TOKEN or not URL:
        print("ERROR: CANVAS_API_TOKEN / CANVAS_API_URL not set"); sys.exit(1)

    print("Fetching assignments + groups...")
    assignments = get_all("/assignments")
    groups = get_all("/assignment_groups")
    a_by_id = {a["id"]: a for a in assignments}
    capstone = a_by_id[CAPSTONE_ID]
    cap_pts = capstone["points_possible"]
    print(f"  {len(assignments)} assignments, {len(groups)} groups")
    print(f"  Capstone in group '{[g['name'] for g in groups if g['id']==capstone['assignment_group_id']][0]}' "
          f"(weight {[g['group_weight'] for g in groups if g['id']==capstone['assignment_group_id']][0]}%)")

    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))
    print(f"  {len(rows)} students in CSV\n")

    print(f"{'Student':35s} {'Now':>7s} {'New':>7s} {'Δ':>7s}  {'Cap':>5s}  Letter")
    print("-" * 78)

    drops = []
    for r in rows:
        uid = r["user_id"].strip()
        new_cap = float(r["score_out_of_100"])

        # Pull this student's submissions
        subs = requests.get(
            f"{URL}/api/v1/courses/{COURSE_ID}/students/submissions",
            headers=H,
            params={"student_ids[]": uid, "per_page": 100, "include[]": "assignment"},
        ).json()
        # paginate
        link = ""
        # (small enough — single page usually; fall through)
        sub_by_aid = {s["assignment_id"]: s for s in subs}

        before = weighted_grade(sub_by_aid, assignments, groups)

        # Simulate new capstone score
        sub_by_aid[CAPSTONE_ID] = {"score": new_cap, "excused": False}
        after = weighted_grade(sub_by_aid, assignments, groups)

        if before is None or after is None:
            print(f"{r['student'][:34]:35s}  (insufficient data)")
            continue
        delta = after - before
        if delta < -2:
            drops.append((r["student"], before, after, delta, new_cap))
        marker = ""
        if letter(before) != letter(after):
            marker = f"  {letter(before)}→{letter(after)}"
        print(f"{r['student'][:34]:35s} {before:7.2f} {after:7.2f} {delta:+7.2f}  "
              f"{new_cap:5.0f}  {letter(after)}{marker}")
        time.sleep(0.05)

    if drops:
        print(f"\n⚠  Largest drops (>2 pts):")
        for s, b, a, d, c in sorted(drops, key=lambda x: x[3])[:10]:
            print(f"   {s[:35]:36s} {b:6.2f} → {a:6.2f}  ({d:+.2f})  cap={c:.0f}")


if __name__ == "__main__":
    main()
