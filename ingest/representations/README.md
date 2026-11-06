# Representation pipeline

Uploaded documents are processed automatically by the [ingestion API](../../ingest/README.md).
Its background workflow converts PDFs, passes registered IDs/source keys to this
pipeline, and stores the resulting summaries. Each tenant has separate artifacts
and a catalog. The commands below remain available for standalone generation.

The host-side pipeline builds one RAPTOR representation from existing
`data/pdf_parsed_output/**/*.md` files. Each Markdown document is sent to the
chunking service, the resulting passages are persisted as level-zero RAPTOR
nodes, and the generated cluster, document, and catalog summaries are persisted
at levels 1 and above. It does not read or convert PDFs.

Start batch observability:

```bash
docker compose up -d pushgateway prometheus grafana
```

Run the pipeline from the project root:

```bash
.venv/bin/python -m representations.main
```
nohup .venv/bin/python -u -m representations.main --clean \
  > representations.log 2>&1 < /dev/null &

By default, the command keeps complete existing RAPTOR hierarchies and builds
missing outputs. Hierarchies created before level zero was persisted are rebuilt
automatically. Use `--clean` to delete and rebuild the `data/summaries` output.
Cleaning never deletes the Markdown source files in `data/pdf_parsed_output`.

There are no service preflight checks or final dataset validation; a builder
error stops the pipeline and leaves its partial outputs in place.

Options:

```text
--data-dir PATH
--pushgateway-url URL
--no-metrics
--resume
--clean
```

`--resume` is the default and is provided explicitly for scripts where the
chosen mode should be visible.

Service configuration uses `CHUNKING_URL`, `OLLAMA_BASE_URL`,
`OLLAMA_GENERATION_MODEL`, `EMBEDDING_URL`, `EMBEDDING_MODEL`, and
`RAPTOR_MAX_WORKERS`. The RAPTOR worker count defaults to 2 and controls both
concurrent document builds and concurrent cluster summaries within a level. A
shared limit prevents nested worker pools from exceeding that number of
simultaneous Ollama generations.

Files whose names start with `chat-`, `email-`, `event-`, or `note-` remain a
single level-zero node. Content below 500 tokens is kept unchanged; content at
or above the limit is summarized through Ollama to a maximum generation length
of 450 tokens before it becomes the level-zero node.

Grafana is available at <http://localhost:3003>. The provisioned dashboard is
named **RAG Pipeline Report** in the **RAG** folder. Completed representation
runs publish document counts, native artifact counts, and per-representation
durations to Pushgateway.

The resulting files are `data/summaries/level_0.json`, `level_1.json`, and so
on. Store ingestion and retrieval support for the unified hierarchy is handled
separately.



EMBEDDING API CALLING:

curl -X POST http://127.0.0.1:8089/embed \
  -H 'Content-Type: application/json' \
  -d '{
    "texts": [
      "First passage to embed",
      "Second passage to embed"
    ],
    "model": "bge-m3",
    "input_type": "passage",
    "normalize": true
  }'

The response has this shape:

  {
  "embeddings": [
    [0.0123, -0.0456, "... 1024 values ..."]
  ],
  "sparse": null,
  "model": "bge-m3",
  "kind": "dense",
  "dim": 1024,
  "store": "weaviate",
  "modes": []
}

Use moderate application batches, such as 12–64 texts, instead of making one HTTP request per document or one enormous request for the complete corpus.

Replace:
models.Document(
    text=query,
    model=DENSE_MODEL,
)
with:
dense_query = embed_texts(
    [query],
    input_type="query",
)[0]

Then use the raw query vector:
models.Prefetch(
    query=dense_query,
    using=DENSE_VECTOR,
    limit=candidate_limit,
)


HOW TO CALL:


You can currently make two calls.
Dense BGE-M3:
POST /embed

{
  "texts": ["Text to embed"],
  "model": "bge-m3",
  "input_type": "passage",
  "normalize": true
}


Learned sparse MILCO:
POST /embed

{
  "texts": ["Text to embed"],
  "model": "milco-650m",
  "input_type": "passage"
}

The sparse response looks like:
{
  "embeddings": null,
  "sparse": [
    {
      "indices": [104, 892, 19344],
      "values": [0.41, 1.27, 0.63]
    }
  ],
  "model": "milco-650m",
  "kind": "sparse",
  "dim": 280524
}
