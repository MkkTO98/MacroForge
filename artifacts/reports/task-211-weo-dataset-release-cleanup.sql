\set ON_ERROR_STOP on
BEGIN;

CREATE TEMP TABLE _target_dataset_release AS
SELECT dr.dataset_release_id, s.source_code, dr.provider_dataset_code, dr.release_key, dr.raw_artifact_path, dr.raw_sha256, dr.metadata
FROM meta.dataset_release dr
JOIN meta.source s USING (source_id)
WHERE s.source_code = 'IMF_WEO_DATAMAPPER_API_V1'
  AND dr.release_key = 'world-economic-outlook-april-2026'
  AND dr.provider_dataset_code IN ('IMF:WEO:DATAMAPPER:BROAD_MACRO_ANNUAL', 'IMF:WEO:DATAMAPPER:PROJECTIONS');

DO $$
DECLARE
  tbl record;
  cnt bigint;
  total_refs bigint := 0;
BEGIN
  IF (SELECT count(*) FROM _target_dataset_release) <> 2 THEN
    RAISE EXCEPTION 'Expected exactly 2 target dataset_release rows, found %', (SELECT count(*) FROM _target_dataset_release);
  END IF;

  IF (SELECT count(*)
      FROM meta.dataset_release dr
      JOIN meta.source s USING (source_id)
      WHERE s.source_code = 'IMF_WEO_DATAMAPPER_API_V1'
        AND dr.provider_dataset_code = 'IMF:WEO:DATAMAPPER'
        AND dr.release_key = 'world-economic-outlook-april-2026') <> 1 THEN
    RAISE EXCEPTION 'Canonical IMF:WEO:DATAMAPPER April 2026 release missing or non-unique';
  END IF;

  CREATE TEMP TABLE _dataset_release_reference_audit (
    table_schema text,
    table_name text,
    column_name text,
    reference_count bigint
  ) ON COMMIT DROP;

  FOR tbl IN
    SELECT table_schema, table_name, column_name
    FROM information_schema.columns
    WHERE column_name = 'dataset_release_id'
      AND table_schema NOT IN ('pg_catalog', 'information_schema')
      AND table_schema NOT LIKE 'pg_temp_%'
      AND table_schema NOT LIKE 'pg_toast_temp_%'
      AND NOT (table_name IN ('_target_dataset_release', '_dataset_release_reference_audit', '_deleted_dataset_release'))
    ORDER BY table_schema, table_name, column_name
  LOOP
    EXECUTE format(
      'SELECT count(*) FROM %I.%I t JOIN _target_dataset_release d ON t.%I = d.dataset_release_id',
      tbl.table_schema, tbl.table_name, tbl.column_name
    ) INTO cnt;
    INSERT INTO _dataset_release_reference_audit VALUES (tbl.table_schema, tbl.table_name, tbl.column_name, cnt);
    IF NOT (tbl.table_schema = 'meta' AND tbl.table_name = 'dataset_release') THEN
      total_refs := total_refs + cnt;
    END IF;
  END LOOP;

  IF total_refs <> 0 THEN
    RAISE EXCEPTION 'Blocked obsolete dataset_release cleanup: % non-self references remain', total_refs;
  END IF;
END $$;

CREATE TEMP TABLE _deleted_dataset_release AS
WITH deleted AS (
  DELETE FROM meta.dataset_release dr
  USING _target_dataset_release t
  WHERE dr.dataset_release_id = t.dataset_release_id
  RETURNING t.source_code, t.provider_dataset_code, t.release_key, t.raw_artifact_path, t.raw_sha256, t.metadata
)
SELECT * FROM deleted;

DO $$
BEGIN
  IF (SELECT count(*) FROM _deleted_dataset_release) <> 2 THEN
    RAISE EXCEPTION 'Expected exactly 2 deleted rows, deleted %', (SELECT count(*) FROM _deleted_dataset_release);
  END IF;
END $$;

SELECT jsonb_pretty(jsonb_build_object(
  'operation', 'task-211-weo-obsolete-dataset-release-cleanup',
  'status', 'deleted_exactly_approved_rows',
  'deleted_rows', (SELECT jsonb_agg(to_jsonb(d) ORDER BY provider_dataset_code) FROM _deleted_dataset_release d),
  'reference_audit', (SELECT jsonb_agg(to_jsonb(a) ORDER BY table_schema, table_name, column_name) FROM _dataset_release_reference_audit a),
  'remaining_weo_dataset_releases', (
    SELECT jsonb_agg(jsonb_build_object('provider_dataset_code', dr.provider_dataset_code, 'release_key', dr.release_key) ORDER BY dr.provider_dataset_code, dr.release_key)
    FROM meta.dataset_release dr JOIN meta.source s USING(source_id)
    WHERE s.source_code = 'IMF_WEO_DATAMAPPER_API_V1' AND dr.provider_dataset_code LIKE 'IMF:WEO:DATAMAPPER%'
  )
));

COMMIT;
