# Implementation Design — Trigger-Gated MetaHarvest Consultation

Date: 2026-06-26
Status: design only
Type: implementation design report, not implementation
Related artifact: `artifacts/reports/R-20260619-metaharvest-trigger-gated-retrieval-future-work.md`

## Executive summary

MacroForge should add the smallest possible trigger-gated MetaHarvest consultation mechanism at the existing task-scope / governance-classification gate.

This design does not implement the mechanism, create implementation tasks, or change workflow behavior. It specifies a narrow future implementation that can be reviewed before any workflow changes are made.

Recommended next integration work item:

> Trigger-gated consultation remains the next recommended integration work item because the practical TASK-042 consultation trial produced sufficient evidence of value at low retrieval cost.

## Goal

When a proposed or active MacroForge task materially matches existing MetaHarvest consultation triggers, MacroForge should run compact MetaHarvest retrieval during preflight/governance classification and attach a short advisory retrieval note to the task context.

The mechanism must not run during ordinary startup and must not run for routine tasks.

## Non-goals and hard boundaries

The design must preserve these boundaries:

- MetaHarvest remains advisory evidence only.
- No startup-wide retrieval.
- No mandatory retrieval for all tasks.
- No automatic adoption of MetaHarvest findings.
- No automatic task creation.
- No runtime/framework adoption.
- No authority transfer from MacroForge to MetaHarvest.
- No replacement of MacroForge decisions, task artifacts, human review, or local relevance judgment.
- No broad reading of MetaHarvest project cards, component cards, cloned repos, or full reports unless compact retrieval proves relevance and the task is governance/design-level.

## Existing trigger source

Use the existing MacroForge trigger artifact:

`architecture/architectureharvest/relevance_map.yaml`

Current consultation categories:

- `canonicalization_architecture_changes`
- `source_contract_design_changes`
- `lineage_or_validation_registry_changes`
- `orchestration_or_runtime_adoption_decisions`
- `generalized_ingestion_framework_decisions`

This file is the only initial MacroForge-side trigger source. Do not invent a parallel trigger registry unless later evidence proves the existing relevance map is insufficient.

Architectural invariant against trigger drift:

> New consultation trigger categories must only be added when there is evidence that the absence of such a trigger previously resulted in architectural mistakes, duplicated work, or missed reusable knowledge.

Do not add trigger categories based solely on intuition, speculation, convenience, or broad thematic similarity. A proposed new trigger category needs a file-backed rationale that points to concrete prior failure evidence, such as an architecture decision that had to be reversed, duplicated reusable design work, or a missed MetaHarvest record that would probably have changed the design process. This invariant exists to prevent gradual trigger expansion until consultation effectively runs for nearly every engineering task.

## Recommended insertion point

Insert the trigger check at task-scope / governance classification:

1. Startup/recovery identifies active or proposed work.
2. Agent reads the active/proposed task, user request, or design objective.
3. Agent produces a structured task classification using the taxonomy below.
4. If classification materially matches a trigger in `architecture/architectureharvest/relevance_map.yaml`, run compact MetaHarvest retrieval before proceeding with governance/design reasoning.
5. Attach a compact advisory retrieval note to the working context or report.
6. Continue MacroForge-owned decision-making.

The trigger check should not occur before task scope is known. This avoids startup-wide retrieval.

## Structured task classification

The future helper should not rely on arbitrary English descriptions such as "governance-ish" or "architecture-like". It should emit a compact structured classification before consulting the relevance map.

Recommended classification fields:

```yaml
task_classification_version: 1
task_classification:
  primary_category: <one category>
  secondary_categories: [<zero or more categories>]
  durable_semantic_change: true|false
  routine_execution_only: true|false
  proposed_trigger_matches: [<relevance_map trigger ids>]
  rationale: <one or two sentences>
```

`task_classification_version` is required whenever structured task classification is stored in a report, task artifact, advisory note, or future helper output. Versioning preserves interpretation of historical reports, permits deliberate taxonomy evolution without ambiguity, and avoids breaking older artifacts if the classification model changes.

Recommended category taxonomy:

| Category | Meaning | Default consultation behavior |
| --- | --- | --- |
| `routine_operation` | Run existing commands, checks, closeout, recovery, fixture refresh, report regeneration, or status inspection without changing durable semantics. | Never consult by itself. |
| `feature_implementation` | Add or modify bounded behavior under an existing accepted design. | Do not consult unless it also changes durable architecture, data model, governance, runtime, or cross-project boundary semantics. |
| `architecture_modification` | Change durable architecture, subsystem boundaries, accepted patterns, or project operating model. | Consult when a relevance-map trigger matches. |
| `governance_decision` | Create or revise a decision, review lifecycle, acceptance gate, policy, or authority boundary. | Consult when a relevance-map trigger matches. |
| `data_model_evolution` | Change canonical/staging/raw schema semantics, mapping state, source contracts, metadata models, eligibility states, or lineage/check artifacts. | Consult when source-contract, canonicalization, lineage, or validation triggers match. |
| `runtime_orchestration_adoption` | Evaluate or adopt runtime, scheduler, catalog, orchestration, dbt/Dagster/OpenMetadata-like systems, or materialization platform behavior. | Consult when the runtime/orchestration trigger matches; advisory only and never adoption authority. |
| `cross_project_boundary_change` | Change authority, artifact flow, dependency, or responsibility boundaries between MacroForge, MetaHarvest, ProjectForge, or other EIP projects. | Consult only if a relevance-map trigger also matches; MacroForge boundary decisions remain local. |

The relevance map should match against this structured classification wherever practical. A task should trigger consultation only when both are true:

1. `primary_category` or `secondary_categories` indicates governance/design/architecture/data-model/runtime/cross-project significance rather than routine execution; and
2. `proposed_trigger_matches` contains at least one material trigger from `architecture/architectureharvest/relevance_map.yaml`.

This keeps the mechanism lightweight while making trigger behavior auditable.

The taxonomy is internal to MacroForge's governance model for now. Do not make it user-configurable in the initial implementation. Keep it versioned and evolve it deliberately through reviewed governance changes. If future evidence demonstrates that configurability reduces real maintenance cost without weakening authority boundaries, that can be proposed later as a separate design change.

## Consultation and retrieval contracts

The mechanism has two separate architectural contracts. Keeping them distinct prevents retrieval mechanics from quietly becoming consultation policy and allows retrieval implementation to evolve without changing the governance rule for when consultation is appropriate.

### Consultation Contract

Responsibility: decide whether MetaHarvest should be consulted.

Inputs:

- `task_classification_version` and structured task classification;
- `architecture/architectureharvest/relevance_map.yaml`;
- active consultation triggers;
- trigger-drift invariant and current MacroForge governance boundaries.

Output:

- `consult` or `do_not_consult`;
- matched trigger IDs when `consult`;
- short rationale.

Rules:

- It must never perform retrieval itself.
- It must not inspect MetaHarvest records.
- It must not create tasks, adopt findings, or authorize design changes.
- It must return `do_not_consult` for routine operation unless another structured category records a durable semantic/governance change.
- It must apply the trigger-drift invariant before any future trigger category is added.

### Retrieval Contract

Responsibility: perform bounded MetaHarvest retrieval only after the Consultation Contract has already returned `consult`.

Inputs:

- problem identifier;
- keyword fallback;
- adjacent problem fallback;
- retrieval budget and escalation limits;
- matched trigger IDs and classification rationale for advisory context.

Output:

- compact advisory information suitable for the standardized `MetaHarvest Advisory` block.

Rules:

- It must never decide whether consultation should occur.
- It must not expand trigger categories.
- It must not create tasks, adopt findings, or authorize design changes.
- It must remain read-only and bounded.
- It may evolve retrieval methods later, but only behind the same advisory-only boundary.

## Trigger behavior

Consult MetaHarvest only when the task materially involves at least one trigger category.

### Trigger: `canonicalization_architecture_changes`

Run consultation when work changes or evaluates:

- canonicalization lifecycle semantics;
- accepted/provisional/deferred/rejected mapping state;
- comparability semantics;
- report eligibility semantics;
- review-to-accepted lifecycle;
- canonical asset/manifest semantics;
- mapping-state governance.

Do not run for:

- routine regeneration of existing canonicalization reports;
- typo/documentation edits that do not alter semantics;
- running existing tests.

### Trigger: `source_contract_design_changes`

Run consultation when work changes or evaluates:

- source contract shape;
- new source evidence requirements;
- provider metadata semantics;
- source identity, territory, period, unit, or frequency contract semantics;
- repeated provider metadata patterns that might justify shared definitions.

Do not run for:

- bounded source-specific loader fixes;
- fixture refreshes;
- source-specific parsing where the contract is already accepted.

### Trigger: `lineage_or_validation_registry_changes`

Run consultation when work changes or evaluates:

- lineage artifact shape;
- validation/check-contract semantics;
- reusable report-use gates;
- replay evidence surfaces;
- registry/manifest schema or semantics;
- quality-check gating for downstream eligibility.

Do not run for:

- simply executing existing validation commands;
- ordinary test additions that do not change validation architecture;
- one-off validation report regeneration.

### Trigger: `orchestration_or_runtime_adoption_decisions`

Run consultation when work reopens:

- dbt/Dagster/Airflow/Prefect/OpenMetadata adoption;
- scheduling/runtime adoption;
- catalog/runtime materialization;
- durable orchestration architecture.

Do not run when the task merely preserves the existing no-runtime-adoption boundary.

### Trigger: `generalized_ingestion_framework_decisions`

Run consultation when work reopens:

- generalized ingestion frameworks;
- shared source abstractions;
- plugin systems;
- cross-source framework extraction;
- source framework replacement or consolidation.

Do not run for bounded source-specific implementation under already accepted source-specific-first doctrine.

## Retrieval command design

The Retrieval Contract runs only after the Consultation Contract returns `consult`.

Use MetaHarvest compact retrieval first from the MetaHarvest project root:

`/home/mkkto/srv/EIP/projects/MetaHarvest`

Primary command shape:

```bash
python3 tools/query_knowledge.py --problem <problem_key>
```

Fallback command shape:

```bash
python3 tools/query_knowledge.py --keyword <keyword>
```

Adjacent-problem fallback command shape:

```bash
python3 tools/query_knowledge.py --problem <adjacent_problem_key>
```

The implementation should call the command read-only and capture stdout in memory. It should not redirect output to temp files, delete temp files, mutate MetaHarvest, or mutate MacroForge during retrieval.

## Classification-to-query mapping

Initial mapping should be a tiny deterministic table inside the implementation, or a compact YAML field added later if review approves config-file evolution. The mapping should use structured task classification plus relevance-map trigger IDs, not loose prose alone.

Recommended initial mapping:

| Structured classification / trigger | Primary problem query | Keyword fallback | Adjacent problem fallback |
| --- | --- | --- | --- |
| `data_model_evolution` or `governance_decision` + `canonicalization_architecture_changes` | `canonicalization_lifecycle_comparability_eligibility_check_gates` | `canonicalization` | `transformation_lineage_asset_orchestration`, `metadata_catalog_lineage_governance` |
| `data_model_evolution` + `source_contract_design_changes` | `source_contract_metadata_governance` | `source contract`, `metadata` | `metadata_catalog_lineage_governance` |
| `data_model_evolution` or `governance_decision` + `lineage_or_validation_registry_changes` | `transformation_lineage_asset_orchestration` | `lineage`, `validation`, `contract` | `metadata_catalog_lineage_governance` |
| `runtime_orchestration_adoption` + `orchestration_or_runtime_adoption_decisions` | `transformation_lineage_asset_orchestration` | `orchestration`, `runtime`, `dagster`, `dbt` | `metadata_catalog_lineage_governance` |
| `architecture_modification` + `generalized_ingestion_framework_decisions` | `generalized_ingestion_framework_decisions` | `framework`, `ingestion`, `source-specific` | `transformation_lineage_asset_orchestration` |

The TASK-042 trial showed that exact problem query coverage can be sparse. Therefore fallback is required, not optional.

## Retrieval budget

Default budget per trigger-matched task:

1. Primary problem query: maximum 1 command.
2. Keyword fallback: maximum 1 command if the primary query returns no useful records.
3. Adjacent-problem fallback: maximum 2 commands if keyword fallback is broad or insufficient.
4. Deeper artifact reads: maximum 3 selected MetaHarvest records by default.
5. Absolute deeper-read cap: 5 records only for governance/design reports that explicitly need concepts, patterns, interfaces, and contradictions.
6. Stop if compact retrieval returns no useful records after primary + keyword + adjacent fallback.
7. Stop if retrieved evidence only confirms already-settled no-change doctrine and does not reduce uncertainty.

Context-size controls:

- Attach only a compact advisory note to MacroForge context, not full raw retrieval output.
- Advisory note target size: 1,000-2,000 words for design/governance reports; 300-700 words for task preflight notes.
- Include only:
  - commands run;
  - records consulted;
  - relevant concepts/patterns/interfaces;
  - contradictions;
  - applicability judgment;
  - explicit non-authority disclaimer.
- Store full detailed consultation output only if the task itself is a governance/design report and the output is part of the deliverable.

## Escalation conditions

Escalate from compact retrieval to selected deeper records only when all are true:

1. The task is governance/design/architecture-level or changes durable semantics.
2. Compact retrieval identifies specific relevant records.
3. The compact output is insufficient to assess applicability.
4. The expected value is higher than context cost.

Do not escalate when:

- the task is routine implementation;
- compact retrieval returns no useful records;
- compact retrieval only repeats already settled MacroForge doctrine;
- the deeper record would be used to justify runtime/framework adoption without a separate MacroForge decision;
- the user explicitly asked for no modifications and no deeper inspection is necessary.

## Retrieval failure behavior

Retrieval failure must be non-blocking by default.

Failure classes:

1. MetaHarvest path missing:
   - Record: `MetaHarvest unavailable; consultation skipped.`
   - Continue MacroForge task using local project state.

2. `tools/query_knowledge.py` missing or exits nonzero:
   - Record command and error summary.
   - Continue unless the user explicitly requested a consultation trial as the primary deliverable.

3. Primary problem query returns no records:
   - Run keyword fallback.
   - If keyword fallback returns no records, run at most two adjacent-problem fallbacks.
   - If still empty, record `no relevant MetaHarvest evidence found` and continue.

4. Retrieval returns too many records:
   - Prefer synthesis records over component/project cards.
   - Prefer MacroForge adoption/outcome records over generic candidates.
   - Prefer contradiction records when the task concerns tradeoffs.
   - Stop after the default deeper-read cap.

5. Contradictory advice:
   - Record contradiction.
   - MacroForge doctrine and current decisions decide applicability.
   - Do not auto-resolve in MetaHarvest's favor.

## Output attached to context

The output attached to MacroForge context should use this standardized advisory block:

```text
MetaHarvest Advisory
Reason triggered:
- <structured task category + relevance-map trigger + one-sentence rationale>

Retrieved records:
- <record path or "none">

Confidence:
- <low|medium|high> using the documented confidence semantics below

Relevant prior decisions:
- <MacroForge decision/task/report/state artifacts that remain authoritative>

Recommended considerations:
- <3-7 compact advisory bullets for MacroForge to consider>

Ignored because:
- <retrieved alternative or broader pattern>: <brief reason it is intentionally discarded, e.g. runtime adoption exceeds scope, repeats settled doctrine, not relevant to current task, insufficient evidence>

Authority note:
- Mandatory. MetaHarvest provides historical architectural context only. MacroForge retains full ownership of design decisions. Consultation is advisory rather than authoritative.
```

The Authority note is mandatory for every consultation, even when it feels repetitive, because advisory blocks and reports may later be read without surrounding workflow context.

Confidence semantics:

| Confidence | Meaning |
| --- | --- |
| `high` | MetaHarvest contains evidence for the same architectural problem or substantially identical governance/design tradeoff previously solved or rejected. |
| `medium` | MetaHarvest contains a closely related architectural problem with meaningful transferable guidance, but the current MacroForge task still requires local adaptation. |
| `low` | MetaHarvest contains only analogous prior work, vocabulary, or weakly related pattern evidence; use only as context, not as strong recommendation evidence. |

Confidence is not truth authority and does not override MacroForge decisions. It only describes retrieval relevance and transferability.

The "Ignored because" section is mandatory when retrieval surfaces alternatives that are intentionally not used. This prevents future agents from repeatedly re-evaluating already rejected approaches such as broad dbt/Dagster/OpenMetadata adoption, startup-wide retrieval, or generic ingestion frameworks.

For file-backed design reports, the advisory block can be embedded in the report. For implementation tasks, it should remain a short preflight note rather than a new artifact unless the task already requires a governance report.

## Workflow diagram

```text
User request / active task
        |
        v
Bounded MacroForge recovery
        |
        v
Read active/proposed task scope
        |
        v
Classify work with structured taxonomy
        |
        +--> routine implementation / tests / fixture refresh / closeout only
        |        |
        |        v
        |   No MetaHarvest retrieval
        |
        +--> governance/design/architecture or durable semantic change
                 |
                 v
          Check architecture/architectureharvest/relevance_map.yaml
          through Consultation Contract
                 |
                 +--> do_not_consult
                 |        |
                 |        v
                 |   No MetaHarvest retrieval
                 |
                 +--> consult
                          |
                          v
                   Retrieval Contract runs compact problem query
                          |
              +-----------+------------+
              |                        |
              v                        v
        useful records             no records
              |                        |
              v                        v
  inspect selected records       keyword fallback
  only if needed                 + adjacent fallback
              |                        |
              v                        v
       advisory note           useful? yes/no
              |                        |
              +-----------+------------+
                          |
                          v
             MacroForge-owned decision/review/task work
```

## Estimated implementation complexity

Smallest implementation: low to low-medium complexity.

Expected files if later implemented:

- One small helper script or module to classify triggers and run retrieval.
- One small documentation update explaining the gate.
- Optional test fixture for representative task descriptions and expected trigger classifications.

Likely implementation shape:

1. Add a small script, e.g. `tools/consult_metaharvest.py`, that:
   - reads `architecture/architectureharvest/relevance_map.yaml`;
   - accepts a task summary or task file path;
   - emits `task_classification_version: 1` plus structured task classification;
   - applies the Consultation Contract to return `consult` or `do_not_consult` without retrieval side effects;
   - applies the Retrieval Contract only after `consult`;
   - runs compact MetaHarvest retrieval only when triggered;
   - prints the standardized `MetaHarvest Advisory` block with mandatory Authority note.

The helper name should use `consult` rather than `gate` because MetaHarvest is informational, not an authorizing control point. The initial taxonomy should remain internal to the helper/MacroForge governance model rather than configurable user input.

2. Add tests for:
   - no retrieval for routine fixture/test/closeout task text;
   - trigger match for TASK-042-style comparability text;
   - Consultation Contract returns `consult`/`do_not_consult` without running retrieval;
   - Retrieval Contract runs only when consultation was requested;
   - fallback when primary problem query returns no records;
   - non-blocking failure when MetaHarvest path is missing;
   - advisory output includes mandatory Authority note and versioned task classification.

3. Document in MacroForge workflow docs that this is a preflight/governance classification aid, not authority.

This is not approved for implementation by this design report.

## Implementation risks

1. Trigger drift
   - Risk: consultation categories gradually expand until nearly every engineering task triggers MetaHarvest retrieval.
   - Mitigation: new trigger categories require evidence that the missing trigger previously caused architectural mistakes, duplicated work, or missed reusable knowledge; intuition or speculation is insufficient.

2. Over-triggering
   - Risk: routine source-specific work triggers consultation too often.
   - Mitigation: require structured classification plus material semantic/governance change, not mere keyword occurrence.

3. Under-triggering
   - Risk: important canonicalization or lineage design work misses consultation.
   - Mitigation: keep trigger categories explicit and review them periodically against actual missed-use evidence.

4. Context bloat
   - Risk: agents read too many MetaHarvest files.
   - Mitigation: compact retrieval first, default deeper-read cap of 3 records, absolute cap of 5 records.

5. Authority confusion
   - Risk: MetaHarvest output is treated as directive.
   - Mitigation: every advisory block states MacroForge retains authority; adoption requires MacroForge decision/task artifacts.

6. Retrieval brittleness
   - Risk: exact problem queries return no records.
   - Mitigation: required keyword and adjacent-problem fallback.

7. Framework creep
   - Risk: dbt/Dagster/OpenMetadata evidence is misread as adoption approval.
   - Mitigation: design explicitly permits pattern extraction only, no runtime/framework adoption without separate accepted MacroForge decision.

8. Contract coupling
   - Risk: consultation policy and retrieval mechanics become tangled, making future retrieval evolution change governance behavior accidentally.
   - Mitigation: keep Consultation Contract responsible only for `consult`/`do_not_consult`, and Retrieval Contract responsible only for bounded retrieval after consultation is requested.

9. Classification drift
   - Risk: the task taxonomy changes without preserving historical interpretation.
   - Mitigation: store `task_classification_version: 1` whenever classification is persisted and evolve the internal taxonomy only through reviewed governance changes, not configuration.

10. Cross-project coupling
   - Risk: MacroForge workflow becomes dependent on MetaHarvest availability.
   - Mitigation: retrieval failure is non-blocking except when consultation itself is the requested deliverable.

## Final recommendation

Implement later only after review approval.

If approved, implement the smallest version: a preflight helper named `tools/consult_metaharvest.py` that reads the existing relevance map, emits `task_classification_version: 1` plus structured task classification, applies a Consultation Contract that only returns `consult`/`do_not_consult`, applies a separate Retrieval Contract only after consultation is requested, runs compact MetaHarvest retrieval with fallback, and emits the standardized `MetaHarvest Advisory` note with mandatory Authority note. Do not add startup retrieval, task creation, automatic adoption, taxonomy configurability, or runtime/framework integration.

Trigger-gated consultation remains the next recommended integration work item because the consultation trial demonstrated enough value: low retrieval cost, useful vocabulary, external pattern evidence, and clearer governance boundaries for canonicalization, eligibility, lineage, and check-contract work.
