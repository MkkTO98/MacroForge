# DEC-015 — Next scope after first canonical GDP snapshot: minimal indicator and unit comparability

Status: accepted
Date: 2026-06-04
Related task: TASK-029
Preceded by: TASK-028
Follow-on task: TASK-030
Governing context: DEC-010, DEC-011, DEC-013, DEC-014

## Decision

MacroForge will next do focused governance/design for minimal canonical indicator and unit comparability before adding more research reports, new sources, broad schema changes, mart layers, or ingestion framework extraction.

The follow-on task is:

- TASK-030 — Design minimal canonical indicator and unit comparability.

TASK-030 should produce a bounded design note and decision proposal for how MacroForge should represent enough source-agnostic analytical meaning to say when provider observations are comparable.

The design should focus on the smallest useful case exposed by TASK-028:

- OECD `B1GQ` annual GDP rows;
- Eurostat `B1GQ` quarterly GDP rows;
- WDI `NY.GDP.MKTP.CD` annual GDP rows;
- observed units `CP_MEUR`, `USD_EXC`, `USD_PPP`, and WDI's current `unknown` unit representation;
- explicit annual/quarterly non-aggregation boundaries.

## Why this option now

TASK-028 succeeded as the first research-facing canonical report:

- core report queries used `curated.*` plus `meta.*` only;
- no staging-table dependency was required for core content;
- the report produced deterministic JSON and Markdown artifacts;
- the report covered 3 sources, 5 territories, annual and quarterly frequencies, and 16 GDP snapshot observations;
- bounded expected GDP observations: 16;
- missing GDP observations: 0;
- duplicate fact grains: 0;
- failing quality checks: 0.

This proves basic canonical analytical usability. The canonical substrate can support a small report without source-specific leakage.

But the report also exposed the next real analytical boundary: MacroForge can list GDP-ish observations, but it cannot yet express whether they share a canonical economic concept, unit semantics, price basis, currency basis, seasonal-adjustment basis, or aggregation policy.

A second report would likely repeat caveats instead of improving analytical correctness. A new source would increase breadth before the existing GDP substrate can state comparability. Framework extraction is still premature because the current need is domain semantics, not loader abstraction.

Therefore the smallest useful next step is a design/governance task for minimal indicator and unit comparability.

## Accepted TASK-030 scope

TASK-030 may create:

- a fresh governance/design dry-run;
- a design note under `docs/architecture/`, for example `minimal-canonical-indicator-unit-comparability.md`;
- a decision artifact accepting or rejecting the proposed model;
- one follow-on implementation task if the design is accepted;
- updates to state, backlog, roadmap, summaries, and handoff.

The design should answer:

1. What is the minimal canonical indicator concept needed for GDP snapshot reporting?
2. Should provider indicators map to canonical concepts through `meta` mapping tables, curated dimensions, or report-local metadata?
3. What unit attributes are required to avoid false comparability?
4. How should MacroForge represent currency basis, price basis, scale/multiplier, PPP/exchange-rate basis, and unknown unit quality?
5. How should annual and quarterly observations be kept explicit without implying aggregation?
6. What is required now versus deferred?
7. What exact implementation task, if any, should follow?

## Recommended design posture

The expected posture is source-agnostic and minimal:

- canonical economic concept identity should not be provider-specific;
- provider indicator codes should map to canonical concepts rather than become canonical concepts;
- unit semantics should be explicit enough to block invalid comparisons;
- no conversion or aggregation should be implemented merely because metadata exists;
- report consumers should be able to distinguish comparable groups from descriptive-only rows.

TASK-030 should prefer a design that can be implemented incrementally and tested with the existing bounded fixtures.

## Rejected alternatives

### Do not add a second research report next

A second report is deferred because TASK-028 already proved report generation. The next blocker is not report mechanics; it is whether GDP observations across providers and units can be grouped or compared with honest semantics.

### Do not add a new source next

New source onboarding is deferred. More sources would increase provider diversity before MacroForge has a minimal way to represent cross-provider indicator/unit comparability.

### Do not extract an ingestion framework next

Framework extraction remains premature. TASK-028 did not reveal source-ingestion abstraction pressure; it revealed domain-semantic pressure.

### Do not implement schema changes inside TASK-029 or TASK-030 without design acceptance

TASK-029 is governance-only. TASK-030 should be design/governance first. Any migration or code implementation should be a separate follow-on task after the design is accepted.

## Explicit non-goals

DEC-015 does not approve:

- new source onboarding;
- FRED onboarding;
- live source fetches;
- live/default `macro` writes;
- PostgreSQL migrations;
- report code implementation;
- unit conversion engine;
- quarterly-to-annual aggregation;
- mart schema implementation;
- dashboard/UI/notebook work;
- generalized source/plugin/JSON-stat/SDMX ingestion framework;
- provider-specific fact columns;
- git push.

## Reconsideration triggers

Reopen governance if TASK-030 finds that:

- current `curated.dim_indicator` can support only provider indicators and cannot be extended without breaking existing evidence;
- unit semantics require a larger measurement-model design before any small implementation is safe;
- WDI's current unit handling blocks honest GDP comparability even descriptively;
- source-provider metadata is insufficient to map OECD/Eurostat/WDI GDP concepts safely;
- comparability requires conversion or aggregation policies that exceed the current bounded design scope.

## Evidence reviewed

Context bundle:

- `context/active_context.md`
- `context/context_audit.md`
- `context/context_audit.json`

The compact governance context exceeded the default budget, so TASK-029 used justified `project_wide_review` mode under the context policy:

- context mode: `project_wide_review`;
- estimated tokens: 22441;
- budget tokens: 64000;
- within budget: true;
- raw logs excluded: true;
- summaries used: true.

Implementation/report evidence:

- `artifacts/reports/canonical-gdp-snapshot-20260604.json`;
- `artifacts/reports/canonical-gdp-snapshot-20260604.md`;
- TASK-028 outcome and handoff;
- DEC-014;
- DEC-010/DEC-011 deferred canonical indicator ontology and unit conversion framework until real pressure appeared.

TASK-028 showed the pressure is now concrete but should still be handled as bounded design before implementation.

## Consequences

MacroForge remains disciplined:

- analytical reporting is proven at the canonical/meta layer;
- next work improves semantic correctness before multiplying reports or sources;
- source-specific loaders and raw-SQL/PostgreSQL/psql architecture remain unchanged;
- implementation waits for a focused accepted design rather than being mixed into governance.

No implementation was performed under TASK-029.
No git push was performed.
