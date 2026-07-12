#!/usr/bin/env python3
"""Bounded TASK-213 obsolete BIS WS_CBPOL metadata cleanup.

This script audits references to exactly one obsolete dataset_release row and exactly
36 obsolete country-encoded BIS WS_CBPOL indicators before optionally deleting them.
It is intentionally task-specific; it is not a generic metadata cleanup framework.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_NAME = "macroforge"
OBSOLETE_RELEASE_KEY = "bis-ws-cbpol-current-snapshot-2015m01-2026m06"
CANONICAL_RELEASE_KEY = "bis-ws-cbpol-snapshot-prepared-20260712t114554z"
DATASET_CODE = "BIS:WS_CBPOL"
SOURCE_CODE = "BIS_PUBLIC_SDMX_API"
OBSOLETE_INDICATOR_PATTERN = "BIS:WS_CBPOL:M.%"
CANONICAL_INDICATOR_CODE = "BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M"
RUN_KEY = "task-213-bis-cbpol-policy-rate-phase2"
AUDIT_PATH = Path("artifacts/reports/task-213-bis-cbpol-metadata-cleanup-reference-audit.json")
POST_PATH = Path("artifacts/reports/task-213-bis-cbpol-metadata-cleanup-post-verification.json")


def psql_json(sql: str, db_name: str = DB_NAME) -> Any:
    command = [
        "psql",
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "-d",
        db_name,
        "-At",
        "-c",
        f"select coalesce(jsonb_agg(t), '[]'::jsonb) from ({sql}) t;",
    ]
    result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = result.stdout.strip()
    return json.loads(text) if text else []


def psql_text(sql: str, db_name: str = DB_NAME) -> str:
    command = ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql]
    result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.strip()


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def discover_columns(column_name: str) -> list[dict[str, str]]:
    return psql_json(
        f"""
        select table_schema, table_name, column_name
        from information_schema.columns
        where column_name = {sql_literal(column_name)}
          and table_schema not in ('information_schema','pg_catalog')
        order by table_schema, table_name, column_name
        """
    )


def discover_indicator_code_columns() -> list[dict[str, str]]:
    return psql_json(
        """
        select table_schema, table_name, column_name
        from information_schema.columns
        where table_schema not in ('information_schema','pg_catalog')
          and column_name in ('indicator_code','source_indicator_code')
        order by table_schema, table_name, column_name
        """
    )


def discover_foreign_keys() -> list[dict[str, str]]:
    return psql_json(
        """
        select
          ns.nspname as table_schema,
          c.relname as table_name,
          a.attname as column_name,
          confns.nspname as referenced_schema,
          confrel.relname as referenced_table,
          con.conname as constraint_name
        from pg_constraint con
        join pg_class c on con.conrelid=c.oid
        join pg_namespace ns on c.relnamespace=ns.oid
        join pg_class confrel on con.confrelid=confrel.oid
        join pg_namespace confns on confrel.relnamespace=confns.oid
        join unnest(con.conkey) with ordinality ck(attnum,ord) on true
        join pg_attribute a on a.attrelid=c.oid and a.attnum=ck.attnum
        where con.contype='f'
          and (
            confns.nspname||'.'||confrel.relname in ('meta.dataset_release','curated.dim_indicator')
            or a.attname in ('dataset_release_id','indicator_id')
          )
        order by ns.nspname, c.relname, a.attname
        """
    )


def count_column_refs(columns: list[dict[str, str]], column_name: str, predicate_sql: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for col in columns:
        schema = col["table_schema"]
        table = col["table_name"]
        q = f'select count(*)::bigint as c from "{schema}"."{table}" where "{column_name}" {predicate_sql}'
        count = int(psql_text(q) or "0")
        rows.append({"table": f"{schema}.{table}", "column": column_name, "count": count})
    return rows


def build_audit() -> dict[str, Any]:
    release_rows = psql_json(
        f"""
        select dr.dataset_release_id::text, s.source_code, dr.provider_dataset_code, dr.release_key,
               dr.release_date::text, dr.raw_artifact_path, dr.raw_sha256, dr.metadata
        from meta.dataset_release dr
        join meta.source s on s.source_id = dr.source_id
        where s.source_code = {sql_literal(SOURCE_CODE)}
          and dr.provider_dataset_code = {sql_literal(DATASET_CODE)}
          and dr.release_key = {sql_literal(OBSOLETE_RELEASE_KEY)}
        """
    )
    canonical_release_rows = psql_json(
        f"""
        select dr.dataset_release_id::text, s.source_code, dr.provider_dataset_code, dr.release_key,
               dr.release_date::text, dr.raw_artifact_path, dr.raw_sha256, dr.metadata
        from meta.dataset_release dr
        join meta.source s on s.source_id = dr.source_id
        where s.source_code = {sql_literal(SOURCE_CODE)}
          and dr.provider_dataset_code = {sql_literal(DATASET_CODE)}
          and dr.release_key = {sql_literal(CANONICAL_RELEASE_KEY)}
        """
    )
    indicators = psql_json(
        f"""
        select indicator_id::text, source_indicator_code, indicator_name, topic
        from curated.dim_indicator
        where source_indicator_code like {sql_literal(OBSOLETE_INDICATOR_PATTERN)}
        order by source_indicator_code
        """
    )
    canonical_indicator = psql_json(
        f"""
        select indicator_id::text, source_indicator_code, indicator_name, topic
        from curated.dim_indicator
        where source_indicator_code = {sql_literal(CANONICAL_INDICATOR_CODE)}
        """
    )
    dataset_columns = discover_columns("dataset_release_id")
    indicator_columns = discover_columns("indicator_id")
    indicator_code_columns = discover_indicator_code_columns()
    fk_rows = discover_foreign_keys()

    release_id = release_rows[0]["dataset_release_id"] if len(release_rows) == 1 else None
    release_ref_counts = count_column_refs(dataset_columns, "dataset_release_id", f"= {sql_literal(release_id)}::uuid") if release_id else []

    indicator_ids = [row["indicator_id"] for row in indicators]
    id_list_sql = ",".join(sql_literal(x) + "::uuid" for x in indicator_ids) or "null::uuid"
    indicator_ref_counts = count_column_refs(indicator_columns, "indicator_id", f"in ({id_list_sql})") if indicator_ids else []

    code_list_sql = ",".join(sql_literal(row["source_indicator_code"]) for row in indicators) or "null"
    indicator_code_ref_counts = []
    if indicators:
        for col in indicator_code_columns:
            schema = col["table_schema"]
            table = col["table_name"]
            column = col["column_name"]
            q = f'select count(*)::bigint as c from "{schema}"."{table}" where "{column}" in ({code_list_sql})'
            indicator_code_ref_counts.append({"table": f"{schema}.{table}", "column": column, "count": int(psql_text(q) or "0")})

    replacement = canonical_indicator[0] if canonical_indicator else None
    indicator_rows = []
    for row in indicators:
        per_indicator_refs = count_column_refs(indicator_columns, "indicator_id", f"= {sql_literal(row['indicator_id'])}::uuid")
        indicator_rows.append({
            "indicator_id": row["indicator_id"],
            "indicator_code": row["source_indicator_code"],
            "reference_counts_by_table": per_indicator_refs,
            "total_indicator_id_external_references": sum(r["count"] for r in per_indicator_refs if r["table"] != "curated.dim_indicator"),
            "canonical_replacement": CANONICAL_INDICATOR_CODE,
        })

    release_external_total = sum(r["count"] for r in release_ref_counts if r["table"] != "meta.dataset_release")
    indicator_external_total = sum(r["count"] for r in indicator_ref_counts if r["table"] != "curated.dim_indicator")
    # Code-column rows in dim_indicator are the target rows themselves. Other exact old code occurrences would be semantic references.
    indicator_code_external_total = sum(r["count"] for r in indicator_code_ref_counts if r["table"] != "curated.dim_indicator")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "database": DB_NAME,
        "scope": {
            "source_code": SOURCE_CODE,
            "dataset_code": DATASET_CODE,
            "obsolete_release_key": OBSOLETE_RELEASE_KEY,
            "obsolete_indicator_pattern": OBSOLETE_INDICATOR_PATTERN,
            "canonical_release_key": CANONICAL_RELEASE_KEY,
            "canonical_indicator_code": CANONICAL_INDICATOR_CODE,
        },
        "catalogue_discovery": {
            "dataset_release_id_columns": dataset_columns,
            "indicator_id_columns": indicator_columns,
            "indicator_code_columns": indicator_code_columns,
            "foreign_keys": fk_rows,
        },
        "obsolete_release": {
            "resolved_rows": release_rows,
            "resolved_count": len(release_rows),
            "reference_counts_by_table": release_ref_counts,
            "external_reference_total_excluding_target_table": release_external_total,
        },
        "canonical_release": {
            "resolved_rows": canonical_release_rows,
            "resolved_count": len(canonical_release_rows),
        },
        "obsolete_indicators": {
            "resolved_rows": indicators,
            "resolved_count": len(indicators),
            "reference_counts_by_indicator_id_table": indicator_ref_counts,
            "exact_code_occurrence_counts_by_table": indicator_code_ref_counts,
            "external_indicator_id_reference_total_excluding_target_table": indicator_external_total,
            "external_exact_code_occurrence_total_excluding_target_table": indicator_code_external_total,
            "per_indicator": indicator_rows,
        },
        "canonical_indicator": {
            "resolved_rows": canonical_indicator,
            "resolved_count": len(canonical_indicator),
        },
        "delete_preconditions": {
            "obsolete_release_resolved_exactly_one": len(release_rows) == 1,
            "obsolete_indicators_resolved_exactly_36": len(indicators) == 36,
            "canonical_release_resolved_exactly_one": len(canonical_release_rows) == 1,
            "canonical_indicator_resolved_exactly_one": len(canonical_indicator) == 1,
            "obsolete_release_external_references_zero": release_external_total == 0,
            "obsolete_indicators_external_indicator_id_references_zero": indicator_external_total == 0,
            "obsolete_indicator_external_exact_code_occurrences_zero": indicator_code_external_total == 0,
        },
    }


def preconditions_pass(audit: dict[str, Any]) -> bool:
    return all(audit["delete_preconditions"].values())


def run_cleanup_transaction() -> dict[str, Any]:
    sql = f"""
    begin;
    do $$
    declare
      deleted_releases integer;
      deleted_indicators integer;
    begin
      if (select count(*) from meta.dataset_release dr join meta.source s on s.source_id=dr.source_id
          where s.source_code={sql_literal(SOURCE_CODE)} and dr.provider_dataset_code={sql_literal(DATASET_CODE)} and dr.release_key={sql_literal(OBSOLETE_RELEASE_KEY)}) <> 1 then
        raise exception 'obsolete release resolution count mismatch';
      end if;
      if (select count(*) from curated.dim_indicator where source_indicator_code like {sql_literal(OBSOLETE_INDICATOR_PATTERN)}) <> 36 then
        raise exception 'obsolete indicator resolution count mismatch';
      end if;
      if exists (select 1 from curated.fact_observation fo join meta.dataset_release dr on dr.dataset_release_id=fo.dataset_release_id join meta.source s on s.source_id=dr.source_id where s.source_code={sql_literal(SOURCE_CODE)} and dr.provider_dataset_code={sql_literal(DATASET_CODE)} and dr.release_key={sql_literal(OBSOLETE_RELEASE_KEY)}) then
        raise exception 'obsolete release still referenced by curated facts';
      end if;
      if exists (select 1 from meta.pipeline_run pr join meta.dataset_release dr on dr.dataset_release_id=pr.dataset_release_id join meta.source s on s.source_id=dr.source_id where s.source_code={sql_literal(SOURCE_CODE)} and dr.provider_dataset_code={sql_literal(DATASET_CODE)} and dr.release_key={sql_literal(OBSOLETE_RELEASE_KEY)}) then
        raise exception 'obsolete release still referenced by pipeline runs';
      end if;
      if exists (select 1 from meta.provider_code_list pcl join meta.dataset_release dr on dr.dataset_release_id=pcl.dataset_release_id join meta.source s on s.source_id=dr.source_id where s.source_code={sql_literal(SOURCE_CODE)} and dr.provider_dataset_code={sql_literal(DATASET_CODE)} and dr.release_key={sql_literal(OBSOLETE_RELEASE_KEY)}) then
        raise exception 'obsolete release still referenced by provider code lists';
      end if;
      if exists (select 1 from curated.fact_observation fo join curated.dim_indicator di on di.indicator_id=fo.indicator_id where di.source_indicator_code like {sql_literal(OBSOLETE_INDICATOR_PATTERN)}) then
        raise exception 'obsolete indicators still referenced by curated facts';
      end if;

      delete from meta.dataset_release dr
      using meta.source s
      where s.source_id = dr.source_id
        and s.source_code = {sql_literal(SOURCE_CODE)}
        and dr.provider_dataset_code = {sql_literal(DATASET_CODE)}
        and dr.release_key = {sql_literal(OBSOLETE_RELEASE_KEY)};
      get diagnostics deleted_releases = row_count;
      if deleted_releases <> 1 then
        raise exception 'deleted release count %, expected 1', deleted_releases;
      end if;

      delete from curated.dim_indicator
      where source_indicator_code like {sql_literal(OBSOLETE_INDICATOR_PATTERN)};
      get diagnostics deleted_indicators = row_count;
      if deleted_indicators <> 36 then
        raise exception 'deleted indicator count %, expected 36', deleted_indicators;
      end if;
    end $$;
    commit;
    select 'cleanup_committed|release=1|indicators=36';
    """
    return {"transaction_output": psql_text(sql)}


def build_post_verification(deleted_counts: dict[str, Any] | None = None) -> dict[str, Any]:
    rows = psql_json(
        f"""
        with task_run as (
          select pipeline_run_id, run_key, dataset_release_id
          from meta.pipeline_run
          where run_key = {sql_literal(RUN_KEY)}
        ), task_facts as (
          select fo.*
          from curated.fact_observation fo
          join task_run tr on tr.pipeline_run_id = fo.pipeline_run_id
        ), task_staging as (
          select st.*
          from staging.bis_cbpol_policy_rate_phase2_observation st
          join task_run tr on tr.pipeline_run_id = st.pipeline_run_id
        )
        select
          (select count(*) from meta.source where source_code={sql_literal(SOURCE_CODE)})::bigint as canonical_bis_source_rows,
          (select count(*) from meta.dataset_release dr join meta.source s on s.source_id=dr.source_id where s.source_code={sql_literal(SOURCE_CODE)} and dr.provider_dataset_code={sql_literal(DATASET_CODE)} and dr.release_key={sql_literal(CANONICAL_RELEASE_KEY)})::bigint as canonical_snapshot_rows,
          (select count(*) from meta.dataset_release dr join meta.source s on s.source_id=dr.source_id where s.source_code={sql_literal(SOURCE_CODE)} and dr.provider_dataset_code={sql_literal(DATASET_CODE)} and dr.release_key={sql_literal(OBSOLETE_RELEASE_KEY)})::bigint as obsolete_window_snapshot_rows,
          (select count(*) from curated.dim_indicator where source_indicator_code={sql_literal(CANONICAL_INDICATOR_CODE)})::bigint as canonical_policy_rate_indicator_rows,
          (select count(*) from curated.dim_indicator where source_indicator_code like {sql_literal(OBSOLETE_INDICATOR_PATTERN)})::bigint as obsolete_country_encoded_indicators,
          (select count(*) from task_staging)::bigint as task213_staging_rows,
          (select count(*) from task_facts)::bigint as task213_facts,
          (select count(*) from task_facts where observation_status = 'observed')::bigint as provider_valued,
          (select count(*) from task_facts where observation_status = 'missing')::bigint as explicit_missing,
          (select count(distinct territory_id) from task_facts)::bigint as territories,
          (select count(distinct period_id) from task_facts)::bigint as periods,
          (select count(*) from task_facts fo join curated.dim_territory dt on dt.territory_id=fo.territory_id where dt.iso3_code='HKG')::bigint as hk_facts,
          (select count(*) from meta.quality_check qc join task_run tr on tr.pipeline_run_id=qc.pipeline_run_id where qc.check_status='fail')::bigint as failed_quality_checks,
          (select count(*) from (
              select source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*)
              from curated.fact_observation
              group by source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date
              having count(*) > 1
          ) d)::bigint as duplicate_canonical_key_groups,
          (select count(*) from curated.fact_observation)::bigint as repository_total_facts
        """
    )[0]
    same_run_before = rows["repository_total_facts"]
    # Re-run the already generated TASK-213 load SQL to verify idempotence without repository growth.
    load_sql = Path("artifacts/reports/task-213-bis-cbpol-policy-rate-load.sql")
    if load_sql.exists():
        subprocess.run(["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", DB_NAME, "-f", str(load_sql)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    same_run_after = int(psql_text("select count(*) from curated.fact_observation") or "0")
    rows["same_run_idempotence_before_total_facts"] = same_run_before
    rows["same_run_idempotence_after_total_facts"] = same_run_after
    rows["same_run_idempotence_repository_growth"] = same_run_after - same_run_before
    if deleted_counts:
        rows["deleted_counts"] = deleted_counts
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "database": DB_NAME,
        "scope": {
            "source_code": SOURCE_CODE,
            "dataset_code": DATASET_CODE,
            "canonical_release_key": CANONICAL_RELEASE_KEY,
            "canonical_indicator_code": CANONICAL_INDICATOR_CODE,
            "run_key": RUN_KEY,
        },
        "verification": rows,
        "snapshot_terminology": {
            "canonical_snapshot_description": "acquired BIS response snapshot/as-of identity based on SDMX message Prepared timestamp, not an official BIS publication release",
            "release_date_expected": None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--post-verify", action="store_true")
    args = parser.parse_args()
    if not (args.audit or args.delete or args.post_verify):
        parser.error("choose --audit, --delete, or --post-verify")

    if args.audit or args.delete:
        audit = build_audit()
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {AUDIT_PATH}")
        print(json.dumps(audit["delete_preconditions"], indent=2, sort_keys=True))
        if not preconditions_pass(audit):
            raise SystemExit("delete preconditions failed; no deletion performed")

    deleted_counts = None
    if args.delete:
        deleted_counts = run_cleanup_transaction()
        print(json.dumps(deleted_counts, indent=2, sort_keys=True))

    if args.post_verify or args.delete:
        post = build_post_verification(deleted_counts=deleted_counts)
        POST_PATH.parent.mkdir(parents=True, exist_ok=True)
        POST_PATH.write_text(json.dumps(post, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {POST_PATH}")
        print(json.dumps(post["verification"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
