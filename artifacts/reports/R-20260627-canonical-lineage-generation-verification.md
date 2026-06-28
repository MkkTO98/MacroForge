# Canonical Lineage Event Generation Verification

Date: 2026-06-27
Status: implementation verification complete
Capability transition: Specified -> Verified

## Capability definition refinement

Accepted selected capability from TASK-047: `Deterministic Lineage Event Emission`.

Refined durable capability name: `Canonical Lineage Event Generation`.

Rationale:

- `Event Generation` describes the shared semantic algorithm: generate the canonical two lineage events currently required by supported source loaders.
- `Emission` overstates the implementation boundary because this task explicitly did not extract storage, persistence, or orchestration.
- `Canonical Lineage Generation` alone is too broad and could imply graph/catalog lineage, lineage storage, or full transformation lineage. The word `Event` keeps the capability narrow enough for current evidence.
- `Deterministic` remains an invariant of the implementation and verification, not the most durable capability name. MacroForge's Constitution already requires deterministic shared infrastructure.

The implemented capability is therefore:

```text
Canonical Lineage Event Generation
```

## Implementation summary

Implemented only the smallest repeated semantic algorithm shared by WDI, OECD, and Eurostat:

- Added `src/macroforge/lineage_generation.py`.
- Added immutable `CanonicalLineageEvent` specs.
- Added `canonical_lineage_events(...)` to generate exactly the current two-step lineage semantics:
  - `raw_to_staging`
  - `staging_to_curated`
- Added `lineage_values_sql(...)` only as a thin VALUES-clause adapter for existing loader-owned persistence SQL.
- Refactored only the lineage event VALUES construction in:
  - `src/macroforge/wdi_loader.py`
  - `src/macroforge/oecd_sdmx_loader.py`
  - `src/macroforge/eurostat_namq_loader.py`
- Added `tests/test_lineage_generation.py`.

The loaders still own:

- source-specific acquisition and normalization;
- staging and canonical load SQL;
- `INSERT INTO meta.lineage_event` persistence;
- source identity and run lookup;
- row-count SQL scoping;
- quality checks;
- provider metadata;
- canonical dimensions and fact upserts.

No storage, persistence, orchestration, graph/catalog system, source framework, quality-check abstraction, provider-metadata abstraction, canonical dimension abstraction, or fact-upsert abstraction was extracted.

## TDD evidence

RED command:

```text
uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py -q
```

RED result:

```text
ModuleNotFoundError: No module named 'macroforge.lineage_generation'
1 error
```

GREEN command:

```text
uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py -q
```

GREEN result:

```text
3 passed in 0.01s
```

## Verification results

Targeted loader and capability tests:

```text
uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py -q
.........                                                                [100%]
9 passed in 1.73s
```

Cross-source deterministic verification path:

```text
uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py tests/test_deterministic_change_verification.py -q
................                                                         [100%]
16 passed in 3.23s
```

Full test suite:

```text
uvx --from pytest --with pyyaml pytest tests -q
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 5.80s
```

Final closeout verification after documentation/state updates:

```text
git diff --check
<no output; exit 0>

python3 tools/check_coherence.py --project .
WARN: context health: state/project_state.md is approaching context-health limit (9265/12000 chars)
WARN: context health: state/architecture.md is approaching context-health limit (10677/12000 chars)
coherence: 0 block(s), 2 warning(s)

python3 tools/context_health.py --project .
WARN: state/project_state.md is approaching context-health limit (9265/12000 chars)
WARN: state/architecture.md is approaching context-health limit (10677/12000 chars)
context health: 0 block(s), 2 warning(s)
```

No deterministic report JSON files remain modified after restoring temporary isolated database identifier changes.

Additional guard:

```text
search_files SOURCE_CODE|WDI|OECD|EUROSTAT|source == in src/macroforge/lineage_generation.py
0 matches
```

## Deterministic change verification usage

The existing Deterministic Change Verification test was included in the cross-source verification set.

That test loads WDI, OECD, and Eurostat into an isolated PostgreSQL database and verifies loaded canonical observations match expected `ObservedIngestionPackage` fingerprints, row counts, expected row counts, observation counts, and differing-observation diagnostics.

This proves the lineage extraction did not alter supported-source canonical loaded behavior. Combined-source smoke additionally preserves the expected lineage counts by source:

```text
{"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
```

## Extraction evidence summary

### Contract convergence

Converged.

All current supported loaders require the same post-boundary lineage contract:

- event type;
- upstream artifact;
- downstream artifact;
- row-count evidence;
- optional checksum;
- deterministic details;
- source/run binding owned by persistence SQL.

The two current canonical events are common across all supported sources:

- `raw_to_staging`;
- `staging_to_curated`.

### Algorithm convergence

Converged for the extracted scope.

The shared algorithm is:

1. generate one `raw_to_staging` event from raw artifact to source-specific staging artifact;
2. attach the raw checksum when source evidence has one;
3. generate one `staging_to_curated` event from staging artifact to `curated.fact_observation`;
4. leave curated checksum empty;
5. attach loader-supplied deterministic row-count SQL and details.

No source-specific branching is required.

### Implementation convergence

Converged for the extracted scope.

Before extraction, WDI/OECD/Eurostat each duplicated equivalent lineage VALUES construction inside loader SQL. Differences were explicit event inputs, not different algorithms.

The implementation now centralizes the repeated event generation while leaving persistence SQL in the loaders.

### ArchitectureHarvest consultation

TASK-047 already performed the required deep `foundational_capability_extraction` ArchitectureHarvest/MetaHarvest consultation.

The consultation supported compact lineage edge/event details but warned against:

- graph/index complexity;
- catalog/platform adoption;
- broad governance taxonomy;
- runtime/orchestration systems;
- metadata-platform sprawl.

This implementation follows that advice by extracting only a tiny local lineage event generation helper.

### Deterministic verification availability

Available and used.

- New unit tests prove generated event semantics and SQL VALUES shape.
- Existing loader tests prove WDI/OECD/Eurostat idempotent behavior still works.
- Existing combined-source smoke proves lineage event counts remain unchanged across supported sources.
- Existing deterministic change verification proves loaded canonical observations still match expected observed packages.
- Full test suite remains green.

### Remaining coupling risks

Remaining risks are intentionally bounded:

- `lineage_values_sql(...)` still renders SQL VALUES tuples because current loaders are raw-SQL loaders. It does not own `INSERT`, table names, source/run CTEs, or persistence policy.
- Row-count SQL remains loader-supplied because row-count scoping depends on loader-owned staging aliases and run CTEs.
- Event detail payloads remain loader-supplied because task/provenance details may evolve.
- The helper must not grow into a lineage graph, metadata catalog, runtime registry, or validation framework without a new evidence threshold and consultation.

## Capability maturity update

Completed transition:

```text
Canonical Lineage Event Generation: Specified -> Verified
```

Not claimed:

- Adopted: future source work has not yet been required to use this path.
- Shared/Stable/Mature: the capability is implemented and used by current loaders, but future adoption policy and longer regression history are still needed before higher maturity claims.

## Future extraction evaluation template

Future foundational extractions should not proceed until this evidence record can be filled.

Pre-implementation evidence gate:

1. Contract convergence: current implementations expose the same durable inputs, outputs, invariants, and ownership boundary.
2. Algorithm convergence: current implementations use the same semantic algorithm; differences are explicit inputs, not hidden source-specific branches.
3. Implementation convergence: repeated implementation exists in current source paths and can be extracted without source-specific conditionals.
4. Deterministic verification availability: tests, replay, fingerprints, isolated database checks, or equivalent deterministic evidence can prove behavior before and after extraction.
5. ArchitectureHarvest consultation completed: `foundational_capability_extraction` consultation has investigated architectural patterns, common failure modes, over-abstraction risks, minimal extraction, and reasons not to extract.
6. Semantic coupling acceptable: the extraction does not improperly take ownership of source-specific acquisition, provider semantics, persistence policy, runtime orchestration, graph/catalog behavior, or broader frameworks outside the evidence.
7. Capability prerequisites satisfied: every prerequisite listed in `docs/architecture/capability-maturity-model.md` is already Verified, unless the task is explicitly limited to documenting/specifying rather than advancing the dependent capability.

Implementation and closeout evidence:

1. Capability name refined to durable semantic capability, not current mechanism.
2. Explicit extraction boundary and non-goals.
3. RED test or equivalent failing deterministic check proving the missing shared capability.
4. GREEN targeted tests proving the extracted capability.
5. Cross-source equivalence/regression tests proving supported behavior unchanged.
6. Full-suite or proportionate final verification.
7. Remaining coupling risks and reasons not to advance beyond the target maturity.

This template is now recorded as the standard engineering template in `docs/architecture/capability-maturity-model.md`.

## Rationale for completed transition

The transition to Verified is justified because the capability now has:

- an implemented narrow shared contract;
- tests that prove the canonical two-event semantics;
- loader integration across WDI, OECD, and Eurostat;
- no source-specific conditionals in the shared helper;
- deterministic cross-source verification of unchanged supported behavior;
- no expansion into storage, persistence, orchestration, or broader platform abstractions.

This establishes the first repeatable pattern for future foundational capability extraction without advancing beyond Verified.
