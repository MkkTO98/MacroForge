# ObservedIngestionPackage v1 Contract

Status: public internal architectural contract
Version: v1
Implementation: `src/macroforge/observed_ingestion.py`
Tests: `tests/test_observed_ingestion.py`
Source evidence: `artifacts/reports/R-20260626-observed-common-ingestion-representation-discovery.md`
Established: 2026-06-26

## Purpose

`ObservedIngestionPackage` v1 is MacroForge's narrow shared handoff between source-specific normalization and existing source-specific canonical load SQL for the current WDI, OECD, and Eurostat evidence slices.

It is an equivalence extraction from implemented behavior. It was not designed as a generalized ingestion framework, source plugin system, source registry, or runtime architecture.

Contract changes must be treated as contract evolution. They should be reviewed against current source evidence, tests, loader behavior, lineage, validation, and replay outputs rather than treated as ordinary refactoring.

## Preserved architecture boundary

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1
-> Existing source-specific staging/canonical load SQL
-> Validation
-> Canonical PostgreSQL
```

The package does not replace source-specific acquisition, source-specific normalized metadata, source-specific staging tables, provider-specific mapping logic, lineage emission, quality checks, or canonicalization review semantics.

## Package-level fields

| Field | Purpose | Ownership | Why it exists | Contract status |
|---|---|---|---|---|
| `source_code` | Stable MacroForge source identity used by loader/meta tables. | Source adapter, matching existing loader constants. | All current loaders load `meta.source` and join/report by source code. | Required. |
| `source_name` | Human-readable source name. | Source adapter, matching existing loader/source metadata. | Loader reports and source metadata preserve source provenance. | Required. |
| `source_home_url` | Human-readable source home URL when available. | Source adapter. | Current loaders/source records preserve source-level provenance. | Optional value, required field. |
| `provider_dataset_code` | Provider dataset/dataflow identity for the bounded slice. | Source adapter from normalized artifact or existing loader constant. | Dataset release identity, provider mappings, and reports depend on provider dataset identity. | Required. |
| `release_key` | Existing source-specific deterministic dataset-release key. | Source adapter, preserving existing loader formulas. | Current loaders create `meta.dataset_release` records keyed by source-specific release evidence. | Required; implementation-detail formula must remain source-compatible. |
| `raw_evidence` | Source URL/path/checksum/raw-metadata evidence needed for lineage and report provenance. | Source adapter from normalized metadata. | Existing loaders preserve raw artifact pointers/checksums and source metadata differently by source. | Required field; contents are source-specific. |
| `input_filters` | Bounded source/query/filter evidence for replay and expected coverage. | Source adapter from normalized metadata. | Current artifacts record countries/indicators/date range or provider filters. | Required field; contents are source-specific. |
| `row_count` | Observed normalized-row count. | Source adapter from normalized artifact or observation tuple length. | Current loaders and reports verify staging/fact counts. | Required. |
| `expected_row_count` | Expected row count for bounded smoke validation. | Source adapter from normalized artifact where present, otherwise observed row count. | WDI has explicit expected rows; OECD/Eurostat currently use observed rows as expected load count. | Required; semantics are source-specific when no independent expected count exists. |
| `observations` | Tuple of canonical-load-ready observation rows. | Source adapter. | This is the extracted common handoff demonstrated across WDI, OECD, and Eurostat loaders. | Required. |

## Observation-level fields

| Field | Purpose | Ownership | Why it exists | Contract status |
|---|---|---|---|---|
| `provider_indicator_code` | Provider/source indicator code loaded into canonical indicator dimension. | Source adapter. | All current loaders map provider indicator identity into `curated.dim_indicator`. | Required. |
| `provider_indicator_label` | Provider/source indicator label when available. | Source adapter. | WDI/Eurostat provide labels; OECD currently uses code as label in loader behavior. | Optional value, required field. |
| `provider_territory_code` | Provider territory/geography code before canonical mapping. | Source adapter. | All loaders map provider territories to canonical territory identity or provider mappings. | Required. |
| `provider_territory_label` | Provider territory label when available. | Source adapter. | WDI/Eurostat preserve labels; OECD currently uses code as label. | Optional value, required field. |
| `provider_period_code` | Provider period string as emitted by source. | Source adapter. | Provider period evidence is needed before structured canonical period mapping. | Required. |
| `frequency` | Source/provider frequency code. | Source adapter. | Annual and quarterly periods must remain distinct; no aggregation is performed. | Required. |
| `period_year` | Parsed year used by current loaders for canonical period insertion. | Source adapter. | Existing WDI/OECD annual and Eurostat quarterly loaders already compute/load year. | Optional for future sources, required for current supported observations. |
| `period_quarter` | Parsed quarter for quarterly observations. | Source adapter. | Eurostat quarterly loader requires quarter; annual WDI/OECD do not. | Optional; source-specific. |
| `unit_code` | Provider/source unit code loaded into unit dimension. | Source adapter. | All loaders load/preserve unit identity; WDI uses `unknown` when source row lacks unit. | Required. |
| `unit_label` | Provider/source unit label when available. | Source adapter. | Eurostat provides labels; WDI/OECD current loader behavior does not. | Optional; source-specific. |
| `value` | Numeric observation value or missing value. | Source adapter. | All current loaders load facts from source observation values. | Required field; value may be null. |
| `observation_status` | Loader-compatible status such as observed/missing/suppressed. | Source adapter, preserving source-specific status derivation. | Existing loaders write status to staging/fact observations and quality context. | Required. |
| `decimal_precision` | Source precision metadata where currently used. | Source adapter. | WDI and OECD loaders preserve decimal metadata; Eurostat row may provide it. | Optional; source-specific. |
| `attributes` | Attribute payload used to define/hash `curated.dim_attribute_set`. | Source adapter. | OECD and Eurostat preserve attributes; WDI currently uses empty attributes. | Required field; contents may be empty and source-specific. |
| `attribute_hash` | Deterministic hash/key for attribute payload where applicable. | Source adapter/shared hash helper. | Current loaders use attribute hashes for `curated.dim_attribute_set` keys; WDI uses `empty`. | Required. |
| `source_payload` | Retained source/provider payload evidence for staging/debug/replay. | Source adapter. | All loaders preserve source payload evidence, though WDI uses the full normalized row. | Required field; contents are source-specific. |

## Invariants

- Package builders must be deterministic for the same normalized artifact.
- Observation ordering must preserve current loader behavior unless an explicit contract evolution approves a different stable ordering.
- The package must not infer accepted canonical truth; it only carries source/provider evidence into existing loaders.
- Provider codes remain provider evidence. Canonical identity remains owned by the existing canonical-domain loader/mapping logic.
- Attribute hashing must remain stable: JSON canonicalization with sorted keys and compact separators, then SHA-256.
- WDI empty attributes must continue to use the existing `empty` attribute-hash sentinel unless a migration/task explicitly changes existing facts/tests.
- Missing unit handling must preserve existing WDI behavior: absent source unit becomes `unknown`.
- Annual/quarterly distinctions must be preserved. The contract must not aggregate frequency or convert units/currencies.
- `raw_evidence` and `input_filters` are source-specific dictionaries. Their presence is shared; their key sets are not v1-shared.

## Compatibility expectations

Any change to this contract should demonstrate compatibility by running, at minimum:

```text
git diff --check
python3 tools/check_coherence.py --project .
uvx --from pytest --with pyyaml pytest tests/test_observed_ingestion.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q
uvx --from pytest --with pyyaml pytest tests -q
```

If deterministic report artifacts regenerate with only isolated temporary database-name differences, restore them unless the task explicitly changes report content.

## Versioning policy

- v1 covers only current WDI, OECD, and Eurostat bounded evidence behavior.
- Additive fields require evidence from implemented repeated behavior or an accepted task showing a concrete recurring-effort reduction.
- Removing, renaming, or changing semantics of fields requires a contract-evolution task and equivalence verification across all current supported sources.
- Source-specific adapter internals may change only if package outputs and downstream canonical behavior remain equivalent.
- Broad runtime abstractions, source plugins, registries, generalized staging, source auto-discovery, and acquisition frameworks are not contract evolution; they require separate architecture approval.

## Explicitly outside the contract

The contract does not own:

- source approval or onboarding authority;
- live fetch behavior;
- credentials, secrets, billing, or production database authority;
- source parser/protocol abstraction;
- source plugin registration;
- base loader inheritance;
- source-specific staging schema replacement;
- provider period/territory/code mapping semantics;
- accepted canonical mapping status;
- canonical concept truth;
- unit/currency conversion;
- frequency aggregation;
- AI/model canonicalization;
- report eligibility decisions;
- canonicalization review/approval lifecycle;
- PostgreSQL schema evolution.
