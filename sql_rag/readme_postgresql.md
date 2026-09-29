
- to connect to postgrsql:
docker compose exec postgres psql -U raguser -d ragdb

- to connect to promotheus:  http://localhost:9090/
curl http://localhost:8008/metrics | grep rag_retrieval

- to access grafana:   http://prometheus:9090

- CSSH Tunnel to access from local!!
ssh -N -L 9090:127.0.0.1:9090 peyzaguirre@wiig.dia.fi.upm.es

ssh -N -o ExitOnForwardFailure=yes -L 9090:127.0.0.1:9090 -L 3003:127.0.0.1:3003 peyzaguirre@wiig.dia.fi.upm.es

Then open:
- Prometheus: http://localhost:9090/
- Grafana: http://localhost:3003/


docker compose build app

docker compose run --rm app python -m sql_rag.semantic_search

docker compose up -d --build --force-recreate app

To interact with that background process, attach your terminal:
docker attach learning_1-app-1

To interact with that background process, attach your terminal:
docker attach learning_1-app-1
You can then enter questions. To leave the terminal without stopping the application, press:
Ctrl+P, then Ctrl+Q