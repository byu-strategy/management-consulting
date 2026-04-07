---
name: grade-deck
description: Grade a student slide deck PDF against the Capstone Deck Quality Rubric. Reads each slide as an image for design analysis and extracts text for content analysis. Outputs structured scores (1-7) across four dimensions with justifications.
user_invocable: true
---

# Grade Deck Skill

You are grading a student's slide deck for STRAT 325 (Intro to Management Consulting) at BYU. The student built an unsolicited proposal deck targeting a real public company. Your job is to apply the Deck Quality Rubric rigorously and produce a draft grade with specific justifications.

## Instructions

1. **Get the PDF path** from the user's argument. If no path is provided, ask for one.

2. **Read the rubric** from `00-assessments.qmd`. Search for the section starting with `#### Deck Quality Rubric {#deck-quality-rubric}` and read through the scoring formula and conversion table. This is your scoring standard.

3. **Read every page of the PDF as images.** Use the Read tool with the `pages` parameter, reading in batches of up to 20 pages. You MUST visually inspect every slide. For each slide, note:
   - The action title (or lack thereof)
   - What the slide body contains (charts, text, data, visuals)
   - Whether sources appear in footnotes
   - Visual quality (alignment, spacing, font consistency, white space, color usage)
   - Whether the slide advances the argument

4. **Check the two quality gates first** (these cap scores):
   - **Source Quality Gate**: Do all slides citing numbers have traceable sources on-slide? Is there an appendix sources page with full citations? Untraceable sourcing on key claims caps Evidence at 4.
   - **Client-Readiness Gate**: Any assignment artifacts ("P1," "P2," "STRAT 325," template section labels as titles)? Missing contact info? Missing/weak exec summary? Any of these cap Storyline at 4.

5. **Score each dimension 1-7** using the rubric descriptions exactly as written. Reference specific slides by number in your justifications.

6. **Calculate the final score** using the formula:
   > Deck Quality Score = (Storyline x 0.30 + Insight x 0.30 + Evidence x 0.25 + Design x 0.15) x 100 / 7

7. **Output the structured result** in the exact format shown below.

8. **Save the assessment to a file.** Write the full output to `grades/[student-name-or-company].md` (e.g., `grades/sato-adobe.md`). Use lowercase, hyphens for spaces. If the `grades/` directory doesn't exist, create it. This file is the student's feedback document.

## The Four Dimensions

| Dimension | Weight | What It Covers |
|-----------|--------|----------------|
| Storyline | 30% | SCR arc, action titles, exec summary, proposed next steps, deck tightness, client-readiness |
| Insight | 30% | Non-obvious "so what," pressure-testing, pushing past observation to actionable recommendation |
| Evidence | 25% | On-slide sourcing, data quality, format choices, assumptions, appendix bibliography |
| Slide Design | 15% | Squint test, consistency, white space, chart quality, professional formatting |

## Source Quality Guide

A **traceable source** names the specific document, database, or event so a reader could find and verify the claim.

**Good sources (traceable):**
- "Source: Apple 10-K (FY2025), p. 34"
- "Source: McKinsey Global Institute, 'The Future of Work' (2024)"
- "Source: Capital IQ; Crunchbase"
- "Source: Q3 2025 Earnings Call Transcript, CFO remarks"
- "Source: IBISWorld, US Coffee Shop Industry Report (Dec 2025)"
- "Source: Bureau of Labor Statistics, Current Employment Statistics (2024)"

**Bad sources (not traceable, triggers the gate):**
- "Source: Google" or "Source: Internet"
- "Source: Company website" (which page? which document?)
- "Source: News articles" or "Source: Various news sources"
- "Source: Statista" (without naming the specific dataset or report)
- "Source: Industry reports" (which reports? by whom? when?)
- "Source: Research" or "Source: Online research"
- "Source: AI research" or "Source: ChatGPT" or "Source: Claude"
- "Source: Analyst estimates" (which analyst? which firm?)
- "Source: Proprietary analysis" (without showing the assumptions)
- No source at all on a slide with numerical claims
- Sources listed only in appendix but not on the slide where the claim appears

The gate triggers when **key claims** use bad sources. A single passing mention of a round number without a footnote is minor. But if the core analytical claims lack traceable sources, cap Evidence at 4.

**Appendix bibliography**: The deck should include a sources page in the appendix with full citations (report titles, authors, dates, URLs where available). This is the verification layer. Missing bibliography is a weakness in Evidence scoring.

## Calibration Benchmarks

### McKinsey: European Tech IPO (reference scores)

- **Storyline: 7.** Clear SCR arc. Exec summary compresses five numbered claims, each proved by subsequent slides. Section numbering (1-5) creates clear narrative progression. Resolution dominates. Every title is a specific conclusion (quantified where content warrants). No proposal slide (thought leadership piece), but the deck's resolution section is effectively the recommendation.
- **Insight: 7.** Non-obvious analysis. Decomposes the IPO gap into volume vs. valuation drivers. Challenges the perception that EU IPOs underperform by showing outlier-driven averages. Quantifies economic loss at 439 USD bn and contextualizes as ~26% of DAX40 market cap.
- **Evidence: 7.** Every chart sourced to Capital IQ, FactSet, Crunchbase, Preqin, IMF, or World Bank. Specific numbers throughout. One minor "Web research" citation on a non-critical slide.
- **Slide Design: 7.** Consistent two-color palette. Clean charts. Generous white space. Navigation tabs maintain orientation. Passes squint test on every slide.

### BCG: Loose Dogs in Dallas (reference scores)

- **Storyline: 6.** Clear four-part structure (Context, Key Findings, Recommendations, Next Steps). Strong SCR arc. Some structural slides use labels ("Context," "Agenda") rather than conclusions. Next steps are specific and actionable.
- **Insight: 7.** Original primary research (BCG conducted their own dog census). Decomposes the problem using a memorable "buckets and flows" framework. Shows why single-point interventions fail through systems thinking.
- **Evidence: 7.** Extensive sourcing in detailed footnotes. Named sources throughout (DAS Chameleon database, AVMA, ASPCA, Census data). Quantified claims with explicit methodology notes.
- **Slide Design: 5.** Clean BCG template. Good conceptual diagrams. But some slides are text-heavy (Executive Findings page), and the agenda slides interrupt visual flow.

### Calibration guidance for student decks

- A **7** means the student's work on that dimension is at or near MBB quality. This is rare.
- A **6** means strong, professional-quality work with one minor issue.
- A **5** means good work with a couple of clear weaknesses.
- A **4** means adequate but unpolished, with noticeable gaps.
- A **3** means the student followed the structure but missed the substance.
- A **2** means significant problems across the dimension.
- A **1** means the dimension is essentially absent.

Most student decks will cluster in the 3-5 range. Be honest but fair. Justify every score with specific slide references.

## Output Format

Always output results in this exact format:

```
# Deck Quality Assessment

**Student:** [filename or student name]
**Company:** [target company from the deck]
**Slides:** [number of main slides, excluding title/appendix]

## Quality Gates

- [ ] Source Quality Gate: [PASS / TRIGGERED -- list specific slides with unsourced claims. If triggered, caps Evidence at 4.]
- [ ] Client-Readiness Gate: [PASS / TRIGGERED -- list specific instances (artifacts, missing contact info, weak/missing exec summary). If triggered, caps Storyline at 4.]

## Scores

### 1. Storyline: [X]/7 (weight: 30%)

**SCR Arc & Structure:** [2-3 sentences on the narrative arc, section proportions, deck tightness]

**Action Titles:**
- Slide 1: "[exact title]"
- Slide 2: "[exact title]"
- [... all slides]

[Does reading these titles alone tell the story? 1-2 sentences.]

**Executive Summary:** [1-2 sentences. Does it compress the full argument? Could a reader skip the body and understand the recommendation?]

**Proposed Next Steps:** [1-2 sentences. Are they specific, earned by the analysis? Or generic questions?]

### 2. Insight: [X]/7 (weight: 30%)

[3-4 sentences. Is the analysis non-obvious? Does it push past observation? Would someone at the company learn something? Are conclusions pressure-tested?]

### 3. Evidence: [X]/7 (weight: 25%)

[3-4 sentences. Are claims sourced on-slide? Traceable? Internally consistent? Right format for the content? Is there an appendix bibliography?]

### 4. Slide Design: [X]/7 (weight: 15%)

[2-3 sentences based on visual inspection. Squint test, consistency, white space, chart quality.]

## Calculation

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Storyline | X | 0.30 | X.XX |
| Insight | X | 0.30 | X.XX |
| Evidence | X | 0.25 | X.XX |
| Design | X | 0.15 | X.XX |
| **Weighted Avg** | | | **X.XX** |

**Deck Quality Score: XX.X / 100**

## Key Feedback

**Strongest dimension:** [which and why, 1 sentence]

**Biggest opportunity:** [which dimension and specific, actionable advice, 2-3 sentences]
```

## Important Notes

- This is a DRAFT grade. The professor will review and adjust.
- Be specific. "Good analysis" is not helpful. "Slide 4 cites McKinsey Global Institute 2024 report by name" is helpful.
- Storyline is now a broad dimension. Evaluate ALL of: SCR arc, action titles (list them all), exec summary quality, proposed next steps quality, deck tightness, and client-readiness. A deck with great structure but all label titles can't score above a 5. A deck with great titles but a weak proposal can't score above a 5.
- When grading proposed next steps (within Storyline), remember: students should be proposing specific workstreams, not asking generic questions. Penalize "What's your growth strategy?" Reward "Map POS walkaway data against staffing levels."
- Do not inflate grades. A student deck that follows the template competently but without non-obvious insight is a 3-4 on Insight, not a 5-6.
- Check both gates FIRST. Gates cap the relevant dimension at 4 regardless of other quality.
- Evidence now includes format choices (charts vs. text), appendix bibliography quality, and assumption transparency, not just whether sources exist.
