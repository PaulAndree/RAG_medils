
1) Representation building is manual [improvement: make a pipeline for all representation]

2) DB ingestion (Stores) is manual running main_ingestion.py. It reads from /data all the jsons to ingest them

3) The indexer is a separate one-time job and is not started by docker compose up. Run it only when you need to build a new index:

      Start the databases:
      docker compose up -d postgres qdrant neo4j

      docker compose ps postgres qdrant

      build de indexer images: (apply changes)

      docker compose build summary-indexer

      Run the unified RAPTOR summary indexer:
      docker compose --profile jobs run --rm summary-indexer


Start the API:
docker compose build api
docker compose up -d api
curl http://127.0.0.1:8009/health/live



Checkings:

Confirm PostgreSQL source counts
docker compose exec -T postgres psql \
  -U raguser \
  -d ragdb \
  -c "
    SELECT 'documents' AS representation, count(*) FROM documents
    UNION ALL
    SELECT 'summaries', count(*) FROM summaries;
  "


Delete_previous INGESTION WORK
docker compose exec postgres psql -U raguser -d ragdb \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public AUTHORIZATION raguser;"



-------------------------------------------------------------------------------------------
ARCHITECTURE:
Summaries use the configured dense and sparse embedding models.

- PostgreSQL on host port 5432
- Qdrant on host ports 6335 and 6336
- FastAPI on 127.0.0.1:8002
- Prometheus on 127.0.0.1:9090
- Grafana on port 3003

- CSSH Tunnel to access from local!!

Qdrant 6337, API Retrieval 8005, Promotheus 9092, Chatbot UI 3005

ssh -N -L 6337:127.0.0.1:6337 -L 8005:127.0.0.1:8005 -L 9092:127.0.0.1:9092 -L 3005:127.0.0.1:3005 peyzaguirre@wiig.dia.fi.upm.es


Then open:
API documentation: http://localhost:8004/docs
Qdrant: http://localhost:6337/dashboard
Grafana: http://127.0.0.1:3004
PostgreSQL: 127.0.0.1:5433
Prometheus: http://127.0.0.1:9092
Pushgateway: http://127.0.0.1:9093


For a fresh restart delete the table on POSTGRESQL
DROP public.summaries CASCADE

API :

docker compose up -d --build api-medils
docker compose logs -f api-medils

You must also restart the Next.js frontend so it loads the new runtime code:
cd /home/peyzaguirre/notebooks/chat_ui/rag-chatbot
npm run dev


{
  "question": "What is the relationship between X and Y?",
  "limit": 5,
  "retrievals": ["summaries", "graph"]
}

