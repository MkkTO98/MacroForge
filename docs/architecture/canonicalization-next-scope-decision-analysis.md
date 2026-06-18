# TASK-033 decision analysis — canonicalization workflow before complexity

Status: accepted analysis
Date: 2026-06-05
Related decision: `artifacts/decisions/DEC-019-next-scope-deterministic-canonicalization-proposal-workflow.md`
Related task: TASK-033

## Evaluation posture

TASK-033 optimizes for uncertainty reduction, not capability.

Criteria:

1. smallest implementation;
2. highest learning value;
3. lowest architectural risk;
4. maximum validation of the TASK-032 foundation;
5. avoid introducing AI dependence before workflow validation.

The central uncertainty after TASK-032 is not whether MacroForge can represent canonicalization state. TASK-032 proved that. The central uncertainty is whether that state can support an auditable workflow loop:

```text
provider evidence
-> proposal generation
-> review routing
-> accepted/provisional mapping update proposal
-> audit report
```

## Option A — Deterministic proposal-generation workflow for a tiny fixture set

Assessment: best next step.

Smallest implementation:

- Reuses existing fixture-backed TASK-032 evidence and audit structures.
- Requires only a small deterministic ruleset and tests around workflow output.
- Avoids schema persistence, AI configuration, prompt design, live fetches, new sources, and ontology growth.

Highest learning value:

- Tests the exact workflow gap left by TASK-032.
- Reveals whether identifiers, provenance, run records, proposal status, review routing, unit caveats, and accepted/provisional mapping separation are usable when proposals are generated rather than pre-seeded.
- Produces review-queue evidence before deciding whether AI reduces or amplifies review burden.

Lowest architectural risk:

- Keeps state file-backed and deterministic for one more iteration.
- Avoids freezing untested workflow semantics into PostgreSQL tables.
- Avoids shaping architecture around model/prompt artifacts before workflow mechanics are validated.

Maximum TASK-032 validation:

- Directly exercises provider indicator evidence, canonicalization runs, mapping proposals, unit/comparability profiles, accepted/provisional mapping state, review status, and supersession fields.
- Validates that proposals remain separate from accepted mapping state.
- Validates that high-impact GDP remains review-routed and WDI unknown unit metadata blocks false comparability.

Avoids AI dependence:

- Uses deterministic behavior so failures are attributable to workflow/state design, not model behavior.

Primary uncertainty reduced:

- Can the TASK-032 foundation support the complete canonicalization workflow loop for bounded GDP evidence?

## Option B — AI-assisted proposal generation

Assessment: defer.

Smallest implementation:

- Not small. Even a tiny AI workflow introduces prompts, model/provider versions, reproducibility concerns, output validation, credentials/configuration, failure modes, and policy capture.

Learning value:

- Potentially high later, but confounded now. If results fail, MacroForge could not isolate whether the issue is evidence richness, state design, prompt design, model choice, or review policy.

Architectural risk:

- High relative to maturity. It introduces AI dependence before validating the non-AI lifecycle.

TASK-032 validation:

- Partial. It would emit proposals into TASK-032 state, but model variance would obscure state/workflow defects.

AI dependence:

- Fails the user's explicit criterion to avoid AI dependence before workflow validation.

Primary uncertainty left unresolved:

- Whether the canonicalization workflow works without AI complexity.

## Option C — Additional canonicalization state expansion

Assessment: defer.

Smallest implementation:

- Larger than needed because TASK-032 already represented the minimum required entities.

Learning value:

- Low-to-medium. It increases representational capability but does not prove the existing representation is operational.

Architectural risk:

- Medium. It risks state/entity bloat and pseudo-ontology growth before workflow pressure proves the fields are needed.

TASK-032 validation:

- Weak-to-medium. It validates extensibility more than workflow correctness.

AI dependence:

- Avoided, but solves a less important uncertainty.

Primary uncertainty left unresolved:

- Whether generated proposals, review routing, and mapping-state transitions work end to end.

## Option D — Alternative bounded scope

Assessment: defer unless TASK-034 reveals a sharper blocker.

Alternatives considered:

- WDI unit metadata enrichment.
- PostgreSQL persistence for canonicalization state.
- Deterministic report integration.
- Review policy calibration.
- Deferring canonicalization for another data/report task.

Smallest implementation:

- WDI enrichment may be small, but it optimizes a known caveat rather than validating the workflow.
- PostgreSQL persistence is larger and prematurely commits to state semantics.
- Report integration should follow a proven proposal lifecycle.
- Review calibration needs generated proposal examples.

Learning value:

- Each alternative has value, but none reduces the central workflow uncertainty as directly as option A.

Architectural risk:

- WDI enrichment is low-risk but narrow.
- PostgreSQL persistence is higher-risk.
- Report integration risks presenting static seed state as more mature than it is.

TASK-032 validation:

- Adjacent rather than direct.

AI dependence:

- Usually avoided, but the validation target is less precise than option A.

Primary uncertainty left unresolved:

- Whether TASK-032 state can support canonicalization workflow before AI/model complexity is introduced.

## Comparative ranking

| Option | Smallest implementation | Learning value | Architectural risk | Validates TASK-032 | Avoids AI dependence | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| A. Deterministic tiny proposal workflow | High | High | Low | High | High | Best |
| B. AI-assisted proposal generation | Low | Medium but confounded | High | Medium | Low | Defer |
| C. More state expansion | Medium | Low-medium | Medium | Low-medium | High | Defer |
| D. Alternative bounded scope | Variable | Medium | Variable | Medium-low | Usually high | Defer |

## Recommendation

Select option A.

The next implementation should be a tiny deterministic proposal-generation workflow over the existing fixture evidence. It should validate the canonicalization workflow before introducing AI dependence, schema persistence, richer state, report integration, or new data scope.
