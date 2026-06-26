# MacroForge Post-Freeze Architectural Assessment for v1.1

Date: 2026-06-26
Status: completed assessment; no implementation
Scope: current implementation after TASK-045 v1 freeze-readiness hardening

## Boundaries preserved

This assessment did not implement ingestion features, add sources, change schemas, mutate canonical data, write to PostgreSQL, create autonomous agents, add orchestration/runtime frameworks, or approve any mapping/conversion/aggregation policy.

The assessment is based on current implementation state, not pre-v1 intentions. Evidence inspected included:

- `CONSTITUTION.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `src/macroforge/wdi.py`
- `src/macroforge/oecd_sdmx.py`
- `src/macroforge/wdi_loader.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `src/macroforge/eurostat_namq_loader.py`
- `src/macroforge/db_helpers.py`
- `src/macroforge/combined_source_smoke.py`
- `src/macroforge/canonical_gdp_snapshot.py`
- `src/macroforge/canonicalization_state.py`
- `db/migrations/001_v0_schema_foundation.sql`
- `db/migrations/002_oecd_sdmx_staging.sql`
- `db/migrations/003_canonical_domain_dimensions.sql`
- `db/migrations/004_eurostat_namq_staging.sql`
- normalized WDI/OECD/Eurostat fixture metadata under `data/metadata/`
- `docs/data/source-contract.md`
- `docs/data/source-catalog.md`
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
- `docs/architecture/metaharvest-trigger-gated-consultation.md`
- `artifacts/manifests/canonical_assets.json`
- v1 closure, operational validation, comparability, and eligibility reports
- current tests under `tests/`

MetaHarvest consultation was trigger-gated and advisory only. The helper was run for this architectural assessment scope because the request concerns architecture, source contracts, canonicalization, and framework decisions. MacroForge remains authoritative.

## Executive assessment

MacroForge v1 has naturally evolved a reusable ingestion lifecycle, but not a generalized ingestion framework.

The project now has three different source implementations that all converge on a shared PostgreSQL canonical-domain substrate:

```text
source evidence / bounded fixture
-> source-specific parser or normalized metadata
-> source-specific staging table
-> shared meta/source/release/run records
-> shared canonical dimensions and provider mappings
-> shared curated.fact_observation grain
-> shared lineage_event and quality_check patterns
-> combined-source validation smoke
-> canonical GDP snapshot / eligibility artifacts
```

The reusable center of gravity is therefore not source acquisition. It is the post-normalization, pre-research layer: provider evidence, staging-to-curated loading contracts, canonical-domain dimensions, mapping/caveat state, lineage, quality checks, and fixture-backed replay.

The highest-leverage v1.1 work is to refactor existing ingestion infrastructure before expanding coverage. Specifically: extract a small, explicit `normalized observation package` contract plus shared loader/reporting mechanics from the repeated WDI/OECD/Eurostat patterns. This should be a thin contract and helper layer, not a source plugin framework.

The assessment rejects adding a new external dataset as the next task. A fourth source would force more duplicated loader SQL, quality-check boilerplate, fixture rules, and human/LLM interpretation before the existing repeated patterns have been canonized. That would increase surface area faster than it increases platform leverage.

## Current ingestion lifecycle

### 1. Source selection and governance framing

Responsibilities:

- Decide whether a source/scope is justified.
- Preserve source-specific-first doctrine.
- Prevent scope creep into broad frameworks, dashboards, live database writes, conversion policy, or unsupported research claims.
- Record durable decisions/tasks/reports in ProjectForge artifacts.
- Use MetaHarvest only as bounded advisory context for architecture/governance changes.

Degree of reuse:

- High at the ProjectForge governance layer: state files, task artifacts, reports, decisions, handoffs, summaries, and coherence checks are shared.
- Medium inside MacroForge-specific source governance: `docs/data/source-contract.md`, `source-catalog.md`, decision reports, and source-specific runbooks exist but are not yet a single checklist-driven source-onboarding template.

Duplicated logic:

- Each source/task tends to restate boundaries: no live `macro`, no generalized framework, no conversion/aggregation, no silent canonical truth.
- Source evidence expectations recur in prose rather than a single machine-checkable source onboarding contract.

Canonization opportunity:

- Create a `source onboarding assessment template` that records: source code, dataset code, access mode, credentials, license, raw artifact path/checksum, normalized package path, staging table, loader, expected rows, canonical dimension mappings, quality checks, replay command, forbidden shortcuts.
- Keep it file-backed. Do not create a runtime registry until repeated query needs prove it.

Remain source-specific or shared:

- Shared governance template: yes.
- Automated source approval authority: no.
- Runtime source plugin framework: no.

### 2. Source acquisition

Responsibilities:

- Obtain bounded evidence from source APIs or tracked support bundles/fixtures.
- Preserve raw artifacts and checksums.
- Avoid credentials/paid APIs/live production assumptions.
- Produce project-layout artifacts under `data/raw`, `data/metadata`, and `artifacts/reports`.

Current implementation:

- WDI has a support-bundle path in `src/macroforge/wdi.py` that can regenerate raw/metadata evidence without live network.
- OECD has `src/macroforge/oecd_sdmx.py` for no-key SDMX fetch/parsing, bounded fixture-backed normalization, raw metadata, and codelist label enrichment.
- Eurostat currently has recorded normalized/raw fixture evidence and a PostgreSQL loader, but no comparable acquisition module surfaced in `src/macroforge`; Eurostat acquisition remains more fixture/report-driven than code-driven.

Degree of reuse:

- Low to medium.
- Shared filesystem layout exists.
- Shared artifact expectations exist informally.
- Protocol parsing is source-specific: World Bank JSON shape, OECD SDMX XML, Eurostat JSON-stat-like normalized fixture.

Duplicated logic:

- Raw artifact path/checksum capture.
- Source URL/home URL/provider dataset metadata.
- Bounded filter descriptions.
- Expected row counts.
- Normalized JSON writing and report writing.

Canonization opportunity:

- Define shared acquisition metadata fields and fixture manifest shape.
- Add helper functions for checksum/path/byte metadata and deterministic artifact writing.
- Do not abstract protocol parsers yet; WDI, SDMX, and Eurostat JSON-stat are genuinely different.

Remain source-specific or shared:

- Protocol fetching/parsing: source-specific.
- Raw artifact metadata/checksum/manifest writing: shared.
- Fixture persistence guard: shared.

### 3. Source parsing and normalized metadata

Responsibilities:

- Parse source payload into bounded observations.
- Preserve provider-specific dimensions and attributes.
- Produce normalized JSON consumed by loaders.
- Avoid asserting canonical truth during parsing.

Current implementation:

WDI normalized rows contain:

- `country_id`, `country_name`, `countryiso3code`
- `indicator_id`, `indicator_name`
- `date`
- `value`
- `unit`, `decimal`, `obs_status`, `source`

OECD normalized rows contain:

- `source_code`, `provider_dataset_code`
- `indicator_code`, `territory_code`, `frequency`, `period`, `unit`, `value`
- `attributes`
- `source_payload` with series and observation dimensions

Eurostat normalized rows contain:

- `source`, `provider_dataset_code`
- `indicator_code`, `indicator_name`
- `territory_code`, `territory_name`
- `frequency`, `period`, `period_year`, `period_quarter`
- `unit`, `unit_name`, `seasonal_adjustment`, `seasonal_adjustment_name`
- `value`, `observation_status`, `decimal_precision`, `as_of_date`
- `source_payload`

Degree of reuse:

- Medium conceptually, low formally.
- All three normalized artifacts now describe observation-like records with provider source, dataset, indicator, territory, period/frequency, unit/profile, value, status/attributes, and raw/source payload evidence.
- Field names and richness differ across sources.

Duplicated logic:

- Each loader reads a JSON normalized artifact and assumes source-specific keys.
- Each source encodes provider dimensions/attributes differently.
- Each source independently decides how much raw payload to preserve.

Emergent intermediate representation:

A common intermediate representation already exists, but only as fragments. It is not a named abstraction in code.

The fragments are:

1. A normalized observation list: each source emits `rows` with observation records.
2. Provider identity fields: source code, provider dataset/release code, provider indicator code/name.
3. Domain coordinates: territory, period/frequency, unit/profile, value, observation status.
4. Source evidence fields: raw artifact path/checksum, source URL/home URL, payload snippets, filters, metadata/codelists.
5. Expected replay metadata: row counts and bounded filters.
6. Provider dimension evidence: OECD attributes/source payload, Eurostat dimensions/source payload, WDI country/indicator metadata.

This is enough to canonize a `NormalizedObservationPackage` contract. It is not enough to justify a full ingestion framework with pluggable protocol adapters.

Remain source-specific or shared:

- Shared: package-level contract and validation.
- Source-specific: payload parser and provider-specific dimension interpretation.

### 4. Staging schema

Responsibilities:

- Preserve source-shaped observations before curated facts.
- Avoid forcing provider-specific columns into canonical fact tables.
- Provide audit/debug boundary between normalized JSON and curated load.

Current implementation:

- `staging.wdi_observation` is in migration 001.
- `staging.oecd_sdmx_observation` is in migration 002.
- `staging.eurostat_namq_observation` is in migration 004.

Degree of reuse:

- Medium in intent, low in DDL shape.
- Each staging table is source-specific, which remains appropriate.
- All staging tables include source/run/release linkage and observation fields sufficient for source-specific replay.

Duplicated logic:

- Repeated pipeline_run/dataset_release/source foreign key handling.
- Repeated source-specific insert/upsert and idempotency patterns.
- Repeated count checks.

Canonization opportunity:

- Keep staging tables source-specific.
- Extract shared loader helper functions for inserting source/release/run records and rendering common CTEs.
- Create a required staging contract checklist rather than one universal staging table.

Remain source-specific or shared:

- Staging tables: source-specific.
- Shared staging contract/checklist and loader boilerplate: shared.

### 5. Canonical-domain mapping and curated facts

Responsibilities:

- Map source-shaped observations into canonical-domain dimensions.
- Preserve provider period/territory mapping records.
- Preserve source-specific indicator identity without claiming universal economic truth.
- Produce `curated.fact_observation` at a stable grain.

Current implementation:

Reusable schema already exists:

- `curated.dim_indicator`
- `curated.dim_territory`
- `curated.dim_period`
- `curated.dim_unit`
- `curated.dim_attribute_set`
- `curated.fact_observation`
- `meta.provider_period_mapping`
- `meta.provider_territory_mapping`
- `meta.provider_code_list`
- `meta.provider_code`

Degree of reuse:

- High in schema.
- Medium in loader code.
- WDI, OECD, and Eurostat loaders all touch the same core meta/curated tables and provider mapping concepts.

Duplicated logic:

- Each loader independently builds canonical period rows.
- Each loader independently maps provider territory codes to canonical ISO3 territories.
- Each loader independently inserts units, attribute sets, facts, provider mappings.
- Each loader independently handles unknown/default units/attributes.

Canonization opportunity:

- Add shared deterministic functions or SQL builders for:
  - annual/quarterly period derivation;
  - provider period mapping insertion;
  - country territory insertion from ISO2/ISO3/provider code plus name;
  - provider territory mapping insertion;
  - unit/profile insertion;
  - attribute-set canonical JSON hashing or natural-key handling;
  - fact upsert grain.

Remain source-specific or shared:

- Canonical dimension/fact schema: shared.
- Mapping policy/semantic interpretation: source-specific and review-gated.
- Mechanical dimension/fact upsert patterns: shared.

### 6. Lineage and quality checks

Responsibilities:

- Record raw-to-staging and staging-to-curated events.
- Record expected staging/fact rows and source-specific semantic checks.
- Preserve replay/debug evidence without treating reports as truth.

Current implementation:

All three loaders insert `meta.lineage_event` and `meta.quality_check` records with near-identical structure. WDI lacks checksum in lineage where OECD/Eurostat include it, but the pattern is otherwise repeated. Combined smoke aggregates checks across all sources.

Degree of reuse:

- High conceptually.
- Low to medium in code: repeated SQL blocks exist inside every loader.

Duplicated logic:

- `WITH source_row`, `run_row`, `INSERT INTO meta.lineage_event` boilerplate.
- `INSERT INTO meta.quality_check` boilerplate.
- Expected row count checks.
- Source-specific check names with similar semantics.

Canonization opportunity:

- Extract a shared lineage/quality SQL helper layer or templated CTE builder.
- Define a small quality-check spec format:
  - check name;
  - scope;
  - severity;
  - observed SQL;
  - expected value;
  - pass expression;
  - details.
- Keep source-specific semantic checks source-owned.

Remain source-specific or shared:

- Check registry/spec mechanics: shared.
- Check content and thresholds: source-specific unless obviously universal.

### 7. Validation and smoke workflows

Responsibilities:

- Reconstruct bounded evidence in isolated PostgreSQL databases.
- Refuse live/default `macro` database writes.
- Apply explicit migrations in order.
- Load sources, validate counts/mappings/lineage/quality, write deterministic reports, drop temporary DBs.

Current implementation:

- `wdi_smoke.py` performs repaired WDI-only isolated smoke.
- `combined_source_smoke.py` runs all source loaders against migrations 001-004.
- `canonical_gdp_snapshot.py` builds a research-facing snapshot from an isolated combined DB.
- Tests cover live-DB refusal, fake-runner behavior, isolated PostgreSQL behavior when available, report writing, and fixture persistence.

Degree of reuse:

- Medium.
- Combined smoke and snapshot duplicate plan construction, migration path handling, live DB refusal, runner protocol, temp DB naming, report writing, and cleanup mechanics.

Duplicated logic:

- `CommandRunner`/`SubprocessRunner` patterns exist in multiple modules.
- Temporary database naming/refusal logic repeats.
- Migration path tuples repeat.
- Source normalized fixture paths repeat.
- Report summaries/check aggregation repeat.

Canonization opportunity:

- Extract an `isolated_db_workflow` helper for temp DB naming, live DB refusal, migration application, runner protocol, cleanup, and report writing.
- Extract a `current_fixture_paths` or manifest reader only if backed by a file already used by tests; avoid a runtime source registry prematurely.

Remain source-specific or shared:

- Isolated DB lifecycle: shared.
- Source loader sequence and validation assertions: shared enough for helper, but source-specific counts/checks remain source-owned.

### 8. Canonicalization, eligibility, and reusable knowledge

Responsibilities:

- Represent provider evidence, mapping proposals, review outcomes, caveats, and eligibility boundaries.
- Prevent false comparability.
- Route downstream use with deterministic artifacts.

Current implementation:

- `canonicalization_state.py` creates deterministic file-backed canonicalization state/proposal evidence.
- Canonicalization reports define WDI governed provisional status, OECD/Eurostat deferred status, OECD unit-basis split, and advancement requirements.
- `canonical_assets.json` is a narrow pointer registry for canonicalization artifacts.
- `gdp-eligibility-classification-20260619.json` is the compact downstream eligibility contract for current GDP evidence.

Degree of reuse:

- Medium to high as knowledge artifacts.
- Low as executable loader infrastructure.

Duplicated logic:

- Review routing, caveat wording, evidence pointers, forbidden shortcuts, and advancement requirements recur across artifacts.
- The same semantic blockers appear in multiple places: no conversion, no aggregation, no accepted truth, no cross-source comparable GDP without review.

Canonization opportunity:

- Create reusable review/eligibility templates and checklists.
- Eventually materialize canonicalization/eligibility metadata into PostgreSQL only after repeated query need. Current file-backed state is sufficient and safer.

Remain source-specific or shared:

- Review lifecycle mechanics and eligibility categories: shared.
- Indicator-specific policy decisions: source/domain-specific and human-governed.

## Reusable infrastructure inventory

### Already generic / shared today

1. ProjectForge operating layer
   - State files, handoffs, tasks, reports, summaries, coherence checks, continuity framework.

2. Database helper mechanics
   - `sql_literal`, `jsonb_literal`, `run_psql_file`, `psql_scalar`, `psql_int`, `parse_pipe_counts`, `write_json_report`.

3. Canonical-domain PostgreSQL substrate
   - Shared `meta`, `staging`, and `curated` schemas.
   - Shared source/release/run/lineage/quality tables.
   - Shared canonical dimensions and `curated.fact_observation`.
   - Shared provider period/territory/code mapping tables.

4. Isolated reconstruction posture
   - Temporary DB creation.
   - Live `macro` refusal.
   - Explicit migrations.
   - Drop DB cleanup.
   - Deterministic reports.

5. Canonical GDP snapshot and combined smoke boundary
   - Curated/meta-only reporting.
   - Combined-source quality/mapping/fact-grain checks.

6. File-backed canonicalization/eligibility knowledge
   - Proposal/review state artifacts.
   - Canonical asset manifest.
   - GDP eligibility classification categories.

7. Trigger-gated MetaHarvest consultation helper
   - Advisory architecture/governance preflight.
   - Non-authoritative, bounded retrieval.

### Repeated concepts that should become shared infrastructure

1. Normalized observation package contract
   - Package metadata: source code, source name, source URL/home URL, provider dataset code, access method, filters, raw artifact path/checksum, row count, created/fetched timestamp.
   - Row core: provider indicator code/name, territory code/name, period/frequency, unit/profile, value, observation status, attributes/source payload.
   - Replay: expected row count, fixture paths, raw checksums.

2. Fixture manifest and persistence guard
   - Required raw/metadata files.
   - Git-ignore status.
   - Checksums.
   - Reconstruction role.

3. Source/release/run insertion helper
   - Common `meta.source`, `meta.dataset_release`, `meta.pipeline_run` upsert pattern.

4. Canonical period helper
   - Annual and quarterly period derivation.
   - Provider period mapping insertion.
   - Explicit non-aggregation boundary.

5. Canonical territory helper
   - Country territory creation with ISO3-preserved identity.
   - Provider territory mapping insertion.
   - Aggregate/economic-area deferral boundary.

6. Unit/profile helper
   - Unit code/label/profile insertion.
   - Unknown unit handling.
   - No-conversion caveats.

7. Attribute-set helper
   - Stable JSONB attribute set insertion and reuse.

8. Fact upsert helper
   - Stable source/indicator/territory/period/unit/attribute/as_of grain.
   - Duplicate prevention checks.

9. Lineage event helper
   - Standard raw-to-staging and staging-to-curated event insertion with optional checksums.

10. Quality-check spec helper
   - Reusable representation for count/mapping/duplicate/failing checks.

11. Isolated DB workflow helper
   - Runner protocol, temp DB naming, live DB refusal, migration application, cleanup, report-path handling.

12. Source onboarding assessment template
   - Governance checklist for future sources.

### Repeated concepts that are only accidental similarity

1. WDI JSON, OECD SDMX XML, and Eurostat JSON-stat parsing
   - These are protocol-specific and should remain source-specific.

2. Dataset-specific dimensions
   - OECD `UNIT_MEASURE`, `CONF_STATUS`, `DECIMALS`; Eurostat seasonal adjustment and unit labels; WDI country/indicator metadata are not the same semantic objects.

3. Quality-check thresholds
   - Expected row counts and expected provider mapping counts are fixture-specific.

4. Codelist enrichment
   - OECD codelist parsing is reusable only after a second SDMX source proves the same mechanics; current evidence supports bounded OECD-specific code.

5. GDP eligibility categories as universal macro categories
   - The category structure may generalize, but current classifications are GDP-specific and should not become universal policy without another domain proving it.

## Canonization opportunities

Priority-ranked canonization opportunities:

1. Canonize the normalized observation package contract.
   - This is the clearest emergent IR.
   - It reduces new source loader ambiguity without constraining acquisition protocols.
   - It should be validated by tests against existing WDI/OECD/Eurostat artifacts before any new source is added.

2. Canonize source fixture/replay manifests.
   - TASK-045 showed clean-clone fixture persistence is operationally important.
   - A manifest would remove human guesswork around which ignored/unignored files are required.

3. Canonize loader boilerplate around source/release/run, lineage, quality checks, and canonical dimension/fact upserts.
   - Repetition is now proven across three loaders.
   - This reduces deterministic engineering per source while preserving source-specific staging and parsing.

4. Canonize isolated workflow mechanics.
   - Combined smoke and canonical snapshot repeat enough lifecycle code to justify a small helper.
   - This improves testability and prevents stale workflow drift like the pre-TASK-044 WDI smoke issue.

5. Canonize review/eligibility templates.
   - Human decisions recur around mapping status, unit basis, frequency, conversion, aggregation, report eligibility, and forbidden shortcuts.
   - Templates reduce human cognitive load without pretending semantic approval is automatic.

6. Canonize provider metadata evidence extraction into reusable knowledge records.
   - Provider indicator names, unit labels, codelist labels, methodology snippets, and dimension context should accumulate as evidence over time.
   - Do this file-backed first; PostgreSQL persistence can follow proven query pressure.

Do not canonize yet:

- A generalized acquisition plugin framework.
- A universal staging table.
- A universal SDMX framework from one OECD SDMX source.
- Conversion/currency/frequency aggregation policy.
- Autonomous canonicalization agents.
- Mart/dashboard/reporting framework.

## AI opportunity inventory

The goal is to reduce future LLM reasoning, not increase it. AI should be used only for bounded semantic proposal work where deterministic rules are insufficient, and every output should become reusable evidence or deterministic rules when possible.

### Good bounded local-LLM candidates later

1. Indicator mapping proposal
   - Input: provider indicator code/name/description, dataset context, codelist labels, examples.
   - Output: proposed canonical concept relationship, confidence band, evidence citations, caveats.
   - Authority: proposal only; high-impact concepts remain review-gated.

2. Unit/profile interpretation
   - Input: unit code, unit label, source methodology, observed magnitudes, provider dimensions.
   - Output: unit/profile candidate, conversion blockers, comparability caveats.
   - Authority: proposal only.

3. Metadata interpretation and summarization
   - Input: provider documentation snippets, source contract, codelists.
   - Output: compact source evidence summary for humans and future deterministic rules.

4. Synonym and concept-neighbor discovery
   - Input: provider labels/descriptions across sources.
   - Output: candidate synonym groups or distinct-profile warnings.

5. Schema understanding for new sources
   - Input: bounded raw payload and provider docs.
   - Output: source-specific onboarding notes: dimensions, likely observation fields, units, frequencies, identifiers, risks.

6. Validation suggestions
   - Input: normalized package and loader report.
   - Output: proposed quality checks and expected invariants to review/turn deterministic.

7. Documentation/runbook summarization
   - Input: generated source artifacts and tests.
   - Output: draft runbook/source contract sections, not final authority.

### Reasoning that should become deterministic rules over time

1. Annual and quarterly period parsing.
2. ISO3 country identity and provider territory mapping.
3. Raw artifact checksum validation.
4. Expected fixture row count validation.
5. No live `macro` database refusal.
6. Duplicate fact grain detection.
7. Missingness over bounded source-specific universes.
8. Known unit-code handling once reviewed, such as existing WDI current-USD metadata, OECD `USD_EXC`/`USD_PPP`, and Eurostat `CP_MEUR` caveats.
9. Eligibility routing categories once human-approved for a concept/domain.
10. Repeated codelist label extraction for a protocol after at least two sources justify it.

### Human decisions that should become reusable knowledge

1. What counts as the same canonical economic concept.
2. Whether a unit/profile is comparable, profile-specific, deferred, unsupported, or blocked.
3. Whether conversion/aggregation is allowed and under what evidence/policy.
4. Whether a mapping can advance from proposed/deferred to provisional/accepted.
5. Whether a source's license/access/coverage is acceptable.
6. Whether a data release is good enough for downstream use.
7. Whether a validation failure is a source problem, loader bug, or policy blocker.

These decisions should accumulate as review artifacts, templates, accepted mapping state, caveat catalogs, and eventually deterministic eligibility rules.

## Proposed MacroForge v1.1 roadmap

### Wave 1 — Refactor emerged ingestion contract before expansion

#### Task 1: Define and validate `NormalizedObservationPackage` v1

Objective:

- Create a file-backed contract and validator for normalized source evidence packages using existing WDI/OECD/Eurostat artifacts.

Motivation:

- A common intermediate representation already exists as fragments but is not named or validated.
- Future sources currently require humans/LLMs to infer the expected normalized shape from loader code.

Expected reusable value:

- High. Every future source can target the same package contract before loader promotion.

Implementation complexity:

- Medium. Requires a contract doc, validator, fixtures/tests, and possibly non-breaking adapter metadata for existing artifacts.

Dependencies:

- Existing normalized WDI/OECD/Eurostat fixture files.
- No schema migration required.

Estimated reduction in future engineering effort:

- High. New source parser output becomes testable before database loader work.

Estimated reduction in future human effort:

- Medium-high. Reviewers can inspect one common package shape.

Estimated reduction in future LLM reasoning:

- High. LLMs no longer need to infer expected observation metadata from scattered examples.

#### Task 2: Add fixture/replay manifest and clean-clone verification

Objective:

- Record required raw/metadata fixture files, checksums, roles, and reconstruction commands in one manifest; test it.

Motivation:

- TASK-045 exposed fixture persistence as a freeze-readiness blocker.

Expected reusable value:

- High. Future sources become replayable and clean-clone safe by construction.

Implementation complexity:

- Low-medium.

Dependencies:

- Current unignored fixture evidence.
- Existing fixture persistence test.

Estimated reduction in future engineering effort:

- Medium.

Estimated reduction in future human effort:

- High. No manual rediscovery of required fixture files.

Estimated reduction in future LLM reasoning:

- Medium. Agents can read one manifest instead of searching `data/` and reports.

#### Task 3: Extract isolated DB workflow helper

Objective:

- Share temp DB naming, live DB refusal, migration application, runner protocol, cleanup, and report path mechanics across WDI smoke, combined smoke, and snapshot workflows.

Motivation:

- Stale workflow drift caused TASK-044. The pattern is repeated.

Expected reusable value:

- Medium-high. All future loaders/smokes inherit safer operational behavior.

Implementation complexity:

- Medium.

Dependencies:

- Existing tests for WDI smoke, combined smoke, canonical snapshot.

Estimated reduction in future engineering effort:

- Medium.

Estimated reduction in future human effort:

- Medium.

Estimated reduction in future LLM reasoning:

- Medium. Fewer bespoke workflow variants to reason about.

### Wave 2 — Loader boilerplate canonization

#### Task 4: Extract shared source/release/run + lineage/quality helpers

Objective:

- Remove repeated SQL boilerplate from WDI/OECD/Eurostat loaders for meta records, lineage events, and quality checks.

Motivation:

- All three loaders independently implement near-identical `meta.source`, `dataset_release`, `pipeline_run`, `lineage_event`, and `quality_check` mechanics.

Expected reusable value:

- High.

Implementation complexity:

- Medium-high because refactor must preserve existing SQL behavior and reports.

Dependencies:

- Tests must lock current loader outputs/idempotency before refactor.
- Prefer after `NormalizedObservationPackage` contract.

Estimated reduction in future engineering effort:

- High.

Estimated reduction in future human effort:

- Medium.

Estimated reduction in future LLM reasoning:

- Medium-high.

#### Task 5: Extract canonical dimension/fact upsert helpers

Objective:

- Share mechanical period, territory, unit, attribute-set, provider mapping, and fact upsert patterns while preserving source-specific semantics.

Motivation:

- Canonical-domain schema is already shared; loader code still repeats the mechanics.

Expected reusable value:

- Very high for source onboarding.

Implementation complexity:

- High. This is the riskiest refactor and should follow smaller helper extraction.

Dependencies:

- Task 4 preferred.
- Strong loader idempotency tests and combined smoke verification.

Estimated reduction in future engineering effort:

- Very high.

Estimated reduction in future human effort:

- Medium.

Estimated reduction in future LLM reasoning:

- High.

### Wave 3 — Reusable semantic knowledge

#### Task 6: Create review/eligibility template pack

Objective:

- Turn recurring mapping-status, unit-basis, deferred advancement, and eligibility decision structures into reusable templates/checklists.

Motivation:

- Human decisions are repetitive but should not become automatic authority.

Expected reusable value:

- High for governance quality and future source review.

Implementation complexity:

- Low-medium.

Dependencies:

- Existing canonicalization and eligibility reports.

Estimated reduction in future engineering effort:

- Low.

Estimated reduction in future human effort:

- High.

Estimated reduction in future LLM reasoning:

- High. Future assessments can fill templates rather than reason from scratch.

#### Task 7: Build provider metadata evidence inventory from existing sources

Objective:

- Extract existing provider indicator/unit/dimension/codelist evidence into a reusable file-backed inventory.

Motivation:

- AI-assisted canonicalization needs bounded evidence records; current evidence is scattered.

Expected reusable value:

- Medium-high.

Implementation complexity:

- Medium.

Dependencies:

- Normalized package contract and existing canonicalization evidence.

Estimated reduction in future engineering effort:

- Medium.

Estimated reduction in future human effort:

- Medium.

Estimated reduction in future LLM reasoning:

- High. Local LLMs can consume compact evidence instead of raw reports.

### Wave 4 — Only after infrastructure refactor: next data coverage

#### Task 8: Add or deepen a source only when a concrete downstream question requires it

Objective:

- Use the new contract/helper infrastructure to onboard or deepen evidence with lower effort.

Motivation:

- The point of v1.1 infrastructure is to make this cheaper than the WDI/OECD/Eurostat implementations.

Expected reusable value:

- Medium, because source-specific value depends on downstream need.

Implementation complexity:

- Medium-high but should be lower after Waves 1-2.

Dependencies:

- At least Tasks 1-3, preferably Task 4.

Estimated reduction in future engineering effort:

- N/A as this consumes the infrastructure rather than creating it.

Estimated reduction in future human effort:

- Depends on source.

Estimated reduction in future LLM reasoning:

- Depends on source.

## Prioritized implementation backlog for v1.1

1. Define and validate `NormalizedObservationPackage` v1 over existing WDI/OECD/Eurostat artifacts.
2. Add fixture/replay manifest and clean-clone verification.
3. Extract isolated DB workflow helper.
4. Extract shared source/release/run and lineage/quality helper mechanics.
5. Extract canonical dimension/fact upsert helper mechanics.
6. Create review/eligibility template pack.
7. Build provider metadata evidence inventory from existing sources.
8. Reassess whether to deepen WDI/OECD/Eurostat or add a fourth source after the refactor proves effort reduction.

## Dataset recommendation

Recommendation: refactor existing ingestion infrastructure before expanding coverage.

Chosen option: 3. Refactor existing ingestion infrastructure before expanding coverage.

Justification:

- The current bottleneck is no longer whether MacroForge can ingest a source. It can ingest WDI, OECD, and Eurostat into shared canonical-domain facts.
- The repeated work is now clear: normalized artifact shape, fixture persistence, meta/run/release setup, canonical period/territory/unit mapping, lineage, quality checks, isolated DB workflows, and governance templates.
- Adding a fourth dataset now would increase duplicated loader and governance work before these patterns are canonized.
- Deepening an existing source would improve coverage but would not attack the main compounding bottleneck unless framed as infrastructure extraction.
- The long-term objective says every new source should require progressively less deterministic engineering, human intervention, and LLM reasoning. That will not happen reliably until the emerged intermediate representation and loader mechanics are made explicit.

## Single next implementation task recommendation

Recommended next task:

```text
TASK-046 — Define and validate NormalizedObservationPackage v1 for existing WDI/OECD/Eurostat evidence
```

Objective:

- Create a minimal file-backed normalized observation package contract and validator based entirely on existing WDI/OECD/Eurostat normalized artifacts.

Scope:

- Contract documentation under `docs/data/` or `docs/architecture/`.
- Validator module that reads current normalized artifacts and reports contract compliance.
- Tests covering WDI, OECD, and Eurostat current fixture packages.
- No loader behavior changes unless required only to add non-semantic compatibility metadata.
- No new source.
- No database schema migration.
- No conversion, aggregation, or mapping approval.
- No AI/model calls.

Why this task first:

- It canonizes the strongest emerged abstraction without inventing a new framework.
- It directly reduces future source parser/loader ambiguity.
- It gives future local LLM or deterministic tooling a compact evidence input.
- It is safer than refactoring loaders first because it can be validated around existing artifacts before changing execution paths.

Expected acceptance criteria:

- Existing WDI/OECD/Eurostat normalized artifacts validate or produce documented, explicitly accepted adapter gaps.
- The contract distinguishes required core observation fields from optional provider-specific evidence.
- The contract preserves source-specific payloads and does not collapse provider semantics into canonical truth.
- Full test suite and coherence checks pass.

## Final verdict

MacroForge should not expand coverage next. It should first turn the naturally emerged normalized observation and loader/replay patterns into small shared infrastructure. This is the highest-leverage v1.1 path because it compounds: every future source should target a clearer contract, reuse safer operational mechanics, and require less repeated human/LLM reconstruction of what MacroForge already learned from WDI, OECD, and Eurostat.
