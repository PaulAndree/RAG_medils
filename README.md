# Hierarchical-Summary RAG on an Enterprise Corpus

This repository evaluates a Retrieval-Augmented Generation (RAG) system that uses RAPTOR-style hierarchical summaries [1]. The system is tested on a controlled, enterprise-like corpus. The existing pipeline is reused without architectural changes: hierarchical representations, PostgreSQL storage, hybrid dense–sparse retrieval in Qdrant, LangGraph orchestration, and a Next.js chat interface. Only corpus ingestion and evaluation are new. The work has two objectives:

1. **Retrieval evaluation.** Measure document-level and evidence-level retrieval quality over the full corpus, using a fixed benchmark of questions.
2. **Conversational access.** Serve the same index through the chat interface.

## 1. Corpus and benchmark

| Resource | Description |
| --- | --- |
| `data/*.json` | 6,142 pre-parsed records in six types: `document` (1,925), `email` (1,817), `chat` (846), `note` (777), `event` (399), `task` (378). Records are mostly Spanish. Each has `id`, `type`, `title`, `language`, `tags`, `related`, `metadata`, and `content`. No OCR is required. |
| `evaluation/questions_easy.json` | 578 English questions (a cross-lingual setting), all answerable from content text. Each question lists the **facts** its answer needs (962 in total). Each fact lists every place that states it (`alternatives`: a `doc_id` and, for text alternatives, the exact span). |

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

Each question is issued verbatim and the top *k* = 10 retrieved nodes are scored. Ten nodes cover 7.9 distinct records on average.

**Document-level metrics.** Each node is mapped to its record id, and duplicate ids are removed in rank order. The catalog node covers the whole corpus and is not attributable to one record, so it is excluded from the ranking. Any `doc_id` among a question's alternatives is relevant. Alternatives are unordered and equivalent, so retrieving one of them suffices.

| Metric | Definition |
| --- | --- |
| Hit@10 | 1 if any relevant record is in the top 10 |
| MRR@10 | reciprocal rank of the first relevant record |
| nDCG@10 | binary DCG with the ideal ranking taken as one relevant record at rank 1, i.e. 1/log₂(rank + 1) of the first hit |

Document recall and MAP are not reported. Both divide by the number of relevant records, which varies from 1 to 859 per question, so they would penalize redundancy rather than retrieval quality.

**Evidence-level metrics.** A fact is *found* if the `text` of any of its alternatives occurs in the text of a retrieved node, or in the source chunks of a retrieved summary. Both texts are case-folded before matching, whitespace is collapsed, and `**` is removed. For independent units the full serialized record is used. Text Evidence Recall@10 is the fraction of a question's facts that are found, and Text Evidence Hit@10 indicates whether at least one fact is found. A *strict* variant ignores the source chunks of summaries.

Scores are averaged over questions. Each run writes `summary.json` (overall results, and breakdowns by answer type, retrieval type, reasoning type, and record type) and `per_question.jsonl` to `evaluation/results/<timestamp>/`. The evaluator also accepts the earlier `relevant_doc_ids` format.

Answer correctness is not evaluated. The metrics measure retrieval only.

## 4. Results (rag/v2)

578 questions, 16,172 indexed nodes. The detailed report is in [`evaluation/informe_rag_v2.md`](evaluation/informe_rag_v2.md) (in Spanish).

| Metric | Value |
| --- | --- |
| Document Hit@10 | 0.891 |
| Document MRR@10 | 0.698 |
| Document nDCG@10 | 0.745 |
| Text Evidence Recall@10 | 0.781 |
| Text Evidence Hit@10 | 0.830 |
| Text Evidence Recall@10 (strict) | 0.714 |
| Text Evidence Hit@10 (strict) | 0.791 |

A relevant record is retrieved for 89% of questions, usually at rank 1 or 2. Evidence recall drops for questions that need several facts: 0.39 when `retrieval_type` is `multiple` and 0.30 when `reasoning_type` is `implicit`. The catalog node was never retrieved.

## 5. Reproduction

### 5.1 Services

| Service | Default address |
| --- | --- |
| PostgreSQL 16 | `127.0.0.1:5433` |
| Qdrant | `127.0.0.1:6337` |
| Ollama, `qwen3:14b` (summarization and generation) | `127.0.0.1:11436` |
| Embedding service (`bge-m3`, `milco-650m`) | `127.0.0.1:8089` |
| Semantic chunking service | `127.0.0.1:8085` |
| Retrieval and chat API (FastAPI) | `127.0.0.1:8005` |
| Chat UI (Next.js) | `127.0.0.1:3007` |

### 5.2 Experiment CLI

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

### 5.3 Chat interface

After indexing, start the API, then the UI (`npx next dev -H 127.0.0.1 -p 3007` in the UI project). Log in with an account created by `create-user`.

```bash
DOCUMENT_PATH_PREFIX=$PWD/RAG_medils/ingest/data \
  python -m uvicorn RAG_medils.retrieval_and_generation.api:app --host 127.0.0.1 --port 8005
```

`DOCUMENT_PATH_PREFIX` lets the interface open source documents. `QUERY_REWRITE_ENABLED=true` restores LLM query rewriting.

## 6. Repository layout

| Path | Content |
| --- | --- |
| `experiment/` | CLI, resumable corpus ingestion, retrieval evaluation |
| `ingest/corpus/` | Record loading, serialization, per-type routing |
| `ingest/representations/` | Chunking and RAPTOR hierarchy construction |
| `ingest/stores/`, `ingest/indexing/` | PostgreSQL persistence and Qdrant indexing |
| `retrieval_and_generation/` | Hybrid search, LangGraph workflow, chat API |
| `tests/` | Unit tests (`python -m unittest RAG_medils/tests/<module>.py`) |

## 7. Limitations

- Text evidence is matched on normalized text rather than character offsets, and a span counts in any retrieved node. Very short spans, such as amounts, may therefore match in unrelated records.
- Summaries are produced by an LLM and may be written in English for Spanish sources. The independent units longer than 500 words (about 2% of them) are stored as summaries, not verbatim text.
- One catalog summary spans the whole corpus. It is frequently retrieved, but it cannot be attributed to individual records.

## References

[1] P. Sarthi, S. Abdullah, A. Tuli, S. Khanna, A. Goldie, and C. D. Manning. "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval." *ICLR*, 2024.
