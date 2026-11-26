# Hierarchical-Summary RAG on an Enterprise Corpus

This repository evaluates a Retrieval-Augmented Generation (RAG) system that uses RAPTOR-style hierarchical summaries [1]. The system is tested on a controlled, enterprise-like corpus. The existing pipeline is reused without architectural changes: hierarchical representations, PostgreSQL storage, hybrid dense–sparse retrieval in Qdrant, LangGraph orchestration, and a Next.js chat interface. Only corpus ingestion and evaluation are new. The work has two objectives:

1. **Retrieval evaluation.** Measure document-level and evidence-level retrieval quality over the full corpus, using a fixed benchmark of questions.
2. **Conversational access.** Serve the same index through the chat interface.

## 1. Corpus and benchmark

| Resource | Description |
| --- | --- |
| `data/*.json` | 6,142 pre-parsed records in six types: `document` (1,925), `email` (1,817), `chat` (846), `note` (777), `event` (399), `task` (378). Records are mostly Spanish. Each has `id`, `type`, `title`, `language`, `tags`, `related`, `metadata`, and `content`. No OCR is required. |
| `evaluation/questions_easy.json` | 558 English questions (a cross-lingual setting). Each has a reference answer, `relevant_doc_ids`, and, for 398 questions, gold `evidence` text spans. The remaining 160 questions have computed answers with no verbatim span. |

Both resources are distributed separately and are excluded from version control.

## 2. Method

### 2.1 Representation by record type

| Record type | Representation |
| --- | --- |
| `document` | RAPTOR hierarchy. Semantic chunks (200–500 tokens) form level 0. Levels with at least 10 nodes are clustered by UMAP + GMM soft clustering and summarized recursively. Each document then receives one document-level summary. |
| `chat` | All messages are concatenated into a single document, one line per message in the form `[HH:MM] Author: message`, and processed with the same RAPTOR hierarchy. |
| `email`, `event`, `note`, `task` | One independent unit per record, with no hierarchical summaries. The record metadata is serialized as a plain-text header and prepended to the body (example below). Units longer than 500 words are condensed into a single summary so they fit the embedding input limit. |

A single catalog summary, built from all document-level summaries, forms the top level of the corpus hierarchy.

Example of a serialized email unit:

```
ID: email1327
Type: email
Title: AVISO: Su buzón ha superado el límite de almacenamiento
Language: es
Tags: Email
Created Date: 2024-02-16T09:00:00Z
From: Administrador del Webmail (admin@webmail-soporte-cuota.info)
To: Elena Villegas Carmona (elena.villegas@urbeterra.es)
Thread ID: thread-email1327
Body:
Estimada usuaria: ...
```

### 2.2 Metadata and provenance

Chunks and single-document summaries keep their source record's metadata in the Qdrant payload: `dataset_id`, `doc_type`, `language`, `tags`, `doc_author`, `createdDateTime`, and the full `metadata` object. The catalog summary spans many documents, so it carries no document metadata. Instead it keeps provenance (`source_document_ids`, `source_dataset_ids`, `source_chunk_ids`). The existing provenance validation is unchanged, except that a single passage with no summaries is now accepted as a complete unit.

### 2.3 Retrieval

Query rewriting is disabled, so each question is searched verbatim, with no date filters. Retrieval is hybrid: dense `bge-m3` and sparse `milco-650m` vectors are fused with Reciprocal Rank Fusion (RRF), with a small recency bonus (at most 0.05). All levels of the hierarchy are indexed in one collection, so a query can match a chunk or a summary.

## 3. Evaluation protocol

Each question is issued verbatim and the top *k* = 10 retrieved nodes are scored.

**Document-level metrics.** Each node is mapped to its record id: chunks and single-document summaries map to their own `dataset_id`. Duplicate ids are removed in rank order. The catalog node covers the whole corpus and is not attributable to one record, so it is excluded from the ranking and its retrieval rate is reported separately. Relevance is binary with respect to `relevant_doc_ids`. All 558 questions are scored.

| Metric | Definition |
| --- | --- |
| Hit@10 | 1 if any relevant record is in the top 10 |
| Recall@10 | fraction of relevant records found in the top 10 |
| MRR@10 | reciprocal rank of the first relevant record |
| MAP@10 | average precision at the relevant ranks, normalized by the number of relevant records |
| nDCG@10 | DCG with log₂ discount, normalized by the ideal DCG |

**Evidence-level metrics.** A gold `evidence.text` span is *found* if it appears as a substring of a retrieved node's text. Before matching, both texts are case-folded, whitespace is collapsed, and `**` is removed. For independent units the full serialized record is used, since over-limit units are stored as summaries. Text Evidence Recall@10 is the fraction of a question's spans that are found. Text Evidence Hit@10 indicates whether at least one span is found. Only the 398 questions with spans are scored. A lenient variant (`*_via_sources`) also matches against the source chunks of retrieved summaries.

Scores are averaged over questions. Each run writes `summary.json` (overall results, and breakdowns by retrieval type, reasoning type, and relevant record type) and `per_question.jsonl` to `evaluation/results/<timestamp>/`.

Answer correctness is not evaluated. The metrics measure retrieval only.

## 4. Reproduction

### 4.1 Services

| Service | Default address |
| --- | --- |
| PostgreSQL 16 | `127.0.0.1:5433` |
| Qdrant | `127.0.0.1:6337` |
| Ollama, `qwen3:14b` (summarization and generation) | `127.0.0.1:11436` |
| Embedding service (`bge-m3`, `milco-650m`) | `127.0.0.1:8089` |
| Semantic chunking service | `127.0.0.1:8085` |
| Retrieval and chat API (FastAPI) | `127.0.0.1:8005` |
| Chat UI (Next.js) | `127.0.0.1:3007` |

### 4.2 Experiment CLI

Run all commands from the directory that contains `RAG_medils/`, using the project's virtual environment.

```bash
python -m RAG_medils.experiment ingest   [--types document,chat,...] [--limit N] [--workers N] [--resume | --clean]
python -m RAG_medils.experiment index    # rebuild the Qdrant collection from PostgreSQL
python -m RAG_medils.experiment evaluate [--questions PATH] [--k 10] [--limit-questions N]
python -m RAG_medils.experiment run      # ingest, index, evaluate
python -m RAG_medils.experiment create-user USERNAME   # chat UI account for the tenant
```

- Records are ingested into the tenant `company_benchmark`; change it with `--tenant`.
- Each processed record is checkpointed, so interrupted runs resume where they stopped.
- The catalog summary is built once, after all records are processed. The complete catalog is then written to PostgreSQL in a single transaction.
- Failed records are listed in `failures.json` and retried on the next run.
- Runtime is dominated by LLM summarization and takes several hours for the full corpus with two workers (`RAPTOR_MAX_WORKERS`). Run it in the background:

```bash
nohup python -u -m RAG_medils.experiment run > run.log 2>&1 &
```

### 4.3 Chat interface

After indexing, start the API, then the UI (`npx next dev -H 127.0.0.1 -p 3007` in the UI project). Log in with an account created by `create-user`.

```bash
DOCUMENT_PATH_PREFIX=$PWD/RAG_medils/ingest/data \
  python -m uvicorn RAG_medils.retrieval_and_generation.api:app --host 127.0.0.1 --port 8005
```

`DOCUMENT_PATH_PREFIX` lets the interface open source documents. `QUERY_REWRITE_ENABLED=true` restores LLM query rewriting.

## 5. Repository layout

| Path | Content |
| --- | --- |
| `experiment/` | CLI, resumable corpus ingestion, retrieval evaluation |
| `ingest/corpus/` | Record loading, serialization, per-type routing |
| `ingest/representations/` | Chunking and RAPTOR hierarchy construction |
| `ingest/stores/`, `ingest/indexing/` | PostgreSQL persistence and Qdrant indexing |
| `retrieval_and_generation/` | Hybrid search, LangGraph workflow, chat API |
| `tests/` | Unit tests (`python -m unittest RAG_medils/tests/<module>.py`) |

## 6. Limitations

- Each question has a single gold relevant record. Records that are needed only to compute an answer (`answer_doc_ids`) do not count as relevant.
- Summaries are produced by an LLM and may be written in English for Spanish sources. The independent units longer than 500 words (about 2% of them) are stored as summaries, not verbatim text.
- One catalog summary spans the whole corpus. It is frequently retrieved, but it cannot be attributed to individual records.

## References

[1] P. Sarthi, S. Abdullah, A. Tuli, S. Khanna, A. Goldie, and C. D. Manning. "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval." *ICLR*, 2024.
