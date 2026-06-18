# Canonicalization Deferred Mapping Advancement Requirements

Date: 2026-06-18
Task: TASK-039
Source: TASK-038 lifecycle validation
Status: complete

## Purpose

Persist what must be true before the TASK-038 deferred OECD and Eurostat GDP mappings can advance. This prevents future agents from re-opening the full lifecycle artifact and guessing which evidence is missing.

## Boundaries

- Existing TASK-038 evidence only.
- No code, tests, schemas, migrations, live fetches, model calls, conversion, aggregation, report integration, base accepted-state mutation, or canonical asset manifest mutation.
- This artifact records requirements; it does not advance any mapping.

## Deferred mappings

### OECD_NAAG `B1GQ` -> `MACRO_GDP_OUTPUT`

Current outcome: `deferred` / `deferred_pending_unit_basis_policy`

Rationale: OECD B1GQ has GDP-like evidence, but the bounded evidence carries multiple unit/comparability profiles, USD_EXC and USD_PPP. The lifecycle must preserve separate basis caveats rather than approve a single comparable GDP mapping without policy.

Semantic blocker: `unit_basis_ambiguity`

Missing evidence or policy:
- Explicit selection or separation policy for exchange-rate USD versus PPP USD comparability profiles.
- Evidence-backed rule for whether OECD B1GQ should map to one canonical GDP concept, separate basis-specific canonical concepts, or remain excluded from comparable GDP outputs.
- Review decision documenting how USD_EXC and USD_PPP profiles affect downstream report eligibility.

Minimum advancement condition:

- A review-approved unit-basis policy must distinguish USD_EXC from USD_PPP, choose the applicable mapping/report treatment, and preserve basis caveats in accepted/provisional state before the mapping can advance.

Caveats that must remain preserved:
- Exchange-rate USD and PPP USD are separate comparability profiles.
- PPP-basis USD and exchange-rate USD are separate comparability profiles.
- No conversion or basis-selection policy is applied.
- Report integration is deferred.

Replay/evidence pointers:
- `artifacts/reports/canonicalization-review-lifecycle-20260614.json` sha256 `34b2b8882677478b92904fb64e5bed559f49970f008725fef49346ef63509f16`
- `artifacts/reports/canonicalization-review-lifecycle-20260614.md`
- `artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md`

Forbidden shortcuts:
- Do not treat provider code B1GQ alone as proof of canonical comparability.
- Do not resolve blocker by confidence score alone.
- Do not perform unit/currency conversion or frequency aggregation without accepted policy and tests.
- Do not integrate into GDP reports before report-impact policy is explicit.
- Do not auto-apply accepted mapping changes from proposal artifacts.

### EUROSTAT_NAMQ_GDP `B1GQ` -> `MACRO_GDP_OUTPUT`

Current outcome: `deferred` / `deferred_pending_frequency_currency_policy`

Rationale: Eurostat B1GQ has GDP-like evidence, but quarterly current-price million EUR values cannot be treated as comparable to annual/current-USD evidence without explicit conversion and aggregation policy, which TASK-038 rejects.

Semantic blocker: `frequency_currency_scale_policy_missing`

Missing evidence or policy:
- Explicit currency conversion policy for current-price million EUR relative to current-USD or PPP-USD evidence.
- Explicit quarterly-to-annual aggregation policy or a separate quarterly canonical/report treatment.
- Scale/price-basis handling evidence proving million-EUR current-price values are not silently compared to annual USD values.

Minimum advancement condition:

- A review-approved frequency/currency/scale policy must state whether conversion and aggregation are allowed, how they are performed and audited, or why Eurostat remains separate/deferred.

Caveats that must remain preserved:
- Current-price million euro values are not directly comparable to USD_EXC, USD_PPP, or WDI current-USD metadata without conversion policy.
- Quarterly frequency must not be aggregated to annual in this lifecycle validation.
- No currency/unit conversion is performed.
- Report integration is deferred.

Replay/evidence pointers:
- `artifacts/reports/canonicalization-review-lifecycle-20260614.json` sha256 `34b2b8882677478b92904fb64e5bed559f49970f008725fef49346ef63509f16`
- `artifacts/reports/canonicalization-review-lifecycle-20260614.md`
- `artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md`

Forbidden shortcuts:
- Do not treat provider code B1GQ alone as proof of canonical comparability.
- Do not resolve blocker by confidence score alone.
- Do not perform unit/currency conversion or frequency aggregation without accepted policy and tests.
- Do not integrate into GDP reports before report-impact policy is explicit.
- Do not auto-apply accepted mapping changes from proposal artifacts.

## WDI reference

WDI `NY.GDP.MKTP.CD` reached governed provisional status in TASK-038. It is not accepted truth and is not an advancement target in this artifact.

## How to use this artifact

Before any future task proposes advancing OECD or Eurostat GDP mapping status, inspect this artifact first. A valid future task should either satisfy the listed minimum advancement condition with evidence, or explicitly keep the mapping deferred.
