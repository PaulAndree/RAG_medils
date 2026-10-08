import json
import requests
from pathlib import Path    

MODEL = "qwen3:14b"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
INPUT_DIR = PROJECT_ROOT / "data" / "pdf_parsed_output"
#use the chunks for arguments
CHUNKS_DIR = PROJECT_ROOT / "data" / "arguments" / "chunks_for_arguments"
ENTITIES_DIR = PROJECT_ROOT / "data" / "entities"



def extract_triplets(chunk: str, title: str, chunk_id: int, document_id: str) -> dict:
    user_template = (PROMPT_DIR / "entity_extraction_usr.txt").read_text(
        encoding="utf-8"
    )
    system_prompt = (PROMPT_DIR / "entity_extraction_sys.txt").read_text(
        encoding="utf-8"
    )
    
    user_prompt = user_template.format(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    document_title=title,
                    chunk_text=chunk
                )

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        },
    )

    response.raise_for_status()

    content = response.json()["message"]["content"]

    return json.loads(content)

def main() -> None:

    for chunk_json_file in sorted(CHUNKS_DIR.glob("*.json")):
        output_path = ENTITIES_DIR / f"{chunk_json_file.stem}_entities.json"
        with open(chunk_json_file, "r", encoding="utf-8") as f:
            document = json.load(f)
        results = []

        for i, chunk, title in zip(range(len(document["chunk_list"])), document["chunk_list"], document["chunk_title"]):
            extraction = extract_triplets(
                chunk=chunk,
                title=title if title else "Unknown Title",
                chunk_id=i,
                document_id=chunk_json_file.stem
            )

            results.append({
                "chunk_id": i,
                **extraction,
            })

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f)

if __name__ == "__main__":
    main()