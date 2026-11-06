# End-to-end RAG: from documents to a conversational research assistant

This project records our learning path while building a Retrieval-Augmented Generation (RAG) system. We started with document processing and connected every stage: uploading original files, extracting text, constructing a hierarchy of passages and summaries, storing their provenance, indexing dense and sparse embeddings, retrieving evidence with temporal constraints, and streaming an answer into a persistent chat interface.

The central idea is that an answer should come from our documents and remain traceable to them. The system therefore needs more than an LLM: it needs reliable ingestion, useful representations, metadata that survives each transformation, tenant isolation, conversation memory, and a way to open the original sources.

This README describes the **working-tree implementation inspected on 3 November 2026**. It covers the backend in `RAG_medils/`, the frontend in `/home/peyzaguirre/notebooks/chat_ui/rag-chatbot/`, and the supporting services under `/srv/iarag/services/`. Commands below use the current package layout. Some older component notes, Docker entry points, and tests still refer to earlier layouts.

The main application flow is implemented. There are also specific unfinished details: author metadata is stored but is not yet propagated into newly indexed retrieval payloads, the generation prompt uses thegit branch passage title rather than `document_title`, and some deployment/evaluation files need updating. These are explained below so reproducing the project does not depend on assumptions about features that are not connected yet.

## Contents

- [1. Architecture](#1-architecture)
- [2. Project map and learning sequence](#2-project-map-and-learning-sequence)
- [3. Ingestion: files, metadata, and OCR](#3-ingestion-files-metadata-and-ocr)
- [4. Hierarchical representation with RAPTOR](#4-hierarchical-representation-with-raptor)
- [5. PostgreSQL, embeddings, and Qdrant](#5-postgresql-embeddings-and-qdrant)
- [6. Query rewriting, temporal retrieval, and recency](#6-query-rewriting-temporal-retrieval-and-recency)
- [7. Generation, memory, streaming, and sources](#7-generation-memory-streaming-and-sources)
- [8. Frontend architecture](#8-frontend-architecture)
- [9. Authentication and tenant isolation](#9-authentication-and-tenant-isolation)
- [10. Reproduce the system locally](#10-reproduce-the-system-locally)
- [11. API reference and direct chat example](#11-api-reference-and-direct-chat-example)
- [12. Operations, monitoring, and recovery](#12-operations-monitoring-and-recovery)
- [13. Verification and evaluation](#13-verification-and-evaluation)
- [14. Current limits and next improvements](#14-current-limits-and-next-improvements)

## 1. Architecture

There are two main backend workflows. **Ingestion** runs through a FastAPI application and background processing functions. **Retrieval and generation** run through a second FastAPI application, with LangGraph orchestrating the conversational workflow. LangGraph does not currently orchestrate the ingestion stages.

```mermaid
flowchart TD
    Upload["PDF or Markdown + metadata"] --> Ingest["Ingestion FastAPI :8009"]
    Ingest --> Originals["Original files on disk"]
    Ingest --> DB["PostgreSQL :5433"]
    Ingest --> Background["Background processing per tenant"]
    Background --> Parse{"File type"}
    Parse -->|PDF| OCR["MinerU OCR :8084"]
    Parse -->|Markdown| Markdown["Parsed Markdown"]
    OCR --> Markdown
    Markdown --> Chunks["Semantic chunking :8085"]
    Chunks --> Hierarchy["RAPTOR passages and summaries"]
    Hierarchy <--> Ollama["Ollama / qwen3:14b :11436"]
    Hierarchy <--> Embeddings["Vectorizer :8089"]
    Hierarchy --> DB
    DB --> Indexer["Dense + sparse index build"]
    Embeddings --> Indexer
    Indexer --> Qdrant["Qdrant :6337"]
    Browser["Browser"] <--> Next["Next.js :3005"]
    Next <--> API["Retrieval FastAPI :8005"]
    API <--> Graph["LangGraph: retrieve → generate"]
    Graph <--> Qdrant
    Graph <--> Embeddings
    Graph <--> Ollama
    Graph <--> DB
    API --> Originals
```

| Component | Responsibility | Main implementation |
| --- | --- | --- |
| Ingestion API | Authenticate an ingestion key, validate and register a file, schedule processing, report summary completion | [`ingest/api.py`](RAG_medils/ingest/api.py) |
| Ingestion coordinator | Prepare Markdown, build the tenant representation, commit summaries, trigger indexing | [`ingest/processing.py`](RAG_medils/ingest/processing.py) |
| OCR service | Convert PDFs into Markdown using MinerU | `/srv/iarag/services/ocr/` |
| Chunking service | Split Markdown into semantically related passages with titles and token counts | `/srv/iarag/services/chunking/` |
| RAPTOR builder | Build passage, cluster, document, and catalog nodes with provenance | [`summaries/builder.py`](RAG_medils/ingest/representations/summaries/builder.py) |
| Vectorizer | Serve BGE-M3 dense embeddings and MILCO learned sparse embeddings | `/srv/iarag/services/vectorizer/` |
| PostgreSQL | Persist originals' metadata, representations, accounts, sessions, conversation history, and graph checkpoints | [`database_postgres.py`](RAG_medils/ingest/stores/database_postgres.py), [`auth.sql`](RAG_medils/retrieval_and_generation/auth.sql) |
| Qdrant | Search all hierarchy levels through named dense and sparse vectors and metadata filters | [`indexer_qdrant.py`](RAG_medils/ingest/indexing/summaries/indexer_qdrant.py) |
| Retrieval API | Authentication, retrieval, chat streaming, history, and source downloads | [`retrieval_and_generation/api.py`](RAG_medils/retrieval_and_generation/api.py) |
| LangGraph | Maintain conversation state and execute retrieval followed by generation | [`rag_graph.py`](RAG_medils/retrieval_and_generation/workflows/rag_graph.py) |
| Next.js UI | Login, chat, saved conversations, streamed Markdown, and source previews | `/home/peyzaguirre/notebooks/chat_ui/rag-chatbot/` |
| Prometheus / Pushgateway / Grafana | Collect retrieval timings and batch processing metrics; visualize runs | [`metrics.py`](RAG_medils/metrics.py), [`grafana/`](RAG_medils/grafana/) |

Neo4j appears in Compose and the Python dependencies, but the current `retrieve → generate` graph does not use it. Earlier graph, argument, and separate passage retrieval experiments are not part of the active pipeline. Similarly, the shared vectorizer has integrations for other stores; **this application's index is Qdrant**.

## 2. Project map and learning sequence

```text
/home/peyzaguirre/learning/
├── README.md                              # This whole-project guide
├── python_client/
│   ├── ingestion_client.py                # Upload files or directories
│   └── ingestion_status.py                # Check one document
└── RAG_medils/                             # Backend Git repository
    ├── pyproject.toml / uv.lock            # Python dependencies
    ├── docker-compose.yml                 # Databases and monitoring; legacy API entry point
    ├── metrics.py
    ├── ingest/
    │   ├── api.py / processing.py
    │   ├── create_table.py                # Ingestion API-key table/helper
    │   ├── representations/
    │   │   ├── main.py
    │   │   ├── passages/builder.py
    │   │   └── summaries/
    │   │       ├── builder.py
    │   │       └── raptor_clustering.py
    │   ├── stores/
    │   │   ├── ingestion.py               # Validation and provenance checks
    │   │   └── database_postgres.py
    │   ├── indexing/
    │   │   ├── main.py / embedding_api.py
    │   │   └── summaries/indexer_qdrant.py
    │   └── data/                          # Default API-managed artifacts
    ├── retrieval_and_generation/
    │   ├── api.py / auth.sql / hash_password.py
    │   ├── retrieval/semantic_search.py
    │   ├── generation/generator.py
    │   └── workflows/rag_graph.py
    ├── tests/
    ├── evaluation/                        # Earlier benchmark code and results
    └── grafana/

/home/peyzaguirre/notebooks/chat_ui/rag-chatbot/
├── app/                                   # App Router pages and server routes
├── components/                            # Chat, sources, and UI primitives
├── hooks/use-persistent-chat-runtime.ts
├── lib/rag-api.ts                          # Server-side API and session proxy
└── package.json / package-lock.json
```

`learning/` itself is a workspace, not the backend Git root. Keep this README, the upload clients, the backend, the frontend, and the external services together when packaging a reproducible copy. Absolute paths in this guide describe this machine; substitute your own roots on another machine. Some evaluation and test files are ignored by the backend's `.gitignore`, so a clone may not contain every local experiment.

A useful order for understanding or rebuilding the project is:

| Step | What we learn | Concrete result |
| --- | --- | --- |
| 1 | Separate document content from metadata and identity | A stored original, UUID, content hash, tenant, and metadata object |
| 2 | Normalize input formats before retrieval | PDFs become Markdown; Markdown can enter directly |
| 3 | Split documents without losing their structure | Passages with section titles and token counts |
| 4 | Represent the same content at several levels | A hierarchy from passages to a tenant catalog summary |
| 5 | Preserve relationships through transformations | Every summary identifies its source nodes, passages, and documents |
| 6 | Combine semantic and term-sensitive search | BGE-M3 and MILCO vectors on each Qdrant point |
| 7 | Translate temporal intent into database constraints | Structured query analysis and Qdrant creation-date filters |
| 8 | Balance relevance with freshness | A modification-date bonus after hybrid retrieval |
| 9 | Ground generation and preserve conversations | LangGraph state, PostgreSQL checkpoints, and streamed answers |
| 10 | Build a usable application around the pipeline | Login, private history, tenant-owned documents, and source previews |

## 3. Ingestion: files, metadata, and OCR

### 3.1 Upload contract

`POST /ingest` accepts one multipart file and an optional JSON string in the `metadata` form field. Supported uploads are nonempty `.pdf` files and nonempty UTF-8 `.md` files. The surrounding OCR service supports additional formats, but the ingestion API currently accepts only PDF and Markdown.

The request carries `Authorization: Bearer <ingestion-key>`. PostgreSQL resolves the key to a tenant and a permission. Only `ingest` and `admin` permissions can upload. Ownership comes from the authenticated key, not a tenant field supplied in metadata.

Example metadata:

```json
{
  "title": "DNA repair experiment report",
  "author": "Research team",
  "createdDateTime": "2026-10-01T09:00:00Z",
  "modifiedDateTime": "2026-10-20T15:30:00Z",
  "language": "en",
  "repository_id": "research-notes",
  "tags": ["DNA repair", "experiment"]
}
```

| Field | Meaning and current behavior |
| --- | --- |
| `title` | Human-readable document title. If omitted or blank, the filename stem is used. |
| `author` | Source author, preserved in `documents.metadata`. The current indexing path does not copy it into Qdrant; see the citation section. |
| `createdDateTime` | Source-document creation time used by temporal retrieval. |
| `modifiedDateTime` | Source-document modification time used by the recency bonus. |
| `language` | Optional stored language metadata. |
| Other JSON fields | Preserved, including nested objects and arrays; not automatically made searchable. |

Dates should be ISO 8601 timestamps with an explicit timezone, preferably UTC, such as `2026-10-01T09:00:00Z`. These are **source-document dates**, not the time the file was uploaded or indexed. They are optional in the current API. Missing, null, and empty dates become SQL `NULL` when summaries are stored.

Metadata validation checks JSON shape and selected string fields; it does not strictly validate date formats at upload time. A malformed timestamp can therefore allow registration and then fail during the PostgreSQL timestamp cast in background processing. Supply valid timestamps at ingestion.

### 3.2 Registration and deduplication

Before acknowledging an upload, the API:

1. Sanitizes the filename and creates a document UUID.
2. Saves the original file in the tenant's artifact directory.
3. Validates the file and computes its SHA-256 content hash.
4. Stores the document row and commits it.
5. Schedules background processing and returns the document ID.

Uniqueness is based on `(tenant_id, doc_hash)`. Identical bytes uploaded to the same tenant reuse the original row and preserve its original metadata. Changing only the filename or the metadata does not update the existing document. The same bytes in another tenant create an independent document.

New or unfinished documents return HTTP `202`:

```json
{"document_id": "<uuid>", "tenant_id": "learning-demo", "has_summary": false}
```

A completed duplicate returns `200` and schedules indexing again without regenerating its hierarchy. An unfinished duplicate schedules another processing attempt.

### 3.3 Background processing and artifacts

The ingestion service must run with **one Uvicorn worker**. An `asyncio.Lock` serializes processing for each tenant; blocking OCR, model, and storage work runs in a background thread. Different tenants can have work in progress, while a process-wide lock serializes API-triggered rebuilds of the shared index. A PostgreSQL advisory lock also coordinates index builds from the API and command line.

The default artifact root in the current code is `RAG_medils/ingest/data`, configurable with `INGEST_DATA_ROOT`:

```text
<INGEST_DATA_ROOT>/tenants/<sha256-of-tenant-id>/
├── documents/<document-uuid>/<original-filename>
├── pdf_parsed_output/<document-uuid>/<filename-stem>.md
└── summaries/
    ├── level_0.json
    ├── level_1.json
    └── ...
```

Hashing tenant IDs keeps arbitrary tenant names out of filesystem paths. The document UUID avoids filename collisions; the original filename stem remains available to the chunking rules.

PDFs are posted to `OCR_URL` with `type_name=pdf`; the coordinator reads the returned `content_parsed` Markdown. Markdown uploads bypass OCR. Nonempty parsed Markdown is cached, and writes use a temporary file followed by replacement.

The external OCR implementation uses MinerU's pipeline with automatic PDF parsing and layout-aware Markdown output. Its cleanup removes image references, table-of-contents blocks, and trailing reference sections. This affects the evidence available downstream: the indexed text is the cleaned extraction, while source previews still open the original file. OCR requests use a bounded queue; an overloaded OCR service can return `503`.

### 3.4 Completion and recovery

The coordinator builds a complete representation for the tenant, validates provenance, and stores the summaries transactionally. Summary rows and `has_summary=true` commit together. It then triggers indexing.

**`has_summary=true` confirms PostgreSQL representation storage, not Qdrant readiness.** The current indexing path does not update `documents.index_status` to `indexed`. Confirm search readiness from the indexer log or Qdrant alias/count checks.

Original files and registered metadata survive processing errors. Startup schedules tenants that have unfinished documents. A new or pending upload for a tenant also retries unfinished work. Completed hierarchies can be reused, while uncommitted/corrupt cached output is rebuilt. An indexing-only failure needs an explicit reupload or manual index run; startup recovery is driven by unfinished summarization.

## 4. Hierarchical representation with RAPTOR

Ordinary chunk retrieval is useful for a precise detail. Broader questions may need a representation of a whole section, document, or collection. Our RAPTOR-style representation stores all these levels together so retrieval can match the scale of the question.

```mermaid
flowchart BT
    P1["Passage 1, level 0"] --> C1["Semantic cluster summary"]
    P2["Passage 2, level 0"] --> C1
    P2 --> C2["Overlapping cluster summary"]
    P3["Passage 3, level 0"] --> C2
    C1 --> D1["Document summary A"]
    C2 --> D1
    D1 --> Catalog["Tenant catalog summary"]
    D2["Document summary B"] --> Catalog
```

### 4.1 Passage construction

[`passages/builder.py`](RAG_medils/ingest/representations/passages/builder.py) calls `POST /services/chunking/doc` with:

| Parameter | Value sent by the RAG application |
| --- | --- |
| `min_split_tokens` | `200` |
| `max_split_tokens` | `500` |
| `split_tokens_tolerance` | `50` |
| `window_size` | `5` |

The external chunking service first separates Markdown at headings. Sections that already fit remain intact; longer sections use a semantic rolling-window splitter. BGE-M3 provides the encoder and tokenizer, and the service uses BGE token counts for splitting and reporting. `window_size=5` is a semantic-window setting, not a promise of five overlapping tokens.

The response contains aligned `chunk_list`, `chunk_title`, and `token_count` arrays. Each passage becomes a persisted level-zero node. The active hierarchy builder calls the chunking function directly; it does not require a separate `passages_chunk/` export.

Files whose stems start with `chat-`, `email-`, `event-`, or `note-` follow a special rule: they become a single passage. Content below a threshold of 500 whitespace-separated words is retained. At or above that threshold, Ollama summarizes it with a generation cap of 450 tokens, and that summary becomes the level-zero text. The input threshold in this shortcut is a word-count approximation, unlike the tokenizer-based document chunker. Consequently, level zero is not always a verbatim excerpt for these prefixed files.

### 4.2 Recursive clustering and summarization

For each document, the builder:

1. Embeds passages with the configured dense model, normally BGE-M3. A passage's section title is prepended when available.
2. Keeps those passages as level zero.
3. When a level contains at least 10 nodes, reduces their embeddings with UMAP and fits Gaussian mixture models (GMMs).
4. Selects the number of mixture components using Bayesian information criterion (BIC), with at most eight candidate components.
5. Uses soft membership: a node can contribute to multiple semantic clusters. The builder passes a probability threshold of `0.3`.
6. Applies global clustering and, for sufficiently large groups, local clustering. Small groups and small sample sizes receive explicit fallback handling.
7. Summarizes each cluster with Ollama and embeds its summary to form the next level.
8. Repeats while enough nodes remain, stopping if clustering fails to reduce the node count.
9. Produces one final document summary, then one catalog summary combining the tenant's document summaries.

The catalog occupies one level above the deepest document hierarchy. A document with few passages may go directly from passages to its document summary; level 1 does not always mean a cluster summary. Read both `level` and `scope`.

Summarization prompts ask the model to retain claims, methods, findings, conditions, limitations, and uncertainty, to use only the source content, and to preserve its language. The default model is `qwen3:14b`, with summarization temperature `0.1`.

| Setting | Default | Purpose |
| --- | --- | --- |
| `RAPTOR_MAX_WORKERS` | `2` | Concurrent document/cluster workers; a shared semaphore limits simultaneous summary generations |
| `OLLAMA_NUM_CTX` | `16384` | Summary model context window |
| `OLLAMA_NUM_PREDICT` | `2024` | Summary generation limit |
| `SUMMARY_INPUT_TOKEN_LIMIT` | `13500` | Approximate input budget; oversized groups use recursive batches |
| `EMBEDDING_MODEL` | `bge-m3` | Dense embedding model used inside hierarchy construction |

The input budget plus generation budget must not exceed the configured context window. The builder estimates tokens from UTF-8 byte length; this is a batching heuristic, not exact model tokenization. These context settings belong to summarization; the final answer generator does not explicitly apply the same context-window options.

### 4.3 Identity and provenance

Each node records its text, level, scope, catalog, and source relationships:

| Field | Purpose |
| --- | --- |
| `node_id` | Stable identity within the representation |
| `scope` | `passage`, `document_cluster`, `document`, or `catalog` |
| `document_id` | Registered source document; null for catalog summaries |
| `document_title` | Registered document title; null for catalog summaries |
| `title` | Passage section title, when available; distinct from the document title |
| `catalog_id` | `tenant:<tenant_id>` for API-created representations |
| `source_node_ids` | Immediate lower-level inputs to a summary |
| `source_chunk_ids` | Original level-zero nodes contributing to this node |
| `source_document_ids` | Original documents contributing to this node |
| `source_key`, `chunk_index`, `token_count` | Passage location and size information where applicable |

Passage IDs are derived from the document UUID, chunk position, and content hash. Summary IDs encode document/catalog identity and hierarchy position. Generated `level_*.json` files omit embedding arrays; indexing computes fresh dense and sparse vectors from the stored text.

Before storage, validation checks that references exist, referenced nodes belong to lower levels and the same catalog, source-document/chunk sets agree, and complete document and catalog representations are supplied. Provenance is what lets a retrieved catalog summary still lead back to its original documents.

## 5. PostgreSQL, embeddings, and Qdrant

### 5.1 Why there are three forms of storage

| Storage | What it holds | Why it is needed |
| --- | --- | --- |
| Filesystem | Original files, parsed Markdown, generated hierarchy JSON | Preserve source material, preview originals, and reuse expensive intermediate work |
| PostgreSQL | Document metadata and ownership, hierarchy nodes, accounts, conversations, checkpoints | Transactions, relationships, recovery state, and authoritative ownership checks |
| Qdrant | Dense/sparse vectors and retrieval payloads | Efficient hybrid similarity search with metadata constraints |

The `summaries` SQL table contains **both original passage nodes and generated summaries**. Its name does not imply that every row is a generated summary. The same is true of the Qdrant collection.

Document creation/modification dates live first in `documents.metadata`. During each summary-storage transaction, they are copied into `summaries."createdDateTime"` and `summaries."modifiedDateTime"`, both `TIMESTAMPTZ`, for every document-owned level. Catalog nodes remain undated because they combine multiple documents.

### 5.2 Dense and sparse embeddings

[`embedding_api.py`](RAG_medils/ingest/indexing/embedding_api.py) calls the external vectorizer twice for each indexing input or query:

| Representation | Service model alias | Model in the local registry | Shape / scoring |
| --- | --- | --- | --- |
| Dense | `bge-m3` | `BAAI/bge-m3` | 1,024 floating-point dimensions; normalized vectors and cosine distance |
| Learned sparse | `milco-650m` | `omai-research/milco-650m` | Nonzero `indices` and `values` in a configured 280,524-column space; sparse dot-product scoring |

Dense search represents semantic similarity. Learned sparse search represents weighted vocabulary features and provides another retrieval signal for terms and multilingual matches. The active sparse path uses MILCO; the commented BM25 option in the helper is not active.

The local MILCO registry enables `source_view=true`, retaining both English-pivot and source-language features. The vectorizer selects `encode_query` for queries and `encode_document` for passages. It preserves sparse weight magnitudes rather than applying dense L2 normalization to them.

Indexing sends `input_type="passage"`; retrieval sends `input_type="query"`. These roles must match the model's encoding contract. The RAG index/query helper currently hardcodes BGE-M3, MILCO, and the 1,024-dimensional dense size. Changing only `EMBEDDING_MODEL` changes hierarchy construction, not the final index/query models.

The registry currently limits BGE-M3 inputs to 8,192 tokens and MILCO inputs to 512. Generated summaries can be much longer than passages and may exceed MILCO's input window. A successful embedding request alone does not establish that all summary text was represented; inspect truncation behavior when evaluating this tradeoff.

### 5.3 Qdrant points and payloads

Each SQL node becomes one Qdrant point with named vectors `dense` and `sparse`. Qdrant point UUIDs are deterministically derived from `node_id`.

The payload includes:

```text
node_id, summary_text, level, scope,
document_id, document_title, catalog_id,
createdDateTime, modifiedDateTime,
source_key, chunk_index, title, token_count,
source_node_ids, source_chunk_ids, source_document_ids
```

Timestamps are serialized as timezone-bearing ISO strings. The current indexer creates a keyword payload index on `catalog_id`. Date range filtering is implemented, but explicit Qdrant datetime payload indexes are not currently created. Add them if date-filter performance becomes a bottleneck.

`author` / `doc_author` is absent from this payload list in the current implementation. Arbitrary upload metadata is also not automatically copied into the index.

### 5.4 Validated collection replacement

The active alias is **`summaries_embeddings_live`**. Every index run reads all stored summary rows across tenants and:

1. Acquires a PostgreSQL advisory lock.
2. Creates a new physical collection named `summaries_embeddings_<UTC-timestamp>_<suffix>`.
3. Embeds and uploads every hierarchy node.
4. Checks the exact point count and executes a hybrid smoke query.
5. Switches the live alias to the validated replacement.
6. Deletes unaliased collections matching the generated-name pattern.

A failed candidate build is cleaned up without intentionally deleting the active index. Cleanup rechecks aliases because an activation request can succeed remotely even if its response fails. Empty source data is rejected rather than activating an empty index.

This makes replacement safer, but it is a **full rebuild**, not incremental indexing. Old generated collections are not retained as rollback copies. Disk must temporarily accommodate the old and new collections, and the current indexer builds its text/vector lists for the full corpus in application memory.

## 6. Query rewriting, temporal retrieval, and recency

### 6.1 Structured query analysis

Before retrieval, [`rewrite_query()`](RAG_medils/retrieval_and_generation/generation/generator.py) calls Ollama with temperature `0` and a Pydantic JSON schema:

```json
{
  "query": "Find reports about DNA repair created in October 2026",
  "createdDate_greater_than": "2026-10-01",
  "createdDate_less_than": "2026-10-31"
}
```

This is the query-analysis agent in the application: a structured model call inside the `retrieve` node. It is not a separate looping/tool-using agent. It fixes grammar only when needed and preserves the query's meaning and language.

The key instruction distinguishes **a document's creation date** from **a date mentioned in its subject matter**:

| Question | Intended analysis |
| --- | --- |
| “Find DNA repair reports created in October 2026.” | Creation-date bounds for October |
| “Show documents created on 1 October 2026.” | The same date in both bounds |
| “Find notes created after 1 October.” | A lower bound, interpreted with the schema's inclusive-day semantics |
| “What did the 1998 experiment show?” | No document-creation filter merely because 1998 appears in the topic |
| “Which reports were created last month?” | Resolve relative dates using the backend's current calendar date |

The prompt uses Python `date.today()` on the backend. Configure the backend clock/timezone consistently; it does not receive the browser's timezone. Model interpretation is still a behavior to evaluate, especially for ambiguous “latest,” “after,” or “before” requests. The enforced filter semantics are inclusive calendar-day bounds.

### 6.2 Applying dates before similarity ranking

[`search_summaries()`](RAG_medils/retrieval_and_generation/retrieval/semantic_search.py) always requires the authenticated tenant and constructs:

```text
catalog_id = "tenant:" + authenticated_tenant_id
```

If query analysis supplies either date bound, it adds the following eligibility rule:

```text
same tenant AND (
    createdDateTime falls within the requested range
    OR createdDateTime is missing/null
)
```

The lower bound becomes midnight UTC, inclusive. The upper calendar date becomes midnight UTC of the next day, exclusive. Therefore an October query uses `>= 2026-10-01T00:00:00Z` and `< 2026-11-01T00:00:00Z`, including all of 31 October.

The same filter is attached to **both dense and sparse prefetches and the final fusion query**. Filtering before candidate selection prevents other tenants' documents, or ineligible dated documents, from filling the candidate pool.

Undated nodes deliberately remain eligible. That includes catalog summaries, so this policy is not a strict “every source was created inside this interval” guarantee: a matching undated catalog summary can contain evidence from documents outside the requested range. This is a recall-oriented tradeoff to revisit if strict temporal provenance is required.

### 6.3 Hybrid retrieval and fusion

For requested result count `k`:

1. Embed the rewritten query using BGE-M3 and MILCO.
2. Fetch up to `max(50, 2 × k)` candidates from each named vector.
3. Fuse the ranked results with Qdrant's Reciprocal Rank Fusion (RRF).
4. Request up to the same candidate count from the fused result.
5. Apply the recency adjustment, then take the first `k` nodes.

RRF combines ranking positions from the two retrieval signals rather than directly adding dense and sparse similarity values, whose scales differ.

Retrieval searches the flattened collection of all hierarchy levels. It does not traverse the RAPTOR tree from catalog to document to passage, automatically expand retrieved parents into their children, or guarantee that the top `k` nodes come from different documents.

### 6.4 Recency adjustment

After fusion, results receive a bonus based on **`modifiedDateTime`**:

```text
age_days = (current_time - modification_time) / 86400
recency_bonus = 0.05 × 2 ^ (-age_days / 90)
ordering_score = original_fusion_score + recency_bonus
```

For example, a valid modification date from today adds `0.05`; 90 days old adds `0.025`; 180 days old adds `0.0125`. Missing, invalid, timezone-free, or future modification dates receive no bonus.

This is a freshness boost on top of relevance, not a pure newest-first sort and not a cross-encoder reranker. It runs even when the query has no date filter. The returned point's `score` remains the original Qdrant score; the adjusted score controls ordering but is not written back into that field.

Keep these two operations distinct when debugging:

| Operation | Metadata field | Effect |
| --- | --- | --- |
| Temporal eligibility | `createdDateTime` | Restricts the candidate set, with the undated exception |
| Recency ordering | `modifiedDateTime` | Adjusts relevance ordering among eligible candidates |

## 7. Generation, memory, streaming, and sources

### 7.1 LangGraph state and execution

The graph is deliberately small:

```mermaid
flowchart LR
    START --> Retrieve["retrieve: analyze query + hybrid search + recency"]
    Retrieve --> Generate["generate: context + conversation → Ollama"]
    Generate --> END
```

Its state contains `limit`, `tenant_id`, retrieved `summaries`, and a message list using LangGraph's `add_messages` reducer. `AsyncPostgresSaver` persists checkpoints. A thread key encodes the tenant ID, user ID, and conversation UUID together, so graph memory follows the authorized conversation.

The API extracts the latest user text from the submitted messages and adds that message to the graph. Previous graph messages come from the checkpoint. Generation sees that history; **query rewriting currently sees only the latest user message**, so follow-up retrieval can still be ambiguous even though the final generator understands earlier conversation text.

### 7.2 What the generator receives

The generator defaults to Ollama's `qwen3:14b` at temperature `0`. Its system prompt asks it to use conversation history for follow-ups, ground document answers in the supplied context, and say when the evidence is insufficient.

Each retrieved node is currently formatted as:

```text
summary_text: <retrieved passage or generated summary>
createdDateTime: <date or Unknown>
title_document: <payload.title or Untitled>
doc_author: <payload.doc_author or Unknown>
```

The graph retains the serialized Qdrant payloads, but the generator receives this **selected text projection**, not every payload field. The default context contains three retrieved nodes; `/chat` accepts a limit from 1 to 20.

The intended design is to provide content, dates, document names, and authors so answers can attribute evidence. Two current gaps matter:

- The formatter reads `title`, which is the passage section title. It should use `document_title` for the registered document name. Higher-level nodes often have no passage title and therefore become `Untitled` in the prompt.
- Upload metadata contains `author`, but the current SQL-to-Qdrant path never creates `doc_author`. Newly built payloads therefore produce `Unknown` in this prompt field.

The prompt also does not enforce numbered inline citations or validate each claim against a source. Source navigation is implemented separately and is more deterministic than prose attribution. Do not treat the presence of a source panel as proof that every answer sentence has a validated citation.

### 7.3 Source events and document previews

After retrieval, the API collects `source_document_ids` from the retrieved nodes, removes duplicates, takes at most ten IDs, and looks up those documents in PostgreSQL with the authenticated tenant condition.

It emits `source-document` events containing document ID, media type, registered title, filename, and provider metadata. This path obtains the real title from PostgreSQL, so the UI can show the correct document title even when the generation prompt uses the wrong title field. The source event currently does not include author metadata.

The frontend uses the document ID to request `/api/documents/{id}/content`. FastAPI checks tenant ownership and maps the stored file path under the configured document root. PDFs open in an iframe; Markdown is fetched and rendered in a dialog. Range headers are forwarded for PDF viewers. The preview is of the full original document; there are no page-level highlights or exact cited-span anchors.

### 7.4 Streaming and two kinds of memory

`POST /chat` returns Server-Sent Events in the AI SDK UI-message stream format, including `start`, `source-document`, `text-start`, `text-delta`, `text-end`, `finish`, and the final `[DONE]`. Errors during generation become stream error events. Only tokens from the LangGraph `generate` node are exposed as answer text.

There are two separate persistence mechanisms:

| Mechanism | Purpose |
| --- | --- |
| `conversations` and `chat_messages` | Restore the UI's thread list and message representation, including IDs, parent links, format, and JSON content |
| LangGraph checkpoint tables | Restore the backend graph's state and conversational context |

The UI history adapter explicitly saves messages. Calling `/chat` directly maintains graph memory but does not by itself create the UI's `chat_messages` records. Conversation deletion cascades to those message rows; the current deletion endpoint does not explicitly purge the corresponding LangGraph checkpoints.

## 8. Frontend architecture

The frontend lives in [`rag-chatbot/`](/home/peyzaguirre/notebooks/chat_ui/rag-chatbot). It is a Next.js App Router application with TypeScript and React. The versions below come from the inspected lockfile, not from an assumption about the latest release.

| Technology | Locked version / role |
| --- | --- |
| Next.js | `16.4.2`; routing, server-rendered account gate, and backend proxy routes |
| React / React DOM | `19.3.1`; interactive components and hooks |
| TypeScript | `7.0.2`; typed UI and adapter contracts |
| `@assistant-ui/react` | `0.15.30`; thread UI, composer, message rendering, thread list, and runtime primitives |
| `@assistant-ui/ai-sdk` | `0.0.14`; `AssistantChatTransport` and `useChatRuntime` |
| AI SDK (`ai`) | `7.0.146`; the chat streaming integration used by the transport |
| `assistant-stream` | Local stream construction for generated thread titles |
| Tailwind CSS | `4.3.3`; styling through the PostCSS plugin and utility classes |
| Radix UI | Dialog, tooltip, and other accessible UI primitives |
| Lucide React | Interface icons |
| Markdown renderers / `remark-gfm` | Answer and source rendering, including GitHub-flavored Markdown |
| `class-variance-authority`, utility helpers, animation packages | Shared component variants, class composition, and visual states |

`zod`, `zustand`, and `@ai-sdk/openai` also appear in the dependency manifest. The application's own persistent chat coordination is implemented through the assistant-ui adapters and FastAPI. The active server route forwards chat to the RAG backend; it does not call an OpenAI model, and `OPENAI_API_KEY` is not required for this chat flow.

### 8.1 Pages and components

| File or directory | Responsibility |
| --- | --- |
| `app/layout.tsx` | Root HTML layout and global CSS |
| `app/page.tsx` | Server-side `/auth/me` check; redirects unauthenticated visitors to `/login`; renders the account header and chat |
| `app/login/page.tsx` | Username/password form and login errors |
| `components/chat.tsx` | Runtime provider, thread sidebar, chat area, and initial suggestions |
| `hooks/use-persistent-chat-runtime.ts` | Remote thread-list adapter, history adapter, and streaming transport |
| `components/assistant-ui/thread-list.tsx` | Saved conversations |
| `components/assistant-ui/elements/thread.aui.tsx` | Composer, messages, action controls, and source list |
| `components/assistant-ui/source-document-viewer.tsx` | PDF/Markdown preview dialog |
| `lib/rag-api.ts` | Server-only fetch helper, session cookie, origin checks, response forwarding |
| `app/api/**/route.ts` | Thin routes for auth, chat, conversations, messages, and documents |
| `next.config.js` | Assistant-ui Next integration and package transpilation |

### 8.2 Request path

```mermaid
sequenceDiagram
    participant B as Browser / assistant-ui
    participant N as Next.js server routes
    participant F as FastAPI
    participant G as LangGraph
    participant P as PostgreSQL
    B->>N: POST /api/auth/login
    N->>F: POST /auth/login
    F->>P: Verify user and create session
    F-->>N: Bearer token + expiration
    N-->>B: HttpOnly session cookie
    B->>N: Initialize conversation
    N->>F: POST /conversations + Bearer token
    B->>N: POST /api/chat with conversation ID
    N->>F: Forward authenticated request
    F->>G: Invoke graph for authorized thread
    G-->>F: Retrieved sources and answer tokens
    F-->>N: SSE stream
    N-->>B: Forward stream without buffering
    B->>N: Save message through history adapter
    N->>F: POST /conversations/{id}/messages
    F->>P: Persist UI message
```

The browser calls the same-origin Next.js API routes. Next.js reads the session cookie and adds the Bearer header when calling FastAPI. Backend URLs remain server-side environment variables, so the browser does not need direct access to port 8005.

The proxy forwards cancellation, content type, range requests, and stream-related response headers. It uses no-store caching and returns `502` when it cannot reach FastAPI. Mutating requests must carry an `Origin` matching the UI origin; `APP_ORIGIN` supplies the public origin behind a reverse proxy.

### 8.3 Conversation persistence

The remote thread adapter lists, creates, renames, archives, unarchives, and deletes conversations through the backend. It initializes a saved conversation before chat uses its ID. Titles are derived from the first user message and shortened to 50 characters; no additional LLM title-generation call is needed.

The format-aware history adapter loads saved message JSON and appends/updates messages through the messages endpoint. A `401` during these requests redirects to login. Signing out reloads the page to discard in-memory chat state.

The reusable thread template includes attachment controls and generic tool/reasoning components. **Those controls do not constitute an ingestion UI.** The backend chat handler extracts user text; upload documents through `/ingest` or the Python client. The starter suggestions and page metadata also still contain generic example text.

## 9. Authentication and tenant isolation

There are two different credential types:

| Credential | User of the credential | Storage and lifetime |
| --- | --- | --- |
| Ingestion API key | Upload client or integration | SHA-256 hash in `api_keys`; active flag and permission; no automatic expiration field in the current schema |
| Chat session token | Logged-in user | Random token, SHA-256 hash in `sessions`, eight-hour expiry |

An ingestion key is not a chat login token. Users are assigned directly to a tenant in PostgreSQL and have Argon2 password hashes. The application has no account-registration or tenant-administration UI.

The backend derives ownership from authenticated credentials on every protected request. Tenant members share documents; conversations are private to their user and tenant. Downloads, source lookups, retrieval, history operations, and chat authorization check ownership. The model and request body cannot choose a different tenant.

The browser session cookie is host-only, HttpOnly, and SameSite=Lax. Production adds `Secure`, requiring HTTPS. The token is not returned to browser JavaScript or stored in localStorage. Logout deletes the server session and clears the cookie.

A database trigger revokes a user's sessions when their password hash, tenant assignment, or active status changes. Existing conversations retain their original tenant. Login throttling permits five attempts per username/client address per minute per API process; it is in-memory and resets on restart. With the UI proxy, FastAPI sees the proxy address.

`/health`, API documentation, and the retrieval service's metrics endpoint remain public. The current Compose ports bind to loopback for local use.

## 10. Reproduce the system locally

### 10.1 Prerequisites and topology

Use this topology: **databases and supporting services in Docker; the two application APIs and Next.js on the host**. It matches the current Python package layout and avoids the stale application Dockerfile.

You need:

- Python 3.12 and `uv`; the backend declares Python `>=3.12`, and the inspected environment uses 3.12.3.
- Node.js and npm. The installed Next.js package declares Node `>=20.9.0`; the inspected machine uses Node 26.8.1.
- Docker Engine with Compose, and NVIDIA Container Toolkit for the supplied OCR, chunker, and vectorizer GPU configurations.
- Ollama and the generation model.
- Access to all three service source directories, including the OCR's bundled MinerU code and the vectorizer's `registry.json`.
- Model weights already cached or network access to download them. The initial load can be much slower than later requests.

No fixed minimum GPU-memory figure is established by this project. OCR, chunking, dense/sparse embedding, and the 14B generator compete for memory if they share a device. Start with the supplied concurrency limits and inspect actual memory use.

| Process/service | Host address in this guide | Container address where applicable |
| --- | --- | --- |
| Ingestion API | `127.0.0.1:8009` | Host process |
| Retrieval API | `127.0.0.1:8005` | Host process |
| UI | `127.0.0.1:3005` | Host process |
| PostgreSQL | `127.0.0.1:5433` | `postgres:5432` |
| Qdrant HTTP / gRPC | `127.0.0.1:6337` / `6338` | `qdrant:6333` / `6334` |
| OCR | `127.0.0.1:8084` | `ocr:8084` on `n8n-net` |
| Chunker | `127.0.0.1:8085` | `chunker:8084` on `n8n-net` |
| Vectorizer | `127.0.0.1:8089` | `vectorizer:8089` on `n8n-net` |
| Ollama | `127.0.0.1:11436` | Host process |
| Pushgateway | `127.0.0.1:9093` | `pushgateway:9091` |
| Prometheus / Grafana | `127.0.0.1:9092` / `3004` | Optional; see monitoring notes |

The root Compose API service still publishes port 8004 and references the old application layout. It is not the retrieval process used in this guide. The Docker network is named `n8n-net` because the services are shared with another stack; n8n itself is not required to run this RAG application.

### 10.2 Install the backend and define its environment

```bash
cd /home/peyzaguirre/learning/RAG_medils
uv sync --frozen --no-install-project
cd /home/peyzaguirre/learning
```

Create `RAG_medils/.env.local` with the following development configuration. The database credentials shown are the development defaults already present in Compose; they are not production credentials.

```dotenv
RAG_WORKSPACE=/home/peyzaguirre/learning
RAG_BACKEND=/home/peyzaguirre/learning/RAG_medils
RAG_UI=/home/peyzaguirre/notebooks/chat_ui/rag-chatbot
PYTHONPATH=/home/peyzaguirre/learning:/home/peyzaguirre/learning/RAG_medils

DATABASE_URL=postgresql://raguser:ragpass@127.0.0.1:5433/ragdb
QDRANT_URL=http://127.0.0.1:6337
SUMMARIES_QDRANT_COLLECTION=summaries_embeddings_live

INGEST_DATA_ROOT=/home/peyzaguirre/learning/RAG_medils/ingest/data
OCR_URL=http://127.0.0.1:8084/services/ocr
CHUNKING_URL=http://127.0.0.1:8085
EMBEDDING_URL=http://127.0.0.1:8089/embed
EMBEDDING_MODEL=bge-m3

OLLAMA_BASE_URL=http://127.0.0.1:11436
OLLAMA_GENERATION_MODEL=qwen3:14b
OLLAMA_NUM_CTX=16384
OLLAMA_NUM_PREDICT=2024
SUMMARY_INPUT_TOKEN_LIMIT=13500
RAPTOR_MAX_WORKERS=2
PUSHGATEWAY_URL=http://127.0.0.1:9093

DOCUMENT_PATH_PREFIX=/home/peyzaguirre/learning/RAG_medils/ingest/data
DOCUMENT_ROOT=/home/peyzaguirre/learning/RAG_medils/ingest/data
```

Load this file in **every shell used for backend commands**:

```bash
cd /home/peyzaguirre/learning
set -a
source RAG_medils/.env.local
set +a
```

The active backend modules read `os.getenv`; they do not automatically load this file. `PYTHONPATH` includes both roots because some current modules still import `metrics` as a top-level module. Use fully qualified `RAG_medils...` entry points to avoid loading the same code under different module names.

Set `DATABASE_URL` explicitly for both APIs. The ingestion stores also support individual `POSTGRES_*` variables, while the retrieval API reads `DATABASE_URL` directly. Similarly, explicitly setting `OLLAMA_BASE_URL` avoids the differing fallback ports in older passage helpers.

`DOCUMENT_PATH_PREFIX` is the prefix recorded in PostgreSQL's original file paths; `DOCUMENT_ROOT` is where those files are accessible to the retrieval process. They are identical for this host deployment. When moving documents into a container, map the stored host prefix to the mounted container root. Without these settings, the retrieval API's current default root points inside `retrieval_and_generation/`, and source previews of newly ingested files can return 404.

### 10.3 Start PostgreSQL, Qdrant, and the supporting services

Create the shared network only if it does not exist:

```bash
docker network inspect n8n-net >/dev/null 2>&1 || docker network create n8n-net

cd /home/peyzaguirre/learning/RAG_medils
docker compose up -d postgres qdrant pushgateway
docker compose exec -T postgres pg_isready -U raguser -d ragdb
curl --fail http://127.0.0.1:6337/collections
```

On a machine where the shared services are already running, check their health and reuse them. On a fresh machine with the service sources and GPU runtime prepared:

```bash
cd /srv/iarag/services/ocr
docker compose up -d --build

cd /srv/iarag/services/chunking
docker compose up -d --build

cd /srv/iarag/services/vectorizer
docker compose up -d --build
```

The chunker and vectorizer Compose files mount `/srv/iarag/services/vectorizer/cache`; update these absolute mount paths if relocating the services. The vectorizer registry must contain `bge-m3` and `milco-650m`. Its general registry response can mention another default store; the RAG application requests explicit models and writes the returned vectors to Qdrant itself.

```bash
curl --fail http://127.0.0.1:8084/health
curl --fail http://127.0.0.1:8085/health
curl --fail http://127.0.0.1:8089/health
curl --fail http://127.0.0.1:8089/models
```

The OCR service downloads MinerU weights lazily. Its local [service README](/srv/iarag/services/ocr/README.md) documents model preloading and alternative local execution. The [chunking README](/srv/iarag/services/chunking/README.md) documents its API and tokenizer behavior; the [vectorizer README](/srv/iarag/services/vectorizer/README.md) explains its shared registry.

### 10.4 Start Ollama and verify the model endpoints

If an Ollama instance already serves port 11436, reuse it. Otherwise start it in a dedicated terminal:

```bash
OLLAMA_HOST=127.0.0.1:11436 ollama serve
```

In another terminal:

```bash
OLLAMA_HOST=127.0.0.1:11436 ollama pull qwen3:14b
curl --fail http://127.0.0.1:11436/api/tags
```

Check both embedding contracts before uploading a large document:

```bash
curl --fail-with-body http://127.0.0.1:8089/embed \
  -H 'Content-Type: application/json' \
  -d '{"texts":["DNA repair experiment"],"model":"bge-m3","input_type":"passage","normalize":true}'

curl --fail-with-body http://127.0.0.1:8089/embed \
  -H 'Content-Type: application/json' \
  -d '{"texts":["DNA repair experiment"],"model":"milco-650m","input_type":"query","normalize":true}'
```

Expect `kind="dense"` with one 1,024-value embedding in the first response, and `kind="sparse"` with one `indices`/`values` entry in the second. A health check alone does not verify model loading or successful encoding.

### 10.5 Provision an ingestion key and start ingestion

From `learning/`, with the backend environment loaded:

```bash
"$RAG_BACKEND/.venv/bin/python" - <<'PY'
from RAG_medils.ingest.create_table import create_api_keys_table, add_client

create_api_keys_table()
add_client("learning-demo")
PY
```

Save the newly printed key. Only its hash is stored. Repeating the helper for the same tenant/name does not issue or recover another key. This helper creates the ingestion credential; the chat account is created separately below.

Start the ingestion API in its own terminal:

```bash
cd "$RAG_WORKSPACE"
"$RAG_BACKEND/.venv/bin/python" -m uvicorn RAG_medils.ingest.api:app \
  --host 127.0.0.1 --port 8009 --workers 1
```

Startup creates missing current document/summary tables and schedules unfinished work. It does not provide a general migration system for older table layouts.

```bash
curl --fail http://127.0.0.1:8009/health
```

### 10.6 Ingest a small document and confirm indexing

In the client terminal, load the backend environment and enter the key without putting its value in shell history:

```bash
read -rsp 'Ingestion API key: ' INGEST_API_KEY
printf '\n'
export INGEST_API_KEY

cat > /tmp/rag-learning-demo.md <<'MD'
# DNA repair experiment

The team compared an untreated control with a treated sample.
The treated sample showed increased repair activity under the tested conditions.
This observation does not establish how the treatment behaves outside those conditions.
MD

"$RAG_BACKEND/.venv/bin/python" "$RAG_WORKSPACE/python_client/ingestion_client.py" \
  /tmp/rag-learning-demo.md \
  --metadata '{"title":"DNA repair learning example","author":"Research team","createdDateTime":"2026-10-01T09:00:00Z","modifiedDateTime":"2026-10-20T15:30:00Z"}'
```

This example exercises Markdown chunking, hierarchy creation, storage, and both embedding paths. To exercise OCR as well, upload a real PDF using the same client or curl:

```bash
curl --fail-with-body http://127.0.0.1:8009/ingest \
  -H "Authorization: Bearer $INGEST_API_KEY" \
  -F 'file=@/path/to/paper.pdf' \
  -F 'metadata={"title":"Example paper","author":"Research team","createdDateTime":"2026-10-01T09:00:00Z","modifiedDateTime":"2026-10-20T15:30:00Z"}'
```

Replace the following UUID with the upload response value:

```bash
DOCUMENT_ID='<document UUID>'
"$RAG_BACKEND/.venv/bin/python" "$RAG_WORKSPACE/python_client/ingestion_status.py" "$DOCUMENT_ID"

curl --fail http://127.0.0.1:6337/aliases
curl --fail-with-body http://127.0.0.1:6337/collections/summaries_embeddings_live/points/count \
  -H 'Content-Type: application/json' \
  -d '{"exact":true,"filter":{"must":[{"key":"catalog_id","match":{"value":"tenant:learning-demo"}}]}}'
```

Wait for summary completion **and** index activation. Before the first successful build, the alias does not exist. A single short demo document usually yields a passage, a document summary, and a catalog summary; larger documents create more nodes.

The client also accepts directories and sends one request per PDF/Markdown file. A single `--metadata` object is applied to every file in that invocation, so upload separately when dates or authors differ. Explicitly set `INGEST_API_KEY`: the current example clients contain a historical hardcoded fallback that should be removed before distributing them.

### 10.7 Start retrieval and create a chat user

In another terminal, load the same backend environment, then:

```bash
cd "$RAG_WORKSPACE"
"$RAG_BACKEND/.venv/bin/python" -m uvicorn RAG_medils.retrieval_and_generation.api:app \
  --host 127.0.0.1 --port 8005
```

Retrieval startup creates the application/auth tables, imports existing ingestion tenants, and initializes LangGraph checkpoint tables. PostgreSQL and Qdrant must be reachable. Retrieval itself needs the populated live alias.

Generate an Argon2 password hash using the interactive helper:

```bash
"$RAG_BACKEND/.venv/bin/python" -m RAG_medils.retrieval_and_generation.hash_password
```

Open a database prompt:

```bash
cd "$RAG_BACKEND"
docker compose exec postgres psql -U raguser -d ragdb
```

Run this SQL, replacing the hash placeholder with the helper's output and choosing a unique username:

```sql
INSERT INTO tenants (id) VALUES ('learning-demo') ON CONFLICT DO NOTHING;

INSERT INTO users (username, password_hash, tenant_id)
VALUES ('researcher', '<Argon2 hash from helper>', 'learning-demo');
```

The tenant string must match the ingestion key's tenant. A successful login to another tenant will not expose these documents. Usernames are case-sensitive.

### 10.8 Install and start the UI

```bash
cd /home/peyzaguirre/notebooks/chat_ui/rag-chatbot
npm ci
```

Create or update `.env.local`, preserving other local settings if it already exists:

```dotenv
RAG_API_URL=http://127.0.0.1:8005/chat
RAG_API_BASE_URL=http://127.0.0.1:8005
```

Start the UI:

```bash
npm run dev -- --hostname 127.0.0.1 --port 3005
```

Open `http://127.0.0.1:3005`, sign in with the PostgreSQL account, and ask:

> What did the DNA repair experiment report? Use documents created in October 2026.

Confirm that an answer streams, the source appears, and clicking it opens the Markdown original. Reload the page and reopen the conversation to check history persistence. Then upload a PDF and repeat the source-preview check.

For the production-mode frontend build:

```bash
npx tsc --noEmit
npm run build
npm run start -- --hostname 127.0.0.1 --port 3005
```

Production login requires an HTTPS public origin because its cookie is Secure. Put the UI behind an HTTPS reverse proxy and set `APP_ORIGIN=https://your-public-host` without a trailing slash. The proxy must preserve streaming; a successful build alone does not configure hosting, process supervision, or TLS.

## 11. API reference and direct chat example

Swagger/OpenAPI is available at `http://127.0.0.1:8009/docs` for ingestion and `http://127.0.0.1:8005/docs` for retrieval. The current active routes are:

| Service | Method and path | Purpose |
| --- | --- | --- |
| Ingestion | `GET /health` | Liveness |
| Ingestion | `POST /ingest` | Register a file and schedule processing; ingestion/admin key |
| Ingestion | `GET /ingest/{document_id}` | Tenant-scoped summary status; active ingestion API key |
| Retrieval | `GET /health` | Liveness |
| Retrieval | `POST /auth/login` | Username/password → eight-hour Bearer session |
| Retrieval | `GET /auth/me` | Current user and tenant |
| Retrieval | `POST /auth/logout` | Revoke session; returns 204 |
| Retrieval | `POST /retrieve` | Query analysis and ranked Qdrant points, without answer generation |
| Retrieval | `POST /chat` | Authorized conversation → streamed answer and sources |
| Retrieval | `GET`, `POST /conversations` | List or create owned conversations |
| Retrieval | `GET`, `PATCH`, `DELETE /conversations/{id}` | Read, rename/archive, or delete an owned conversation |
| Retrieval | `GET`, `POST /conversations/{id}/messages` | Load or save UI messages |
| Retrieval | `GET /documents/{id}/content` | Tenant-owned original PDF/Markdown |
| Retrieval | `/metrics/` | Prometheus exposition |

`/retrieve` accepts `{"query":"...","limit":3}` and returns a JSON array of Qdrant scored points with payloads. Its default limit is 3, with a minimum of 1. `/chat` also defaults to 3 and caps the limit at 20. Neither endpoint accepts a caller-selected tenant.

The following Python example prompts for a password, logs in, inspects retrieval, creates an owned conversation, and prints its SSE stream. Run from `learning/` with the backend environment loaded:

```bash
"$RAG_BACKEND/.venv/bin/python" - <<'PY'
import getpass
import json
import requests

base = "http://127.0.0.1:8005"
with requests.Session() as session:
    response = session.post(
        f"{base}/auth/login",
        json={"username": "researcher", "password": getpass.getpass("Password: ")},
        timeout=30,
    )
    response.raise_for_status()
    session.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

    question = "What did the DNA repair experiment report? Use documents created in October 2026."
    response = session.post(f"{base}/retrieve", json={"query": question, "limit": 3}, timeout=600)
    response.raise_for_status()
    for point in response.json():
        payload = point["payload"]
        print(json.dumps({key: payload.get(key) for key in (
            "node_id", "scope", "document_title", "createdDateTime", "modifiedDateTime"
        )}, indent=2))

    response = session.post(f"{base}/conversations", timeout=30)
    response.raise_for_status()
    conversation_id = response.json()["id"]
    with session.post(
        f"{base}/chat",
        json={
            "id": conversation_id,
            "messages": [{"role": "user", "parts": [{"type": "text", "text": question}]}],
            "limit": 3,
        },
        stream=True,
        timeout=(10, 600),
    ) as stream:
        stream.raise_for_status()
        for line in stream.iter_lines(decode_unicode=True):
            if line:
                print(line)
    session.post(f"{base}/auth/logout", timeout=30).raise_for_status()
PY
```

This demonstrates the API contract; the UI additionally saves message history through its adapter. A malformed/missing conversation ID is rejected before chat streaming. Unauthorized or nonexistent documents/conversations return 404; invalid or expired sessions return 401.

## 12. Operations, monitoring, and recovery

### 12.1 Manual rebuilding and standalone representations

After an indexing-only failure, rerun the index from the current PostgreSQL summaries:

```bash
cd "$RAG_WORKSPACE"
"$RAG_BACKEND/.venv/bin/python" -m RAG_medils.ingest.indexing.main
```

This rebuilds the shared index for all stored tenants, switches the live alias after validation, and deletes obsolete generated collections. It is an operational rebuild, not a read-only diagnostic.

For an isolated representation experiment with existing Markdown:

```bash
cd "$RAG_WORKSPACE"
"$RAG_BACKEND/.venv/bin/python" -m RAG_medils.ingest.representations.main \
  --data-dir /path/to/experiment --no-metrics
```

Place inputs under `/path/to/experiment/pdf_parsed_output/`. The command creates `/path/to/experiment/summaries/level_*.json`; it does not upload/register documents, convert PDFs, store them in PostgreSQL, or index them. Default standalone IDs/catalogs differ from the authenticated upload path. Use `/ingest` for the reproducible application workflow.

Resume is the representation CLI default. `--clean` deletes the selected root's generated `summaries/` before rebuilding, so use it only when intending to regenerate those artifacts. It does not delete parsed Markdown.

### 12.2 Observability

The backend exposes:

| Metric | Meaning |
| --- | --- |
| `rag_retrieval_duration_seconds` | Histogram for search, including query embedding, Qdrant retrieval, and recency ordering; excludes the preceding query-analysis model call |
| `rag_process_document_count` | Source-document count for a completed batch process |
| `rag_process_item_count` | Native artifact counts, labeled by process, representation, and item type |
| `rag_process_duration_seconds` | Duration of a completed batch process |

Representation and indexing jobs push batch metrics to Pushgateway. Metric-publication failures log warnings and do not invalidate otherwise completed work. These gauges describe the latest pushed run; they are not a durable per-document job history.

The provisioned Grafana dashboard is **RAG Pipeline Report**. Optional monitoring containers can be started without the stale API dependency:

```bash
cd "$RAG_BACKEND"
docker compose up -d --no-deps pushgateway prometheus grafana
```

Grafana is on port 3004; Prometheus is on 9092. The supplied Prometheus configuration can scrape Pushgateway on the Compose network. Its online API target is still `api-medils:8000`, which does not describe the host API in this guide. Batch metrics and live retrieval metrics therefore need to be considered separately.

To collect host API metrics, configure Prometheus with a network route to the host retrieval process and update its target. A container's `127.0.0.1` is not the host's loopback interface. One local Linux option is to run Prometheus with host networking and a configuration targeting `127.0.0.1:8005` and `127.0.0.1:9093`, then point Grafana's datasource at that Prometheus instance. The existing Compose file does not configure this variant automatically.

### 12.3 Troubleshooting

| Symptom | What to inspect |
| --- | --- |
| `ModuleNotFoundError` on startup | Run from `learning/`, load the documented `PYTHONPATH`, and use the fully qualified module paths. Older `ingest.api`, `indexing.main`, and root `api:app` commands refer to different layouts. |
| Upload returns 401 / 403 | Use the ingestion key, check its active flag and `ingest`/`admin` permission; a chat session is a different credential. |
| `has_summary` stays false | Read ingestion logs; check OCR/chunker/vectorizer/Ollama availability, malformed dates, and file paths. The status endpoint does not expose the underlying error. |
| Summary complete but no search result | Check alias activation and indexing logs, then verify the authenticated tenant's catalog. Retry indexing if needed. |
| Missing `summaries_embeddings_live` | Complete one successful ingestion/index build; an empty database cannot activate an index. |
| Source is listed but preview returns 404 | Check tenant ownership, stored `doc_path`, actual file presence, and `DOCUMENT_PATH_PREFIX` / `DOCUMENT_ROOT`. |
| Temporal results include undated content | This is the current filter policy, including catalog summaries; inspect `scope` and provenance. |
| Results appear out of score order | Recency changes ordering without changing the point's reported Qdrant score. |
| Author is `Unknown` or a heading appears as the document name | Current payload/prompt mapping gaps described in section 7. |
| GPU out-of-memory or long first request | Check model residency and concurrent OCR, chunking, embedding, and Ollama activity; lower `RAPTOR_MAX_WORKERS` and inspect service logs. |
| UI returns 502 | Check the retrieval process and server-side `RAG_API_*` settings. |
| UI mutation returns 403 | Check the browser Origin and configured `APP_ORIGIN`, especially behind a proxy. |
| Production login does not persist | Verify HTTPS and Secure-cookie handling. |
| Docker application build fails at `COPY api.py` | The backend Dockerfile still references the pre-reorganization tree; use the host application launch commands. |

### 12.4 What to retain for reproduction

Preserve the backend `uv.lock`, frontend `package-lock.json`, service source/configuration, vectorizer model registry, model versions/caches, and the original metadata. The lockfiles fix application dependencies more closely than broad package ranges, but several container images use `latest`, and model revisions are not comprehensively pinned. Reproduction of architecture is therefore stronger than a guarantee of byte-identical generated summaries.

Back up PostgreSQL and original-file storage together: database paths alone cannot restore source previews. Qdrant can be rebuilt from stored summaries and matching embedding services. Generated Markdown and hierarchy files save recomputation. Preserve checkpoint tables if graph conversation memory matters. Docker named volumes retain database state across ordinary container restarts; `docker compose down -v` removes those volumes.

## 13. Verification and evaluation

### 13.1 Test the layers separately

Useful validation covers registration, metadata/provenance, tenant isolation, date boundaries, ranking, stream events, and source access. Model output quality requires a separate evaluation; passing API tests does not measure answer accuracy.

The following existing suites exercise processing and representation validation without requiring a real corpus. Run them in separate Python processes to avoid mixing legacy module imports. Point service settings at closed local ports so an unexpectedly unmocked dependency fails instead of reaching a working application:

```bash
cd /home/peyzaguirre/learning
for suite in test_ingest_processing.py test_stores_raptor.py test_auth_integration.py; do
  RUN_POSTGRES_TESTS=0 \
  DATABASE_URL=postgresql://unused:unused@127.0.0.1:1/no_live_database \
  QDRANT_URL=http://127.0.0.1:1 \
  OLLAMA_BASE_URL=http://127.0.0.1:1 \
  EMBEDDING_URL=http://127.0.0.1:1/embed \
  PYTHONPATH="$PWD:$PWD/RAG_medils" \
  RAG_medils/.venv/bin/python -m unittest discover \
    -s RAG_medils/tests -p "$suite" -v || break
done
```

In `test_auth_integration.py`, this runs the in-memory tenant/date hybrid-search test and skips the PostgreSQL-dependent tests. Those database tests require `RUN_POSTGRES_TESTS=1` and a disposable PostgreSQL database; the current auth suite creates temporary schemas and uses mocked model calls. Review integration-test patches before enabling them after any package reorganization.

### 13.2 Documentation-time verification status

The inspection used the existing environment; it did not install a fresh stack or establish a clean-machine end-to-end run. Results from the targeted existing tests were:

| Suite | Observed result |
| --- | --- |
| `test_ingest_processing.py` | 14 passed |
| `test_stores_raptor.py` | 11 passed |
| `test_auth_integration.py` | In-memory hybrid tenant/date test passed; 9 database tests skipped |
| `test_retrieval_integration.py` | Four subtest failures: an old assertion expects Qdrant `limit=7`, while the implemented candidate pool is 50 before final truncation |
| `test_ingest_api.py` | 5 failures and 4 errors: mocks still target `ingest.api` while tests import `RAG_medils.ingest.api` |

Do not run the stale ingestion API suite against a working database: its mismatched mock targets can execute real registration and background processing. It needs its patch/logger targets aligned with the imported package. Broad test discovery also includes earlier experiments whose modules have moved or been removed. The full test suite is not currently green.

For the frontend, the existing project checks are `npx tsc --noEmit` and `npm run build`. The documentation update did not change frontend code or rerun its build.

### 13.3 Retrieval and answer evaluation

The workspace includes `evaluation/retrieval_metrics_all.py`, human-evidence question sets, cached judgments, and historical JSON/CSV outputs. That script belongs to an earlier API contract: it defaults to `/v1/query`, submits a `question` field, and expects the old response structure. The current API requires authentication, accepts `query` at `/retrieve`, and returns a point array. Changing only the URL is insufficient.

Before using that evaluator for this implementation, adapt login/Bearer handling, the request body, point-payload extraction, and the result schema. Do not present old benchmark files as measurements of the current system without rerunning a compatible evaluation.

A useful evaluation set should include:

- Precise passage questions and broader document/catalog questions.
- Questions with no temporal requirement, one-sided dates, a single day, and inclusive end-date boundaries.
- Dates in subject matter that must not become document-creation filters.
- Undated documents and catalog summaries, making their eligibility policy explicit.
- Documents with old, recent, invalid, missing, and future modification times.
- Same-tenant and cross-tenant retrieval/download/history checks.
- Follow-ups that require conversation context during retrieval.
- Evidence sufficiency, answer faithfulness, source-title/author accuracy, and citation coverage.

Retrieval metrics such as recall, MRR, MAP, and nDCG address evidence ranking. Answer grounding and citation correctness need their own checks. Compare dense-only, sparse-only, fused, and fused-plus-recency behavior on the same questions before attributing improvements to a particular stage.

## 14. Current limits and next improvements

These are concrete boundaries of the inspected implementation, rather than claims that the pipeline lacks an end-to-end path:

1. **Complete attribution metadata.** Join document author metadata into indexable rows, include a consistent author field in Qdrant, rebuild the index, use `document_title` in generation, and carry author data into source events/UI where desired. Catalogs need multiple-source attribution rather than one invented author/title.
2. **Make inline citations explicit.** Give context items stable source labels and require/validate references in generated answers. The existing document links provide provenance navigation but not sentence-level citation verification.
3. **Align deployment and tests with the package layout.** Update the backend Dockerfile/Compose application entry points, old imports/mocks, monitoring scrape target, and evaluation adapter. Preserve the host startup sequence until the container path is verified.
4. **Expose reliable processing status.** Add durable stage/error/index status and retries beyond the current `has_summary` flag and process-local background tasks. Avoid scaling ingestion workers until tenant scheduling is coordinated across processes.
5. **Clarify temporal policy.** Decide whether strict temporal searches should exclude undated nodes or constrain all source dates of catalog summaries. Add datetime payload indexes and structured date validation as the corpus grows.
6. **Manage embedding and context budgets.** Account for MILCO's shorter window, batch index inputs at the application level, bound final generation context/history, and measure how much source content survives each summarization stage.
7. **Improve retrieval diversity and follow-ups.** Use conversation-aware rewriting where needed; consider deduplication across hierarchy levels or source expansion when multiple retrieved nodes repeat the same evidence.
8. **Finish the application lifecycle.** Connect upload UI if desired, replace template suggestions/page metadata, remove the clients' historical key fallback, and define deletion/retention across files, SQL rows, Qdrant, and graph checkpoints.

The main lesson of this project is that RAG quality depends on the whole path. Good embeddings cannot repair lost metadata, a correct date parser cannot repair missing payload dates, and a fluent answer cannot replace traceable evidence. Keeping each transformation observable and reproducible makes the system understandable enough to improve deliberately.
