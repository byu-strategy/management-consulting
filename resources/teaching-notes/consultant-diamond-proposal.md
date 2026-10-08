# Consultant Diamond in STRAT 325: Proposal

*Instructor note, not published. Drafted 2026-10-08. Nothing here is wired into grades, Canvas, or `00-assessments.qmd`.*

The diamond is introduced to students in `02-consultant-diamond.qmd#consultant-diamond` as a development framework: four axes, the toolkit roll-up, and the verbatim anchors. This note proposes how 325 could collect ratings on it. Every option that touches points is a decision for Scott, and only for a term that has not started yet.

## What 325 already has

| Mechanism | Who rates | What it measures | Grade use today |
|---|---|---|---|
| Presentation feedback form (P1, P2, Capstone pods) | Pod members + TA | The presentation: Informed / Compelling / Credible, 1 to 4 | Developmental only. Points are for submitting forms for every pod member (15 per round) |
| Practice interview feedback form (per student copy) | Peer interviewers + TA | Behavioral and case rubric dimensions | Completion points only |
| Goals Worksheet self-assessment | Student | 1 to 4 on the six practice interview dimensions | Goals Chat points (10) |
| TA Mentoring Sessions (3) | TA | Practice interview, growth over the semester | Completion points (20 each) |
| Mid-semester self-reflection (`04-working-as-a-team.qmd`) | Student | Open | Not graded |

There is no peer evaluation of a teammate as a teammate. Most graded work is individual, so the pod is the only group that sees a student work with others over the whole semester.

Note a site inconsistency found while drafting: `04-working-as-a-team.qmd` says the capstone is done "in sub-teams of 3-4" and describes capstone team formation, while `index.qmd`, `00-assessments.qmd`, and `97-ta-handbook.qmd` list the Capstone as Individual. Which one is current determines whether a capstone team review is possible at all.

## Who can see which axis in 325

| Axis | Pod peers | TA | Self |
|---|---|---|---|
| Judgment | Good: they watch each other's cases and presentations | Good: three case interviews | Yes, with an instance |
| Ownership | Weak: little shared work to drive | Moderate: networking tracker, resume revisions, follow-through | Yes, with an instance |
| Communication | Good: decks and pod presentations | Good: P1, P2, Capstone feedback | Yes, with an instance |
| Collaboration | Good: interviewer feedback, pod Q&A, how feedback is taken | Good: coachability across three sessions | Yes, with an instance |

Ownership is the thin axis. Under the Foundry rule (an axis needs three independent raters), it may often need the TA rating plus two peers who saw it, and some students will show "not enough ratings."

## Option A (recommended for a first term): developmental pod diamond

No points change.

1. **End-of-semester pod review.** Each student rates each pod-mate once on the four axes, against the anchors, after the last pod presentation. The TA rates every student in the pod. Roughly five minutes per person.
2. **Same question per axis as the Foundry peer form** (`~/courses/ai-foundry/ops/developmentship-model.md`, section 4):
   - Judgment: Did they solve the right problem, and say what the facts supported?
   - Ownership: Did they drive the work, or wait to be told?
   - Communication: Could you tell the state of the work from what they wrote?
   - Collaboration: Did they make the people around them better, and do you want them on your next team?
3. **Evidence rule.** Any 1, 2, or 5 requires a specific instance; a rating without one is dropped.
4. **"Not observed" option** on each axis, so a peer who never saw Ownership does not guess.
5. **Self-rating first.** Add the four axes to the Goals Worksheet (start) and a closing self-rating (end), each with an instance. The self-rating closes before results are released and is never averaged in.
6. **Release.** Each student gets their diamond with the number of raters per axis, never who said what. An axis shows only with three or more raters. Written comments go to the TA and Scott and come back as themes.
7. **Use.** TA Mentoring Session 3 opens with the diamond and the gap between self and others.

Delivery: a Google Form built from `resources/pod-feedback-form.md` conventions (collect email, dropdowns of pod members), and a small script to aggregate per student and draw each diamond with `scripts/consultant_diamond.py`.

## Option B (future term): completion points for the review

Mirror the existing presentation feedback rule: points for submitting a review of every pod-mate, none for the ratings received. This needs points taken from somewhere, which changes Canvas weights and `00-assessments.qmd` together, and must be published before the term starts.

## Option C (not recommended for 325): score-based grade

The Foundry converts the diamond composite to 180 of 500 points with caps. That fits the Foundry because students share client work for weeks. In 325 the graded work is individual, peers share little work, Ownership is thinly observed, and pod-mates may be recruiting for the same firms. A score-based grade would rest on less observation than the Foundry has.

## Decisions for Scott

1. Option A, B, or neither, and for which term.
2. Is the Capstone individual or in sub-teams of 3-4? Fix the site either way; if teams, a capstone teammate review is the strongest Ownership evidence 325 could get.
3. Should TAs rate all four axes, or only Judgment, Communication, and Collaboration?
4. Add the diamond to the Goals Worksheet self-assessment (currently six practice interview dimensions), or keep it separate?
5. Should `97-ta-handbook.qmd` get a short section on using the diamond in Mentoring Session 3?

## Files a rollout would touch

- `00-assessments.qmd` (description of the review; points only under Option B)
- `00-schedule.qmd` and `scripts/sync_canvas.py` (Option B only)
- `04-working-as-a-team.qmd` ("Feedback in This Class" table)
- `97-ta-handbook.qmd` (TA rating and Session 3)
- `resources/create-goals-worksheet.js` (self-rating)
- A new form spec beside `resources/pod-feedback-form.md`
