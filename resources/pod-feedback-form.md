# Pod Feedback Form

*Use this to build a Google Form for P1, P2, and Capstone presentations.*

---

## Form Settings

- **Collect email addresses**: Yes (for tracking)
- **Limit to 1 response**: No (they submit multiple per session)
- **Edit after submit**: Yes

---

## Section 1: Basics

### Question 1: Your Name
- **Type**: Dropdown
- **Required**: Yes
- **Options**: [List of all students]

### Question 2: Presenter Name
- **Type**: Dropdown
- **Required**: Yes
- **Options**: [List of all students]

### Question 3: Project
- **Type**: Dropdown
- **Required**: Yes
- **Options**:
  - P1: Intelligence Brief
  - P2: Point of View
  - Capstone: Conversation Deck

---

## Section 2: Instructions

**Section description** (display as text, no question):

> Put yourself in the shoes of someone at the presenter's target company — a strategy director, business unit lead, or chief of staff. You're busy. You get cold outreach all the time. As you watch this presentation, ask yourself: *Would I take this meeting?*

---

## Section 3: Ratings

### Question 4: Informed
- **Type**: Multiple choice (single select)
- **Required**: Yes
- **Question text**: Do they understand my world?
- **Options**:
  - 4 — Yes: They've done their homework and surfaced tensions I'd recognize as real
  - 3 — Mostly: Solid understanding with minor gaps or oversimplifications
  - 2 — Somewhat: They get the basics but miss nuances I'd expect them to know
  - 1 — No: This feels like a surface-level read; they don't really understand my situation

### Question 5: Compelling
- **Type**: Multiple choice (single select)
- **Required**: Yes
- **Question text**: Would I want to explore this opportunity?
- **Options**:
  - 4 — Yes: This is worth my time; I want to dig into this with them
  - 3 — Probably: There's something interesting here worth a conversation
  - 2 — Maybe: I'd need more convincing before I'd give up 20 minutes
  - 1 — No: Nothing here makes me want to continue this conversation

### Question 6: Credible
- **Type**: Multiple choice (single select)
- **Required**: Yes
- **Question text**: Would I trust this person?
- **Options**:
  - 4 — Absolutely: Sharp, prepared, handled my questions like they've done the work
  - 3 — Yes: Professional and competent, knows their material
  - 2 — Somewhat: A few gaps or shaky moments made me wonder
  - 1 — Not really: I wouldn't trust them with a real project

---

## Section 4: Written Feedback

### Question 7: One Strength
- **Type**: Short answer (or Paragraph)
- **Required**: Yes
- **Question text**: What would make someone at this company say yes?

### Question 8: One Thing to Work On
- **Type**: Short answer (or Paragraph)
- **Required**: Yes
- **Question text**: What would most increase their chances of getting the meeting?

---

## Section 5: The Gut Check

### Question 9: Would You Take This Meeting?
- **Type**: Multiple choice (single select)
- **Required**: No
- **Question text**: If you were at this company, would you take this meeting?
- **Options**:
  - Yes — I'd make time
  - Probably — if my calendar allowed
  - Unlikely — I'd need a stronger hook
  - No — I'd pass

---

## Scoring Reference (for TAs)

This is not on the form — use for calculating Capstone grades.

| Dimension | Weight | 4 pts | 3 pts | 2 pts | 1 pt |
|-----------|--------|-------|-------|-------|------|
| Informed | 40% | 24 | 18 | 12 | 6 |
| Compelling | 40% | 24 | 18 | 12 | 6 |
| Credible | 20% | 12 | 9 | 6 | 3 |
| **Total** | 100% | **60** | **45** | **30** | **15** |

**Capstone calculation**:
1. Average each dimension across all raters
2. Convert: (average rating / 4) × max points
3. Sum all three dimensions

*Example*: Informed avg 3.2, Compelling avg 3.5, Credible avg 3.0
- Informed: (3.2/4) × 24 = 19.2
- Compelling: (3.5/4) × 24 = 21.0
- Credible: (3.0/4) × 12 = 9.0
- **Total: 49.2 / 60 pts**

---

## Tracking Completion (for TAs)

Use a pivot table or matrix to verify each student submitted for all pod members:

| Rater | Alice | Bob | Carol | ... | Complete? |
|-------|-------|-----|-------|-----|-----------|
| Alice | — | ✓ | ✓ | ... | 6/6 ✓ |
| Bob | ✓ | — | ✗ | ... | 5/6 ✗ |

**Points**:
- P1/P2: 15 pts if all forms submitted, 0 if any missing
- Capstone: 20 pts if all forms submitted, 0 if any missing
