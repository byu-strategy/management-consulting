#!/usr/bin/env python3
"""Batch-send capstone grade PDFs via Resend.

Fetches student emails from Canvas (by user_id from the manifest), matches each
to the correct PDF in grades/pdf/, and sends via Resend.

Usage:
  python3 scripts/send_capstone_grades.py --dry-run
  python3 scripts/send_capstone_grades.py --send
"""
import argparse
import base64
import csv
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env.local")

CANVAS_URL = os.environ["CANVAS_API_URL"].rstrip("/")
CANVAS_TOKEN = os.environ["CANVAS_API_TOKEN"]
COURSE_ID = 34877
RESEND_KEY = os.environ["RESEND_API_KEY"]
FROM_ADDR = "STRAT 325 <scott.murff@strategy.byu.edu>"
REPLY_TO = os.environ.get("GRADE_REPLY_TO", "scott.murff@byu.edu")

MANIFEST = REPO_ROOT / "grades" / "_manifest.csv"
PDF_DIR = REPO_ROOT / "grades" / "pdf"

SUBJECT = "STRAT 325 Capstone Deck: grade and feedback"

BODY_TEMPLATE = """<p>Hi {first_name},</p>

<p>Your final capstone deck has been graded and is attached to this email with a detailed report, and your grades on Canvas are in "final draft" form. Please let me know if you see anything incorrect.</p>

<p>My philosophy with grading this deck is to hold a firm bar for what a top-tier professional deck would be expected to be. As such, the scoring may appear harsh, however I designed the grading in this course in such a way that this will not torpedo your grade.</p>

<p>Hence, I think this report will be the most valuable thing you take away from this class, giving you a very unvarnished look at what details to pay attention to as you work on decks in the future.</p>

<p>Grading was done systematically by Claude Code Opus 4.7 after I spent ~10 hours building a Claude Code Skill to very thoroughly analyze every aspect of your deck. You can see in your report an appendix containing the specific things I was looking for and that affected your score. I built the skill based on detailed review of actual decks and iterated on it to make sure that the Skill was giving relatively good answers. The skill is not perfect, but I actually think it is doing a better job in many ways than a human would to give you an unbiased assessment. And the same Skill was applied to all decks in the class, again reducing human bias.</p>

<p>Thank you for going on this journey with me this semester, and I wish you all the best in your future endeavors! Please keep me posted as you land consulting or other opportunities you are excited about.</p>

<p>All my best,<br>Scott</p>

<p>PS. A couple of the main things you will see in how the Skill works is that I flagged what I would call "AI-smells," which are writing artifacts that LLMs commonly produce and a human would rarely if ever use. Leaving these things un-edited sends the message that the writing was not carefully read and stamped as valid by a human.</p>

<p>I also flagged what I would call "scaffolding." Think of the scaffolding around a building during construction: it's important and useful when building the structure, but you take the scaffolding off of the final product. Examples of scaffolding are things like explicitly stating on your slides the words "situation," "complication," etc. Many consulting frameworks should be viewed as scaffolding: they're certainly helpful and sometimes essential, however you generally don't telegraph them to your audience; rather, let the argument speak for itself.</p>
"""


def canvas_get(path: str, params: dict | None = None) -> dict:
    r = requests.get(
        f"{CANVAS_URL}/api/v1{path}",
        headers={"Authorization": f"Bearer {CANVAS_TOKEN}"},
        params=params or {},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def fetch_user_emails(user_ids: list[str]) -> dict[str, tuple[str, str]]:
    """Return {user_id: (email, name)}."""
    result: dict[str, tuple[str, str]] = {}
    for uid in user_ids:
        try:
            data = canvas_get(f"/users/{uid}/profile")
            email = data.get("primary_email") or data.get("login_id") or ""
            name = data.get("name") or ""
            result[str(uid)] = (email, name)
        except Exception as e:
            print(f"  ERROR fetching user {uid}: {e}", file=sys.stderr)
            result[str(uid)] = ("", "")
    return result


def load_manifest() -> list[dict]:
    rows = []
    with MANIFEST.open() as fh:
        for row in csv.DictReader(fh):
            if row["slug"] == "test-student":
                continue
            pdf = PDF_DIR / f"{row['slug']}.pdf"
            if not pdf.exists():
                print(f"  WARNING: no PDF for {row['slug']}", file=sys.stderr)
                continue
            row["pdf_path"] = pdf
            rows.append(row)
    return rows


def send_one(to_email: str, first_name: str, pdf_path: Path) -> dict:
    with pdf_path.open("rb") as fh:
        encoded = base64.b64encode(fh.read()).decode()
    payload = {
        "from": FROM_ADDR,
        "to": [to_email],
        "reply_to": REPLY_TO,
        "subject": SUBJECT,
        "html": BODY_TEMPLATE.format(first_name=first_name),
        "attachments": [{"filename": pdf_path.name, "content": encoded}],
    }
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--send", action="store_true")
    ap.add_argument("--only", help="Only send to this user_id (useful for testing)")
    args = ap.parse_args()

    manifest = load_manifest()
    if args.only:
        manifest = [r for r in manifest if r["user_id"] == args.only]

    print(f"Loaded {len(manifest)} student(s) with matched PDFs.")
    print(f"Fetching Canvas emails...")
    emails = fetch_user_emails([r["user_id"] for r in manifest])

    missing = [r["student"] for r in manifest if not emails.get(r["user_id"], ("", ""))[0]]
    if missing:
        print(f"\nWARNING: {len(missing)} student(s) missing email:", file=sys.stderr)
        for n in missing:
            print(f"  - {n}", file=sys.stderr)

    print(f"\n{'='*80}")
    print(f"Plan ({'DRY RUN' if args.dry_run else 'LIVE SEND'})")
    print(f"From: {FROM_ADDR}")
    print(f"Reply-to: {REPLY_TO}")
    print(f"Subject: {SUBJECT}")
    print(f"{'='*80}\n")

    for row in manifest:
        uid = row["user_id"]
        email, canvas_name = emails.get(uid, ("", ""))
        first_name = row["student"].split()[0]
        pdf = row["pdf_path"]
        line = f"  {row['student']:40s} → {email:40s} [{pdf.name}]"
        if not email:
            print(f"SKIP {line} (no email)")
            continue
        if args.dry_run:
            print(f"DRY  {line}")
        else:
            try:
                res = send_one(email, first_name, pdf)
                print(f"SENT {line}  id={res.get('id', '?')}")
                time.sleep(0.5)  # gentle rate limit
            except Exception as e:
                print(f"FAIL {line}  error={e}", file=sys.stderr)


if __name__ == "__main__":
    main()
