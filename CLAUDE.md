# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Quarto book** for STRAT 325 (Intro to Management Consulting) at BYU Marriott School of Business. The course teaches the "MBB consultant toolkit" through two concurrent goals: interview prep and applied consulting projects.

## Build Commands

```bash
# Preview the book locally (starts a local server with live reload)
quarto preview

# Render a single chapter
quarto preview 01-welcome.qmd
```

## Project Structure

- **`_quarto.yml`** - Main configuration defining book structure, chapters, theme, and output settings
- **`index.qmd`** - Syllabus/landing page
- **`##-*.qmd`** - Chapter files numbered by sequence (01-15 for main content, 97-99 for appendices)
- **`references.bib`** - BibTeX bibliography
- **`styles.css`** - Custom CSS overrides
- **`images/`** - Image assets

The site is only rendered via GitHub actions and never rendered locally, only previewed.

## Chapter Organization

  | Part                 | File                         | Chapter Title             | Published? |
  |----------------------|------------------------------|---------------------------|:----------:|
  | Course Info          | index.qmd                    | Syllabus                  | Yes        |
  |                      | 00-schedule.qmd              | *(Canvas sync source)*    | **No**     |
  |                      | 00-assessments.qmd           | Assessments               | Yes        |
  | Foundation           | 01-what-is-consulting.qmd    | What is Consulting?       | Yes        |
  |                      | 02-consultant-diamond.qmd    | The Consultant Diamond    | Yes        |
  |                      | 03-leveraging-ai.qmd         | Leveraging AI             | Yes        |
  |                      | 04-working-as-a-team.qmd     | Working as a Team         | Yes        |
  | The Four Axes        | 05-structured-problem-solving.qmd | 1. Judgment: Structured Problem-Solving | Yes |
  |                      | 06-analytics-modeling.qmd    | 2. Judgment: Analytics & Modeling | Yes |
  |                      | 07-ownership.qmd             | 3. Ownership              | Yes        |
  |                      | 08-communication.qmd         | 4. Communication          | Yes        |
  |                      | 09-collaboration.qmd         | 5. Collaboration          | Yes        |
  | Resources            | 95-antigravity-reference.qmd | Antigravity Reference     | Yes        |
  |                      | 96-firms-guide.qmd           | Firms Guide               | Yes        |
  |                      | 97-ta-handbook.qmd           | TA Handbook               | Yes        |
  |                      | 98-resources.qmd             | Resources                 | Yes        |
  |                      | 99-references.qmd            | References                | Yes        |

## Course Architecture: Website + LMS

This course uses a **two-system architecture** with strict separation of concerns. The dividing line is **WHAT vs. WHEN** — the website describes what students learn and do, Canvas tells them when and where.

### The Separation Principle

The core question when placing content: **"Will a student need this after the semester ends?"**

- **Yes** → website (they'll have lost Canvas access but still need interview prep, frameworks, project guides)
- **No** → Canvas only (dates, submissions, weekly instructions, announcements)

A second test: **"Does this change semester to semester?"**

- **The STAR framework doesn't change** → website
- **"Due Saturday Feb 21"** changes every semester → Canvas only

### The Website (Quarto book — public, durable)

The website is the **textbook and career reference**. It contains timeless, referenceable content that serves multiple audiences long after the course ends.

**What belongs on the website:**
- Chapter readings (frameworks, tools, the Consultant diamond)
- Assessment DESCRIPTIONS — what the deliverable is, how to do it well, rubrics, scoring criteria
- Interview prep guides (STAR framework, case rubrics, behavioral questions, feedback delivery)
- Project requirements (what slides to include, what to research, how feedback works)
- Course overview / marketing pitch (what students learn, who teaches it)
- Firm profiles, resource lists, reference material

**What does NOT belong on the website:**
- Due dates, week references ("Due: Week 9"), or submission deadlines
- Submission logistics ("Submit via Canvas" / "Upload a PDF")
- Schedule with specific dates and session numbers
- Weekly sequencing or "what to do this week" guidance
- Grading percentages (these live authoritatively in Canvas gradebook; the website should not duplicate them or risk divergence)

**Audiences served:**
| Audience | What they want | Example |
|----------|---------------|---------|
| Enrolled students | "How does MECE work?" or "What goes in P1?" | Deep-link from Canvas to a specific section |
| Alumni (post-course) | "How do I structure a case interview again?" | Browse interview prep, rubrics, frameworks |
| Prospective students | "What does this course teach?" | Browse chapters, see the diamond |
| Employers / recruiters | "What can BYU consulting students do?" | The diamond as a capability portfolio |
| Other professors | "How is this course structured?" | Course design and pedagogy inspiration |

### The LMS (Canvas — private, temporal)

Canvas is the **planner and cockpit**. Students open Canvas first for "what do I do this week?" and click through to the website for "how do I do it well?"

**What belongs in Canvas:**
- Weekly modules with session headers, reading links, and due items
- Assignments with points, due dates, and submission — each linking to the website for full description
- Grade categories with authoritative weights
- Announcements, calendar events, and operational communication
- The schedule (expressed as module structure, not a separate page)

**The student experience:**
```
Student opens Canvas (the "remote control")
  → Sees "Week 5" module → knows exactly what to read and what's due
  → Clicks a reading link → lands on the Quarto site chapter section
  → Clicks an assignment → sees link to full description on website + submits here
  → Never has to figure out which system has what
```

**The alumni experience:**
```
Former student preparing for interviews (no Canvas access)
  → Goes to course website → finds behavioral rubrics, STAR framework, case scoring
  → Revisits project descriptions to prep for a real consulting deliverable
  → All reference material is still available
```

### Content Placement Examples

| Content | Website | Canvas | Why |
|---------|:-------:|:------:|-----|
| "P1 is a 4-6 slide deck analyzing a public company" | Yes | Link to it | Durable deliverable description |
| "P1 is due Saturday Feb 21 at 11:59 PM" | No | Yes | Changes every semester |
| STAR framework and behavioral scoring rubric | Yes | Link to it | Career-long reference material |
| "Complete Practice Interview: Peer 3 by Saturday" | No | Yes | Weekly operational instruction |
| Case interview tips for interviewers/interviewees | Yes | Link to it | Durable skill content |
| "Quiz 4 covers chapters 5.1–5.7" | No | Yes | Temporal scope instruction |
| Presentation feedback rubric (Informed/Compelling/Credible) | Yes | Link to it | Reusable assessment framework |
| Grade category weights (10%, 12%, 42%, 36%) | No | Yes | Authoritative in gradebook only |

### File Roles

| File | Published on website? | Role |
|------|:---------------------:|------|
| `index.qmd` | Yes | Course marketing page — what you'll learn, who teaches it, the diamond overview. No specific dates or grade weights |
| `00-schedule.qmd` | **No** | Source of truth for `sync_canvas.py` — lives in repo, feeds Canvas, not published |
| `00-assessments.qmd` | Yes | Assessment reference — deliverable descriptions, rubrics, frameworks. **No due dates or week references** |
| `01-*.qmd` through `08-*.qmd` | Yes | Chapter readings — the textbook content |
| `95-*.qmd` through `99-*.qmd` | Yes | Resources, references, appendices |

### Sync Workflow

`00-schedule.qmd` is the **single source of truth** for course structure and timing. It lives in the repo but is not published on the website.

```bash
# Push course structure to Canvas (modules + assignments + gradebook)
python3 scripts/sync_canvas.py

# Generate Learning Suite imports (if needed)
python3 scripts/generate_imscc.py    # modules with reading links
python3 scripts/generate_moodle.py   # assignment shells with gradebook
```

The Canvas sync script is **idempotent** — it clears and rebuilds. Run it manually after schedule changes; do not auto-sync (a typo could push broken content to students mid-semester).

### Avoiding Divergence

The most dangerous failure mode is **the same fact stated in two places with different values** (e.g., grading weights on the website that don't match Canvas). Rules to prevent this:

1. **Dates and weights have exactly one authoritative source** — Canvas (via `sync_canvas.py`)
2. **Assessment descriptions have exactly one authoritative source** — the website (`00-assessments.qmd`)
3. **Canvas assignments link to the website** for full descriptions; they never duplicate the content
4. **`index.qmd` does not repeat grading details** — it describes the course at a marketing level and directs enrolled students to Canvas for operational details
5. **If you must state a fact in both places, automate it** — generate it from one source (the schedule QMD or assessment data in the sync scripts)

## Content Guidelines

- Course emphasizes AI-assisted consulting work (Claude, VS Code/Cursor, Gemini, GitHub Copilot)
- All projects expect AI-assisted research and analysis
- Key frameworks: MECE, Pyramid Principle, PARADE (behavioral interviews), Trust Equation (networking)
- Content targets BYU undergraduate business and MBA students

## The Consultant Diamond

*How top consultants work, and what the people around them notice.*

The course's framework is called the **Consultant diamond**. "The Consultant's OS" was retired as a name on 2026-10-08 (Scott's decision: one name, and the diamond is what students rate themselves on). Do not reintroduce it. Core-action anchors keep their `#os-` prefix only because changing them would break links.

This course is designed to help you learn and apply the diamond to do two things simultaneously:

1. **Help you land a consulting internship or job** through networking, resume building, and interview preparation
2. **Make you an effective consultant right now and prepared to excel on Day 1 by conducting real consutling proposal and pitch decks using outside in analysis just like a real consultant would**

The diamond has three layers (restructured 2026-10-08; the Four Imperatives were retired):

1. **Four axes** rated by other people: Judgment, Ownership, Communication, Collaboration.
2. **Toolkit components**: eight named skills, each under exactly one axis.
3. **Core actions**: numbered behaviors, each under exactly one toolkit component. The number is `chapter.n` and the anchor is `#os-chapter-n`.

Each axis is a chapter (Judgment is two, one per toolkit component). Inside a chapter, each toolkit component is an `##` section and each core action an `###` section. The student-facing map of all three layers is "Core Actions by Axis" in `02-consultant-diamond.qmd`; keep it, the chapters, and this file in step.

### The Four Axes

Four axes, each rated 1 to 5 by other people (teammates, clients, TAs) against written behavioral anchors. Drawn clockwise from the top: Judgment, Communication, Ownership, Collaboration. The work is on the vertical, the people on the horizontal. Student-facing home: `02-consultant-diamond.qmd#consultant-diamond`, also shown on the syllabus (`index.qmd`); image `images/consultant-diamond.png` (regenerate with `python3 scripts/consultant_diamond.py`).

| Axis | Question | Judged on | Toolkit components | Chapter file |
|------|----------|-----------|--------------------|--------------|
| Judgment | Is this the right work, and is the answer right? | Solves the right problem; says what the facts support | Structured Problem-Solving, Analytics & Modeling | 05, 06 |
| Ownership | Does the work move? | Whether you drive the work | Workstream Ownership, Tolerance for Ambiguity | 07 |
| Communication | Do people understand it? | The artifacts written for a reader | Clear Communication | 08 |
| Collaboration | Do people trust you, and want you on the next one? | How the team and client experience working with you | Client Hands, Teamwork & Collaboration, Coachability | 09 |

Two placements were decided on purpose: Synthesize (4.1) is Communication, not Judgment, because it is tagged Clear Communication and leads straight into the storyline; Tailor to Stakeholders (4.4) is Clear Communication, not Client Hands, because the diamond judges it on the artifact.

**McKinsey 7-Step Problem-Solving Process**

| Step | Name | Description | Axis |
|------|------|-------------|------|
| 0 | Diagnose the current state | Understand what is happening and why before defining the problem. | Judgment |
| 1 | Define the problem | Write a clear, precise problem statement that specifies what decision must be made, under what constraints, and by when. | Judgment |
| 2 | Disaggregate the problem | Break the problem into mutually exclusive, collectively exhaustive (MECE) components so the team can work in parallel and think clearly. | Judgment |
| 3 | Prioritize the issues | Focus on the branches that matter most: those with the biggest impact and that are realistically changeable. | Judgment |
| 4 | Develop a work plan | Decide what analyses to run, who will do them, how deep to go, and on what timeline (with iteration built in). | Ownership |
| 5 | Conduct the analysis | Start with simple heuristics and descriptive statistics, then move to deeper analysis as needed; constantly test assumptions. | Judgment |
| 6 | Synthesize the findings | Integrate results into a coherent, insight-driven answer, clearly addressing "What should we do?" | Communication |
| 7 | Communicate and motivate action | Tell a compelling story, acknowledge uncertainty, and drive alignment so the organization actually acts on the recommendation. | Communication |

**Core Operating Actions**

| Symbol | Meaning |
|--------|---------|
| **(n)** | McKinsey 7-Step Problem-Solving Process step number |
| 🔺 | Pyramid Principle (top-down, answer-first logic) |
| ◯ ◯ | MECE / Venn logic (complete, non-overlapping structure) |

#### Judgment

**Structured Problem-Solving** (`05-structured-problem-solving.qmd`)

| # | Core Action |
|---|-------------|
| 1.1 | Diagnose the current state to understand what is happening and why **(0)** 🔺 |
| 1.2 | Define the problem (the gap between the current state and the desired state) **(1)** 🔺 |
| 1.3 | Frame the problem: articulate the decision set for closing the gap and commit to success criteria, constraints, trade-offs, and what is in vs. out of scope **(1)** 🔺 |
| 1.4 | State a provisional Day-1 hypothesis about which decision to make 🔺 |
| 1.5 | Articulate explicit "what would have to be true" hypotheses for that decision to succeed **(3)** 🔺 |
| 1.6 | Disaggregate those hypotheses into MECE issues designed to test them efficiently **(2)** ◯ ◯ |
| 1.7 | Prioritize decision-critical issues and hypotheses based on likelihood of changing the decision and magnitude of impact **(3)** ◯ ◯ |
| 1.8 | Explicitly exclude questions and analyses that would not change the decision |

**Analytics & Modeling** (`06-analytics-modeling.qmd`)

| # | Core Action |
|---|-------------|
| 2.1 | Design analyses to confirm or falsify priority "must-be-true" hypotheses **(5)** 🔺 |
| 2.2 | Build an outside-in fact base using best-available data **(5)** |
| 2.3 | State assumptions explicitly and identify appropriate proxies **(5)** ◯ ◯ |
| 2.4 | Perform back-of-the-envelope calculations to bound answers **(5)** |
| 2.5 | Build models and run sensitivities to understand drivers, uncertainty, and risk **(5)** ◯ ◯ |

#### Ownership (`07-ownership.qmd`)

**Workstream Ownership**

| # | Core Action |
|---|-------------|
| 3.1 | Translate prioritized hypotheses into a concrete, decision-oriented workplan with milestones **(4)** 🔺 |
| 3.2 | Own a workstream end-to-end, from decision-relevant question to answer |
| 3.3 | Sequence work to deliver insight early and reduce decision risk |
| 3.4 | Reprioritize tasks dynamically as new information changes the decision outlook |
| 3.5 | Identify risks, dependencies, and bottlenecks before they stall progress |
| 3.6 | Manage up with concise updates that surface implications for the decision |

**Tolerance for Ambiguity**

| # | Core Action |
|---|-------------|
| 3.7 | Advance the work using best-available information, without waiting for certainty |

#### Communication (`08-communication.qmd`)

**Clear Communication**

| # | Core Action |
|---|-------------|
| 4.1 | Synthesize analytical results into clear answers to the decision **(6)** 🔺 |
| 4.2 | Craft a storyline that links insights to the decision and its implications **(6)** 🔺 |
| 4.3 | Communicate recommendations with clear logic, explicit trade-offs, and executive-level brevity **(7)** 🔺 |
| 4.4 | Tailor messages to senior audiences and stakeholder concerns **(7)** 🔺 |

#### Collaboration (`09-collaboration.qmd`)

**Client Hands**

| # | Core Action |
|---|-------------|
| 5.1 | Build trust by demonstrating judgment, reliability, and empathy |
| 5.2 | Prewire stakeholders so decision-makers are never surprised in a meeting |
| 5.3 | Navigate difficult conversations and deliver hard messages constructively |

**Teamwork & Collaboration**

| # | Core Action |
|---|-------------|
| 5.4 | Coordinate effectively across team members to present a unified decision narrative |

**Coachability**

| # | Core Action |
|---|-------------|
| 5.5 | Actively solicit feedback and adjust thinking and output in response |

The anchors are copied verbatim from the AI Foundry course's canonical source, `~/courses/ai-foundry/ops/developmentship-model.md` (section 3). If they change there, change them here too; do not reword them locally.

**Grading status:** the diamond is not a graded component in STRAT 325. Any grading use is a proposal in `resources/teaching-notes/consultant-diamond-proposal.md` and needs Scott's decision before a term starts (a rule may cost students points only if published before the term began, and the site and Canvas change together).
