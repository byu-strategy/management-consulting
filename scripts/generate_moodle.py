#!/usr/bin/env python3
"""
Generate a Moodle backup (.mbz) file with assignment shells from course data.

Workflow:
  1. Edit your course website (00-schedule.qmd, 00-assessments.qmd, etc.)
  2. Run: python3 scripts/generate_moodle.py
  3. Upload strat325-assignments.mbz to Learning Suite (Moodle import)

Creates gradeable assignment shells with:
  - Title, points, due dates
  - Grade categories (assignment groups) with weights
  - Organized into weekly sections
"""

import zipfile
import os
import time
from datetime import datetime, timezone, timedelta

# ── Configuration ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(PROJECT_DIR, "strat325-assignments.mbz")

COURSE_TITLE = "STRAT 325 - Intro to Management Consulting"
COURSE_SHORT = "STRAT325"
BASE_URL = "https://byu-strategy.github.io/management-consulting"
ASSESSMENTS_URL = f"{BASE_URL}/00-assessments.html"

# Mountain Time offset (UTC-7 for MDT)
MT_OFFSET = timedelta(hours=-7)
NOW_TS = int(time.time())

# Moodle backup version (4.1 LTS — widely compatible)
MOODLE_VERSION = "2022112800"
MOODLE_RELEASE = "4.1"
BACKUP_VERSION = "2022112800"
BACKUP_RELEASE = "4.1"

# Course start/end (Winter 2026)
COURSE_START = int(datetime(2026, 1, 5, 0, 0, 0, tzinfo=timezone(MT_OFFSET)).timestamp())
COURSE_END = int(datetime(2026, 4, 14, 23, 59, 59, tzinfo=timezone(MT_OFFSET)).timestamp())


# ── Assessment Data (shared with generate_imscc.py) ──────────────────────

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

def xml_escape(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def date_to_timestamp(date_str):
    """Convert 'YYYY-MM-DD' to Unix timestamp at 11:59 PM Mountain Time."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt = dt.replace(hour=23, minute=59, second=0, tzinfo=timezone(MT_OFFSET))
    return int(dt.timestamp())


def get_assessment_url(assessment):
    """Build URL pointing to the relevant section on the assessments page."""
    anchor = assessment.get("anchor", "")
    if anchor:
        return ASSESSMENTS_URL + anchor
    return ASSESSMENTS_URL


# ── ID management ─────────────────────────────────────────────────────────
# Moodle uses integer IDs that cross-reference between files.
# We assign them sequentially and track the mappings.

class IdManager:
    def __init__(self):
        self.next_id = 1
        # Maps: group_id_str -> grade_category_id (int)
        self.category_ids = {}
        # Maps: assessment index -> module_id (cm->id)
        self.module_ids = {}
        # Maps: assessment index -> activity_id (assign.id)
        self.activity_ids = {}
        # Maps: assessment index -> grade_item_id
        self.grade_item_ids = {}
        # Maps: assessment index -> context_id
        self.context_ids = {}
        # Maps: group_id_str -> category grade_item_id
        self.category_grade_item_ids = {}
        # Section IDs
        self.section_ids = {}
        # Course context
        self.course_id = None
        self.course_context_id = None
        self.root_category_id = None
        self.root_grade_item_id = None

    def next(self):
        val = self.next_id
        self.next_id += 1
        return val


def build_ids():
    """Pre-allocate all IDs for cross-referencing."""
    ids = IdManager()

    # Course
    ids.course_id = ids.next()
    ids.course_context_id = ids.next()

    # Root grade category
    ids.root_category_id = ids.next()
    ids.root_grade_item_id = ids.next()

    # Grade categories (one per assignment group)
    for g in ASSIGNMENT_GROUPS:
        ids.category_ids[g["id"]] = ids.next()
        ids.category_grade_item_ids[g["id"]] = ids.next()

    # Sections (section 0 = general, then sections 1-15 for weeks)
    for s in range(0, 16):
        ids.section_ids[s] = ids.next()

    # Activities
    for i, a in enumerate(ASSESSMENTS):
        ids.module_ids[i] = ids.next()
        ids.activity_ids[i] = ids.next()
        ids.grade_item_ids[i] = ids.next()
        ids.context_ids[i] = ids.next()

    return ids


# ── XML Builders ──────────────────────────────────────────────────────────

def build_moodle_backup_xml(ids):
    """Master manifest file."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<moodle_backup>',
        '  <information>',
        f'    <name>strat325-assignments.mbz</name>',
        f'    <moodle_version>{MOODLE_VERSION}</moodle_version>',
        f'    <moodle_release>{MOODLE_RELEASE}</moodle_release>',
        f'    <backup_version>{BACKUP_VERSION}</backup_version>',
        f'    <backup_release>{BACKUP_RELEASE}</backup_release>',
        f'    <backup_date>{NOW_TS}</backup_date>',
        '    <mnet_remoteusers>0</mnet_remoteusers>',
        '    <include_files>0</include_files>',
        '    <include_file_references_to_external_content>0</include_file_references_to_external_content>',
        '    <original_wwwroot>https://learningsuite.byu.edu</original_wwwroot>',
        '    <original_site_identifier_hash>strat325generated</original_site_identifier_hash>',
        f'    <original_course_id>{ids.course_id}</original_course_id>',
        '    <original_course_format>weeks</original_course_format>',
        f'    <original_course_fullname>{xml_escape(COURSE_TITLE)}</original_course_fullname>',
        f'    <original_course_shortname>{xml_escape(COURSE_SHORT)}</original_course_shortname>',
        f'    <original_course_startdate>{COURSE_START}</original_course_startdate>',
        f'    <original_course_enddate>{COURSE_END}</original_course_enddate>',
        f'    <original_course_contextid>{ids.course_context_id}</original_course_contextid>',
        '    <original_system_contextid>1</original_system_contextid>',
        '',
        '    <details>',
        '      <detail backup_id="strat325backup2026">',
        '        <type>course</type>',
        '        <format>moodle2</format>',
        '        <interactive>0</interactive>',
        '        <mode>10</mode>',
        '        <execution>1</execution>',
        '        <executiontime>0</executiontime>',
        '      </detail>',
        '    </details>',
        '',
        '    <contents>',
        '      <activities>',
    ]

    # List all activities
    for i, a in enumerate(ASSESSMENTS):
        mid = ids.module_ids[i]
        sid = ids.section_ids[a["week"]] if a["week"] <= 15 else ids.section_ids[15]
        lines.append('        <activity>')
        lines.append(f'          <moduleid>{mid}</moduleid>')
        lines.append(f'          <sectionid>{sid}</sectionid>')
        lines.append('          <modulename>assign</modulename>')
        lines.append(f'          <title>{xml_escape(a["title"])}</title>')
        lines.append(f'          <directory>activities/assign_{mid}</directory>')
        lines.append('        </activity>')

    lines.append('      </activities>')
    lines.append('      <sections>')

    # List all sections
    for s in range(0, 16):
        sid = ids.section_ids[s]
        title = "General" if s == 0 else f"Week {s}"
        lines.append('        <section>')
        lines.append(f'          <sectionid>{sid}</sectionid>')
        lines.append(f'          <title>{title}</title>')
        lines.append(f'          <directory>sections/section_{sid}</directory>')
        lines.append('        </section>')

    lines.append('      </sections>')
    lines.append('      <course>')
    lines.append(f'        <courseid>{ids.course_id}</courseid>')
    lines.append(f'        <title>{xml_escape(COURSE_SHORT)}</title>')
    lines.append('        <directory>course</directory>')
    lines.append('      </course>')
    lines.append('    </contents>')
    lines.append('')

    # Settings
    lines.append('    <settings>')
    for name, val in [
        ("filename", "strat325-assignments.mbz"),
        ("users", "0"), ("anonymize", "0"), ("role_assignments", "0"),
        ("activities", "1"), ("blocks", "0"), ("filters", "0"),
        ("comments", "0"), ("calendarevents", "0"), ("userscompletion", "0"),
        ("logs", "0"), ("grade_histories", "0"),
    ]:
        lines.append('      <setting>')
        lines.append('        <level>root</level>')
        lines.append(f'        <name>{name}</name>')
        lines.append(f'        <value>{val}</value>')
        lines.append('      </setting>')

    # Per-section settings
    for s in range(0, 16):
        sid = ids.section_ids[s]
        lines.append('      <setting>')
        lines.append('        <level>section</level>')
        lines.append(f'        <section>section_{sid}</section>')
        lines.append(f'        <name>section_{sid}_included</name>')
        lines.append('        <value>1</value>')
        lines.append('      </setting>')
        lines.append('      <setting>')
        lines.append('        <level>section</level>')
        lines.append(f'        <section>section_{sid}</section>')
        lines.append(f'        <name>section_{sid}_userinfo</name>')
        lines.append('        <value>0</value>')
        lines.append('      </setting>')

    # Per-activity settings
    for i in range(len(ASSESSMENTS)):
        mid = ids.module_ids[i]
        lines.append('      <setting>')
        lines.append('        <level>activity</level>')
        lines.append(f'        <activity>assign_{mid}</activity>')
        lines.append(f'        <name>assign_{mid}_included</name>')
        lines.append('        <value>1</value>')
        lines.append('      </setting>')
        lines.append('      <setting>')
        lines.append('        <level>activity</level>')
        lines.append(f'        <activity>assign_{mid}</activity>')
        lines.append(f'        <name>assign_{mid}_userinfo</name>')
        lines.append('        <value>0</value>')
        lines.append('      </setting>')

    lines.append('    </settings>')
    lines.append('  </information>')
    lines.append('</moodle_backup>')
    return "\n".join(lines)


def build_assign_xml(idx, assessment, ids):
    """Assignment activity definition."""
    aid = ids.activity_ids[idx]
    mid = ids.module_ids[idx]
    ctx = ids.context_ids[idx]
    due_ts = date_to_timestamp(assessment["due"])
    url = get_assessment_url(assessment)

    intro = (
        f'&lt;p&gt;See full details: '
        f'&lt;a href=&quot;{xml_escape(url)}&quot;&gt;{xml_escape(assessment["title"])} on course website&lt;/a&gt;'
        f'&lt;/p&gt;'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<activity id="{aid}" moduleid="{mid}" modulename="assign" contextid="{ctx}">
  <assign id="{aid}">
    <name>{xml_escape(assessment["title"])}</name>
    <intro>{intro}</intro>
    <introformat>1</introformat>
    <alwaysshowdescription>1</alwaysshowdescription>
    <submissiondrafts>0</submissiondrafts>
    <sendnotifications>0</sendnotifications>
    <sendlatenotifications>0</sendlatenotifications>
    <sendstudentnotifications>1</sendstudentnotifications>
    <duedate>{due_ts}</duedate>
    <cutoffdate>0</cutoffdate>
    <gradingduedate>0</gradingduedate>
    <allowsubmissionsfromdate>0</allowsubmissionsfromdate>
    <grade>{assessment["points"]}</grade>
    <timemodified>{NOW_TS}</timemodified>
    <completionsubmit>0</completionsubmit>
    <requiresubmissionstatement>0</requiresubmissionstatement>
    <teamsubmission>0</teamsubmission>
    <requireallteammemberssubmit>0</requireallteammemberssubmit>
    <teamsubmissiongroupingid>0</teamsubmissiongroupingid>
    <blindmarking>0</blindmarking>
    <hidegrader>0</hidegrader>
    <revealidentities>0</revealidentities>
    <attemptreopenmethod>none</attemptreopenmethod>
    <maxattempts>-1</maxattempts>
    <markingworkflow>0</markingworkflow>
    <markingallocation>0</markingallocation>
    <markinganonymous>0</markinganonymous>
    <preventsubmissionnotingroup>0</preventsubmissionnotingroup>
    <activity></activity>
    <activityformat>1</activityformat>
    <timelimit>0</timelimit>
    <submissionattachments>0</submissionattachments>
    <userflags>
    </userflags>
    <submissions>
    </submissions>
    <grades>
    </grades>
    <plugin_configs>
      <plugin_config id="{aid * 10 + 1}">
        <plugin>onlinetext</plugin>
        <subtype>assignsubmission</subtype>
        <name>enabled</name>
        <value>0</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 2}">
        <plugin>file</plugin>
        <subtype>assignsubmission</subtype>
        <name>enabled</name>
        <value>1</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 3}">
        <plugin>file</plugin>
        <subtype>assignsubmission</subtype>
        <name>maxfilesubmissions</name>
        <value>1</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 4}">
        <plugin>file</plugin>
        <subtype>assignsubmission</subtype>
        <name>maxsubmissionsizebytes</name>
        <value>0</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 5}">
        <plugin>comments</plugin>
        <subtype>assignsubmission</subtype>
        <name>enabled</name>
        <value>0</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 6}">
        <plugin>comments</plugin>
        <subtype>assignfeedback</subtype>
        <name>enabled</name>
        <value>1</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 7}">
        <plugin>offline</plugin>
        <subtype>assignfeedback</subtype>
        <name>enabled</name>
        <value>0</value>
      </plugin_config>
      <plugin_config id="{aid * 10 + 8}">
        <plugin>file</plugin>
        <subtype>assignfeedback</subtype>
        <name>enabled</name>
        <value>0</value>
      </plugin_config>
    </plugin_configs>
    <overrides>
    </overrides>
  </assign>
</activity>"""


def build_module_xml(idx, assessment, ids):
    """Course module record for an assignment."""
    mid = ids.module_ids[idx]
    week = assessment["week"] if assessment["week"] <= 15 else 15
    sid = ids.section_ids[week]

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<module id="{mid}" version="{MOODLE_VERSION}">
  <modulename>assign</modulename>
  <sectionid>{sid}</sectionid>
  <sectionnumber>{week}</sectionnumber>
  <idnumber>$@NULL@$</idnumber>
  <added>{NOW_TS}</added>
  <score>0</score>
  <indent>0</indent>
  <visible>1</visible>
  <visibleoncoursepage>1</visibleoncoursepage>
  <visibleold>1</visibleold>
  <groupmode>0</groupmode>
  <groupingid>0</groupingid>
  <completion>0</completion>
  <completiongradeitemnumber>$@NULL@$</completiongradeitemnumber>
  <completionpassgrade>0</completionpassgrade>
  <completionview>0</completionview>
  <completionexpected>0</completionexpected>
  <availability>$@NULL@$</availability>
  <showdescription>0</showdescription>
  <downloadcontent>1</downloadcontent>
  <lang></lang>
  <tags>
  </tags>
</module>"""


def build_activity_grades_xml(idx, assessment, ids):
    """Per-activity grade item."""
    gid = ids.grade_item_ids[idx]
    aid = ids.activity_ids[idx]
    cat_id = ids.category_ids[assessment["group"]]
    sort_order = idx + len(ASSIGNMENT_GROUPS) + 2  # after category items

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<activity_gradebook>
  <grade_items>
    <grade_item id="{gid}">
      <categoryid>{cat_id}</categoryid>
      <itemname>{xml_escape(assessment["title"])}</itemname>
      <itemtype>mod</itemtype>
      <itemmodule>assign</itemmodule>
      <iteminstance>{aid}</iteminstance>
      <itemnumber>0</itemnumber>
      <iteminfo>$@NULL@$</iteminfo>
      <idnumber></idnumber>
      <calculation>$@NULL@$</calculation>
      <gradetype>1</gradetype>
      <grademax>{assessment["points"]:.5f}</grademax>
      <grademin>0.00000</grademin>
      <scaleid>$@NULL@$</scaleid>
      <outcomeid>$@NULL@$</outcomeid>
      <gradepass>0.00000</gradepass>
      <multfactor>1.00000</multfactor>
      <plusfactor>0.00000</plusfactor>
      <aggregationcoef>0.00000</aggregationcoef>
      <aggregationcoef2>0.00000</aggregationcoef2>
      <weightoverride>0</weightoverride>
      <sortorder>{sort_order}</sortorder>
      <display>0</display>
      <decimals>$@NULL@$</decimals>
      <hidden>0</hidden>
      <locked>0</locked>
      <locktime>0</locktime>
      <needsupdate>0</needsupdate>
      <timecreated>{NOW_TS}</timecreated>
      <timemodified>{NOW_TS}</timemodified>
      <grade_grades>
      </grade_grades>
    </grade_item>
  </grade_items>
  <grade_letters>
  </grade_letters>
</activity_gradebook>"""


def build_activity_inforef_xml(idx, ids):
    """References for an activity."""
    gid = ids.grade_item_ids[idx]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<inforef>
  <grade_itemref>
    <grade_item>
      <id>{gid}</id>
    </grade_item>
  </grade_itemref>
</inforef>"""


def build_gradebook_xml(ids):
    """Course-level gradebook with categories and category grade items."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gradebook>',
        '  <grade_categories>',
        # Root category
        f'    <grade_category id="{ids.root_category_id}">',
        '      <parent>$@NULL@$</parent>',
        '      <depth>1</depth>',
        f'      <path>/{ids.root_category_id}/</path>',
        '      <fullname>?</fullname>',
        '      <aggregation>10</aggregation>',  # Weighted mean
        '      <keephigh>0</keephigh>',
        '      <droplow>0</droplow>',
        '      <aggregateonlygraded>1</aggregateonlygraded>',
        '      <aggregateoutcomes>0</aggregateoutcomes>',
        f'      <timecreated>{NOW_TS}</timecreated>',
        f'      <timemodified>{NOW_TS}</timemodified>',
        '      <hidden>0</hidden>',
        '    </grade_category>',
    ]

    # Sub-categories (one per assignment group)
    for g in ASSIGNMENT_GROUPS:
        cid = ids.category_ids[g["id"]]
        lines.append(f'    <grade_category id="{cid}">')
        lines.append(f'      <parent>{ids.root_category_id}</parent>')
        lines.append('      <depth>2</depth>')
        lines.append(f'      <path>/{ids.root_category_id}/{cid}/</path>')
        lines.append(f'      <fullname>{xml_escape(g["title"])}</fullname>')
        lines.append('      <aggregation>13</aggregation>')  # Natural (sum) within category
        lines.append('      <keephigh>0</keephigh>')
        lines.append('      <droplow>0</droplow>')
        lines.append('      <aggregateonlygraded>1</aggregateonlygraded>')
        lines.append('      <aggregateoutcomes>0</aggregateoutcomes>')
        lines.append(f'      <timecreated>{NOW_TS}</timecreated>')
        lines.append(f'      <timemodified>{NOW_TS}</timemodified>')
        lines.append('      <hidden>0</hidden>')
        lines.append('    </grade_category>')

    lines.append('  </grade_categories>')
    lines.append('')
    lines.append('  <grade_items>')

    # Root course total grade item
    lines.append(f'    <grade_item id="{ids.root_grade_item_id}">')
    lines.append('      <categoryid>$@NULL@$</categoryid>')
    lines.append('      <itemname>$@NULL@$</itemname>')
    lines.append('      <itemtype>course</itemtype>')
    lines.append('      <itemmodule>$@NULL@$</itemmodule>')
    lines.append(f'      <iteminstance>{ids.root_category_id}</iteminstance>')
    lines.append('      <itemnumber>$@NULL@$</itemnumber>')
    lines.append('      <iteminfo>$@NULL@$</iteminfo>')
    lines.append('      <idnumber></idnumber>')
    lines.append('      <calculation>$@NULL@$</calculation>')
    lines.append('      <gradetype>1</gradetype>')
    lines.append('      <grademax>100.00000</grademax>')
    lines.append('      <grademin>0.00000</grademin>')
    lines.append('      <scaleid>$@NULL@$</scaleid>')
    lines.append('      <outcomeid>$@NULL@$</outcomeid>')
    lines.append('      <gradepass>0.00000</gradepass>')
    lines.append('      <multfactor>1.00000</multfactor>')
    lines.append('      <plusfactor>0.00000</plusfactor>')
    lines.append('      <aggregationcoef>0.00000</aggregationcoef>')
    lines.append('      <aggregationcoef2>0.00000</aggregationcoef2>')
    lines.append('      <weightoverride>0</weightoverride>')
    lines.append('      <sortorder>1</sortorder>')
    lines.append('      <display>0</display>')
    lines.append('      <decimals>$@NULL@$</decimals>')
    lines.append('      <hidden>0</hidden>')
    lines.append('      <locked>0</locked>')
    lines.append('      <locktime>0</locktime>')
    lines.append('      <needsupdate>0</needsupdate>')
    lines.append(f'      <timecreated>{NOW_TS}</timecreated>')
    lines.append(f'      <timemodified>{NOW_TS}</timemodified>')
    lines.append('      <grade_grades>')
    lines.append('      </grade_grades>')
    lines.append('    </grade_item>')

    # Category total grade items (one per assignment group)
    sort_order = 2
    for g in ASSIGNMENT_GROUPS:
        gi_id = ids.category_grade_item_ids[g["id"]]
        cat_id = ids.category_ids[g["id"]]
        weight = g["weight"] / 100.0  # Convert percentage to decimal

        lines.append(f'    <grade_item id="{gi_id}">')
        lines.append(f'      <categoryid>{ids.root_category_id}</categoryid>')
        lines.append(f'      <itemname>{xml_escape(g["title"])}</itemname>')
        lines.append('      <itemtype>category</itemtype>')
        lines.append('      <itemmodule>$@NULL@$</itemmodule>')
        lines.append(f'      <iteminstance>{cat_id}</iteminstance>')
        lines.append('      <itemnumber>$@NULL@$</itemnumber>')
        lines.append('      <iteminfo>$@NULL@$</iteminfo>')
        lines.append('      <idnumber></idnumber>')
        lines.append('      <calculation>$@NULL@$</calculation>')
        lines.append('      <gradetype>1</gradetype>')
        lines.append('      <grademax>100.00000</grademax>')
        lines.append('      <grademin>0.00000</grademin>')
        lines.append('      <scaleid>$@NULL@$</scaleid>')
        lines.append('      <outcomeid>$@NULL@$</outcomeid>')
        lines.append('      <gradepass>0.00000</gradepass>')
        lines.append('      <multfactor>1.00000</multfactor>')
        lines.append('      <plusfactor>0.00000</plusfactor>')
        lines.append(f'      <aggregationcoef>{weight:.5f}</aggregationcoef>')
        lines.append(f'      <aggregationcoef2>{weight:.5f}</aggregationcoef2>')
        lines.append('      <weightoverride>1</weightoverride>')
        lines.append(f'      <sortorder>{sort_order}</sortorder>')
        lines.append('      <display>0</display>')
        lines.append('      <decimals>$@NULL@$</decimals>')
        lines.append('      <hidden>0</hidden>')
        lines.append('      <locked>0</locked>')
        lines.append('      <locktime>0</locktime>')
        lines.append('      <needsupdate>0</needsupdate>')
        lines.append(f'      <timecreated>{NOW_TS}</timecreated>')
        lines.append(f'      <timemodified>{NOW_TS}</timemodified>')
        lines.append('      <grade_grades>')
        lines.append('      </grade_grades>')
        lines.append('    </grade_item>')
        sort_order += 1

    lines.append('  </grade_items>')
    lines.append('  <grade_letters>')
    lines.append('  </grade_letters>')
    lines.append('</gradebook>')
    return "\n".join(lines)


def build_section_xml(section_num, ids):
    """Section definition."""
    sid = ids.section_ids[section_num]

    # Build sequence: comma-separated module IDs for assignments in this section
    module_ids_in_section = []
    for i, a in enumerate(ASSESSMENTS):
        week = a["week"] if a["week"] <= 15 else 15
        if week == section_num:
            module_ids_in_section.append(str(ids.module_ids[i]))
    sequence = ",".join(module_ids_in_section)

    name = "$@NULL@$" if section_num == 0 else f"Week {section_num}"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<section id="{sid}">
  <number>{section_num}</number>
  <name>{name}</name>
  <summary></summary>
  <summaryformat>1</summaryformat>
  <sequence>{sequence}</sequence>
  <visible>1</visible>
  <availabilityjson>$@NULL@$</availabilityjson>
  <component>$@NULL@$</component>
  <itemid>0</itemid>
  <timemodified>{NOW_TS}</timemodified>
</section>"""


def build_course_xml(ids):
    """Course definition."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<course id="{ids.course_id}" contextid="{ids.course_context_id}">
  <shortname>{xml_escape(COURSE_SHORT)}</shortname>
  <fullname>{xml_escape(COURSE_TITLE)}</fullname>
  <idnumber></idnumber>
  <summary>&lt;p&gt;{xml_escape(COURSE_TITLE)} - BYU Marriott School of Business, Winter 2026&lt;/p&gt;</summary>
  <summaryformat>1</summaryformat>
  <format>weeks</format>
  <showgrades>1</showgrades>
  <newsitems>0</newsitems>
  <startdate>{COURSE_START}</startdate>
  <enddate>{COURSE_END}</enddate>
  <marker>0</marker>
  <maxbytes>8388608</maxbytes>
  <legacyfiles>0</legacyfiles>
  <showreports>0</showreports>
  <visible>1</visible>
  <groupmode>0</groupmode>
  <groupmodeforce>0</groupmodeforce>
  <defaultgroupingid>0</defaultgroupingid>
  <lang></lang>
  <theme></theme>
  <timecreated>{NOW_TS}</timecreated>
  <timemodified>{NOW_TS}</timemodified>
  <requested>0</requested>
  <showactivitydates>1</showactivitydates>
  <showcompletionconditions>0</showcompletionconditions>
  <pdfexportfont></pdfexportfont>
  <enablecompletion>0</enablecompletion>
  <completionstartonenrol>0</completionstartonenrol>
  <completionnotify>0</completionnotify>
  <category id="1">
    <name>Miscellaneous</name>
    <description>$@NULL@$</description>
  </category>
  <tags>
  </tags>
  <customfields>
  </customfields>
  <courseformatoptions>
  </courseformatoptions>
</course>"""


def build_course_inforef_xml(ids):
    """Course-level references."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<inforef>
</inforef>"""


# Stub files
STUBS = {
    "files.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<files>\n</files>',
    "completion.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<course_completion>\n</course_completion>',
    "groups.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<groups>\n  <groupings>\n  </groupings>\n</groups>',
    "outcomes.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<outcomes_definition>\n</outcomes_definition>',
    "scales.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<scales_definition>\n</scales_definition>',
    "questions.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<question_categories>\n</question_categories>',
    "roles.xml": (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<roles_definition>\n'
        '  <role id="5">\n'
        '    <name></name>\n'
        '    <shortname>student</shortname>\n'
        '    <nameincourse>$@NULL@$</nameincourse>\n'
        '    <description></description>\n'
        '    <sortorder>5</sortorder>\n'
        '    <archetype>student</archetype>\n'
        '  </role>\n'
        '</roles_definition>'
    ),
    "course/enrolments.xml": (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<enrolments>\n'
        '  <enrols>\n'
        '    <enrol id="1">\n'
        '      <enrolmethod>manual</enrolmethod>\n'
        '      <status>0</status>\n'
        '      <user_enrolments>\n'
        '      </user_enrolments>\n'
        '    </enrol>\n'
        '  </enrols>\n'
        '</enrolments>'
    ),
    "course/roles.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n</roles>',
    "course/filters.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<filters>\n</filters>',
    "course/comments.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<comments>\n</comments>',
    "course/calendar.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<events>\n</events>',
}


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("Generating Moodle backup (.mbz) file...")
    print(f"  {len(ASSESSMENTS)} assignments in {len(ASSIGNMENT_GROUPS)} categories")

    total_points = sum(a["points"] for a in ASSESSMENTS if a["group"] != "surveys_bonus")
    bonus_points = sum(a["points"] for a in ASSESSMENTS if a["group"] == "surveys_bonus")
    print(f"  Total points: {total_points} + {bonus_points} bonus")

    # Pre-allocate all IDs
    ids = build_ids()

    # Show categories
    for g in ASSIGNMENT_GROUPS:
        group_assessments = [a for a in ASSESSMENTS if a["group"] == g["id"]]
        pts = sum(a["points"] for a in group_assessments)
        print(f"    {g['title']}: {len(group_assessments)} items, {pts} pts, {g['weight']}%")

    # Build the .mbz ZIP
    with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        # Master manifest
        zf.writestr("moodle_backup.xml", build_moodle_backup_xml(ids))

        # Course-level gradebook
        zf.writestr("gradebook.xml", build_gradebook_xml(ids))

        # Stub files
        for path, content in STUBS.items():
            zf.writestr(path, content)

        # Course definition
        zf.writestr("course/course.xml", build_course_xml(ids))
        zf.writestr("course/inforef.xml", build_course_inforef_xml(ids))

        # Sections
        for s in range(0, 16):
            sid = ids.section_ids[s]
            zf.writestr(f"sections/section_{sid}/section.xml",
                        build_section_xml(s, ids))
            zf.writestr(f"sections/section_{sid}/inforef.xml",
                        '<?xml version="1.0" encoding="UTF-8"?>\n<inforef>\n</inforef>')

        # Activities
        for i, a in enumerate(ASSESSMENTS):
            mid = ids.module_ids[i]
            prefix = f"activities/assign_{mid}"
            zf.writestr(f"{prefix}/assign.xml", build_assign_xml(i, a, ids))
            zf.writestr(f"{prefix}/module.xml", build_module_xml(i, a, ids))
            zf.writestr(f"{prefix}/grades.xml", build_activity_grades_xml(i, a, ids))
            zf.writestr(f"{prefix}/inforef.xml", build_activity_inforef_xml(i, ids))
            zf.writestr(f"{prefix}/roles.xml",
                        '<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n</roles>')
            zf.writestr(f"{prefix}/filters.xml",
                        '<?xml version="1.0" encoding="UTF-8"?>\n<filters>\n</filters>')
            zf.writestr(f"{prefix}/comments.xml",
                        '<?xml version="1.0" encoding="UTF-8"?>\n<comments>\n</comments>')
            zf.writestr(f"{prefix}/calendar.xml",
                        '<?xml version="1.0" encoding="UTF-8"?>\n<events>\n</events>')
            zf.writestr(f"{prefix}/completion.xml",
                        '<?xml version="1.0" encoding="UTF-8"?>\n<completion>\n</completion>')

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"\nCreated: {OUTPUT_FILE} ({size_kb:.1f} KB)")
    print(f"  29 assignment shells across 15 weekly sections")
    print(f"  5 grade categories with weighted percentages")
    print(f"  Upload to Learning Suite via 'Moodle format' import")


if __name__ == "__main__":
    main()
