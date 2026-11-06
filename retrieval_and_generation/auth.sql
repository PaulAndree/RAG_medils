-- Run after the application tables have been created. Safe to rerun.
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY CHECK (btrim(id) <> '')
);

-- Preserve tenant identifiers already used by ingestion.
DO $$ BEGIN
    IF to_regclass('api_keys') IS NOT NULL THEN
        INSERT INTO tenants (id) SELECT DISTINCT tenant_id FROM api_keys
        WHERE btrim(tenant_id) <> '' ON CONFLICT DO NOTHING;
    END IF;
    IF to_regclass('documents') IS NOT NULL THEN
        INSERT INTO tenants (id) SELECT DISTINCT tenant_id FROM documents
        WHERE btrim(tenant_id) <> '' ON CONFLICT DO NOTHING;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    username TEXT NOT NULL UNIQUE CHECK (btrim(username) <> ''),
    password_hash TEXT NOT NULL,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_user_idx ON sessions(user_id);

CREATE OR REPLACE FUNCTION revoke_user_sessions() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    DELETE FROM sessions WHERE user_id = OLD.id;
    RETURN NEW;
END $$;

CREATE OR REPLACE TRIGGER revoke_user_sessions
AFTER UPDATE OF password_hash, tenant_id, is_active ON users
FOR EACH ROW
WHEN (OLD.password_hash IS DISTINCT FROM NEW.password_hash
   OR OLD.tenant_id IS DISTINCT FROM NEW.tenant_id
   OR OLD.is_active IS DISTINCT FROM NEW.is_active)
EXECUTE FUNCTION revoke_user_sessions();

-- NULL deliberately leaves legacy shared conversations inaccessible.
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS tenant_id TEXT REFERENCES tenants(id);
CREATE INDEX IF NOT EXISTS conversations_owner_idx ON conversations(user_id, tenant_id);
