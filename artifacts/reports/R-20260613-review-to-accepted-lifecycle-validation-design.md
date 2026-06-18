# Review-to-Accepted-State Lifecycle Validation Design

Date: 2026-06-13
Timestamp UTC: 2026-06-13T20:56:22Z
Scope: Recommendation/design artifact only. No TASK-038 was created, selected, or started. No implementation was performed.

## Goal

Design the smallest bounded validation task capable of proving or falsifying this claim:

> MacroForge can move from proposal state to governed accepted/provisional mapping state with replayable audit evidence.

This artifact uses the uncertainty analysis in `artifacts/reports/R-20260613-largest-canonicalization-uncertainty.md`, which ranked review-to-accepted-state lifecycle and check gating as the largest remaining canonicalization architecture uncertainty after TASK-037.

## Smallest experiment

Candidate experiment title, if the user later approves task creation:

`Simulate bounded canonicalization proposal review-to-accepted-state lifecycle`

Smallest useful experiment:

Create a file-backed, deterministic review simulation over the existing WDI/OECD/Eurostat GDP canonicalization proposal set. The experiment would not create new source evidence, not call models, not mutate existing accepted mapping state automatically, and not integrate reports. It would add only enough proposed review-decision, accepted-state-delta, check-gate, manifest-delta, lineage, and replay artifacts to prove whether a proposal can be traceably reviewed and converted into governed accepted/provisional state.

The experiment should answer one yes/no question:

Can a future implementation replay, from existing fixture-backed evidence alone, the path:

```text
provider evidence
-> TASK-034/TASK-037 proposal artifact
-> explicit review decision
-> accepted/provisional mapping-state delta
-> accepted-state check gates
-> manifest update delta
-> evidence/lineage pointers
-> deterministic replay report
```

without silent auto-apply, hidden reviewer judgment, mutation of proposal evidence, live data access, or report integration?

## Hard scope boundaries

Allowed:

- Existing WDI/OECD/Eurostat GDP fixture-backed evidence only.
- Existing TASK-034/TASK-037 proposal and enrichment artifacts only.
- New recommendation/design artifacts describing the future validation task.
- If later approved as a task, new fixture-style review-decision/check/lineage/replay artifacts under `artifacts/reports/` or a task-specific artifact folder.

Rejected for this design and for the future bounded validation task unless separately approved:

- Creating TASK-038 now.
- AI/model calls, prompt/provider setup, embeddings, or calibration benchmarks.
- Live source fetches.
- New sources or indicators.
- PostgreSQL migrations or canonicalization persistence.
- Live/default `macro` database writes.
- Unit/currency conversion.
- Quarterly-to-annual aggregation.
- Canonical GDP snapshot report integration.
- Broad metadata/source framework extraction.
- Runtime adoption of dbt, Dagster, orchestration, scheduling, or materialization frameworks.
- Automatic mutation of accepted mapping state from proposal state.
- Git push.

## Existing evidence to use

The future validation task should use exactly these current evidence classes.

### Source/proposal evidence

- `artifacts/reports/canonicalization-state-foundation-20260605.json`
  - Existing provider indicator evidence.
  - Existing provisional accepted mappings.
  - Existing unit/comparability profiles.
  - Existing proposal/accepted-state separation.
- `artifacts/reports/canonicalization-proposal-workflow-20260613.json`
  - TASK-034 generated workflow proposals.
  - TASK-034 mapping update proposals.
  - Existing `auto_apply: false` proposal behavior.
  - Existing high-impact GDP review routing.
- `artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json`
  - TASK-037 WDI metadata enrichment evidence.
  - Evidence that WDI metadata is source metadata, not canonical truth.
  - Evidence that no accepted mapping state was auto-mutated.

### Governance/architecture evidence

- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`
  - Accepted lifecycle: provider evidence -> canonicalization run -> proposal -> review -> accepted/provisional mapping state -> curated facts/reports.
  - Required review for high-impact concepts and unknown/conflicting unit metadata.
- `artifacts/decisions/DEC-019-next-scope-deterministic-canonicalization-proposal-workflow.md`
  - Deterministic workflow scope and proposal/accepted-state separation.
- `artifacts/decisions/DEC-020-architectureharvest-canonical-asset-manifest-registry.md`
  - Manifest fields and boundaries.
- `artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md`
  - WDI unit metadata enrichment scope and no-auto-apply boundary.
- `artifacts/manifests/canonical_assets.json`
  - Current file-backed manifest vocabulary and existing provisional mapping entries.
- `architecture/architectureharvest/adoption_candidates.md`
  - Deferred `MF-AH-REV-002` lineage edge artifacts.
  - Deferred `MF-AH-REV-003` accepted-state check/contract artifacts.

## Minimal review decision artifacts

The validation task should define, and then fixture-write only if approved, one compact review-decision artifact with three review decisions: one WDI, one OECD, and one Eurostat GDP mapping proposal.

Recommended future artifact path:

`artifacts/reports/canonicalization-review-decisions-20260613.json`

Minimal top-level shape:

```json
{
  "review_run_id": "review-run:canonicalization-gdp-lifecycle-20260613",
  "review_policy_version": "DEC-018",
  "proposal_source_artifacts": [
    "artifacts/reports/canonicalization-proposal-workflow-20260613.json",
    "artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json"
  ],
  "review_decisions": [],
  "manual_review_required": true,
  "auto_apply": false
}
```

Each review decision needs only these fields:

- `review_decision_id`: stable ID for replay.
- `reviewed_workflow_proposal_id`: TASK-034/TASK-037 proposal ID.
- `reviewed_mapping_update_proposal_id`: TASK-034 mapping update proposal ID.
- `reviewer_role`: `MacroForge canonicalization review`.
- `decision`: one of `accept_as_provisional`, `accept_as_accepted`, `reject`, `defer`.
- `decision_rationale`: short evidence-backed reason.
- `required_caveats`: caveats that must remain on accepted/provisional state.
- `required_checks`: check IDs that must pass before the decision can be applied.
- `accepted_state_delta_id`: pointer to the simulated state delta.
- `manifest_delta_id`: pointer to the simulated manifest update.
- `evidence_links`: list of evidence artifact paths and IDs.
- `created_at`: deterministic timestamp used by the fixture.

Recommended minimum decision set:

1. WDI `NY.GDP.MKTP.CD` -> `MACRO_GDP_OUTPUT`
   - Decision: `accept_as_provisional`.
   - Rationale: TASK-037 resolves generic unknown-unit metadata into explicit current-USD source metadata, but GDP remains high-impact and conversion/report-impact policy is still deferred.
   - Required caveats: source metadata evidence is not canonical truth; no conversion; high-impact review retained.

2. OECD `B1GQ` -> `MACRO_GDP_OUTPUT`
   - Decision: `defer` or `accept_as_provisional` depending on the strictness of the check gate.
   - Smallest falsification-friendly recommendation: use `defer` because multiple unit profiles (`USD_EXC`, `USD_PPP`) remain ambiguous without basis-specific mapping choice.
   - Required caveats: exchange-rate USD and PPP USD are separate comparability profiles.

3. Eurostat `B1GQ` -> `MACRO_GDP_OUTPUT`
   - Decision: `defer`.
   - Rationale: quarterly frequency and current-price million EUR values remain non-comparable without explicit conversion and aggregation policy.
   - Required caveats: no frequency aggregation; no currency conversion; report integration deferred.

This mix is intentionally small and information-rich: one provisional acceptance candidate plus two deferrals is enough to prove that the lifecycle supports both forward movement and governed non-acceptance.

## Minimal accepted-state check gates

The validation task should define a compact check-gate artifact, not a broad framework.

Recommended future artifact path:

`artifacts/reports/canonicalization-accepted-state-checks-20260613.json`

Check gates should be applied to each review decision before a simulated accepted/provisional state delta can be considered valid.

Required gates:

1. `proposal_exists`
   - The referenced workflow proposal exists in TASK-034/TASK-037 artifacts.

2. `mapping_update_proposal_exists`
   - The referenced mapping update proposal exists and targets the expected existing mapping ID.

3. `auto_apply_false`
   - The proposal and review decision both preserve `auto_apply: false`.

4. `high_impact_review_recorded`
   - GDP review is explicitly recorded by review decision, not inferred from confidence score.

5. `evidence_links_complete`
   - The review decision links source evidence, proposal artifact, enrichment artifact when relevant, accepted-state delta, and manifest delta.

6. `unit_frequency_caveats_preserved`
   - Required unit/frequency/comparability caveats are present in the state delta and manifest delta.

7. `no_conversion_or_aggregation`
   - State delta does not claim currency conversion, unit conversion, or quarterly-to-annual aggregation.

8. `proposal_state_immutable`
   - Proposal artifacts are read-only inputs; accepted/provisional changes are represented as deltas, not edits to proposal evidence.

9. `accepted_status_allowed`
   - Resulting mapping status is one of the manifest/state-allowed statuses: `proposed`, `provisional`, `accepted`, `rejected`, `retired`.

10. `report_impact_flagged`
   - The decision records whether existing reports would be affected; this experiment should flag `report_integration_deferred` rather than modify reports.

11. `replay_inputs_declared`
   - The replay report can list every input artifact and ID required to reproduce the decision outcome.

A decision fails the validation task if any required gate is missing, ambiguous, manually inferred outside the artifact, or contradicted by the proposed state/manifest delta.

## Manifest update behavior

The validation task should not mutate `artifacts/manifests/canonical_assets.json` directly unless the future task explicitly includes an implementation step. The smallest safe experiment should first produce a manifest delta artifact.

Recommended future artifact path:

`artifacts/reports/canonicalization-manifest-delta-20260613.json`

Required behavior:

- Existing mapping asset entries remain the base state.
- The delta references existing `asset_key` values:
  - `mapping.wdi.gdp_to_macro_gdp_output`
  - `mapping.oecd_naag.gdp_to_macro_gdp_output`
  - `mapping.eurostat_namq_gdp.to_macro_gdp_output`
- Each delta records:
  - `asset_key`;
  - old status;
  - proposed new status;
  - review decision ID;
  - accepted/provisional mapping pointer;
  - required caveats;
  - related artifact paths;
  - source provider evidence pointers;
  - lineage edge IDs, if included;
  - check result IDs;
  - no direct report integration.
- WDI may move from existing provisional/review-required posture to explicitly review-approved provisional state.
- OECD and Eurostat should remain provisional/deferred unless their caveats can be fully represented without implying conversion/aggregation.
- The delta must not create new asset roles, new runtime concepts, or framework-specific fields.

A later implementation task may choose whether to apply this delta to `canonical_assets.json`, but this validation experiment only needs to prove that a safe delta can be generated and replayed.

## Evidence linkage requirements

Every review decision and state/manifest delta should link these evidence layers explicitly:

1. Provider evidence ID
   - Example: `evidence:WDI:WDI:NY.GDP.MKTP.CD`.

2. Source evidence artifact path
   - `artifacts/reports/canonicalization-state-foundation-20260605.json`.

3. Workflow proposal ID
   - Example: `workflow-proposal:run:canonicalization-proposal-workflow-20260613:WDI:NY.GDP.MKTP.CD`.

4. Mapping update proposal ID
   - Example: `mapping-update:workflow-proposal:run:canonicalization-proposal-workflow-20260613:WDI:NY.GDP.MKTP.CD`.

5. Enrichment evidence when applicable
   - WDI should link `artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json` and the WDI fixture metadata role.

6. Target accepted/provisional mapping ID
   - Example: `mapping:v1:WDI:NY.GDP.MKTP.CD:MACRO_GDP_OUTPUT`.

7. Review decision ID
   - Example: `review-decision:review-run:canonicalization-gdp-lifecycle-20260613:WDI:NY.GDP.MKTP.CD`.

8. Check result IDs
   - One result per required gate per reviewed mapping, or a compact object with named gate statuses.

9. Manifest asset key and proposed delta ID
   - Example: `manifest-delta:canonical-assets:20260613:mapping.wdi.gdp_to_macro_gdp_output`.

10. Replay input manifest
   - A top-level list of artifact paths, IDs, and expected checksums if a future implementation adds checksums.

The validation should fail if any lifecycle step relies on prose-only evidence that cannot be followed by ID/path from proposal to decision to state/manifest delta.

## Replay requirements

The smallest replay requirement is a deterministic replay report, not a database replay.

Recommended future artifact path:

`artifacts/reports/canonicalization-review-lifecycle-replay-20260613.json`

Replay must prove:

1. All input artifact paths are declared.
2. All reviewed proposal IDs can be found in the input artifacts.
3. All mapping update proposal IDs can be found in the input artifacts.
4. Each review decision references exactly one workflow proposal and one mapping update proposal.
5. Each state delta references exactly one review decision.
6. Each manifest delta references exactly one state delta or review decision.
7. Every required check gate has an explicit pass/fail/not_applicable result.
8. Proposal artifacts remain unchanged.
9. No accepted mapping state is changed except through the simulated delta artifact.
10. No report artifact is changed or claimed as integrated.
11. Re-running the replay over the same inputs produces the same review outcomes and delta IDs.
12. The replay report can explain why each mapping outcome is `accepted`, `provisional`, `rejected`, or `deferred` without using hidden chat context.

A future implementation may add file checksums, but the minimal validation does not require them if the artifact paths and IDs are stable and tests prove deterministic output.

## Success criteria

The validation task succeeds if all of the following are true:

1. It uses only existing WDI/OECD/Eurostat GDP fixture-backed evidence.
2. It uses existing TASK-034/TASK-037 proposal artifacts as input.
3. It creates explicit review decisions for WDI, OECD, and Eurostat GDP mapping proposals.
4. It proves at least one mapping can move to a more governed state, likely WDI as `review_approved_provisional`, without auto-apply.
5. It proves at least one mapping can be deferred or rejected with explicit reasons while preserving proposal evidence.
6. It defines and evaluates minimal accepted-state check gates.
7. It produces a manifest delta rather than silently editing the manifest.
8. It links provider evidence -> proposal -> mapping update proposal -> review decision -> state delta -> manifest delta -> replay report by IDs and paths.
9. It proves replayability from file-backed artifacts without live fetches, database writes, model calls, or hidden chat context.
10. It preserves unit/frequency caveats and does not imply conversion or aggregation.
11. It leaves existing reports unchanged and marks report integration as deferred.
12. Full tests, coherence, and architecture audit pass after artifact creation.

If these criteria pass, MacroForge has enough evidence to say the review-to-accepted-state lifecycle is viable in bounded file-backed form.

## Failure criteria

The validation task fails if any of the following occur:

1. Review decisions cannot be expressed without changing proposal artifacts in place.
2. Acceptance/provisional state cannot be represented as a deterministic delta from existing proposal evidence.
3. A mapping appears accepted only because a confidence score is high, not because a review decision exists.
4. WDI cannot move beyond generic review-required posture even after TASK-037 metadata enrichment, and the artifact cannot explain why.
5. OECD/Eurostat caveats cannot be represented without implying conversion, aggregation, or source-specific fact columns.
6. Manifest updates require broad schema/runtime changes rather than a small delta.
7. Evidence links are incomplete, prose-only, or impossible to replay by ID/path.
8. Replay depends on live data, database state, model output, current chat context, or manual interpretation outside the artifacts.
9. The lifecycle collapses into manual-every-mapping governance with no reusable gates or deltas.
10. The lifecycle silently auto-applies mapping changes from proposals.
11. Tests/coherence/audit reveal drift, missing artifacts, oversized handoff/state, or project-governance violations.

If these criteria fail, MacroForge should modify or reject the current canonicalization lifecycle before adding AI assistance, persistence, or report integration.

## Adopt / modify / reject outcome model

The future validation task should end with one of these outcomes.

### Adopt narrowly

Use when:

- All success criteria pass.
- The lifecycle works with small file-backed artifacts.
- Review decisions, check gates, state deltas, manifest deltas, and replay reports are understandable from ordinary JSON/Markdown files.
- No runtime/framework/database/model dependence is needed.

Consequence:

- Record that MacroForge can support a bounded proposal-to-governed-state lifecycle.
- Consider a later task to apply the validated manifest/state delta or to test AI proposal generation against the now-defined review lifecycle.

### Modify

Use when:

- The experiment mostly works, but one lifecycle surface needs adjustment.
- Example modifications:
  - review decisions need one extra field;
  - check gates need to distinguish `accepted`, `review_approved_provisional`, and `deferred` more clearly;
  - manifest delta needs explicit lineage edge IDs;
  - WDI can be review-approved provisional but OECD/Eurostat require sharper deferral semantics.

Consequence:

- Keep the lifecycle direction, but revise the artifact shape before applying it to durable accepted state.
- Do not proceed to AI/model or persistence work until the modified lifecycle passes replay.

### Reject

Use when:

- The lifecycle cannot be represented without auto-apply, hidden manual judgment, proposal mutation, framework adoption, or broad schema changes.
- Evidence links cannot be made replayable from current artifacts.
- Check gates are too weak to distinguish safe provisional acceptance from unsafe mapping changes.

Consequence:

- Reopen DEC-018 or create a new governance decision before implementation proceeds.
- Reconsider whether accepted/provisional mapping state needs a different model, stronger metadata evidence contract, or narrower human review policy.

### More evidence required

Use when:

- The artifact shape works but current WDI/OECD/Eurostat GDP evidence is insufficient to evaluate at least one decisive lifecycle transition.
- This should be treated as a modification outcome, not as approval to add new sources or AI calls automatically.

Consequence:

- Identify the smallest missing evidence class.
- Prefer source-specific metadata enrichment or clearer review policy over new broad frameworks.

## Why this is the smallest falsifying experiment

This experiment is smaller than AI proposal generation, PostgreSQL persistence, or report integration because it tests only the architectural crossing that is still uncertain: proposal state to governed accepted/provisional mapping state.

It is also falsification-friendly:

- If WDI can be review-approved provisional while OECD/Eurostat remain explicitly deferred, the lifecycle supports governed partial progress.
- If all three remain review-required because the system cannot express decisions, deltas, checks, or replay, the lifecycle is not yet viable.
- If the experiment requires model output, live data, database persistence, report changes, or framework concepts, the current file-backed architecture is insufficient for this stage.

## Recommendation status

Recommendation/design only. No TASK-038 was created. No task was opened. No decision was accepted. No code or data implementation was performed.
