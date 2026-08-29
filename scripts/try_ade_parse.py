"""One-off: parse a student deck with LandingAI ADE and print a summary."""
import os
import json
from pathlib import Path
from collections import Counter

from dotenv import load_dotenv
from landingai_ade import LandingAIADE

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT / ".env.local", override=True)
load_dotenv(override=True)
assert os.getenv("VISION_AGENT_API_KEY"), "VISION_AGENT_API_KEY not set"

DECK = ROOT / "grades/pdfs/collin-powell.pdf"
assert DECK.exists(), DECK

client = LandingAIADE()
print(f"Parsing: {DECK.name} ({DECK.stat().st_size/1024:.0f} KB)")

result = client.parse(document=DECK, model="dpt-2-latest", split="page")

print("\n=== METADATA ===")
print(f"job_id:    {result.metadata.job_id}")
print(f"pages:     {len(result.splits)}")
print(f"chunks:    {len(result.chunks)}")
print(f"ms:        {result.metadata.duration_ms}")
print(f"md chars:  {len(result.markdown)}")

type_counts = Counter(c.type for c in result.chunks)
print(f"\n=== CHUNK TYPES ===")
for t, n in type_counts.most_common():
    print(f"  {t:15s} {n}")

print(f"\n=== PER-SLIDE SUMMARY ===")
print(f"{'#':>3} {'words':>6} {'chunks':>6}  types")
for i, split in enumerate(result.splits, start=1):
    words = len((split.markdown or "").split())
    slide_chunks = [c for c in result.chunks if c.grounding.page == i - 1]
    types = Counter(c.type for c in slide_chunks)
    types_str = ", ".join(f"{t}:{n}" for t, n in types.most_common())
    print(f"{i:>3} {words:>6} {len(slide_chunks):>6}  {types_str}")

# Save full markdown + a compact JSON summary for inspection
out_md = ROOT / "scripts/collin-powell.parse.md"
out_md.write_text(result.markdown)
print(f"\nSaved markdown -> {out_md.relative_to(ROOT)}")

out_json = ROOT / "scripts/collin-powell.parse.json"
compact = {
    "metadata": {
        "pages": len(result.splits),
        "chunks": len(result.chunks),
        "duration_ms": result.metadata.duration_ms,
    },
    "slides": [
        {
            "slide": i,
            "words": len((s.markdown or "").split()),
            "markdown": s.markdown,
        }
        for i, s in enumerate(result.splits, start=1)
    ],
    "chunks": [
        {
            "id": c.id,
            "type": c.type,
            "page": c.grounding.page,
            "box": [c.grounding.box.l, c.grounding.box.t, c.grounding.box.r, c.grounding.box.b],
        }
        for c in result.chunks
    ],
}
out_json.write_text(json.dumps(compact, indent=2))
print(f"Saved JSON     -> {out_json.relative_to(ROOT)}")

print(f"\n=== FIRST SLIDE MARKDOWN (preview) ===")
print(result.splits[0].markdown[:800])
