docker compose down    # Stop and remove containers and networks

docker compose up -d   # Recreate and start them in the background

If you changed Python code, dependencies, or the Dockerfile:
docker compose up -d --build
This starts:
- PostgreSQL on host port 5432
- Qdrant on host ports 6335 and 6336
- FastAPI on 127.0.0.1:8002
- Prometheus on 127.0.0.1:9090
- Grafana on port 3003


The indexer is a separate one-time job and is not started by docker compose up. Run it only when you need to build a new index:
docker compose run --rm indexer


- CSSH Tunnel to access from local!!

ssh -N -L 8004:127.0.0.1:8002 -L 9090:127.0.0.1:9090 -L 3003:127.0.0.1:3003 peyzaguirre@wiig.dia.fi.upm.es

Then open:
API documentation: http://localhost:8002/docs
Prometheus: http://localhost:9090
Grafana: http://localhost:3003


-----------------------------------------------------------------------
To stop containers while keeping them available for a quick restart:
docker compose stop
Restart them later with:
docker compose start

