# TASK-036 decision analysis — next scope after deterministic canonicalization proposal workflow

Status: accepted analysis
Date: 2026-06-13
Related task: TASK-036
Related decision: `artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md`
Preceded by: TASK-034, DEC-019, DEC-018, DEC-016, DEC-015

## Evaluation posture

TASK-036 optimizes for uncertainty reduction, not capability expansion.

Criteria:

1. smallest bounded implementation;
2. highest learning value;
3. lowest architectural risk;
4. strongest validation of the TASK-032/TASK-034 canonicalization foundation;
5. avoidance of premature AI/model dependence, database persistence, report expansion, or new sources.

The central evidence from TASK-034 is that the deterministic workflow now works mechanically:

```text
provider evidence
-> deterministic proposal generation
-> review routing
-> mapping update proposals
-> audit output
```

The workflow generated 3 provider-evidence-derived proposals and 3 mapping update proposals for WDI, OECD/SDMX, and Eurostat GDP evidence. All proposals are review-required and `auto_apply: false`. The report also shows that WDI remains blocked by `unknown_unit_metadata`, while OECD and Eurostat have explicit but non-comparable unit profiles.

## Evidence from TASK-034

Inspected evidence:

- `artifacts/tasks/TASK-034-implement-tiny-deterministic-canonicalization-proposal-workflow.md`;
- `artifacts/reports/canonicalization-proposal-workflow-20260613.json`;
- `src/macroforge/canonicalization_state.py`;
- `tests/test_canonicalization_proposal_workflow.py`;
- `artifacts/decisions/DEC-019-next-scope-deterministic-canonicalization-proposal-workflow.md`;
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`;
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`;
- `docs/architecture/canonicalization-next-scope-decision-analysis.md`.

TASK-034 succeeded on its bounded acceptance checks:

- generated from provider evidence: pass;
- proposal state separate from accepted mapping state: pass;
- high-impact review routing: pass;
- unknown unit caveat propagated: pass;
- annual/quarterly non-aggregation: pass;
- no auto-apply mapping updates: pass.

What the evidence proves:

- The file-backed canonicalization state can support a deterministic proposal lifecycle.
- Proposal generation can remain separate from accepted/provisional mapping state.
- The audit report can preserve provenance, ruleset, model/prompt absence, unit caveats, period policy, and review routing.
- High-impact GDP mappings remain review-gated, as required by DEC-018.

What the evidence does not yet prove:

- Whether richer provider evidence reduces avoidable review blockers.
- Whether AI proposal generation improves proposal quality rather than compensating for missing metadata.
- Whether review routing can become exception-focused for GDP-like mappings.
- Whether canonicalization state should be persisted in PostgreSQL.
- Whether reports should consume proposal/accepted mapping state.

## Option A — Bounded WDI unit metadata enrichment for canonicalization evidence

Assessment: best next step.

Uncertainty reduced:

- Whether the current WDI `unknown_unit_metadata` blocker is an artifact of missing source-specific metadata extraction rather than a canonicalization workflow limitation.
- Whether enriched provider evidence can make deterministic proposals and review queues more useful before AI/model dependence.

Implementation size:

- Small if limited to recorded/fixture-backed WDI indicator metadata for the existing GDP slice.
- Can reuse existing WDI source-specific patterns and canonicalization state/report writers.

Learning value:

- High. It directly addresses the sharpest blocker surfaced by TASK-034.
- It tests whether canonicalization quality is currently limited by evidence richness, not proposal mechanics.

Architectural risk:

- Low if kept source-specific, fixture-backed, and report/audit oriented.
- Does not require schema migrations, live database writes, unit conversion, frequency aggregation, report integration, or generalized source framework work.

Validation of prior foundation:

- Strong. Re-running the deterministic proposal workflow after WDI enrichment can show whether the WDI proposal moves from `unknown_unit_metadata` to an explicit unit/currency comparability caveat.

AI/model dependence:

- Avoided. This preserves the sequence: evidence quality first, then AI proposal quality later.

Explicit deferrals:

- no model calls;
- no prompt/provider setup;
- no PostgreSQL persistence;
- no report integration;
- no unit conversion;
- no new sources;
- no generalized ingestion or metadata framework.

## Option B — AI-assisted proposal generation

Assessment: defer.

Uncertainty reduced:

- Eventually, this will test whether AI can improve canonicalization proposal quality and reasoning.

Why not next:

- TASK-034 shows at least one central blocker is missing WDI unit metadata. Calling an AI model now would confound model quality with sparse source evidence.
- It introduces prompts, provider/version governance, validation, reproducibility, and failure handling before the bounded evidence substrate is complete enough for a fair test.

## Option C — Review-policy calibration

Assessment: defer until after WDI metadata enrichment.

Uncertainty reduced:

- Whether review routing can become more exception-focused.

Why not next:

- All current GDP mappings are high-impact, so review-required is expected under DEC-018.
- WDI unknown metadata would still require review regardless of policy calibration.
- Better calibration needs a less obviously metadata-blocked proposal set.

## Option D — PostgreSQL persistence design for canonicalization state

Assessment: defer.

Uncertainty reduced:

- Whether canonicalization state belongs in database tables.

Why not next:

- Persistence would freeze state semantics before evidence enrichment shows what fields are necessary.
- The file-backed workflow remains sufficient for the current bounded scale.

## Option E — Integrate canonicalization state into the canonical GDP snapshot report

Assessment: defer.

Uncertainty reduced:

- Whether reports can consume governed mapping state.

Why not next:

- Report integration would present canonicalization semantics to a research-facing artifact while WDI unit metadata is still unknown.
- It would mix evidence-enrichment uncertainty with report semantics.

## Option F — New source or broader capability expansion

Assessment: reject for this step.

Why not next:

- New sources and broader capability would add surface area before resolving the central canonicalization evidence blocker exposed by the existing bounded GDP set.

## Comparative ranking

| Option | Smallest implementation | Learning value | Architectural risk | Validates foundation | Avoids premature AI/model dependence | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| A. Bounded WDI unit metadata enrichment | High | High | Low | High | High | Best |
| B. AI-assisted proposal generation | Low-medium | Medium but confounded | High | Medium | Low | Defer |
| C. Review-policy calibration | Medium | Medium | Medium | Medium | High | Defer |
| D. PostgreSQL persistence design | Low | Medium | High | Low-medium | High | Defer |
| E. Report integration | Medium | Medium | Medium-high | Medium | High | Defer |
| F. New source/capability expansion | Low | Low for current uncertainty | High | Low | Variable | Reject now |

## Recommendation

Select option A: a bounded WDI unit metadata enrichment task for canonicalization evidence.

The next implementation should remain source-specific and fixture-backed. It should enrich only the existing WDI GDP evidence enough to replace `unknown_unit_metadata` with explicit source-derived unit/currency metadata in the canonicalization state/proposal workflow, then regenerate or validate a bounded audit artifact. It should not implement unit conversion, accepted mapping mutation, AI/model calls, database persistence, report integration, new source onboarding, live/default database writes, or generalized metadata framework extraction.
