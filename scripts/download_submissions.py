"""Download Capstone: Conversation Deck submissions from Canvas."""
from __future__ import annotations
"""

Outputs:
  grades/submissions/<lastname-firstname>.<ext>  -- original files
  grades/pdfs/<lastname-firstname>.pdf           -- PDFs (converted from pptx as needed)
  grades/_manifest.csv                           -- one row per enrolled student
"""

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

CANVAS_API_TOKEN = os.environ["CANVAS_API_TOKEN"]
CANVAS_API_URL = os.environ["CANVAS_API_URL"].rstrip("/")
COURSE_ID = 34877
ASSIGNMENT_ID = 1322679

ROOT = Path("grades")
SUBMISSIONS_DIR = ROOT / "submissions"
PDFS_DIR = ROOT / "pdfs"
MANIFEST = ROOT / "_manifest.csv"

HEADERS = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
SOFFICE = "/opt/homebrew/bin/soffice"


def slug(name: str) -> str:
    # "Doe, Jane" -> "doe-jane"
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
        name = f"{last} {first}"
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"\s+", "-", name)


def paginated(url, params=None):
    params = dict(params or {})
    params.setdefault("per_page", 100)
    while url:
        r = requests.get(url, headers=HEADERS, params=params)
        r.raise_for_status()
        yield from r.json()
        url = r.links.get("next", {}).get("url")
        params = None


def convert_to_pdf(src: Path, dest_dir: Path) -> Path | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(dest_dir), str(src)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        print(f"  ! conversion failed: {result.stderr.strip()}", file=sys.stderr)
        return None
    expected = dest_dir / (src.stem + ".pdf")
    return expected if expected.exists() else None


def main():
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    PDFS_DIR.mkdir(parents=True, exist_ok=True)

    url = f"{CANVAS_API_URL}/api/v1/courses/{COURSE_ID}/assignments/{ASSIGNMENT_ID}/submissions"
    subs = list(paginated(url, params={"include[]": ["user"]}))
    print(f"Fetched {len(subs)} submission records")

    rows = []
    for s in subs:
        user = s.get("user") or {}
        name = user.get("sort_name") or user.get("name") or f"user-{s.get('user_id')}"
        student_slug = slug(name)
        row = {
            "student": name,
            "slug": student_slug,
            "user_id": s.get("user_id"),
            "email": user.get("login_id") or "",
            "submitted_at": s.get("submitted_at") or "",
            "late": bool(s.get("late")),
            "missing": bool(s.get("missing")),
            "workflow_state": s.get("workflow_state"),
            "original_format": "",
            "pdf_path": "",
            "notes": "",
        }

        attachments = s.get("attachments") or []
        if not attachments:
            row["notes"] = "no attachment"
            rows.append(row)
            continue

        # Take the first attachment (students rarely submit multiple for this assignment).
        att = attachments[0]
        ext = Path(att["filename"]).suffix.lower().lstrip(".")
        row["original_format"] = ext
        if len(attachments) > 1:
            row["notes"] = f"{len(attachments)} attachments; using first"

        src_path = SUBMISSIONS_DIR / f"{student_slug}.{ext}"
        if not src_path.exists():
            print(f"  downloading {student_slug}.{ext}")
            r = requests.get(att["url"], headers=HEADERS)
            r.raise_for_status()
            src_path.write_bytes(r.content)

        if ext == "pdf":
            pdf_path = PDFS_DIR / f"{student_slug}.pdf"
            if not pdf_path.exists():
                pdf_path.write_bytes(src_path.read_bytes())
            row["pdf_path"] = str(pdf_path)
        elif ext in ("pptx", "ppt", "key"):
            pdf_path = PDFS_DIR / f"{student_slug}.pdf"
            if not pdf_path.exists():
                print(f"  converting {student_slug}.{ext} -> pdf")
                out = convert_to_pdf(src_path, PDFS_DIR)
                if out is None:
                    row["notes"] = (row["notes"] + "; " if row["notes"] else "") + "conversion failed"
                else:
                    row["pdf_path"] = str(out)
            else:
                row["pdf_path"] = str(pdf_path)
        else:
            row["notes"] = (row["notes"] + "; " if row["notes"] else "") + f"unsupported format: {ext}"

        rows.append(row)

    rows.sort(key=lambda r: r["slug"])
    with MANIFEST.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    with_pdf = sum(1 for r in rows if r["pdf_path"])
    missing = sum(1 for r in rows if r["missing"])
    late = sum(1 for r in rows if r["late"])
    failed = sum(1 for r in rows if "failed" in r["notes"] or "no attachment" in r["notes"])
    print()
    print(f"Manifest: {MANIFEST}")
    print(f"  {with_pdf}/{total} students have a gradable PDF")
    print(f"  {late} late, {missing} missing, {failed} with issues")


if __name__ == "__main__":
    main()
