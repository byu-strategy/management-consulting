#!/usr/bin/env python3
"""
Generate a Canvas-compatible IMS Common Cartridge (.imscc) file from 00-schedule.qmd.

Workflow:
  1. Edit your course website (00-schedule.qmd, chapter files, etc.)
  2. Run: python3 scripts/generate_imscc.py
  3. Upload strat325-schedule.imscc to Learning Suite

Learning Suite only supports two CC activity types:
  - ExternalUrl (web links) → these import successfully
  - ContextModuleSubHeader → section dividers within modules

Everything is modeled as web links pointing to the published course website.
"""

import zipfile
import re
import os
import hashlib

# ── Configuration ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SCHEDULE_FILE = os.path.join(PROJECT_DIR, "00-schedule.qmd")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "strat325-schedule.imscc")

BASE_URL = "https://byu-strategy.github.io/management-consulting"
ASSESSMENTS_URL = f"{BASE_URL}/00-assessments.html"
COURSE_TITLE = "STRAT 325 - Intro to Management Consulting"
COURSE_CODE = "STRAT325"
YEAR = 2026


# ── Assessment Data ────────────────────────────────────────────────────────

ASSIGNMENT_GROUPS = [
    {"id": "reading_quizzes", "title": "Reading Quizzes", "weight": 10.0, "position": 1},
    {"id": "resume_networking", "title": "Resume and Networking", "weight": 12.0, "position": 2},
    {"id": "practice_interviews", "title": "Practice Interviews", "weight": 42.0, "position": 3},
    {"id": "client_work", "title": "Client Work", "weight": 36.0, "position": 4},
    {"id": "surveys_bonus", "title": "Surveys (Bonus)", "weight": 0.0, "position": 5},
]

# Each assessment with a URL pointing to the relevant section on the course website
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
     "due": "2026-03-12", "week": 10, "anchor": "#reading-quizzes"},
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


# ── Helpers ────────────────────────────────────────────────────────────────

def make_id(seed):
    return "i" + hashlib.md5(seed.encode()).hexdigest()


def xml_escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


# ── Parse the schedule QMD ─────────────────────────────────────────────────

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
    guest = None

    guest_match = re.search(
        r"\*\*Guest:\s*\[([^\]]+)\]\(([^)]+)\)\s*\(([^)]+)\)\*\*", topic_raw
    )
    if guest_match:
        guest = f"{guest_match.group(1)} ({guest_match.group(3)})"

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
        "topic": topic_text, "links": links, "guest": guest,
        "assessments": assessments, "interviews": interviews,
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


# ── Build CC files ─────────────────────────────────────────────────────────
# Learning Suite only imports ExternalUrl and ContextModuleSubHeader.
# Everything is a web link pointing to the published course website.

def build_weblink_xml(title, url):
    """IMS CC web link resource file."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<webLink xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imswl_v1p1"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imswl_v1p1'
        ' http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imswl_v1p1.xsd">\n'
        f"  <title>{xml_escape(title)}</title>\n"
        f'  <url href="{xml_escape(url)}"/>\n'
        "</webLink>"
    )


def build_canvas_export_txt():
    return "created by STRAT 325 schedule generator\nversion=1.1\n"


def build_course_settings_xml():
    course_id = make_id("strat325_course")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<course identifier="{course_id}"'
        ' xmlns="http://canvas.instructure.com/xsd/cccv1p0"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0'
        ' https://canvas.instructure.com/xsd/cccv1p0.xsd">\n'
        f"  <title>{xml_escape(COURSE_TITLE)}</title>\n"
        f"  <course_code>{xml_escape(COURSE_CODE)}</course_code>\n"
        "  <default_view>modules</default_view>\n"
        "  <license>private</license>\n"
        "</course>"
    )


def build_assignment_groups_xml():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<assignmentGroups xmlns="http://canvas.instructure.com/xsd/cccv1p0"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0'
        ' https://canvas.instructure.com/xsd/cccv1p0.xsd">',
    ]
    for g in ASSIGNMENT_GROUPS:
        gid = make_id(f"group_{g['id']}")
        lines.append(f'  <assignmentGroup identifier="{gid}">')
        lines.append(f"    <title>{xml_escape(g['title'])}</title>")
        lines.append(f"    <position>{g['position']}</position>")
        lines.append(f"    <group_weight>{g['weight']}</group_weight>")
        lines.append("  </assignmentGroup>")
    lines.append("</assignmentGroups>")
    return "\n".join(lines)


def get_assessment_url(assessment):
    """Build URL pointing to the relevant section on the assessments page."""
    return ASSESSMENTS_URL + assessment.get("anchor", "")


def build_module_meta_xml(weeks_data, phases, assessments_by_week):
    """Build module_meta.xml — only ExternalUrl and SubHeader types."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<modules xmlns="http://canvas.instructure.com/xsd/cccv1p0"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        ' xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0'
        ' https://canvas.instructure.com/xsd/cccv1p0.xsd">',
    ]

    for week_num, sessions in sorted(weeks_data.items()):
        phase = get_phase_for_week(week_num, phases)
        module_id = make_id(f"week_{week_num}")

        lines.append(f'  <module identifier="{module_id}">')
        lines.append(f"    <title>Week {week_num}: {xml_escape(phase)}</title>")
        lines.append("    <workflow_state>active</workflow_state>")
        lines.append(f"    <position>{week_num}</position>")
        lines.append("    <require_sequential_progress>false</require_sequential_progress>")
        lines.append("    <locked>false</locked>")
        lines.append("    <items>")

        pos = 1

        for s in sessions:
            # Session header (sub-header)
            item_id = make_id(f"session_{s['num']}_header")
            title = f"{s['date']} \u2014 {s['topic']}"
            if s.get("guest"):
                title += f" (Guest: {s['guest']})"
            lines.append(f'      <item identifier="{item_id}">')
            lines.append("        <content_type>ContextModuleSubHeader</content_type>")
            lines.append("        <workflow_state>active</workflow_state>")
            lines.append(f"        <title>{xml_escape(title)}</title>")
            lines.append(f"        <position>{pos}</position>")
            lines.append("        <new_tab/>")
            lines.append("        <indent>0</indent>")
            lines.append("      </item>")
            pos += 1

            # Reading links (ExternalUrl)
            for i, (text, page, anchor) in enumerate(s["links"]):
                url = f"{BASE_URL}/{page}"
                if anchor:
                    url += anchor
                link_item_id = make_id(f"link_s{s['num']}_{i}_item")
                lines.append(f'      <item identifier="{link_item_id}">')
                lines.append("        <content_type>ExternalUrl</content_type>")
                lines.append("        <workflow_state>active</workflow_state>")
                lines.append(f"        <title>{xml_escape(text)}</title>")
                lines.append(f"        <identifierref>{link_item_id}</identifierref>")
                lines.append(f"        <url>{xml_escape(url)}</url>")
                lines.append(f"        <position>{pos}</position>")
                lines.append("        <new_tab>true</new_tab>")
                lines.append("        <indent>1</indent>")
                lines.append("      </item>")
                pos += 1

        # Assessments due this week (as ExternalUrl items)
        week_assessments = assessments_by_week.get(week_num, [])
        if week_assessments:
            assess_header_id = make_id(f"week_{week_num}_assess_header")
            lines.append(f'      <item identifier="{assess_header_id}">')
            lines.append("        <content_type>ContextModuleSubHeader</content_type>")
            lines.append("        <workflow_state>active</workflow_state>")
            lines.append("        <title>Due This Week</title>")
            lines.append(f"        <position>{pos}</position>")
            lines.append("        <new_tab/>")
            lines.append("        <indent>0</indent>")
            lines.append("      </item>")
            pos += 1

            for a in week_assessments:
                a_item_id = make_id(f"assess_{a['id']}_item")
                a_url = get_assessment_url(a)
                a_title = f"{a['title']} ({a['points']} pts \u2014 due {a['due']})"
                lines.append(f'      <item identifier="{a_item_id}">')
                lines.append("        <content_type>ExternalUrl</content_type>")
                lines.append("        <workflow_state>active</workflow_state>")
                lines.append(f"        <title>{xml_escape(a_title)}</title>")
                lines.append(f"        <identifierref>{a_item_id}</identifierref>")
                lines.append(f"        <url>{xml_escape(a_url)}</url>")
                lines.append(f"        <position>{pos}</position>")
                lines.append("        <new_tab>true</new_tab>")
                lines.append("        <indent>1</indent>")
                lines.append("      </item>")
                pos += 1

        lines.append("    </items>")
        lines.append("  </module>")

    lines.append("</modules>")
    return "\n".join(lines)


def build_manifest(weeks_data, phases, assessments_by_week):
    """Build imsmanifest.xml — CC 1.1, all items as web links."""
    ns = (
        'xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" '
        'xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" '
        'xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="'
        "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 "
        "http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd "
        "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource "
        "http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd "
        "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest "
        'http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd"'
    )

    manifest_id = make_id("strat325_manifest")
    course_settings_id = make_id("strat325_course_settings")

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<manifest identifier="{manifest_id}" {ns}>')

    # Metadata
    lines.append("  <metadata>")
    lines.append("    <schema>IMS Common Cartridge</schema>")
    lines.append("    <schemaversion>1.1.0</schemaversion>")
    lines.append("    <lomimscc:lom>")
    lines.append("      <lomimscc:general>")
    lines.append("        <lomimscc:title>")
    lines.append(f"          <lomimscc:string>{xml_escape(COURSE_TITLE)}</lomimscc:string>")
    lines.append("        </lomimscc:title>")
    lines.append("      </lomimscc:general>")
    lines.append("    </lomimscc:lom>")
    lines.append("  </metadata>")

    # Organizations
    lines.append("  <organizations>")
    lines.append('    <organization identifier="org_1" structure="rooted-hierarchy">')
    lines.append('      <item identifier="LearningModules">')

    resource_entries = []

    for week_num, sessions in sorted(weeks_data.items()):
        phase = get_phase_for_week(week_num, phases)
        module_id = make_id(f"week_{week_num}")

        lines.append(f'        <item identifier="{module_id}">')
        lines.append(f"          <title>Week {week_num}: {xml_escape(phase)}</title>")

        for s in sessions:
            # Session sub-header (no identifierref)
            header_id = make_id(f"session_{s['num']}_header")
            title = f"{s['date']} \u2014 {s['topic']}"
            if s.get("guest"):
                title += f" (Guest: {s['guest']})"
            lines.append(f'          <item identifier="{header_id}">')
            lines.append(f"            <title>{xml_escape(title)}</title>")
            lines.append("          </item>")

            # Reading links (web link resources)
            for i, (text, page, anchor) in enumerate(s["links"]):
                url = f"{BASE_URL}/{page}"
                if anchor:
                    url += anchor
                link_res_id = make_id(f"link_s{s['num']}_{i}_res")
                link_item_id = make_id(f"link_s{s['num']}_{i}_item")
                link_file = f"links/link_s{s['num']:02d}_{i}.xml"

                lines.append(f'          <item identifier="{link_item_id}" identifierref="{link_res_id}">')
                lines.append(f"            <title>{xml_escape(text)}</title>")
                lines.append("          </item>")

                resource_entries.append(
                    f'    <resource identifier="{link_res_id}" type="imswl_xmlv1p1">\n'
                    f'      <file href="{link_file}"/>\n'
                    f"    </resource>"
                )

        # Assessment links for this week
        week_assessments = assessments_by_week.get(week_num, [])
        if week_assessments:
            assess_header_id = make_id(f"week_{week_num}_assess_header")
            lines.append(f'          <item identifier="{assess_header_id}">')
            lines.append("            <title>Due This Week</title>")
            lines.append("          </item>")

            for a in week_assessments:
                a_item_id = make_id(f"assess_{a['id']}_item")
                a_res_id = make_id(f"assess_{a['id']}_res")
                a_file = f"links/assess_{a['id']}.xml"
                a_title = f"{a['title']} ({a['points']} pts \u2014 due {a['due']})"

                lines.append(f'          <item identifier="{a_item_id}" identifierref="{a_res_id}">')
                lines.append(f"            <title>{xml_escape(a_title)}</title>")
                lines.append("          </item>")

                resource_entries.append(
                    f'    <resource identifier="{a_res_id}" type="imswl_xmlv1p1">\n'
                    f'      <file href="{a_file}"/>\n'
                    f"    </resource>"
                )

        lines.append("        </item>")

    lines.append("      </item>")
    lines.append("    </organization>")
    lines.append("  </organizations>")

    # Resources
    lines.append("  <resources>")
    lines.append(f'    <resource identifier="{course_settings_id}"'
                 ' type="associatedcontent/imscc_xmlv1p1/learning-application-resource"'
                 ' href="course_settings/canvas_export.txt">')
    lines.append('      <file href="course_settings/canvas_export.txt"/>')
    lines.append('      <file href="course_settings/course_settings.xml"/>')
    lines.append('      <file href="course_settings/module_meta.xml"/>')
    lines.append('      <file href="course_settings/assignment_groups.xml"/>')
    lines.append("    </resource>")
    for entry in resource_entries:
        lines.append(entry)
    lines.append("  </resources>")

    lines.append("</manifest>")
    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print(f"Parsing: {SCHEDULE_FILE}")
    sessions, phases = parse_schedule(SCHEDULE_FILE)
    print(f"  Found {len(sessions)} sessions, {len(phases)} phases")

    total_links = sum(len(s["links"]) for s in sessions)
    print(f"  Found {total_links} reading links")
    print(f"  Defined {len(ASSESSMENTS)} assessments in {len(ASSIGNMENT_GROUPS)} groups")

    total_points = sum(a["points"] for a in ASSESSMENTS if a["group"] != "surveys_bonus")
    bonus_points = sum(a["points"] for a in ASSESSMENTS if a["group"] == "surveys_bonus")
    print(f"  Total points: {total_points} + {bonus_points} bonus")

    # Group by week
    weeks = {}
    for s in sessions:
        weeks.setdefault(s["week"], []).append(s)

    assessments_by_week = {}
    for a in ASSESSMENTS:
        assessments_by_week.setdefault(a["week"], []).append(a)

    # Build .imscc
    with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("imsmanifest.xml", build_manifest(weeks, phases, assessments_by_week))
        zf.writestr("course_settings/canvas_export.txt", build_canvas_export_txt())
        zf.writestr("course_settings/course_settings.xml", build_course_settings_xml())
        zf.writestr("course_settings/module_meta.xml",
                     build_module_meta_xml(weeks, phases, assessments_by_week))
        zf.writestr("course_settings/assignment_groups.xml", build_assignment_groups_xml())

        # Reading link XML files
        for s in sessions:
            for i, (text, page, anchor) in enumerate(s["links"]):
                url = f"{BASE_URL}/{page}"
                if anchor:
                    url += anchor
                zf.writestr(f"links/link_s{s['num']:02d}_{i}.xml",
                            build_weblink_xml(text, url))

        # Assessment link XML files
        for a in ASSESSMENTS:
            a_url = get_assessment_url(a)
            a_title = f"{a['title']} ({a['points']} pts)"
            zf.writestr(f"links/assess_{a['id']}.xml",
                        build_weblink_xml(a_title, a_url))

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"\nCreated: {OUTPUT_FILE} ({size_kb:.1f} KB)")

    # Count total items that will import
    total_items = total_links + len(ASSESSMENTS)
    print(f"  {total_links} reading links + {len(ASSESSMENTS)} assessments = {total_items} web link items")
    print(f"  {len(sessions)} session headers + {len(assessments_by_week)} 'Due This Week' headers")
    print(f"  15 weekly modules")


if __name__ == "__main__":
    main()
