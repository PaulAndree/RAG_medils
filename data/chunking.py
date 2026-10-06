from pathlib import Path

import requests

pdf_path = Path(
    "/home/peyzaguirre/learning_1/data/pdf_docs/example.pdf"
)
outputh_path = Path(
    "/home/peyzaguirre/learning_1/data/pdf_parsed_output/"
)

with pdf_path.open("rb") as pdf_file:
    ocr_response = requests.post(
        "http://localhost:8084/services/ocr",
        files={
            "file": (
                pdf_path.name,
                pdf_file,
                "application/pdf",
            )
        },
        data={"type_name": "pdf"},
        timeout=300,
    )

ocr_response.raise_for_status()
content_parsed = ocr_response.json()["content_parsed"]

with open(outputh_path / f"{pdf_path.stem}.md", "w") as text_file:
    text_file.write(content_parsed)

chunk_response = requests.post(
    "http://localhost:8085/services/chunking/doc",
    data={"content_parsed": content_parsed},
    timeout=300,
)

chunk_response.raise_for_status()
print(chunk_response.json())

with open(outputh_path / f"{pdf_path.stem}_chunks.json", "w") as chunks_file:
    chunks_file.write(chunk_response.text)