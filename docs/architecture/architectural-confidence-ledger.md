# Architectural Confidence Ledger

Status: active lightweight architectural reasoning ledger
Created: 2026-06-29

## Purpose

This ledger records the important architectural assumptions currently guiding MacroForge.

It is intentionally lightweight. Confidence values are disciplined engineering estimates, not statistical claims.

Use this ledger to:

- make architectural assumptions explicit;
- identify which implementation evidence supports or weakens them;
- improve future source-implementation estimates;
- prevent convenience-driven architecture changes;
- keep extraction evidence-gated.

Update this ledger after materially informative implementations, especially heterogeneous source slices.

After every heterogeneous source implementation, perform a post-implementation calibration step for each tracked assumption:

- confidence before implementation;
- confidence after implementation;
- evidence supporting the update;
- whether confidence increased, decreased, or remained unchanged.

Also record one lightweight implementation-level field:

- Prediction Quality: Accurate, Mostly Accurate, Mixed, or Poor.

Support Prediction Quality with short evidence only. The goal is trend observation, not numerical scoring.

Over time, this ledger should answer one question:

```text
Is MacroForge becoming better at predicting future implementation behavior?
```

The objective is to improve MacroForge's future implementation estimates, not to create statistical precision.

## Prediction Quality scale

- Accurate: predictions were materially correct and useful for implementation decisions.
- Mostly Accurate: predictions were directionally correct with minor misses or under-specified details.
- Mixed: important predictions were both confirmed and refuted, or predictions were too uneven to guide future decisions confidently.
- Poor: predictions missed important behavior, effort centers, or architectural pressure.

Repeated Poor or Mixed prediction quality should increase architectural attention even when implementation succeeds, because it indicates missing understanding.

## Confidence scale

- 0-30%: weak assumption; likely wrong or under-evidenced.
- 31-60%: plausible but uncertain.
- 61-80%: supported by repeated evidence but still falsifiable.
- 81-95%: strongly supported; changes require substantial contrary evidence.
- 96-100%: reserved for invariants or explicit project policy, not empirical architecture bets.

## Current assumptions

### 1. ObservedIngestionPackage boundary is correctly placed

Current confidence: 88%.

Assumption:

```text
The boundary between source-specific acquisition/normalization and deterministic shared post-boundary mechanics is currently placed correctly at `ObservedIngestionPackage`.
```

Supporting evidence:

- WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, BLS_CPI, BEA_NIPA, and TREASURY_FISCAL_DATA can be represented through the observed package model.
- TASK-053 BEA table/line evidence required no contract evolution.
- TASK-054 Treasury row-oriented API evidence required no contract evolution.
- TASK-055 ECB SDW monthly exchange-rate evidence required no contract evolution while preserving SDMX structure/query evidence.
- Post-boundary fingerprinting, comparison, validation, lineage, and feedback operate across heterogeneous source shapes.

Future implementations that can increase confidence:

- ECB SDW if it passes through the boundary without loss of SDMX provenance.
- IMF SDMX if high-dimensional SDMX identity can remain pre-boundary.
- ALFRED/FRED if vintage semantics can be represented without muddying observation identity.

Future implementations that can decrease confidence:

- Any source requiring lossy encoding into provider indicator/territory/period fields.
- Any repeated need to add observed fields for source families rather than true shared semantics.
- Any post-boundary component requiring source-specific conditionals.

### 2. Deterministic Ingestion Substrate is sufficiently stable for continued heterogeneous source expansion

Current confidence: 83%.

Assumption:

```text
The current deterministic post-boundary substrate is stable enough that more architectural knowledge comes from bounded heterogeneous source implementations than from substrate-first refinement.
```

Supporting evidence:

- Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback are Verified for current scopes.
- TASK-053, TASK-054, and TASK-055 required no substrate redesign.
- Recent implementation effort has repeatedly concentrated before the boundary.

Future implementations that can increase confidence:

- ECB, IMF, ALFRED/FRED, or another materially different source passing through unchanged substrate mechanics.
- Three consecutive heterogeneous implementations without post-boundary redesign, triggering a bounded stability review.

Future implementations that can decrease confidence:

- Repeated substrate explanation failures.
- Need for source-specific substrate branches.
- Contract validation/fingerprint/lineage semantics failing for common macroeconomic source patterns.

### 3. Most future engineering effort belongs before the observed boundary

Current confidence: 84%.

Assumption:

```text
For near-term trustworthy economic sources, most new implementation effort will be acquisition, provider interpretation, source-specific normalization, and identity construction before `ObservedIngestionPackage`.
```

Supporting evidence:

- BLS_CPI, BEA_NIPA, and TREASURY_FISCAL_DATA all concentrated work before the observed boundary.
- TASK-054 confirmed query provenance, endpoint metadata, fiscal period handling, and categorical row identity as pre-boundary concerns.
- TASK-055 confirmed ECB SDMX dataflow, series key, structure metadata, exchange-rate unit construction, and provider identity remain pre-boundary concerns.
- Post-boundary changes have been Low to Very Low in recent source slices.

Future implementations that can increase confidence:

- ECB if SDMX interpretation remains source-specific before the boundary.
- IMF if high-dimensional provider interpretation dominates effort.
- Additional non-SDMX sources with new payload shapes but unchanged post-boundary mechanics.

Future implementations that can decrease confidence:

- Sources whose main difficulty is post-boundary comparison, validation, lineage, or canonical semantics.
- Repeated contract changes after the boundary.
- Provider families where shared pre-boundary layers become obviously necessary.

### 4. Provider interpretation should remain source-specific for now

Current confidence: 82%.

Assumption:

```text
Provider metadata interpretation should remain source-specific until repeated implementations show stable semantic convergence.
```

Supporting evidence:

- BEA table/line metadata and Treasury endpoint metadata were both useful but not shared enough to justify provider metadata infrastructure.
- OECD SDMX, Eurostat JSON-stat, BEA iTable, BLS API, and Treasury API all expose different provider semantics.
- ECB SDW shares SDMX GenericData mechanics with OECD, but EXR dataflow dimensions, unit construction, and structure metadata interpretation remained ECB-specific.
- Shared infrastructure with source-specific conditionals is explicitly rejected by the Strategic Constitution.

Future implementations that can increase confidence:

- ECB if SDMX syntax overlaps with OECD but semantic interpretation remains provider-specific.
- ALFRED/FRED if vintage/revision semantics differ from table/API/SDMX metadata patterns.

Future implementations that can decrease confidence:

- ECB and OECD showing nearly identical metadata interpretation algorithms.
- IMF confirming the same SDMX interpretation model across three providers.
- Repeated duplicated provider-metadata code with stable algorithms and no source-specific conditionals.

### 5. SDMX commonality is currently only protocol-level

Current confidence: 78%.

Assumption:

```text
SDMX is currently an acquisition/protocol family, not yet a MacroForge architectural boundary.
```

Supporting evidence:

- Current strong SDMX evidence is mainly OECD; one provider is insufficient for extraction.
- Similar XML/dataflow vocabulary does not prove convergent provider semantics.
- TASK-055 ECB SDW showed repeated SDMX XML mechanics but source-specific provider interpretation remained substantial.
- DEC-022 requires repeated implementation evidence before extraction.

Future implementations that can increase confidence:

- ECB showing that SDMX syntax is shared but dataflow/dimension/codelist interpretation remains ECB-specific.
- IMF showing SDMX provider semantics differ enough that shared interpretation would require conditionals.

Future implementations that can decrease confidence:

- ECB requiring substantially identical algorithms to OECD for structure parsing, codelist interpretation, key normalization, and observation construction.
- ECB and OECD naturally producing the same intermediate normalized SDMX representation before `ObservedIngestionPackage`.
- IMF later confirming the same pattern.

### 6. Future reusable capability extraction should remain evidence-driven

Current confidence: 95%.

Assumption:

```text
Reusable infrastructure should be extracted only after implementation evidence demonstrates contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable future effort reduction.
```

Supporting evidence:

- Strategic Constitution v1.1 explicitly governs extraction this way.
- Earlier tiny helper extractions were safer when they were mechanical and evidence-backed.
- Premature framework extraction remains a recurring project risk.
- TASK-053 and TASK-054 generated useful patterns without justifying extraction.

Future implementations that can increase confidence:

- Any source implementation where restraint avoids unnecessary complexity.
- Any later extraction candidate succeeding because repeated evidence made scope obvious.

Future implementations that can decrease confidence:

- Repeated duplicated code causing defects, drift, or high maintenance burden because extraction was delayed too long.
- Local agents repeatedly spending high LLM/human effort on identical source-family mechanics.

### 7. Source-specific first remains the correct posture for provider acquisition/parsing

Current confidence: 84%.

Assumption:

```text
New provider acquisition and parsing should start source-specific; shared mechanics should be extracted only after repeated non-semantic duplication appears.
```

Supporting evidence:

- WDI, OECD, Eurostat, BLS, BEA, and Treasury each had materially different acquisition and payload shapes.
- Source-specific slices preserved boundedness and auditability.
- Repeated post-boundary stability suggests the pre-boundary adapter posture is working.
- TASK-055 kept ECB SDW source-specific while still producing a valid observed package and explicit future extraction evidence.

Future implementations that can increase confidence:

- ECB if a source-specific adapter remains small and clear.
- ALFRED/FRED if revision semantics require careful provider-specific handling.

Future implementations that can decrease confidence:

- Multiple SDMX providers sharing enough acquisition/parsing logic to make independent adapters wasteful.
- Repeated provider-specific adapters differing only in endpoint constants.

### 8. Prediction-ledger implementation improves future estimation quality

Current confidence: 80%.

Assumption:

```text
Writing pre-implementation predictions and evaluating them after implementation will improve MacroForge's ability to estimate future source implementations.
```

Supporting evidence:

- TASK-053 and TASK-054 prediction reviews clarified that post-boundary effort remained lower than expected and pre-boundary work dominated.
- TASK-055 prediction review clarified that repeated SDMX XML mechanics are real but not yet architecture-boundary evidence.
- The prediction review format turns implementation into reusable judgment, not just completed code.

Future implementations that can increase confidence:

- TASK-055 if predictions about SDMX boundary pressure are clear enough to update future estimates.
- Later source slices where prediction errors directly improve candidate ranking.

Future implementations that can decrease confidence:

- Prediction ledgers becoming ritual documentation without changing future decisions.
- Predictions being too vague to classify as Confirmed, Partially confirmed, or Refuted.

## Post-implementation calibration template

Use this template after every heterogeneous source implementation.

```markdown
## Calibration — TASK-XXX source name

Date:
Related task:
Related prediction ledger:
Related implementation lessons:
Related surprise-log entry, if any:
Prediction Quality: Accurate / Mostly Accurate / Mixed / Poor
Prediction Quality evidence:

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | | | increased/decreased/unchanged | |
| Deterministic Ingestion Substrate is sufficiently stable | | | increased/decreased/unchanged | |
| Most future engineering effort belongs before the observed boundary | | | increased/decreased/unchanged | |
| Provider interpretation should remain source-specific for now | | | increased/decreased/unchanged | |
| SDMX commonality is currently only protocol-level | | | increased/decreased/unchanged | |
| Future reusable capability extraction should remain evidence-driven | | | increased/decreased/unchanged | |
| Source-specific first remains correct for acquisition/parsing | | | increased/decreased/unchanged | |
| Prediction-ledger implementation improves future estimation quality | | | increased/decreased/unchanged | |
```

## Current TASK-055 confidence target

TASK-055 should update at least these assumptions:

- SDMX commonality is currently only protocol-level.
- Provider interpretation should remain source-specific for now.
- ObservedIngestionPackage boundary is correctly placed.
- Most future engineering effort belongs before the observed boundary.
- Future reusable capability extraction should remain evidence-driven.
- Prediction-ledger implementation improves future estimation quality.

The implementation should explicitly evaluate whether ECB SDW strengthens, weakens, or falsifies each relevant assumption, and should record any material prediction mismatch in `docs/architecture/architectural-surprise-log.md`.


## Calibration — TASK-055 ECB SDW bounded exchange-rate evidence slice

Date: 2026-06-29
Related task: `artifacts/tasks/TASK-055-bounded-ecb-sdw-architectural-experiment.md`
Related prediction ledger: `artifacts/tasks/TASK-055-bounded-ecb-sdw-architectural-experiment.md`
Related implementation lessons: `artifacts/reports/L-20260629-task-055-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-055 surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-055 predictions correctly anticipated no observed-package evolution, no deterministic substrate evolution, source-specific ECB SDW interpretation before the observed boundary, and future SDMX extraction evidence without immediate extraction justification.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 85% | 88% | increased | ECB SDW monthly exchange-rate evidence preserved SDMX query, structure, series, attribute, and observation evidence through existing `raw_evidence`, `attributes`, and `source_payload`; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 80% | 83% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; no post-boundary production code changed. |
| Most future engineering effort belongs before the observed boundary | 82% | 84% | increased | Implementation effort centered on ECB-specific SDMX interpretation, period/unit/indicator identity, and metadata preservation before the boundary. |
| Provider interpretation should remain source-specific for now | 78% | 82% | increased | ECB shared GenericData XML mechanics with OECD, but EXR dataflow dimensions, unit construction, structure metadata, and provider indicator semantics remained ECB-specific. |
| SDMX commonality is currently only protocol-level | 70% | 78% | increased | ECB confirmed repeated SDMX XML/protocol mechanics while not producing enough source-neutral semantic convergence to justify an SDMX Interpretation Layer. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-055 produced future extraction evidence around repeated SDMX mechanics but did not satisfy the contract/algorithm/implementation convergence gate. |
| Source-specific first remains correct for acquisition/parsing | 82% | 84% | increased | A bounded source-specific ECB adapter stayed small, auditable, deterministic, and framework-free while preserving provider evidence. |
| Prediction-ledger implementation improves future estimation quality | 75% | 80% | increased | The prediction ledger cleanly separated confirmed architecture stability from future SDMX extraction evidence, improving the next SDMX-family estimate. |
