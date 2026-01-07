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

  | Part                 | File                         | Chapter Title             |
  |----------------------|------------------------------|---------------------------|
  | Course Info          | index.qmd                    | Syllabus                  |
  |                      | 00-schedule.qmd              | Schedule                  |
  |                      | 00-assessments.qmd           | Assessments               |
  | Foundation           | 01-what-is-consulting.qmd    | What is Consulting?       |
  |                      | 02-consultants-os.qmd        | The Consultant's OS       |
  |                      | 03-leveraging-ai.qmd         | Leveraging AI             |
  |                      | 04-working-as-a-team.qmd     | Working as a Team         |
  | The Four Imperatives | 05-think-clearly.qmd         | Think Clearly             |
  |                      | 06-get-right-answer.qmd      | Get to the Right Answer   |
  |                      | 07-move-work-forward.qmd     | Move Work Forward         |
  |                      | 08-create-impact.qmd         | Create Impact with People |
  | Course Goals         | 09-land-an-offer.qmd         | Land an Offer             |
  |                      | 10-your-first-engagement.qmd | Your First Engagement     |
  | Resources            | 98-resources.qmd             | Resources                 |
  |                      | 99-references.qmd            | References                |

## Content Guidelines

- Course emphasizes AI-assisted consulting work (Claude, VS Code/Cursor, Gemini, GitHub Copilot)
- All projects expect AI-assisted research and analysis
- Key frameworks: MECE, Pyramid Principle, PARADE (behavioral interviews), Trust Equation (networking)
- Content targets BYU undergraduate business and MBA students

## The Consultant's OS

*A professional operating system for solving problems, delivering work, and creating impact — in your job search and client engagements.*

This course is designed to help you learn and apply the Consultant's OS to do two things simultaneously:

1. **Help you land a consulting internship or job** through networking, resume building, and interview preparation
2. **Make you an effective consultant right now and prepared to excel on Day 1 by conducting real consutling proposal and pitch decks using outside in analysis just like a real consultant would**

The course organizes consulting skills into **4 Imperatives**, each with a guiding question, core operating actions, and associated toolkit components.

**McKinsey 7-Step Problem-Solving Process**

| Step | Name | Description |
|------|------|-------------|
| 1 | Define the problem | Write a clear, precise problem statement that specifies what decision must be made, under what constraints, and by when. |
| 2 | Disaggregate the problem | Break the problem into mutually exclusive, collectively exhaustive (MECE) components so the team can work in parallel and think clearly. |
| 3 | Prioritize the issues | Focus on the branches that matter most—those with the biggest impact and that are realistically changeable. |
| 4 | Develop a work plan | Decide what analyses to run, who will do them, how deep to go, and on what timeline (with iteration built in). |
| 5 | Conduct the analysis | Start with simple heuristics and descriptive statistics, then move to deeper analysis as needed; constantly test assumptions. |
| 6 | Synthesize the findings | Integrate results into a coherent, insight-driven answer—not just analysis—clearly addressing "What should we do?" |
| 7 | Communicate and motivate action | Tell a compelling story, acknowledge uncertainty, and drive alignment so the organization actually acts on the recommendation. |

**Core Operating Actions**

| Symbol | Meaning |
|--------|---------|
| **(n)** | McKinsey 7-Step Problem-Solving Process step number |
| 🔺 | Pyramid Principle (top-down, answer-first logic) |
| ◯ ◯ | MECE / Venn logic (complete, non-overlapping structure) |

### 1. Think Clearly
**Guiding Question:** Are we solving the right problem in the right way?

| Core Action | Toolkit Component |
|-------------|-------------------|
| Diagnose the current state to understand what is happening and why **(0)** 🔺 | Structured Problem-Solving |
| Define the problem (the gap between the current state and the desired state) **(1)** 🔺 | Structured Problem-Solving |
| Frame the problem: articulate the decision set for closing the gap and commit to success criteria, constraints, trade-offs, and what is in vs. out of scope **(1)** 🔺 | Structured Problem-Solving |
| State a provisional Day-1 hypothesis about which decision to make 🔺 | Structured Problem-Solving |
| Articulate explicit "what would have to be true" hypotheses for that decision to succeed **(3)** 🔺 | Structured Problem-Solving |
| Disaggregate those hypotheses into MECE issues designed to test them efficiently **(2)** ◯ ◯ | Structured Problem-Solving |
| Prioritize decision-critical issues and hypotheses based on likelihood of changing the decision and magnitude of impact **(3)** ◯ ◯ | Structured Problem-Solving |
| Explicitly exclude questions and analyses that would not change the decision | Structured Problem-Solving |

### 2. Get to the Right Answer
**Guiding Question:** What do the facts and data actually say?

| Core Action | Toolkit Component |
|-------------|-------------------|
| Design analyses to confirm or falsify priority "must-be-true" hypotheses **(5)** 🔺 | Analytics & Modeling |
| Build an outside-in fact base using best-available data **(5)** | Analytics & Modeling |
| State assumptions explicitly and identify appropriate proxies **(5)** ◯ ◯ | Analytics & Modeling |
| Perform back-of-the-envelope calculations to bound answers **(5)** | Analytics & Modeling |
| Build models and run sensitivities to understand drivers, uncertainty, and risk **(5)** ◯ ◯ | Analytics & Modeling |
| Synthesize analytical results into clear answers to the decision **(6)** 🔺 | Clear Communication |

### 3. Move Work Forward
**Guiding Question:** Is the work actually progressing toward a decision?

| Core Action | Toolkit Component |
|-------------|-------------------|
| Translate prioritized hypotheses into a concrete, decision-oriented workplan with milestones **(4)** 🔺 | Workstream Ownership |
| Own a workstream end-to-end, from decision-relevant question to answer | Workstream Ownership |
| Sequence work to deliver insight early and reduce decision risk | Workstream Ownership |
| Reprioritize tasks dynamically as new information changes the decision outlook | Workstream Ownership |
| Identify risks, dependencies, and bottlenecks before they stall progress | Workstream Ownership |
| Manage up with concise updates that surface implications for the decision | Workstream Ownership |
| Advance the work using best-available information, without waiting for certainty | Tolerance for Ambiguity |

### 4. Create Impact with People
**Guiding Question:** Do people understand, trust, and act on this work?

| Core Action | Toolkit Component |
|-------------|-------------------|
| Craft a storyline that links insights to the decision and its implications **(6)** 🔺 | Clear Communication |
| Communicate recommendations with clear logic, explicit trade-offs, and executive-level brevity **(7)** 🔺 | Clear Communication |
| Tailor messages to senior audiences and stakeholder concerns **(7)** 🔺 | Client Hands |
| Build trust by demonstrating judgment, reliability, and empathy | Client Hands |
| Coordinate effectively across team members to present a unified decision narrative | Teamwork & Collaboration |
| Actively solicit feedback and adjust thinking and output in response | Coachability |

### Toolkit Components Summary

| Component | Primary Imperative |
|-----------|-------------------|
| Structured Problem-Solving | Think Clearly |
| Analytics & Modeling | Get to the Right Answer |
| Clear Communication | Get to the Right Answer, Create Impact with People |
| Workstream Ownership | Move Work Forward |
| Tolerance for Ambiguity | Move Work Forward |
| Client Hands | Create Impact with People |
| Teamwork & Collaboration | Create Impact with People |
| Coachability | Create Impact with People |
