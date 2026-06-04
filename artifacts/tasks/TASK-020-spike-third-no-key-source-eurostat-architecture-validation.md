# TASK-020 — Spike third no-key source for architecture validation

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Governing decision: DEC-009

## Objective

Validate MacroForge's canonical model, ingestion framework posture, metadata architecture, and fact table design against one additional public no-key source.

This task is intentionally a bounded architecture spike, not a production-grade ingestion implementation.

## Source

Eurostat quarterly national accounts GDP (`namq_10_gdp`).

Bounded endpoint:

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp?format=JSON&lang=en&freq=Q&unit=CP_MEUR&na_item=B1GQ&s_adj=NSA&geo=DE&geo=FR&time=2023-Q1&time=2023-Q2
```

## Acceptance criteria

- [x] Fresh dry-run is created and validated before execution.
- [x] One public no-key source is selected and scoped.
- [x] Raw public source evidence is captured with checksum and byte count.
- [x] A compact normalized evidence artifact maps source dimensions to MacroForge contract concepts.
- [x] A short findings report evaluates:
  - canonical model,
  - ingestion framework posture,
  - metadata architecture,
  - fact table design.
- [x] Recommended schema changes are recorded if gaps are found.
- [x] No production-grade hardening beyond architecture-gap identification.
- [x] No database writes, schema migrations, generalized source framework, broad codelist harvest, or research/mart implementation.
- [x] Final tests and coherence checks pass after governance updates.

## Outcome

TASK-020 completed a bounded Eurostat third-source architecture spike.

Evidence produced:

- raw artifact: `data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`
- normalized architecture evidence: `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`
- report: `artifacts/reports/eurostat-third-source-architecture-spike-20260604.md`
- dry-run: `simulation/dry_runs/20260604_081341-task-020-third-no-key-source-spike-eurostat.md`

Live public no-key fetch succeeded:

```text
HTTP status: 200
Content type: application/json
Raw bytes: 3262
Raw SHA-256: 914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a
Rows normalized: 4
```

Smoke rows:

| geo | label | period | unit | adjustment | value |
| --- | --- | --- | --- | --- | --- |
| DE | Germany | 2023-Q1 | CP_MEUR | NSA | 1043520.0 |
| DE | Germany | 2023-Q2 | CP_MEUR | NSA | 1031880.0 |
| FR | France | 2023-Q1 | CP_MEUR | NSA | 684762.7 |
| FR | France | 2023-Q2 | CP_MEUR | NSA | 706147.7 |

## Findings

Verdict: PARTIAL.

Eurostat validates MacroForge's broad canonical observation concept and source-specific ingestion posture, but exposes two concrete schema gaps before third-source PostgreSQL promotion:

1. `curated.dim_period` is too annual. Its natural key `(frequency, period_year)` would collapse quarterly observations such as `2023-Q1` and `2023-Q2` into the same `Q + 2023` row.
2. `curated.dim_territory.iso3_code` is too specifically named and constrained for provider geography codes. Eurostat uses `DE` and `FR` in this slice and may use aggregate/provider codes such as `EU27_2020` or `EA20`.

Secondary finding: repeated provider dimension/code dictionaries are now visible across OECD and Eurostat evidence. Metadata architecture should grow a first-class provider-code-list home or a stricter dataset-release metadata convention before many sources accumulate.

## Recommended schema changes

Report-only recommendations; no executable migration was created in TASK-020.

1. High priority: replace or extend `curated.dim_period` natural key from `(frequency, period_year)` to `(frequency, period_code)`, with `period_code text` values such as `2023-Q1`, plus optional `period_year`, `period_quarter`, `period_month`, `period_start_date`, and `period_end_date` fields.
2. High priority: rename or extend `curated.dim_territory.iso3_code` to a provider-neutral `territory_code` / `source_territory_code` plus `code_system`, so non-ISO3 provider codes are not mislabeled.
3. Medium priority: add metadata storage for provider dimension/code dictionaries, either as `meta.provider_code_list`/`meta.provider_code` tables or as a stricter `dataset_release.metadata` convention.
4. Medium priority: when promoting Eurostat, use source-specific `staging.eurostat_namq_observation`; do not build a generalized ingestion framework yet.
5. Low priority: preserve seasonal adjustment in `curated.dim_attribute_set` initially; normalize later only if repeated querying requires it.

## Non-recommendations

- Do not production-harden Eurostat ingestion yet.
- Do not write Eurostat rows into PostgreSQL until the period and territory design gaps are resolved.
- Do not introduce a generalized ingestion framework yet.
- Do not broaden the spike beyond one Eurostat dataset and four observations.

## Verification evidence

Dry-run validation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_081341-task-020-third-no-key-source-spike-eurostat.md

valid: simulation/dry_runs/20260604_081341-task-020-third-no-key-source-spike-eurostat.md
```

Source fetch/artifact generation:

```text
{
  "content_type": "application/json",
  "normalized": "data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json",
  "raw_artifact": "data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json",
  "raw_bytes": 3262,
  "report": "artifacts/reports/eurostat-third-source-architecture-spike-20260604.md",
  "row_count": 4,
  "sha256": "914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a",
  "status": 200
}
```

Checksum verification:

```text
914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a  data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json
3262 data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json
```

Final post-governance tests/coherence are recorded in `state/project_state.md` and `context/latest_handoff.md`.
