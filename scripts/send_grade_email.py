#!/usr/bin/env python3
"""Send a grade PDF via Resend. Usage: send_grade_email.py <pdf_path> <to_email> [--student "Name"]"""
import argparse
import base64
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env.local")

API_KEY = os.environ["RESEND_API_KEY"]
FROM_ADDR = os.environ.get("GRADE_FROM", "STRAT 325 <grades@strategy.byu.edu>")


def send(pdf_path: Path, to_email: str, student_name: str | None = None) -> dict:
    student = student_name or pdf_path.stem.replace("-", " ").title()
    with pdf_path.open("rb") as fh:
        encoded = base64.b64encode(fh.read()).decode()

    subject = "STRAT 325 Capstone Deck: grade and feedback"
    body_html = f"""
    <p>Hi {student.split()[0]},</p>
    <p>Attached is your graded Capstone Deck assessment. It includes your scores across the four rubric dimensions (Storyline, Insight, Evidence, Design), specific justifications tied to slides in your deck, and an appendix listing every pattern I check for when grading.</p>
    <p>If anything is unclear or you'd like to discuss, reply to this email or stop by office hours.</p>
    <p>Nice work this semester,<br>Prof. Murff</p>
    """

    payload = {
        "from": FROM_ADDR,
        "to": [to_email],
        "subject": subject,
        "html": body_html,
        "attachments": [{"filename": pdf_path.name, "content": encoded}],
    }
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("to")
    ap.add_argument("--student", default=None)
    args = ap.parse_args()
    result = send(Path(args.pdf), args.to, args.student)
    print(result)


if __name__ == "__main__":
    main()
