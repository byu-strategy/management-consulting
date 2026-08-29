"""Quick test of Reducto parse API on a student deck PDF."""
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from reducto import Reducto

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env.local")

PDF = ROOT / "grades" / "pdfs" / "benjamin-william-hughes.pdf"
OUT_DIR = ROOT / "workspace" / "reducto-output-enriched"
OUT_DIR.mkdir(parents=True, exist_ok=True)

client = Reducto()

print(f"Uploading {PDF.name} ({PDF.stat().st_size / 1024:.1f} KB)...")
upload = client.upload(file=PDF)
print(f"Uploaded: {upload.file_id}")

print("Parsing...")
parse_result = client.parse.run(
    input=upload.file_id,
    enhance={
        "summarize_figures": True,
        "intelligent_ordering": True,
        "agentic": [
            {"scope": "figure", "advanced_chart_agent": True, "return_overlays": False},
            {"scope": "table"},
        ],
    },
)

if parse_result.result.type == "url":
    chunks = requests.get(parse_result.result.url).json()
else:
    chunks = [c.model_dump() if hasattr(c, "model_dump") else c for c in parse_result.result.chunks]

raw_path = OUT_DIR / f"{PDF.stem}.parse.json"
raw_path.write_text(json.dumps(parse_result.model_dump(), indent=2, default=str))
chunks_path = OUT_DIR / f"{PDF.stem}.chunks.json"
chunks_path.write_text(json.dumps(chunks, indent=2, default=str))

text_path = OUT_DIR / f"{PDF.stem}.txt"
with text_path.open("w") as f:
    for i, ch in enumerate(chunks):
        content = ch["content"] if isinstance(ch, dict) else ch.content
        f.write(f"\n\n===== CHUNK {i} =====\n{content}\n")

print(f"\nWrote:\n  {raw_path}\n  {chunks_path}\n  {text_path}")
print(f"\n{len(chunks)} chunks. Job duration: {parse_result.duration:.2f}s")
print("\n--- First chunk preview ---")
first = chunks[0]
preview = first["content"] if isinstance(first, dict) else first.content
print(preview[:800])
