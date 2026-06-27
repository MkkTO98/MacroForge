# Observed Common Ingestion Representation Discovery

Date: 2026-06-26
Status: discovery complete
Scope: current MacroForge implementation only
Implementation changes: none
Model calls for canonicalization or source analysis: none

## Executive conclusion

MacroForge has accumulated enough implementation evidence to justify introducing a formal shared observation representation, but only as a narrow extraction from the existing WDI, OECD, and Eurostat loaders.

The evidence does not justify a generalized ingestion framework, source plugin system, source abstraction hierarchy, or schema redesign. The evidence does justify extracting the repeated object that now sits between source-specific acquisition/normalization and shared canonical loading: a source-preserving observation bundle with source identity, provider dataset identity, row count, raw evidence metadata, observation rows, provider indicator/territory/period/unit/value fields, source payload evidence, and enough metadata to load canonical dimensions/facts, lineage, and quality checks deterministically.

During this discovery phase, the neutral name used below is Observed Intermediate Representation. The previously suggested `NormalizedObservationPackage` name is plausible but should not be treated as accepted terminology until an implementation task extracts and validates the contract from current behavior.

## Evidence base inspected

### Source acquisition and normalized metadata

WDI:

- `src/macroforge/wdi.py`
- `data/metadata/wdi/wdi-smoke-normalized.json`
- `artifacts/handoffs/wdi-live-smoke-support-20260602/`

OECD:

- `src/macroforge/oecd_sdmx.py`
- `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`
- `data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json`

Eurostat:

- `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`
- `src/macroforge/eurostat_namq_loader.py`

### Staging, canonicalization, lineage, validation, and tests

- `db/migrations/001_v0_schema_foundation.sql`
- `db/migrations/002_oecd_sdmx_staging.sql`
- `db/migrations/003_canonical_domain_dimensions.sql`
- `db/migrations/004_eurostat_namq_staging.sql`
- `src/macroforge/wdi_loader.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `src/macroforge/eurostat_namq_loader.py`
- `src/macroforge/combined_source_smoke.py`
- `src/macroforge/canonical_gdp_snapshot.py`
- `src/macroforge/canonicalization_state.py`
- `tests/test_wdi_loader.py`
- `tests/test_oecd_sdmx_loader.py`
- `tests/test_eurostat_namq_loader.py`
- `tests/test_combined_source_smoke.py`
- `tests/test_canonical_gdp_snapshot.py`
- `tests/test_canonicalization_state.py`
- `tests/test_canonicalization_proposal_workflow.py`
- `docs/runbooks/wdi-v1-runbook.md`

## What each source currently produces

### WDI

The WDI acquisition utility normalizes a World Bank JSON payload into source-shaped rows. The top-level normalized artifact contains:

- `source`
- `support_bundle`
- `created_at_utc`
- `countries`
- `indicators`
- `date_range`
- `expected_row_count`
- `row_count`
- `rows`
- `raw_artifacts`

Each row contains:

- `source`
- `indicator_id`
- `indicator_name`
- `country_id`
- `country_name`
- `countryiso3code`
- `date`
- `value`
- `unit`
- `obs_status`
- `decimal`

WDI loader behavior:

- derives `source_code = WDI`, `provider_dataset_code = WDI`, and a release key from source metadata/date range;
- loads `meta.source`, `meta.dataset_release`, and `meta.pipeline_run`;
- stages rows in `staging.wdi_observation`;
- maps WDI `countryiso3code` to canonical ISO3 territory;
- maps WDI year strings to annual canonical periods;
- writes `curated.dim_indicator`, `curated.dim_territory`, `curated.dim_period`, `curated.dim_unit`, `curated.dim_attribute_set`, and `curated.fact_observation`;
- writes two lineage events: `raw_to_staging` and `staging_to_curated`;
- writes quality checks for expected staging and fact rows.

Source-specific traits:

- WDI uses `indicator_id`, `countryiso3code`, and `date` rather than the later `indicator_code`, `territory_code`, and `period` spelling.
- WDI normalized rows do not include `source_payload`; instead the entire row is inserted as source payload by the loader.
- WDI unit metadata is incomplete in the source row (`unit: null`) and is converted to loader-level `unknown`; later deterministic WDI-specific enrichment adds source metadata evidence for GDP only.
- WDI acquisition stores multiple raw artifacts, one per indicator, under `raw_artifacts`.

### OECD

The OECD SDMX normalizer produces a top-level artifact containing:

- `source_code`
- `source_name`
- `source_home_url`
- `provider_dataset_code`
- `raw_metadata`
- `filters`
- `row_count`
- `rows`

Each row contains:

- `source_code`
- `provider_dataset_code`
- `indicator_code`
- `territory_code`
- `period`
- `frequency`
- `value`
- `unit`
- `attributes`
- `source_payload`

OECD loader behavior:

- derives release key from provider dataset, observed period range, and raw checksum;
- loads `meta.source`, `meta.dataset_release`, and `meta.pipeline_run`;
- stages rows in `staging.oecd_sdmx_observation`;
- maps SDMX `MEASURE`, `REF_AREA`, `TIME_PERIOD`, `FREQ`, and `UNIT_MEASURE` into canonical indicator, territory, period, unit, and fact rows;
- writes provider period and territory mappings;
- hashes source attributes into `curated.dim_attribute_set`;
- writes two lineage events and four quality checks;
- preserves SDMX codelist/label evidence separately in normalized metadata.

Source-specific traits:

- OECD has explicit SDMX `attributes` and `series_dimensions`.
- It has multiple unit profiles for the same provider indicator: `USD_EXC` and `USD_PPP`.
- Codelist enrichment exists but is bounded to observed OECD fixture codes, not shared metadata infrastructure.

### Eurostat

The Eurostat normalized fixture contains a top-level artifact with:

- `source_code`
- `source_name`
- `source_home_url`
- `source_url`
- `provider_dataset_code`
- `access_method`
- `content_type`
- `credentials_required`
- `http_status`
- `response_date_header`
- `fetched_at_utc`
- `raw_artifact_path`
- `raw_bytes`
- `raw_sha256`
- `license_note`
- `filters`
- `dimensions`
- `row_count`
- `rows`
- architecture-spike notes and non-recommendations

Each row contains:

- `source`
- `provider_dataset_code`
- `indicator_code`
- `indicator_name`
- `territory_code`
- `territory_name`
- `period`
- `period_year`
- `period_quarter`
- `frequency`
- `unit`
- `unit_name`
- `seasonal_adjustment`
- `seasonal_adjustment_name`
- `value`
- `observation_status`
- `decimal_precision`
- `as_of_date`
- `source_payload`

Eurostat loader behavior:

- derives release key from provider dataset, observed period range, and checksum;
- loads `meta.source`, `meta.dataset_release`, and `meta.pipeline_run`;
- stages rows in `staging.eurostat_namq_observation`;
- maps Eurostat two-letter `geo` codes to canonical ISO3 through a source-specific `GEO_TO_ISO3` map;
- maps quarterly period codes into structured canonical quarterly periods;
- writes provider period and territory mappings;
- writes provider code list/code dictionaries for Eurostat dimensions;
- folds seasonal adjustment/status/provider context into attributes and hashes them into `curated.dim_attribute_set`;
- writes curated facts, two lineage events, and four quality checks.

Source-specific traits:

- Eurostat has quarterly periods, source provider code dictionaries, seasonal adjustment attributes, and source-specific two-letter to ISO3 mapping.
- Eurostat’s acquisition/normalization is currently represented as a persisted fixture from the architecture spike rather than a reusable parser module analogous to `wdi.py` or `oecd_sdmx.py`.
- The normalized artifact still includes architecture-spike recommendations; these are evidence/history, not part of a future runtime contract.

## Exact row-key convergence observed

A mechanical comparison of the three persisted normalized artifacts showed that only two row keys are textually common to all three:

- `unit`
- `value`

Two-source exact row-key overlaps:

- OECD + Eurostat: `frequency`, `indicator_code`, `period`, `provider_dataset_code`, `source_payload`, `territory_code`
- WDI + Eurostat: `indicator_name`, `source`
- WDI + OECD: no additional exact row-key overlap beyond `unit` and `value`

This matters: the implementation has not converged by naming alone. The stronger convergence appears in loader behavior and canonical targets, not in identical normalized JSON field names.

## Semantic convergence observed before shared canonical processing

Despite field-name differences, each source now provides enough information to populate the same canonical-domain flow:

1. Source identity.
2. Provider dataset/release identity.
3. Raw artifact/reproducibility metadata.
4. Pipeline run identity and input/artifact manifests.
5. Observation rows.
6. Provider indicator identity.
7. Provider territory identity.
8. Provider period identity plus frequency/period structure.
9. Unit identity or explicit unknown-unit handling.
10. Numeric observation value.
11. Observation status.
12. Attribute set, even if empty.
13. Source payload or source-row evidence retained as JSON.
14. Provider period mappings.
15. Provider territory mappings.
16. Canonical dimensions and source-agnostic `curated.fact_observation` rows.
17. Lineage events for raw-to-staging and staging-to-curated.
18. Quality checks for row counts and source-specific structural expectations.

This is the real emerged representation: not a unified parser, but a repeated normalized observation bundle sufficient to drive the same canonical load pattern.

## Classification of candidate fields and concepts

| Candidate concept | Classification | Evidence |
| --- | --- | --- |
| Source identity | Observed invariant | All loaders write `meta.source`; OECD/Eurostat normalized artifacts have `source_code`; WDI loader derives `WDI` from constants. |
| Source name/home/license metadata | Strong emerging pattern | All loaders write source metadata; OECD/Eurostat normalized artifacts contain source name/home; WDI has source/source metadata but not identical fields. |
| Provider dataset code | Observed invariant at loader boundary | All loaders write `meta.dataset_release.provider_dataset_code`; OECD/Eurostat normalized artifacts carry it; WDI loader derives `WDI`. |
| Release key | Observed invariant at loader boundary | All loaders compute release keys, but formulas remain source-specific. |
| Raw artifact path | Observed invariant | All dataset releases/lineage events preserve raw/support-bundle path evidence. WDI has multiple raw artifacts/support bundle; OECD/Eurostat have single raw paths in current fixtures. |
| Raw checksum | Observed invariant | WDI `raw_artifacts[].sha256`, OECD `raw_metadata.sha256`, Eurostat `raw_sha256`; loaders preserve checksums in releases/lineage where available. |
| Raw bytes/content type/status/endpoint | Strong emerging pattern | Present in normalized metadata but field shapes differ by source. Useful as source evidence, not a uniform required row field yet. |
| Filters/input parameters | Strong emerging pattern | WDI has countries/indicators/date range; OECD/Eurostat have `filters`; loaders write `pipeline_run.input_parameters`. |
| Row count / expected row count | Observed invariant | All normalized artifacts include `row_count`; WDI additionally has `expected_row_count`; loaders emit row-count quality checks. |
| Observation rows array | Observed invariant | All normalized artifacts have `rows`; all loaders use it as their input. |
| Provider indicator code | Observed invariant semantically | WDI `indicator_id`; OECD/Eurostat `indicator_code`; all become `curated.dim_indicator.source_indicator_code`. |
| Provider indicator name/label | Strong emerging pattern | WDI and Eurostat rows include names; OECD current loader uses the code as name, while codelist label evidence exists separately. |
| Provider territory code | Observed invariant semantically | WDI `countryiso3code`; OECD `territory_code`; Eurostat `territory_code`; all become provider territory mappings and canonical territory rows. |
| Provider territory label | Strong emerging pattern | WDI/Eurostat include labels; OECD current fixture uses code as label in loader. |
| Canonical ISO3 territory | Observed invariant at canonical boundary | All current examples map to country ISO3 canonical territories. Eurostat requires a source-specific DE/FR -> DEU/FRA mapping. Do not assume all future territories are countries. |
| Provider period code | Observed invariant semantically | WDI `date`, OECD `period`, Eurostat `period`; all become provider period mappings. |
| Frequency | Observed invariant at canonical boundary | All canonical periods carry frequency. OECD/Eurostat normalized rows carry it directly; WDI loader assigns annual `A`. |
| Structured period fields | Strong emerging pattern | Annual and quarterly canonical periods are both implemented; Eurostat normalized rows carry `period_year`/`period_quarter`; WDI/OECD derive annual years. |
| Unit code | Observed invariant | All rows carry `unit` or loader-derived `unknown`; all facts require `unit_id`. |
| Unit label/profile | Strong emerging pattern | Eurostat has `unit_name`; OECD has codelist/unit profile evidence; WDI gets bounded fixture metadata enrichment for GDP. Current evidence supports carrying unit code; richer unit profile remains canonicalization evidence, not raw ingestion invariant. |
| Numeric observation value | Observed invariant | All rows carry `value`; all loaders load it into `curated.fact_observation.value`. |
| Observation status | Observed invariant at loader boundary | WDI derives observed/missing from value and `obs_status`; OECD derives from `OBS_STATUS` and value; Eurostat carries `observation_status`. Status is present but source-specific derivation remains. |
| Decimal precision | Strong emerging pattern | WDI `decimal`, OECD `DECIMALS`, Eurostat `decimal_precision`; not always present/meaningful, but repeatedly preserved. |
| Attributes | Observed invariant at canonical boundary | All facts get an attribute set: WDI empty, OECD source attributes, Eurostat constructed attributes. A shared representation should support attributes but not require non-empty attributes. |
| Attribute hash | Observed invariant in loader mechanics for OECD/Eurostat; source-specific/empty for WDI | OECD and Eurostat compute canonical hashes from attributes; WDI uses constant `empty`. Hashing mechanics are nearly identical and extractable. |
| Source payload evidence | Observed invariant | OECD/Eurostat rows carry `source_payload`; WDI inserts the normalized row as payload. The invariant is retained source evidence, not identical payload shape. |
| Provider code dictionaries | Source-specific behavior with emerging infrastructure | Eurostat writes `meta.provider_code_list`/`meta.provider_code`; OECD codelist label artifacts exist but are not loaded into that table; WDI does not use provider code dictionaries. |
| Lineage events | Observed invariant | All loaders write `raw_to_staging` and `staging_to_curated` lineage events. |
| Quality checks | Observed invariant | All loaders write row-count checks; OECD/Eurostat add source-specific checks for units/attributes/periods/provider mappings. |
| Canonical fact grain | Observed invariant | All sources load into the same source-agnostic fact grain: source, release, run, indicator, territory, period, unit, attribute set, value, as-of date, observation status. |
| Canonical mapping/review status | Strong emerging pattern after fact loading | Canonicalization state groups facts by source/dataset/indicator and derives provider evidence/proposals. This is downstream of ingestion, not part of raw normalized row production. |
| Unit comparability profile | Strong emerging pattern after canonical snapshot | Implemented in `canonicalization_state.py`, not by all source normalizers. Should remain downstream evidence unless extraction proves it belongs in ingestion metadata. |
| Frequency aggregation/conversion policy | Observed invariant as explicit non-action | Combined snapshot/canonicalization reports repeatedly encode no unit conversion and no frequency aggregation. It is a policy boundary, not an ingestion row field. |

## What is produced by every existing source

Every source implementation now produces or derives:

- source identity;
- provider dataset identity;
- raw evidence location and checksum evidence;
- bounded input/filter evidence;
- row count evidence;
- an iterable observation row set;
- provider indicator code;
- provider territory code;
- provider period code;
- frequency at or before canonical period insertion;
- unit code, including explicit `unknown` where source data lacks unit metadata;
- numeric value;
- observation status at or before fact insertion;
- attribute-set representation, including empty attributes;
- retained source payload/evidence;
- canonical dimension insertions;
- provider period/territory mappings;
- canonical fact insertions;
- raw-to-staging and staging-to-curated lineage;
- quality checks.

## What is produced by exactly two sources

- Exact normalized-row `frequency`, `indicator_code`, `period`, `provider_dataset_code`, `source_payload`, and `territory_code`: OECD and Eurostat.
- Exact normalized-row `indicator_name` and `source`: WDI and Eurostat.
- Non-empty row attributes before loading: OECD and Eurostat.
- Attribute hash derived from non-empty attributes: OECD and Eurostat.
- Provider code/label dictionaries or codelist evidence: OECD and Eurostat.
- Explicit raw endpoint/access-method fields in top-level normalized metadata: OECD and Eurostat.
- Explicit territory label in normalized rows: WDI and Eurostat.
- Explicit indicator label in normalized rows: WDI and Eurostat.
- Period detail beyond a raw provider period string/year: WDI and Eurostat have direct year-like fields; Eurostat adds quarter fields; OECD derives year from `period` in loader.

## What remains source-specific

- WDI’s multiple raw artifact support bundle and per-indicator raw artifact list.
- WDI’s World Bank metadata extraction and source-specific unit enrichment for `NY.GDP.MKTP.CD`.
- OECD’s SDMX XML parsing, series/observation dimension extraction, SDMX attributes, codelist label parsing, and `USD_EXC`/`USD_PPP` basis evidence.
- Eurostat’s JSON-stat fixture shape, dimension dictionary handling, two-letter geo to ISO3 mapping, quarterly period parsing, seasonal-adjustment attributes, and provider code list/code loading.
- Release-key formulas.
- Staging table names and source-specific staging columns.
- Source-specific quality checks beyond row counts.
- Any future mapping acceptance/review decision.

## Transformations that are effectively identical

These transformations are repeated enough to be candidates for shared helper extraction:

1. Build/load `meta.source` from source identity.
2. Build/load `meta.dataset_release` from provider dataset, release key, raw URL/path/checksum, and metadata.
3. Build/load `meta.pipeline_run` from run key, source, release, input parameters, and artifact manifest.
4. Insert source-specific staging rows from a normalized row list.
5. Upsert provider indicators into `curated.dim_indicator`.
6. Upsert canonical country territories and provider territory mappings.
7. Upsert canonical periods and provider period mappings.
8. Upsert units into `curated.dim_unit`.
9. Upsert attribute sets, including the empty WDI case.
10. Insert facts into `curated.fact_observation` with the same fact grain.
11. Write two lineage events.
12. Write expected row-count quality checks.
13. Verify no duplicate fact grain in tests/smoke reports.

The repeated mechanics are real. The SQL text is duplicated because each loader maps from different source-specific staging names and fields, but the target model and load lifecycle are the same.

## Metadata that consistently survives into canonicalization

The canonical GDP snapshot and canonicalization state preserve or derive:

- `source_code`
- `provider_dataset_code`
- `release_key`
- `indicator_code`
- `indicator_name`
- canonical territory code/name
- frequency
- period label/start/end
- unit code
- value
- as-of date
- observation status
- source lineage counts
- quality-check counts
- provider evidence grouped by source/dataset/indicator
- release keys
- frequencies
- territories
- unit codes
- period labels
- observation counts

Notably, raw source payloads and staging-specific attributes do not all survive into the snapshot report directly, but unit/period/territory/indicator/fact/lineage/quality metadata survives in canonical or meta tables.

## Pipeline-by-pipeline comparison

| Stage | WDI | OECD | Eurostat | Reuse classification |
| --- | --- | --- | --- | --- |
| Acquisition/parsing | World Bank JSON support bundle parser | SDMX GenericData XML parser plus optional live fetch | JSON-stat fixture from architecture spike | Source-specific |
| Raw evidence metadata | Multiple raw artifacts with URL/status/content type/bytes/SHA/source metadata | Single raw XML metadata with endpoint/content type/bytes/SHA/path | Single raw JSON metadata with URL/status/content type/bytes/SHA/path/date header | Partially shared shape; source-specific extraction |
| Normalized metadata artifact | `source`, countries/indicators/date range/raw artifacts/rows | `source_code`, provider dataset/raw metadata/filters/rows | source/provider/raw/filter/dimension/rows plus spike notes | Partially shared; exact field names not converged |
| Observation row representation | Source-shaped World Bank row | Normalized SDMX observation row | Normalized Eurostat observation row | Partially shared; semantic convergence stronger than exact names |
| Staging table | `staging.wdi_observation` | `staging.oecd_sdmx_observation` | `staging.eurostat_namq_observation` | Source-specific tables should remain |
| Source/release/run metadata loading | Implemented in loader SQL | Implemented in loader SQL | Implemented in loader SQL | Fully shareable helper candidate |
| Indicator handling | `indicator_id/name` -> `dim_indicator` | `MEASURE` -> `dim_indicator`, code as name | `na_item` code/name -> `dim_indicator` | Partially shared target logic; source-specific extraction/labels |
| Territory handling | ISO3 already present | ISO3-like `REF_AREA` in current fixture | two-letter `geo` mapped to ISO3 | Partially shared canonical target; source-specific mapping remains |
| Period handling | annual year | annual SDMX period | quarterly JSON-stat period | Partially shared structured canonical target; source-specific parse/validate remains |
| Units | null -> `unknown`; WDI-specific later enrichment | `USD_EXC`/`USD_PPP` | `CP_MEUR` plus unit label | Partially shared unit-code handling; profiles remain downstream/source-specific evidence |
| Attributes | empty set | source attributes (`CONF_STATUS`, `DECIMALS`, `OBS_STATUS`) | constructed attributes incl. status/seasonal adjustment/provider context | Fully shared attribute-set target; source-specific construction |
| Provider code dictionaries | none | codelist label evidence file only | provider code list/code DB loading | Source-specific behavior with emerging shared metadata opportunity |
| Fact ingestion | same target fact grain | same target fact grain | same target fact grain | Fully shared target mechanics candidate |
| Lineage | raw_to_staging, staging_to_curated | raw_to_staging, staging_to_curated | raw_to_staging, staging_to_curated | Fully shared helper candidate |
| Validation/quality | staging/fact row checks | row/unit/attribute checks | row/quarter/provider-mapping checks | Partially shared: row-count baseline shared; structural checks source-specific |
| Smoke workflow | WDI runbook and isolated smoke | loader tests/smoke | loader tests/smoke | Partially shared isolation/reporting pattern |
| Canonicalization state | grouped from snapshot | grouped from snapshot | grouped from snapshot | Fully shared downstream grouping from canonical facts; source-specific caveats remain |

## Shared infrastructure opportunities

The following are evidence-backed opportunities, not implementation decisions.

### Good candidates for sharing now

1. Attribute hash helper

OECD and Eurostat independently hash sorted JSON attributes; WDI uses a constant empty hash. This is a low-risk shared helper.

2. Source/release/run metadata assembly

All loaders perform near-identical metadata upserts. The details of release-key construction and source metadata extraction should remain source-specific, but the object handed to SQL can be shared.

3. Observation row contract adapter

A thin adapter can convert WDI/OECD/Eurostat source-shaped rows into a common internal row shape for canonical insertion while preserving source payloads and source-specific staging.

4. Lineage event builder

All loaders emit the same two event types. This can be shared without changing source behavior.

5. Baseline row-count quality check builder

All loaders compare staging/fact counts against expected normalized row counts. Source-specific checks should remain separate.

6. Canonical fact grain assembly

All loaders ultimately produce facts with identical columns. A shared structure could describe these fact-grain inputs before SQL generation.

### Candidates that should remain partially shared

1. Period handling

The canonical target is shared, but annual WDI/OECD and quarterly Eurostat parsing differ. Share canonical-period insertion semantics only after preserving source-specific period parsing.

2. Territory handling

The canonical target is shared, but provider-territory-to-canonical mapping is source-specific. Eurostat proves the need for mapping logic; WDI/OECD current fixtures happen to use ISO3-like codes.

3. Unit handling

Unit code persistence is shared, but unit meaning/comparability profiles are downstream review/canonicalization evidence. Do not move unit comparability truth into ingestion.

4. Provider code dictionaries

Eurostat loads dictionaries; OECD has codelist label evidence; WDI has none. Shared dictionary infrastructure is plausible later, but current evidence is exactly two-source and uneven.

### Poor candidates for sharing now

1. Source acquisition clients.

The current implementation explicitly keeps World Bank JSON, SDMX XML, and Eurostat JSON-stat handling source-specific. That boundary is still correct.

2. Source-specific staging table schemas.

Staging is intentionally source-preserving. The common representation should not erase staging tables.

3. Canonicalization acceptance/review lifecycle.

The lifecycle is downstream of ingestion. It uses canonical facts and reports, not raw normalized source rows as authoritative truth.

4. Unit/currency conversion or frequency aggregation.

Current implementation repeatedly records that these are not implemented and must not be smuggled into an ingestion abstraction.

## Candidate Observed Intermediate Representation

If a future task extracts the observed representation, the evidence supports a minimal candidate with these sections.

### Top-level candidate fields

- `source_code`
- `source_name`
- `source_home_url`
- `provider_dataset_code`
- `release_key` or enough source-specific release evidence to compute it
- `raw_evidence`
  - source URL/endpoint/support bundle/raw path as available
  - content type/status/bytes/checksum as available
  - source-specific raw metadata
- `input_filters`
- `row_count`
- `expected_row_count` when explicit, otherwise default to `row_count`
- `observations`

### Candidate observation fields

- `provider_indicator_code`
- `provider_indicator_label` optional
- `provider_territory_code`
- `provider_territory_label` optional
- `provider_period_code`
- `frequency`
- structured period hints when known: year, quarter/month/date, start/end only after deterministic parsing
- `unit_code`
- `unit_label` optional
- `value`
- `observation_status`
- `decimal_precision` optional
- `attributes` defaulting to `{}`
- `source_payload`

### Candidate non-fields / boundaries

The candidate should not contain:

- accepted canonical mapping status;
- canonical concept truth;
- unit conversion output;
- frequency aggregation output;
- source plugins or base-loader inheritance;
- model-generated assertions;
- production/live database authority.

## Readiness assessment

Answer: Yes, with extraction discipline.

Sufficient implementation evidence has accumulated to justify a formal shared observation representation, because three independently implemented pipelines now repeat the same lifecycle:

- normalized artifact with rows and row counts;
- source/release/run metadata;
- source-specific staging;
- provider indicator/territory/period/unit/value extraction;
- canonical dimension/fact insertion;
- provider period/territory mappings;
- attribute set handling;
- lineage events;
- quality checks;
- combined-source canonical smoke validation;
- canonical snapshot and deterministic canonicalization evidence built from the shared canonical result.

The evidence is not strong enough to justify a generalized ingestion framework. The representation should be introduced only as a narrow extracted data shape and validation/helper layer around the repeated handoff between normalized source evidence and canonical loading.

The evidence also argues against overfitting to exact field names. WDI proves that the common representation must be extracted through adapters from existing behavior, not imposed by renaming all source artifacts first.

## Recommended follow-up implementation task

Recommended task title:

TASK-046 — Extract and validate the observed common ingestion representation for existing WDI/OECD/Eurostat loaders

### Scope

- Introduce a small internal representation or typed adapter layer extracted from the current WDI, OECD, and Eurostat normalized inputs.
- Keep source-specific acquisition/parsing and source-specific staging tables unchanged.
- Add fixture-backed tests proving that WDI, OECD, and Eurostat adapters produce the same canonical-load-ready representation from existing artifacts.
- Reuse only low-risk mechanics proven repeated today: attribute hashing, row-count expectations, lineage-event construction, and canonical fact-grain assembly.
- Preserve all current loader outputs and smoke reports.

### Constraints

- Do not change production database schema.
- Do not redesign ingestion.
- Do not add datasets or deepen existing datasets.
- Do not introduce model calls.
- Do not implement unit/currency conversion or frequency aggregation.
- Do not auto-advance canonical mapping state.
- Do not replace source-specific staging with a generic staging table.
- Do not introduce plugin/base-loader/orchestration framework concepts.

### Expected reusable value

- Reduces future source-onboarding effort by making the canonical-load handoff explicit.
- Reduces source-maintenance effort by removing repeated metadata/lineage/quality/fact-grain boilerplate.
- Improves testability by allowing all existing sources to validate against one observed representation shape before canonical loading.
- Improves future agent recovery by naming and localizing the true intermediate contract that has already emerged.

### Risks

- Over-abstraction: turning a thin representation into a framework would violate current evidence.
- Semantic leakage: unit comparability or canonical mapping review status could be accidentally moved into ingestion.
- Staging erosion: a shared representation could tempt removal of source-preserving staging tables.
- WDI mismatch: exact field-name convergence is weak, so adapters must preserve WDI behavior rather than forcing JSON renames.

### Why the abstraction is now justified

The abstraction is justified because the repeated implementation is no longer hypothetical. Three loaders now independently converge on the same canonical fact grain, same source/release/run metadata pattern, same provider period/territory mapping pattern, same lineage pattern, same quality-check baseline, and same canonicalization evidence source. Extracting the representation would reduce recurring implementation effort without changing authority, semantics, schema, or source-specific acquisition.

## Final boundary statement

MacroForge has not become a generalized ingestion platform. It has become a source-specific ingestion system with a real, repeated, canonical-load-ready observation representation hidden inside three loaders. The next task should extract that hidden representation carefully, preserving source-specific evidence and canonical-domain doctrine.
