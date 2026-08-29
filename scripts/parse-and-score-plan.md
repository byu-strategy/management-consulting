# Parse & Score Plan

Plan for a deterministic deck-grading pipeline: parse a slide deck once into a rich JSON dossier, then derive scores as a pure function over the JSON.

**Prerequisite reading** (self-contained; you don't need the conversation that produced this):

- `scripts/slide-atoms-v3.md` — the 29-atom taxonomy (empirically validated across 11 decks)
- `scripts/slide-element-taxonomy.md` — derivation notes and stress-test results
- `.claude/skills/grade-deck/SKILL.md` — current (prose) grading workflow and rubric logic
- `.claude/skills/grade-deck/patterns.md` — current pattern catalog
- `00-assessments.qmd` — search for `#### Deck Quality Rubric {#deck-quality-rubric}` for the four dimension descriptors

---

## Why this architecture

Current `grade-deck` skill re-queries images for every pattern check. Vision calls are the expensive part; every rubric change, every iteration, every regrade re-pays that cost.

**New architecture:** parse each deck once into a rich JSON observational dossier. Then grading becomes pure text processing over that JSON. Vision touches the deck exactly once.

Principles:

1. **Observations, not judgments.** The parse records *what is on the slide*. The grader decides *what that means for the rubric*.
2. **Pure function from JSON to score.** `score_deck(deck.json, rubric.yaml) → scoring.json`. Same input → same output. Reproducible, cacheable, auditable.
3. **Cast a wide net at parse time.** Over-observe, under-judge. Anything the rubric might ask should be derivable from the parse without re-looking at images.
4. **Calibration first.** Before writing scoring code, parse one known-graded deck and manually walk the scoring. Validate the data dictionary captures what's needed.

---

## Artifact structure

One directory per deck:

```
grading-artifacts/<deck-id>/
├── deck.json               # the full dossier (schema 1.0, atoms v3)
├── deck.meta.json          # parse model, prompt version, timestamps  (could fold into deck.json)
├── slides/
│   ├── s01.png             # 150 DPI renders
│   ├── s02.png
│   └── ...
└── scoring.json            # downstream artifact: findings + scores
```

One file (`deck.json`) is the machine-readable source of truth. JSON-only; no markdown projection needed. The PDF is the human-readable reference.

Rubrics live separately and consume the parse artifacts:

```
rubrics/
├── deck-quality-rubric.yaml       # Murff rubric, for capstone decks
├── case-writeup-bryce.yaml        # Bryce rubric, for STRAT 411 case write-ups
└── ...
```

A single `deck.json` can be scored by any rubric. That's the payoff of investing in a rich rubric-agnostic parse.

---

## The `deck.json` schema

```json
{
  "schema_version": "1.0",
  "atoms_version": "v3",
  "meta": {
    "deck_id": "collin-powell",
    "source_pdf": "grades/pdfs/collin-powell.pdf",
    "parsed_at": "2026-04-22T20:00:00Z",
    "parse_model": "claude-sonnet-4-6",
    "prompt_hash": "<sha256 of prompt template>",
    "slide_count": 9,
    "page_size_pts": [960, 540]
  },

  "deck": {
    "features": { ... },
    "observations": { ... }
  },

  "slides": [
    {
      "index": 1,
      "image_path": "slides/s01.png",
      ...per-slide fields...
    },
    ...
  ]
}
```

Deck-level cross-slide observations reference slides by index (e.g., `{"color": "red", "slides": [3, 4, 7], "detail": "..."}`). No separate cross-reference file needed.

---

## Data dictionary — per-slide

### Identity

| Field | Type | Notes |
|---|---|---|
| `index` | int | 1-based position in deck |
| `image_path` | string | relative path to slide PNG |
| `page_number_shown` | int \| null | number printed on the slide (may differ from index) |

### Classification

| Field | Type | Notes |
|---|---|---|
| `role_guess` | enum | `title` / `executive-summary` / `section-divider` / `agenda` / `analytical-body` / `recommendation` / `workstream` / `risks` / `appendix` / `bibliography` / `closing` / `disclaimer` / `other` |
| `density` | enum | `sparse` / `moderate` / `dense` / `very-dense` |
| `dominant_element` | atom-id | which atom your eye lands on first (squint-test answer) |

### Atoms

Each atom in `atoms[]` has `id` (e.g., `s03-a02`), `type` (from v3 taxonomy), and type-specific fields.

**Type-specific atom field schemas:**

`title`
```json
{
  "text": "string",
  "action": true|false,
  "hedge_words": ["could", "may", ...],
  "contains_course_artifact": false,
  "ends_with_period": true,
  "uses_em_dash": false
}
```

`kicker`
```json
{
  "text": "string",
  "position": "above-title" | "fused-with-title" | "side-badge",
  "all_caps": true|false
}
```

`stat-block`
```json
{
  "big_number": "$12B" | "47%" | "+$1.0B",
  "unit": "string | null",
  "label": "string",
  "has_source_reference": true|false
}
```

`bar-chart` (also applies to `line-chart`, `waterfall`, `scatter-bubble`, `map` with analogous fields)
```json
{
  "variant": "vertical-bars" | "horizontal-bars" | "grouped" | "stacked" | "100pct-stacked" | "marimekko",
  "chart_caption": "string | null",
  "x_axis": { "label": "string | null", "unit": "string | null", "categories": [...] },
  "y_axis": { "label": "string | null", "unit": "string | null", "range": [min, max] },
  "series": [
    { "name": "string", "color": "hex", "values": [...] }
  ],
  "legend_present": true|false,
  "data_labels_present": true|false,
  "highlighted_elements": [
    { "element": "string description", "reason_visible": "string" }
  ],
  "takeaway_annotation_present": true|false
}
```

`sidebar`
```json
{
  "header": "string | null",
  "bullets": ["string", ...],
  "emphasized_bullet_indices": [1, 2],
  "placement": "right-column" | "bottom-banner" | "left-panel" | "boxed"
}
```

`n-card-grid`
```json
{
  "card_count": 3,
  "orientation": "horizontal" | "vertical" | "2d-grid",
  "cards": [
    {
      "heading": "string",
      "body": "string",
      "icon_description": "string | null",
      "sub_label": "string | null",
      "accent_color": "hex | null",
      "stat": "string | null"
    }
  ],
  "sub_labels_identical_across_cards": true|false,
  "card_body_length_variance": "low" | "moderate" | "high"
}
```

`data-table`
```json
{
  "rows": int,
  "cols": int,
  "header_row_present": true|false,
  "color_coded_cells": true|false,
  "cells": [[...]]
}
```

`annotation-callout`
```json
{
  "text": "string",
  "variant": "multiplier" | "floating-stat" | "rounded-rect-banner" | "brace-label" | "methodology-box" | "horizontal-takeaway-banner" | "starburst" | "circled-value" | "speech-bubble" | "operator-glyph",
  "points_at": "atom-id | null",
  "placement": "top" | "bottom" | "on-chart" | "between-elements"
}
```

`pull-quote`
```json
{
  "text": "string",
  "attribution": "string",
  "attribution_is_named_role": true|false,
  "attribution_is_named_org": true|false
}
```

`source-line`
```json
{
  "text": "string",
  "citations": [
    { "ref_id": "1", "source_text": "string", "is_named_org": true, "is_dated": true, "is_specific": true }
  ],
  "specificity": "specific-named-and-dated" | "named-undated" | "generic" | "missing"
}
```

`image`
```json
{
  "variant": "hero-photo" | "product-shot" | "scene-photo" | "decorative-motif" | "section-divider-bg" | "photo-backed-card" | "logo" | "news-thumbnail",
  "description": "string",
  "appears_decorative": true|false
}
```

Other atoms (`paragraph`, `bulleted-list`, `brand-mark`, `metadata-block`, `title-divider`, `page-number`, `footnote`, `chart-caption`, `axis-labels`, `legend`, `tab-filter-bar`, `icon`, `harvey-balls`, `process-flow`, `comparison-panel`) use sensible text/structural fields.

### Per-slide observations

| Field | Type | Notes |
|---|---|---|
| `word_count` | int | all visible text on slide |
| `palette` | `[{hex, name, role, usage_count}]` | colors and what each one means on this slide |
| `title_body_alignment` | enum | `supports` / `mismatch` / `partial` / `n-a` |
| `title_body_mismatch_detail` | string \| null | specifics if mismatch |
| `chart_has_takeaway` | bool \| null | null if no chart |
| `llm_smell_tells` | string[] | observed AI-writing patterns on this slide (see vocabulary below) |
| `antithesis_constructions` | string[] | parallel "X, not Y" / "not X, but Y" / "X — but Y" patterns |
| `hedging_language` | string[] | observed overhedging phrases |
| `three_item_list_detected` | bool | any list of exactly three items |
| `identical_sub_labels_on_cards` | bool \| null | null if no card grid |
| `chart_craft_issues` | string[] | observed chart problems (missing units, unlabeled series, unclear legend, reversed axis, color-without-meaning) |
| `mechanics_issues` | `[{type, quote, correction}]` | per-slide grammar/spelling/punctuation/spacing/word-choice/inconsistency errors with verbatim quote + suggested fix |
| `pyramid_compliance` | `{lead_line_is_takeaway, drill_down_supports_lead_line, detail}` | does the title (lead line) state the slide's takeaway, and does the body drill down into it |
| `free_form` | string | escape hatch for anything else observed |

### Per-slide argument observations

The observations above cover mechanics and AI smells. This block captures whether the slide's thinking is any good — the questions that separate rubric level 5 from level 7.

```json
"argument": {
  "core_claim": "one-sentence restatement of what this slide asserts",
  "claim_is_specific": true|false,
  "claim_is_supported_on_slide": true|false,
  "evidence_quality": "strong" | "adequate" | "weak" | "missing",
  "evidence_quality_detail": "string",
  "hidden_assumptions": ["...", "..."],
  "logical_gaps": ["jumps in reasoning where the reader has to fill in"],
  "so_what_stated": true|false,
  "so_what_detail": "string | null",
  "generic_applicability": "specific" | "partially-generic" | "fully-generic",
  "generic_applicability_detail": "could this slide work unchanged for a different company/industry?",
  "advances_argument": true|false,
  "advances_detail": "what does this slide add that previous slides didn't",
  "numeric_claims": [
    {
      "claim": "verbatim quote",
      "derivation_shown": true|false,
      "plausible": true|false,
      "plausibility_note": "string | null"
    }
  ]
}
```

Field notes:

- `claim_is_specific` — the "swap test" at slide level. "Apple should win AI" = not specific. "Apple can capture ~$12B by shortening upgrade cycles from 3-4 years to ~2 years on Apple-Silicon-locked features" = specific.
- `claim_is_supported_on_slide` — the body/chart actually shows what the title claims. Distinct from `title_body_alignment` which is about whether they *contradict*; this is about whether the body *proves* the title.
- `hidden_assumptions` — what the claim rests on but doesn't state. "10% of users adopt" is an assumption that should be surfaced.
- `so_what_stated` — does the slide push past observation ("sales fell 10%") to implication ("sales fell because of pricing, not demand, so the fix is marketing not discounting")?
- `generic_applicability` — swap the company name. Does the claim still work? If yes, the slide is scaffolding.
- `advances_argument` — does this slide add to the deck's thesis, or is it restating? Devil's-advocate test: if removed, would the deck be weaker?
- `numeric_claims` — every claim with a number gets one entry. `derivation_shown` = is the math visible on-slide or in footnote? `plausible` = does the magnitude make sense given what you know?

**`llm_smell_tells` vocabulary** (what the prompt should look for):
- "This matters because...", "The implication is...", "What this tells us is..."
- Stacked participial phrases
- Consistent Oxford commas across every bullet
- Identical sentence rhythms across slides
- "WHY IT WORKS / WHAT IT DELIVERS / RISK" style card sub-labels
- Kicker labels on every analytical slide
- Bullets of exactly three on every slide
- Title-subtitle restatement (subtitle rephrases title)
- Generic applicability (card labels would work unchanged on any company)
- Colored emphasis text that doesn't pay off (green/red words without consistent role)

---

## Data dictionary — deck-level (second pass, text-only over slide records)

### `deck.features` (derived scalars; deterministic)

| Field | Type | How computed |
|---|---|---|
| `avg_words_per_slide` | float | mean of word_count across core slides |
| `max_words_per_slide` | int | max of word_count |
| `core_slide_count` | int | total minus title, exec summary, dividers, appendix |
| `action_title_ratio` | float | % of body-slide titles with `action:true` |
| `kicker_recurrence` | `{kicker_text: count}` | frequency map |
| `chart_types_used` | string[] | unique chart types + variants |
| `slides_with_sources` | int | count where source-line atom present |
| `slides_with_charts` | int | |
| `slides_missing_sources_with_quant_claims` | int[] | slide indices that have stat-blocks but no source |
| `identical_sub_label_card_slides` | int[] | slide indices where `identical_sub_labels_on_cards:true` |
| `exactly_three_item_list_recurrence` | int | count of slides with `three_item_list_detected:true` |
| `total_mechanics_errors` | int | sum of `mechanics_issues[]` across slides (David's rubric: ≥5 = not CEO-ready) |
| `mechanics_errors_by_type` | `{spelling: int, grammar: int, punctuation: int, spacing: int, word-choice: int, inconsistency: int}` | breakdown |

### `deck.observations` (cross-slide observations from deck-level prompt)

```json
{
  "title_flow": {
    "titles": ["...", "..."],
    "coherent": true|false,
    "arc": "one-sentence summary of the structure (situation → complication → resolution)",
    "weak_links": [{"slide": 3, "reason": "..."}]
  },
  "color_consistency": {
    "consistent": true|false,
    "issues": [
      {"color": "#E5542E red", "slides": [3, 4, 7], "detail": "red=risk on 3,4 but highlight-with-no-risk-meaning on 7"}
    ]
  },
  "typography_consistency": {
    "consistent": true|false,
    "drift_slides": [...]
  },
  "template_saturation_level": "none" | "mild" | "moderate" | "saturated",
  "template_saturation_tells": ["...", "..."],
  "student_ownership_gestalt": "student-authored" | "mixed" | "llm-scaffolded",
  "gestalt_detail": "1-2 sentence assessment",
  "free_form": "string"
}
```

### `deck.observations.coherence` (argument quality at deck level)

This block captures whether the deck's *thinking* holds together across slides. It's the text-grounded deck-level complement to per-slide `argument` observations.

```json
"coherence": {
  "core_thesis": "one-sentence of the deck's central argument as stated",
  "thesis_is_specific": true|false,

  "recommendation": {
    "stated": true|false,
    "text": "string | null",
    "specificity": "specific-action" | "directional" | "do-more-analysis" | "missing",
    "is_execution_or_substitute": "execution" | "substitute" | "mixed",
    "addresses_problem": true|false
  },

  "exec_summary_matches_body": true|false,
  "exec_summary_mismatch_detail": "string | null",

  "internal_contradictions": [
    {
      "claim_a": "slide N: ...",
      "claim_b": "slide M: ...",
      "nature": "string"
    }
  ],

  "numbers_tie_across_slides": true|false,
  "number_reconciliation_issues": [
    {"slides": [N, M], "issue": "slide 2 says 5M drivers, slide 10 says 6.7M"}
  ],

  "argument_arc": {
    "situation_established": true|false,
    "complication_named": true|false,
    "resolution_proposed": true|false,
    "recommendation_specific": true|false,
    "implementation_addressed": true|false,
    "arc_is_complete": true|false,
    "weak_transitions": [{"from_slide": N, "to_slide": M, "reason": "string"}]
  },

  "pressure_test": {
    "strongest_counterargument_a_skeptic_would_raise": "string",
    "deck_anticipates_it": "holds-up" | "partial" | "unaddressed" | "weak",
    "assumptions_made_explicit_in_deck": true|false,
    "detail": "string"
  },

  "non_obviousness": {
    "is_insight_in_company_filings_already": true|false,
    "is_insight_in_standard_analyst_coverage": true|false,
    "pushes_past_observation_to_interpretation": true|false,
    "detail": "string"
  },

  "cuttable_slides": [
    {"slide": N, "reason": "restates slide X / adds no evidence / decoration only"}
  ],

  "word_salad_flags": [
    {"slide": N, "quote": "verbatim", "why": "could mean anything; no concrete referent"}
  ],

  "strategic_framework": {
    "market_identified": true|false,
    "market_detail": "what market the solution targets, with size/scope named",
    "unique_users_identified": true|false,
    "unique_users_detail": "who specifically the solution serves and why them",
    "resources_and_capabilities_named": true|false,
    "resources_and_capabilities_detail": "what the company brings that others can't match",
    "sustainability_addressed": true|false,
    "sustainability_detail": "why the advantage is durable over time",
    "feasibility_addressed": true|false,
    "feasibility_detail": "why the company can execute this given constraints"
  },

  "complication_implies_key_question": true|false,
  "key_question": "string | null",

  "conclusion_quality": {
    "has_closing_slide": true|false,
    "restates_thesis": true|false,
    "summarizes_evidence": true|false,
    "commits_to_recommendation": true|false,
    "detail": "string"
  }
}
```

Field notes:

- `recommendation.specificity` — "specific-action" means the company could do it Monday (acquire X, exit Y, launch Z, reprice, reorg). "directional" means "invest more in AI". "do-more-analysis" means "conduct a diagnostic" — proposing to study the problem the deck was supposed to solve.
- `recommendation.is_execution_or_substitute` — if the recommendation is "three 4-10 week diagnostic workstreams," that's a substitute for the recommendation, not the recommendation itself. The rubric's Storyline-7 hurdle cares about this distinction.
- `pressure_test` — the grader currently runs this manually. Capturing it at parse time means a consistent counterargument per deck rather than grader-dependent reasoning.
- `non_obviousness` — is the insight something the company's own investor deck would say, or does it push past? This is the Insight-7 hurdle.
- `word_salad_flags` — per-slide entries where language is consultant buzzword without concrete meaning ("synergistic moat", "ecosystem flywheel with no named metric"). Quote verbatim.

**Word-salad test:** can you swap the nouns (company, industry, specific metrics) and have the claim still read as plausible? If yes, flag it.

---

## Prompts

### Per-slide parse prompt (v1)

```
You are parsing a single slide from a consulting slide deck. Your job is to
produce a structured JSON record of what is on the slide, using a fixed
taxonomy of 29 slide elements (atoms).

Be factual and specific. Do NOT judge the slide's quality against any rubric.
Observations only.

## The 29 atoms

FRAME: title, kicker, title-divider, source-line, footnote, page-number,
brand-mark, metadata-block

TEXT: paragraph, bulleted-list, sidebar, stat-block, pull-quote

CHARTS: bar-chart, line-chart, waterfall, scatter-bubble, map

NON-CHART VISUALS: harvey-balls, process-flow, comparison-panel, n-card-grid,
data-table

CHART DECOR: chart-caption, axis-labels, legend, annotation-callout,
tab-filter-bar

DECORATION: icon, image

(See scripts/slide-atoms-v3.md for full atom definitions.)

## Input

- slide_index: 1-based position in deck
- deck_id: identifier string
- Image of the slide

## Output

Return a single JSON object matching the slide schema. See the data
dictionary in scripts/parse-and-score-plan.md for full field definitions.

Top-level fields:
- index, image_path, page_number_shown
- role_guess, density, dominant_element
- atoms[] (each with id, type, and type-specific fields)
- observations (word_count, palette, title_body_alignment,
  chart_has_takeaway, llm_smell_tells, antithesis_constructions,
  hedging_language, three_item_list_detected,
  identical_sub_labels_on_cards, chart_craft_issues,
  mechanics_issues, pyramid_compliance, free_form)
- argument (core_claim, claim_is_specific, claim_is_supported_on_slide,
  evidence_quality, hidden_assumptions, logical_gaps, so_what_stated,
  generic_applicability, advances_argument, numeric_claims)

## Rules

1. Every text block, chart, image, or structural element on the slide must
   be represented as exactly one atom.
2. Nested atoms are allowed: a sidebar can contain a stat-block; an
   n-card-grid contains cards; a data-table contains cells.
3. If uncertain between two atom types, pick the better-fit one and note the
   ambiguity in free_form.
4. Title `action` field: true only if the title commits to a specific claim.
   "Growth is slowing in the Americas" = action. "Revenue Overview" = not
   action.
5. For palette, identify 3-6 meaningful colors (ignore near-white backgrounds
   and near-black body text unless used as an accent). For each color, name
   its role on this slide: "risk" / "positive" / "accent-brand" /
   "decorative" / "highlight" / "text-primary".
6. llm_smell_tells: flag specific phrases and patterns you observe.
   Quote verbatim when the tell is a phrase. Examples of what to look for:
   - "This matters because...", "The implication is...", "What this tells us is..."
   - Identical sub-labels across cards (Why / What / Risk style)
   - Bullets of exactly three on every slide
   - Stacked participial phrases
   - Over-hedging ("could potentially", "may represent a significant opportunity")
   - Generic card labels that would work unchanged on any company
   - Colored emphasis text without consistent role
7. antithesis_constructions: note verbatim any "X, not Y" / "not X, but Y" /
   "X — but Y" parallel constructions. These are LLM-rhetorical tells when
   they recur across the deck.
8. title_body_alignment: look at the title's claim and the body's main
   visual/content. "mismatch" if the title asserts something the body
   doesn't show. Put specifics in title_body_mismatch_detail.
9. chart_craft_issues: list observed problems on any chart (missing y-axis
   unit, legend not distinguishable, data labels absent where needed,
   reversed axis convention, color with no clear meaning).
10. Report facts. Do not say "this is bad" or "this violates rubric X."
11. For atoms you can't classify cleanly, use the taxonomy's closest match
    and note the uncertainty in free_form.

## Argument observations (harder, but critical)

The `argument` block asks whether the slide's thinking is any good. These
observations require judgment, not just description. You are allowed to judge
argument quality here. Do NOT judge it against a rubric.

12. core_claim: restate what the slide asserts in one sentence. Use the
    title's claim if it's committal; otherwise synthesize from the body.
13. claim_is_specific: the swap test. Could you replace the company/industry/
    metric names with generic ones and have the claim still read plausibly?
    If yes, not specific. "Apple should win AI" = not specific. "Apple can
    capture $12B by shortening upgrade cycles from 3-4 to ~2 years on
    Silicon-locked features, with 30% adoption by year 5" = specific.
14. claim_is_supported_on_slide: the body/chart actually proves the title's
    claim. Distinct from title_body_alignment (about contradictions); this
    asks whether the evidence discharges the claim.
15. evidence_quality: "strong" if multiple independent sources or a clear
    derivation; "adequate" if one named source supports the main claim;
    "weak" if sources are generic ("industry reports", "Web research") or
    extrapolated without shown method; "missing" if none.
16. hidden_assumptions: list the 1-3 assumptions the claim rests on but does
    not state. "Users will pay a premium" / "Regulation won't change" /
    "Competitors won't respond." Be specific.
17. logical_gaps: jumps in reasoning where the reader has to fill in. "The
    chart shows X; the claim is Y; the link between them is not shown."
18. so_what_stated: does the slide push past observation (what is happening)
    to implication (what it means for the decision)? "Sales fell 10%" alone
    is not a so-what. "Sales fell 10%, and because it's conversion not
    traffic, the fix is product-value not marketing" is a so-what.
19. generic_applicability: the swap test applied to the whole slide.
    "specific" = company-specific claims with named metrics.
    "partially-generic" = some specific, some generic scaffolding.
    "fully-generic" = the slide would work unchanged for any company.
20. advances_argument: does this slide add to the thesis, or is it restating
    an earlier point, or is it decoration? If the slide were removed, would
    the deck be weaker?
21. numeric_claims: for every claim with a number on the slide, record:
    the verbatim claim, whether the derivation is shown (on-slide or in a
    named footnote), whether the magnitude seems plausible, and a short
    plausibility note if anything is surprising.

## Mechanics and pyramid compliance

22. mechanics_issues: list every spelling, grammar, punctuation, spacing,
    word-choice, or consistency error you see on the slide. For each:
    - type: one of spelling | grammar | punctuation | spacing | word-choice | inconsistency
    - quote: the verbatim offending text
    - correction: the suggested fix
    Be thorough but not pedantic. Focus on errors a CEO-level reader would
    notice: misspellings, subject-verb disagreement, typos in numbers,
    inconsistent capitalization/punctuation, missing periods, awkward
    phrasing that breaks professional tone.
23. pyramid_compliance: does the slide follow the pyramid principle?
    - lead_line_is_takeaway: the title (the lead line) states the slide's
      key takeaway, not just the topic. This is the same question as
      title.action but phrased per the pyramid principle explicitly.
    - drill_down_supports_lead_line: the body drills down into the takeaway
      with supporting evidence, not unrelated content.
    - detail: string. Note where the structure breaks if it breaks.

Output valid JSON only. No preamble, no explanation.
```

### Deck-level observation prompt (v1)

```
You are analyzing a full consulting deck. You will receive an array of
per-slide parse records (already produced by the slide parser) and the
original slide images (optional reference). Your job is to produce
deck-level observations that cannot be seen from a single slide.

## Input

- slides[]: array of per-slide records
- image_paths[]: (optional, can be reviewed if text is insufficient)

## Output

Return a single JSON object with two top-level keys: `features` and
`observations`. See data dictionary in scripts/parse-and-score-plan.md.

## Rules

1. Compute features deterministically from the slide data. Don't estimate.
2. For title_flow.titles, list every title in order. "coherent" = reading
   titles alone tells a story with situation, complication, and
   committed-to-recommendation. "arc" = one-sentence summary of the
   structure (e.g., "situation → complication → recommendation → timing →
   execution → ask"). "weak_links" = titles that break the flow.
3. color_consistency: look across slides at each color's role. Flag cases
   where the same color carries different meanings (e.g., red = risk on
   most slides, red = highlighted-bar on one). List the slides.
4. typography_consistency: look for drift in fonts, weights, sizes across
   body slides.
5. template_saturation_level thresholds:
   - none: <2 signals
   - mild: 2-3 signals, each on few slides
   - moderate: 3-5 signals
   - saturated: 5+ signals appearing on most core slides
   Signals include: kicker-on-every-slide, cards-of-exactly-three recurrence,
   identical sub-labels across card sets, rigid three-part body structure,
   LLM phrases recurring.
6. student_ownership_gestalt: trust your overall read. Does this feel like
   a student wrote, re-read, and edited it, or like an LLM first-draft with
   cosmetic polish? Be specific in gestalt_detail.
7. Be specific in "detail" and "reason" fields. Not "weak flow" but
   "Slide 3's topic-label title breaks the sequence between slides 2 and 4."

## Coherence observations (hardest block)

The `coherence` block asks whether the deck's thinking holds together across
slides. This is judgment over the whole deck. You're allowed to judge
argument quality. Do NOT judge against a rubric.

8. core_thesis: one sentence restating the deck's central argument. Pull it
   from exec summary if specific; otherwise synthesize from the titles.
9. thesis_is_specific: swap test at deck level. Could this thesis work
   unchanged for a different company?
10. recommendation:
    - stated: is there an explicit recommendation, or just a diagnostic?
    - specificity: "specific-action" (company could execute Monday: acquire,
      exit, launch, reprice, reorg, restructure); "directional" (general
      direction without a specific action); "do-more-analysis" (proposing
      to study what the deck was supposed to solve); "missing".
    - is_execution_or_substitute: if the deck's "recommendation" is "run
      three diagnostic workstreams," that's a substitute for the
      recommendation, not the recommendation. Flag it.
    - addresses_problem: does the recommendation actually solve the problem
      identified earlier in the deck?
11. exec_summary_matches_body: does the exec summary's claims match what
    the body actually argues? Flag mismatches.
12. internal_contradictions: scan for claims on one slide that contradict
    claims on another. Number mismatches, framing reversals, scope drifts.
13. numbers_tie_across_slides: do numbers referenced on multiple slides
    reconcile? List any discrepancies.
14. argument_arc: assess whether each component of a complete argument is
    present. The rubric cares about situation → complication → resolution
    with specific recommendation and implementation.
15. pressure_test: as an analyst from the target company, what's the
    strongest counterargument to the deck's thesis? (Name a specific
    competitor dynamic, customer behavior, macro risk, or internal
    constraint.) Then assess whether the deck addresses it:
    - "holds-up": deck acknowledges and refutes/navigates it
    - "partial": some assumptions acknowledged, strongest objection not
    - "unaddressed": no pressure testing anywhere
    - "weak": obvious counterargument ignored that would change the rec
16. non_obviousness: is the core insight something the company's own
    investor deck would already say? Is it in standard analyst coverage?
    Does it push past observation to interpretation?
17. cuttable_slides: list slides that could be removed without weakening
    the argument. If a slide restates an earlier point or is pure
    decoration, flag it.
18. word_salad_flags: consultant buzzword language that sounds like a
    claim but isn't. Quote verbatim. Examples: "ecosystem flywheel",
    "synergistic moat", "durable agentic AI triad" without a concrete
    referent or a named metric.

## Strategic framework, key question, conclusion

19. strategic_framework: evaluate whether the deck's proposed strategy
    (its recommendation) addresses five components. For each:
    - market_identified: does the deck name the market the solution targets,
      with scope/size? Not "AI" — "US iPhone installed base (142M users)".
    - unique_users_identified: does the deck specify who is served and why
      them? Not "customers" — "drivers who change employers every 3.9 years."
    - resources_and_capabilities_named: does the deck name what the company
      brings that competitors can't match? Not "we're good at tech" —
      "Apple's vertical integration across silicon, OS, and distribution
      with 2.5B device install base."
    - sustainability_addressed: does the deck explain why the advantage is
      durable over time? Not "we'll keep investing" — "switching costs
      compound via IRA Match, deposit relationships, and 89% retention."
    - feasibility_addressed: does the deck explain why the company can
      execute given constraints? Not "we'll do it" — "no net new marketing
      spend; $1B reallocation from lifestyle demand-creation budget."
    For each, record true/false and a brief detail citing evidence from
    specific slides.

20. complication_implies_key_question: does the deck's complication set up
    an analytical question that the rest of the deck answers? Good example:
    "If current trajectory holds, Nike loses $13B by 2028 — what would it
    take to reverse course?" → explicit key question. Bad: complication
    is stated but no question drives the analysis.
    Record the key question in key_question if one is clearly implied.

21. conclusion_quality:
    - has_closing_slide: is there a dedicated closing/summary slide
      (role_guess == "closing")?
    - restates_thesis: does the conclusion restate the deck's core thesis?
    - summarizes_evidence: does the conclusion tie back to key evidence
      from body slides?
    - commits_to_recommendation: does the conclusion reassert the
      specific recommendation (not a topic label, not "do more analysis")?
    - detail: string describing the conclusion's shape.

Output valid JSON only.
```

---

## Scoring architecture (build after calibration validates the data)

### Three components

**1. Pattern library.** Each pattern is a pure function over `deck.json` returning `{fires, tier, dimension, slides, evidence}`. Example:

```python
def client_readiness_gate(deck):
    hits = []
    for s in deck.slides:
        for a in s.atoms:
            if a.type == "title" and a.get("contains_course_artifact"):
                hits.append({"slide": s.index, "text": a.text})
    if hits:
        return Finding(fires=True, tier="CAP=4", dimension="storyline",
                       evidence=f"Course artifacts in titles: {hits}",
                       slides=[h['slide'] for h in hits])
```

Most patterns from `.claude/skills/grade-deck/patterns.md` port directly. Mapping:

| Current pattern | Operates on |
|---|---|
| S-C01 through S-C07 (AI-residue tells) | `slides[].observations.llm_smell_tells` |
| D-C05a density | `deck.features.avg_words_per_slide`, `max_words_per_slide` |
| I-C01 "so what" | `slides[].argument.so_what_stated` |
| Source Quality Gate | `deck.features.slides_missing_sources_with_quant_claims` |
| Client-Readiness Gate | `title.contains_course_artifact` |
| G05 AI-Scaffolding Saturation | `deck.observations.template_saturation_level`, multiple counts |
| Golden Rule | `slides[].observations.title_body_alignment == "mismatch"` |
| Color-without-meaning | `deck.observations.color_consistency.issues` |
| Recommendation specificity (Storyline-7) | `deck.coherence.recommendation.specificity` |
| Recommendation is execution not substitute (Storyline-7) | `deck.coherence.recommendation.is_execution_or_substitute` |
| Pressure test (Insight-7) | `deck.coherence.pressure_test.deck_anticipates_it` |
| Non-obviousness (Insight-7) | `deck.coherence.non_obviousness.*` |
| Generic applicability (swap test) | `slides[].argument.generic_applicability`, aggregated |
| Devil's advocate (cuttable slides) | `deck.coherence.cuttable_slides` |
| Internal contradictions | `deck.coherence.internal_contradictions` |
| Numbers tie | `deck.coherence.numbers_tie_across_slides` |

**Bryce rubric (STRAT 411 Case Write-up) pattern mapping:**

| Bryce criterion | Operates on |
|---|---|
| Situation clarity | `deck.coherence.argument_arc.situation_established`, role_guess |
| Complication → key question | `deck.coherence.complication_implies_key_question`, `key_question` |
| Solution clarity & exec summary | `deck.coherence.recommendation.stated`, `exec_summary_matches_body` |
| Overall Strategy (5 components) | `deck.coherence.strategic_framework.*` |
| Supporting Logic, Data | `slides[].argument.evidence_quality`, `numeric_claims`, `hidden_assumptions`, `logical_gaps` |
| Sequence and Timing | `deck.coherence.argument_arc.implementation_addressed`, process-flow atoms |
| Expected Impact | `slides[].argument.numeric_claims`, impact-stat slides |
| Grammar/Mechanics | `deck.features.total_mechanics_errors`, `mechanics_errors_by_type` |
| Professional Slide Design | `deck.observations.typography_consistency`, `color_consistency` |
| Flow (pyramid principle) | `slides[].observations.pyramid_compliance`, `deck.observations.title_flow` |
| Use of Graphics | `slides[].observations.chart_craft_issues`, `chart_has_takeaway` |
| Summary & Key Takeaways | `deck.coherence.conclusion_quality.*` |

Same `deck.json` can be scored by either rubric. Multiple rubrics map onto one parse artifact.

**2. Rubric as YAML.** Port from `00-assessments.qmd` prose. Structure:

```yaml
dimensions:
  storyline:
    weight: 0.30
    descriptors: {1: "...", 2: "...", ..., 7: "..."}
    gates: [client-readiness-gate, g05-ai-scaffolding-saturation]
    level_7_hurdles: [...]
    level_6_hurdles: [...]
  insight:
    weight: 0.30
    ...
  evidence:
    weight: 0.25
    ...
  design:
    weight: 0.15
    ...

patterns:
  s-c01:
    dimension: storyline
    tier: 3
    description: "Over-hedged title language"

gates:
  source-quality:
    triggered_by: "any quantitative claim cites an untraceable source"
    caps: {evidence: 4}
```

**3. Derivation logic.**
- Fire all patterns and gates on the JSON
- For each dimension, match to descriptor via tier anchors:
  - 0 T3 + 0-1 T2 → probably 6 or 7 (check hurdles)
  - 0 T3 + 2-3 T2 → 5
  - 0 T3 + 4-5 T2 → 4
  - 0 T3 + 6+ T2 OR 2+ T3 → 3
  - Pervasive T3 → ≤2
- Enforce hurdles: if descriptor match is 7 but level-7 hurdles aren't all met, cap at 6. If 6 but hurdles fail, drop to 5.
- Apply gate caps
- Weighted total: `sum(score[d] * weight[d] for d in dims) * 100 / 7`

**Descriptor matching strategy:** Start with tier-count anchors (deterministic, defensible). Add empirical calibration later once you have 20-30 graded decks. Avoid "Claude decides the level" for reproducibility.

---

## Execution sequence

### Phase 1 — Calibration (do this before writing any code)

Goal: validate the data dictionary captures what's needed.

1. Pick one deck you've already graded (with known rubric scores). Recommend `grades/pdfs/collin-powell.pdf` — we already have an ADE parse at `scripts/collin-powell.parse.md` for reference.
2. Manually produce a `deck.json` for that deck by walking the parse prompt yourself against each slide image. You can use the `Read` tool with pages parameter.
3. Save to `grading-artifacts/collin-powell/deck.json`.
4. Walk the rubric dimensions. For each dimension, ask: given this JSON, which findings would fire? Do the tier-anchors produce the known grade?
5. Identify gaps: observations you'd need but aren't captured → revise the data dictionary. Ambiguities that need more prompt guidance → revise the prompt.

Time: 1-2 hours. Output: validated data dictionary + revised prompts + notes on what breaks.

### Phase 2 — Automated parser

Goal: produce `deck.json` for any deck via a single script.

1. Write `scripts/parse_deck.py` (or similar). Responsibilities:
   - Render each PDF page to `slides/sNN.png` using `pymupdf` at 150 DPI
   - For each slide image, call Claude with the per-slide parse prompt
   - After all slides parsed, run the deck-level prompt over the slide records
   - Save to `grading-artifacts/<deck-id>/deck.json`
2. Test on 3-5 decks from `grades/pdfs/`. Check parse quality by spot-checking atoms.
3. Handle edge cases: rasterized PPTs (no text layer), very large decks, unusual aspect ratios.

Time: 4-8 hours. Cost: ~$0.50-0.80 per deck in VLM calls.

### Phase 3 — Rubric YAML

Goal: port `.claude/skills/grade-deck/SKILL.md` + `patterns.md` + `00-assessments.qmd` rubric into a single `rubric.yaml`.

1. Start with the four dimensions, weights, and descriptors.
2. Enumerate every pattern from `patterns.md` with dimension + tier.
3. Enumerate gates (Source Quality, Client-Readiness, G05).
4. Enumerate hurdles from level-6 and level-7 in SKILL.md.

Time: 2-3 hours. Output: a single YAML file that is the executable spec.

### Phase 4 — Scoring harness

Goal: `score_deck(deck.json, rubric.yaml) → scoring.json`.

1. Implement the pattern library (one function per pattern).
2. Implement gate evaluation.
3. Implement descriptor matching via tier anchors.
4. Implement hurdle enforcement.
5. Output `scoring.json` with findings, per-dimension scores, reasoning, and final weighted score.

Time: 8-12 hours. Test against the calibration deck from Phase 1.

### Phase 5 — Student-facing output

Goal: generate the markdown grade file (current `grade-deck` output format) from `scoring.json`.

This is pure transformation: findings → grouped by dimension → formatted per the existing template in SKILL.md. No new logic.

Time: 2-3 hours.

---

## Open decisions (flagged during design)

1. **Atom IDs**: chose `s03-a02` (slide-N, atom-M) for readability. Could use UUIDs if global uniqueness matters across decks. Decision: stick with slide-local.

2. **Bounding boxes**: include in atoms. VLM estimates are approximate; mark as such. Useful if we ever want to render annotations back onto images for student feedback.

3. **Palette cap**: target 3-6 colors per slide. Not a hard cap. If a slide genuinely has 8 meaningful colors, report all 8.

4. **Free-form observations field**: keep. It's the escape hatch when the prompt misses something the model noticed.

5. **Single-pass vs multi-pass per slide**: start single-pass. If parse quality is insufficient on any atom category (e.g., chart data extraction), add a targeted second pass just for that.

6. **Vision at score time**: 2-3 questions inherently require it:
   - Level-7 insight hurdle ("core insight not already in company filings") → external knowledge query
   - Pressure test counterargument → domain reasoning query
   - Squint test per slide → may be covered by parse `dominant_element`, but cross-check

   Keep these as explicit score-time Claude calls. Everything else is deterministic JSON processing.

7. **Versioning**: stamp every `deck.json` with `schema_version`, `atoms_version`, and `prompt_hash`. Re-parse only when vocabulary changes meaningfully.

---

## What success looks like

After Phase 1 (calibration):
- One deck parsed manually; manual walk of rubric produces a score close to the known human grade. If off by more than 10 points, data dictionary has gaps.

After Phase 2 (parser):
- Any deck in `grades/pdfs/` can be parsed in under 2 minutes for under $1.
- Spot-checked parse JSON is factually accurate (>90% atom classification correct; text extraction verbatim; palette and roles reasonable).

After Phase 4 (scoring):
- Parse one deck → automated score within 5 points of human grade on all four dimensions.
- 10-deck batch run produces consistent, defensible scores with full audit trails.

After Phase 5:
- `grade-deck` skill can be rewritten to: `parse_deck.py deck.pdf → score_deck deck.json → format_output scoring.json`. Three deterministic steps replacing the current vision-heavy flow.

---

## First command to run when fresh context opens

```
Read scripts/parse-and-score-plan.md and scripts/slide-atoms-v3.md.
Then begin Phase 1 calibration using grades/pdfs/collin-powell.pdf as the
test deck. Walk each slide with the Read tool, produce deck.json by hand
following the data dictionary, save to grading-artifacts/collin-powell/deck.json,
and report any gaps in the dictionary as you hit them.
```

---

# Schema v1.1 — additions after Phase 1 calibration

Phase 1 walked the Collin Powell deck by hand and surfaced ~20 gaps where the scorer could not fire a pattern deterministically from the JSON. This section locks v1.1. Every field below is either new or revised from v1.0.

Set `schema_version: "1.1"` on new parses.

## Provenance codes

Every field has a single source. Codes used below:

| Code | Mechanism | Determinism |
|---|---|---|
| **PDF** | pymupdf reads (page size, count, renders) | deterministic |
| **V1-obs** | per-slide VLM pass, descriptive | parse-time judgment (not deterministic) |
| **V1-judg** | per-slide VLM pass, judgmental | parse-time judgment |
| **TXT** | deterministic text-processing over V1-emitted text | deterministic |
| **AGG** | deterministic aggregation across slide records | deterministic |
| **DECK** | deck-level VLM pass over slide records ± images | parse-time judgment |

EXT (external-knowledge call) is **dropped** in v1.1. See "Insight-7 redefinition" below.

## Per-slide additions and revisions

### Title atom (revised)

```json
{
  "text": "string",
  "action": true,
  "hedge_words": ["could", "may"],
  "contains_course_artifact": false,
  "ends_with_period": true,
  "uses_em_dash": false,

  "casing": "Title|Sentence|UPPER|lower|mixed",              // NEW — TXT
  "verb_strength": "causal|associative|observational|none",   // NEW — V1-judg
  "uses_move_as_noun": false,                                 // NEW — TXT
  "has_ai_explainer_parenthetical": false,                    // NEW — TXT
  "has_internal_contradiction": false                         // NEW — V1-judg
}
```

### Kicker atom (revised)

```json
{
  "text": "string",
  "position": "above-title|fused-with-title|side-badge",
  "all_caps": true,
  "is_empty_container_label": true      // NEW — TXT
}
```

### Chart atoms (bar-chart, line-chart, waterfall, scatter-bubble, map)

Add two sub-blocks on every chart atom:

```json
"readability": {                                   // NEW — V1-obs
  "has_data_labels": false,
  "has_axis_units": true,
  "has_legend_if_multiseries": true,
  "has_takeaway_annotation": false
},
"chart_math": {                                    // NEW — V1-judg
  "stated_whole": 750,
  "stated_whole_unit": "$M",
  "parts_sum": 3450,
  "ties": false,
  "notes": "Per-agency bars exceed the stated $750M pool"
}
```

`chart_math` applies only when the chart has a stated whole (e.g., total-waste bar, 100% stack, pie, or a "$X total" anchor). For charts without a stated whole, use `{"stated_whole": null, "parts_sum": null, "ties": null, "notes": null}`.

### Process-flow atom (Gantt/timeline variant)

```json
"timeline_math": {                                 // NEW — V1-judg
  "stated_duration_days": 14,
  "sum_of_bar_days": 19,
  "reconciles": false,
  "overlap_implied": true
}
```

### Source-line / citations

```json
"citations": [
  {
    "ref_id": "1",
    "source_text": "GAO FY24 IT Budget Analysis (GAO-24-106720)",
    "is_named_org": true,
    "is_dated": true,
    "is_specific": true,
    "source_type": "external-public"               // NEW — V1-judg
  }
]
```

`source_type` enum: `"external-public" | "external-paywall" | "internal-self" | "generic-vague" | "uncheckable"`.

- **external-public**: GAO reports, SEC filings, government datasets, published news with URL
- **external-paywall**: analyst reports behind paywall, Capital IQ, industry databases
- **internal-self**: student's target company, student's internal model, anything the deck owner controls
- **generic-vague**: "industry reports", "Google", "AI research", "various sources"
- **uncheckable**: source named but cannot be verified (private interviews, unpublished docs)

### Icon atom

```json
{
  "variant": "semantic|decorative|wayfinding|logo",
  "description": "string",
  "is_third_party_brand_logo": true                // NEW — V1-obs
}
```

### N-card-grid

```json
{
  "card_count": 3,
  "orientation": "horizontal|vertical|2d-grid",
  "cards": [
    {
      "heading": "string",
      "body": "string",
      "body_word_count": 8,                        // NEW — TXT
      "icon_description": "string|null",
      "sub_label": "string|null",
      "accent_color": "#hex|null",
      "stat": "string|null"
    }
  ],
  "sub_labels_identical_across_cards": true,
  "card_body_length_variance": "low|moderate|high",
  "card_headings_are_imperatives": false           // NEW — TXT
}
```

### Per-slide observations

Add these fields to the existing observations block:

```json
{
  "word_count": 85,
  "palette": [...],

  // REVISED enum (was "supports|mismatch|partial|n-a")
  "title_body_alignment": "supports|title_overreaches_body|body_has_material_not_serving_title|internal_contradiction|partial|n-a",

  "title_body_mismatch_detail": "string|null",
  "chart_has_takeaway": true,
  "llm_smell_tells": [...],
  "antithesis_constructions": [...],
  "hedging_language": [...],
  "three_item_list_detected": false,
  "identical_sub_labels_on_cards": null,
  "chart_craft_issues": [...],
  "mechanics_issues": [...],
  "pyramid_compliance": {...},
  "free_form": "string",

  // --- NEW fields below ---
  "has_clear_focal_point": true,                   // V1-judg
  "is_single_visual_slide": false,                 // V1-judg
  "empty_follow_on_sentences": [                   // V1-judg
    {"atom_id": "s03-a04", "quote": "Is real."}
  ],
  "self_referential_phrases": [                    // TXT
    {"atom_id": "s05-a04", "quote": "as noted on slide 3"}
  ],
  "vague_quantifiers_without_number": [            // TXT
    {"atom_id": "s03-a01", "word": "significant"}
  ],
  "has_placeholder_text": false,                   // TXT
  "has_edge_clipping": false,                      // V1-obs
  "takeaway_banner_restates_title": false,         // V1-judg

  "unified_by_explicit_structure": {               // V1-judg
    "is_unified": true,
    "device": "arrow|grid|numbered-flow|equation|none",
    "content_block_count": 3
  },

  // Exec-summary slides only (role_guess == "executive-summary")
  "exec_summary_components": {                     // V1-judg
    "situation": true,
    "complication": true,
    "resolution": true,
    "recommendation": true,
    "next_steps": true
  }
}
```

### Per-slide argument (add one field)

```json
"argument": {
  ...existing v1.0 fields...,

  // Recommendation slides only (role_guess == "recommendation")
  "next_steps_reverse_map_to_findings": false      // NEW — V1-judg
}
```

## Deck-level additions

### `deck.features` — new aggregates

```json
{
  ...existing v1.0 features...,

  "word_count_std_dev": 42.3,                      // AGG
  "has_breathing_slides": false,                   // AGG (count slides with word_count < 30)

  "title_word_counts": [5, 9, 15, 17, 19, 28, 13, 12, 5],  // AGG
  "title_length_std_dev": 7.0,                     // AGG
  "title_casing_consistent": true,                 // AGG
  "bullet_punctuation_consistent": true,           // AGG
  "number_format_consistent": true,                // AGG

  "kicker_identical_text_repeats": 2,              // AGG (max freq of any repeated kicker text)

  "source_type_count": 2,                          // AGG (unique values across all citations.source_type)
  "source_line_format_variants": 1,                // AGG (cluster source-line strings by template)

  "page_number_integrity": {                       // AGG
    "observed_sequence": [null, 1, 2, 3, 4, 5, 5, 8, 9],
    "expected_sequence": [null, 1, 2, 3, 4, 5, 6, 7, 8],
    "duplicates": [5],
    "skips": [6, 7],
    "missing_slides": [],
    "is_clean": false
  },

  "has_letterbox_bleed": false,                    // AGG from PDF page size + per-slide edge-clip

  // --- From Option C Insight-7 proxies ---
  "core_slides_claim_is_specific_ratio": 0.83,     // AGG
  "core_slides_generic_applicability_specific_ratio": 0.67   // AGG
}
```

### `deck.observations` — one addition

```json
{
  ...existing v1.0 observations...,

  "parallel_card_structure_across_slides": {       // DECK
    "detected": false,
    "slides": [],
    "shared_sub_labels": []
  }
}
```

### `deck.observations.coherence` — revisions for Option C

**Drop these fields** (were EXT-only in v1.0):
- `non_obviousness.is_insight_in_company_filings_already`
- `non_obviousness.is_insight_in_standard_analyst_coverage`
- `pressure_test.strongest_counterargument_a_skeptic_would_raise`

**Retain and redefine** (now DECK-fillable from internal signals only):

```json
"coherence": {
  ...,

  "pressure_test": {
    "assumptions_made_explicit_in_deck": true,         // DECK
    "deck_anticipates_it": "holds-up|partial|unaddressed|weak",  // DECK — based on internal signals
    "detail": "Deck states assumptions X,Y,Z; hedges near strongest claim on slide N; names alternative on slide M."
  },

  "non_obviousness": {
    "pushes_past_observation_to_interpretation": true,  // DECK
    "detail": "string"
  },

  "strategic_framework": {
    // tri-state change (was bool + detail)
    "market": "missing|named-unsubstantiated|substantiated",     // DECK
    "market_detail": "string",
    "unique_users": "missing|named-unsubstantiated|substantiated",
    "unique_users_detail": "string",
    "resources_and_capabilities": "missing|named-unsubstantiated|substantiated",
    "resources_and_capabilities_detail": "string",
    "sustainability": "missing|named-unsubstantiated|substantiated",
    "sustainability_detail": "string",
    "feasibility": "missing|named-unsubstantiated|substantiated",
    "feasibility_detail": "string"
  }
}
```

## Insight-7 redefinition (Option C)

Because EXT is out of scope, Insight-7 hurdles are redefined to be fillable from internal deck signals only. Encoded in `rubric.yaml`:

```yaml
insight_7_hurdles:
  all_of:
    - coherence.thesis_is_specific: true
    - coherence.recommendation.specificity: "specific-action"
    - coherence.recommendation.is_execution_or_substitute: "execution"
    - coherence.pressure_test.deck_anticipates_it: ["holds-up", "partial"]
    - coherence.pressure_test.assumptions_made_explicit_in_deck: true
    - coherence.non_obviousness.pushes_past_observation_to_interpretation: true
    - features.core_slides_claim_is_specific_ratio: ">= 0.80"
    - features.core_slides_generic_applicability_specific_ratio: ">= 0.70"

insight_6_hurdles:
  all_of:
    - coherence.recommendation.specificity: ["specific-action", "directional"]
    - coherence.non_obviousness.pushes_past_observation_to_interpretation: true
    - coherence.pressure_test.deck_anticipates_it: ["holds-up", "partial"]
    - features.core_slides_claim_is_specific_ratio: ">= 0.60"
  at_least_one:
    - coherence.pressure_test.assumptions_made_explicit_in_deck: true
    - coherence.internal_contradictions: "length == 0"
```

The 0.80 / 0.70 ratios are initial values. Re-calibrate against 5 known-graded decks before locking.

## Pattern → field map (for rubric.yaml)

Every pattern in `.claude/skills/grade-deck/patterns.md` now maps to typed JSON fields:

| Pattern | Condition over `deck.json` |
|---|---|
| **G01** Assignment artifact in title | `any slide`: `atoms[type=title].contains_course_artifact == true` |
| **G02** Missing contact info | `slides[0].atoms` has no atom of type `metadata-block` with non-empty `contact` |
| **G03** Missing/weak exec summary | No slide has `role_guess == "executive-summary"`, OR that slide has `exec_summary_components.{situation,complication,resolution}` any false |
| **G04** Untraceable sources on key claims | `any slide with numeric_claims`: any `source-line.citations[].source_type == "generic-vague"` |
| **G05** AI-scaffolding saturation | count of firing patterns in {S-C01,S-C02,S-C03,S-C04,S-C05,S-C06,S-C07,S-C07a,S-C07b,S-C07c,S-C07d,S-C07e} ≥ 3 |
| **S-B01** Title contradicts own chart | `any slide`: `observations.title_body_alignment in ["title_overreaches_body","internal_contradiction"]` AND has a chart atom AND (chart `readability.has_takeaway_annotation == false` OR `chart_math.ties == false`) |
| **S-B02** Title-internal contradiction | `any slide`: `atoms[type=title].has_internal_contradiction == true` |
| **S-C01** Topic-label title | `core slides`: count where `atoms[type=title].action == false` ≥ 1 |
| **S-C02** Imperative-verb step label in cards | `any slide`: `atoms[type=n-card-grid].card_headings_are_imperatives == true` |
| **S-C03** Empty container label kicker | `any slide`: `atoms[type=kicker].is_empty_container_label == true` |
| **S-C04** "Move" as noun | `any slide`: `atoms[type=title].uses_move_as_noun == true` |
| **S-C05** Antithesis "not X, it's Y" | `any slide`: `observations.antithesis_constructions.length > 0` |
| **S-C06** AI-explainer parenthetical | `any slide`: `atoms[type=title].has_ai_explainer_parenthetical == true` |
| **S-C07** Empty follow-on sentence | `any slide`: `observations.empty_follow_on_sentences.length > 0` |
| **S-C07a** Self-referential scaffolding | `any slide`: `observations.self_referential_phrases.length > 0` |
| **S-C07b** Formulaic parallel recommendation slides | `deck.observations.parallel_card_structure_across_slides.detected == true` OR any single slide with `n-card-grid.sub_labels_identical_across_cards == true` on a recommendation slide |
| **S-C07c** Next-steps reverse-maps to deck findings | `any recommendation slide`: `argument.next_steps_reverse_map_to_findings == true` |
| **S-C07d** Uniform title length | `features.title_length_std_dev <= 2.0` AND `core_slide_count >= 5` |
| **S-C07e** Uniform parallel-bullet length | `any n-card-grid slide`: `card_body_length_variance == "low"` AND card_count ≥ 3 |
| **S-C08** Devil's-advocate fail | `coherence.cuttable_slides.length > 0` |
| **S-C09** Redundant callout | `any slide`: `observations.takeaway_banner_restates_title == true` |
| **S-C10** Generic next-steps | `coherence.recommendation.specificity in ["do-more-analysis"]` OR presence of generic-ask atom pattern |
| **S-C11** Two takeaways fighting | TBD — add `observations.has_two_competing_claims:bool` in v1.2 if needed |
| **S-C12** Title-flow breaks | `observations.title_flow.weak_links.length > 0` |
| **S-C13** Visual unification fail | `any slide`: `observations.unified_by_explicit_structure.is_unified == false` AND `content_block_count >= 4` |
| **S-C14** Letterbox bleed | `features.has_letterbox_bleed == true` |
| **S-C15** Body contains material not serving title | `any slide`: `observations.title_body_alignment == "body_has_material_not_serving_title"` |
| **I-C01** So-what missing | `count of slides with so_what_stated == false among analytical-body` ≥ 1 |
| **I-C02** Unaddressed strongest counterargument | `coherence.pressure_test.deck_anticipates_it in ["unaddressed","weak"]` |
| **I-C03** Vague quantifier without number | `any slide`: `observations.vague_quantifiers_without_number.length > 0` |
| **I-C04** Surface-level analysis | `coherence.non_obviousness.pushes_past_observation_to_interpretation == false` |
| **E-B01** Chart math doesn't tie | `any chart atom`: `chart_math.ties == false` |
| **E-B02** Chart title's claim doesn't match chart data | `any slide with chart`: `title_body_alignment in ["title_overreaches_body","internal_contradiction"]` |
| **E-B03** Cross-slide numerical inconsistency | `coherence.number_reconciliation_issues.length > 0` |
| **E-B04** Magnitude insanity | `any slide`: any `argument.numeric_claims[].plausible == false` |
| **E-B05** Temporal validity failure | *cannot derive without EXT; leave unfireable in v1.1* |
| **E-B06** Fabricated-looking source | `any slide with numeric_claims`: any `source-line.citations[].source_type == "internal-self"` used for a headline number |
| **E-C01** Format-matches-content violation | *needs `observations.format_appropriate_for_content:bool` (add in v1.2)* |
| **E-C02** Missing assumption statement | `count of numeric_claims[].derivation_shown == false across deck` ≥ 2 |
| **E-C03** Vague source | `any slide`: any `source-line.citations[].is_specific == false` |
| **E-C04** On-slide source missing | `features.slides_missing_sources_with_quant_claims.length > 0` |
| **E-D01** Appendix bibliography incomplete | *needs bibliography structure (add in v1.2)* |
| **E-D02** Single vague source | `count of slides with at least one vague citation == 1` |
| **E-D03** Source line format varies | `features.source_line_format_variants > 1` |
| **D-B01** Edge clipping | `any slide`: `observations.has_edge_clipping == true` |
| **D-B02** Placeholder text | `any slide`: `observations.has_placeholder_text == true` |
| **D-C01** Uniform high density | `features.avg_words_per_slide >= 150` AND `features.word_count_std_dev <= 30` |
| **D-C02** Low visual variety | `features.slides_with_charts / features.core_slide_count < 0.5` |
| **D-C03** Focal-point fail | `count of core slides with has_clear_focal_point == false` ≥ 2 |
| **D-C04** Inconsistent semantic color | `observations.color_consistency.issues.length > 0` |
| **D-C05** Text-heavy body slide | `any slide`: `word_count > 250` AND has no chart atom |
| **D-C05a** Deck density high | `features.avg_words_per_slide > 180` OR `features.max_words_per_slide > 250` |
| **D-C06** Color without meaning | *evaluated within `color_consistency.issues` free-text; v1.2 may add a structured flag* |
| **D-D04** Inconsistent title casing | `features.title_casing_consistent == false` |
| **D-D05** Inconsistent bullet punctuation | `features.bullet_punctuation_consistent == false` |
| **D-D06** Inconsistent number formatting | `features.number_format_consistent == false` |
| **D-D07** Page number missing on some slides | `features.page_number_integrity.is_clean == false` |
| **D-D09** Chart missing title/takeaway | `count of chart atoms with readability.has_takeaway_annotation == false` ≥ 2 |
| **D-D10** Axis labels / units missing | `any chart atom`: `readability.has_axis_units == false` |
| **D-D11** Legend missing or unclear | `any multi-series chart`: `readability.has_legend_if_multiseries == false` |

Patterns marked *cannot derive* or *needs X (add in v1.2)* are non-firing in the v1.1 pipeline. They can be added as schema migration when bandwidth allows.

## Scorer architecture (Phase 4 spec)

Locked:

- `rubrics/deck-quality-rubric.yaml` — weights, descriptors, gate→cap, pattern tier, hurdles (YAML-as-config)
- `scripts/score_deck.py` — pattern functions as pure Python over deck.json (YAML declaratively references by ID; pattern-firing logic is in Python for readability)
- `scripts/format_grade.py` — scoring.json → student-facing markdown

Pattern functions signature:

```python
def s_b01_title_contradicts_chart(deck: dict) -> list[Finding]:
    findings = []
    for s in deck["slides"]:
        if s["observations"]["title_body_alignment"] in ("title_overreaches_body", "internal_contradiction"):
            if any(a["type"] in CHART_TYPES for a in s["atoms"]):
                findings.append(Finding(
                    pattern_id="S-B01",
                    dimension="storyline",
                    tier=3,
                    slides=[s["index"]],
                    evidence=s["observations"]["title_body_mismatch_detail"]
                ))
    return findings
```

Tier-anchor scoring (from SKILL.md section 4d):

```python
def tier_anchor_score(findings_by_dim: dict[str, list[Finding]], dim: str) -> int:
    t3 = sum(1 for f in findings_by_dim[dim] if f.tier == 3)
    t2 = sum(1 for f in findings_by_dim[dim] if f.tier == 2)
    if t3 == 0 and t2 <= 1: return 6  # provisional; will be confirmed/dropped by hurdle check
    if t3 == 0 and 2 <= t2 <= 3: return 5
    if t3 == 0 and 4 <= t2 <= 5: return 4
    if t3 == 1: return 4
    if t3 == 0 and t2 >= 6: return 3
    if t3 >= 2: return 3
    return 2
```

Hurdle enforcement:

```python
def enforce_hurdles(deck: dict, provisional: int, dim: str) -> int:
    if provisional == 7 and not passes_level_7_hurdles(deck, dim):
        provisional = 6
    if provisional == 6 and not passes_level_6_hurdles(deck, dim):
        provisional = 5
    return provisional
```

Gate caps applied last:

```python
def apply_gate_caps(dim_score: int, gates_fired: list[str], dim: str) -> int:
    cap = min((g.cap for g in gates_fired if g.target == dim), default=7)
    return min(dim_score, cap)
```

Weighted total:

```python
def final_score(scores: dict[str, int], weights: dict[str, float]) -> float:
    return sum(scores[d] * weights[d] for d in scores) * 100 / 7
```

Output: `scoring.json` with per-pattern findings, per-dimension score derivation (provisional → hurdles → gates → final), weighted total, and a diff-friendly audit trail.

