"""Build chunks and extract claim/evidence arguments with Ollama."""

import json
from pathlib import Path

import requests

from chunk_builder import chunker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
INPUT_DIR = PROJECT_ROOT / "data" / "pdf_parsed_output"
CHUNKS_DIR = PROJECT_ROOT / "data" / "arguments" / "chunks_for_arguments"
ARGUMENTS_DIR = PROJECT_ROOT / "data" / "arguments" /"arguments_extracted"

OLLAMA_URL = "http://localhost:11435"
MODEL = "qwen3:14b"


def extract_arguments(
    chunk_list: list[str],
    document_id: str,
    output_path: Path,
) -> list[dict]:
    """Extract arguments from chunks and save them as JSON."""

    user_template = (PROMPT_DIR / "user_extraction_prompt.txt").read_text(
        encoding="utf-8"
    )
    system_prompt = (PROMPT_DIR / "system_extraction_prompt.txt").read_text(
        encoding="utf-8"
    )

    arguments = []

    for chunk_number, chunk_text in enumerate(chunk_list, start=1):
        chunk_id = f"{document_id}_chunk_{chunk_number}"
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": user_template.format(
                    section_id=chunk_id,
                    chunk_text=chunk_text,
                ),
                "system": system_prompt,
                "format": "json",
                "stream": False,
                "think": False,
                "options": {"temperature": 0},
            },
            timeout=(10, 900),
        )
        response.raise_for_status()
        data = json.loads(response.json()["response"])

        for number, argument in enumerate(data.get("arguments", []), start=1):
            argument["id"] = f"{chunk_id}_arg_{number}"
            arguments.append(argument)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(arguments, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return arguments


def main() -> None:
    for markdown_file in sorted(INPUT_DIR.glob("*.md")):
        chunk_data = chunker(markdown_file, CHUNKS_DIR)
        output_path = ARGUMENTS_DIR / f"{markdown_file.stem}_arguments.json"
        arguments = extract_arguments(
            chunk_data["chunk_list"],
            markdown_file.stem,
            output_path,
        )
        print(f"{markdown_file.name}: {len(arguments)} arguments")


if __name__ == "__main__":
    main()
