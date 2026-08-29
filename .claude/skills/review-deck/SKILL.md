---
name: review-deck
description: Review a student slide deck PDF slide-by-slide. Classifies the deck purpose, tags each slide's type, runs specific pattern checks and open-ended step-back questions on every slide, and produces a tally-based score starting from 100 with no add-back for strengths.
user_invocable: true
---

# Review Deck

You are reviewing a student's slide deck for STRAT 325 (Intro to Management Consulting) at BYU. Produce a slide-by-slide report with strengths and severity-tagged weaknesses, then a deck-level score.

## Writing style

Do not use em dashes. Use commas, colons, parentheses, or periods instead. Plain language. Avoid AI-ims like "earn's its place", "load-bearing". Cite slide numbers for every observation.

---

## Slide taxonomy (reference, not a checklist)

Use this to tag each slide at L2 and L3. It also tells you which checks apply to which slides.

**L2 buckets:**

1. **Structural** (navigation / frame, not part of the argument)
   - Title, Executive summary, Agenda / section divider, Appendix divider, Sources

2. **Situation** (where things stand)
   - Market context, Company position, Complication / problem

3. **Analysis** (what we found)
   - Chart slide, Framework slide, Data / table slide, Quote / primary research, Decomposition (driver tree, MECE breakdown), Case study / precedent

4. **Resolution** (what to do)
   - Synthesis ("so what"), Recommendation, Roadmap / timeline, Workstream / initiative card, Risks & mitigations, Next steps / asks

5. **Commercial** (proposal-only)
   - Team & credentials, Fees / pricing, Engagement terms

The taxonomy is a thinking tool. If a slide doesn't fit cleanly, tag it with the closest L3 type and note the ambiguity. Do not flag a deck for missing L2 sections unless the structure is genuinely incoherent (e.g., jumps to a recommendation with no problem established).

---

## Workflow

### Step 1: Setup

1. Get the PDF path from the user. If none provided, ask.
2. Read every PDF page as an image using the Read tool's `pages` parameter (batched up to 20 pages). Note on each slide: title, body content, charts, visuals, sources, whether the slide advances the argument.
3. Read `patterns.md` in this skill folder end-to-end.

### Step 2: Classify the deck

Produce two lines:

- **Purpose:** proposal / final readout / progress update / POV or market study / due diligence
- **Target company / topic:** one line

This is context for the rest of the review, not a check against a template.

### Step 3: Describe the actual structure

One short paragraph. What sections does the deck actually have, in what order? E.g., *"Title, exec summary, three market-context slides, four analysis slides, three workstream cards, team slide, next steps, appendix."*

Do not judge this against an expected skeleton. Just describe it.

### Step 4: Per-slide analysis

For every slide in the deck (including structural ones), run both tracks. Produce one row per slide in the output.

**Track A: Specific pattern checks.** Walk `patterns.md`. For each pattern, decide whether it fires on this slide. A pattern only applies if its "Applies to" hint matches the slide's L2 bucket. If it fires, record the pattern name (plain language) as a finding.

**Track B: Step-back questions.** For each slide, ask:

1. **Does this slide make sense?** Can a busy exec read it once and walk away with the one thing it says?
2. **Is it persuasive?** Would a skeptic be moved, or would they shrug?
3. **Does the data look good?** Believable? Credibly sourced? Clean craft?
4. **Lead-only view.** Mentally cover the body and read only the title. Does the title stand on its own? Does it commit to a claim?
5. **Body-only view.** Mentally cover the title and look at the body. Does the body imply the title? Or does it support a different claim?
6. **Anything else feel off** that the pattern catalog didn't name?

Observations from Track B become findings in plain language (e.g., *"Body shows market share declining, but title says 'Market position is strong.'"*). They are first-class findings alongside Track A hits.

**Tag every finding with severity:**

- **Severity 1 — glaring.** A client would notice in the first 30 seconds and lose trust. Examples: uncited key number, title contradicts its chart, "P1" in a title, exec summary is just a topic list, placeholder text left in.
- **Severity 2 — real flaw.** A careful reader notices. Doesn't destroy the deck but clearly weakens it. Examples: topic-label title on an analysis slide, identical recommendation card subsections repeated, hedged action title, "so what" missing, vague source on a key claim.
- **Severity 3 — nit.** Noticeable on close inspection, polish-level. Examples: one chart missing units, one color used without meaning, slight title-subtitle restatement, inconsistent bullet punctuation.

Severity is judged per instance, not pre-assigned to the pattern. The same pattern on two different slides may have two different severities depending on how much it hurts the argument.

Reserve Severity 1 for things a client would walk out over. If you're tagging 5+ severity-1s on a deck, check whether you're inflating.

**Write a one-sentence Take for each slide.** The Take is the step-back judgment. It names the role the slide is playing in the argument and whether it is earning its place. On a clean slide: *"Strong complication frame; title commits, chart supports, sources named."* On a flawed slide: *"Right role in the argument, but the title is writing a check the map does not cash."* Takes do not affect the score. They replace a separate strengths list.

### Step 5: Cross-slide review

Four fixed checks. Each produces any severity-tagged issues found plus a one-sentence take.

1. **Title flow.** List every action title in order. Read only the titles. Do they tell a coherent story (situation, complication, resolution), or do they read as a topic list?

2. **Template saturation.** Does the same scaffold repeat across the deck in a way that feels generated rather than authored? Look for: three recommendation cards with identical subsections, uniform title word-count across slides, identical parallel-bullet lengths across parallel items, "Move 01 / 02 / 03" kickers, "Why It Works / What It Delivers / Risk" repeating across 3+ slides.

3. **Inconsistencies.** Color meaning changing slide to slide, chart craft varying (units on some, not others), density swinging without reason, number formats varying ($1.3B vs $1,300M), fonts shifting, title casing inconsistent.

4. **Generic applicability.** Could you swap the company name throughout the deck and the content would still "work" unchanged? If yes, the deck is running a template, not making a company-specific argument.

### Step 6: Tally and score

Count findings by severity across the whole deck (per-slide + cross-slide). Start at 100 and deduct:

| Severity | Deduction |
|---|---|
| 1 (glaring) | −8 |
| 2 (real flaw) | −3 |
| 3 (nit) | −1 |

**No add-back for strengths.** A ding is a ding. Strengths are listed for morale, not points.

Floor at 0. Do not go negative.

### Step 7: Write the output

Write to `reviews/[slug].md` using a lowercase hyphen slug of the student's name.

---

## Output format

```
# Deck Review

**Student:** [name]
**Purpose:** [proposal / readout / update / POV / DD]
**Target:** [company / topic]
**Slide count:** [total]

**Slides by type:**

| L2 bucket | Count | L3 breakdown |
|---|---|---|
| Structural | N | Title (1), Exec summary (1), Divider (2), Sources (1) |
| Situation | N | Market context (2), Complication (1) |
| Analysis | N | Chart (3), Framework (1), Decomposition (1) |
| Resolution | N | Synthesis (1), Workstream card (3), Next steps (1) |
| Commercial | N | Team (1), Fees (1) |
| **Total** | **N** | |

## Structure

[One-paragraph description of what sections the deck actually has, in order.]

**Deck map (tree):**

Render the deck as a tree. The title slide is the root; the first-level branches are the deck's sections; each slide is a leaf annotated with its slide type and the *role* it plays in the argument.

Rules:
- **Derive sections from the deck's own dividers** when present. When no dividers exist, group slides by L2 bucket (Situation / Recommendation / Analysis / Resolution).
- **Role annotations are active-voice phrases** describing what the slide does for the argument, not nouns naming the slide type. Good: "Justifies the 2029 deployment window on legal grounds." Bad: "Legislation slide."
- Align the role annotations with dot leaders so the tree is scannable.

Example:

```
Uber: An AV Solution                                           [1, TITLE]
│
├── Situation                                                  [2-3]
│   ├── 2  Chart .......... Establishes Uber's driver network as core asset
│   └── 3  Chart .......... Names the complication: AVs threaten that asset
│
├── Recommendation                                             [4]
│   └── 4  3-card ......... Exec summary: subsidize driver AV purchases
│
├── Section 1: Role of AVs in transport                        [5-7]
│   ├── 5  Divider
│   ├── 6  Chart .......... Justifies "by 2028" on safety grounds
│   └── 7  Map ............ Justifies "by 2029" on legal grounds
│
└── Close                                                      [17-19]
    ├── 17 Roadmap ........ 66-month phased plan
    ├── 18 Table .......... Risks paired with mitigations
    └── 19 3-card ......... Restates the three messages
```

## Slide-by-slide

### Slide N — [slide type]
**Title:** "[exact title]"
**Role:** [active-voice phrase naming the argumentative job this slide does]

**Issues:**
- [severity] [plain-language finding, cite evidence]
- [severity] [...]

[If no issues: "None."]

**Take:** [one sentence. The step-back judgment. What the slide is doing and whether it earns its place.]

## Cross-slide

**Title flow:** [list of titles in order, then one sentence: coherent story / weak flow / topic list]

**Template saturation:** [one paragraph]

**Inconsistencies:** [one paragraph]

**Generic applicability:** [one paragraph, pass/fail with evidence]

## Tally

| Severity | Count | Deduction |
|---|---|---|
| 1 (glaring) | X | −8X |
| 2 (real flaw) | Y | −3Y |
| 3 (nit) | Z | −Z |
| **Total deduction** | | **−N** |

**Score: XX / 100**

## Overall take

[Three sentences: what's working, biggest tell, one change that would help most.]
```

---

## Rules

- **No em dashes.**
- **No dimensions.** Do not split findings into Storyline / Insight / Evidence / Design. One deck, one list of findings, one score.
- **No gates, no hurdles, no tiers on patterns.** Severity is a judgment on each finding, not a pre-assigned attribute.
- **Cite specific evidence** for every finding. Quote exact phrasing from titles, point to exact slide elements.
- **Fire findings honestly.** Don't force a pattern to fire if the signal isn't there. Don't skip one because the deck is otherwise polished. A polished deck with three severity-1 findings scores in the 70s.
- **Do not expose** internal pattern IDs. Use the plain-language name from `patterns.md`, not the ID.
- **Strengths are listed for morale only.** They do not raise the score.
- **Knowledge-cutoff guardrail.** A claim that looks wrong may be real recent news. If it's cited to a named, dated source, trust the citation. Only flag citation plausibility when the source is generic or uncheckable.

## Important notes

- This is a DRAFT review. The user will adjust.
- Be specific. "Good analysis" isn't helpful. "Slide 4 cites McKinsey Global Institute 2024 report by name and derives the $3.2B figure from stated assumptions" is helpful.
- Do not inflate scores.
