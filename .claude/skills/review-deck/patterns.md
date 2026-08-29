# Review-Deck Pattern Catalog

Flat catalog of specific things to look for on a slide. No tiers (severity is judged per instance in SKILL.md), no dimensions.

Each entry has:
- **Name** — plain-language label used in the review output
- **Signal** — what to look for, concretely
- **Applies to** — which L2 slide buckets this check is relevant for
- **Example** — a representative case

Use these alongside the step-back questions in SKILL.md Step 4 Track B. The catalog names specific flaws; the step-back questions catch everything else.

---

## Logic & structure

### Title contradicts own chart
**Signal:** Title uses a strong or causal verb ("dictates", "drives", "guarantees", "proves", "ensures", "forces") that the chart or data can only support at associative strength.
**Applies to:** Analysis, Resolution.
**Example:** Title "X dictates Y" over a chart showing X is the #3 factor.

### Title-internal contradiction
**Signal:** Title has a setup clause and a twist clause that logically negate each other.
**Applies to:** Analysis, Resolution.
**Example:** "URBN is a multi-engine portfolio, but Urban Outfitters dictates growth."

### Topic-label title
**Signal:** Title names the rhetorical move rather than stating a conclusion: "Market Overview", "The Opportunity", "The Challenge", "Diagnosis", "Recommendation", "The Path Forward".
**Applies to:** Situation, Analysis, Resolution.
**Example:** "The Opportunity" over a market-size chart.

### Hedged action title
**Signal:** Title uses "could potentially", "may represent", "appears to suggest" instead of committing to a claim.
**Applies to:** Analysis, Resolution.
**Example:** "Urban Outfitters could potentially benefit from brand diversification."

### Title-body mismatch (body contradicts title)
**Signal:** Body makes a point the title doesn't capture, or body elements (KPIs, bullets, a secondary chart) support a claim different from the title's.
**Applies to:** Analysis, Resolution.
**Example:** Title says "Americas comp is −1% after new-store adjustment"; body has a KPI card on Mexico gross margin not referenced elsewhere.

### So-what missing
**Signal:** Slide states a fact without pushing to the implication for the decision.
**Applies to:** Analysis.
**Example:** "US revenue grew 12%" with no connection to the recommendation.

### Redundant slide
**Signal:** Slide restates what an earlier slide already said. Removing it would not weaken the deck.
**Applies to:** any.
**Example:** Mid-deck slide restating content in the exec summary.

### Two takeaways fighting on one slide
**Signal:** Slide tries to make two distinct arguments and dilutes both.
**Applies to:** Analysis, Resolution.
**Example:** One slide arguing both "market is growing" and "competitor is weak."

### Redundant callout
**Signal:** Sidebar or "Key Takeaways" block restates what's already on the slide.
**Applies to:** any.
**Example:** "Key Takeaway" sidebar reading back the action title.

### Vague quantifier without number
**Signal:** Title or callout uses "significant", "substantial", "major", "considerable", "meaningful" without the actual number.
**Applies to:** Analysis, Resolution.
**Example:** "Significant revenue opportunity in SMB" with no $ figure.

### Visual unification fail
**Signal:** Slide has 4+ independent blocks (chart + KPI row + text cards + callout) not tied together by explicit structure (arrow, numbered flow, grid, equation).
**Applies to:** Analysis, Resolution.
**Example:** Bar chart plus unrelated strip of 5 big-number KPIs at the bottom.

### Broken internal reference
**Signal:** Slide refers to "see Appendix B" or "slide 7" that doesn't exist.
**Applies to:** any.

### Generic next steps
**Signal:** Next-steps slide asks generic questions ("What's your X?", "How can we help?") rather than naming specific workstreams with deliverables.
**Applies to:** Resolution.
**Example:** "Discuss how we can help you grow."

---

## AI / LLM tells

### Imperative-verb step labels in numbered cards
**Signal:** Numbered cards with verb-as-label headers even when paired with concrete content ("01 DIAGNOSE / 02 RE-ALLOCATE / 03 PRESSURE-TEST").
**Applies to:** Resolution.

### Empty container label
**Signal:** ALL-CAPS or colored kicker above a block explaining what's in the block rather than stating a claim: "SO WHAT:", "KEY INSIGHT:", "IMPACT:", "WHAT I NOTICED", "WHAT IT PRODUCES", "FROM THE 10-K", "THE PROBLEM", "THE OPPORTUNITY", "THE ASK".
**Applies to:** any.
**Example:** Red "WHAT I NOTICED | 2 OF 3" kicker above slide title.

### "Move" as noun for recommendations
**Signal:** The word "move" or "moves" used as a noun for a recommendation in titles or exec summary ("the highest-return move is...", "the next move should be..."). Distinctive LLM tell; real consulting writing says "recommendation" or "action" or states the action directly. Do not flag legitimate consulting vocabulary like "lever", "unlock", or "win" used in the student's own prose.
**Applies to:** Resolution, Structural (exec summary).

### Antithesis "not X, it's Y"
**Signal:** Negate-then-pivot construction: "The gap isn't X, it's Y", "Not X, but Y", "X is not A, it is B".
**Applies to:** any.
**Example:** "The path forward isn't more stores, it's diagnosing why..."

### AI-explainer parenthetical
**Signal:** Parenthetical inside a title or callout narrating how content was produced: "(verbatim)", "(paraphrased)", "(my synthesis)", "(from above)", "(as noted)", "(illustrative)".
**Applies to:** any.
**Example:** "FROM THE 10-K (verbatim)" kicker on a quote card.

### Empty follow-on sentence
**Signal:** Short punchy declarative (under 8 words) after a quantitative claim, adding no new actor, number, or implication.
**Applies to:** Analysis, Resolution.
**Example:** "Premium share is the only game." "A gap waiting to be closed."

### Self-referential scaffolding
**Signal:** Deck narrates its own structure: "grounded in slide 6", "as noted above", "building on slide 4", "per finding on slide 3", "each grounded in a finding in this deck".
**Applies to:** Resolution.
**Example:** "Three workstreams, each grounded in a finding in this deck."

### Formulaic parallel recommendation slides
**Signal:** Three (or N) recommendation slides use identical column/card grids with identical sub-labels ("Why It Works" / "What It Delivers" / "Risk") repeated across all. Real consulting decks vary the canvas per recommendation.
**Applies to:** Resolution (Workstream card, Recommendation).

### Next-steps reverse-maps to deck findings
**Signal:** Next-steps slide restates slides already presented, dressed as workstreams ("pressure-test the slide 3 finding", "validate the slide 5 claim"). Real next steps address what the deck cannot yet answer and would require new primary data.
**Applies to:** Resolution.

### Uniform title length
**Signal:** Action titles across the deck cluster in a tight word-count band (e.g., every title is 14-19 words). If 5+ action titles fall within a ±3 word range, fires.
**Applies to:** deck-level (report under cross-slide template saturation; can also note on individual slides).

### Uniform parallel-bullet length
**Signal:** In a multi-column or multi-card parallel layout, bullets across parallel items are within ±2 words of each other. LLM parallel-structure tic.
**Applies to:** Resolution.

### Surface-level analysis presented as insight
**Signal:** Uses easily available facts (recent headlines, standard 10-K summary) without original synthesis on top.
**Applies to:** Analysis.
**Example:** Deck title is "Apple is facing iPhone saturation" sourced only from news articles.

### Unaddressed strongest counterargument
**Signal:** The obvious skeptic objection at the target company isn't acknowledged anywhere (no assumptions stated, no alternative tested).
**Applies to:** Resolution (Recommendation, Synthesis).

---

## Evidence

### Chart math doesn't tie
**Signal:** Parts exceed stated whole, percentages don't sum, bars visually overshoot the total.
**Applies to:** Analysis.
**Example:** Agency bars exceed the $750M total they're supposed to disaggregate.

### Chart title's claim doesn't match chart data
**Signal:** Title asserts a magnitude or direction the chart doesn't show.
**Applies to:** Analysis.
**Example:** Title says "2x", chart shows 1.8x; title says "cheaper", chart shows parity.

### Cross-slide numerical inconsistency
**Signal:** Same metric shows different values on different slides.
**Applies to:** deck-level (flag on the later slide).
**Example:** Slide 4 shows +$373M, slide 9 model shows max $259M.

### Magnitude insanity
**Signal:** Quantitative claim implausible for the company or industry.
**Applies to:** Analysis.
**Example:** TAM claim 10x reality.

### Temporal validity failure
**Signal:** "Current" data is actually outdated, or recommended action already executed by the company.
**Applies to:** Situation, Resolution.
**Example:** Recommending an acquisition the company closed 6 months ago.

### Fabricated-looking source
**Signal:** Source names a document that can't plausibly exist (internal model cited as external, made-up report number, generic uncheckable phrasing like "proprietary analysis" without assumptions shown).
**Applies to:** Analysis, Resolution.

### Format-matches-content violation
**Signal:** Quantitative trend or multi-variable comparison presented as text cards or big-number callouts instead of chart or table.
**Applies to:** Analysis.
**Example:** Margin improvement trend shown as 4 KPI cards with no chart.

### Missing assumption statement
**Signal:** Derived or estimated figure (TAM, revenue opportunity, savings) without the assumption chain shown.
**Applies to:** Analysis, Resolution.
**Example:** "$100M opportunity" with no derivation.

### Vague source
**Signal:** Source incomplete: "Statista" without dataset, news outlet without article title, "industry reports" without naming them, "company website" without page.
**Applies to:** Analysis, Resolution.

### Untraceable source
**Signal:** Quantitative claim cites "Google", "Internet", "industry reports", "AI research", "ChatGPT", "various sources", or "analyst estimates" without naming the analyst.
**Applies to:** Analysis, Resolution.
**Example:** "Source: Google" on a revenue-growth claim.

### On-slide source missing
**Signal:** Slide makes numerical claim with no source line anywhere on slide (even if appendix has sources).
**Applies to:** Analysis, Resolution.

### Appendix bibliography incomplete
**Signal:** Appendix sources page present but missing report titles, dates, or URLs on one or more entries.
**Applies to:** Structural (Sources).

### Source line format varies
**Signal:** Source lines use different templates across slides (some with page, some without; some italic, some not).
**Applies to:** deck-level (Cross-slide Inconsistencies).

---

## Craft & design

### Edge clipping / text overflow
**Signal:** Slide text or visual element extends past slide boundary and is cut off in the PDF.
**Applies to:** any.
**Example:** "Strip out new stores and the Mexico acquisition, and Am" cuts off mid-word.

### Placeholder text left in
**Signal:** "TK", "[insert X]", "Lorem ipsum", "[client name]", template sample text.
**Applies to:** any.

### Letterbox bleed
**Signal:** PDF exported at Letter/A4 landscape with visible empty bands top and bottom across 3+ body slides (Print-to-PDF with paper default).
**Applies to:** deck-level.

### Assignment artifact in title
**Signal:** Slide title or header includes "P1", "P2", "STRAT 325", "Capstone", or template section names used as slide titles.
**Applies to:** Structural (Title), any.
**Example:** Slide titled "P2 Pitch Deck".

### Missing contact info on title slide
**Signal:** Title slide lacks student name or email.
**Applies to:** Structural (Title).

### Missing or weak executive summary
**Signal:** No exec summary, or exec summary doesn't compress the full argument into one standalone slide (jumps to market overview, or is just a topic list).
**Applies to:** Structural (Executive summary).

### Uniform high density across deck
**Signal:** Every core slide at similar heavy density (headline + subhead + 3 content blocks + KPI row); no breathing slides.
**Applies to:** deck-level.

### Low visual variety
**Signal:** Fewer than ~50% of core slides carry a genuine visual device (chart, table, diagram, icon framework); rest are text-only.
**Applies to:** deck-level.

### Focal-point fail
**Signal:** No visual hierarchy on slide, eye darts around, equally-weighted blocks, no dominant visual.
**Applies to:** Analysis, Resolution.

### Text-heavy body slide
**Signal:** Core slide exceeds ~250 words without a chart, table, or framework clearly carrying the message. Above 500 words is a design problem regardless.
**Applies to:** Analysis, Resolution.

### Deck-average word density high
**Signal:** Average words per core slide exceeds ~180, or max single core-slide word count exceeds ~250. Client-ready decks average ~80-140 words per core slide.
**Applies to:** deck-level.

### Color without meaning
**Signal:** Color applied decoratively rather than semantically. Pick a colored element (a number in red, a highlighted box). Ask "what does this color mean here?" If "it just looks nice" or the meaning changes slide to slide, fires.
**Applies to:** any.

### Inconsistent semantic color
**Signal:** Same color means different things across slides.
**Applies to:** deck-level.
**Example:** Green = positive on slide 3, green = competitor on slide 5.

### Intra-element whitespace imbalance
**Signal:** Content inside a card unbalanced: headline at top, paragraph at bottom, large empty middle (or vice versa).
**Applies to:** any.

### Alignment drift
**Signal:** Elements not aligned to consistent grid; left edges vary without reason.
**Applies to:** any.

### Font family inconsistency
**Signal:** Mixed font families across slides without systematic reason.
**Applies to:** deck-level.

### Inconsistent title casing
**Signal:** Some titles Title Case, others Sentence case, others ALL CAPS, without system.
**Applies to:** deck-level.

### Inconsistent bullet punctuation
**Signal:** Some bullets end with period, some don't, within same slide or deck.
**Applies to:** any.

### Inconsistent number formatting
**Signal:** "$1.3B" on one slide, "$1,300M" on another, "1.3 billion" on a third.
**Applies to:** deck-level.

### Page number or footer missing on some slides
**Signal:** Footer present on most slides but missing on one or two.
**Applies to:** deck-level.

### Stock photo that doesn't add meaning
**Signal:** Decorative image (skyline, handshake, laptop) used as filler.
**Applies to:** any.

### Chart missing title or takeaway
**Signal:** Chart has no title caption, or has descriptive title but no "so what" takeaway.
**Applies to:** Analysis.
**Example:** "Revenue by Segment" title with no "X segment drives 60%" note.

### Axis labels or units missing
**Signal:** Axis present but no label or units.
**Applies to:** Analysis.

### Legend missing or unclear
**Signal:** Multi-series chart with no legend, or legend uses unclear labels ("Series 1", "Series 2").
**Applies to:** Analysis.

### Inconsistent data labels
**Signal:** Some bars labeled with values, others not, within same chart.
**Applies to:** Analysis.

### Truncated or rotated axis labels
**Signal:** Axis labels cut off, rotated 90° to fit, or overlapping.
**Applies to:** Analysis.

### Single rough slide amid polish
**Signal:** One slide markedly less polished than the rest (different template, misaligned, rushed).
**Applies to:** deck-level (flag on the rough slide).

---

## Not checked (explicit non-goals)

- "Suspected hallucination" or "likely fabricated" framing. Phrase citation-plausibility issues developmentally: *"Source on slide X could not be verified; strengthening with a named report and date would help."*
- Em dashes in student writing (not a deck-quality concern).
- "This looks AI-generated" as a vibe. Catch specific tells via the AI / LLM tells section, not feel.
- Grading the student's target company choice.
- Grading whether the recommendation is "correct."
