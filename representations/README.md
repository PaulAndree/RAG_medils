# Representation pipeline

The unified host-side pipeline builds passages, arguments, summaries, and graph
representations from existing `data/pdf_parsed_output/*.md` files, in that
order, and records how long each stage takes. It does not read or convert PDFs.

Start batch observability:

```bash
docker compose up -d pushgateway prometheus grafana
```

Run the pipeline from the project root:

```bash
.venv/bin/python -m representations.main
```

By default, the command keeps existing representations and builds only the
missing outputs for each document. Use `--clean` to delete and rebuild all
generated representations. Cleaning never deletes the Markdown source files in
`data/pdf_parsed_output`.

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

Service configuration uses `CHUNKING_URL`, `ARGUMENT_OLLAMA_URL`,
`ARGUMENT_MODEL`, `OLLAMA_BASE_URL`,
`OLLAMA_GENERATION_MODEL`, `GRAPH_OLLAMA_URL`, and `GRAPH_MODEL`.

Grafana is available at <http://localhost:3003>. The provisioned dashboard is
named **RAG Pipeline Report** in the **RAG** folder. Completed representation
runs publish document counts, native artifact counts, and per-representation
durations to Pushgateway.

PostgreSQL ingestion and Qdrant/Neo4j indexing are intentionally separate and
should only run after this pipeline exits successfully.



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