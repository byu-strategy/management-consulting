#!/usr/bin/env python3
"""
Course architecture audit script.

Checks for common issues that cause divergence between the repo and Canvas:
  1. Broken cross-references (links to anchors that don't exist)
  2. Temporal content on the website (week refs, due dates in published files)
  3. Schedule/assessments drift (assignment names that don't match)
  4. Stale LMS references (LearningSuite instead of Canvas)

Usage:
    python3 scripts/audit_course.py              # full audit
    python3 scripts/audit_course.py index.qmd    # audit specific file(s)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent

# Files published on the website (temporal content not allowed)
PUBLISHED_FILES = [
    "index.qmd",
    "00-assessments.qmd",
    "01-what-is-consulting.qmd",
    "02-consultants-os.qmd",
    "03-leveraging-ai.qmd",
    "04-working-as-a-team.qmd",
    "05-think-clearly.qmd",
    "06-get-right-answer.qmd",
    "07-move-work-forward.qmd",
    "08-create-impact.qmd",
    "95-antigravity-reference.qmd",
    "96-firms-guide.qmd",
    "97-ta-handbook.qmd",
    "98-resources.qmd",
    "99-references.qmd",
]

# ── Helpers ──────────────────────────────────────────────────────────

class Issue:
    def __init__(self, file: str, line: int, category: str, message: str):
        self.file = file
        self.line = line
        self.category = category
        self.message = message

    def __str__(self):
        return f"  {self.file}:{self.line}  [{self.category}] {self.message}"


def read_file(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def slugify(text: str) -> str:
    """Convert heading text to Quarto's auto-generated anchor ID."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)   # remove non-word chars except hyphens
    text = re.sub(r"[\s_]+", "-", text)     # spaces/underscores to hyphens
    text = re.sub(r"-+", "-", text)         # collapse multiple hyphens
    return text.strip("-")


def collect_anchors(path: Path) -> set[str]:
    """Extract all anchor IDs defined in a .qmd file (explicit + auto-generated)."""
    anchors = set()
    for line in read_file(path):
        # Explicit Quarto-style: {#anchor-id} or {#os-1-4}
        for m in re.finditer(r"\{#([^}\s]+)", line):
            anchors.add(m.group(1))
        # Auto-generated from headings: ## My Heading → #my-heading
        heading_match = re.match(r"^#{1,6}\s+(.+?)(?:\s*\{[^}]*\})?\s*$", line)
        if heading_match:
            heading_text = heading_match.group(1)
            # Only add auto-generated if no explicit anchor on this heading
            if "{#" not in line:
                anchors.add(slugify(heading_text))
    return anchors


# ── Check 1: Broken cross-references ────────────────────────────────

def check_broken_links(files: list[Path]) -> list[Issue]:
    """Find links to .qmd#anchor where the anchor doesn't exist."""
    issues = []
    anchor_cache: dict[str, set[str]] = {}

    for fpath in files:
        lines = read_file(fpath)
        for i, line in enumerate(lines, 1):
            # Match [text](file.qmd#anchor) patterns
            for m in re.finditer(r"\[([^\]]*)\]\(([^)]+\.qmd)#([^)]+)\)", line):
                link_text, target_file, anchor = m.group(1), m.group(2), m.group(3)
                target_path = REPO / target_file

                if not target_path.exists():
                    issues.append(Issue(
                        fpath.name, i, "broken-link",
                        f"Target file not found: {target_file}"
                    ))
                    continue

                if target_file not in anchor_cache:
                    anchor_cache[target_file] = collect_anchors(target_path)

                if anchor not in anchor_cache[target_file]:
                    issues.append(Issue(
                        fpath.name, i, "broken-anchor",
                        f"Anchor #{anchor} not found in {target_file}"
                    ))

    return issues


# ── Check 2: Temporal content on published pages ────────────────────

# Patterns that indicate temporal/operational content
TEMPORAL_PATTERNS = [
    (r"\bWeek\s+\d+\b", "Week reference"),
    (r"\b(?:Due|due):\s*Week\s+\d+", "Due date with week"),
    (r"\bWeeks?\s+\d+[-–]\d+\b", "Week range"),
    (r"\(Week\s+\d+\)", "Parenthetical week reference"),
    (r"\bJanuary\s+\d+|February\s+\d+|March\s+\d+|April\s+\d+", "Specific date"),
]

# Lines that are OK even if they match (context-dependent exceptions)
TEMPORAL_EXCEPTIONS = [
    r"no quizzes on weeks when",       # generic policy, not a specific week
    r"throughout the semester",         # generic timeframe
    r"10 quizzes throughout",           # generic count
    r"15 weeks",                        # semester length description (index.qmd marketing)
    r"\*Week \d",                       # illustrative workplan examples (e.g., *Week 1: Task*)
    r"- Week \d+-?\d*:",                # bullet-point workplan examples (e.g., - Week 1-2: [task])
    r"Last updated",                    # metadata timestamps are fine
    r"Starting in Week",               # chapter intro framing (pedagogical, not operational)
    r"By the end of Week",             # learning objective framing
]


def check_temporal_content(files: list[Path]) -> list[Issue]:
    """Flag week references and due dates in published website files."""
    issues = []
    published = {f for f in PUBLISHED_FILES}

    for fpath in files:
        if fpath.name not in published:
            continue

        lines = read_file(fpath)
        for i, line in enumerate(lines, 1):
            # Skip YAML frontmatter
            if i <= 10 and (line.startswith("---") or line.startswith("title:") or
                           line.startswith("date:") or line.startswith("author:") or
                           line.startswith("format:") or line.startswith("editor:")):
                continue

            # Check exceptions
            if any(re.search(exc, line, re.IGNORECASE) for exc in TEMPORAL_EXCEPTIONS):
                continue

            for pattern, label in TEMPORAL_PATTERNS:
                if re.search(pattern, line):
                    issues.append(Issue(
                        fpath.name, i, "temporal",
                        f"{label}: {line.strip()[:80]}"
                    ))
                    break  # one issue per line

    return issues


# ── Check 3: LMS reference check ────────────────────────────────────

def check_lms_references(files: list[Path]) -> list[Issue]:
    """Flag any remaining LearningSuite references."""
    issues = []
    for fpath in files:
        lines = read_file(fpath)
        for i, line in enumerate(lines, 1):
            if re.search(r"LearningSuite", line, re.IGNORECASE):
                issues.append(Issue(
                    fpath.name, i, "lms-ref",
                    f"LearningSuite reference (should be Canvas): {line.strip()[:80]}"
                ))
    return issues


# ── Check 4: Schedule/assessments name drift ────────────────────────

EXPECTED_ASSESSMENT_ANCHORS = {
    "reading-quizzes",
    "resume-and-networking",
    "practice-interviews",
    "intelligence-brief",
    "point-of-view",
    "conversation-deck",
}


def check_assessment_anchors() -> list[Issue]:
    """Verify expected assessment anchors exist in 00-assessments.qmd."""
    issues = []
    assessments_path = REPO / "00-assessments.qmd"
    if not assessments_path.exists():
        issues.append(Issue("00-assessments.qmd", 0, "missing-file",
                            "Assessment file not found"))
        return issues

    actual = collect_anchors(assessments_path)
    for expected in EXPECTED_ASSESSMENT_ANCHORS:
        if expected not in actual:
            issues.append(Issue(
                "00-assessments.qmd", 0, "missing-anchor",
                f"Expected anchor #{expected} not found"
            ))

    return issues


# ── Check 5: Schedule not in _quarto.yml chapters ───────────────────

def check_schedule_not_published() -> list[Issue]:
    """Verify 00-schedule.qmd is NOT in the published chapters list."""
    issues = []
    quarto_yml = REPO / "_quarto.yml"
    if not quarto_yml.exists():
        return issues

    content = quarto_yml.read_text(encoding="utf-8")
    if "00-schedule.qmd" in content:
        issues.append(Issue(
            "_quarto.yml", 0, "architecture",
            "00-schedule.qmd is in the published chapters — it should only feed Canvas"
        ))

    return issues


# ── Main ─────────────────────────────────────────────────────────────

def run_audit(target_files: Optional[list[Path]] = None) -> list[Issue]:
    if target_files is None:
        target_files = [REPO / f for f in PUBLISHED_FILES if (REPO / f).exists()]
        # Also check schedule for broken links
        schedule = REPO / "00-schedule.qmd"
        if schedule.exists():
            target_files.append(schedule)

    all_issues: list[Issue] = []
    all_issues.extend(check_broken_links(target_files))
    all_issues.extend(check_temporal_content(target_files))
    all_issues.extend(check_lms_references(target_files))
    all_issues.extend(check_assessment_anchors())
    all_issues.extend(check_schedule_not_published())

    return all_issues


def main():
    # Parse args: specific files or full audit
    if len(sys.argv) > 1:
        files = [REPO / f for f in sys.argv[1:]]
    else:
        files = None

    issues = run_audit(files)

    if not issues:
        print("Course audit: all checks passed")
        return 0

    # Group by category
    by_cat: dict[str, list[Issue]] = {}
    for issue in issues:
        by_cat.setdefault(issue.category, []).append(issue)

    print(f"Course audit: {len(issues)} issue(s) found\n")
    for cat, cat_issues in by_cat.items():
        print(f"[{cat}]")
        for issue in cat_issues:
            print(str(issue))
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
