import json
import os


import os
from pathlib import Path
from time import perf_counter
from typing import Any

import requests    

OCR_URL = os.getenv("OCR_URL", "http://localhost:8084")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHUNKING_URL = os.getenv("CHUNKING_URL", "http://localhost:8085")

pdf_file = PROJECT_ROOT / "data" / "pdf_docs" / "2502.06872v1.pdf"
"""
with pdf_file.open("rb") as source:
    ocr_response = requests.post(
        f"{OCR_URL.rstrip('/')}/services/ocr",
        files={
            "file": (
                pdf_file.name,
                source,
                "application/pdf",
            )
        },
        data={"type_name": "pdf"},
        timeout=(10, 300),
    )
ocr_response.raise_for_status()
ocr_data = ocr_response.json()
content = ocr_data.get("content_parsed")
with open(PROJECT_ROOT / "data" / "pdf_parsed_output" / f"{pdf_file.stem}2222.md", "w", encoding="utf-8") as f:
    f.write(content)
print(content)
""" 


with open(PROJECT_ROOT / "data" / "pdf_parsed_output" / f"{pdf_file.stem}2222.md", "r", encoding="utf-8") as f:
    content = f.read()
"""
chunk_response = requests.post(
    f"{CHUNKING_URL.rstrip('/')}/services/chunking/doc",
    data={"content_parsed": content,
          "min_split_tokens": 200,
          "max_split_tokens": 500,
          "split_tokens_tolerance": 50,
          "window_size": 5},
    timeout=(10, 300),
)
chunk_response.raise_for_status()
chunk_data = chunk_response.json()
with open(PROJECT_ROOT / "data" / "passages_chunk" / f"{pdf_file.stem}222_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunk_data, f, indent=4, ensure_ascii=False)

"""

chunk_response = requests.post(
    f"{CHUNKING_URL.rstrip('/')}/services/chunking/doc_by_titles",
    data={"content_parsed": content, "max_split_tokens": 800},
    timeout=(10, 300),
)
chunk_response.raise_for_status()
chunk_data = chunk_response.json()
with open(PROJECT_ROOT / "data" / "arguments"/ "chunks_for_arguments"/ f"{pdf_file.stem}222_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunk_data, f, indent=4, ensure_ascii=False)
