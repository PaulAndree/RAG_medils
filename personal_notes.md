
1) Representation building is manual [improvement: make a pipeline for all representation]

2) DB ingestion (Stores) is manual running main_ingestion.py. It reads from /data all the jsons to ingest them

3) The indexer is a separate one-time job and is not started by docker compose up. Run it only when you need to build a new index:

      Start the databases:
      docker compose up -d postgres qdrant neo4j

      docker compose ps postgres qdrant

      build de indexer images: (apply changes)

      docker compose build \
        passage-indexer \
        argument-indexer \
        summary-indexer

      Run the validated each representation indexer:
      docker compose --profile jobs run --rm passage-indexer
      docker compose --profile jobs run --rm argument-indexer
      docker compose --profile jobs run --rm summary-indexer
      docker compose --profile jobs run --rm graph-indexer


Start the API:
docker compose build api
docker compose up -d api
curl http://127.0.0.1:8002/health/live



Checkings:

Confirm PostgreSQL source counts
docker compose exec -T postgres psql \
  -U raguser \
  -d ragdb \
  -c "
    SELECT 'passages' AS representation, count(*) FROM chunks
    UNION ALL
    SELECT 'arguments', count(*) FROM arguments
    UNION ALL
    SELECT 'summaries', count(*) FROM summaries;
  "


Delete_previous INGESTION WORK
docker compose exec postgres psql -U raguser -d ragdb \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public AUTHORIZATION raguser;"



-------------------------------------------------------------------------------------------
ARCHITECTURE:
Passages and summaries uses:  FastEmbed → BAAI/bge-small-en-v1.5

- PostgreSQL on host port 5432
- Qdrant on host ports 6335 and 6336
- FastAPI on 127.0.0.1:8002
- Prometheus on 127.0.0.1:9090
- Grafana on port 3003

- CSSH Tunnel to access from local!!

ssh -N -L 6335:127.0.0.1:6335 -L 8004:127.0.0.1:8002 -L 9090:127.0.0.1:9090 -L 3003:127.0.0.1:3003 -L 7474:127.0.0.1:7474 -L 7687:127.0.0.1:7687 peyzaguirre@wiig.dia.fi.upm.es

ssh -L 7474:127.0.0.1:7474 -L 7687:127.0.0.1:7687 peyzaguirre@wiig.dia.fi.upm.es

Then open:
API documentation: http://localhost:8002/docs
Prometheus: http://localhost:9090
Grafana: http://localhost:3003
Qdrant: http://localhost:6335/dashboard

http://localhost:7474/browser/
Username: neo4j
Password: ragpassword



{
  "question": "What is the relationship between X and Y?",
  "limit": 5,
  "retrievals": ["summaries", "graph"]
}

Allowed values:
- "documents"
- "summaries"
- "graph"
If retrievals is omitted, all three run by default. Unselected result fields remain present but empty.


