# Foundational Capability Extraction Candidate Selection

Date: 2026-06-27
Status: recommendation only; no implementation performed
Trigger: `foundational_capability_extraction`

## Purpose

Determine which repeated post-observed-boundary behavior should become MacroForge's first shared foundational platform capability.

This report does not implement the capability. It records implementation evidence, ArchitectureHarvest/MetaHarvest consultation evidence, candidate comparison, rejection rationale, and a narrow future implementation plan.

## Authority boundary

MacroForge remains authoritative. MetaHarvest/ArchitectureHarvest consultation is advisory historical architecture evidence only. No recommendation here changes the Constitution, mutates canonical data, adopts external runtime platforms, creates source-framework authority, or approves implementation by itself.

## Context used

- `CONSTITUTION.md` Strategic Constitution v1.1, especially extraction rules and ArchitectureHarvest trigger.
- `state/active_goal.md`, `state/project_state.md`, `state/architecture.md`, and `context/latest_handoff.md`.
- `docs/architecture/capability-maturity-model.md`.
- `docs/architecture/metaharvest-trigger-gated-consultation.md`.
- `architecture/architectureharvest/relevance_map.yaml`.
- `artifacts/tasks/TASK-046-extract-observed-common-ingestion-representation.md`.
- `src/macroforge/observed_ingestion.py`.
- `src/macroforge/deterministic_change_verification.py`.
- `src/macroforge/wdi_loader.py`.
- `src/macroforge/oecd_sdmx_loader.py`.
- `src/macroforge/eurostat_namq_loader.py`.
- `tests/test_observed_ingestion.py`, `tests/test_deterministic_change_verification.py`, and `tests/test_combined_source_smoke.py`.

## ArchitectureHarvest consultation summary

Command run:

```bash
python3 tools/consult_metaharvest.py --allow-governance-deeper-cap --json --task-summary 'foundational capability extraction: select first shared deterministic post-observed-boundary infrastructure from converged implementation evidence; evaluate lineage generation, quality-check handling, provider metadata handling, canonical dimension mechanics, canonical load/upsert mechanics, validation helpers; investigate mature patterns, failure modes, over-abstraction risks, minimal extraction, reasons not to extract; no implementation.'
```

Consultation decision:

- Action: `consult`.
- Matched triggers:
  - `source_contract_design_changes`
  - `lineage_or_validation_registry_changes`
  - `foundational_capability_extraction`
- Confidence: Medium.
- Retrieved records:
  - `retrieval/problem_catalog.yaml`
  - `retrieval/retrieval_index.yaml`
  - `component_cards/openmetadata-schema-first-entity-model.yaml`
  - `component_cards/openmetadata-lineage-resource.yaml`
  - `component_cards/openmetadata-governance-taxonomy.yaml`

Relevant advisory patterns:

1. Schema-first metadata entity model
   - Useful pattern: compact schemas for canonical metadata concepts and lineage references.
   - Failure modes addressed: provider-specific metadata shape leaks, unclear asset identity, unvalidated metadata fields.
   - Failure modes introduced: schema maintenance burden and catalog-platform complexity.
   - MacroForge implication: prefer a tiny typed contract if extracting metadata/lineage, but do not adopt a metadata catalog or platform.

2. Lineage edge + details interface
   - Useful pattern: represent lineage as explicit upstream/downstream edges with details, source type/checksum/query/pipeline context where useful.
   - Failure modes addressed: unreviewed lineage edits, impact-analysis gaps, loss of transformation context.
   - Failure modes introduced: graph/index complexity and authorization overhead.
   - MacroForge implication: lineage extraction is plausible only as file/code-local deterministic edge/event emission. Do not build graph indexes, runtime lineage APIs, authorization subsystems, or catalog integration.

3. Governance taxonomy vocabulary
   - Useful pattern: track only governance fields that answer real retrieval/audit questions.
   - Failure modes addressed: semantic drift, unclear ownership, absent policy context.
   - Failure modes introduced: taxonomy sprawl and over-classification.
   - MacroForge implication: a shared capability should be narrowly named and not become a general governance/metadata taxonomy.

Consultation conclusion:

The advisory evidence strengthens a lineage-first extraction if, and only if, the extraction is minimal: a deterministic lineage event emission contract used by existing loaders. The consultation argues against broad provider metadata extraction, catalog-like schemas, lineage graph APIs, generalized validation registries, and runtime/platform adoption.

## Candidate comparison

| Candidate | Contract converged? | Algorithm converged? | Implementation converged? | Future deterministic engineering eliminated | Future human effort reduced | Future LLM reasoning reduced | Coupling introduced | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Narrow lineage event emission | Yes, for current two-step post-boundary load evidence: `raw_to_staging` and `staging_to_curated` events in `meta.lineage_event`, bound to `pipeline_run_id` and `source_id`, with `from_artifact`, `to_artifact`, optional checksum, row count, and details. | Yes. All three loaders insert the same event types idempotently after canonical load, differing only in source-provided event specs. | Strong. WDI, OECD, and Eurostat all duplicate the same SQL shape; combined smoke verifies 2 events per source. | Repeated SQL CTE/value construction for lineage events in every future loader. | Less manual audit wiring and fewer source-specific mistakes in lineage row names/counts/checksum placement. | Less repeated reasoning about how to preserve provenance after observed-boundary load. | Low if the helper accepts explicit event specs and has no source conditionals. | Recommend first. |
| Quality-check handling | Partial. `meta.quality_check` row shape converges, but check names, scopes, expected values, and semantics differ materially. | Partial. Row-count checks repeat, but source-specific checks differ: WDI has 2 checks, OECD has units/attribute-set checks, Eurostat has quarterly-period/provider-mapping checks. | Partial. Insert SQL shape is similar, but check logic is embedded as source-specific SQL expressions. | Some repeated insert boilerplate, but not semantic check engineering. | Limited unless a check-spec contract is designed. | Limited; humans/LLMs still need to decide which checks are valid per source. | Medium: a generic check helper could hide source-specific validation semantics inside a false abstraction. | Reject for first extraction. |
| Provider metadata handling | No. WDI raw artifacts, OECD SDMX metadata/codelists, and Eurostat JSON-stat dimensions/provider code dictionaries have different shapes and maturity. | No. Metadata algorithms are source/provider-specific by design. | No. Eurostat has provider code list/code persistence; OECD has codelist/label artifacts; WDI has bounded raw artifact/source metadata. | Low now; most work remains source-specific interpretation. | Low-to-medium later after more sources expose repeated metadata classes. | Low now; extraction would require more semantic reasoning, not less. | High: likely to leak provider-specific conditionals into shared infrastructure. | Reject. |
| Canonical dimension mechanics | Partial. Target tables converge (`dim_indicator`, `dim_territory`, `dim_period`, `dim_unit`, `dim_attribute_set`, provider mappings), but source semantics differ. | Partial. Indicator/unit/attribute upserts are similar; annual vs quarterly period construction, ISO3 vs provider territory mapping, and provider-code dictionaries differ. | Partial. There is repeated SQL, but with meaningful differences. | Potentially high later, but extraction now would touch core canonical semantics. | Potentially high later, but with current uncertainty. | Potentially high later, but requires design choices not yet proven. | High: easy to introduce source-specific conditionals or premature canonical-domain abstractions. | Reject for first extraction. |
| Canonical load/upsert mechanics | Partial. `fact_observation` grain and upsert shape are converged across sources. | Partial. Fact insert algorithm depends on prior source-specific dimension/mapping joins and as-of-date semantics. | Partial. SQL pattern is visibly repeated, but still tightly coupled to source temp table column names and dimension join mechanics. | High later if safely extracted. | Medium-to-high later. | Medium later. | High: fact loading is core correctness machinery; premature extraction could obscure canonical grain semantics. | Reject for first extraction. |
| Validation helpers | Partial. Isolated PostgreSQL tests, combined smoke, and deterministic change verification exist, but they serve different scopes. | Partial. Verification has converged for package equivalence, but validation report checks remain a mixed set. | Partial. Deterministic change verification is already Verified and should not be expanded now per user instruction. | Medium, but this would expand the just-completed capability. | Medium. | Medium. | Medium: risks violating the explicit instruction not to expand Deterministic Change Verification now. | Reject for this task. |

## Recommended first foundational capability

Recommended capability:

```text
Deterministic Lineage Event Emission
```

Recommended capability boundary:

A narrow shared post-observed-boundary helper that emits deterministic lineage event SQL/records from explicit event specifications produced by source-specific loaders.

What it should own:

- The shared `meta.lineage_event` insertion shape.
- Idempotent insertion keyed by current loader behavior: `pipeline_run_id` + `event_type`.
- Required event fields:
  - `event_type`
  - `from_artifact`
  - `to_artifact`
  - `row_count_sql` or already computed row count expression
  - optional `checksum_sha256`
  - deterministic `details`
- A tiny typed Python spec, if implementation proceeds.
- Tests proving SQL output and end-to-end loader behavior are unchanged.

What it must not own:

- Source acquisition.
- Source normalization.
- Staging table design.
- Canonical dimension or fact semantics.
- Provider metadata interpretation.
- Quality-check semantics.
- Lineage graph APIs, catalog integration, authorization, search indexes, or runtime orchestration.
- Source-specific conditionals such as `if source == WDI`.

## Why this is the highest-leverage first extraction

1. Evidence threshold is strongest.

All three current loaders generate the same two lineage stages:

- `raw_to_staging`
- `staging_to_curated`

The combined-source smoke test expects exactly two lineage events for each supported source:

```python
{"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
```

2. It is foundational but not semantically overreaching.

Lineage is part of MacroForge's trust doctrine. Extracting event emission improves provenance reliability without deciding economic semantics, canonical mappings, dimensions, units, frequencies, or quality policy.

3. It reduces future source-onboarding friction.

Every future source that loads post-boundary evidence will need lineage. A small shared helper eliminates repeated low-level SQL construction while preserving source-specific event specification.

4. It improves auditability before broader extraction.

A reliable lineage emission contract becomes evidence infrastructure for future extraction of checks, diagnostics, and canonical loading. This compounds without turning MacroForge into a general ETL or metadata platform.

5. ArchitectureHarvest consultation supports the narrow shape.

The MetaHarvest/OpenMetadata record supports lineage as edge/event details, but explicitly warns against graph/index complexity and platform adoption. That aligns with a tiny local helper, not a catalog.

## Rationale for rejecting other candidates

### Quality-check handling

Reject now because only the storage row shape has converged. The semantic contract has not.

- WDI currently checks staging rows and fact rows.
- OECD checks staging rows, fact rows, expected units, and attribute sets.
- Eurostat checks staging rows, fact rows, quarterly periods, and provider mappings.

A first extraction here would likely become either a thin insert helper with low leverage or a false validation framework that hides source-specific semantics. Better path: revisit after lineage emission and after more deterministic diagnostics clarify which check classes truly repeat.

### Provider metadata handling

Reject now because provider metadata remains intentionally source-specific.

- WDI metadata is raw artifact/source metadata around WDI API evidence.
- OECD metadata is SDMX endpoint/raw metadata plus codelist/label artifacts.
- Eurostat metadata includes JSON-stat dimensions and provider code list/code persistence.

A shared provider metadata capability would either be too abstract to help or would require source-specific branches, violating the shared infrastructure invariant.

### Canonical dimension mechanics

Reject now despite visible repetition because the repeated code carries real canonical-domain semantics.

- Annual and quarterly periods differ.
- Provider period strings belong in mapping metadata, not canonical period identity.
- ISO3 preservation and provider territory mappings differ by source.
- Eurostat provider code dictionaries add semantics that WDI/OECD do not share in the same form.

This may become high-leverage later, but it is not safe as the first extraction because errors here corrupt canonical identity rather than merely audit metadata.

### Canonical load/upsert mechanics

Reject now because the fact upsert is close to the core correctness boundary.

The `curated.fact_observation` grain is common, but each loader reaches that grain through source-specific temp tables, dimension joins, provider mappings, and as-of-date assumptions. Extracting too early would either create a generic loader framework in disguise or obscure the canonical grain's correctness assumptions.

### Validation helpers

Reject now because Deterministic Change Verification has just reached Verified and the user explicitly instructed not to expand it further at this time.

Existing validation helpers are important, but this task should select a separate first shared foundational extraction candidate. Future validation extraction should wait until lineage emission and diagnostics clarify repeated check contracts.

## Expected capability maturity transition

This selection advances:

```text
Shared Post-Boundary Infrastructure Extraction: Discovered -> Specified
```

It also creates a proposed sub-capability maturity state:

```text
Deterministic Lineage Event Emission: Discovered -> Specified
```

Not claimed:

- Verified: no implementation or equivalence test has been added in this task.
- Adopted: existing loaders still contain source-specific inline lineage SQL.
- Shared: no reusable implementation exists yet.
- Stable/Mature: future proof and repeated use are still required.

The next implementation task, if accepted, should target:

```text
Deterministic Lineage Event Emission: Specified -> Verified
```

Only after tests prove behavior-preserving extraction across WDI/OECD/Eurostat should MacroForge consider claiming Shared or Adopted for this sub-capability.

## Narrow implementation plan for selected capability

Do not implement under this report. If approved later, implement as a small TDD extraction.

### Scope

Extract only deterministic lineage event emission boilerplate from WDI/OECD/Eurostat loaders.

### Non-goals

- No database migration.
- No generalized ingestion framework.
- No source registry or plugin system.
- No lineage graph, catalog, OpenMetadata, dbt, Dagster, or runtime integration.
- No provider metadata extraction.
- No quality-check extraction.
- No canonical dimension/fact loading extraction.
- No changes to current event counts, event types, checksums, row counts, details, or report outputs.

### Proposed implementation steps

1. Add failing unit tests for a tiny lineage spec renderer.
   - Target file: `tests/test_lineage_events.py`.
   - Expected behavior: rendering two event specs produces the same `INSERT INTO meta.lineage_event` shape currently embedded in loaders.
   - Include optional checksum support because WDI currently lacks checksum in the lineage insert while OECD/Eurostat include it.

2. Add the smallest helper module.
   - Target file: `src/macroforge/lineage_events.py`.
   - Suggested objects:
     - `LineageEventSpec`
     - `build_lineage_event_insert_sql(...)`
   - The helper should accept source/run CTE names or SQL snippets explicitly rather than discovering source behavior.
   - The helper must not import source-specific loader modules.
   - The helper must not branch on `source_code`.

3. Refactor WDI lineage SQL only.
   - Replace only the `meta.lineage_event` insert block in `src/macroforge/wdi_loader.py`.
   - Run `tests/test_wdi_loader.py` and the new lineage helper tests.
   - Confirm WDI lineage event count and deterministic verification behavior remain unchanged.

4. Refactor OECD lineage SQL.
   - Replace only the `meta.lineage_event` insert block in `src/macroforge/oecd_sdmx_loader.py`.
   - Preserve checksum behavior.
   - Run `tests/test_oecd_sdmx_loader.py` and helper tests.

5. Refactor Eurostat lineage SQL.
   - Replace only the `meta.lineage_event` insert block in `src/macroforge/eurostat_namq_loader.py`.
   - Preserve checksum behavior.
   - Run `tests/test_eurostat_namq_loader.py` and helper tests.

6. Run cross-source verification.
   - Run:
     ```bash
     uvx --from pytest --with pyyaml pytest tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py tests/test_deterministic_change_verification.py -q
     ```
   - Expected invariant: lineage events remain `{"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}` and deterministic package equivalence remains true for all sources.

7. Update docs/state only after tests pass.
   - Add a short architecture note if the helper becomes accepted.
   - Update capability maturity only to Verified if deterministic equivalence passes.
   - Do not claim Shared/Stable until the helper is used by WDI/OECD/Eurostat and protected by tests.

### Acceptance criteria for future implementation

- Existing loader behavior is unchanged.
- Combined-source smoke still reports 2 lineage events per source.
- Deterministic change verification still passes for WDI, OECD, and Eurostat.
- No source-specific conditionals appear in the shared helper.
- No quality-check, provider metadata, canonical dimension, or fact-upsert logic is extracted.
- No runtime/catalog/orchestration platform is introduced.

## Final recommendation

Select `Deterministic Lineage Event Emission` as the first foundational post-boundary extraction candidate.

Reason: it has the clearest convergence evidence, the lowest semantic coupling, direct trust/audit value, support from ArchitectureHarvest consultation when scoped narrowly, and the best risk-adjusted path for reducing future deterministic engineering without premature framework extraction.
