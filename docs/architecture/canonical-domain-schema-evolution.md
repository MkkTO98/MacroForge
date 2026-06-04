# Canonical-domain schema evolution after Eurostat

Status: design note
Date: 2026-06-04
Related evidence: TASK-020, DEC-009, `artifacts/reports/eurostat-third-source-architecture-spike-20260604.md`

## Purpose

Eurostat exposed real pressure in MacroForge's current annual-only period model and ISO3-shaped territory assumptions. The important design question is not whether those limits exist; they do. The question is how to evolve the schema without letting provider representations become canonical identities.

This note compares two paths:

1. Provider-centric schema evolution.
2. Canonical-domain schema evolution.

Recommendation: choose canonical-domain schema evolution.

MacroForge's long-term goal is to integrate many heterogeneous macroeconomic sources for investment research. That requires a stable source-agnostic observation model where provider codes are mapped into canonical domain entities, not promoted into canonical identities.

## Current pressure from Eurostat

Eurostat `namq_10_gdp` introduced source variation not covered by the original WDI-centered v0 schema:

- quarterly periods such as `2023-Q1`, while `curated.dim_period` currently keys only by `(frequency, period_year)`;
- provider geography codes such as `DE` and `FR`, while the current `curated.dim_territory` uses `iso3_code` and is scoped by `source_id`;
- potential regional aggregate codes such as `EU27_2020` or `EA20`, which are not ISO3 country identifiers;
- provider dimension dictionaries for units, adjustments, geography, period labels, and dataset-specific concepts.

The TASK-020 report correctly identified schema pressure, but its first-pass recommended wording leaned too close to provider-centric canonical dimensions by suggesting `period_code` and provider-neutral `territory_code` as canonical identity fields. The revised design should preserve canonical-domain identity and store provider codes in mapping/metadata tables.

## Option A — Provider-centric schema evolution

Provider-centric evolution treats provider representations as the natural shape of the curated dimensions.

Typical changes would include:

- `curated.dim_period(frequency, period_code)` where `period_code` stores values like `2023-Q1`, `2023M01`, `2024`, or provider-specific strings.
- `curated.dim_territory(territory_code, code_system)` where `territory_code` might hold `USA`, `DE`, `EU27_2020`, `EA20`, or any provider geography code.
- Provider labels and source-specific code dictionaries become close to canonical dimensions.
- The loader maps source payload fields into curated facts with minimal transformation.

### Advantages

- Fast to implement after a new source spike.
- Preserves provider detail without needing an upfront canonical mapping layer.
- Low immediate friction for each source loader.
- Works well for evidence slices and source-specific staging.

### Disadvantages

- Canonical identity becomes unstable because the meaning of a key depends on provider conventions.
- The same real-world country may appear under multiple identifiers: `USA`, `US`, `840`, `United States`, or source-specific codes.
- Period identity becomes string-shaped rather than time-domain-shaped, making comparisons, joins, annualization, resampling, and cross-frequency analysis harder.
- Provider revisions to aggregate definitions can appear as new canonical territories instead of versioned memberships/definitions.
- Investment research queries become provider-aware too early: analysts must remember which source code system shaped the dimension.
- Deduplication and cross-source reconciliation become harder as each provider adds more canonical-looking variants.
- It optimizes ingestion convenience over source-agnostic analytical meaning.

### Where provider-centric modeling belongs

Provider-centric modeling is still appropriate in:

- `staging.*` source-specific observation tables;
- `meta.dataset_release.metadata` for raw provider dimensions and request filters;
- provider code mapping tables;
- raw artifact manifests and lineage;
- diagnostic reports.

It should not define canonical curated dimensions unless the provider code is already the accepted canonical domain identifier.

## Option B — Canonical-domain schema evolution

Canonical-domain evolution treats curated dimensions as MacroForge's domain model. Provider representations are translated into, or linked to, canonical entities through mappings.

The curated model should answer analytical questions in stable domain terms:

- What entity is this observation about?
- What time interval does it measure?
- What concept/indicator does it represent?
- What unit and transformation qualify it?
- Which source/release/run supports it?

Provider payloads should remain reconstructable, but they should not own canonical identity.

## Period design under canonical-domain evolution

Periods should support annual, quarterly, monthly, and eventually daily frequencies through structured fields.

Recommended conceptual shape for `curated.dim_period`:

```text
curated.dim_period
- period_id
- frequency                 -- A, Q, M, D, etc.
- period_year               -- integer, required for all normal periods
- period_quarter            -- integer nullable, required for quarterly
- period_month              -- integer nullable, required for monthly
- period_date               -- date nullable, useful for daily
- period_start_date         -- date, canonical interval start
- period_end_date           -- date, canonical interval end
- period_label              -- display label, e.g. 2023 Q1
- created_at
```

Natural-key direction:

```text
frequency + period_start_date + period_end_date
```

or frequency-specific check constraints, for example:

- annual: `frequency = 'A'`, `period_year` set, quarter/month/date null;
- quarterly: `frequency = 'Q'`, `period_year` and `period_quarter` set;
- monthly: `frequency = 'M'`, `period_year` and `period_month` set;
- daily: `frequency = 'D'`, `period_date` set.

Provider period strings should live outside canonical identity, for example:

```text
meta.provider_period_mapping
- source_id
- provider_dataset_code
- provider_period_code      -- e.g. 2023-Q1, 2023M01, 2023-Q1-S1 if a source uses unusual strings
- period_id
- provider_label
- valid_from_release_key
- valid_to_release_key
- metadata jsonb
```

This lets MacroForge interpret Eurostat `2023-Q1`, OECD annual `2020`, WDI `2021`, and future daily observations as canonical time intervals while preserving the original source code for audit and reprocessing.

## Territory design under canonical-domain evolution

ISO3 should remain the canonical country identifier for countries.

The current model needs extension, not replacement. The core issue is that the v0 table conflates two concerns:

1. canonical country identity;
2. provider/source territory codes.

Recommended conceptual direction:

```text
curated.dim_territory
- territory_id
- territory_type            -- country, region, economic_area, aggregate, other
- iso3_code                 -- nullable except territory_type = country
- territory_name
- canonical_code            -- optional MacroForge-owned code for non-country territories
- created_at
```

For countries:

- `iso3_code` remains the canonical identifier.
- `territory_type = 'country'`.
- `iso3_code` should be unique for country rows independent of source.

For aggregate regions:

- `iso3_code` should be null.
- `territory_type` should describe the kind of entity, e.g. `economic_area` or `aggregate`.
- A MacroForge-owned `canonical_code` can represent stable analytical entities such as `EU27_2020` or `EA20` if MacroForge chooses to support them as first-class domains.
- Aggregate definitions may need versioned membership metadata later.

Provider geography codes should live in mapping metadata, for example:

```text
meta.provider_territory_mapping
- source_id
- provider_dataset_code
- provider_territory_code   -- e.g. DE, FR, USA, DNK, EU27_2020, EA20
- territory_id
- provider_label
- code_system               -- eurostat_geo, wdi_country_code, oecd_ref_area, etc.
- valid_from_release_key
- valid_to_release_key
- metadata jsonb
```

This preserves ISO3 semantics while allowing many provider codes to map to the same canonical country:

```text
WDI USA      -> country / USA
OECD USA     -> country / USA
Eurostat DE  -> country / DEU
Eurostat FR  -> country / FRA
```

and aggregate codes to map to non-country canonical territories only when MacroForge explicitly supports them:

```text
Eurostat EU27_2020 -> aggregate/economic_area / canonical_code EU27_2020
Eurostat EA20      -> aggregate/economic_area / canonical_code EA20
```

## Provider metadata architecture

Provider dimensions and labels remain important. They are not noise; they are provenance and mapping evidence.

But their home should be metadata/mapping, not the canonical dimensions themselves.

A future metadata design can start small:

```text
meta.provider_code_list
- provider_code_list_id
- source_id
- provider_dataset_code
- dimension_name            -- geo, time, unit, na_item, s_adj, etc.
- release_key
- metadata jsonb

meta.provider_code
- provider_code_id
- provider_code_list_id
- provider_code
- provider_label
- provider_parent_code
- metadata jsonb
```

Then specific mapping tables can link provider codes to canonical dimensions where needed:

- provider territory code -> `curated.dim_territory`;
- provider period code -> `curated.dim_period`;
- provider unit code -> `curated.dim_unit`;
- provider indicator code -> source-scoped `curated.dim_indicator` or later canonical concepts.

This keeps provider fidelity while giving MacroForge a stable analytical core.

## Comparison

| Criterion | Provider-centric evolution | Canonical-domain evolution |
| --- | --- | --- |
| Ingestion speed | Faster initially | Slightly slower because mappings are explicit |
| Source fidelity | High | High, if raw/staging/provider metadata are preserved |
| Canonical identity stability | Weak; identities drift with provider codes | Strong; identities represent domain concepts |
| Cross-source joins | Harder; analysts must understand provider code systems | Easier; provider codes map into shared entities |
| Period analytics | String-shaped periods complicate resampling/comparison | Structured intervals support annual/quarterly/monthly/daily analysis |
| Country semantics | Provider codes can blur ISO2/ISO3/aggregate distinctions | ISO3 remains country identity; aggregates are separately typed |
| Aggregate regions | Easy to store as codes, hard to reason about | Explicitly modeled as non-country territories with versioned definitions later |
| Research usability | Provider-aware and brittle | Source-agnostic and query-friendly |
| Long-term many-source integration | Accumulates semantic debt | Scales better as sources multiply |
| Best layer | staging/meta | curated/mart |

## Recommendation

MacroForge should adopt canonical-domain schema evolution.

Provider-centric representations should remain in raw artifacts, staging rows, source payloads, provider code dictionaries, and mapping tables. Curated dimensions should represent stable domain entities.

The Eurostat lesson should be reframed as:

- not "replace ISO3 with provider territory codes";
- not "make provider period strings canonical";
- instead: strengthen canonical period and territory dimensions, then add provider mapping metadata.

This better supports the long-term MacroForge goal: integrating many heterogeneous macroeconomic sources into a coherent investment research substrate.

Investment research needs stable comparisons across countries, time, units, and indicators. If every provider's vocabulary leaks into the canonical layer, later research notebooks, analyst agents, and mart tables inherit source-specific complexity. A canonical-domain layer lets ingestion remain source-specific while downstream research can ask source-agnostic questions.

## Revised design direction

Recommended next design task should decide a schema migration plan around these principles:

1. Periods:
   - extend `curated.dim_period` with structured annual/quarterly/monthly/daily fields;
   - key by canonical interval/frequency, not provider period string;
   - store provider period codes in metadata/mapping.

2. Territories:
   - preserve ISO3 as the canonical country identifier;
   - remove source scoping from canonical country identity where practical;
   - add `territory_type`;
   - support aggregate/economic-area territories separately from countries;
   - map provider geography codes to canonical territories.

3. Provider metadata:
   - add a small provider code-list/code metadata design;
   - add mapping tables only where needed for ingestion and audit;
   - keep raw provider payloads reconstructable.

4. Facts:
   - keep `curated.fact_observation` source/release/run lineage;
   - keep the fact grain centered on canonical dimensions plus unit/attributes/as-of date;
   - do not widen the fact table with provider-specific columns.

## Non-goals

This design note does not approve:

- an executable migration;
- Eurostat PostgreSQL promotion;
- a generalized ingestion framework;
- broad source onboarding;
- research/mart implementation;
- replacing source-specific staging loaders.

Those require separate accepted decisions/tasks and a fresh dry-run before implementation.
