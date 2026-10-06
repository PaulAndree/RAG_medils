

INGESTION WORK:

Delete_previous
docker compose exec -T postgres \
  psql -U raguser -d ragdb -v ON_ERROR_STOP=1 \
  -c 'DROP TABLE IF EXISTS chunks, documents CASCADE;'


create the tables:
POSTGRES_HOST=localhost uv run python -c \
"from sql_rag.database_postgres import create_tables; create_tables(); print('Schema created')"


Inspect the schema
docker compose exec -T postgres \
  psql -U raguser -d ragdb \
  -c '\d+ documents' \
  -c '\d+ chunks' \
  -c 'SELECT COUNT(*) AS documents FROM documents;' \
  -c 'SELECT COUNT(*) AS chunks FROM chunks;'

Run for example of normalization  check
  uv run python -c "
from pathlib import Path
from sql_rag.ingestion import load_and_normalize_json

document = load_and_normalize_json(
    Path('data/pdf_parsed_output/example_chunks.json')
)

print('chunks:', document.chunk_count)
print('language:', document.language)
print('metadata:', document.metadata)
print('first title:', document.chunks[0].title)
print('first token count:', document.chunks[0].token_count)
"


run for example of identity and hashing:

uv run python -c "
from pathlib import Path
from sql_rag.ingestion import prepare_document, build_chunk_id

document = prepare_document(
    json_path=Path('data/pdf_parsed_output/example_chunks.json'),
    chunks_root=Path('data/pdf_parsed_output'),
    pdf_root=Path('data/pdf_docs'),
)

first_chunk = document.chunks[0]

print('source key:', document.source_key)
print('name:', document.name)
print('title:', document.title)
print('document UUID:', document.id)
print('chunks:', len(document.chunks))
print('JSON hash length:', len(document.json_hash))
print('PDF found:', document.pdf_path is not None)
print('warnings:', document.warnings)
print('first chunk hash length:', len(first_chunk.content_hash))
print(
    'first chunk UUID:',
    build_chunk_id(
        document.id,
        1,
        first_chunk.chunk_index,
        first_chunk.content_hash,
    ),
)
"


run for file discovery:

uv run python -c "
from pathlib import Path
from sql_rag.ingestion import discover_chunk_files, prepare_document

chunks_root = Path('data/pdf_parsed_output')
pdf_root = Path('data/pdf_docs')

files = discover_chunk_files(chunks_root)

print('discovered:', len(files))

for json_path in files:
    document = prepare_document(
        json_path=json_path,
        chunks_root=chunks_root,
        pdf_root=pdf_root,
    )

    print('source:', document.source_key)
    print('JSON:', document.json_path)
    print('PDF:', document.pdf_path)
    print('warnings:', document.warnings)
"


execute the main script for ingestion:

peyzaguirre@wiig:~/learning_1$ POSTGRES_HOST=localhost uv run python -m sql_rag.main_ingestion   --chunks-dir data/pdf_parsed_output   --pdf-dir data/pdf_docs

-------------------------------------------------------------------------------------------
ARCHITECTURE:

Original files → object/file storage
Document + chunk records → PostgreSQL (source of truth)
Embeddings + searchable payload → Qdrant (derived search index)


----------------------------------------------------------------
docker compose down    # Stop and remove containers and networks

docker compose up -d   # Recreate and start them in the background

If you changed Python code, dependencies, or the Dockerfile:
docker compose up -d --build
This starts:
- PostgreSQL on host port 5432
- Qdrant on host ports 6335 and 6336
- FastAPI on 127.0.0.1:8002
- Prometheus on 127.0.0.1:9090
- Grafana on port 3003


The indexer is a separate one-time job and is not started by docker compose up. Run it only when you need to build a new index:
docker compose run --rm indexer


- CSSH Tunnel to access from local!!

ssh -N -L 8004:127.0.0.1:8002 -L 9090:127.0.0.1:9090 -L 3003:127.0.0.1:3003 peyzaguirre@wiig.dia.fi.upm.es

Then open:
API documentation: http://localhost:8002/docs
Prometheus: http://localhost:9090
Grafana: http://localhost:3003


-----------------------------------------------------------------------
To stop containers while keeping them available for a quick restart:
docker compose stop
Restart them later with:
docker compose start

