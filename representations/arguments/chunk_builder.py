"""Build chunks from top-level sections in parsed Markdown files."""

import json
from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter



TOKENIZER_MODEL = "qwen3:14b"


def count_tokens(text: str) -> int:
    """Return a simple whitespace-based token estimate."""

    return len(text.split())


def chunker(source_path: Path, output_dir: Path) -> dict:
    """Build, save, and return chunks for one Markdown file."""

    markdown = source_path.read_text(encoding="utf-8")
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "section")],
        strip_headers=False,
    )
    sections = splitter.split_text(markdown)
    chunks = [section.page_content for section in sections]
    chunk_titles = [section.metadata.get("section", "Untitled") for section in sections]
    output_path = output_dir / f"{source_path.stem}_chunks.json"
    chunk_data = {
        "chunk_list": chunks,
        "chunk_size": len(chunks),
        "chunk_title": chunk_titles,
        "token_count": [count_tokens(chunk) for chunk in chunks],
        "source_path": str(source_path),
        "output_path": str(output_path),
        "tokenizer_model": TOKENIZER_MODEL,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(chunk_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return chunk_data
