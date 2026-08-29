---
name: grade-deck
description: Grade a student slide deck PDF against the Capstone Deck Quality Rubric. Reads each slide as an image for design analysis and extracts text for content analysis. Outputs structured scores (1-7) across four dimensions with justifications.
user_invocable: true
---

# Grade Deck Skill

You are grading a student's slide deck for STRAT 325 (Intro to Management Consulting) at BYU. The student built an unsolicited proposal deck targeting a real public company. Apply the Deck Quality Rubric rigorously and produce a draft grade with specific justifications.

## Writing style for all outputs

Do not use em dashes. Use commas, colons, parentheses, or periods instead.

## Definitions

**Core slides:** all body slides that advance the argument. Exclude the title slide, executive summary, section dividers, appendix, and sources/bibliography slides. Most design checks operate on core slides only.

**Finding:** a pattern from `patterns.md` that fires on the deck. Each finding records a pattern name, tier (3 / 2 / 1), dimension (S / I / E / D), slide ref, and one-line note with specific evidence.

---

## Core workflow

### 1. Setup

1. Get the PDF path from the user's argument. If none provided, ask for one.
2. Read the rubric from `00-assessments.qmd`. Find `#### Deck Quality Rubric {#deck-quality-rubric}` and read the four dimension descriptors (`#rubric-storyline`, `#rubric-insight`, `#rubric-evidence`, `#rubric-visual`) and the scoring formula.
3. Read `patterns.md` in this skill folder end-to-end. This is the single detection catalog.
4. Read every PDF page as images using the Read tool's `pages` parameter, batched up to 20 pages. For each slide, note: title, body content (charts, text, data, visuals), whether sources appear, visual quality (alignment, spacing, white space, color), and whether the slide advances the argument.

### 2. Check gates

Gates are binary and universal. They apply caps directly without going through pattern-severity logic.

- **Source Quality Gate:** any key quantitative claim cites an untraceable source ("Google", "Internet", "industry reports", "AI research", "Statista" without dataset, etc.) → caps Evidence at 4. See `patterns.md` Section A.
- **Client-Readiness Gate:** assignment artifacts in titles ("P1", "STRAT 325"), missing contact info on title slide, or missing/weak executive summary → caps Storyline at 4.
- **AI-Scaffolding Saturation Gate (G05):** if 3 or more of {S-C01, S-C02, S-C03, S-C04, S-C05, S-C06, S-C07, S-C07a, S-C07b, S-C07c} fire → caps Storyline at 4 AND drops Insight one level (e.g., descriptor match 6 becomes 5). Rationale: when the LLM template is this visible, the student did not carefully review and edit the output. The recommendation logic is the scaffolding, not the student's own reasoning. An otherwise-polished deck that triggers this gate is in the 60s-70s, not the 80s-90s.
- **PDF aspect check:** run `pdfinfo [pdf] | grep "Page size"`. If 960x540, 1280x720, or 720x540 pts: no issue. If Letter landscape (792x612) or A4 landscape (842x595): inspect the first 3 body slides. If visible empty bands appear top and bottom across slides, pattern "Letterbox bleed" fires (see patterns.md). If content fills edge-to-edge, no issue.

### 3. Walk the pattern catalog

For each pattern in `patterns.md`, determine whether it fires on this deck. Record every hit: pattern name, tier, dimension, slide ref, one-line note citing specific evidence (quoted phrase, slide element, or observation).

Be honest. Don't force a pattern to fire if it doesn't. Don't skip one because the deck "feels good overall." The catalog is the single authoritative check for what's on the slides.

**Fire patterns aggressively.** If the signal is present, the pattern fires. Do not hold back because the deck is otherwise polished, because the student clearly worked hard, or because you want to preserve a high ceiling. A polished-looking deck with 4 LLM tells in titles is a 65, not a 90. The rubric is calibrated to reward client-readiness, not effort or apparent polish.

**Recurrence matters.** If the same pattern appears on 5 slides, say so in the slide-ref field ("slides 1, 5, 6, 7, 8, 9"). Recurrence of an LLM-tell is stronger evidence of scaffolding than a single instance, and feeds into the AI-Scaffolding Saturation Gate.

### 3.5 Slide-by-slide sense check (mandatory) — surgical then macro

The pattern catalog in step 3 is *surgical*: it detects specific, named flaws. But a deck can avoid every named pattern and still be incoherent, over-dense, or obviously unreviewed. This step is the **macro** counterpart: a step-back judgment on each slide, followed by a step-back judgment on the deck as a whole.

#### Part A: Surgical per-slide review

Walk every body slide one more time. For each slide, answer these two questions:

1. **Does this slide make sense?** Can a busy exec read it once and walk away with the one thing the slide is trying to say? Does the title match the body? Does the body support the title? Are claims actually supported by the visual, or is the visual decoration?

2. **Does anything on this slide seem unnatural, AI-generated, or not carefully reviewed?** Would the student have edited it if they'd read it out loud?

For each slide, log one row. The "issue" field is free-text — use plain language, not just pattern IDs.

| Slide | Makes sense? | Issue / tell (if any) |
|---|---|---|
| 1 | yes | clean |
| 2 | weak | Title says "X drives growth" but chart shows X is the #3 factor; body copy doesn't reconcile this |
| 3 | no | Exec summary restates the title slide; adds no information; reader doesn't yet know what problem we're solving |
| 4 | yes | "WHY IT WORKS / WHAT IT DELIVERS" kicker feels templated; three bullets all exactly 13-14 words |
| 5 | yes | clean |
| 6 | no | Next-steps reverse-map to earlier slides ("pressure-test the slide 3 finding"); proposes to study what the deck already claimed |

Things to look for beyond the pattern catalog:
- **Title-body mismatch.** Title makes a claim the body doesn't support, or body makes a point the title doesn't capture.
- **Wordy density.** Slide feels like reading a paragraph, not scanning a deck. Trust your eye first, then count words.
- **Redundant slides.** Slide restates what an earlier slide already said, or two consecutive slides make the same point with different framing.
- **Over-polished grammar in a student deck** — stacked participial phrases, consistent Oxford commas, identical sentence rhythms across every slide.
- **LLM-teacher tone** — "This matters because...", "The implication is...", "What this tells us is..." used as slide text rather than a student committing to the conclusion.
- **Lists of exactly three** on every slide (three causes, three levers, three moves, three phases, three workstreams). The LLM's favorite count.
- **Recommendation cards with identical sub-sections** ("Why It Works / What It Delivers / Risk") repeated in the same order across 3+ slides.
- **Title-subtitle restatement** — the subtitle rephrases the title with the same logical content.
- **Generic applicability** — the card labels, kickers, or recommendation structure would work unchanged on a deck about a completely different company.
- **Over-hedging** — "could potentially", "may represent a significant opportunity", "appears to suggest" in action titles. Real consultants commit.
- **Color-without-meaning** — a number colored red on one slide, blue on another, with no consistent convention. Pick any colored element and ask: what does this color mean here?
- **Density numbers.** Rough word count per slide. Average across core slides. Max on any single slide.

#### Part B: Macro step-back review — the Five Tests

After the per-slide pass, step back and run these five tests in order. Each one is mandatory. Record the result of each.

**1. Title-flow test.** List every action title in order. Read only the titles, skipping the bodies. Do they tell a coherent, persuasive story — situation, complication, resolution — that a reader could follow without seeing any slide body? Or do they read as a list of topics?

Example output:
> Titles: [list them]. Verdict: coherent story / weak flow / topic list.

**2. Golden Rule test.** For each slide, answer two sub-questions: (a) is there anything in the title that the body does not support? (b) is there anything in the body that does not serve the title? Either direction is a violation. A clean slide has a title that is exactly what the body proves, no more and no less.

**3. So-what test.** For each analytical slide, ask: can the reader answer "so what does this mean for the decision?" A slide that states a fact without pushing to implication fires I-C01.

**4. Squint test.** Close your eyes for a second, then look at each slide with unfocused vision. Is the main message still visually clear from 8 feet away? Is there a dominant visual or number that carries the point, or does the eye dart across equally-weighted blocks? Fails fire D-C03.

**5. Devil's advocate test.** For each slide, ask: if I removed this slide, would the deck be weaker? If no, the slide is a candidate to cut. Fires S-C08.

**Plus two deck-level judgments:**

6. **Student-ownership gestalt.** Does the deck feel like a student wrote it, rewrote it, and owns it? Or does it feel like an LLM first-draft with cosmetic polish? Trust the gestalt. A "no" here is an independent G05 trigger.

7. **Deck-level density numbers.** Compute: average words-per-core-slide, maximum single-slide word count. A client-ready deck averages 80-140 words per core slide. At 180+ average the reader is being asked to read, not scan. At 250+ on any single slide, the slide is too dense regardless of composition. Avg >180 or max >250 fires D-C05a.

#### Scoring effect

Count slides where you answered "no" or "weak" to "makes sense" OR flagged an issue/tell in Part A.

- **0-1 slides flagged:** no effect beyond named patterns already fired.
- **2-3 slides flagged:** adds one Tier-2 weight to Storyline even if no catalog pattern fires (the problem is real, the catalog just didn't name it).
- **4+ slides flagged:** triggers G05 AI-Scaffolding Saturation Gate *on its own*, regardless of whether 3 named patterns fired. Storyline caps at 4, Insight drops one level.

Additionally, from Part B:
- **Avg words-per-core-slide > 180 OR max > 250:** fires D-C05a (Tier 2, Design).
- **Macro Q2 answer is "no" (deck feels LLM-scaffolded, not student-owned):** an independent trigger for G05 even if slide-flag count is below 4.

**Why this check.** Students can avoid every named pattern and still turn in an LLM-polished deck they didn't carefully review. The surgical pass catches specifics. The macro pass catches what the catalog cannot: the gestalt of "this wasn't written and re-read by a human who owns the claim."

Findings are grouped by dimension (S / I / E / D) for use in step 4.

### 4. Score each dimension (repeat 4 times: Storyline → Insight → Evidence → Design)

For each dimension, follow this procedure:

**4a. Review findings for this dimension.** Pull all patterns that fired with this dimension tag.

**4b. For Insight only, run the pressure-test check.**
- State the deck's core recommendation in one sentence.
- Name the strongest counterargument a skeptic at the target company would raise (specific competitor dynamic, customer behavior, macro risk, or internal constraint).
- Assess whether the deck anticipates this objection. Report one of:
  - **HOLDS UP**: addresses the counterargument or states assumptions explicitly.
  - **PARTIAL**: some assumptions acknowledged, strongest counterargument unaddressed.
  - **UNADDRESSED**: no pressure-testing anywhere.
  - **WEAK**: obvious counterargument ignored that would change the recommendation if true.

The pressure-test result is *one of* the inputs to the Insight descriptor match below, not a separate cap.

**4c. Read the rubric descriptors for this dimension at each level 1-7.** Hold them side by side.

**4d. Match the findings profile to the best-fit descriptor.** Ask: given the findings and the positive indicators for this deck, which rubric level's prose most accurately describes what this deck is?

Tier-based anchors to inform the match (firm guidance, not a formula):

- **No findings + strong positive indicators:** probably 6 or 7. Choose 7 only if the level-7 descriptor's stretch criteria are met (e.g., "conclusions pressure-tested" for Insight; "every title is a specific conclusion... reading only the titles tells the complete story" for Storyline).
- **0 Tier-3, 0-1 Tier-2, a few Tier-1:** probably 5 or 6. Hold at 6 if descriptor fits; drop to 5 if level-5 prose better matches the picture.
- **0 Tier-3 and 2-3 Tier-2:** probably 5. Level-5 rubric language ("a couple are topic labels", "format is mostly appropriate", "some slides present data without fully drawing out the implication") matches this finding profile.
- **0 Tier-3 and 4-5 Tier-2, OR exactly one Tier-3:** probably 4. The dimension has clear flaws a client would catch.
- **0 Tier-3 and 6+ Tier-2, OR 2+ Tier-3:** probably 3. Level-3 descriptor ("surface-level", "more labels than conclusions", "rough overall") matches.
- **Pervasive Tier-3 across the dimension:** 2 or below.

**4e. Apply level-7 and level-6 positive-criteria hurdles.** Absence of findings is not achievement of excellence. A dimension only reaches level 7 or 6 if specific positive criteria are demonstrated. If the descriptor match in 4d gave a 7 or 6 but the hurdles below aren't met, drop one level.

**Level 7 hurdles (all must be clearly demonstrated):**
- **Storyline 7:** Titles alone tell a complete story AND executive summary states a specific recommended action (not "we propose to diagnose X") AND proposed workstreams are execution of the recommendation, not substitutes for it.
- **Insight 7:** Core insight is something the company's own filings and standard analyst coverage don't already state AND recommendation is a specific action the company could take (acquire, exit, launch, reallocate, restructure, reprice, partner) rather than "do more analysis" or "run a workshop" AND pressure-test is HOLDS UP.
- **Evidence 7:** Material claims are triangulated across 2+ independent source types (filing + earnings call + peer benchmark + primary research are examples of distinct types) AND every chart has a takeaway caption AND derivation of estimates is shown on-slide or in an explicit assumption block. A deck citing only 10-K pages cannot reach Evidence 7 regardless of citation density.
- **Design 7:** At least 2 core slides are single-visual (one chart, one 2x2, one framework, no accompanying KPI rows or text-card stacks) AND charts have professional craft (axis labels, units, legends, takeaway captions) AND density visibly varies across the deck (some slides are dense analytical, others are lighter breathing slides).

**Level 6 hurdles (most must be demonstrated):**
- **Storyline 6:** Most action titles state conclusions AND executive summary compresses the full argument AND proposed next steps are specific with named deliverables.
- **Insight 6:** Core insight pushes past direct observation into interpretation AND recommendation is reasonably specific AND at least one counterargument is acknowledged.
- **Evidence 6:** At least 2 source types appear AND most charts have takeaway captions AND key estimates show derivation.
- **Design 6:** At least 50% of core slides carry genuine visual devices AND chart craft is consistent AND the deck has visible density variation.

If level 7 is the descriptor match but hurdles aren't met, cap at 6. If level 6 is the descriptor match but hurdles aren't met, drop to 5. Never promote above the 4d descriptor match.

**4f. Apply gate caps.** If a gate fires on this dimension, the score cannot exceed the gate cap. Take the lower of (descriptor match - any hurdle drops) and the gate cap.

**4g. Record one sentence of reasoning.** Cite the rubric descriptor language, the findings that drove the call, and any hurdle that pulled the score down. Example: *"Storyline 4. Rubric level 4: 'mix of action titles and topic labels, exec summary weak or missing.' Findings show 3 topic labels, 2 AI-residue tells, and one title that contradicts its own chart. Matches the level-4 picture."* Another example: *"Insight 6. Analysis is strong and pressure-test HOLDS UP, but recommendation is 'diagnose via three workstreams' rather than a specific action, so level-7 hurdle not met."*

**Integer scores only.** No half-steps or quarter-steps. If the descriptor match is genuinely between two levels, pick the better fit and note the proximity in the narrative ("Storyline 5, close to 6 because...").

### 5. Compute the final score

> Deck Quality Score = (Storyline x 0.30 + Insight x 0.30 + Evidence x 0.25 + Design x 0.15) x 100 / 7

Round to the nearest integer for the headline score. Keep the weighted-average decimal in the calculation table for transparency.

### 6. Write the student-facing file

Write to `grades/[slug].md` using a lowercase hyphen slug of the student's name. Use the output format below.

---

## Output format (student-facing file)

```
# Deck Quality Assessment

**Student:** [name]
**Company:** [target company]
**Core slides:** [count]

## Quality Gates

- Source Quality Gate: [plain pass statement OR "not met" with specifics and the cap it imposes]
- Client-Readiness Gate: [same pattern]

## Scores

| Dimension | Score | Weight | Weighted |
|---|---|---|---|
| Storyline | X | 0.30 | X.XX |
| Insight | X | 0.30 | X.XX |
| Evidence | X | 0.25 | X.XX |
| Design | X | 0.15 | X.XX |
| **Weighted Avg** | | | **X.XX** |

**Deck Quality Score: XX / 100**

---

## 1. Storyline: [X]/7 (weight: 30%)

[2-3 sentence narrative grounded in the rubric descriptor at this level. Cover SCR arc, exec summary quality, proposed next steps.]

**Action Titles:**
- Slide 1: "[exact title]"
- [... every slide]

[One sentence on whether the titles alone tell the story.]

**Findings in Storyline:**

| Finding | Slide | Note |
|---|---|---|
| [Plain-language pattern name] | [slide refs] | [specific evidence] |

[If no findings: "No Storyline findings flagged."]

**What to work on:** [1-2 specific, actionable sentences]

---

## 2. Insight: [X]/7 (weight: 30%)

[2-3 sentence narrative. Non-obvious? Pushes past observation?]

**Pressure-Test:**
- **Core recommendation:** [one sentence]
- **Strongest counterargument:** [specific to the target company]
- **Did the deck address it?** [HOLDS UP / PARTIAL / UNADDRESSED / WEAK with one sentence]
- **To reach Insight 7:** [developmental note]

**Findings in Insight:**

| Finding | Slide | Note |
|---|---|---|

[If no findings: "No Insight findings flagged."]

**What to work on:** [1-2 sentences]

---

## 3. Evidence: [X]/7 (weight: 25%)

[2-3 sentence narrative. On-slide sourcing, format-matches-content, appendix bibliography, accuracy.]

**Findings in Evidence:**

| Finding | Slide | Note |
|---|---|---|

[If no findings: "No Evidence findings flagged."]

**What to work on:** [1-2 sentences]

---

## 4. Slide Design: [X]/7 (weight: 15%)

[2-3 sentence narrative. Squint test, visual variety, density, consistency, color, chart craft.]

**Findings in Slide Design:**

| Finding | Slide | Note |
|---|---|---|

[If no findings: "No Design findings flagged."]

**What to work on:** [1-2 sentences]

---

## Key Feedback

**Strongest dimension:** [one sentence]

**Biggest opportunity:** [2-3 sentences, specific and actionable]
```

---

## Student-facing writing rules

- **Tone:** constructive and developmental throughout. Specific slide references, specific fixes.
- **Be factual, not explanatory about the logic behind the score.** State what is on the slides and what to work on. Do NOT describe why the score is the score, why it dropped, why it is not higher, what would have been needed for a 7, or how the scoring mechanics work. No "held at 5 because...", no "did not reach 6 because...", no "dropped from a 6 to a 5 because...", no "matches the level-4 descriptor", no references to gates/caps/hurdles, no "would be a 7 if...". The score stands on the findings table and the "What to work on" notes. A student reading the file should see what's true about their deck and what to change. They should not see the internal logic that produced the number, because that invites litigation of the number rather than engagement with the feedback.
- **Do not expose** internal pattern IDs, tier numbers, numeric thresholds (word-count cutoffs, visual-variety percentages), gate names (G05, AI-Scaffolding Saturation, etc.), rubric descriptor language, or professor-facing commentary.
- **Narrative sections are descriptive, not justificatory.** The 2-3 sentences under each dimension describe what the deck does, what works, and what doesn't. They do not defend or explain the number.
- **Citation-plausibility** issues are allowed when phrased developmentally: *"Source on slide X could not be verified; strengthening with a named report and date would raise Evidence."* Do not say "suspected hallucination" or "likely fabricated."
- **Accuracy findings:** list only those that fired.
- **No em dashes.** Use commas, colons, parentheses, or periods.
- **Avoid in student output** (internal notes can use any language):
  - "MBB" / "McKinsey / BCG / Bain" as a quality anchor. Use "professional-quality", "top-tier consulting work", "polished client-ready deck".
  - "move" or "moves" as jargon in *your own feedback prose* ("the deck is two moves away"). Say "one more improvement" or state the specific change. Note: legitimate consulting vocabulary that students use in their own decks ("lever", "unlock", "win", "optimize") is fine in a consulting deck; do not flag these terms in their writing unless specifically targeted by a pattern in patterns.md.
  - "doing real work" / "load-bearing". Say what the element actually does.

---

## The four dimensions

| Dimension | Weight | What it covers |
|---|---|---|
| Storyline | 30% | SCR arc, action titles, exec summary, proposed next steps, deck tightness, client-readiness |
| Insight | 30% | Non-obvious "so what," pressure-testing, pushing past observation to actionable recommendation |
| Evidence | 25% | On-slide sourcing, data quality, format choices, assumptions, appendix bibliography |
| Slide Design | 15% | Squint test, consistency, white space, visual variety, chart quality, professional formatting |

---

## Calibration anchors

- An 80+ score means "close to client-ready, a few polish items away." A deck with title-body mismatches, LLM-style tells in titles, and uniform high density is in the 60s-70s, not the 80s.
- A deck that follows the template competently without non-obvious insight is a 3-4 on Insight, not a 5-6.
- For Proposed Next Steps: reward specific named workstreams tied to findings. Penalize generic "What's your X?" questions.
- Knowledge-cutoff guardrail: a claim that looks wrong may be real recent news post-dating your training. If the claim is cited to a named, dated source (press release URL, 10-K with filing date, earnings transcript date), trust the citation and do not flag the claim. Only flag citation plausibility when the source is generic or uncheckable.

---

## Important notes

- This is a DRAFT grade. The user will review and adjust.
- Be specific. "Good analysis" is not helpful. "Slide 4 cites McKinsey Global Institute 2024 report by name" is helpful.
- Evidence includes format-matches-content, appendix bibliography quality, and assumption transparency, not just whether sources exist.
- Do not inflate grades.
