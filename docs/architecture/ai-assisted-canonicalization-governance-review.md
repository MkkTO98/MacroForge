# AI-assisted canonicalization governance review

Status: proposed governance refinement before TASK-030
Date: 2026-06-04
Related task: TASK-030
Related decisions: D-20260602-setup-purpose, D-20260602-setup-success, DEC-003, DEC-010, DEC-011, DEC-015
Decision proposal: DEC-016

## Purpose

This review checks whether the current canonical indicator/comparability direction remains aligned with MacroForge's original objective.

MacroForge was not conceived as a conventional manually curated data warehouse. The long-term target is an AI-assisted macroeconomic knowledge system that can ingest heterogeneous public datasets, normalize them into a canonical analytical model, and scale across many providers and indicators while preserving auditability, reproducibility, evidence, lineage, and human-governed risk boundaries.

The immediate trigger is TASK-030. DEC-015 opened TASK-030 to design minimal canonical indicator and unit comparability after the first canonical GDP snapshot report. That direction is correct in identifying the semantic gap, but it needs refinement: canonical indicator strategy must not accidentally become a manual registry that requires humans to create and maintain every canonical indicator and mapping.

## Findings against the review questions

### 1. Does the current direction assume humans must define and maintain canonical indicators over time?

Partly, yes.

DEC-015 and the original TASK-030 scope do not explicitly require manual maintenance, but their language can be read as a traditional governance workflow:

- identify provider indicators;
- define a canonical concept;
- map providers to that concept;
- decide comparability status;
- later implement mappings.

For the current bounded GDP fixture, this is acceptable. For MacroForge's long-term goal, it is dangerous if left implicit. It could cause future agents to treat canonical concepts as hand-authored artifacts for each provider indicator.

The better interpretation is:

- humans define principles, thresholds, policies, review queues, and high-impact canonical model changes;
- automated canonicalization proposes mappings and canonical concept creation;
- humans audit exceptions, low-confidence cases, and high-impact changes.

### 2. Does the current direction scale to thousands or tens of thousands of provider indicators?

Not if implemented as manual canonical governance.

Manual canonical indicator creation and approval can work for a few high-value GDP/CPI/rates indicators. It does not scale to tens of thousands of indicators across WDI, OECD, Eurostat, IMF, BIS, ECB, FRED, UN, and future sources.

At scale, provider indicators carry useful metadata:

- provider code;
- name/title;
- long description;
- dataset/code-list context;
- dimensions;
- units;
- frequency;
- adjustment flags;
- methodology notes;
- links/documentation;
- source hierarchy;
- observed value behavior.

MacroForge should treat those as evidence for an automated canonicalization process, not as a backlog of manual mapping tickets.

### 3. Would the proposed model create a growing manual governance burden?

Yes, if TASK-030 stays focused only on canonical concepts and unit comparability without designing the automation/audit layer around them.

The burden would grow along several axes:

- new provider indicators;
- provider metadata updates;
- revised descriptions or code-list labels;
- duplicated concepts across providers;
- multiple units for one concept;
- ambiguous names;
- frequency/seasonal-adjustment variants;
- methodology differences;
- stale mappings when better logic becomes available.

Without an explicit automated mapping-proposal and review mechanism, every source expansion would add governance debt.

### 4. Can canonicalization instead be an auditable AI-assisted process?

Yes. This is the better long-term model for MacroForge.

MacroForge should treat canonicalization as a reproducible, evidence-backed pipeline:

```text
Provider Indicator Evidence
-> Automated Canonicalization Layer
-> Mapping or Canonical-Creation Proposal
-> Confidence / Reasoning / Evidence / Version
-> Human Review Queue for exceptions
-> Accepted Canonical Indicator Mapping
-> Curated Facts
```

The AI-assisted layer should not be opaque. It should store every proposal and decision with:

- provider source code;
- provider dataset code;
- provider indicator code;
- provider title/name;
- provider description;
- provider dimensions and code-list context;
- provider unit metadata;
- canonical target candidate;
- canonical target version;
- proposed mapping status;
- confidence score;
- reasoning summary;
- evidence references;
- model/ruleset version;
- timestamp;
- reviewer state if reviewed;
- supersession lineage for re-canonicalization.

This preserves the ProjectForge/MacroForge preference for readable, auditable, file/database-backed state while allowing scale.

### 5. What minimum architecture is required?

Minimum architecture is not a broad ingestion framework or a full ontology. It is a small canonicalization governance surface around provider metadata and mapping proposals.

Required conceptual components:

1. Provider indicator evidence store

   Stores normalized metadata about provider indicators independent of whether they are loaded as facts.

   Required evidence:

   - source/provider identity;
   - dataset/collection identity;
   - provider indicator code;
   - provider indicator title/name;
   - provider description/methodology text when available;
   - dimensions and code-list context;
   - observed frequency/territory/unit hints;
   - documentation/source URL references;
   - raw evidence artifact/checksum references.

2. Canonicalization run

   A reproducible run record for the mapping process.

   Required fields:

   - run id;
   - timestamp;
   - mapping method type, for example rules, embedding, LLM, hybrid;
   - model/ruleset/prompt version;
   - input evidence version/checksums;
   - thresholds;
   - operator/agent identity if applicable.

3. Canonical indicator concept

   A source-agnostic analytical concept, not a provider code.

   Minimal fields:

   - stable canonical concept id/code;
   - concept label;
   - concept definition;
   - domain/category;
   - measure type, for example flow/stock/index/rate/count;
   - default comparability caveats;
   - lifecycle status, for example proposed/active/deprecated/superseded;
   - version or valid interval.

4. Mapping proposal

   An auditable proposed relationship between provider indicator evidence and a canonical concept.

   Required fields:

   - provider indicator reference;
   - proposed canonical concept reference;
   - relationship type, for example exact, close, broader, narrower, related, not comparable;
   - confidence score;
   - confidence band, for example auto-accept candidate, review required, reject/no match;
   - reasoning/evidence summary;
   - evidence references;
   - proposed unit/comparability treatment;
   - created by run id;
   - timestamp;
   - status.

5. Canonical creation proposal

   When no existing concept fits, the system proposes a new canonical concept instead of forcing a bad match.

   Required fields:

   - proposed canonical code/label;
   - definition;
   - supporting provider indicators;
   - evidence;
   - confidence;
   - duplication-risk notes;
   - status.

6. Human review queue

   Governance focuses on exceptions:

   - low confidence;
   - conflicting proposals;
   - high-impact indicators;
   - new canonical concept proposals;
   - mappings that would change existing curated facts;
   - re-canonicalization proposals.

7. Accepted mapping state

   Curated facts should depend only on accepted mapping state or explicitly labelled provisional mapping state. They should not depend on opaque one-off model output.

8. Re-canonicalization support

   Mapping logic will improve. MacroForge needs versioned mapping decisions and the ability to rerun canonicalization without losing historical decisions.

   Required support:

   - previous mapping id/version;
   - superseded-by pointer;
   - reason for change;
   - affected facts/report scope;
   - reproducibility of old and new mapping decisions.

## Traditional warehouse governance model

### Shape

```text
Human analyst/steward
-> manually defines canonical indicator
-> manually maps provider indicators
-> manually reviews unit/comparability
-> curated facts use accepted mapping
```

### Strengths

- High precision for a small number of critical indicators.
- Easy to explain.
- Good fit for financial-grade curated universes where the indicator set is intentionally small.
- Low automation risk.
- Clear accountability.

### Weaknesses

- Does not scale to thousands/tens of thousands of indicators.
- Creates a growing backlog for every source expansion.
- Makes source onboarding dependent on manual semantic work.
- Encourages ad hoc decisions hidden in task files if governance pressure rises.
- Slow to adapt when provider metadata changes.
- Expensive to re-canonicalize when logic improves.
- Conflicts with MacroForge's AI-first long-term direction.

### Appropriate use in MacroForge

Traditional governance should remain for:

- defining policy;
- high-impact macro concepts;
- thresholds and auto-accept rules;
- exception review;
- audit of sampled auto-accepted mappings;
- final acceptance of schema/model changes.

It should not be the default path for every provider indicator.

## AI-assisted canonicalization model

### Shape

```text
Provider Indicator
-> Provider Metadata/Evidence Extraction
-> Automated Canonicalization Layer
-> Mapping Proposal or Canonical-Creation Proposal
-> Confidence / Reasoning / Evidence / Version
-> Human Review for exceptions
-> Accepted Mapping State
-> Canonical Indicator
-> Curated Facts
```

### Strengths

- Scales to large heterogeneous source catalogs.
- Preserves provider metadata and evidence for audit.
- Allows automatic mapping proposals with human governance concentrated where it matters.
- Supports confidence thresholds and risk-based review.
- Makes re-canonicalization possible when better models/rules become available.
- Aligns with AI-first local-execution/cloud-governance: local deterministic processing where possible, cloud/premium governance only for high-leverage review.
- Avoids turning source expansion into a manual taxonomy project.

### Weaknesses

- Requires careful audit design to avoid opaque model behavior.
- Confidence scores can be misleading if not calibrated.
- LLM/embedding methods may produce plausible but wrong mappings.
- Provider descriptions can be vague or inconsistent.
- Duplicate canonical concept creation is a real risk.
- Automated changes can silently affect downstream research unless versioned and gated.
- Requires governance around thresholds, review queues, and re-canonicalization.

### Appropriate use in MacroForge

This should become the default direction for indicator canonicalization, but only after designing a minimal auditable model. The immediate TASK-030 should not implement automation. It should define the minimal architecture and governance constraints needed before implementation.

## Tradeoffs

| Dimension | Traditional manual governance | AI-assisted auditable canonicalization |
| --- | --- | --- |
| Small-scope precision | Strong | Strong if reviewed; variable if fully automated |
| Scale | Poor | Strong |
| Auditability | Strong if documented | Strong only if evidence/reasoning/versioning are first-class |
| Speed of source onboarding | Slow | Faster |
| Human workload | Grows linearly or worse | Focused on exceptions and audits |
| Risk | Human bottleneck/staleness | Automation error/overconfidence |
| Re-canonicalization | Hard/manual | Designed-in if versioned |
| Fit with MacroForge long-term goals | Limited | Strong |

## Risks and mitigations

### Risk: automation creates wrong canonical mappings

Mitigation:

- confidence thresholds;
- relationship types beyond exact match;
- review-required states;
- high-impact indicator rules;
- sample audits of auto-accepted mappings;
- preserve provider evidence and reasoning.

### Risk: confidence scores become false authority

Mitigation:

- treat confidence as routing metadata, not truth;
- store method/model version;
- calibrate thresholds against reviewed examples;
- require evidence citations/reasoning.

### Risk: duplicate canonical indicators proliferate

Mitigation:

- canonical creation proposals must search existing concepts;
- store duplication-risk notes;
- require review for new canonical concept creation above a materiality threshold;
- support merge/supersession lineage.

### Risk: re-canonicalization breaks reproducibility

Mitigation:

- version mappings;
- never overwrite accepted mapping history silently;
- record supersession and affected facts/reports;
- allow old reports to reference mapping versions used at generation time.

### Risk: full automation outruns governance

Mitigation:

- no direct opaque model output into curated facts;
- mapping proposals first;
- accepted mapping state is the gate;
- human review for low-confidence, conflicting, high-impact, or new-concept cases.

## Recommendation

The AI-assisted canonicalization model better aligns with MacroForge's long-term goals.

TASK-030 should not continue unchanged. It should be modified.

The modified TASK-030 should design a minimal auditable automated canonicalization layer, not merely a manual canonical indicator/unit comparability registry.

The modified scope should still include GDP comparability because GDP is the immediate evidence case, but GDP should be used as the seed example for the canonicalization process:

```text
Provider indicator evidence
-> automated mapping / canonical creation proposal
-> confidence + reasoning + provenance
-> human review only if needed
-> accepted canonical indicator mapping
```

## Decision proposal

Accept the following refinement:

1. DEC-015 remains valid only as the identification of the semantic gap.
2. TASK-030 is modified, not replaced.
3. TASK-030 should design the minimal AI-assisted canonicalization architecture required to support:
   - automatic canonical indicator mapping;
   - automatic canonical indicator creation proposals;
   - mapping confidence;
   - mapping provenance;
   - evidence storage;
   - human review queues for exceptions;
   - re-canonicalization and supersession.
4. TASK-030 should explicitly reject a model where every new provider indicator requires manual canonical indicator creation or manual approval.
5. TASK-030 should not implement migrations, schema changes, source ingestion, report generation, or model calls.

## Expected modified TASK-030 output

TASK-030 should produce a design note and decision artifact for a minimal canonicalization layer with at least these conceptual entities:

- provider indicator evidence;
- canonicalization run;
- canonical indicator concept;
- mapping proposal;
- canonical creation proposal;
- accepted mapping state;
- review status/queue;
- supersession/re-canonicalization lineage.

It should define which parts are required now and which remain deferred.

It should also define policy questions such as:

- confidence thresholds for auto-accept candidates vs review required;
- which indicators are high-impact and always reviewed;
- when provider facts may enter curated facts under provisional mappings;
- how generated reports cite mapping versions;
- how future improved logic can reprocess mappings without rewriting history.

## Answer to the required decision question

TASK-030 should be modified.

It should not continue unchanged because unchanged wording risks drifting toward manual canonical indicator governance.

It should not be replaced because the semantic gap it identified is still the right next problem. The change is scope orientation: from manual canonical comparability design to AI-assisted, auditable canonicalization design.
