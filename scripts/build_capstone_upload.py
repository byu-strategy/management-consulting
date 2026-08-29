#!/usr/bin/env python3
"""Aggregate per-student grade markdown files into one Canvas upload CSV.

Parses grades/[slug].md for:
  - Deck Quality Score: XX / 100
  - Storyline / Insight / Evidence / Design dimension scores from the scores table

Joins with grades/_manifest.csv on slug to attach user_id and email.
Writes grades/capstone_canvas_upload.csv with columns:
    student, user_id, email, score_out_of_100, storyline, insight, evidence, design
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRADES = ROOT / "grades"
MANIFEST = GRADES / "_manifest.csv"
OUT = GRADES / "capstone_canvas_upload.csv"

SCORE_RE = re.compile(r"\*\*Deck Quality Score:\s*(\d+)\s*/\s*100\*\*", re.IGNORECASE)
# Row shape: | Storyline | 4 | 0.30 | 1.20 |
DIM_RE = re.compile(r"^\|\s*(Storyline|Insight|Evidence|Design)\s*\|\s*(\d)\s*\|", re.IGNORECASE | re.MULTILINE)


def parse_grade_file(path: Path):
    text = path.read_text(encoding="utf-8")
    m = SCORE_RE.search(text)
    if not m:
        return None
    dims = {k.lower(): None for k in ("Storyline", "Insight", "Evidence", "Design")}
    for dm in DIM_RE.finditer(text):
        dims[dm.group(1).lower()] = int(dm.group(2))
    return {
        "score_out_of_100": int(m.group(1)),
        "storyline": dims["storyline"],
        "insight": dims["insight"],
        "evidence": dims["evidence"],
        "design": dims["design"],
    }


def main() -> int:
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))

    rows = []
    missing = []
    for m in manifest:
        slug = m["slug"]
        grade_path = GRADES / f"{slug}.md"
        if not grade_path.exists():
            # No grade file: either no PDF to grade (Test Student) or truly missing.
            if not m.get("pdf_path"):
                continue
            missing.append(slug)
            continue
        parsed = parse_grade_file(grade_path)
        if not parsed:
            missing.append(slug)
            continue
        rows.append({
            "student": m["student"],
            "user_id": m["user_id"],
            "email": m["email"],
            **parsed,
        })

    fieldnames = [
        "student", "user_id", "email",
        "score_out_of_100",
        "storyline", "insight", "evidence", "design",
    ]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {OUT} with {len(rows)} rows.")
    if missing:
        print(f"Missing or unparseable ({len(missing)}): {missing}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
