"""Walk graded markdown files and emit grades/_results.csv.

Parses:
  grades/[slug].md                 -- student-facing grade
  grades/_calibration/[slug].md    -- per-agent McKinsey calibration run
  grades/_professor/[slug].md      -- professor-only notes (for a boolean flag)
  grades/_manifest.csv             -- canvas user ids, email, submission status

Emits: grades/_results.csv
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path("grades")
STUDENT_DIR = ROOT
CALIB_DIR = ROOT / "_calibration"
PROF_DIR = ROOT / "_professor"
MANIFEST = ROOT / "_manifest.csv"
RESULTS = ROOT / "_results.csv"


def parse_grade_file(path: Path) -> dict:
    """Extract structured fields from a grade markdown file."""
    text = path.read_text()
    out: dict = {}

    company = re.search(r"\*\*Company:\*\*\s*(.+)", text)
    out["company"] = company.group(1).strip() if company else ""

    def score(dim: str) -> int | None:
        m = re.search(rf"###\s*\d+\.\s*{dim}:\s*(\d)\s*/\s*7", text)
        return int(m.group(1)) if m else None

    out["storyline"] = score("Storyline")
    out["insight"] = score("Insight")
    out["evidence"] = score("Evidence")
    out["design"] = score("Slide Design")

    final = re.search(r"Deck Quality Score:\*{0,2}\s*(\d+(?:\.\d+)?)", text)
    if final:
        out["final_score"] = round(float(final.group(1)))
    else:
        out["final_score"] = None

    # Gate status (plain-language student files use "passed" / "not met" / describe the miss).
    src_line = re.search(r"Source Quality Gate:\s*([^\n]+)", text, re.IGNORECASE)
    cr_line = re.search(r"Client-Readiness Gate:\s*([^\n]+)", text, re.IGNORECASE)
    out["source_gate_passed"] = bool(src_line and "pass" in src_line.group(1).lower())
    out["client_readiness_gate_passed"] = bool(cr_line and "pass" in cr_line.group(1).lower())

    # Pressure-test status
    pt = re.search(r"Did the deck address it\?\*{0,2}\s*([A-Z\s]+?)(?:[.—\-]|$)", text)
    if not pt:
        pt = re.search(r"Pressure-test[^\n]*?\b(HOLDS UP|PARTIAL|UNADDRESSED|WEAK)\b", text, re.IGNORECASE)
    out["pressure_test"] = pt.group(1).strip().upper() if pt else ""

    # Biggest opportunity — first line after that heading
    bo = re.search(r"\*\*Biggest opportunity:?\*\*\s*(.+)", text)
    out["biggest_opportunity"] = bo.group(1).strip()[:300] if bo else ""

    return out


def calibration_score(slug: str) -> int | None:
    """Parse the McKinsey calibration run for this agent (expected 100)."""
    path = CALIB_DIR / f"{slug}.md"
    if not path.exists():
        return None
    text = path.read_text()
    m = re.search(r"Deck Quality Score:\*{0,2}\s*(\d+(?:\.\d+)?)", text)
    return round(float(m.group(1))) if m else None


def has_professor_notes(slug: str) -> bool:
    path = PROF_DIR / f"{slug}.md"
    if not path.exists():
        return False
    body = path.read_text().strip().lower()
    # Empty or "no concerns" → no meaningful notes
    return "no integrity or calibration concerns" not in body and len(body) > 80


def main() -> None:
    manifest = {r["slug"]: r for r in csv.DictReader(open(MANIFEST))}

    rows = []
    for md in sorted(STUDENT_DIR.glob("*.md")):
        slug = md.stem
        if slug not in manifest:
            continue  # skip stray files
        m = manifest[slug]
        parsed = parse_grade_file(md)
        calib = calibration_score(slug)
        rows.append({
            "slug": slug,
            "student_name": m["student"],
            "canvas_user_id": m["user_id"],
            "email": m["email"],
            "company": parsed["company"],
            "submitted_at": m["submitted_at"],
            "late": m["late"],
            "calibration_mckinsey_score": calib if calib is not None else "",
            "calibration_deviation": (calib - 100) if calib is not None else "",
            "storyline": parsed["storyline"] or "",
            "insight": parsed["insight"] or "",
            "evidence": parsed["evidence"] or "",
            "design": parsed["design"] or "",
            "final_score_100": parsed["final_score"] if parsed["final_score"] is not None else "",
            "source_gate_passed": parsed["source_gate_passed"],
            "client_readiness_gate_passed": parsed["client_readiness_gate_passed"],
            "pressure_test": parsed["pressure_test"],
            "professor_notes": has_professor_notes(slug),
            "biggest_opportunity": parsed["biggest_opportunity"],
            "report_path": str(md),
        })

    rows.sort(key=lambda r: (-(r["final_score_100"] or 0), r["slug"]))

    with RESULTS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {RESULTS} with {len(rows)} graded students")
    print(f"\nScore distribution:")
    scores = [r["final_score_100"] for r in rows if r["final_score_100"]]
    if scores:
        print(f"  min={min(scores)} median={sorted(scores)[len(scores)//2]} max={max(scores)}")
    calibs = [r["calibration_mckinsey_score"] for r in rows if r["calibration_mckinsey_score"]]
    if calibs:
        print(f"\nCalibration McKinsey scores (should all be 100):")
        print(f"  min={min(calibs)} median={sorted(calibs)[len(calibs)//2]} max={max(calibs)}")
        off = [c for c in calibs if c != 100]
        if off:
            print(f"  WARNING: {len(off)} agent(s) deviated from 100: {off}")


if __name__ == "__main__":
    main()
