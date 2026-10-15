"""Build chunks from top-level sections in parsed Markdown files."""

import json
import os
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHUNKING_URL = os.getenv("CHUNKING_URL", "http://localhost:8085")




def chunker(source_path: Path, output_dir: Path) -> dict:
    """Build, save, and return chunks for one Markdown file."""

    markdown = source_path.read_text(encoding="utf-8")

    chunk_response = requests.post(
        f"{CHUNKING_URL.rstrip('/')}/services/chunking/doc_by_titles",
        data={"content_parsed": markdown, "max_split_tokens": 800},
        timeout=(10, 300),
    )
    chunk_response.raise_for_status()
    chunk_data = chunk_response.json()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{source_path.stem}_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunk_data, f, indent=4, ensure_ascii=False)

    return chunk_data
