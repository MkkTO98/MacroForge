# MacroForge Strategic Constitution v1.1 Backlog Reassessment

Date: 2026-06-26
Status: governance reassessment complete
Scope: current implementation state after TASK-046 and adoption of Strategic Constitution v1.1
Implementation changes: none beyond governance/documentation/state
Model calls: none
MetaHarvest/ArchitectureHarvest consultation: bounded helper returned `do_not_consult`; no retrieval performed because no active extraction task is being implemented in this reassessment

## Executive conclusion

Strategic Constitution v1.1 strengthens the post-TASK-046 roadmap rather than reversing it.

The highest-leverage next implementation task remains deterministic `ObservedIngestionPackage` replay/equivalence diagnostics, but the reason is sharper now: MacroForge's strategic asset is reusable deterministic ingestion capability. The next task should therefore increase confidence and reduce future proof burden before extracting more shared implementation.

Under the Constitution, dataset expansion moves later. Helper extraction remains desirable, but only after deterministic equivalence diagnostics make behavior preservation cheap to prove. The roadmap should be evaluated as a dependency graph of capability accumulation, not a fixed list.

## Constitution adoption

`CONSTITUTION.md` has been updated to Strategic Constitution v1.1. The prior trust doctrine and safety/project-state rules were retained where they are still compatible with the new governing optimization objective.

Primary adopted objective:

> The marginal cost of acquiring, updating, validating, and maintaining trustworthy economic data continuously decreases over time without sacrificing determinism, auditability, provenance, or canonical consistency.

This changes task evaluation emphasis from "what next capability can MacroForge add?" to "what next implementation compounds deterministic ingestion capability most while preserving confidence?"

## Current implementation evidence

Current implementation state:

- WDI/OECD/Eurostat have source-specific acquisition/normalization/loading paths.
- `ObservedIngestionPackage` v1 exists in `src/macroforge/observed_ingestion.py`.
- WDI/OECD/Eurostat loaders consume the package while preserving source-specific SQL, staging, provider mappings, lineage, quality checks, and canonical fact behavior.
- Combined-source smoke validates current canonical counts, dimensions, provider mappings, duplicate grains, and quality checks.
- Canonical GDP snapshot exists as deterministic report output.
- Canonicalization state/proposal/review mechanics are deterministic and file-backed.
- Fixture persistence is guarded for bounded OECD/Eurostat fixtures.
- Governance state recognizes `ObservedIngestionPackage` as a public internal contract.

## Dependency graph

```text
Strategic Constitution v1.1
  -> ObservedIngestionPackage v1 contract governance
      -> deterministic package replay/equivalence diagnostics
          -> package contract validation helpers
          -> ingestion diagnostics report artifact
              -> fixture replay manifest
                  -> provider metadata evidence helper extraction
          -> lineage and quality-check helper extraction
              -> canonical load/upsert helper extraction spike
                  -> future shared canonical infrastructure extraction
                      -> future dataset expansion / source onboarding

Existing canonicalization file-backed state
  -> mapping/review lifecycle diagnostics
      -> future provider-mapping advancement tasks
          -> eventual report eligibility expansion only after deterministic evidence gates

ArchitectureHarvest consultation doctrine
  -> deep consultation before new shared infrastructure extraction
      -> applies before lineage/quality helper extraction, provider metadata helper extraction, canonical helper extraction, or future reusable canonical infrastructure
      -> does not block current governance-only reassessment
```

## Reassessment principles applied

The Constitution changes backlog scoring in five ways:

1. Confidence is mandatory, not secondary.
2. Dataset count is not strategic unless each dataset leaves reusable ingestion knowledge behind.
3. Shared infrastructure extraction is eligible only when contract, algorithm, and implementation have converged.
4. Generic shared code must not depend on `if source == ...` conditionals; source-specific behavior belongs in adapters.
5. LLM reasoning should decrease over time through deterministic diagnostics, replay, and validation.

## Proposed tasks and leverage analysis

### 1. Deterministic ObservedIngestionPackage replay/equivalence diagnostics

Objective: Build deterministic fixture-backed diagnostics that construct WDI/OECD/Eurostat packages from current normalized fixtures, compute stable package/observation fingerprints, and compare downstream canonical/load health.

Dependencies:

- Strategic Constitution v1.1.
- TASK-046 `ObservedIngestionPackage` v1.
- Existing fixtures, loader tests, combined-source smoke, and canonical GDP snapshot.

Reduces future deterministic engineering: High. Future shared-infrastructure changes can reuse one equivalence harness instead of bespoke comparison scripts.

Reduces future human effort: High. Humans can review compact deterministic diagnostics rather than manually inspecting loaders, SQL, and reports.

Reduces future LLM reasoning: High. Agents can cite package/load fingerprints and count comparisons rather than reasoning from code diffs.

Increases confidence: Very high. It directly tests whether future refactors preserve semantics.

Knowledge accumulated: High. Captures provider/package behavior, observed row shapes, release evidence, counts, and downstream effects as deterministic replay knowledge.

Architectural leverage: Very high. It is the gate that makes later shared implementation extraction safer.

Implementation complexity introduced: Medium-low. It should be diagnostic-only and fixture-backed.

Long-term maintenance burden: Low-medium. Expected fingerprints must be maintained when intentional behavior changes occur.

ArchitectureHarvest requirement: Bounded consultation is enough for the diagnostics task itself because it is not extracting new shared runtime infrastructure. Deep consultation becomes mandatory if the task expands into shared loader/helper extraction.

Constitution fit: Excellent.

Recommendation: Rank 1. This is the next task.

### 2. Package contract validation helpers

Objective: Add small deterministic validators for `ObservedIngestionPackage` invariants: required fields, row-count agreement, stable attribute hashing, source-specific dictionary preservation, period/frequency consistency, and WDI `unknown`/`empty` conventions.

Dependencies:

- TASK-046 contract.
- Prefer Task 1 first so validation failures can be interpreted in replay context.

Reduces future deterministic engineering: Medium.

Reduces future human effort: Medium.

Reduces future LLM reasoning: Medium-high.

Increases confidence: High for contract drift; lower for downstream canonical equivalence unless paired with Task 1.

Knowledge accumulated: Medium. Encodes package invariants as executable checks.

Architectural leverage: High as a guardrail.

Implementation complexity introduced: Low.

Long-term maintenance burden: Low.

ArchitectureHarvest requirement: No deep consultation if validators remain contract checks. Deep consultation required if validators become a generalized source/runtime framework.

Constitution fit: Strong.

Recommendation: Rank 2, but can be merged into Task 1 if the implementation remains small.

### 3. Ingestion diagnostics report artifact

Objective: Produce a compact deterministic report summarizing package fingerprints, normalized fixture provenance, staging/fact counts, provider mapping counts, lineage counts, quality checks, duplicate grains, and smoke/report stability.

Dependencies:

- Task 1.
- Existing combined-source smoke and report generation.

Reduces future deterministic engineering: Medium-high.

Reduces future human effort: High.

Reduces future LLM reasoning: High.

Increases confidence: High if it compares expected/current values rather than merely reporting them.

Knowledge accumulated: High. Converts scattered ingestion evidence into reusable project knowledge.

Architectural leverage: High for future recovery/review.

Implementation complexity introduced: Medium.

Long-term maintenance burden: Medium. Report expectations must be kept intentional and compact.

ArchitectureHarvest requirement: Bounded unless it starts extracting shared runtime infrastructure.

Constitution fit: Strong.

Recommendation: Rank 3. Could be included in Task 1 only if scope stays bounded; otherwise keep separate.

### 4. Fixture replay manifest

Objective: Add a small file-backed manifest for current fixture replay: normalized artifact paths, package builder, source evidence pointer/checksum, expected package fingerprint, expected row counts, and replay command.

Dependencies:

- Task 1.
- Prefer Task 3 so the manifest points to a mature diagnostics surface.

Reduces future deterministic engineering: Medium.

Reduces future human effort: Medium-high.

Reduces future LLM reasoning: Medium-high.

Increases confidence: Medium-high when paired with diagnostics.

Knowledge accumulated: High for replay and fixture provenance.

Architectural leverage: Medium-high.

Implementation complexity introduced: Medium.

Long-term maintenance burden: Medium. Risk of stale manifests if not checked in tests.

ArchitectureHarvest requirement: Deep consultation not required if manifest remains replay metadata. Required if it becomes a source registry.

Constitution fit: Strong with guardrails.

Recommendation: Rank 4.

### 5. Shared lineage and quality-check helper extraction

Objective: Extract small helpers for repeated lineage-event and quality-check insertion/reporting patterns after replay diagnostics prove behavior preservation.

Dependencies:

- Tasks 1-3 strongly recommended.
- Deep ArchitectureHarvest consultation before extraction because this is shared infrastructure.

Reduces future deterministic engineering: Medium.

Reduces future human effort: Medium.

Reduces future LLM reasoning: Medium.

Increases confidence: Medium if carefully checked; negative if extracted before diagnostics.

Knowledge accumulated: Medium-high. Encodes lineage/quality patterns as infrastructure.

Architectural leverage: Medium-high.

Implementation complexity introduced: Medium.

Long-term maintenance burden: Medium. Helper semantics must avoid source-specific conditionals.

ArchitectureHarvest requirement: Deep consultation required before implementation.

Constitution fit: Good after diagnostics, premature before diagnostics.

Recommendation: Rank 5.

### 6. Provider metadata evidence helper extraction

Objective: Extract small deterministic helpers for provider evidence dictionaries only where algorithmic convergence has emerged: source URL/path/checksum, dataset code, input filters, source home URL, and replay evidence.

Dependencies:

- Tasks 1-4.
- Deep ArchitectureHarvest consultation before extraction.

Reduces future deterministic engineering: Medium.

Reduces future human effort: Medium.

Reduces future LLM reasoning: Medium.

Increases confidence: Medium if it standardizes evidence preservation; low if it generalizes source-specific metadata prematurely.

Knowledge accumulated: High if tied to provider quirks and replay evidence.

Architectural leverage: Medium.

Implementation complexity introduced: Medium-low.

Long-term maintenance burden: Medium due to risk of becoming a generalized metadata framework.

ArchitectureHarvest requirement: Deep consultation required.

Constitution fit: Conditional. Good only as evidence helpers, not a metadata framework.

Recommendation: Rank 6.

### 7. Canonical load/upsert helper extraction spike

Objective: Evaluate whether repeated canonical dimension/fact upsert mechanics can be safely extracted without changing provider mappings, dimensions, facts, lineage, quality checks, or canonical semantics.

Dependencies:

- Tasks 1-5.
- Deep ArchitectureHarvest consultation required before implementation.

Reduces future deterministic engineering: Potentially high.

Reduces future human effort: Medium-high.

Reduces future LLM reasoning: Medium-high.

Increases confidence: Potentially high after diagnostics; high risk before diagnostics.

Knowledge accumulated: High if successful because canonical-loading knowledge becomes reusable.

Architectural leverage: Very high but dangerous.

Implementation complexity introduced: High.

Long-term maintenance burden: High unless the extracted contract is extremely narrow.

ArchitectureHarvest requirement: Deep consultation required.

Constitution fit: Later-stage fit. Not next.

Recommendation: Rank 7. Treat as spike/equivalence extraction, not broad refactor.

### 8. Provider mapping advancement tasks for OECD/Eurostat

Objective: Advance deferred OECD/Eurostat GDP mappings only when required evidence and review gates from TASK-039/TASK-040 are satisfied.

Dependencies:

- TASK-039/TASK-040.
- Potentially diagnostics/report eligibility work.
- Explicit review approval.

Reduces future deterministic engineering: Low-medium.

Reduces future human effort: Medium for downstream research users.

Reduces future LLM reasoning: Medium if advancement criteria are encoded deterministically.

Increases confidence: High only if review evidence is complete.

Knowledge accumulated: High about unit basis, comparability, and provider semantics.

Architectural leverage: Medium.

Implementation complexity introduced: Medium-high due to semantic risk.

Long-term maintenance burden: Medium.

ArchitectureHarvest requirement: Bounded unless it changes shared infrastructure or canonical doctrine.

Constitution fit: Conditional. Important, but not before ingestion diagnostics because the strategic bottleneck is now reusable ingestion capability.

Recommendation: Defer behind Tasks 1-4 unless a concrete downstream blocker emerges.

### 9. New dataset/source expansion

Objective: Add another economic data source or deepen existing datasets.

Dependencies:

- Shared diagnostics and replay infrastructure should exist first unless a concrete external blocker justifies earlier expansion.

Reduces future deterministic engineering: Low if done now; higher later after reusable infrastructure exists.

Reduces future human effort: Low-medium now; likely high later.

Reduces future LLM reasoning: Low now; likely high later if diagnostics/validators exist.

Increases confidence: Low if expansion happens before infrastructure; medium-high if each new dataset leaves reusable ingestion knowledge.

Knowledge accumulated: Potentially high, but only if captured systematically.

Architectural leverage: Low now.

Implementation complexity introduced: Medium-high.

Long-term maintenance burden: High if added before shared deterministic infrastructure is mature.

ArchitectureHarvest requirement: Bounded/deep depending on whether source onboarding introduces new shared extraction or architecture doctrine.

Constitution fit: Poor as immediate next task.

Recommendation: Move later.

## Updated prioritized backlog

1. Deterministic `ObservedIngestionPackage` replay/equivalence diagnostics.
2. Package contract validation helpers, preferably integrated carefully with diagnostics if small.
3. Ingestion diagnostics report artifact.
4. Fixture replay manifest.
5. Shared lineage and quality-check helper extraction after deep ArchitectureHarvest consultation.
6. Provider metadata evidence helper extraction after deep ArchitectureHarvest consultation.
7. Canonical load/upsert helper extraction spike after diagnostics and deep ArchitectureHarvest consultation.
8. Provider mapping advancement tasks for OECD/Eurostat only after evidence/review prerequisites or a downstream blocker.
9. New dataset/source expansion only after reusable diagnostics/replay infrastructure makes expansion leave durable ingestion knowledge.

## Tasks moved earlier

- Deterministic diagnostics remain first and become even more important under Strategic Constitution v1.1.
- Package validation helpers move close to diagnostics because contract drift would undermine shared infrastructure compounding.

## Tasks moved later

- Provider mapping advancement moves behind ingestion diagnostics unless a concrete downstream blocker appears.
- Dataset expansion moves later because it increases dataset count before reducing marginal ingestion cost.
- Canonical upsert helper extraction stays later because it is high leverage but high risk.

## Tasks merged or split

- Package validation helpers may be merged into diagnostics only if kept small and executable as contract checks.
- Ingestion diagnostics report and fixture replay manifest should remain separate unless the first diagnostics task remains small enough to include a compact report without creating a registry.
- Canonical helper extraction should be split into a spike/equivalence phase before implementation.

## Removed tasks

No prior proposed task is fully removed, but broad/generalized versions are rejected:

- generalized ingestion framework;
- source plugin registry;
- workflow orchestration platform;
- generic metadata framework;
- AI-driven ingestion engine.

## Recommended next implementation task

Recommended next task: deterministic `ObservedIngestionPackage` replay/equivalence diagnostics.

Task statement:

Implement a deterministic fixture-backed diagnostics workflow for the current WDI, OECD, and Eurostat sources. It should build each `ObservedIngestionPackage` from existing normalized fixtures, compute stable package and observation fingerprints, and compare downstream load/canonical health against expected behavior: staging rows, canonical fact rows, provider mappings, lineage events, quality checks, duplicate fact grains, smoke workflow outputs, eligibility artifacts, and canonical GDP snapshot outputs where practical.

Constraints:

- no production behavior change;
- no database schema change;
- no new datasets or dataset deepening;
- no live data fetch unless explicitly approved;
- no mapping advancement;
- no conversion or aggregation;
- no AI/model calls;
- no generalized ingestion framework, source plugin system, or source registry;
- no source-specific conditionals in shared diagnostics beyond adapter selection/configuration.

Why this best advances the Constitution:

- It reduces future deterministic engineering by creating one repeatable equivalence harness.
- It reduces future human effort by compressing multi-file/manual inspection into deterministic diagnostics.
- It reduces future LLM reasoning by making behavior preservation observable rather than inferred.
- It increases confidence before convenience, making later helper extraction safer.
- It accumulates ingestion knowledge about provider evidence, package shape, row fingerprints, lineage/quality behavior, and canonical effects.
- It preserves the source-specific/shared boundary while making post-boundary infrastructure more reusable.

## ArchitectureHarvest consultation policy after adoption

This reassessment did not implement a new shared extraction. The bounded consultation helper classified the task as a governance decision and returned `do_not_consult` with no retrieval.

For future tasks:

- deterministic replay/equivalence diagnostics: bounded consultation is enough if diagnostic-only;
- package validators: bounded consultation is enough if contract-only;
- lineage/quality helper extraction: deep ArchitectureHarvest consultation required;
- provider metadata helper extraction: deep ArchitectureHarvest consultation required;
- canonical load/upsert helper extraction: deep ArchitectureHarvest consultation required;
- any task drifting toward framework/plugin/orchestration behavior: deep consultation plus explicit decision required, with a strong default rejection.

## Final assessment

The current roadmap remains directionally right but must now be governed by the Strategic Constitution's compounding-capability objective. The next task should not optimize for immediate code reuse or new data. It should optimize for confidence-preserving reduction in future proof burden.

Therefore, deterministic `ObservedIngestionPackage` replay/equivalence diagnostics is the best next implementation task.
