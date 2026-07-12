\set ON_ERROR_STOP on
WITH targets AS (
  SELECT dr.dataset_release_id, s.source_code, dr.provider_dataset_code, dr.release_key, dr.raw_artifact_path, dr.raw_sha256, dr.metadata
  FROM meta.dataset_release dr
  JOIN meta.source s USING (source_id)
  WHERE s.source_code = 'IMF_WEO_DATAMAPPER_API_V1'
    AND dr.release_key = 'world-economic-outlook-april-2026'
    AND dr.provider_dataset_code IN ('IMF:WEO:DATAMAPPER:BROAD_MACRO_ANNUAL', 'IMF:WEO:DATAMAPPER:PROJECTIONS')
), refs AS (
  SELECT 'curated'::text AS table_schema, 'fact_observation'::text AS table_name, 'dataset_release_id'::text AS column_name, count(*)::bigint AS reference_count
  FROM curated.fact_observation f JOIN targets t ON f.dataset_release_id=t.dataset_release_id
  UNION ALL
  SELECT 'meta','pipeline_run','dataset_release_id', count(*) FROM meta.pipeline_run r JOIN targets t ON r.dataset_release_id=t.dataset_release_id
  UNION ALL
  SELECT 'staging','task209_imf_weo_g20_projection_observation','dataset_release_id', count(*) FROM staging.task209_imf_weo_g20_projection_observation st JOIN targets t ON st.dataset_release_id=t.dataset_release_id
  UNION ALL
  SELECT 'staging','task211_imf_weo_broad_macro_observation','dataset_release_id', count(*) FROM staging.task211_imf_weo_broad_macro_observation st JOIN targets t ON st.dataset_release_id=t.dataset_release_id
), by_target AS (
  SELECT t.source_code, t.provider_dataset_code, t.release_key,
    (SELECT count(*) FROM curated.fact_observation f WHERE f.dataset_release_id=t.dataset_release_id) AS curated_fact_observation_refs,
    (SELECT count(*) FROM meta.pipeline_run r WHERE r.dataset_release_id=t.dataset_release_id) AS meta_pipeline_run_refs,
    (SELECT count(*) FROM staging.task209_imf_weo_g20_projection_observation st WHERE st.dataset_release_id=t.dataset_release_id) AS staging_task209_refs,
    (SELECT count(*) FROM staging.task211_imf_weo_broad_macro_observation st WHERE st.dataset_release_id=t.dataset_release_id) AS staging_task211_refs
  FROM targets t
)
SELECT jsonb_pretty(jsonb_build_object(
  'operation', 'task-211-weo-obsolete-dataset-release-cleanup-predelete-audit',
  'status', CASE WHEN (SELECT coalesce(sum(reference_count),0) FROM refs) = 0 AND (SELECT count(*) FROM targets)=2 THEN 'eligible_for_deletion' ELSE 'blocked_references_or_target_count_mismatch' END,
  'approved_target_count', (SELECT count(*) FROM targets),
  'total_non_self_references', (SELECT coalesce(sum(reference_count),0) FROM refs),
  'target_rows', (SELECT jsonb_agg(to_jsonb(t) ORDER BY provider_dataset_code) FROM targets t),
  'reference_audit', (SELECT jsonb_agg(to_jsonb(r) ORDER BY table_schema, table_name) FROM refs r),
  'references_by_target', (SELECT jsonb_agg(to_jsonb(b) ORDER BY provider_dataset_code) FROM by_target b)
));
