# MacroForge v1.1 Roadmap Reassessment After ObservedIngestionPackage v1

Date: 2026-06-26
Status: completed governance reassessment; no runtime changes
Scope: current implementation after TASK-046 observed ingestion representation extraction
Primary evidence: implemented code, tests, fixtures, reports, and ProjectForge state

## Executive conclusion

TASK-046 changed the v1.1 roadmap. The previous post-freeze assessment correctly identified ingestion infrastructure as the next leverage point, but its first major extraction has now happened. The optimal next work is no longer to introduce a shared representation. That exists.

The next highest-leverage implementation task is to build deterministic fixture replay/equivalence diagnostics around `ObservedIngestionPackage` v1. This should prove and monitor that each supported source still produces the same package, SQL inputs, canonical counts, lineage counts, provider mappings, quality checks, and report outputs from fixture evidence.

This is higher leverage than extracting lineage helpers, validation helpers, canonical upsert helpers, or provider metadata infrastructure immediately because those later extractions need a stable regression harness first. Without deterministic replay diagnostics, each helper extraction would require repeated manual/LLM reasoning to prove equivalence.

## TASK-046 closeout status

TASK-046 is closed as an implementation task:

- `src/macroforge/observed_ingestion.py` exists and defines the extracted package/observation contract plus current WDI/OECD/Eurostat builders.
- WDI/OECD/Eurostat loaders consume the extracted representation where behavior is shared and preserve source-specific SQL/staging/canonicalization behavior.
- `tests/test_observed_ingestion.py` verifies package semantics for all supported sources and guards against generalized framework introduction.
- Loader, combined-source, and full-suite pytest verification passed during TASK-046 implementation.
- The contract is documented in `docs/architecture/observed-ingestion-representation.md`.

No production database schema, dataset scope, canonicalization semantics, validation semantics, lineage semantics, provider mapping semantics, conversion/aggregation policy, or AI/model behavior changed.

## Current implementation evidence reviewed

Implementation evidence used for this reassessment:

- `src/macroforge/observed_ingestion.py`
- `src/macroforge/wdi_loader.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `src/macroforge/eurostat_namq_loader.py`
- `src/macroforge/combined_source_smoke.py`
- `src/macroforge/canonical_gdp_snapshot.py`
- `src/macroforge/canonicalization_state.py`
- WDI/OECD/Eurostat normalized fixtures under `data/metadata/`
- WDI/OECD/Eurostat loader tests
- combined-source smoke tests
- canonical GDP snapshot tests
- canonicalization tests and governance reports
- `docs/architecture/observed-ingestion-representation.md`
- `artifacts/reports/R-20260626-observed-common-ingestion-representation-discovery.md`
- project state and summary files

## Contract stability assessment

Conclusion: Yes, with minor governance refinements.

Evidence:

- The representation stayed narrow. It consists of immutable package and observation dataclasses plus deterministic builders for current normalized artifacts.
- It did not introduce source plugin registration, base-loader inheritance, generalized staging, SQLAlchemy/Alembic, orchestration, live fetch behavior, conversion, aggregation, or model calls.
- The loaders still own source-specific SQL and staging/canonical details.
- The tests verify current source-specific semantics rather than hypothetical future sources.
- Source-specific dictionaries remain source-specific: `raw_evidence`, `input_filters`, `attributes`, and `source_payload` are intentionally not normalized into a broad metadata framework.
- Existing full-suite verification passed after extraction.

Minor governance refinements now completed:

- The contract has explicit field documentation.
- Compatibility expectations are recorded.
- Contract evolution is distinguished from ordinary implementation refactoring.
- Explicit out-of-contract areas are documented.

## Roadmap change from the prior assessment

The previous roadmap sequence was broadly:

1. Extract the common observation representation.
2. Extract shared loader/reporting mechanics.
3. Improve replay/fixture/source metadata infrastructure.
4. Later consider provider metadata, lineage, validation, or canonical helper extraction.

After TASK-046, the order should change:

1. Stabilize representation use through deterministic replay/equivalence diagnostics.
2. Extract tiny shared diagnostics/reporting around package/load outputs.
3. Then consider lineage/quality helper extraction.
4. Then consider provider metadata/fixture manifest improvements.
5. Delay canonical upsert helper extraction until replay diagnostics make equivalence cheap to prove.

The key shift is that the shared package now exists, so the bottleneck is proving future changes preserve behavior, not identifying the representation.

## Newly enabled architectural opportunities

### 1. Deterministic package replay and equivalence diagnostics

`ObservedIngestionPackage` v1 creates a stable comparison surface before SQL generation and canonical loading. MacroForge can now deterministically compare source package outputs from fixtures before deeper database checks.

Natural outputs:

- package snapshot per source;
- row-count/fingerprint summary;
- observation fingerprint summary;
- raw evidence/filter fingerprint summary;
- downstream canonical count/lineage/quality comparison.

This directly reduces future LLM reasoning and human review because helper extractions can be checked against deterministic equivalence reports.

### 2. Shared package validation helpers

The contract enables small validators for required package fields, observation fields, deterministic hashes, row-count agreement, empty/missing conventions, and source-specific dictionary presence.

This should be small and source-preserving, not a runtime framework.

### 3. Ingestion diagnostics report

A compact report can summarize each source's package, staging counts, fact counts, lineage count, quality count, provider mapping count, duplicate grains, and smoke output. This gives future agents a single bounded artifact for ingestion health.

### 4. Fixture replay manifest improvement

The package's raw evidence and input filters make fixture replay metadata more coherent. A small file-backed manifest could record normalized fixture path, source builder, expected package fingerprint, expected canonical counts, and replay command.

This should wait until the deterministic diagnostics exist.

### 5. Later helper extraction for lineage/quality patterns

WDI/OECD/Eurostat still repeat lineage and quality-check SQL patterns. Now that package-level identity and counts are shared, helper extraction is more feasible. It should still wait until replay diagnostics make equivalence cheap.

### 6. Later canonical upsert helper extraction

Canonical dimension/fact upserts remain repetitive but semantically delicate. They touch provider mapping and canonical-domain behavior. This should not be the immediate next task; it carries higher architectural risk.

## Non-opportunities still rejected

The current implementation still does not justify:

- adding a fourth dataset;
- deepening datasets;
- generalized ingestion frameworks;
- source plugin systems;
- source auto-discovery;
- generalized staging tables;
- runtime orchestration;
- schema redesign;
- model/AI canonicalization calls;
- conversion/aggregation policy;
- canonical report eligibility expansion.

## Revised MacroForge v1.1 roadmap

### Task 1 — Deterministic ObservedIngestionPackage replay and equivalence diagnostics

Objective: Add a deterministic fixture-backed replay/diagnostics command or helper that builds package outputs for WDI/OECD/Eurostat and compares package fingerprints plus downstream canonical/load health against expected values.

Motivation: TASK-046 made the shared contract explicit. Future infrastructure extraction now needs cheap equivalence proof before touching lineage, validation, reporting, or canonical SQL mechanics.

Dependencies: TASK-046; existing normalized fixtures; existing loader tests; combined-source smoke.

Expected reusable value: High. Establishes a reusable regression/equivalence harness for all later ingestion infrastructure work.

Implementation complexity: Medium-low. Mostly deterministic Python over existing fixtures plus optional isolated PostgreSQL smoke reuse.

Expected reduction in future deterministic engineering: High. Future helper extractions can reuse one comparison harness.

Expected reduction in future human effort: High. Less manual inspection of package rows, SQL outputs, and smoke reports.

Expected reduction in future LLM reasoning: High. Agents can cite deterministic diagnostics rather than infer equivalence from code.

Architectural risk: Low if kept as diagnostics only and no runtime behavior changes.

Depends directly on ObservedIngestionPackage: Yes.

### Task 2 — Package contract validation helpers

Objective: Add tiny validation helpers/tests for `ObservedIngestionPackage` v1 invariants: required fields, deterministic row counts, observation ordering, attribute hash correctness, WDI `unknown`/`empty` conventions, annual/quarterly period field consistency, and source-specific dictionary preservation.

Motivation: The contract is now public internal architecture. Small validators prevent accidental broadening or silent contract drift.

Dependencies: Task 1 recommended but not strictly required; TASK-046 contract documentation.

Expected reusable value: Medium-high. Protects the shared contract before broader reuse.

Implementation complexity: Low.

Expected reduction in future deterministic engineering: Medium.

Expected reduction in future human effort: Medium.

Expected reduction in future LLM reasoning: Medium-high.

Architectural risk: Low if validators remain contract checks and do not become source authority.

Depends directly on ObservedIngestionPackage: Yes.

### Task 3 — Ingestion diagnostics report artifact

Objective: Produce a compact deterministic report summarizing package fingerprints, normalized fixture provenance, staging/fact counts, provider mapping counts, lineage counts, quality checks, duplicate grains, and report-artifact stability for WDI/OECD/Eurostat.

Motivation: Current evidence exists but is scattered across tests, report JSONs, and loader behavior. A single ingestion diagnostics artifact would improve future recovery and review.

Dependencies: Task 1; existing combined-source smoke.

Expected reusable value: High for future agent recovery and architecture review.

Implementation complexity: Medium.

Expected reduction in future deterministic engineering: Medium.

Expected reduction in future human effort: High.

Expected reduction in future LLM reasoning: High.

Architectural risk: Low-medium; must avoid becoming a new source registry or authority layer.

Depends directly on ObservedIngestionPackage: Yes.

### Task 4 — Fixture replay manifest

Objective: Add a small file-backed manifest for current supported fixture replay: normalized artifact path, raw evidence pointer/checksum, package builder name, expected package fingerprint, expected row counts, and replay command.

Motivation: Fixture replay is central to trusted deterministic work, but evidence pointers are still distributed across normalized artifacts and tests.

Dependencies: Task 1 and preferably Task 3.

Expected reusable value: Medium-high.

Implementation complexity: Medium.

Expected reduction in future deterministic engineering: Medium.

Expected reduction in future human effort: Medium-high.

Expected reduction in future LLM reasoning: Medium-high.

Architectural risk: Medium if it drifts toward runtime source registry. Keep it file-backed replay metadata only.

Depends directly on ObservedIngestionPackage: Yes.

### Task 5 — Shared lineage and quality-check helper extraction

Objective: Extract tiny helpers for repeated lineage-event and quality-check insertion/reporting patterns that now share package source/release/run/count inputs.

Motivation: WDI/OECD/Eurostat repeat lineage and quality-check SQL mechanics. After replay diagnostics, these mechanics can be factored with lower equivalence risk.

Dependencies: Tasks 1-3 strongly recommended.

Expected reusable value: Medium.

Implementation complexity: Medium.

Expected reduction in future deterministic engineering: Medium.

Expected reduction in future human effort: Medium.

Expected reduction in future LLM reasoning: Medium.

Architectural risk: Medium. Lineage and quality semantics must remain unchanged; helpers must not hide source-specific evidence.

Depends directly on ObservedIngestionPackage: Partially. It can use package identity/counts but must preserve loader semantics.

### Task 6 — Provider metadata evidence helper extraction

Objective: Extract small deterministic helpers for provider metadata/evidence dictionaries where repetition is now proven: source URL, raw path, checksum, filters, provider dataset, and source home URL.

Motivation: `raw_evidence` and `input_filters` are shared as dictionary concepts but source-specific in key shape. Small helper functions could reduce boilerplate while preserving source specifics.

Dependencies: Tasks 1-4 recommended.

Expected reusable value: Medium.

Implementation complexity: Medium-low.

Expected reduction in future deterministic engineering: Medium.

Expected reduction in future human effort: Medium.

Expected reduction in future LLM reasoning: Medium.

Architectural risk: Medium; risk is accidentally creating a generalized metadata framework before evidence supports it.

Depends directly on ObservedIngestionPackage: Yes.

### Task 7 — Canonical upsert helper extraction spike

Objective: After diagnostics and smaller helpers, evaluate whether repeated canonical upsert SQL patterns can be safely extracted without changing provider mappings, dimensions, attribute sets, facts, lineage, or quality checks.

Motivation: Canonical SQL repetition exists, but it is close to semantic behavior and carries the highest regression risk.

Dependencies: Tasks 1-5.

Expected reusable value: Potentially high, but unproven until lower-risk infrastructure exists.

Implementation complexity: High.

Expected reduction in future deterministic engineering: High if successful.

Expected reduction in future human effort: Medium-high.

Expected reduction in future LLM reasoning: Medium-high.

Architectural risk: High. It could accidentally redesign ingestion or canonical semantics. Treat as a spike or equivalence extraction, not a broad refactor.

Depends directly on ObservedIngestionPackage: Partially.

## Prioritized implementation backlog

1. Deterministic ObservedIngestionPackage replay and equivalence diagnostics.
2. Package contract validation helpers.
3. Ingestion diagnostics report artifact.
4. Fixture replay manifest.
5. Shared lineage and quality-check helper extraction.
6. Provider metadata evidence helper extraction.
7. Canonical upsert helper extraction spike.

## Single highest-leverage next implementation task

Recommended next task: Deterministic ObservedIngestionPackage replay and equivalence diagnostics.

Task statement:

Implement a deterministic, fixture-backed equivalence diagnostics workflow for the current WDI, OECD, and Eurostat sources. The workflow should build each `ObservedIngestionPackage` from existing normalized fixtures, compute stable fingerprints/summaries for package-level and observation-level fields, and verify that downstream canonical/load behavior remains unchanged by comparing existing isolated loader/combined-source outputs: staging rows, canonical fact rows, provider mappings, lineage events, quality checks, duplicate fact grains, smoke workflow outputs, and canonical GDP snapshot outputs.

Constraints:

- Do not change production loader behavior.
- Do not change database schema.
- Do not introduce runtime source registry/plugin/framework behavior.
- Do not add or deepen datasets.
- Do not introduce model calls, conversion, aggregation, or mapping advancement.
- Treat outputs as diagnostics/equivalence evidence, not canonical truth.

Why this is now justified:

`ObservedIngestionPackage` v1 gives MacroForge a stable comparison surface. Before extracting more infrastructure, MacroForge needs deterministic proof that future changes preserve package and canonical behavior. This task directly reduces future deterministic engineering, human review, and LLM reasoning by making equivalence cheap and repeatable.
