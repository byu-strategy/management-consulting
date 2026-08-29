# Grade-Deck Pattern Catalog

Single detection catalog organized by rubric dimension. Each pattern fires once per deck unless the signal says otherwise. Record every hit with: pattern name, tier, slide ref, and one-line note with specific evidence.

**Columns:**
- **ID** — stable internal identifier (used for calibration and diffs; not shown to students)
- **Name** — plain-language label used in the student-facing findings table
- **Tier** — severity: `3` client-embarrassing, `2` visible professional flaw, `1` polish miss
- **Signal** — what to look for, concretely
- **Example** — representative text, image, or case

**How tiers inform scoring.** The SKILL.md scoring step matches findings to rubric descriptors. Tier guides the match: Tier-3 findings typically mean a dimension can't exceed 5; 2-3 Tier-2 findings typically mean level 5; 4-5 Tier-2 typically means level 4. Final call is the rubric descriptor match, not tier arithmetic.

---

## Gates (hard caps, applied outside the dimension walks)

| ID | Name | Dim capped at 4 | Signal | Example |
|---|---|---|---|---|
| G01 | Assignment artifact in title | Storyline | Slide title or header includes "P1", "P2", "STRAT 325", "Capstone", or template section names used as slide titles | Slide titled "P2 Pitch Deck" |
| G02 | Missing contact info | Storyline | Title slide lacks student name or email | No email on title slide |
| G03 | Missing or weak executive summary | Storyline | No exec summary, or exec summary doesn't compress the full argument into one standalone slide | First body slide jumps to market overview with no summary |
| G04 | Untraceable sources on key claims | Evidence | Quantitative claims cite "Google", "Internet", "industry reports", "AI research", "ChatGPT", "various sources", "Statista" without dataset, or "analyst estimates" without the analyst | "Source: Google" on a revenue-growth claim |
| G05 | AI-scaffolding saturation | Storyline (cap 4) AND Insight (drop one level) | 3 or more of {S-C01, S-C02, S-C03, S-C04, S-C05, S-C06, S-C07, S-C07a, S-C07b, S-C07c} fire on the deck. Interpretation: the deck is LLM-template-saturated. The student accepted the model's output without careful review and editing. The recommendation logic is the scaffolding, not the student's own reasoning. | Deck has "Move 01/02/03" kickers (S-C02) + "Why It Works / What It Delivers" labels (S-C03) + "moves" as noun (S-C04) + "The gap isn't X, it's Y" (S-C05) = gate fires |

---

## Storyline patterns

*Does the deck tell a coherent, answer-first story from first slide to last?*

### Tier 3 — client-embarrassing

| ID | Name | Signal | Example |
|---|---|---|---|
| S-B01 | Title contradicts own chart (verb overreach) | Title uses strong/causal verb ("dictates", "drives", "guarantees", "proves", "ensures", "forces") that the body chart or data can only support at relational or associative strength | Title "X dictates Y" over a chart showing X is the #3 factor |
| S-B02 | Title-internal contradiction | Title has setup-clause and twist-clause that logically negate each other | "URBN is a multi-engine portfolio, but Urban Outfitters dictates growth" |

### Tier 2 — visible professional flaw

| ID | Name | Signal | Example |
|---|---|---|---|
| S-C01 | Topic-label title | Title names the rhetorical move rather than stating the conclusion: "Market Overview", "The Opportunity", "The Challenge", "Diagnosis", "Recommendation", "Forecasting", "The Path Forward" | "The Opportunity" over a market-size chart |
| S-C02 | Imperative-verb step label in numbered cards | Numbered cards with verb-as-label headers even when paired with concrete content | "01 DIAGNOSE / 02 RE-ALLOCATE / 03 PRESSURE-TEST" |
| S-C03 | Empty container label | ALL-CAPS or colored kicker above a block explaining what's in the block rather than stating a claim: "SO WHAT:", "KEY INSIGHT:", "IMPACT:", "WHAT I NOTICED", "WHAT IT PRODUCES", "FROM THE 10-K", "THE PROBLEM", "THE OPPORTUNITY", "THE ASK" | Red "WHAT I NOTICED \| 2 OF 3" kicker above slide title |
| S-C04 | "Move" as noun for recommendations | The word "move" or "moves" used as a noun for a recommendation in titles or exec summary ("the highest-return move is...", "the next move should be..."). This is a distinctive LLM tell; real consulting writing says "recommendation" or "action" or just states the action directly. Do NOT flag legitimate consulting vocabulary like "lever", "unlock", "win", or "optimize" used in the student's own prose — these are appropriate in a consulting deck. | "The highest-return move is to institutionalize..." |
| S-C05 | Antithesis "not X, it's Y" | Negate-then-pivot construction: "The gap isn't X, it's Y", "Not X, but Y", "X is not A, it is B" | "The path forward isn't more stores, it's diagnosing why..." |
| S-C06 | AI-explainer parenthetical | Parenthetical inside a title or callout narrating how content was produced: "(verbatim)", "(paraphrased)", "(my synthesis)", "(from above)", "(as noted)", "(illustrative)" | "FROM THE 10-K (verbatim)" kicker on a quote card |
| S-C07 | Empty follow-on sentence | Short punchy declarative (<8 words) after a quantitative claim, adding no new actor, number, or implication: "A gap waiting to be closed." "Is real." "Is clear." "The opportunity is not theoretical." | "Premium share is the only game." |
| S-C07a | Self-referential scaffolding | Deck narrates its own structure: "grounded in slide 6", "as noted above", "building on slide 4", "per finding on slide 3", "each grounded in a finding in this deck", "as established earlier", "per the analysis above". AI tell: the model is stitching its output to itself rather than the student committing to the claim on its own merits. | "Three workstreams, each grounded in a finding in this deck" |
| S-C07b | Formulaic parallel recommendation slides | Three (or N) recommendation slides use identical column/card grids with identical sub-labels ("Why It Works" / "What It Delivers" / "Risk" repeated across all three). Real consulting decks vary the canvas per recommendation because the argument shape differs. Uniform parallelism is an LLM template tell. | Slides 5/6/7 all formatted as "Move / Why It Works / What It Delivers / Risk" column grid |
| S-C07c | Next-steps reverse-maps to deck findings | Next-steps slide is a restatement of slides already presented, dressed as workstreams. Workstreams are "pressure-test the slide 3 finding", "validate the slide 5 claim", "confirm the slide 7 estimate". Real proposed next steps address what the *deck cannot yet answer* and would require new primary data, not re-chewing the deck's own analysis. | "Workstream 1: pressure-test the cross-sell gap (slide 3). Workstream 2: validate the client-band thesis (slide 6)." |
| S-C07d | Uniform title length | Action titles across the deck cluster in a tight word-count band (e.g., every title is 14-19 words) or tight character-count band. Real consulting titles vary meaningfully in length because the argument shape differs per slide. Uniform length is an LLM-template tell. Threshold: if 5+ action titles fall within a ±3 word range, fires. | All 7 action titles between 15-19 words |
| S-C07e | Uniform parallel-bullet length | In a multi-column or multi-card parallel layout (three recommendations, three workstreams, three phases), the bullets in each column are within ±2 words of each other across parallel items — i.e., bullet 1 in column A is 12 words, bullet 1 in column B is 13 words, bullet 1 in column C is 11 words. This is the LLM's parallel-structure tic; real writing has variable density. | Three recommendation cards, each with a ~13-word "Why It Works" and a ~11-word "What It Delivers" bullet |
| S-C08 | Devil's-advocate fail | Slide could be removed without weakening the deck (orphan, doesn't advance argument) | Mid-deck slide restating what's already in exec summary |
| S-C09 | Redundant callout | Sidebar or "Key Takeaways" block restates what's already on the slide | "Key Takeaway" sidebar reading back the action title |
| S-C10 | Generic next-steps | Proposal slide asks generic questions ("What's your X?", "How can we help?") rather than naming specific workstreams with deliverables | "Discuss how we can help you grow" |
| S-C11 | Two takeaways fighting on one slide | Slide tries to make two distinct arguments, dilutes both | One slide arguing both "market is growing" and "competitor is weak" |
| S-C12 | Title-flow breaks | Reading only the titles in order, one title presupposes body content the reader hasn't seen | Title says "Therefore X" with no prior title establishing premise |
| S-C13 | Visual unification fail | Slide has 4+ independent blocks (chart + KPI row + text cards + callout) not tied by explicit structure (arrow, numbered flow, grid alignment, equation) | Bar chart plus unrelated strip of 5 big-number KPIs at the bottom |
| S-C14 | Letterbox bleed | PDF exported at Letter/A4 landscape with visible empty bands top and bottom across 3+ body slides (sign of Print-to-PDF with paper default) | Consistent ~0.5" empty bands on body slides |
| S-C15 | Body contains material not serving title | Golden Rule violation in the reverse direction: body elements (KPIs, bullets, a second chart, an extra callout) make a point the title does not claim. If a reader took the title as the slide's thesis, some body element would feel unrelated or like a tangent. | Title: "Americas comp is -1% after new-store adjustment"; body has a KPI card on "Mexico gross margin" that is not referenced anywhere else on the slide |

### Tier 1 — polish miss

| ID | Name | Signal | Example |
|---|---|---|---|
| S-D01 | Broken internal reference | Slide refers to "see Appendix B" or "slide 7" that doesn't exist | "See Appendix B" with no Appendix B |
| S-D02 | One title could be sharper | Single topic-label or soft-action title in an otherwise strong deck | One "Market Overview" title amid 7 strong action titles |

---

## Insight patterns

*Does the deck push past observation into non-obvious, actionable insight?*

Note: The pressure-test check runs as a separate structured analysis in SKILL.md step 4b. Its result (HOLDS UP / PARTIAL / UNADDRESSED / WEAK) informs the rubric descriptor match but is not a pattern in this catalog.

### Tier 2 — visible professional flaw

| ID | Name | Signal | Example |
|---|---|---|---|
| I-C01 | "So what" missing on analytical slide | Slide states a fact without pushing to implication for the decision | "US revenue grew 12%" with no connection to the recommendation |
| I-C02 | Unaddressed strongest counterargument | The obvious skeptic objection at the target company isn't acknowledged anywhere (no assumptions stated, no alternative tested) | Recommending a playbook without falsifying the tailwind alternative |
| I-C03 | Vague quantifier without number | Title or callout uses "significant", "substantial", "major", "considerable", "meaningful" without the actual number | "Significant revenue opportunity in SMB" with no $ figure |
| I-C04 | Surface-level analysis presented as insight | Uses easily available facts (recent headlines, standard 10-K summary) without original synthesis on top | Deck title is "Apple is facing iPhone saturation" sourced only from news articles |

---

## Evidence patterns

*Is every claim backed by traceable, on-slide sourcing in the right format?*

### Tier 3 — client-embarrassing

| ID | Name | Signal | Example |
|---|---|---|---|
| E-B01 | Chart math doesn't tie | Parts exceed stated whole, percentages don't sum, bars visually overshoot the total | Agency bars exceed the $750M total they're supposed to disaggregate |
| E-B02 | Chart title's claim doesn't match chart data | Title asserts a magnitude or direction the chart doesn't show | Title says "2x", chart shows 1.8x; title says "cheaper", chart shows parity |
| E-B03 | Cross-slide numerical inconsistency | Same metric shows different values on different slides | Slide 4 shows +$373M, slide 9 model shows max $259M |
| E-B04 | Magnitude insanity | Quantitative claim implausible for the company or industry | TAM claim 10x reality |
| E-B05 | Temporal validity failure | "Current" data actually outdated, or recommended move already executed by the company | Recommending an acquisition the company closed 6 months ago |
| E-B06 | Fabricated-looking source | Source names a document that can't plausibly exist (internal model cited as external, made-up report number, generic uncheckable phrasing like "proprietary analysis" without assumptions shown) | "Source: [Company] Q2FY26 Internal Financial Positioning" with no such doc |

### Tier 2 — visible professional flaw

| ID | Name | Signal | Example |
|---|---|---|---|
| E-C01 | Format-matches-content violation | Quantitative trend or multi-variable comparison presented as text cards or big-number callouts instead of chart or table | Margin improvement trend shown as 4 KPI cards with no chart |
| E-C02 | Missing assumption statement | Derived or estimated figure (TAM, revenue opportunity, savings) without the assumption chain shown | "$100M opportunity" with no derivation |
| E-C03 | Vague source | Source incomplete: "Statista" without dataset, news outlet without article title, "industry reports" without naming them, "company website" without page | "Source: Statista" on a market-share claim |
| E-C04 | On-slide source missing | Slide makes numerical claim with no source line anywhere on slide (even if appendix has sources) | Revenue chart on slide 4 with no "Source:" footer |

### Tier 1 — polish miss

| ID | Name | Signal | Example |
|---|---|---|---|
| E-D01 | Appendix bibliography incomplete | Appendix sources page present but missing report titles, dates, or URLs on one or more entries | Bibliography lists "Statista data" with no dataset name or date |
| E-D02 | Single vague source | One source on one slide is vague while others are named | Slide 5 cites "industry reports"; other slides all named |
| E-D03 | Source line format varies | Source lines use different templates across slides (some with page, some without; some italic, some not) | "Source: 10-K p. 34" on slide 3; "10-K (2024)" on slide 5 |

---

## Slide Design patterns

*Would a busy exec actually read this?*

### Tier 3 — client-embarrassing

| ID | Name | Signal | Example |
|---|---|---|---|
| D-B01 | Edge clipping / text overflow | Slide text or visual element extends past slide boundary and is cut off in the PDF | "Strip out new stores and the Mexico acquisition, and Am" cuts off mid-word |
| D-B02 | Placeholder text left in | "TK", "[insert X]", "Lorem ipsum", "[client name]", template sample text | "[Insert company logo here]" on title slide |

### Tier 2 — visible professional flaw

| ID | Name | Signal | Example |
|---|---|---|---|
| D-C01 | Uniform high density across deck | Every core slide at similar heavy density (headline + subhead + 3 content blocks + KPI row); no breathing slides | 6 slides in a row each with 4-6 KPI cards |
| D-C02 | Low visual variety | Fewer than 50% of core slides carry a genuine visual device (chart, table, diagram, icon framework); rest are text-only | 6 core slides: 2 charts, 4 text-and-KPI-card pages |
| D-C03 | Focal-point fail | No visual hierarchy on slide, eye darts around, equally-weighted blocks, no dominant visual | Wall of 12 equally-sized bullets |
| D-C04 | Inconsistent semantic color | Same color means different things across slides, or color appears without legend or convention | Green = positive on slide 3, green = competitor on slide 5 |
| D-C05 | Text-heavy body slide | Core slide exceeds ~250 words without a chart, table, or framework clearly carrying the message (slide above 500 words is a design problem regardless) | Core slide with 350 words and no visual |
| D-C05a | Deck-average word density high | Average words-per-core-slide exceeds ~180, or maximum single core-slide word count exceeds ~250. Calculate for the deck as a whole: sum of words on core slides / number of core slides. At 180+ average, the reader is being asked to read, not scan. At 250+ on any single slide, the slide is too dense regardless of composition. Client-ready consulting decks average ~80-140 words per core slide. | Deck of 8 core slides averaging 210 words each, peak slide 320 words |
| D-C06 | Color without meaning | Color applied decoratively rather than semantically. Test: pick a colored element (a number in red, a highlighted box, a colored bullet). Ask "what does this color mean here, and is the meaning consistent across the deck?" If the answer is "it just looks nice" or "the color's meaning changes slide to slide", fires. Includes: numbers colored differently for visual variety rather than to signal positive/negative/emphasis, 4+ colors used on one slide without a legend, gradient fills used purely decoratively, brand-palette colors applied inconsistently across semantically equivalent elements. Related to but distinct from D-C04 (D-C04 is inconsistent *semantics*; D-C06 is *no* semantics). | Revenue number in red on slide 3 (meaning: negative), revenue number in red on slide 5 (meaning: highlight), revenue number in blue on slide 7 (meaning: highlight) |

### Tier 1 — polish miss

| ID | Name | Signal | Example |
|---|---|---|---|
| D-D01 | Intra-element whitespace imbalance | Content inside a card unbalanced: headline at top, paragraph at bottom, large empty middle (or vice versa); looks unfinished | Three-card layout with text crammed at bottom and ~40% empty space in middle |
| D-D02 | Alignment drift | Elements not aligned to consistent grid; left edges vary by a few pixels without reason | Three headers starting at slightly different x-positions |
| D-D03 | Font family inconsistency | Mixed font families across slides without systematic reason | Slide 3 uses Arial, slide 4 uses Calibri |
| D-D04 | Inconsistent title casing | Some titles Title Case, others Sentence case, others ALL CAPS, without system | Slide 2: "Market Share Growth"; slide 3: "competitors are losing share" |
| D-D05 | Inconsistent bullet punctuation | Some bullets end with period, some don't, within same slide or deck | Mixed terminal periods in a list |
| D-D06 | Inconsistent number formatting | "$1.3B" on one slide, "$1,300M" on another, "1.3 billion" on a third | Revenue figure formatted three different ways across the deck |
| D-D07 | Page number or footer missing on some slides | Footer present on most slides but missing on one or two | Slide 4 has no footer, rest do |
| D-D08 | Stock photo that doesn't add meaning | Decorative image (skyline, handshake, laptop) used as filler | Generic "business handshake" photo on recommendations slide |
| D-D09 | Chart missing title or takeaway | Chart has no title caption, or has descriptive title but no "so what" takeaway | "Revenue by Segment" title with no "X segment drives 60%" note |
| D-D10 | Axis labels or units missing | Axis present but no label or units | Y-axis numbers with no "$M" or "%" indicator |
| D-D11 | Legend missing or unclear | Multi-series chart with no legend, or legend uses unclear labels | Two-line chart with "Series 1" and "Series 2" labels |
| D-D12 | Inconsistent data labels | Some bars labeled with values, others not, within same chart | Bar chart with three of five bars value-labeled |
| D-D13 | Truncated or rotated axis labels | Axis labels cut off, rotated 90° to fit, or overlapping | X-axis category labels rotated vertically and overflowing |
| D-D14 | Single rough slide amid polish | One slide markedly less polished than the rest (different template, misaligned, rushed) | Slide 8 bare bullet list while slides 1-7 and 9-12 are formatted cards |

---

## Not checked (explicit non-goals)

- "Suspected hallucination" or "likely fabricated" framing in student-facing output. Citation-plausibility issues are expressed developmentally: *"Source on slide X could not be verified; strengthening with a named report and date would raise Evidence."*
- Em dashes in student writing (not a deck-quality concern).
- "This looks AI-generated" framing. We catch specific LLM tells via S-C01 through S-C07, not vibes.
- Grading on the student's target company choice.
- Grading on whether the recommendation is "correct."
