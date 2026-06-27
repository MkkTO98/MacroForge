# MacroForge v1.1 Final Governance Refinement and Freeze

Date: 2026-06-27
Status: final planned governance refinement complete; capability maturity lifecycle refined by `docs/architecture/capability-maturity-model.md`
Scope: governance mechanism/documentation refinement only; replay capability not implemented
Implementation changes: consultation trigger mechanism and tests only; no runtime ingestion behavior changed

## Executive conclusion

MacroForge governance is complete for v1.1 and should now be considered frozen pending implementation-driven discoveries.

The final refinement is to adopt the broader trigger name:

```text
foundational_capability_extraction
```

rather than:

```text
foundational_shared_deterministic_infrastructure_extraction
```

This better matches Strategic Constitution v1.1 because the Constitution optimizes durable platform capability, not only current infrastructure terminology. The trigger activates when proposed implementation is expected to become a reusable dependency of multiple future capabilities.

The default development mode after this point is:

```text
Implement
  -> Verify
  -> Update capability maturity
  -> Select next capability/task from evidence
  -> Implement
```

Future architectural reports should only be created when implementation exposes uncertainty that cannot be resolved from the Constitution, capability graph, contracts, dependency graph, or deterministic verification evidence.

## 1. Final governance refinement

The final refinement aligns five governance mechanisms:

1. Strategic Constitution: now explicitly includes uncertainty reduction, capability-oriented planning, capability maturity, the final ArchitectureHarvest trigger, and governance-freeze workflow.
2. Consultation policy: now includes a trigger for foundational capability extraction.
3. Capability planning: now uses capabilities as durable planning units and tasks as execution units.
4. Dependency graph: now tracks capabilities and capability maturity rather than only sequential tasks.
5. Future implementation workflow: now defaults to implementation-driven learning rather than repeated strategic reports.

This is deliberately small. It does not introduce a governance subsystem, planning database, workflow engine, plugin system, or runtime architecture.

## 2. Consultation-trigger recommendation

### Chosen trigger

```text
foundational_capability_extraction
```

### Why this name is better than `foundational_shared_deterministic_infrastructure_extraction`

`foundational_shared_deterministic_infrastructure_extraction` was accurate for the immediate post-`ObservedIngestionPackage` roadmap, but it is too tied to current implementation vocabulary.

The Strategic Constitution's deeper object is durable platform capability. Infrastructure is one way a capability becomes real, but not the strategic unit. A capability may include:

- a shared contract;
- deterministic diagnostics;
- replay/equivalence proof;
- contract validation;
- provider knowledge accumulation;
- canonical loading mechanics;
- lineage/quality behavior;
- future source onboarding affordances.

The better trigger criterion is therefore:

> Will this implementation become a reusable dependency of multiple future capabilities?

If yes, it deserves deeper ArchitectureHarvest consultation because mistakes will compound across future work.

### Trigger scope

The trigger applies to implementation proposals such as:

- foundational capability extraction;
- shared deterministic infrastructure;
- shared validation infrastructure;
- shared replay infrastructure;
- deterministic replay infrastructure when intended as reusable infrastructure;
- shared diagnostics infrastructure;
- shared canonical loading infrastructure;
- canonical load/upsert helper extraction;
- shared lineage infrastructure;
- shared quality-check infrastructure;
- post-observed-boundary shared infrastructure;
- implementation extracted from multiple existing implementations;
- any implementation expected to become a reusable dependency across multiple future capabilities.

The trigger does not apply to:

- ordinary implementation under existing contracts;
- diagnostic-only replay work that does not create long-lived shared runtime infrastructure;
- closeout;
- state recovery;
- status inspection;
- report regeneration;
- fixture refresh;
- running existing tests.

### Mechanism updated

Updated:

- `architecture/architectureharvest/relevance_map.yaml`
- `tools/consult_metaharvest.py`
- `tests/test_consult_metaharvest.py`

The consultation classifier version is now 2.

## 3. Capability maturity recommendation

Note: the final capability model in `docs/architecture/capability-maturity-model.md` refines this lifecycle by adding `Adopted` between `Verified` and `Shared` to distinguish deterministic proof from becoming MacroForge's canonical implementation path.

MacroForge should explicitly track lightweight capability maturity.

Adopted lifecycle as refined by the capability model:

```text
Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature
```

Definitions:

- Discovered: repeated behavior or need has been observed.
- Specified: a narrow evidence-backed contract or target behavior is documented.
- Verified: deterministic checks prove current behavior and preserve equivalence.
- Adopted: the verified capability is the canonical implementation path MacroForge uses for the relevant scope.
- Shared: implementation has been extracted into reusable shared infrastructure without source-specific conditionals.
- Stable: the capability is used by multiple current paths and has regression protection.
- Mature: the capability can guide future source/dataset work with low uncertainty and minimal strategic intervention.

Why this is worth adding:

- It makes capability-oriented planning operational.
- It prevents tasks from masquerading as mature capabilities.
- It makes roadmap dependencies clearer.
- It keeps future agents from prematurely extracting shared implementation before verification exists.
- It adds almost no overhead if tracked only in state/backlog/handoff artifacts.

Smallest implementation:

- Track capability maturity in `state/active_goal.md`, `state/project_state.md`, `state/architecture.md`, `artifacts/tasks/backlog.md`, and `context/latest_handoff.md`.
- Do not create a new capability registry yet.
- Do not create a workflow engine or planning database.

## 4. Governance completeness assessment

MacroForge now possesses:

| Component | Status | Evidence |
| --- | --- | --- |
| Stable optimization objective | Complete | Strategic Constitution v1.1 |
| Stable architectural philosophy | Complete | evidence-derived extraction, source-specific/shared boundaries, no speculative frameworks |
| Stable consultation policy | Complete | bounded routine consultation plus `foundational_capability_extraction` trigger |
| Stable capability planning | Complete | capability hierarchy and maturity lifecycle |
| Stable dependency planning | Complete | capability-oriented dependency graph in state/backlog/report artifacts |
| Stable implementation prioritization | Complete | evaluate reduction in engineering/human/LLM effort, uncertainty reduction, confidence, knowledge, leverage, complexity, maintenance |

No essential governance component remains missing for MacroForge v1.1.

Conclusion:

```text
Governance is complete for v1.1.
```

## 5. Final implementation workflow

After this refinement, MacroForge should default to:

```text
Implement
  -> Verify
  -> Update capability maturity
  -> Select next capability/task from evidence
  -> Implement
```

Detailed workflow:

1. Start from bounded recovery and current state.
2. Identify the current capability and maturity state.
3. If the task is ordinary implementation under existing contracts, implement locally.
4. If the task proposes foundational capability extraction, run deep ArchitectureHarvest consultation first.
5. Verify with deterministic tests/checks/replay outputs.
6. Update affected capability maturity in state/backlog/handoff.
7. Select the next task from implementation evidence.
8. Produce architectural reports only for genuine unresolved uncertainty.

## 6. Frozen governance rules

Governance is now frozen for v1.1 pending implementation-driven discoveries.

This does not mean governance can never change. It means no further planned strategic governance passes are needed.

Future architectural reports should only be created when implementation exposes uncertainty that cannot be resolved from:

- `CONSTITUTION.md`;
- current capability graph;
- `ObservedIngestionPackage` and future contracts;
- dependency graph;
- existing architectural reports;
- deterministic verification evidence.

Routine implementation should not create new strategy reports merely to restate existing doctrine.

## 7. Updated capability graph with maturity

```text
Capability A: Observed Boundary and Contract Stability
  Maturity: Specified
  Evidence: ObservedIngestionPackage v1, contract documentation, WDI/OECD/Eurostat adapters/tests
  Next maturity target: Verified through replay/equivalence diagnostics

Capability B: Deterministic Change Verification
  Maturity: Discovered
  Evidence: governance assessments identify it as the next capability
  First task: deterministic ObservedIngestionPackage replay/equivalence diagnostics
  Next maturity target: Verified

Capability C: Contract Validation and Drift Detection
  Maturity: Discovered
  Evidence: package contract and tests exist; validators not yet extracted
  Next maturity target: Verified via narrow invariant checks

Capability D: Ingestion Diagnostics and Recovery Evidence
  Maturity: Discovered
  Evidence: combined smoke/reports exist; unified diagnostics not yet implemented
  Next maturity target: Specified/Verified after replay shape is known

Capability E: Shared Post-Boundary Infrastructure Extraction
  Maturity: Discovered
  Evidence: repeated WDI/OECD/Eurostat behavior exists; extraction deferred
  Gate: foundational_capability_extraction consultation plus replay/equivalence evidence

Capability F: Canonicalization Governance and Mapping Advancement
  Maturity: Stable for file-backed lifecycle; Discovered/Specified for OECD/Eurostat advancement
  Evidence: existing deterministic lifecycle/report artifacts
  Next maturity target: targeted diagnostics/review evidence when needed

Capability G: Knowledge-Accumulating Source Expansion
  Maturity: Discovered
  Evidence: constitutional objective; source expansion intentionally deferred
  Gate: replay/diagnostics/shared infrastructure maturity sufficient to reduce future marginal cost
```

## 8. Current dependency graph

```text
Strategic Constitution v1.1
  -> Governance freeze complete
      -> foundational_capability_extraction trigger active
      -> capability maturity lifecycle active
      -> implementation-driven workflow active

ObservedIngestionPackage v1 contract
  -> Deterministic Change Verification
      -> deterministic package replay/equivalence diagnostics
      -> narrow package contract validation checks
      -> fixture replay/diagnostic evidence

Deterministic Change Verification
  -> Contract Validation and Drift Detection
  -> Ingestion Diagnostics and Recovery Evidence
  -> Shared Post-Boundary Infrastructure Extraction readiness

Shared Post-Boundary Infrastructure Extraction readiness
  -> foundational_capability_extraction consultation
  -> shared validation/helper extraction
  -> shared lineage/quality helper extraction
  -> provider metadata helper extraction
  -> canonical loading/upsert helper extraction spike

Verified/stable post-boundary capabilities
  -> Canonicalization Governance and Mapping Advancement
  -> Knowledge-Accumulating Source Expansion
```

## 9. Next implementation work remains unchanged in substance

The capability name is refined by `docs/architecture/capability-maturity-model.md` to `Deterministic Change Verification`. Replay and equivalence remain the first mechanisms.

Next capability:

```text
Deterministic Change Verification
```

First task:

```text
Implement deterministic ObservedIngestionPackage replay/equivalence diagnostics.
```

This task should not become a strategy report. It should produce working deterministic diagnostics backed by tests.

Diagnostic-only replay does not require the new foundational trigger. If the task expands into reusable shared infrastructure extraction, the trigger applies and deep ArchitectureHarvest consultation is required first.

## 10. Files changed by this refinement

- `CONSTITUTION.md`
- `architecture/architectureharvest/relevance_map.yaml`
- `tools/consult_metaharvest.py`
- `tests/test_consult_metaharvest.py`
- `artifacts/reports/R-20260627-final-governance-refinement-and-freeze.md`
- state/backlog/handoff/summary files updated separately during closeout
