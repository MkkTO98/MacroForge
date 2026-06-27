# Governance Alignment After Strategic Constitution v1.1

Date: 2026-06-27
Status: governance alignment assessment complete
Scope: governance/planning only; no next-capability implementation
Implementation changes: none to runtime behavior
Model calls: none

## Executive conclusion

MacroForge's substantive governance direction is aligned with Strategic Constitution v1.1, but one final governance refinement is justified before long-lived shared deterministic infrastructure extraction begins:

> Add an explicit ArchitectureHarvest trigger category for extraction of foundational shared deterministic infrastructure.

This refinement should be applied to the consultation trigger system before implementing shared validation, lineage, canonical loading, provider metadata, or other long-lived shared deterministic infrastructure. It is not required before a narrow diagnostic-only replay task, but it is required before replay diagnostics evolve into reusable infrastructure or before any subsequent shared helper extraction.

Roadmap planning should now become capability-oriented:

```text
Strategic Objective
  -> Durable Platform Capabilities
      -> Implementation Tasks
```

Sequential task lists remain useful only as execution queues under capabilities. They should no longer be treated as the primary roadmap structure.

Governance maturity conclusion:

> Yes, with one final governance refinement.

After adding the foundational shared deterministic infrastructure consultation trigger, future architectural reports should only be produced when implementation uncovers uncertainty that cannot be resolved from the existing Constitution, architecture state, contract documentation, and current reports.

## Evidence used

Current implementation/governance evidence:

- Strategic Constitution v1.1 in `CONSTITUTION.md`.
- Post-constitution reassessment in `artifacts/reports/R-20260626-strategic-constitution-v11-backlog-reassessment.md`.
- `ObservedIngestionPackage` v1 contract in `docs/architecture/observed-ingestion-representation.md`.
- Current consultation helper: `tools/consult_metaharvest.py`.
- Current relevance map: `architecture/architectureharvest/relevance_map.yaml`.
- Current state/handoff: `state/active_goal.md`, `state/project_state.md`, `state/architecture.md`, `context/latest_handoff.md`.

## 1. Governance alignment assessment

### ArchitectureHarvest consultation policy

Constitutional requirement:

- Routine work should not be over-consulted.
- Consultation intensity should increase dramatically when MacroForge is about to extract long-lived shared deterministic infrastructure.
- Deep consultation should identify mature design patterns, common failure modes, blind spots, alternatives, and reasons not to extract.

Current policy direction is aligned in prose but not fully guaranteed by the trigger system.

### Roadmap generation

Current reports already shifted from fixed roadmap to evidence-derived dependency graph. This is aligned with the Constitution, but the roadmap should now be expressed as capabilities first and tasks second.

### Dependency graph generation

Current dependency graph is useful but still task-heavy. It should remain, but each task should attach to a durable capability so dependency reasoning tracks accumulated platform ability rather than recent implementation sequence.

### Task generation methodology

Task generation is mostly aligned:

- starts from implementation evidence;
- avoids speculative frameworks;
- favors equivalence and diagnostics before extraction;
- preserves source-specific/shared boundaries.

Missing piece: every task should explicitly state which capability it improves and which strategic objective criteria it optimizes.

### Capability planning

Capability planning is currently implicit. It should become explicit because Strategic Constitution v1.1 optimizes long-term marginal cost, confidence, and knowledge accumulation rather than completion of a fixed task list.

### Implementation prioritization

Current prioritization is aligned: replay/equivalence diagnostics before helper extraction and dataset expansion. It should be reframed as the first task inside the Replay and Equivalence Assurance capability.

## 2. Consultation-policy assessment

### Current trigger map

Current active triggers in `architecture/architectureharvest/relevance_map.yaml`:

```text
canonicalization_architecture_changes
source_contract_design_changes
lineage_or_validation_registry_changes
orchestration_or_runtime_adoption_decisions
generalized_ingestion_framework_decisions
```

These triggers cover some but not all Constitution-critical extraction points.

### Trigger behavior test results

Using the current helper against representative task summaries produced:

| Proposed work | Current behavior | Assessment |
| --- | --- | --- |
| deterministic replay infrastructure | `do_not_consult` | Gap if replay becomes foundational shared infrastructure; acceptable only for diagnostic-only task |
| shared validation infrastructure | `do_not_consult` | Gap |
| shared lineage infrastructure | `consult` via `lineage_or_validation_registry_changes` | Covered |
| shared canonical loading infrastructure | `do_not_consult` | Gap |
| shared provider metadata infrastructure | `consult` via `source_contract_design_changes` | Covered |
| future shared deterministic infrastructure extracted from multiple implementations | `do_not_consult` | Gap |

### Why gaps exist

The classifier currently recognizes terms around canonicalization, source contracts, lineage/validation registry, orchestration/runtime, generalized frameworks, governance, architecture, and cross-project boundaries.

But the Constitution's critical extraction category is broader and more precise:

> Long-lived shared deterministic infrastructure extracted from multiple existing implementations.

This can include replay, validation, canonical loading, diagnostics, provider metadata, lineage, quality checks, and future canonical helpers without necessarily using words already mapped to triggers. Work can be architecturally foundational while not being a framework, registry, runtime, source contract, or canonicalization architecture change.

### Should a new trigger category exist?

Conclusion: Yes.

Justification from Constitution:

- The Constitution explicitly says consultation intensity should increase when Hermes proposes extracting new shared infrastructure.
- It identifies shared deterministic infrastructure as the long-term direction after the observed ingestion boundary.
- It prohibits source-specific conditionals in shared infrastructure, which is an architectural quality constraint that benefits from external design-pattern/failure-mode consultation.

Justification from implementation history:

- WDI/OECD/Eurostat converged enough to extract `ObservedIngestionPackage` v1.
- TASK-046 made the observed boundary real, making future shared infrastructure extraction likely and high leverage.
- Current roadmap explicitly proposes shared validation, lineage, provider metadata, and canonical loading helper extraction.
- Current trigger behavior does not reliably catch replay, validation, canonical loading, or generic shared deterministic infrastructure extraction.

Smallest evidence-backed refinement:

Add one trigger category:

```text
foundational_shared_deterministic_infrastructure_extraction
```

Recommended matching terms:

```text
shared deterministic infrastructure
foundational shared infrastructure
shared validation infrastructure
shared replay infrastructure
deterministic replay infrastructure
shared diagnostics infrastructure
shared canonical loading infrastructure
canonical load helper extraction
canonical upsert helper extraction
shared lineage infrastructure
shared quality-check infrastructure
provider metadata infrastructure
extracted from multiple implementations
post-observed-boundary shared infrastructure
```

Recommended relevance-map addition:

```yaml
consult_required_during:
  - foundational_shared_deterministic_infrastructure_extraction
```

Recommended query mapping:

- primary problem: `transformation_lineage_asset_orchestration`
- keyword: `shared deterministic infrastructure`
- adjacent problems:
  - `metadata_catalog_lineage_governance`
  - `canonicalization_lifecycle_comparability_eligibility_check_gates`

Do not broaden consultation for ordinary feature work, closeout, status inspection, report regeneration, fixture refresh, or diagnostic-only replay that does not create long-lived shared runtime infrastructure.

## 3. ArchitectureHarvest trigger assessment

Current triggers do not guarantee the Constitution's desired behavior.

Covered today:

- source contract/provider metadata changes;
- lineage/validation registry changes;
- orchestration/runtime adoption;
- generalized ingestion framework decisions;
- canonicalization architecture changes.

Not reliably covered today:

- deterministic replay infrastructure;
- shared validation infrastructure unless described as a registry;
- shared canonical loading infrastructure;
- generic shared deterministic infrastructure extraction;
- future post-observed-boundary infrastructure that is not a framework or runtime.

Therefore the trigger system should be refined before the next shared infrastructure extraction milestone.

## 4. Capability-versus-task planning recommendation

Recommendation: move to capability-oriented planning.

Reason:

The Constitution optimizes long-term marginal cost reduction and accumulated ingestion knowledge. Those are capability properties, not task-list properties. Sequential tasks remain necessary for execution, but they should be derived from capabilities.

Recommended planning structure:

```text
Strategic Objective
  -> Capability
      -> Capability maturity state
      -> Evidence/uncertainty
      -> Next task(s)
      -> Verification gate
```

Measurable leverage:

- prevents task-list inertia;
- makes it clear why a task matters;
- avoids dataset expansion before platform capability improves;
- makes dependencies explicit at the capability level;
- reduces future strategic reassessment needs.

Do not create a heavy portfolio-management process. A compact capability graph in roadmap reports/backlog is sufficient.

## 5. Strategic Constitution refinement recommendations

### Uncertainty reduction

Recommendation: incorporate uncertainty reduction explicitly at the next Constitution refinement point.

Suggested addition to the task evaluation framework:

```text
- reduction in future uncertainty / increase in proportion of future work executable with high confidence;
```

Suggested addition to long-term philosophy:

```text
MacroForge should increase the proportion of future work that can be executed with high confidence from deterministic evidence rather than exploratory reasoning.
```

Justification:

- Deterministic replay, diagnostics, contract validation, and equivalence checks primarily reduce uncertainty before they reduce engineering effort.
- Reduced uncertainty is what makes later shared extraction safe.
- This is already implicit in `Confidence before convenience`, but making it explicit prevents mis-scoring diagnostics as merely low-level engineering work.

Do not modify the Constitution automatically in this pass unless the user approves or asks for direct adoption. The current Constitution is sufficient for the next task; this refinement would make scoring clearer, not change project direction.

## 6. Updated dependency graph

```text
Strategic Constitution v1.1
  -> Governance alignment refinement
      -> consultation trigger: foundational_shared_deterministic_infrastructure_extraction
      -> capability-oriented planning
      -> uncertainty-reduction scoring

ObservedIngestionPackage v1 contract
  -> Replay and Equivalence Assurance capability
      -> first task: deterministic package replay/equivalence diagnostics
      -> package contract validation checks
      -> fixture replay surface/manifest
      -> ingestion diagnostics report artifact

Replay and Equivalence Assurance capability
  -> Shared Infrastructure Extraction Readiness capability
      -> deep ArchitectureHarvest consultation gate
      -> shared validation helper extraction
      -> shared lineage/quality helper extraction
      -> provider metadata evidence helper extraction
      -> canonical loading/upsert helper extraction spike

Canonicalization Governance capability
  -> mapping/review lifecycle diagnostics
      -> OECD/Eurostat deferred mapping advancement when review evidence exists
      -> report eligibility advancement only through explicit gates

Source Expansion capability
  -> future new/deeper datasets
      -> only after replay/diagnostics and shared infrastructure make each dataset leave durable ingestion knowledge
```

## 7. Updated capability graph

```text
Strategic objective:
Decrease marginal cost of trustworthy economic-data ingestion without sacrificing determinism, auditability, provenance, or canonical consistency.

Capability A: Observed Boundary and Contract Stability
  Status: v1 exists
  Evidence: TASK-046, contract doc, WDI/OECD/Eurostat adapters/tests
  Next need: protect via replay/validation diagnostics

Capability B: Replay and Equivalence Assurance
  Status: not yet implemented
  Purpose: make behavior preservation observable and cheap to prove
  First task: deterministic ObservedIngestionPackage replay/equivalence diagnostics
  Depends on: Capability A

Capability C: Contract Validation and Drift Detection
  Status: not yet implemented beyond tests
  Purpose: catch package/field/invariant drift early
  Can merge with: Capability B first task if small

Capability D: Ingestion Diagnostics and Recovery Evidence
  Status: partial through combined smoke and reports
  Purpose: compact evidence for humans/agents; lower recovery and review cost
  Depends on: Capabilities B and C

Capability E: Shared Post-Boundary Infrastructure Extraction
  Status: deferred
  Purpose: reduce repeated implementation after observed boundary
  Depends on: Capabilities B-D and deep ArchitectureHarvest consultation

Capability F: Canonicalization Governance and Mapping Advancement
  Status: deterministic file-backed lifecycle exists; OECD/Eurostat advancement deferred
  Purpose: advance semantic confidence without premature acceptance
  Depends on: review evidence and diagnostics

Capability G: Knowledge-Accumulating Source Expansion
  Status: deferred
  Purpose: add data only when each source leaves reusable ingestion knowledge
  Depends on: Capabilities B-E
```

## 8. Revised implementation roadmap

### Capability B — Replay and Equivalence Assurance

Task B1: deterministic `ObservedIngestionPackage` replay/equivalence diagnostics.

- Objective: build deterministic fixture-backed diagnostics for WDI/OECD/Eurostat packages and downstream load/canonical health.
- Scope: package fingerprints, observation fingerprints, row counts, staging/fact counts, provider mappings, lineage counts, quality checks, duplicate grains, smoke/report comparisons where practical.
- Consultation: bounded if diagnostic-only; deep if it creates long-lived shared infrastructure abstractions.
- Architectural risk: low-medium.
- Leverage: very high.

### Capability C — Contract Validation and Drift Detection

Task C1: package contract validators.

- Can merge into B1 if small and limited to invariant checks.
- Should remain contract validation, not a runtime framework.

### Capability D — Ingestion Diagnostics and Recovery Evidence

Task D1: deterministic ingestion diagnostics report artifact.

- Depends on B1/C1.
- Produces compact report for recovery, review, and future task gating.

Task D2: fixture replay manifest.

- Depends on B1 and preferably D1.
- Must not become a source registry.

### Capability E — Shared Post-Boundary Infrastructure Extraction

Task E1: shared lineage/quality helper extraction.

- Depends on B-D.
- Requires deep ArchitectureHarvest consultation.

Task E2: provider metadata evidence helper extraction.

- Depends on B-D.
- Requires deep ArchitectureHarvest consultation.

Task E3: canonical loading/upsert helper extraction spike.

- Depends on B-D and prior helper evidence.
- Requires deep ArchitectureHarvest consultation.

### Capability F — Canonicalization Governance and Mapping Advancement

Task F1: mapping/review lifecycle diagnostics.

- Depends on B-D if it touches pipeline-level evidence.

Task F2: OECD/Eurostat mapping advancement.

- Depends on explicit review evidence and existing deferred requirements.

### Capability G — Knowledge-Accumulating Source Expansion

Task G1: future dataset/source expansion.

- Deferred until replay/diagnostics/shared infrastructure mature enough that onboarding reduces future marginal cost.

## 9. Current roadmap reassessment

### Do replay diagnostics remain highest leverage?

Yes.

They are the first implementation task inside the highest-leverage missing capability: Replay and Equivalence Assurance. That capability is prerequisite to safe shared infrastructure extraction and reduces uncertainty, human review burden, and LLM reasoning.

### Should contract validation merge with replay?

Yes, conditionally.

The first replay task should include minimal package contract validation if it remains narrow and testable:

- row-count agreement;
- required fields;
- stable fingerprint inputs;
- source-specific metadata preservation;
- no source-specific conditional logic in shared diagnostic core.

More ambitious validation should remain a separate task.

### Does fixture replay belong within the replay capability?

Yes.

Fixture replay is not merely documentation. It is part of the Replay and Equivalence Assurance capability. However, a durable manifest can remain a second task after initial diagnostics prove the shape.

### Have dependencies changed?

Slightly.

The main change is not task order but task grouping:

- replay diagnostics, contract validation, fixture replay, and diagnostics reporting are one capability family;
- shared helper extraction depends on that family plus a future consultation-trigger refinement;
- dataset expansion depends on capability maturity rather than being next after a fixed task count.

## 10. Governance maturity assessment

Conclusion:

> Yes, with one final governance refinement.

Evidence:

- Strategic Constitution v1.1 defines optimization objective, extraction doctrine, source/shared boundaries, negative objectives, and roadmap governance.
- `ObservedIngestionPackage` v1 makes the observed ingestion boundary concrete.
- The current roadmap already prioritizes replay/equivalence before shared extraction.
- State, handoff, and summaries point future agents to the correct evidence anchors.
- Remaining gap is mechanical: current consultation triggers do not reliably catch all foundational shared deterministic infrastructure extraction.

After adding that trigger refinement, governance should be stable enough that implementation becomes the primary driver of future learning.

Future architectural reports should only be produced when implementation uncovers uncertainty that cannot be resolved from the existing Constitution, architecture state, contract documentation, current reports, and deterministic verification outputs.

## 11. Single highest-leverage next implementation capability

Next capability:

```text
Replay and Equivalence Assurance
```

Why this capability, not a single task label:

- It directly reduces uncertainty.
- It makes future behavior preservation deterministic.
- It gates shared infrastructure extraction.
- It protects the `ObservedIngestionPackage` contract.
- It reduces future human and LLM proof burden.

## 12. First implementation task within that capability

First task:

```text
Implement deterministic ObservedIngestionPackage replay/equivalence diagnostics.
```

Task constraints:

- diagnostic/equivalence only;
- no production behavior change;
- no database schema change;
- no new datasets or dataset deepening;
- no live fetch unless explicitly approved;
- no mapping advancement;
- no conversion/aggregation;
- no AI/model calls;
- no generalized ingestion framework, plugin system, source registry, or orchestration runtime;
- no shared runtime helper extraction unless deep ArchitectureHarvest consultation is performed first.

Recommended minimum outputs:

- deterministic package fingerprint per current source fixture;
- deterministic observation fingerprint set/count per source;
- package contract invariant checks;
- comparison against downstream load/canonical health from existing smoke/report workflows where practical;
- test coverage proving diagnostics are stable and source-specific behavior remains in adapters.

## 13. No further strategic redesign needed before implementation

Do not run another broad roadmap redesign before B1 unless new implementation evidence invalidates the assumptions above. The next learning should come from building and verifying replay/equivalence diagnostics.
