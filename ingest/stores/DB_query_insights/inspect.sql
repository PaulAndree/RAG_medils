\pset pager off
\x auto

BEGIN TRANSACTION READ ONLY;

SELECT
    chunk_id,
    jsonb_array_length(entities) AS entity_count,
    jsonb_array_length(relations) AS relation_count
FROM entities
ORDER BY chunk_id;



COMMIT;