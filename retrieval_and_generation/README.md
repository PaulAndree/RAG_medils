# Retrieval and generation API

Run from `/home/peyzaguirre/learning`:

```bash
RAG_medils/.venv/bin/python -m uvicorn RAG_medils.retrieval_and_generation.api:app --host 127.0.0.1 --port 8005
```

`DATABASE_URL` defaults to the local `ragdb` database on port 5433. Startup creates
application/authentication tables, preserves existing ingestion tenant IDs, and
adds a `catalog_id` keyword index to the active Qdrant collection. Future summary
index rebuilds create this index too. PostgreSQL and Qdrant must be available.

## Accounts managed directly in PostgreSQL

There are no registration or administration endpoints. `tenants.id` is the same
text identifier as `api_keys.tenant_id` and `documents.tenant_id`. Users belong to
tenants independently of API keys; rotating an ingestion key does not change
login access. Usernames are case-sensitive.

Generate a password hash without putting the password in shell history:

```bash
RAG_medils/.venv/bin/python -m RAG_medils.retrieval_and_generation.hash_password
```

Then run in PostgreSQL, replacing the example values and hash:

```sql
INSERT INTO tenants (id) VALUES ('Company_OEG') ON CONFLICT DO NOTHING;
INSERT INTO users (username, password_hash, tenant_id)
VALUES ('researcher', '<Argon2 hash from helper>', 'Company_OEG');

-- Assign an existing tenant, reset a password, or disable an account:
UPDATE users SET tenant_id = 'Company_OEG' WHERE username = 'researcher';
UPDATE users SET password_hash = '<new Argon2 hash>' WHERE username = 'researcher';
UPDATE users SET is_active = FALSE WHERE username = 'researcher';
```

A database trigger revokes all of the user's sessions when `password_hash`,
`tenant_id`, or `is_active` actually changes. Existing conversations retain their
original tenant; reassigning a user does not transfer their old history. New
ingestion tenants can be registered in `tenants` manually; startup also imports
tenant IDs already present in ingestion keys/documents.

## Login and sessions

- `POST /auth/login` accepts JSON `{"username":"researcher","password":"..."}`
  and returns `access_token`, `token_type: "bearer"`, and `expires_in: 28800`.
- Send `Authorization: Bearer <access_token>` to protected endpoints.
- `GET /auth/me` returns `user_id`, `username`, and `tenant_id`.
- `POST /auth/logout` revokes the current session and returns 204.

Tokens are random, expire after eight hours, and are stored only as SHA-256
hashes. Expired sessions are removed on the next successful login. Login allows
five attempts per username/client address per minute in each API process. This
basic throttle resets on restart; multiple API workers have separate counters.
The UI proxy's address is the client address seen by FastAPI; usernames have
separate limits. No forwarded client-IP header is trusted by this code.

The chat UI keeps the token in an HttpOnly cookie and sends it to FastAPI only
from Next.js server routes. Direct API clients and Swagger can use the same
login endpoint and Bearer token. Ingestion keys are not login sessions.

## Protected endpoints and isolation

| Endpoint | Behavior |
|---|---|
| `POST /retrieve` | Rewrite query, apply dates, return ranked Qdrant points without generation |
| `POST /chat` | Run the graph and stream answer text and document sources |
| `GET/POST /conversations` | List or create the current user's conversations |
| `GET/PATCH/DELETE /conversations/{id}` | Read, rename, archive, or delete an owned conversation |
| `GET/POST /conversations/{id}/messages` | Read or save messages in an owned conversation |
| `GET /documents/{id}/content` | Serve a PDF/Markdown document belonging to the current tenant |

`/retrieve` accepts `{"query":"question","limit":10}`; `limit` defaults to 3.
`/chat` accepts `messages`, `limit` (default 3, maximum 20), and `id`, the UUID of
an existing owned conversation. The installed assistant-ui transport initializes
the saved conversation before sending this ID. Chat authorization happens before
streaming begins. Unauthorized/missing documents and conversations return 404.
Missing, invalid, expired, or revoked sessions return 401.

Tenant identity comes from the authenticated user, never the request body or
model output. The graph receives it on every invocation. Hybrid retrieval uses
`catalog_id = 'tenant:' + tenant_id` in both prefetches and final fusion. Date
conditions remain inclusive of both supplied calendar dates; undated summaries
remain eligible within the tenant. Download/source queries also check tenant
ownership in PostgreSQL. Members of a tenant share documents but have private
conversations. Checkpoint keys contain tenant, user, and conversation IDs.

Legacy shared conversations keep a NULL `tenant_id` and remain inaccessible.
They can be assigned explicitly by setting both `user_id` to a `users.id` value
and `tenant_id` to that user's tenant. Old checkpoint keys are not reused; an
assigned legacy conversation starts fresh graph memory. Unassigned documents
and catalogs outside the tenant naming convention are excluded from retrieval.

`/health`, `/metrics`, `/docs`, and `/openapi.json` retain their existing public
behavior. Ingestion keeps its separate API-key authentication.

## Tests

From `/home/peyzaguirre/learning`:

```bash
RUN_POSTGRES_TESTS=1 PYTHONPATH="$PWD:$PWD/RAG_medils" \
  RAG_medils/.venv/bin/python -m unittest discover \
  -s RAG_medils/tests -p 'test_auth_integration.py' -v
PYTHONPATH="$PWD:$PWD/RAG_medils" \
  RAG_medils/.venv/bin/python -m unittest discover \
  -s RAG_medils/tests -p 'test_retrieval_integration.py' -v
```

Authentication integration tests use disposable PostgreSQL schemas and actual
LangGraph checkpoints. Model calls are mocked. Tenant search tests use in-memory
Qdrant and cover dense/sparse fusion, dates, and foreign-tenant candidate crowding.
The manually retained `rag_auth_test_a`/`rag_auth_test_b` tenants and
`rag_auth_test_user` account are separate from automated test cleanup. Their
password is handed over separately and is not committed to this repository.
