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
COURSE_ID = 34877  # STRAT 325 production course

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

QUIZ_FORMAT = (
    "Completed in class on note cards. Closed laptop, closed note. "
    "1\u20135 questions, mix of free response, multiple choice, and true/false. Peer graded."
)

B = BASE_URL  # shorthand for links


def quiz_description(readings_html):
    """Build quiz description with format info + linked readings."""
    return f"{QUIZ_FORMAT}<br><br><b>Readings covered:</b><br>{readings_html}"


PEER_INTERVIEW_DESCRIPTION = (
    "<b>What to submit (text entry):</b><br>"
    "\u2022 Who interviewed you (interviewee role): [name]<br>"
    "\u2022 Who you interviewed (interviewer role): [name]<br>"
    "\u2022 Link to your feedback form spreadsheet<br>"
    "\u2022 One thing you\u2019re working on based on this session\u2019s feedback<br><br>"
    "<i>Usually the same person for both roles, but doesn\u2019t have to be.</i><br><br>"
    "Each session = behavioral question (~15\u201320 min) + case (~25\u201330 min) per role (~60 min total).<br><br>"
    '<b>Need to set up your feedback form?</b> '
    '<a href="https://docs.google.com/forms/d/1d8jCv8lEOubJTvoePnVGUxgrjUA2RiHDB7joYFmfqPU/copy" '
    'target="_blank">Create your Practice Interview Feedback Form</a>'
)

ASSESSMENTS = [
    # ── Reading Quizzes (10 × 5 pts = 50 pts) ──
    # Quizzes are in class on note cards; peer graded. TA enters scores. No student submission.
    # Each quiz covers all readings since the previous quiz.
    {"id": "quiz_01", "title": "Quiz 1", "group": "reading_quizzes", "points": 5,
     "due": "2026-01-15", "week": 2, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/01-what-is-consulting.html">What Consultants Do</a><br>'
         f'\u2022 <a href="{B}/02-consultants-os.html">The Consultant\'s OS</a><br>'
         f'\u2022 <a href="{B}/03-leveraging-ai.html">AI as Your Operating Amplifier</a><br>'
         f'\u2022 <a href="{B}/03-leveraging-ai.html#ai-assisted-consulting-actions">AI Workflows</a>')},
    {"id": "quiz_02", "title": "Quiz 2", "group": "reading_quizzes", "points": 5,
     "due": "2026-01-22", "week": 3, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/04-working-as-a-team.html">Teams</a><br>'
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-1">Diagnose the Current State</a><br>'
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-1">Root Cause Analysis</a>')},
    {"id": "quiz_03", "title": "Quiz 3", "group": "reading_quizzes", "points": 5,
     "due": "2026-01-29", "week": 4, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-2">Define the Problem</a><br>'
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-3">Frame the Decision</a>')},
    {"id": "quiz_04", "title": "Quiz 4", "group": "reading_quizzes", "points": 5,
     "due": "2026-02-05", "week": 5, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-4">Hypothesize</a><br>'
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-5">WWHTBT</a><br>'
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-6">MECE</a><br>'
         f'\u2022 <a href="{B}/05-think-clearly.html#os-1-7">Prioritization</a>')},
    {"id": "quiz_05", "title": "Quiz 5", "group": "reading_quizzes", "points": 5,
     "due": "2026-02-12", "week": 6, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-2">Outside-In Fact Base</a><br>'
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-3">Assumptions</a><br>'
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-4">Quick Math &amp; Estimation</a>')},
    {"id": "quiz_06", "title": "Quiz 6", "group": "reading_quizzes", "points": 5,
     "due": "2026-02-26", "week": 8, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-1">Design Analyses</a><br>'
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-5">Modeling</a><br>'
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-6">Synthesize: Data to Insight</a>')},
    {"id": "quiz_07", "title": "Quiz 7", "group": "reading_quizzes", "points": 5,
     "due": "2026-03-05", "week": 9, "anchor": "#reading-quizzes",
     "submission_types": ["none"],
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-1">Create a Workplan</a><br>'
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-2">Own Your Workstream</a><br>'
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-3">Sequence</a>')},
    {"id": "quiz_08", "title": "Quiz 8", "group": "reading_quizzes", "points": 5,
     "due": "2026-03-24", "week": 12, "anchor": "#reading-quizzes",
     "canvas_quiz": True,
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-4">Reprioritize</a><br>'
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-5">Anticipate Risks</a><br>'
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-6">Manage Up</a><br>'
         f'\u2022 <a href="{B}/07-move-work-forward.html#os-3-7">Move Without Certainty</a><br>'
         f'\u2022 <a href="{B}/08-create-impact.html#os-4-1">Craft a Storyline (SCQA &amp; Pyramid)</a><br>'
         '\u2022 <a href="https://slideworks.io/resources/bcg-approach-to-great-slides-practical-guide-from-former-consultant#what-are-the-components-of-a-great-presentation">BCG Slides Guide</a><br>'
         '\u2022 <a href="https://slideworks.io/resources/mckinsey-problem-solving-process">McKinsey Problem-Solving</a>')},
    {"id": "quiz_09", "title": "Quiz 9", "group": "reading_quizzes", "points": 5,
     "due": "2026-04-02", "week": 13, "anchor": "#reading-quizzes",
     "canvas_quiz": True, "unlock_at": "2026-04-02T12:30:00-07:00",
     "canvas_description": quiz_description(
         f'\u2022 <a href="{B}/08-create-impact.html#os-4-2">Executive Brevity</a><br>'
         f'\u2022 <a href="{B}/08-create-impact.html#os-4-2">Confident Delivery</a><br>'
         f'\u2022 <a href="{B}/06-get-right-answer.html#os-2-2">Trust Equation</a><br>'
         f'\u2022 <a href="{B}/08-create-impact.html#os-4-4">Build Trust</a><br>'
         f'\u2022 <a href="{B}/08-create-impact.html#os-4-3">Tailor &amp; Handle Pushback</a><br>'
         '\u2022 <a href="https://slideworks.io/resources/getting-to-so-what-guide-to-creating-actionable-business-insights">Getting to the &ldquo;So What&rdquo;</a>')},
    {"id": "quiz_10", "title": "Quiz 10", "group": "reading_quizzes", "points": 5,
     "due": "2026-04-14", "week": 15, "anchor": "#reading-quizzes",
     "canvas_quiz": True, "unlock_at": "2026-04-14T12:30:00-07:00",
     "canvas_description": quiz_description(
         '\u2022 <a href="https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey">How to Write Slide Action Titles</a><br>'
         '\u2022 <a href="https://slideworks.io/resources/getting-to-so-what-guide-to-creating-actionable-business-insights">Getting to the "So What"</a><br>'
         '\u2022 <a href="https://slideworks.io/resources/how-to-write-executive-summary">How to Write an Effective Executive Summary</a><br>'
         '\u2022 <a href="https://slideworks.io/resources/how-mckinsey-consultants-make-presentations">How Management Consultants Make Presentations</a>')},

    # ── Resume and Networking (60 pts) ──
    {"id": "resume_v1", "title": "Resume v1", "group": "resume_networking", "points": 15,
     "due": "2026-02-05", "week": 5, "anchor": "#resume-and-networking",
     "canvas_description": "<b>What to submit:</b> Upload your resume (PDF).<br><br>"
     "1-page consulting-formatted resume with quantified bullets and strong action verbs."},
    {"id": "resume_v2", "title": "Resume v2", "group": "resume_networking", "points": 20,
     "due": "2026-02-19", "week": 7, "anchor": "#resume-and-networking",
     "canvas_description": "<b>What to submit:</b> Upload your revised resume (PDF).<br><br>"
     "Incorporate feedback from your TA on Resume v1."},
    {"id": "networking_tracker", "title": "Networking Tracker", "group": "resume_networking", "points": 25,
     "due": "2026-04-14", "week": 15, "anchor": "#resume-and-networking",
     "canvas_description": "<b>What to submit:</b> Upload or paste a link to your networking tracker "
     "with 5 documented conversations.<br><br>"
     '<a href="https://docs.google.com/spreadsheets/d/1rs3uMtqkH4ELcYcT6PLtcckopRjlUd9PrJXJ2ugFfmI/copy" '
     'target="_blank">Make a copy of the Networking Tracker</a>'},

    # ── Practice Interviews (210 pts) ──
    {"id": "goals_chat", "title": "Goals Chat", "group": "practice_interviews", "points": 10,
     "due": "2026-01-24", "week": 3, "anchor": "#practice-interviews",
     "canvas_description": "<b>What to submit:</b> Paste the link to your completed Goals Worksheet.<br><br>"
     '<a href="https://docs.google.com/document/d/1zq1ih9ZAdjf4K1pisiM6y0NJBAJnn_LezIN6xrWDiIs/copy" '
     'target="_blank">Make a copy of the Goals Worksheet</a>. '
     "Complete it before your first chat with your TA."},
    {"id": "peer_interview_1", "title": "Practice Interview: Peer 1", "group": "practice_interviews", "points": 20,
     "due": "2026-01-31", "week": 4, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "ta_interview_1", "title": "TA Interview and Mentoring 1", "group": "practice_interviews", "points": 20,
     "due": "2026-02-07", "week": 5, "anchor": "#practice-interviews",
     "submission_types": ["none"],
     "canvas_description": "Your TA will mark this complete after your session.<br><br>"
     "Full practice interview (~60 min): behavioral question + case, mirroring actual MBB format."},
    {"id": "peer_interview_2", "title": "Practice Interview: Peer 2", "group": "practice_interviews", "points": 20,
     "due": "2026-02-14", "week": 6, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "peer_interview_3", "title": "Practice Interview: Peer 3", "group": "practice_interviews", "points": 20,
     "due": "2026-02-21", "week": 7, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "peer_interview_4", "title": "Practice Interview: Peer 4", "group": "practice_interviews", "points": 20,
     "due": "2026-02-28", "week": 8, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "ta_interview_2", "title": "TA Interview and Mentoring 2", "group": "practice_interviews", "points": 20,
     "due": "2026-03-07", "week": 9, "anchor": "#practice-interviews",
     "submission_types": ["none"],
     "canvas_description": "Your TA will mark this complete after your session.<br><br>"
     "Progress check practice interview (~60 min): behavioral question + case."},
    {"id": "peer_interview_5", "title": "Practice Interview: Peer 5", "group": "practice_interviews", "points": 20,
     "due": "2026-03-14", "week": 10, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "peer_interview_6", "title": "Practice Interview: Peer 6", "group": "practice_interviews", "points": 20,
     "due": "2026-03-21", "week": 11, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "peer_interview_7", "title": "Practice Interview: Peer 7", "group": "practice_interviews", "points": 20,
     "due": "2026-04-04", "week": 13, "anchor": "#practice-interviews",
     "submission_types": ["online_text_entry", "online_url"],
     "canvas_description": PEER_INTERVIEW_DESCRIPTION},
    {"id": "ta_interview_3", "title": "TA Interview and Mentoring 3", "group": "practice_interviews", "points": 20,
     "due": "2026-04-11", "week": 14, "anchor": "#practice-interviews",
     "submission_types": ["none"],
     "canvas_description": "Your TA will mark this complete after your session.<br><br>"
     "Final practice interview evaluation (~60 min): behavioral question + case."},

    # ── Client Work (180 pts) ──
    {"id": "p1_intel_brief", "title": "P1: Intelligence Brief", "group": "client_work", "points": 40,
     "due": "2026-02-21", "week": 7, "anchor": "#intelligence-brief",
     "canvas_description": "<b>What to submit:</b> Upload your slide deck (PDF or Google Slides link).<br><br>"
     "4\u20136 slide deck (appendix/header/transition slides not counted). "
     "You must also submit the "
     '<a href="https://docs.google.com/forms/d/e/1FAIpQLSccVuQm1vhbx2-6-AC6vDEKqXnkLnaVVIY3RAzCN7JWk6oWMw/viewform" '
     'target="_blank">Presentation Feedback Form</a> for all pod members to receive feedback points (15 pts).'},
    {"id": "p2_point_of_view", "title": "P2: Point of View", "group": "client_work", "points": 40,
     "due": "2026-03-21", "week": 11, "anchor": "#point-of-view",
     "canvas_description": "<b>What to submit:</b> Upload your slide deck (PDF or Google Slides link).<br><br>"
     "5\u20138 slide deck building on your P1 (appendix/header/transition slides not counted). "
     "You must also submit the "
     '<a href="https://docs.google.com/forms/d/e/1FAIpQLSccVuQm1vhbx2-6-AC6vDEKqXnkLnaVVIY3RAzCN7JWk6oWMw/viewform" '
     'target="_blank">Presentation Feedback Form</a> for all pod members to receive feedback points (15 pts).'},
    {"id": "capstone", "title": "Capstone: Conversation Deck", "group": "client_work", "points": 100,
     "due": "2026-04-20", "week": 15, "anchor": "#conversation-deck",
     "canvas_description": "<b>What to submit:</b> Your final deck as a PDF \u2014 6\u201310 slides + appendix.<br><br>"
     "Graded 100% on deck quality by the professor using the "
     '<a href="https://byu-strategy.github.io/management-consulting/00-assessments.html#deck-quality-rubric" '
     'target="_blank">Deck Quality Rubric</a> (Storyline, Insight, Evidence, Slide Design).<br><br>'
     "<b>Capstone Showcase:</b> Wed Apr 22, 11:00 AM\u201312:15 PM, W240 TNRB. "
     "All students are invited and encouraged to attend. "
     "5\u20138 students with the strongest decks will be selected to present their work. "
     "Everyone else will see what top-quality decks look like and hear what made them stand out."},
    {"id": "capstone_outreach", "title": "Capstone: Outreach (Extra Credit)", "group": "client_work", "points": 5,
     "due": "2026-04-20", "week": 15, "anchor": "#conversation-deck",
     "canvas_description": "<b>What to submit:</b> Screenshot or link showing your outreach message "
     "(LinkedIn message, cold email, warm intro, etc.) to someone at your target company.<br><br>"
     "Send your Capstone deck to at least one person at your target company to earn 5 extra credit points. "
     "You\u2019re not graded on whether they respond \u2014 just on putting your work in front of a real professional."},

    # ── Surveys / Bonus ──
    {"id": "mid_semester_feedback", "title": "Mid-Semester Feedback Survey (Bonus)", "group": "surveys_bonus", "points": 5,
     "due": "2026-02-24", "week": 8, "anchor": "",
     "canvas_description": "<b>What to submit:</b> Upload a screenshot of the survey confirmation page.<br><br>"
     '<a href="https://docs.google.com/forms/d/e/1FAIpQLScu_1bXCUhL3n8GtQO1jokKyGr7yZDag5WNnnKwrWvFm2HM6Q/viewform" '
     'target="_blank">Take the Mid-Semester Feedback Survey</a> (anonymous).'},
    {"id": "student_ratings", "title": "Student Ratings (Bonus)", "group": "surveys_bonus", "points": 5,
     "due": "2026-04-14", "week": 15, "anchor": "",
     "canvas_description": "<b>What to submit:</b> Upload a screenshot of the confirmation page "
     "showing you completed the official student ratings survey."},
]


# ── Canvas Quiz Questions ─────────────────────────────────────────────────

QUIZ_QUESTIONS = {
    "quiz_08": [
        {"name": "Q1", "type": "multiple_choice_question", "points": 1,
         "text": "A team is presenting to the CEO about whether to enter a new market. "
                 "Using SCQA, which of the following is the best <em>Complication</em>?",
         "answers": [
             {"text": "Our company has $2B in revenue and operates in 15 countries", "weight": 0},
             {"text": "Competitors have captured 30% of the adjacent market in 18 months, "
                      "and our core market is declining 5% annually", "weight": 100},
             {"text": "We recommend entering the Southeast Asian market", "weight": 0},
             {"text": "Should we enter the Southeast Asian market?", "weight": 0},
         ]},
        {"name": "Q2", "type": "true_false_question", "points": 1,
         "text": "According to the BCG approach to slides, a slide title like "
                 "&ldquo;Revenue Analysis&rdquo; is an example of a strong action title.",
         "answers": [
             {"text": "True", "weight": 0},
             {"text": "False", "weight": 100},
         ]},
        {"name": "Q3", "type": "multiple_choice_question", "points": 1,
         "text": "The Pyramid Principle states that you should:",
         "answers": [
             {"text": "Build suspense by presenting data before your conclusion", "weight": 0},
             {"text": "Start with your answer and support it with grouped arguments", "weight": 100},
             {"text": "Present in chronological order of your analysis", "weight": 0},
             {"text": "Let the audience draw their own conclusions from the data", "weight": 0},
         ]},
        {"name": "Q4", "type": "multiple_choice_question", "points": 1,
         "text": "In McKinsey's 7-step problem-solving process, what is the primary "
                 "purpose of Step 6 (Synthesize)?",
         "answers": [
             {"text": "Run additional analyses to fill in gaps", "weight": 0},
             {"text": "Create a polished presentation deck", "weight": 0},
             {"text": 'Integrate results into a coherent answer addressing '
                      '"What should we do?"', "weight": 100},
             {"text": "Document the methodology for the client's files", "weight": 0},
         ]},
        {"name": "Q5", "type": "multiple_choice_question", "points": 1,
         "text": "You're midway through a 6-week engagement and discover that a key "
                 "assumption about the client's supply chain costs is wrong. "
                 "What should you do FIRST?",
         "answers": [
             {"text": "Continue with the current analysis and note the assumption "
                      "in the appendix", "weight": 0},
             {"text": "Reprioritize your workplan based on how this changes the "
                      "decision outlook", "weight": 100},
             {"text": "Ask for a timeline extension to redo all previous analyses", "weight": 0},
             {"text": "Wait until the next scheduled check-in to raise the issue", "weight": 0},
         ]},
    ],
    "quiz_09": [
        {"name": "Q1", "type": "multiple_choice_question", "points": 1,
         "text": "According to the Trust Equation, which of the following would "
                 "MOST decrease a client's trust in you?",
         "answers": [
             {"text": "Admitting you don't know the answer to a question", "weight": 0},
             {"text": "Missing a deadline you committed to", "weight": 0},
             {"text": "Spending most of the meeting talking about your firm's capabilities "
                      "instead of the client's problem", "weight": 100},
             {"text": "Asking personal questions about the client's weekend plans", "weight": 0},
         ]},
        {"name": "Q2", "type": "multiple_choice_question", "points": 1,
         "text": 'Which of the following is the BEST example of a "So What" insight?',
         "answers": [
             {"text": "Revenue declined 12% last quarter", "weight": 0},
             {"text": "Revenue declined 12% because premium customers are switching to "
                      "Competitor X; we recommend a retention program targeting the top 50 "
                      "accounts within 60 days", "weight": 100},
             {"text": "Revenue has been declining for several quarters", "weight": 0},
             {"text": "Our revenue performance was below expectations", "weight": 0},
         ]},
        {"name": "Q3", "type": "multiple_choice_question", "points": 1,
         "text": 'According to the "Getting to the So What" article, the Five Whys '
                 "technique was originally developed for which purpose?",
         "answers": [
             {"text": "McKinsey's client interview methodology", "weight": 0},
             {"text": "Toyota's manufacturing quality control process", "weight": 100},
             {"text": "Harvard Business School's case method pedagogy", "weight": 0},
             {"text": "The U.S. military's after-action review process", "weight": 0},
         ]},
        {"name": "Q4", "type": "multiple_choice_question", "points": 1,
         "text": "You're presenting to a CFO who cares about ROI and financial impact. "
                 "Your analysis shows a growth opportunity requiring significant upfront "
                 "investment. Applying stakeholder tailoring, what should you lead with?",
         "answers": [
             {"text": "The competitive landscape showing market opportunity", "weight": 0},
             {"text": "The 3-year ROI projection and payback period", "weight": 100},
             {"text": "The strategic vision for company positioning", "weight": 0},
             {"text": "The methodology behind your analysis", "weight": 0},
         ]},
        {"name": "Q5", "type": "multiple_choice_question", "points": 1,
         "text": "A consultant presents a recommendation to sunset a product line. "
                 'The VP of Product says: "My team has spent two years building this '
                 '\u2014 we can\'t just walk away." Which bias from the "So What" '
                 "framework is the VP exhibiting?",
         "answers": [
             {"text": "Overconfidence Bias", "weight": 0},
             {"text": "Anchoring Bias", "weight": 0},
             {"text": "Sunk Cost Bias", "weight": 100},
             {"text": "Confirmation Bias", "weight": 0},
         ]},
    ],
    "quiz_10": [
        {"name": "Q1", "type": "multiple_choice_question", "points": 1,
         "text": "Which of the following is an ACTION TITLE rather than a topic label?",
         "answers": [
             {"text": "Market Overview", "weight": 0},
             {"text": "Financial Analysis", "weight": 0},
             {"text": "Costs grew 2x faster than revenue since 2021", "weight": 100},
             {"text": "Key Findings", "weight": 0},
         ]},
        {"name": "Q2", "type": "multiple_choice_question", "points": 1,
         "text": "According to the 'Getting to the So What' article, what distinguishes "
                 "a meaningful insight from a basic observation?",
         "answers": [
             {"text": "An insight uses more data points than an observation", "weight": 0},
             {"text": "An insight identifies root causes and drives actionable "
                      "recommendations, not just reports what happened", "weight": 100},
             {"text": "An insight must be quantified, while an observation can be qualitative", "weight": 0},
             {"text": "An insight is always surprising, while an observation confirms "
                      "what people already know", "weight": 0},
         ]},
        {"name": "Q3", "type": "multiple_choice_question", "points": 1,
         "text": "According to the Slideworks article on consulting presentations, "
                 "what are the five sections of a complete consulting presentation?",
         "answers": [
             {"text": "Introduction, Literature Review, Methodology, Findings, Conclusion", "weight": 0},
             {"text": "Frontpage, Executive Summary, Body of Slides, Recommendation/Next Steps, Appendix", "weight": 100},
             {"text": "Cover, Agenda, Analysis, Summary, Q&A", "weight": 0},
             {"text": "Title, Problem Statement, Data, Charts, Recommendation", "weight": 0},
         ]},
        {"name": "Q4", "type": "multiple_choice_question", "points": 1,
         "text": "What is the primary purpose of an executive summary slide in a "
                 "consulting deck?",
         "answers": [
             {"text": "List the agenda and table of contents for the presentation", "weight": 0},
             {"text": "Compress the full argument so a reader who sees only this slide "
                      "understands the recommendation", "weight": 100},
             {"text": "Introduce the consulting team and their qualifications", "weight": 0},
             {"text": "Summarize the data sources used in the analysis", "weight": 0},
         ]},
        {"name": "Q5", "type": "multiple_choice_question", "points": 1,
         "text": "If you are struggling to write a clear action title for a slide, "
                 "what does that most likely indicate?",
         "answers": [
             {"text": "The slide needs a better chart or visual", "weight": 0},
             {"text": "The slide's core message isn't clear, or the slide is trying "
                      "to make too many points", "weight": 100},
             {"text": "You should use a topic label instead and explain the point verbally", "weight": 0},
             {"text": "The slide should be moved to the appendix", "weight": 0},
         ]},
    ],
}


# ── Canvas API Client ─────────────────────────────────────────────────────

class CanvasAPI:
    def __init__(self, base_url, token, course_id, dry_run=False):
        self.base_url = base_url
        self.course_id = course_id
        self.dry_run = dry_run
        self._mock_id = 10000
        if not dry_run:
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            })

    def _url(self, path):
        return f"{self.base_url}/api/v1/courses/{self.course_id}{path}"

    def _request(self, method, path, **kwargs):
        if self.dry_run:
            self._mock_id += 1
            return {"id": self._mock_id, "name": "dry-run"}
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
        if self.dry_run:
            return None
        time.sleep(REQUEST_DELAY)
        resp = self.session.delete(self._url(path))
        return resp

    def get_all(self, path, **kwargs):
        """Paginate through all results."""
        if self.dry_run:
            return []
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
        """Delete all existing assignments, preserving quiz-backed ones."""
        assignments = self.get_all("/assignments")
        # Titles of assessments managed as Canvas quizzes
        quiz_titles = {a["title"] for a in ASSESSMENTS if a.get("canvas_quiz")}
        deleted = 0
        for a in assignments:
            if a["name"] in quiz_titles:
                print(f"  Keeping quiz assignment: {a['name']}")
                continue
            print(f"  Deleting assignment: {a['name']}")
            self.delete(f"/assignments/{a['id']}")
            deleted += 1
        return deleted

    def clear_assignment_groups(self, safe_group_id=None):
        """Delete assignment groups, moving any remaining assignments to safe_group_id."""
        groups = self.get_all("/assignment_groups")
        deleted = 0
        for g in groups:
            # Never delete the safe group — it holds preserved quiz assignments
            if safe_group_id and g["id"] == safe_group_id:
                continue
            print(f"  Deleting group: {g['name']}")
            if safe_group_id:
                # Move any surviving assignments (e.g. quizzes) to safe group
                time.sleep(REQUEST_DELAY)
                self.session.delete(
                    self._url(f"/assignment_groups/{g['id']}"),
                    params={"move_assignments_to": safe_group_id}
                )
            else:
                self.delete(f"/assignment_groups/{g['id']}")
            deleted += 1
        return deleted

    def create_assignment_group(self, name, weight, position):
        """Create an assignment group (grade category)."""
        return self.post("/assignment_groups", json={
            "name": name,
            "group_weight": weight,
            "position": position,
        })

    def enable_weighted_grading(self):
        """Set course to use weighted assignment groups."""
        if self.dry_run:
            return {}
        time.sleep(REQUEST_DELAY)
        resp = self.session.put(
            f"{self.base_url}/api/v1/courses/{self.course_id}",
            json={"course": {"apply_assignment_group_weights": True}}
        )
        resp.raise_for_status()
        return resp.json()

    def create_assignment(self, name, points, due_date, group_id, description="",
                          submission_types=None):
        """Create an assignment."""
        if submission_types is None:
            submission_types = ["online_upload", "online_url"]

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
                "submission_types": submission_types,
                "description": description,
                "published": True,
            }
        })

    def create_quiz(self, title, description, group_id, points, due_date,
                     time_limit=None, unlock_at=None):
        """Create a Canvas quiz (Classic Quizzes API).

        Args:
            unlock_at: ISO 8601 datetime string. If set, students can see the
                       quiz description (e.g. reading links) immediately but
                       cannot begin the quiz until this time.
        """
        dt = datetime.strptime(due_date, "%Y-%m-%d")
        dt = dt.replace(hour=23, minute=59, second=0, tzinfo=timezone(MT_OFFSET))
        due_at = dt.isoformat()

        quiz_data = {
            "title": title,
            "description": description,
            "quiz_type": "assignment",
            "assignment_group_id": group_id,
            "time_limit": time_limit,
            "published": False,  # publish after adding questions
            "due_at": due_at,
            "scoring_policy": "keep_highest",
            "allowed_attempts": 1,
        }
        if unlock_at:
            quiz_data["unlock_at"] = unlock_at

        return self.post("/quizzes", json={"quiz": quiz_data})

    def add_quiz_question(self, quiz_id, name, text, question_type, points, answers):
        """Add a question to a Canvas quiz."""
        return self.post(f"/quizzes/{quiz_id}/questions", json={
            "question": {
                "question_name": name,
                "question_text": text,
                "question_type": question_type,
                "points_possible": points,
                "answers": answers,
            }
        })

    def publish_quiz(self, quiz_id):
        """Publish a quiz."""
        return self.put(f"/quizzes/{quiz_id}", json={
            "quiz": {"published": True}
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

    def set_front_page(self, view="wiki"):
        """Set the course home page view ('modules' or 'wiki')."""
        if self.dry_run:
            return {}
        time.sleep(REQUEST_DELAY)
        resp = self.session.put(
            f"{self.base_url}/api/v1/courses/{self.course_id}",
            json={"course": {"default_view": view}}
        )
        resp.raise_for_status()
        return resp.json()

    def set_wiki_front_page(self, html_body):
        """Create or update the wiki front page with the given HTML."""
        if self.dry_run:
            return {}
        time.sleep(REQUEST_DELAY)
        resp = self.session.put(
            self._url("/front_page"),
            json={
                "wiki_page": {
                    "title": "Home",
                    "body": html_body,
                    "published": True,
                }
            }
        )
        if resp.status_code == 404:
            # No front page exists yet — create one
            time.sleep(REQUEST_DELAY)
            resp = self.session.post(
                self._url("/pages"),
                json={
                    "wiki_page": {
                        "title": "Home",
                        "body": html_body,
                        "published": True,
                        "front_page": True,
                    }
                }
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


# ── Homepage HTML ─────────────────────────────────────────────────────────

def generate_schedule_rows(sessions, assessments_by_week):
    """Build HTML table rows for the schedule grid."""
    rows = []
    prev_week = None
    for s in sessions:
        # Week number (only show on first session of the week)
        wk_cell = str(s["week"]) if s["week"] != prev_week else ""
        prev_week = s["week"]

        # Date (compact: "T Jan 13" or "Th Feb 5")
        date = s["date"]

        # Topic with chapter links
        if s["links"]:
            # Build linked topic from chapter reading links
            link_parts = []
            for text, page, anchor in s["links"]:
                href = f"{BASE_URL}/{page}"
                if anchor:
                    href += anchor
                link_parts.append(
                    f'<a href="{href}" target="_blank" '
                    f'style="color: #002E5D; text-decoration: none; '
                    f'border-bottom: 1px dotted #aaa;">{text}</a>'
                )
            topic = " &amp; ".join(link_parts)
        else:
            topic = s["topic"]

        # Guest indicator
        if s.get("guest"):
            guest_name = s["guest"].split("(")[0].strip()
            topic += f' <span style="color:#0062B8; font-size: 12px;">({guest_name})</span>'

        # Due items for this session's week (only on last session of week)
        due_items = []
        # Check if this is the last session in this week
        is_last = True
        idx = sessions.index(s)
        if idx + 1 < len(sessions) and sessions[idx + 1]["week"] == s["week"]:
            is_last = False

        if is_last:
            for a in assessments_by_week.get(s["week"], []):
                title = a["title"]
                # Shorten common prefixes
                title = title.replace("Practice Interview: ", "")
                title = title.replace("TA Interview and Mentoring ", "TA ")
                title = title.replace("Mid-Semester Feedback Survey (Bonus)", "Mid-Sem Survey")
                title = title.replace("Student Ratings (Bonus)", "Student Ratings")
                title = title.replace("Capstone: Conversation Deck", "Capstone")
                title = title.replace("Capstone: Outreach (Extra Credit)", "Outreach EC")
                title = title.replace("P1: Intelligence Brief", "P1")
                title = title.replace("P2: Point of View", "P2")
                title = title.replace("Networking Tracker", "Net. Tracker")
                due_items.append(title)

        due_str = ", ".join(due_items) if due_items else ""

        # Row styling: alternate weeks with subtle background
        bg = "#f9fafb" if s["week"] % 2 == 0 else "#fff"
        td = f'style="padding: 4px 8px; font-size: 13px; border-bottom: 1px solid #f0f0f0; background: {bg};"'
        td_wk = f'style="padding: 4px 8px; font-size: 13px; border-bottom: 1px solid #f0f0f0; background: {bg}; font-weight: 600; color: #002E5D;"'
        td_due = f'style="padding: 4px 8px; font-size: 12px; border-bottom: 1px solid #f0f0f0; background: {bg}; color: #666;"'

        rows.append(
            f'<tr><td {td_wk}>{wk_cell}</td>'
            f'<td {td}>{date}</td>'
            f'<td {td}>{topic}</td>'
            f'<td {td_due}>{due_str}</td></tr>'
        )
    return "\n    ".join(rows)


def generate_homepage_html(course_id, sessions, assessments_by_week):
    """Generate the Canvas wiki front page HTML."""
    schedule_rows = generate_schedule_rows(sessions, assessments_by_week)

    return f"""\
<div style="max-width: 820px; margin: 0 auto;">

  <!-- Header -->
  <div style="background: linear-gradient(135deg, #002E5D 0%, #0062B8 100%); color: white;
              padding: 44px 36px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
    <h1 style="margin: 0 0 6px 0; font-size: 30px; font-weight: 700; color: white;">STRAT 325</h1>
    <p style="margin: 0; font-size: 19px; color: rgba(255,255,255,0.92);">Introduction to Management Consulting</p>
    <p style="margin: 8px 0 0 0; font-size: 14px; color: rgba(255,255,255,0.65);">BYU Marriott School of Business</p>
  </div>

  <!-- Quick Links -->
  <table style="width: 100%; border-collapse: separate; border-spacing: 10px 0; margin-bottom: 20px;">
    <tr>
      <td style="width: 33%; background: #f5f7fa; padding: 18px 12px; border-radius: 8px;
                 text-align: center; border: 1px solid #e2e6ea;">
        <a href="/courses/{course_id}/modules"
           style="text-decoration: none; color: #002E5D; font-weight: 600; font-size: 15px;">
           Modules</a>
      </td>
      <td style="width: 33%; background: #f5f7fa; padding: 18px 12px; border-radius: 8px;
                 text-align: center; border: 1px solid #e2e6ea;">
        <a href="{BASE_URL}/"
           target="_blank" style="text-decoration: none; color: #002E5D; font-weight: 600; font-size: 15px;">
           Course Website</a>
      </td>
      <td style="width: 33%; background: #f5f7fa; padding: 18px 12px; border-radius: 8px;
                 text-align: center; border: 1px solid #e2e6ea;">
        <a href="{BASE_URL}/00-assessments.html"
           target="_blank" style="text-decoration: none; color: #002E5D; font-weight: 600; font-size: 15px;">
           Assessments</a>
      </td>
    </tr>
  </table>

  <!-- Welcome -->
  <div style="background: #fff; border: 1px solid #e2e6ea; border-radius: 8px; padding: 24px; margin-bottom: 20px;">
    <h2 style="margin: 0 0 10px 0; font-size: 19px; color: #002E5D;">Welcome</h2>
    <p style="margin: 0; line-height: 1.65; color: #333; font-size: 14px;">
      This course teaches the <strong>Consultant&rsquo;s Operating System</strong> &mdash; the professional
      toolkit used by top-tier strategy consultants to solve problems, deliver work, and create impact.
      You&rsquo;ll build this toolkit through two parallel tracks:
      <strong>interview preparation</strong> (networking, resume, behavioral &amp; case practice) and
      <strong>applied consulting projects</strong> (real company analysis using the same methods
      MBB firms use).
    </p>
  </div>

  <!-- Schedule -->
  <div style="background: #fff; border: 1px solid #e2e6ea; border-radius: 8px; padding: 24px; margin-bottom: 20px;">
    <h2 style="margin: 0 0 14px 0; font-size: 19px; color: #002E5D;">Schedule</h2>
    <table style="width: 100%; border-collapse: collapse;">
      <tr style="border-bottom: 2px solid #002E5D;">
        <th style="padding: 6px 8px; text-align: left; font-size: 12px; color: #555; font-weight: 600; width: 30px;">Wk</th>
        <th style="padding: 6px 8px; text-align: left; font-size: 12px; color: #555; font-weight: 600; width: 90px;">Date</th>
        <th style="padding: 6px 8px; text-align: left; font-size: 12px; color: #555; font-weight: 600;">Topic</th>
        <th style="padding: 6px 8px; text-align: left; font-size: 12px; color: #555; font-weight: 600; width: 150px;">Due</th>
      </tr>
    {schedule_rows}
    </table>
  </div>

  <!-- The Four Imperatives -->
  <div style="background: #fff; border: 1px solid #e2e6ea; border-radius: 8px; padding: 24px; margin-bottom: 20px;">
    <h2 style="margin: 0 0 14px 0; font-size: 19px; color: #002E5D;">The Four Imperatives</h2>
    <table style="width: 100%; border-collapse: separate; border-spacing: 0 10px;">
      <tr>
        <td style="width: 50%; background: #f0f4f8; padding: 14px 16px; border-radius: 6px;
                   border-left: 4px solid #002E5D; vertical-align: top;">
          <strong style="color: #002E5D;">1. Think Clearly</strong><br>
          <span style="font-size: 13px; color: #555;">Are we solving the right problem in the right way?</span>
        </td>
        <td style="width: 8px;"></td>
        <td style="width: 50%; background: #f0f4f8; padding: 14px 16px; border-radius: 6px;
                   border-left: 4px solid #0062B8; vertical-align: top;">
          <strong style="color: #002E5D;">2. Get to the Right Answer</strong><br>
          <span style="font-size: 13px; color: #555;">What do the facts and data actually say?</span>
        </td>
      </tr>
      <tr>
        <td style="width: 50%; background: #f0f4f8; padding: 14px 16px; border-radius: 6px;
                   border-left: 4px solid #4A90D9; vertical-align: top;">
          <strong style="color: #002E5D;">3. Move Work Forward</strong><br>
          <span style="font-size: 13px; color: #555;">Is the work actually progressing toward a decision?</span>
        </td>
        <td style="width: 8px;"></td>
        <td style="width: 50%; background: #f0f4f8; padding: 14px 16px; border-radius: 6px;
                   border-left: 4px solid #7FB3E8; vertical-align: top;">
          <strong style="color: #002E5D;">4. Create Impact with People</strong><br>
          <span style="font-size: 13px; color: #555;">Do people understand, trust, and act on this work?</span>
        </td>
      </tr>
    </table>
  </div>

  <!-- Course Info -->
  <div style="background: #fff; border: 1px solid #e2e6ea; border-radius: 8px; padding: 24px;">
    <h2 style="margin: 0 0 10px 0; font-size: 19px; color: #002E5D;">Course Info</h2>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
      <tr>
        <td style="padding: 6px 12px 6px 0; font-weight: 600; color: #555; width: 110px;">Instructor</td>
        <td style="padding: 6px 0;">Scott Murff</td>
      </tr>
      <tr>
        <td style="padding: 6px 12px 6px 0; font-weight: 600; color: #555;">Schedule</td>
        <td style="padding: 6px 0;">T/Th &mdash; see <a href="/courses/{course_id}/modules">Modules</a> for session topics</td>
      </tr>
      <tr>
        <td style="padding: 6px 12px 6px 0; font-weight: 600; color: #555;">Website</td>
        <td style="padding: 6px 0;">
          <a href="{BASE_URL}/" target="_blank">{BASE_URL.replace('https://', '')}</a>
        </td>
      </tr>
    </table>
  </div>

</div>"""


# ── Dry-Run Printer ──────────────────────────────────────────────────────

def print_dry_run(sessions, phases, weeks):
    """Print what the sync would do without touching Canvas."""
    print("\n" + "=" * 60)
    print("  DRY RUN — no Canvas changes will be made")
    print("=" * 60)

    print("\n── Would clear ──")
    print("  All existing modules, assignments, and assignment groups")

    print("\n── Would create assignment groups ──")
    for g in ASSIGNMENT_GROUPS:
        print(f"  {g['title']}: {g['weight']}%")

    print("\n── Would create assignments ──")
    for a in ASSESSMENTS:
        flag = " (Canvas quiz, preserved)" if a.get("canvas_quiz") else ""
        print(f"  {a['title']:40s} {a['points']:3d} pts  due {a['due']}{flag}")

    print("\n── Would create modules ──")
    assessments_by_week = {}
    for a in ASSESSMENTS:
        assessments_by_week.setdefault(a["week"], []).append(a)

    for week_num in sorted(weeks.keys()):
        phase = get_phase_for_week(week_num, phases)
        print(f"\n  Week {week_num}: {phase}")
        for s in weeks[week_num]:
            print(f"    {s['date']} — {s['topic']}")
            for text, _, _ in s["links"]:
                print(f"      → {text}")
            for text, _ in s.get("external_links", []):
                print(f"      → {text}")
        for a in assessments_by_week.get(week_num, []):
            print(f"    Due: {a['title']} ({a['points']} pts)")

    print("\n── Would set homepage ──")
    print("  Wiki front page with course branding + quick links")

    total_points = sum(a["points"] for a in ASSESSMENTS if a["group"] != "surveys_bonus")
    bonus_points = sum(a["points"] for a in ASSESSMENTS if a["group"] == "surveys_bonus")
    print(f"\n── Summary ──")
    print(f"  {len(weeks)} weekly modules")
    print(f"  {len(ASSESSMENTS)} assignments ({total_points} pts + {bonus_points} bonus)")
    print(f"  {len(ASSIGNMENT_GROUPS)} assignment groups")
    print(f"  {sum(len(s['links']) for s in sessions)} reading links")


# ── Main Sync Logic ───────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv

    # Parse schedule (always, even in dry-run)
    print(f"Parsing: {SCHEDULE_FILE}")
    sessions, phases = parse_schedule(SCHEDULE_FILE)
    print(f"  {len(sessions)} sessions, {len(phases)} phases")

    # Group sessions by week
    weeks = {}
    for s in sessions:
        weeks.setdefault(s["week"], []).append(s)

    if dry_run:
        print_dry_run(sessions, phases, weeks)
        return

    if not CANVAS_API_TOKEN or not CANVAS_API_URL:
        print("ERROR: Set CANVAS_API_TOKEN and CANVAS_API_URL in .env.local")
        sys.exit(1)

    api = CanvasAPI(CANVAS_API_URL, CANVAS_API_TOKEN, COURSE_ID)

    # Group assessments by week
    assessments_by_week = {}
    for a in ASSESSMENTS:
        assessments_by_week.setdefault(a["week"], []).append(a)

    # ── Step 1: Snapshot existing Canvas state ──
    print("\n── Reading existing Canvas state ──")
    existing_assignments = {a["name"]: a for a in api.get_all("/assignments")}
    existing_groups = {g["name"]: g for g in api.get_all("/assignment_groups")}
    existing_quizzes = {q["title"]: q for q in api.get_all("/quizzes")}
    print(f"  {len(existing_assignments)} assignments, "
          f"{len(existing_groups)} groups, {len(existing_quizzes)} quizzes")

    # ── Step 2: Set up course ──
    print("\n── Configuring course ──")
    api.enable_weighted_grading()
    print("  Enabled weighted grading")

    # ── Step 3: Upsert assignment groups ──
    print("\n── Syncing assignment groups ──")
    group_canvas_ids = {}  # maps our group id -> Canvas group id
    for g in ASSIGNMENT_GROUPS:
        existing = existing_groups.get(g["title"])
        if existing:
            # Update in place
            api.put(f"/assignment_groups/{existing['id']}", json={
                "name": g["title"],
                "group_weight": g["weight"],
                "position": g["position"],
            })
            group_canvas_ids[g["id"]] = existing["id"]
            print(f"  {g['title']}: {g['weight']}% (updated, ID: {existing['id']})")
        else:
            result = api.create_assignment_group(g["title"], g["weight"], g["position"])
            group_canvas_ids[g["id"]] = result["id"]
            print(f"  {g['title']}: {g['weight']}% (created, ID: {result['id']})")

    # Remove stale assignment groups (not in our data)
    our_group_titles = {g["title"] for g in ASSIGNMENT_GROUPS}
    for name, grp in existing_groups.items():
        if name not in our_group_titles and name != "Assignments":
            print(f"  Removing stale group: {name}")
            # Move any assignments to the first group before deleting
            first_group_id = group_canvas_ids.get(ASSIGNMENT_GROUPS[0]["id"])
            if first_group_id:
                time.sleep(REQUEST_DELAY)
                api.session.delete(
                    api._url(f"/assignment_groups/{grp['id']}"),
                    params={"move_assignments_to": first_group_id}
                )
            else:
                api.delete(f"/assignment_groups/{grp['id']}")

    # ── Step 4: Upsert Canvas quizzes ──
    print("\n── Syncing Canvas quizzes ──")
    assignment_canvas_ids = {}  # maps our assessment id -> Canvas assignment id

    for a in ASSESSMENTS:
        if not a.get("canvas_quiz"):
            continue

        desc = a.get("canvas_description", "")
        existing_quiz = existing_quizzes.get(a["title"])

        if existing_quiz:
            # Update description and group (preserves questions and grades)
            quiz_id = existing_quiz["id"]
            assignment_id = existing_quiz.get("assignment_id")
            quiz_update = {"description": desc}
            if a.get("unlock_at"):
                quiz_update["unlock_at"] = a["unlock_at"]
            api.put(f"/quizzes/{quiz_id}", json={"quiz": quiz_update})
            if assignment_id:
                new_group = group_canvas_ids.get(a["group"])
                if new_group:
                    api.put(f"/assignments/{assignment_id}", json={
                        "assignment": {"assignment_group_id": new_group}
                    })
                assignment_canvas_ids[a["id"]] = assignment_id
            print(f"  {a['title']} (updated)")
        else:
            # Create new quiz with questions
            canvas_group_id = group_canvas_ids[a["group"]]
            quiz = api.create_quiz(
                a["title"], desc, canvas_group_id, a["points"], a["due"],
                time_limit=15, unlock_at=a.get("unlock_at"),
            )
            quiz_id = quiz["id"]

            questions = QUIZ_QUESTIONS.get(a["id"], [])
            for q in questions:
                api.add_quiz_question(
                    quiz_id, q["name"], q["text"], q["type"], q["points"], q["answers"]
                )

            api.publish_quiz(quiz_id)
            assignment_canvas_ids[a["id"]] = quiz.get("assignment_id", quiz["id"])
            print(f"  {a['title']} (created, {len(questions)} questions)")

    # ── Step 5: Upsert regular assignments ──
    print("\n── Syncing assignments ──")
    for a in ASSESSMENTS:
        if a.get("canvas_quiz"):
            continue

        url = get_assessment_url(a)
        parts = []
        if a.get("canvas_description"):
            parts.append(a["canvas_description"])
        parts.append(
            f'<p>See full details: '
            f'<a href="{url}" target="_blank">{a["title"]} on course website</a></p>'
        )
        description = "<br>".join(parts)

        # Convert due date
        dt = datetime.strptime(a["due"], "%Y-%m-%d")
        dt = dt.replace(hour=23, minute=59, second=0, tzinfo=timezone(MT_OFFSET))
        due_at = dt.isoformat()

        canvas_group_id = group_canvas_ids[a["group"]]
        submission_types = a.get("submission_types")
        if submission_types is None:
            submission_types = ["online_upload", "online_url"]

        existing = existing_assignments.get(a["title"])
        if existing:
            # Update in place — preserves grades and submissions
            api.put(f"/assignments/{existing['id']}", json={
                "assignment": {
                    "description": description,
                    "points_possible": a["points"],
                    "due_at": due_at,
                    "assignment_group_id": canvas_group_id,
                    "submission_types": submission_types,
                    "published": True,
                }
            })
            assignment_canvas_ids[a["id"]] = existing["id"]
            print(f"  {a['title']} (updated, {a['points']} pts)")
        else:
            result = api.create_assignment(
                a["title"], a["points"], a["due"], canvas_group_id, description,
                submission_types=submission_types,
            )
            assignment_canvas_ids[a["id"]] = result["id"]
            print(f"  {a['title']} (created, {a['points']} pts, due {a['due']})")

    # ── Step 6: Rebuild modules (no grades, safe to clear) ──
    n = api.clear_modules()
    print(f"\n── Rebuilding weekly modules (cleared {n}) ──")
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
                canvas_id = assignment_canvas_ids.get(a["id"])
                if not canvas_id:
                    print(f"    [{pos}]   ⚠ {a['title']} — not found, skipping")
                    continue
                api.add_module_assignment(module_id, canvas_id, pos, indent=1)
                print(f"    [{pos}]   → {a['title']} ({a['points']} pts)")
                pos += 1

        # Publish the module
        api.publish_module(module_id)

    # ── Step 7: Set homepage ──
    print("\n── Setting homepage ──")
    homepage_html = generate_homepage_html(COURSE_ID, sessions, assessments_by_week)
    api.set_wiki_front_page(homepage_html)
    api.set_front_page("wiki")
    print("  Created wiki front page with course branding")
    print("  Set course home to wiki page view")

    # ── Summary ──
    total_points = sum(a["points"] for a in ASSESSMENTS if a["group"] != "surveys_bonus")
    bonus_points = sum(a["points"] for a in ASSESSMENTS if a["group"] == "surveys_bonus")
    print(f"\n── Done ──")
    print(f"  {len(weeks)} weekly modules")
    print(f"  {len(ASSESSMENTS)} assignments ({total_points} pts + {bonus_points} bonus)")
    print(f"  {len(ASSIGNMENT_GROUPS)} assignment groups")
    print(f"  {sum(len(s['links']) for s in sessions)} reading links")
    print(f"\n  Home: {CANVAS_API_URL}/courses/{COURSE_ID}")
    print(f"  Modules: {CANVAS_API_URL}/courses/{COURSE_ID}/modules")


if __name__ == "__main__":
    main()
