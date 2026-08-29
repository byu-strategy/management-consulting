# Slide Atoms — Reference (v3)

A taxonomy of 29 atomic elements that compose consulting slide decks. Derived empirically from atomizing 11 decks / ~160 slides (5 professional: McKinsey ×2, BCG ×2, Bain; 6 student) in distinct visual styles.

Use this as the **output schema** for parsing slide decks and as the **target language** for grading patterns. Every content block on a slide should label as one of the 29 atoms.

---

## How to use

**When parsing a slide**, walk each visual block and tag it with one atom name. A single slide is a *composition* of atoms, not a single atom. A slide's role ("executive summary slide", "section divider") is a recognizable composition of atoms, not an atom itself.

**When writing grading patterns**, target atoms by name. Patterns like "does every chart have a caption?" map onto atoms 13-17 (chart primitives) and atom 24 (chart caption). Atom-level targeting makes patterns deterministic and testable in isolation.

**When an element seems not to fit**, check first for a composition of existing atoms. New atoms should only be added after 3+ sightings across 2+ decks.

---

## The 29 atoms

### A. Frame atoms (page-level furniture)

**1. Title** — the primary slide headline. Variants:
- *Action title*: commits to a claim (e.g., "From 2015 to 2023, IPOs in the US raised ~340 billion USD more than those in Europe")
- *Topic label*: bare label (e.g., "Conclusion", "Executive Summary")

Content quality (action vs topic) is a grading dimension; structurally it's one atom. Styling variants seen: title-in-banner, title with colored left accent bar, title with kicker fused on the same line ("Executive Summary: [action]").

**Grading hooks:** action-vs-topic classifier; Golden-Rule check (body supports title); title-body mismatch detection.

---

**2. Kicker** — small label positioned *above* the title or fused into the title line. Forms:
- Section number prefix ("1.", "2.", "5.")
- Typographic tag in small caps ("EXECUTIVE SUMMARY", "WHAT I NOTICED", "APPENDIX", "THE OPPORTUNITY | 1 OF 3")
- Section/phase banner ("So What?", "Key Findings", "Context")
- Numbered side-badge (BCG-style "1.1", "1.2", "1.3" in a colored rectangular badge on the left edge)

**Grading hooks:** count of kickers across deck as AI-scaffolding saturation signal; kicker recurrence as template-saturation tell.

---

**3. Title divider rule** — horizontal line directly under the title separating it from body. Optional; some firms (McKinsey) use whitespace instead.

**Grading hooks:** consistency across deck; absence/presence as house-style indicator.

---

**4. Source line** — footer citation. One line, small font, bottom-left or bottom-center. Examples: "Source: Capital IQ", "Source: Lululemon Form 10-K (FY2024), Item 7 (MD&A)".

**Grading hooks:** Source Quality Gate (every analytical slide has a source line); source-specificity check ("Web research" vs "Capital IQ; Crunchbase"); source-per-quantitative-claim binding.

---

**5. Footnote** — numbered clarification keyed to a superscript in the body, chart, or table. Usually between source line and page number, small font. "1. EU27, UK, Switzerland, and Norway".

**Grading hooks:** footnote-but-no-citation fallback flag; methodology-footnote-for-extrapolation check.

---

**6. Page number** — single numeric figure, almost always bottom-right. Some decks skip on title/closing slides.

**Grading hooks:** consecutive integrity (no skipped numbers); duplicate detection.

---

**7. Brand mark** — recurring logo, wordmark, or color stripe. Variants:
- Corner logo ("McKinsey & Company" bottom-right on every page)
- Edge stripe (vertical "Uber" wordmark up the left edge)
- Top color bar with page number inside (halle-benson)
- Filename stamp (BCG "20160826_Council_Deck.pptx" bottom-left)
- Left/right color accent stripe (carter-johansen, andres-arroyo)

**Grading hooks:** consistency check; course-artifact detection ("STRAT 325" in footer triggers Client-Readiness Gate).

---

**8. Metadata block** — title-slide-only cluster: authors/team, organization, date, contact info, optional confidentiality notice. Not decomposable further.

**Grading hooks:** presence check on title slide; Client-Readiness Gate signals (missing contact info, course labels in metadata).

---

### B. Text blocks

**9. Paragraph** — unstructured prose block, no bullets.

**Grading hooks:** density check (words per paragraph, lines); formatting consistency.

---

**10. Bulleted list** — vertical list with hanging-indent bullets. Styling variants: numbered (1, 2, 3), lettered (A, B, C), numbered-circle-badge markers, typographic arrows (↗, ▶) as markers.

**Grading hooks:** list parallelism (each item structurally similar); list length discipline (3-5 items ideal); lists-of-exactly-3 recurrence as AI-template tell.

---

**11. Sidebar panel** — right-column or secondary text panel paired with a main visual. Near-universal on analytical slides. Canonical forms:
- McKinsey "Key findings" / "Further insights"
- Uber "Key Implications"
- Lululemon "THE REAL STORY" / "THE MATH" (red-bordered)
- halle-benson "What it means" / "What I'm proposing" (colored-header variants)
- Bain "KEY HIGHLIGHTS" / "KEY DRIVERS"
- carter-johansen green-/dark-header PFOF/NII panels
- larson red "Proposal" solid-bg panel

Structurally a (header + bulleted list or short paragraphs) unit glued to a chart. Fires universal grading patterns.

**Grading hooks:** sidebar-parallelism-across-slides; bullet-count consistency; header-label discipline; presence on every analytical slide.

---

**12. Stat block** — oversized numeric figure with a smaller descriptor label, treated as a standalone content unit. Examples: "47% / of newly created jobs are generated by start-ups", "+41% / China Mainland revenue", "$10,000 in discounts". Fires on ~2/3 of decks as a dominant content primitive.

**Distinct from annotation callout (27):** stat block is a *content primitive* that stands alone; annotation callout overlays or points to a chart element.

**Grading hooks:** stat-has-unit check; stat-has-source check; stat-block-row parallelism.

---

**13. Pull quote / testimonial** — short verbatim quotation from an external speaker (industry expert, customer, survey respondent, analyst, client), rendered in italics, followed by a named-role attribution. Often decorated with a quotation-mark glyph or speech-bubble icon.

Examples: "Though China leads in granted patents, translating into commercial value still has room to improve." — Leading Biotech Chairman (McKinsey). "We are intentionally slowing down the expansion..." — PR Director, Luxury brand (Bain).

**Distinct from paragraph (9):** pull quote has explicit external attribution; paragraph is deck-author prose.
**Distinct from annotation callout (27):** annotation points to a chart; pull quote is standalone evidence.
**Distinct from sidebar (11):** a pull quote can live inside a sidebar, but it's its own content type.

**Grading hooks:** verifiable source (named role, named org); load-bearing vs decorative; length discipline (2 sentences max); attribution-format parallelism across deck.

---

### C. Chart primitives

**14. Bar / column chart** — vertical or horizontal, single-series, grouped, stacked, or 100%-stacked. Variants include marimekko/mosaic (variable-width columns × 100%-stacked heights). The most universal chart type.

**Grading hooks:** has-caption check; axis-labels check; data-label discipline; highlighted-bar-has-meaning check.

---

**15. Line / area chart** — including stacked area and cumulative. Variants: slope chart (2-point line showing before/after), combo chart (line overlaid on bars).

**Grading hooks:** endpoint-labeling; series-identifiability (legend or right-edge labels); trend-line-has-takeaway check.

---

**16. Waterfall / bridge chart** — numeric buildup or breakdown showing additive/subtractive components. McKinsey two-stage waterfalls, Lululemon revenue bridges, braden-fisher EBIT builds.

**Grading hooks:** arithmetic-ties check (components sum to endpoint); component-labeling; derivation traceability.

---

**17. Scatter / bubble chart** — 2D space with optional bubble size as third dimension, optional bubble color as fourth.

**Grading hooks:** axis-direction-convention (e.g., low/high orientation); bubble-size-encoding-disclosed; axis-rating-basis-shown.

---

**18. Map** — choropleth or geo-annotated.

**Grading hooks:** legend completeness; title-matches-map-claim (e.g., title says "35 states" but map shows "promising states").

---

### D. Non-chart visuals

**19. Harvey-balls matrix** — rows × columns grid where each cell is a partial-fill circle (or equivalent) encoding a qualitative score. Close cousin: any fixed-category visual-scoring grid.

**Grading hooks:** legend presence (favorable/neutral/unfavorable states); row-column parallelism; highlighted-column-has-meaning.

---

**20. Process / flow diagram** — any sequenced or system-level visual that is NOT a standard chart type. Covers:
- Process arrow / timeline (numbered steps with arrow connectors)
- Section menu (mini-TOC used as divider slide with current-section marker)
- Funnel (stacked rectangles of decreasing size)
- Custom conceptual diagram (BCG's bucket-and-flows; bucket metaphors; system visuals)
- Hub-and-spoke / wheel diagram (central node with radiating components)
- Arrow-header row (phase arrows above a table)
- Swimlane / Gantt visual
- Decomposition with operator glyphs (× or → connecting charts)

The most abstract atom — variant detection requires vision-model classification.

**Grading hooks:** step-count-matches-narrative; step-parallelism; decomposition-arithmetic-ties.

---

**21. Comparison panel** — two parallel columns with identical structure (same labels, same chart types, same stat positions) to contrast two entities. McKinsey EU-vs-US market structure, Lululemon Americas-vs-International, larson-brown old-paradigm-vs-new-paradigm.

**Grading hooks:** parallel-structure-check (both columns structurally identical); axis-consistency; narrative-symmetry.

---

**22. N-card grid** — 2 to 4 cards (in a row or 2D grid) with identical structure. Each card optionally contains {icon, heading, body, sub-label, stat, photo background}. Examples: Uber 3-cards with icons and green-highlighted body; halle-benson 4 numbered cards (01/02/03/04); Collin Powell 3 recommendation cards with "Output:" sub-labels; BCG 2×4 news thumbnail grid (2D arrangement).

Orientation variants: horizontal (most common), vertical-stacked row-list, 2D grid.

**Grading hooks:** card-parallelism-check (three cards with identical sub-labels = template saturation); card-body-length-variance; icon-semantic-consistency; exact-three-recurrence-across-deck.

---

**23. Data table** — rectangular row/column grid with cells that can hold text, bullets, numbers, or nested elements. Header row often colored. Variants: color-coded cells (red/green/yellow for categorical), logos in cells (Bain brand-ranking tables), photos as row headers.

**Grading hooks:** header-row-consistency; arithmetic-ties; cell-color-has-meaning; multi-level-header-structure.

---

### E. Chart decorations (overlays on any chart)

**24. Chart caption & unit label** — text block above or adjacent to the chart describing what is being shown and the units. "Total capital raised through IPOs (tech & non-tech), in USD bn"; "Venture capital historically shows attractive long-term returns". Often serves as a mini sub-title above the chart.

**Grading hooks:** presence check (every chart has one); unit-disclosure check; caption-matches-chart-data.

---

**25. Axis & data labels** — axis titles, category/tick labels, value labels on or next to bars/points. Includes sample-size indicators ("(7)(9)(10)(32)..." ellipses under x-axis); CAGR annotations at series-endpoints.

**Grading hooks:** axis-title-has-unit; data-label-completeness; scale-reasonableness.

---

**26. Legend** — color-swatch-plus-category-name bar. Usually at top or bottom of chart. Can also label a grid of icons (Harvey-balls legend) or map (color swatches for regions).

**Grading hooks:** legend-required-for-multi-series; legend-position-consistency-across-deck.

---

**27. Annotation callout** — overlay on or near a chart carrying emphasis. Absorbs many visual variants:
- Multiplier / delta label with bracket or arrow ("11.6x", "+340", "+154%", "x2", "8x")
- Floating stat label with curved arrow ("$300-400 billion estimated future value", "10X fewer accidents")
- Dark-rounded-rectangle banner ("AV safety has markedly improved", "Costs", "HARD DEADLINE")
- Brace with label ("Weighted average: -5%", "CAGR since 2011")
- Methodology box or alert callout (McKinsey S9 outlier caveat)
- Illustrative/exemplary tag ("EXEMPLARY", "ILLUSTRATIVE")
- Operator glyph connecting two charts (× between panels; → in decompositions)
- Starburst/explosion-shape badge (Bain "Top 3")
- Hand-drawn-style circle overlay on table values (Bain red marker circles)
- Colored-pill footer on a card
- Horizontal takeaway banner at bottom of slide ("The Ask:", "THE ASK", "HARD DEADLINE")

All behave as grading targets identically. The most versatile atom; any parser must be generous about what counts.

**Grading hooks:** chart-has-takeaway-check; annotation-color-consistency; over-hedging in annotation language ("could potentially", "may represent"); annotation-commits-to-claim.

---

**28. Tab / filter bar** — pill-style selector row above a chart, usually highlighting the "active" selection. Dashboard-style navigation. McKinsey IPO deck S5-S10 all have "Tech IPOs | All IPOs" and "Capital raised | Market cap" tab pairs.

**Grading hooks:** Dashboard-residue gate — a static PDF with tabs that don't do anything is semantically confused (tabs imply interactivity; PDF doesn't have it).

---

### F. Decorations

**29. Icon** — small symbolic glyph. Variants:
- Semantic (handshake for partnership, gavel for regulation, coin stack for savings, building for government, flag for country)
- Decorative (shapes, dots, abstract marks)
- Wayfinding (chevrons, arrows between panels)
- Logo/wordmark (brand or publisher)

**Grading hooks:** semantic-vs-decorative check; icon-consistency across slides; icon-style-consistency (all line-icons vs mixed).

---

### G. Images

**30. Image / photo** — photographic or illustrative image used as a content or brand element. Variants:
- Hero photo (title slide, braden-fisher Nike shoe)
- Product shot (Bain watch + handbag thumbnails)
- Scene photo (BCG case-example thumbnails for French Energy, US Healthcare, etc.)
- Mood image / abstract decorative graphic (McKinsey title rays, molecule renders)
- Photo-backgrounded card (McKinsey 3-question preview with photo backgrounds)
- Full-bleed section divider (McKinsey "Section 1" with photo background)
- Full-height agenda image (Bain agenda with handbag photo)
- News-article thumbnail (BCG 2×4 news grid)
- Brand logo rendered as chart data (Bain marimekko cells in brand typography)

**Grading hooks:** image-relevance-to-point; image-earns-its-space; photo-consistency (mood/era/treatment) across deck.

---

## Atom-selection decision tree

When uncertain which atom applies, walk down this tree:

```
Is it text or visual?
├── Text
│   ├── Is it a headline? → Title (1) or Kicker (2) by position
│   ├── Is it a citation footer? → Source (4) or Footnote (5) by numbering
│   ├── Is it oversized numeric + short label? → Stat block (12)
│   ├── Is it attributed to an external speaker? → Pull quote (13)
│   ├── Is it a right-column panel with header + bullets? → Sidebar (11)
│   ├── Are bullets indented with markers? → Bulleted list (10)
│   └── Else → Paragraph (9)
│
├── Visual — data viz
│   ├── Bars/columns → Bar chart (14)
│   ├── Lines/areas → Line chart (15)
│   ├── Additive/subtractive buildup → Waterfall (16)
│   ├── 2D scatter (optional bubble) → Scatter/bubble (17)
│   ├── Geographic → Map (18)
│   └── Grid of partial-fill circles → Harvey-balls (19)
│
├── Visual — non-chart structure
│   ├── Sequenced steps / system diagram → Process/flow (20)
│   ├── Two parallel columns → Comparison panel (21)
│   ├── 2-4 equal cards → N-card grid (22)
│   └── Row/column grid of cells → Data table (23)
│
├── Visual — chart overlay
│   ├── Describes what chart shows → Chart caption (24)
│   ├── Axis titles / data labels → Axis & data labels (25)
│   ├── Color swatches + category names → Legend (26)
│   ├── Pill-style selector → Tab/filter bar (28)
│   └── Emphasis text/graphic pointing at chart element → Annotation callout (27)
│
└── Visual — decoration
    ├── Small symbolic glyph → Icon (29)
    └── Photographic or illustrative image → Image/photo (30)
```

Frame atoms (3. title divider, 6. page number, 7. brand mark, 8. metadata block) are typically detected by position and are not in the tree.

---

## Output schema example

A parser should emit slide content as labeled elements. Suggested format using anchor-tag IDs with type attributes:

```
<a id="ab12cd34" type="kicker">EXECUTIVE SUMMARY</a>
ADC has revolutionized content creation and erased the complexity moat

<a id="ef56gh78" type="title" action="true">
The highest-return move is to institutionalize UO's full-price playbook
</a>

<a id="ij9012kl" type="title-divider"/>

<a id="mn34op56" type="paragraph">
The right response is not a broad promotional push. It is a tighter operating system...
</a>

<a id="qr78st90" type="n-card-grid" count="3">
  <card index="1" accent-color="red">
    <a type="stat-block">47%</a>
    <a type="paragraph">US apparel shoppers waiting for sales</a>
  </card>
  <card index="2" accent-color="purple">...</card>
  <card index="3" accent-color="red">...</card>
</a>

<a id="uv12wx34" type="sidebar" style="red-bordered" placement="right">
  <a type="kicker">THE MARGIN SIGNAL MATTERS</a>
  <a type="paragraph">In Q4 FY26, URBN's gross-profit rate improved 101 bps...</a>
</a>

<a id="yz56ab78" type="annotation-callout" style="dark-banner" placement="bottom">
SO WHAT: the enterprise narrative of "global momentum" obscures a stalling core
</a>

<a id="cd90ef12" type="source">
Source: Lululemon Form 10-K (FY2024), Item 7 (MD&A) Segment Results
</a>

<a id="gh34ij56" type="brand-mark" variant="footer">Lululemon Intelligence Brief | G. Gould</a>
<a id="kl78mn90" type="page-number">1</a>
```

Composite elements (N-card grid, sidebar, data table, comparison panel) carry children. Frame atoms are flat.

---

## Cross-atom grading patterns

Some patterns operate across multiple atoms:

- **Client-readiness gate**: course artifacts in title (1) or metadata (8) or missing exec-summary composition → caps Storyline score
- **AI-scaffolding saturation**: kicker recurrence (2) + exactly-3 cards (22) + identical-sub-label cards (22) + over-polished paragraph rhythm (9) → signals LLM first-draft
- **Source Quality gate**: any quantitative claim (12, 14-17 data labels) without a matching source (4) → caps Evidence score
- **Dashboard-residue flag**: tab/filter bar (28) on static PDF
- **Deck density check**: aggregate word count across all paragraph (9), bulleted list (10), sidebar (11) atoms per slide, averaged across core slides

---

## Coverage confidence

Empirically validated against 11 decks:
- **Universal atoms (10-11/11)**: title, metadata block, sidebar, bar chart, chart caption, axis/data labels, brand mark, page number, source line
- **Very common (7-9/11)**: kicker, footnote, bulleted list, paragraph, legend, annotation callout, N-card grid, data table, process/flow diagram, image/photo, icon
- **Common (4-6/11)**: stat block, title divider, line/area chart, comparison panel
- **Rare (1-3/11)**: waterfall, pull quote, scatter/bubble, map, Harvey-balls, tab/filter bar

Rare atoms still earn their place — each triggers specific grading patterns that don't apply to other atoms. Absence on a given deck just means "this atom's patterns don't fire here," not "atom is wrong."

---

## Candidates for v4

Not yet promoted (seen 0-2 times in 11 decks; promote on 3rd sighting):
- **Screenshot / UI capture** — expected in digital/SaaS cases (not tested yet)
- **Org chart / tree diagram** — common in consulting but not seen in these 11
- **Quadrant matrix / 2×2** — seen in passing once (strategic positioning)
- **Venn diagram** — not seen in 11 decks