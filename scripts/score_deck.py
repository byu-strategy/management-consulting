#!/usr/bin/env python3
"""
score_deck.py — deterministic scorer for deck.json artifacts (schema 1.1).

Usage:
    python3 scripts/score_deck.py grading-artifacts/<deck-id>/deck.json \
        --rubric rubrics/deck-quality-rubric.yaml \
        --out grading-artifacts/<deck-id>/scoring.json

Contract:
    Pure function from (deck.json, rubric.yaml) -> scoring.json.
    Same inputs produce same outputs. No network, no vision, no randomness.

Architecture:
    - Each pattern/gate is a pure Python function pattern_<id>() or gate_<id>().
    - Pattern functions take the deck dict and return a list of Finding objects.
    - Tier anchors, hurdles, gate caps applied in score_dimension().
    - Output is a dict serialized to JSON with full audit trail.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable
import yaml


CHART_TYPES = {"bar-chart", "line-chart", "waterfall", "scatter-bubble", "map", "process-flow"}
# process-flow only carries chart-like signals when variant is a composite/donut or timeline;
# we defer to atom-level flags where possible.


# =============================================================================
# Data classes
# =============================================================================

@dataclass
class Finding:
    pattern_id: str
    dimension: str       # "storyline" | "insight" | "evidence" | "design"
    tier: int            # 1 | 2 | 3
    slides: list[int]
    evidence: str
    student_name: str = ""    # filled by orchestrator from rubric


@dataclass
class GateResult:
    gate_id: str
    name: str
    fires: bool
    dimension: str
    cap: int
    also_drops: str | None = None
    evidence: str = ""


@dataclass
class DimensionScore:
    dimension: str
    findings: list[Finding]
    t1_count: int
    t2_count: int
    t3_count: int
    provisional: int                  # from tier anchors
    after_hurdles: int                # after level-7 / level-6 checks
    hurdle_notes: list[str]
    after_gates: int                  # after gate caps
    final: int
    weight: float
    weighted: float


# =============================================================================
# Helpers to walk the JSON
# =============================================================================

def slides(deck: dict) -> list[dict]:
    return deck["slides"]

def features(deck: dict) -> dict:
    return deck["deck"]["features"]

def obs(deck: dict) -> dict:
    return deck["deck"]["observations"]

def coherence(deck: dict) -> dict:
    return deck["deck"]["observations"]["coherence"]

def core_slides(deck: dict) -> list[dict]:
    """Slides that advance the argument (analytical-body, recommendation)."""
    return [s for s in slides(deck) if s["role_guess"] in ("analytical-body", "recommendation")]

def atoms_of_type(slide: dict, t: str) -> list[dict]:
    return [a for a in slide.get("atoms", []) if a.get("type") == t]

def first_atom(slide: dict, t: str) -> dict | None:
    xs = atoms_of_type(slide, t)
    return xs[0] if xs else None

def all_atoms(deck: dict, t: str) -> list[tuple[int, dict]]:
    """(slide_index, atom) for atoms of given type across deck."""
    out = []
    for s in slides(deck):
        for a in atoms_of_type(s, t):
            out.append((s["index"], a))
    return out

def has_chart_atom(slide: dict) -> bool:
    return any(a.get("type") in ("bar-chart", "line-chart", "waterfall", "scatter-bubble", "map") for a in slide.get("atoms", []))

def chart_atoms(slide: dict) -> list[dict]:
    return [a for a in slide.get("atoms", []) if a.get("type") in ("bar-chart", "line-chart", "waterfall", "scatter-bubble", "map", "process-flow")]


# =============================================================================
# Pattern functions — STORYLINE
# =============================================================================

def pattern_s_b01(deck: dict) -> list[Finding]:
    findings = []
    for s in slides(deck):
        align = s["observations"].get("title_body_alignment")
        if align not in ("title_overreaches_body", "internal_contradiction"):
            continue
        if not has_chart_atom(s) and not chart_atoms(s):
            continue
        ev = s["observations"].get("title_body_mismatch_detail") or "Title's claim does not match the chart"
        findings.append(Finding("S-B01", "storyline", 3, [s["index"]], ev))
    return findings

def pattern_s_b02(deck: dict) -> list[Finding]:
    findings = []
    for s in slides(deck):
        t = first_atom(s, "title")
        if t and t.get("has_internal_contradiction"):
            findings.append(Finding("S-B02", "storyline", 3, [s["index"]], f'Title: "{t.get("text","")}"'))
    return findings

def pattern_s_c01(deck: dict) -> list[Finding]:
    hits = []
    for s in core_slides(deck):
        t = first_atom(s, "title")
        if t and t.get("action") is False:
            hits.append((s["index"], t.get("text", "")))
    if hits:
        ev = "; ".join(f'slide {i}: "{txt}"' for i, txt in hits)
        return [Finding("S-C01", "storyline", 2, [i for i, _ in hits], ev)]
    return []

def pattern_s_c02(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for g in atoms_of_type(s, "n-card-grid"):
            if g.get("card_headings_are_imperatives"):
                hits.append(s["index"])
    if hits:
        return [Finding("S-C02", "storyline", 2, hits, "Numbered cards use imperative-verb labels")]
    return []

def pattern_s_c03(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for k in atoms_of_type(s, "kicker"):
            if k.get("is_empty_container_label"):
                hits.append((s["index"], k.get("text", "")))
    if hits:
        ev = "; ".join(f'slide {i}: "{txt}"' for i, txt in hits)
        return [Finding("S-C03", "storyline", 2, sorted({i for i, _ in hits}), ev)]
    return []

def pattern_s_c04(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        t = first_atom(s, "title")
        if t and t.get("uses_move_as_noun"):
            hits.append(s["index"])
    if hits:
        return [Finding("S-C04", "storyline", 2, hits, "Title uses 'move' as a noun for a recommendation")]
    return []

def pattern_s_c05(deck: dict) -> list[Finding]:
    hits = []
    examples = []
    for s in slides(deck):
        ac = s["observations"].get("antithesis_constructions") or []
        if ac:
            hits.append(s["index"])
            examples.extend(f'slide {s["index"]}: "{x}"' for x in ac[:1])
    if hits:
        return [Finding("S-C05", "storyline", 2, hits, "; ".join(examples))]
    return []

def pattern_s_c06(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        t = first_atom(s, "title")
        if t and t.get("has_ai_explainer_parenthetical"):
            hits.append(s["index"])
    if hits:
        return [Finding("S-C06", "storyline", 2, hits, "Title contains an AI-explainer parenthetical")]
    return []

def pattern_s_c07(deck: dict) -> list[Finding]:
    hits = []
    examples = []
    for s in slides(deck):
        ef = s["observations"].get("empty_follow_on_sentences") or []
        if ef:
            hits.append(s["index"])
            for ex in ef[:1]:
                examples.append(f'slide {s["index"]}: "{ex.get("quote","")}"')
    if hits:
        return [Finding("S-C07", "storyline", 2, hits, "; ".join(examples))]
    return []

def pattern_s_c07a(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        sr = s["observations"].get("self_referential_phrases") or []
        if sr:
            hits.append(s["index"])
    if hits:
        return [Finding("S-C07a", "storyline", 2, hits, "Deck refers to other slides ('as noted on slide X')")]
    return []

def pattern_s_c07b(deck: dict) -> list[Finding]:
    # Fires if deck-level cross-slide parallelism detected, OR
    # a recommendation slide has identical card sub-labels.
    hits = []
    cross = obs(deck).get("parallel_card_structure_across_slides", {})
    if cross.get("detected"):
        hits.extend(cross.get("slides", []))
    for s in slides(deck):
        if s["role_guess"] in ("recommendation",):
            for g in atoms_of_type(s, "n-card-grid"):
                if g.get("sub_labels_identical_across_cards"):
                    hits.append(s["index"])
    hits = sorted(set(hits))
    if hits:
        return [Finding("S-C07b", "storyline", 2, hits, "Recommendation cards use identical sub-label skeleton")]
    return []

def pattern_s_c07c(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        if s["role_guess"] == "recommendation" and s.get("argument", {}).get("next_steps_reverse_map_to_findings"):
            hits.append(s["index"])
    if hits:
        return [Finding("S-C07c", "storyline", 2, hits, "Next-steps workstreams re-chew the deck's own findings")]
    return []

def pattern_s_c07d(deck: dict) -> list[Finding]:
    f = features(deck)
    if f.get("core_slide_count", 0) >= 5 and (f.get("title_length_std_dev") or 99) <= 2.0:
        return [Finding("S-C07d", "storyline", 2, [], f'Title word counts cluster tightly (std dev {f.get("title_length_std_dev")})')]
    return []

def pattern_s_c07e(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for g in atoms_of_type(s, "n-card-grid"):
            if g.get("card_count", 0) >= 3 and g.get("card_body_length_variance") == "low":
                hits.append(s["index"])
    if hits:
        return [Finding("S-C07e", "storyline", 2, hits, "Parallel-bullet lengths are uniform across cards")]
    return []

def pattern_s_c08(deck: dict) -> list[Finding]:
    cut = coherence(deck).get("cuttable_slides") or []
    if not cut:
        return []
    slides_ = [c["slide"] for c in cut]
    ev = "; ".join(f'slide {c["slide"]}: {c.get("reason","")}' for c in cut)
    return [Finding("S-C08", "storyline", 2, slides_, ev)]

def pattern_s_c09(deck: dict) -> list[Finding]:
    hits = [s["index"] for s in slides(deck) if s["observations"].get("takeaway_banner_restates_title")]
    if hits:
        return [Finding("S-C09", "storyline", 2, hits, "Takeaway banner restates the title")]
    return []

def pattern_s_c10(deck: dict) -> list[Finding]:
    spec = coherence(deck).get("recommendation", {}).get("specificity")
    if spec == "do-more-analysis":
        return [Finding("S-C10", "storyline", 2, [], "Recommendation is 'do more analysis' rather than a specific action")]
    return []

def pattern_s_c12(deck: dict) -> list[Finding]:
    weak = obs(deck).get("title_flow", {}).get("weak_links") or []
    if weak:
        ev = "; ".join(f'slide {w["slide"]}: {w.get("reason","")}' for w in weak)
        return [Finding("S-C12", "storyline", 2, [w["slide"] for w in weak], ev)]
    return []

def pattern_s_c13(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        u = s["observations"].get("unified_by_explicit_structure") or {}
        if u.get("is_unified") is False and u.get("content_block_count", 0) >= 4:
            hits.append(s["index"])
    if hits:
        return [Finding("S-C13", "storyline", 2, hits, "Slide has 4+ blocks without a unifying device")]
    return []

def pattern_s_c14(deck: dict) -> list[Finding]:
    if features(deck).get("has_letterbox_bleed"):
        return [Finding("S-C14", "storyline", 2, [], "Deck exported at paper page size; visible top/bottom empty bands")]
    return []

def pattern_s_c15(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        if s["observations"].get("title_body_alignment") == "body_has_material_not_serving_title":
            ev = s["observations"].get("title_body_mismatch_detail") or "Body contains material not serving the title"
            hits.append((s["index"], ev))
    if hits:
        return [Finding("S-C15", "storyline", 2, [i for i, _ in hits], "; ".join(f"slide {i}: {e}" for i, e in hits))]
    return []


# =============================================================================
# Pattern functions — INSIGHT
# =============================================================================

def pattern_i_c01(deck: dict) -> list[Finding]:
    hits = [s["index"] for s in core_slides(deck) if s.get("argument", {}).get("so_what_stated") is False]
    if hits:
        return [Finding("I-C01", "insight", 2, hits, "Analytical slide states a fact without pushing to implication")]
    return []

def pattern_i_c02(deck: dict) -> list[Finding]:
    pt = coherence(deck).get("pressure_test", {}).get("deck_anticipates_it")
    if pt in ("unaddressed", "weak"):
        detail = coherence(deck).get("pressure_test", {}).get("detail", "")
        return [Finding("I-C02", "insight", 2, [], f"Pressure-test: {pt}. {detail}")]
    return []

def pattern_i_c03(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        v = s["observations"].get("vague_quantifiers_without_number") or []
        if v:
            hits.append(s["index"])
    if hits:
        return [Finding("I-C03", "insight", 2, hits, "Vague quantifier used without a number")]
    return []

def pattern_i_c04(deck: dict) -> list[Finding]:
    if coherence(deck).get("non_obviousness", {}).get("pushes_past_observation_to_interpretation") is False:
        detail = coherence(deck).get("non_obviousness", {}).get("detail", "")
        return [Finding("I-C04", "insight", 2, [], f"Insight does not push past observation to interpretation. {detail}")]
    return []


# =============================================================================
# Pattern functions — EVIDENCE
# =============================================================================

def pattern_e_b01(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for a in chart_atoms(s):
            cm = a.get("chart_math") or {}
            if cm.get("ties") is False:
                hits.append((s["index"], cm.get("notes", "Chart math does not tie")))
    if hits:
        return [Finding("E-B01", "evidence", 3, [i for i, _ in hits], "; ".join(f"slide {i}: {n}" for i, n in hits))]
    return []

def pattern_e_b02(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        if not (has_chart_atom(s) or chart_atoms(s)):
            continue
        if s["observations"].get("title_body_alignment") in ("title_overreaches_body", "internal_contradiction"):
            ev = s["observations"].get("title_body_mismatch_detail") or "Title's claim does not match chart data"
            hits.append((s["index"], ev))
    if hits:
        return [Finding("E-B02", "evidence", 3, [i for i, _ in hits], "; ".join(f"slide {i}: {e}" for i, e in hits))]
    return []

def pattern_e_b03(deck: dict) -> list[Finding]:
    issues = coherence(deck).get("number_reconciliation_issues") or []
    if issues:
        ev = "; ".join(f'slides {it.get("slides",[])}: {it.get("issue","")}' for it in issues)
        all_slides = sorted({s for it in issues for s in it.get("slides", [])})
        return [Finding("E-B03", "evidence", 3, all_slides, ev)]
    return []

def pattern_e_b04(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for nc in s.get("argument", {}).get("numeric_claims", []) or []:
            if nc.get("plausible") is False:
                hits.append((s["index"], nc.get("claim", ""), nc.get("plausibility_note", "")))
    if hits:
        ev = "; ".join(f'slide {i}: "{c}" ({n})' for i, c, n in hits)
        return [Finding("E-B04", "evidence", 3, sorted({i for i, _, _ in hits}), ev)]
    return []

def pattern_e_b06(deck: dict) -> list[Finding]:
    # A slide has a quant claim AND a source whose source_type is "internal-self".
    hits = []
    for s in slides(deck):
        has_quant = bool(s.get("argument", {}).get("numeric_claims"))
        if not has_quant:
            continue
        src_atoms = atoms_of_type(s, "source-line")
        for src in src_atoms:
            for c in src.get("citations", []):
                if c.get("source_type") == "internal-self":
                    hits.append((s["index"], c.get("source_text", "")))
    if hits:
        ev = "; ".join(f'slide {i}: [{t}]' for i, t in hits)
        return [Finding("E-B06", "evidence", 3, sorted({i for i, _ in hits}), ev)]
    return []

def pattern_e_c02(deck: dict) -> list[Finding]:
    # Aggregate: 2+ numeric claims lacking shown derivation.
    missing = []
    for s in slides(deck):
        for nc in s.get("argument", {}).get("numeric_claims", []) or []:
            if nc.get("derivation_shown") is False:
                missing.append((s["index"], nc.get("claim", "")))
    if len(missing) >= 2:
        examples = "; ".join(f'slide {i}: "{c}"' for i, c in missing[:4])
        return [Finding("E-C02", "evidence", 2, sorted({i for i, _ in missing}), f"{len(missing)} numeric claims without shown derivation. Examples: {examples}")]
    return []

def pattern_e_c03(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for src in atoms_of_type(s, "source-line"):
            for c in src.get("citations", []):
                if c.get("is_specific") is False and c.get("source_type") != "internal-self":
                    hits.append((s["index"], c.get("source_text", "")))
    if hits:
        ev = "; ".join(f'slide {i}: "{t}"' for i, t in hits[:4])
        return [Finding("E-C03", "evidence", 2, sorted({i for i, _ in hits}), ev)]
    return []

def pattern_e_c04(deck: dict) -> list[Finding]:
    missing = features(deck).get("slides_missing_sources_with_quant_claims") or []
    if missing:
        return [Finding("E-C04", "evidence", 2, missing, "Quantitative claims without an on-slide source line")]
    return []

def pattern_e_d02(deck: dict) -> list[Finding]:
    # Single vague source (exactly one slide has a vague citation).
    vague_slides = set()
    for s in slides(deck):
        for src in atoms_of_type(s, "source-line"):
            for c in src.get("citations", []):
                if c.get("is_specific") is False and c.get("source_type") != "internal-self":
                    vague_slides.add(s["index"])
    if len(vague_slides) == 1:
        return [Finding("E-D02", "evidence", 1, sorted(vague_slides), "One slide has a vague source while others are named")]
    return []

def pattern_e_d03(deck: dict) -> list[Finding]:
    if (features(deck).get("source_line_format_variants") or 0) > 1:
        return [Finding("E-D03", "evidence", 1, [], "Source-line format varies across slides")]
    return []


# =============================================================================
# Pattern functions — DESIGN
# =============================================================================

def pattern_d_b01(deck: dict) -> list[Finding]:
    hits = [s["index"] for s in slides(deck) if s["observations"].get("has_edge_clipping")]
    if hits:
        return [Finding("D-B01", "design", 3, hits, "Text or visuals clipped at slide edge")]
    return []

def pattern_d_b02(deck: dict) -> list[Finding]:
    hits = [s["index"] for s in slides(deck) if s["observations"].get("has_placeholder_text")]
    if hits:
        return [Finding("D-B02", "design", 3, hits, "Placeholder text left in the deck")]
    return []

def pattern_d_c01(deck: dict) -> list[Finding]:
    f = features(deck)
    avg = f.get("avg_words_per_slide") or 0
    sd = f.get("word_count_std_dev")
    if avg >= 150 and sd is not None and sd <= 30:
        return [Finding("D-C01", "design", 2, [], f"Average density {avg:.0f} words/slide with low variance (std dev {sd:.0f})")]
    return []

def pattern_d_c02(deck: dict) -> list[Finding]:
    f = features(deck)
    core = f.get("core_slide_count") or 0
    withc = f.get("slides_with_charts") or 0
    if core > 0 and (withc / core) < 0.5:
        return [Finding("D-C02", "design", 2, [], f"Only {withc}/{core} core slides carry a chart or visual device")]
    return []

def pattern_d_c03(deck: dict) -> list[Finding]:
    hits = [s["index"] for s in core_slides(deck) if s["observations"].get("has_clear_focal_point") is False]
    if len(hits) >= 2:
        return [Finding("D-C03", "design", 2, hits, "Multiple slides have no dominant visual; eye darts across equally-weighted blocks")]
    return []

def pattern_d_c04(deck: dict) -> list[Finding]:
    issues = obs(deck).get("color_consistency", {}).get("issues") or []
    if issues:
        ev = "; ".join(f'{it.get("color","")} on slides {it.get("slides",[])}: {it.get("detail","")}' for it in issues)
        all_slides = sorted({s for it in issues for s in it.get("slides", [])})
        return [Finding("D-C04", "design", 2, all_slides, ev)]
    return []

def pattern_d_c05(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        if s["role_guess"] in ("title", "executive-summary", "bibliography"):
            continue
        if s["observations"].get("word_count", 0) > 250 and not (has_chart_atom(s) or chart_atoms(s)):
            hits.append(s["index"])
    if hits:
        return [Finding("D-C05", "design", 2, hits, "Core slide exceeds 250 words with no chart/framework")]
    return []

def pattern_d_c05a(deck: dict) -> list[Finding]:
    f = features(deck)
    avg = f.get("avg_words_per_slide") or 0
    mx = f.get("max_words_per_slide") or 0
    if avg > 180 or mx > 250:
        return [Finding("D-C05a", "design", 2, [], f"Deck-wide density: avg {avg:.0f}, max {mx}")]
    return []

def pattern_d_d04(deck: dict) -> list[Finding]:
    if features(deck).get("title_casing_consistent") is False:
        return [Finding("D-D04", "design", 1, [], "Title casing varies across slides")]
    return []

def pattern_d_d05(deck: dict) -> list[Finding]:
    if features(deck).get("bullet_punctuation_consistent") is False:
        return [Finding("D-D05", "design", 1, [], "Bullet terminal punctuation varies")]
    return []

def pattern_d_d06(deck: dict) -> list[Finding]:
    if features(deck).get("number_format_consistent") is False:
        return [Finding("D-D06", "design", 1, [], "Number formatting varies across slides")]
    return []

def pattern_d_d07(deck: dict) -> list[Finding]:
    pni = features(deck).get("page_number_integrity") or {}
    if pni.get("is_clean") is False:
        parts = []
        if pni.get("duplicates"): parts.append(f"duplicates at {pni['duplicates']}")
        if pni.get("skips"): parts.append(f"skipped {pni['skips']}")
        if pni.get("missing_slides"): parts.append(f"missing on slides {pni['missing_slides']}")
        return [Finding("D-D07", "design", 1, [], "Page numbers: " + "; ".join(parts))]
    return []

def pattern_d_d09(deck: dict) -> list[Finding]:
    n_missing = 0
    slides_hit = []
    for s in slides(deck):
        for a in chart_atoms(s):
            r = a.get("readability") or {}
            if r.get("has_takeaway_annotation") is False:
                n_missing += 1
                slides_hit.append(s["index"])
    if n_missing >= 2:
        return [Finding("D-D09", "design", 1, sorted(set(slides_hit)), f"{n_missing} charts lack a takeaway caption")]
    return []

def pattern_d_d10(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for a in chart_atoms(s):
            r = a.get("readability") or {}
            if r.get("has_axis_units") is False:
                hits.append(s["index"])
    if hits:
        return [Finding("D-D10", "design", 1, sorted(set(hits)), "Chart axis labels or units missing")]
    return []

def pattern_d_d11(deck: dict) -> list[Finding]:
    hits = []
    for s in slides(deck):
        for a in chart_atoms(s):
            series = a.get("series") or []
            if len(series) >= 2:
                r = a.get("readability") or {}
                if r.get("has_legend_if_multiseries") is False:
                    hits.append(s["index"])
    if hits:
        return [Finding("D-D11", "design", 1, sorted(set(hits)), "Multi-series chart missing a clear legend")]
    return []


# =============================================================================
# Gate functions
# =============================================================================

def gate_g01(deck: dict) -> GateResult | None:
    for s in slides(deck):
        t = first_atom(s, "title")
        if t and t.get("contains_course_artifact"):
            return GateResult("G01", "Assignment artifact in title", True, "storyline", 4, evidence=f'slide {s["index"]}: "{t.get("text","")}"')
    return None

def gate_g02(deck: dict) -> GateResult | None:
    # Title slide is slide index 1 (by convention). Check for metadata-block with contact.
    title_slide = next((s for s in slides(deck) if s["role_guess"] == "title"), None)
    if title_slide is None:
        return GateResult("G02", "Missing contact info on title slide", True, "storyline", 4, evidence="No title slide found")
    meta = first_atom(title_slide, "metadata-block")
    if not meta or not (meta.get("contact") or "").strip():
        return GateResult("G02", "Missing contact info on title slide", True, "storyline", 4, evidence="Title slide lacks student contact info")
    return None

def gate_g03(deck: dict) -> GateResult | None:
    exec_slide = next((s for s in slides(deck) if s["role_guess"] == "executive-summary"), None)
    if exec_slide is None:
        return GateResult("G03", "Missing or weak executive summary", True, "storyline", 4, evidence="No executive-summary slide found")
    comp = exec_slide["observations"].get("exec_summary_components") or {}
    required = ("situation", "complication", "resolution")
    if not all(comp.get(k) for k in required):
        missing = [k for k in required if not comp.get(k)]
        return GateResult("G03", "Missing or weak executive summary", True, "storyline", 4, evidence=f"Exec summary missing: {missing}")
    return None

def gate_g04(deck: dict) -> GateResult | None:
    # Generic-vague source on a slide that has quant claims.
    for s in slides(deck):
        if not s.get("argument", {}).get("numeric_claims"):
            continue
        for src in atoms_of_type(s, "source-line"):
            for c in src.get("citations", []):
                if c.get("source_type") == "generic-vague":
                    return GateResult("G04", "Untraceable sources on key claims", True, "evidence", 4,
                                       evidence=f'slide {s["index"]}: "{c.get("source_text","")}"')
    return None

def gate_g05(deck: dict, fired_patterns: list[Finding], config: dict) -> GateResult | None:
    g = config["gates"]["G05"]
    trigger = set(g["trigger_patterns"])
    threshold = g["trigger_threshold"]
    fired_ids = {f.pattern_id for f in fired_patterns if f.pattern_id in trigger}
    if len(fired_ids) >= threshold:
        return GateResult("G05", "AI-scaffolding saturation", True, "storyline", 4,
                           also_drops="insight",
                           evidence=f"Template-saturation patterns fired: {sorted(fired_ids)}")
    return None


# =============================================================================
# Hurdle helpers — each is a function (deck) -> bool
# =============================================================================

HURDLE_FUNCS: dict[str, Callable[[dict], bool]] = {}

def hurdle(name):
    def deco(fn):
        HURDLE_FUNCS[name] = fn
        return fn
    return deco

@hurdle("title_flow_coherent")
def _h_title_flow_coherent(d): return bool(obs(d).get("title_flow", {}).get("coherent"))

@hurdle("recommendation_is_specific_action")
def _h_rec_specific_action(d): return coherence(d).get("recommendation", {}).get("specificity") == "specific-action"

@hurdle("recommendation_specificity_is_specific_action")
def _h_rec_specificity_specific_action(d): return coherence(d).get("recommendation", {}).get("specificity") == "specific-action"

@hurdle("recommendation_is_execution_not_substitute")
def _h_rec_execution(d): return coherence(d).get("recommendation", {}).get("is_execution_or_substitute") == "execution"

@hurdle("exec_summary_complete")
def _h_exec_summary_complete(d):
    es = next((s for s in slides(d) if s["role_guess"] == "executive-summary"), None)
    if not es: return False
    comp = es["observations"].get("exec_summary_components") or {}
    return all(comp.get(k) for k in ("situation", "complication", "resolution", "recommendation"))

@hurdle("most_titles_are_conclusions")
def _h_most_titles_conclusions(d):
    r = features(d).get("action_title_ratio") or 0
    return r >= 0.70

@hurdle("exec_summary_compresses_argument")
def _h_exec_summary_compresses(d):
    return bool(coherence(d).get("exec_summary_matches_body"))

@hurdle("next_steps_have_named_deliverables")
def _h_next_steps_deliverables(d):
    for s in slides(d):
        if s["role_guess"] != "recommendation": continue
        for g in atoms_of_type(s, "n-card-grid"):
            if any(c.get("sub_label") for c in g.get("cards", [])):
                return True
    return False

@hurdle("thesis_is_specific")
def _h_thesis_specific(d): return bool(coherence(d).get("thesis_is_specific"))

@hurdle("pressure_test_not_unaddressed")
def _h_pt_not_unaddressed(d):
    return coherence(d).get("pressure_test", {}).get("deck_anticipates_it") in ("holds-up", "partial")

@hurdle("pressure_test_assumptions_explicit")
def _h_pt_assumptions(d):
    return bool(coherence(d).get("pressure_test", {}).get("assumptions_made_explicit_in_deck"))

@hurdle("pushes_past_observation_to_interpretation")
def _h_push_past_obs(d):
    return bool(coherence(d).get("non_obviousness", {}).get("pushes_past_observation_to_interpretation"))

@hurdle("core_slides_claim_specific_ratio_gte_0_80")
def _h_claim_spec_80(d):
    return (features(d).get("core_slides_claim_is_specific_ratio") or 0) >= 0.80

@hurdle("core_slides_claim_specific_ratio_gte_0_60")
def _h_claim_spec_60(d):
    return (features(d).get("core_slides_claim_is_specific_ratio") or 0) >= 0.60

@hurdle("core_slides_generic_applicability_specific_ratio_gte_0_70")
def _h_generic_70(d):
    return (features(d).get("core_slides_generic_applicability_specific_ratio") or 0) >= 0.70

@hurdle("recommendation_is_specific_or_directional")
def _h_rec_specific_or_dir(d):
    return coherence(d).get("recommendation", {}).get("specificity") in ("specific-action", "directional")

@hurdle("no_internal_contradictions")
def _h_no_contradictions(d):
    return not (coherence(d).get("internal_contradictions") or [])

@hurdle("source_type_count_gte_2")
def _h_source_types_2(d):
    return (features(d).get("source_type_count") or 0) >= 2

@hurdle("most_charts_have_takeaway_caption")
def _h_most_charts_takeaway(d):
    total = 0; with_ = 0
    for s in slides(d):
        for a in chart_atoms(s):
            total += 1
            r = a.get("readability") or {}
            if r.get("has_takeaway_annotation"): with_ += 1
    return total > 0 and (with_ / total) >= 0.80

@hurdle("majority_charts_have_takeaway_caption")
def _h_majority_charts_takeaway(d):
    total = 0; with_ = 0
    for s in slides(d):
        for a in chart_atoms(s):
            total += 1
            r = a.get("readability") or {}
            if r.get("has_takeaway_annotation"): with_ += 1
    return total > 0 and (with_ / total) >= 0.50

@hurdle("most_numeric_claims_show_derivation")
def _h_most_claims_derived(d):
    total = 0; shown = 0
    for s in slides(d):
        for nc in s.get("argument", {}).get("numeric_claims", []) or []:
            total += 1
            if nc.get("derivation_shown"): shown += 1
    return total > 0 and (shown / total) >= 0.70

@hurdle("key_estimates_show_derivation")
def _h_key_estimates_derived(d):
    total = 0; shown = 0
    for s in slides(d):
        for nc in s.get("argument", {}).get("numeric_claims", []) or []:
            total += 1
            if nc.get("derivation_shown"): shown += 1
    return total > 0 and (shown / total) >= 0.40

@hurdle("at_least_two_single_visual_core_slides")
def _h_two_single_visual(d):
    return sum(1 for s in core_slides(d) if s["observations"].get("is_single_visual_slide")) >= 2

@hurdle("charts_have_professional_craft")
def _h_pro_craft(d):
    total = 0; good = 0
    for s in slides(d):
        for a in chart_atoms(s):
            total += 1
            r = a.get("readability") or {}
            if all(r.get(k) for k in ("has_axis_units",)) and r.get("has_takeaway_annotation"): good += 1
    return total > 0 and (good / total) >= 0.80

@hurdle("density_visibly_varies")
def _h_density_varies(d):
    return bool(features(d).get("has_breathing_slides")) and (features(d).get("word_count_std_dev") or 0) >= 25

@hurdle("at_least_half_core_slides_carry_visual_device")
def _h_half_visual(d):
    core = features(d).get("core_slide_count") or 0
    withc = features(d).get("slides_with_charts") or 0
    return core > 0 and (withc / core) >= 0.50

@hurdle("chart_craft_consistent")
def _h_chart_craft_consistent(d):
    total = 0; good = 0
    for s in slides(d):
        for a in chart_atoms(s):
            total += 1
            r = a.get("readability") or {}
            if r.get("has_axis_units"): good += 1
    return total > 0 and (good / total) >= 0.70

@hurdle("deck_has_density_variation")
def _h_deck_density_var(d):
    return (features(d).get("word_count_std_dev") or 0) >= 20


def check_hurdles(deck: dict, level_config: dict) -> tuple[bool, list[str]]:
    """Return (all_passed, notes_on_failures)."""
    notes = []
    for req in level_config.get("requires_all", []) or []:
        if not HURDLE_FUNCS[req](deck):
            notes.append(f"requires_all failed: {req}")
    req_any = level_config.get("requires_any") or []
    if req_any and not any(HURDLE_FUNCS[r](deck) for r in req_any):
        notes.append(f"requires_any failed: {req_any}")
    return (len(notes) == 0, notes)


# =============================================================================
# Tier anchors
# =============================================================================

def tier_anchor(t3: int, t2: int, anchors: list[dict]) -> int:
    for a in anchors:
        # Match conditions; all specified keys must hold.
        if "t3_exact" in a and t3 != a["t3_exact"]: continue
        if "t3_min" in a and t3 < a["t3_min"]: continue
        if "t3_max" in a and t3 > a["t3_max"]: continue
        if "t2_min" in a and t2 < a["t2_min"]: continue
        if "t2_max" in a and t2 > a["t2_max"]: continue
        return a["provisional"]
    return 2  # default floor


# =============================================================================
# Orchestration
# =============================================================================

ALL_PATTERN_FNS: dict[str, Callable[[dict], list[Finding]]] = {
    "S-B01": pattern_s_b01, "S-B02": pattern_s_b02,
    "S-C01": pattern_s_c01, "S-C02": pattern_s_c02, "S-C03": pattern_s_c03,
    "S-C04": pattern_s_c04, "S-C05": pattern_s_c05, "S-C06": pattern_s_c06,
    "S-C07": pattern_s_c07, "S-C07a": pattern_s_c07a, "S-C07b": pattern_s_c07b,
    "S-C07c": pattern_s_c07c, "S-C07d": pattern_s_c07d, "S-C07e": pattern_s_c07e,
    "S-C08": pattern_s_c08, "S-C09": pattern_s_c09, "S-C10": pattern_s_c10,
    "S-C12": pattern_s_c12, "S-C13": pattern_s_c13, "S-C14": pattern_s_c14,
    "S-C15": pattern_s_c15,
    "I-C01": pattern_i_c01, "I-C02": pattern_i_c02, "I-C03": pattern_i_c03, "I-C04": pattern_i_c04,
    "E-B01": pattern_e_b01, "E-B02": pattern_e_b02, "E-B03": pattern_e_b03, "E-B04": pattern_e_b04, "E-B06": pattern_e_b06,
    "E-C02": pattern_e_c02, "E-C03": pattern_e_c03, "E-C04": pattern_e_c04,
    "E-D02": pattern_e_d02, "E-D03": pattern_e_d03,
    "D-B01": pattern_d_b01, "D-B02": pattern_d_b02,
    "D-C01": pattern_d_c01, "D-C02": pattern_d_c02, "D-C03": pattern_d_c03,
    "D-C04": pattern_d_c04, "D-C05": pattern_d_c05, "D-C05a": pattern_d_c05a,
    "D-D04": pattern_d_d04, "D-D05": pattern_d_d05, "D-D06": pattern_d_d06, "D-D07": pattern_d_d07,
    "D-D09": pattern_d_d09, "D-D10": pattern_d_d10, "D-D11": pattern_d_d11,
}


def score_deck(deck: dict, rubric: dict) -> dict:
    # Step 1: fire every pattern
    findings: list[Finding] = []
    for pid, fn in ALL_PATTERN_FNS.items():
        pcfg = rubric["patterns"].get(pid)
        if not pcfg:
            continue
        for f in fn(deck):
            f.student_name = pcfg.get("student_name", pid)
            findings.append(f)

    # Step 2: evaluate gates
    gates_fired: list[GateResult] = []
    for gfn, gid in [(gate_g01, "G01"), (gate_g02, "G02"), (gate_g03, "G03"), (gate_g04, "G04")]:
        g = gfn(deck)
        if g: gates_fired.append(g)
    g5 = gate_g05(deck, findings, rubric)
    if g5: gates_fired.append(g5)

    # Step 3: per-dimension scoring
    anchors = rubric["tier_anchors"]
    weights = {d: rubric["dimensions"][d]["weight"] for d in rubric["dimensions"]}
    dim_scores: dict[str, DimensionScore] = {}

    for dim in rubric["dimensions"]:
        dfinds = [f for f in findings if f.dimension == dim]
        t3 = sum(1 for f in dfinds if f.tier == 3)
        t2 = sum(1 for f in dfinds if f.tier == 2)
        t1 = sum(1 for f in dfinds if f.tier == 1)
        provisional = tier_anchor(t3, t2, anchors)

        # hurdles
        hconf = rubric.get("hurdles", {}).get(dim, {})
        after = provisional
        notes: list[str] = []
        if after == 7:
            ok, nts = check_hurdles(deck, hconf.get("level_7", {}))
            if not ok:
                after = 6
                notes.append(f"Level-7 hurdle not met; dropped to 6. {nts}")
        if after == 6:
            ok, nts = check_hurdles(deck, hconf.get("level_6", {}))
            if not ok:
                after = 5
                notes.append(f"Level-6 hurdle not met; dropped to 5. {nts}")

        # gate caps
        after_gates = after
        for g in gates_fired:
            if g.dimension == dim:
                after_gates = min(after_gates, g.cap)
            if g.gate_id == "G05" and g.also_drops == dim:
                after_gates = max(1, after_gates - 1)  # G05 drops insight one level

        final = after_gates
        dim_scores[dim] = DimensionScore(
            dimension=dim,
            findings=dfinds,
            t1_count=t1, t2_count=t2, t3_count=t3,
            provisional=provisional,
            after_hurdles=after,
            hurdle_notes=notes,
            after_gates=after_gates,
            final=final,
            weight=weights[dim],
            weighted=final * weights[dim],
        )

    # Step 4: weighted total
    weighted_sum = sum(ds.weighted for ds in dim_scores.values())
    deck_score = round(weighted_sum * 100 / 7)

    # Step 5: build JSON output
    return {
        "scoring_schema_version": "1.0",
        "rubric_id": rubric["rubric_id"],
        "deck_id": deck["meta"]["deck_id"],
        "final_score_weighted": round(weighted_sum, 3),
        "final_score_100": deck_score,
        "dimensions": {
            dim: {
                "label": rubric["dimensions"][dim]["label"],
                "weight": ds.weight,
                "final": ds.final,
                "weighted": round(ds.weighted, 3),
                "tier_counts": {"T3": ds.t3_count, "T2": ds.t2_count, "T1": ds.t1_count},
                "derivation": {
                    "provisional_from_tier_anchor": ds.provisional,
                    "after_hurdles": ds.after_hurdles,
                    "after_gates": ds.after_gates,
                    "hurdle_notes": ds.hurdle_notes,
                },
                "findings": [asdict(f) for f in ds.findings],
            } for dim, ds in dim_scores.items()
        },
        "gates_fired": [asdict(g) for g in gates_fired],
        "findings_total": len(findings),
    }


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("deck_json", help="Path to deck.json")
    p.add_argument("--rubric", default="rubrics/deck-quality-rubric.yaml")
    p.add_argument("--out", default=None, help="Output path for scoring.json (default: sibling of deck.json)")
    args = p.parse_args()

    deck_path = Path(args.deck_json)
    deck = json.loads(deck_path.read_text())
    rubric = yaml.safe_load(Path(args.rubric).read_text())

    result = score_deck(deck, rubric)

    out_path = Path(args.out) if args.out else deck_path.parent / "scoring.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"Wrote {out_path}")
    print(f"Score: {result['final_score_100']} / 100")
    for dim, info in result["dimensions"].items():
        print(f"  {info['label']}: {info['final']}/7 (tier counts T3={info['tier_counts']['T3']} T2={info['tier_counts']['T2']} T1={info['tier_counts']['T1']})")
    if result["gates_fired"]:
        print("Gates fired:", [g["gate_id"] for g in result["gates_fired"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
