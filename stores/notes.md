POSTGRES_HOST=localhost python -m stores.main_ingestion \
  --data-dir data \
  --rebuild

POSTGRES_HOST=localhost python -m stores.main_ingestion --data-dir data --rebuild

## documents

Identity and relationships: Deterministic UUID primary key; unique text `source_key`.

Stored data: Existing document metadata, PDF/JSON paths and hashes, version, status, and timestamps.

## chunks

Identity and relationships: Deterministic UUID; composite foreign key `(document_id, document_version)` referencing `documents`.

Stored data: Passage content, index, title, token/page data, and content hash.

## chunks_for_arguments

Identity and relationships: Deterministic UUID in a separate ID namespace; composite foreign key referencing `documents`.

Stored data: Argument-oriented chunks using the same validated chunk fields.

## arguments

Identity and relationships: Existing source argument ID as text primary key; UUID `chunk_id` foreign key referencing `chunks_for_arguments`.

Stored data: Claim and JSONB evidence array.

## entities

Identity and relationships: Deterministic UUID primary key; unique UUID `chunk_id` foreign key referencing `chunks_for_arguments`.

Stored data: JSONB entity and relation arrays.

## summaries

Identity and relationships: Text `node_id` primary key.

Stored data: Summary text, level, scope, nullable document UUID, catalog ID, and JSONB provenance arrays.