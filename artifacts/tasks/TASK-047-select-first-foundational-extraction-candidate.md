# TASK-047 — Select first foundational post-boundary extraction candidate

Status: complete
Date: 2026-06-27

## Objective

Determine which repeated post-observed-boundary behavior should become MacroForge's first shared foundational platform capability.

Do not implement the capability. Use implementation evidence plus the required deep ArchitectureHarvest/MetaHarvest consultation under the `foundational_capability_extraction` trigger.

## Scope completed

- Reviewed current WDI/OECD/Eurostat post-boundary loader implementations.
- Evaluated lineage generation, quality-check handling, provider metadata handling, canonical dimension mechanics, canonical load/upsert mechanics, and validation helpers against the Constitution's convergence threshold.
- Ran trigger-gated ArchitectureHarvest/MetaHarvest consultation with the governance deeper-read cap.
- Produced the durable report: `artifacts/reports/R-20260627-foundational-capability-extraction-candidate.md`.
- Selected `Deterministic Lineage Event Emission` as the recommended first extraction candidate.

## ArchitectureHarvest consultation evidence

Command run:

```bash
python3 tools/consult_metaharvest.py --allow-governance-deeper-cap --json --task-summary 'foundational capability extraction: select first shared deterministic post-observed-boundary infrastructure from converged implementation evidence; evaluate lineage generation, quality-check handling, provider metadata handling, canonical dimension mechanics, canonical load/upsert mechanics, validation helpers; investigate mature patterns, failure modes, over-abstraction risks, minimal extraction, reasons not to extract; no implementation.'
```

Result summary:

- Consultation action: `consult`.
- Matched triggers: `source_contract_design_changes`, `lineage_or_validation_registry_changes`, `foundational_capability_extraction`.
- Confidence: Medium.
- Retrieved records included OpenMetadata schema-first metadata, lineage resource, and governance taxonomy component cards.
- Advisory conclusion used locally: lineage edge/event details are useful as a compact deterministic concept; do not adopt graph APIs, catalog platforms, runtime systems, or broad governance taxonomies.

## Outcome

Recommended first foundational capability:

```text
Deterministic Lineage Event Emission
```

Recommended next maturity transition:

```text
Deterministic Lineage Event Emission: Specified -> Verified
```

Project-level maturity implication:

```text
Shared Post-Boundary Infrastructure Extraction: Discovered -> Specified
```

## Rejected candidates

- Quality-check handling: check row shape repeats, but check semantics do not yet converge.
- Provider metadata handling: metadata remains provider/source-specific and would likely create false abstraction.
- Canonical dimension mechanics: repeated code carries real canonical-domain semantics and is too high-risk for first extraction.
- Canonical load/upsert mechanics: fact upsert is close to core correctness and still coupled to source-specific dimension joins.
- Validation helpers: Deterministic Change Verification is already Verified and should not be expanded further now.

## Explicit non-goals preserved

No implementation, code refactor, migration, source expansion, provider metadata framework, quality-check framework, canonical loader abstraction, runtime orchestration, catalog integration, graph API, live/default database write, canonical state mutation, or git push was performed.

## Verification

Final verification is recorded in `context/latest_handoff.md`.
