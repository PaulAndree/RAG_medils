# Representation pipeline

The unified host-side pipeline builds passages, arguments, summaries, and graph
representations in that order and records how long each stage takes.

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
generated representations. Cleaning never deletes `data/pdf_docs`.

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

Service configuration uses `OCR_URL`, `CHUNKING_URL`,
`ARGUMENT_OLLAMA_URL`, `ARGUMENT_MODEL`, `OLLAMA_BASE_URL`,
`OLLAMA_GENERATION_MODEL`, `GRAPH_OLLAMA_URL`, and `GRAPH_MODEL`.

Grafana is available at <http://localhost:3003>. The provisioned dashboard is
named **RAG Pipeline Report** in the **RAG** folder. Completed representation
runs publish document counts, native artifact counts, and per-representation
durations to Pushgateway.

PostgreSQL ingestion and Qdrant/Neo4j indexing are intentionally separate and
should only run after this pipeline exits successfully.
