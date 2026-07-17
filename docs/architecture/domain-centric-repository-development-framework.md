# Domain-Centric Repository Development Framework

Status: accepted planning and governance framework
Date: 2026-07-08
Related decision: `artifacts/decisions/D-20260708-domain-centric-repository-development-framework.md`
Related investigation: `artifacts/reports/R-20260708-domain-centric-repository-development-framework.md`
Related framework: `docs/architecture/confidence-escalation-framework.md`
Refinement: TASK-168 accepts `docs/architecture/analytical-capability-planning-framework.md` as the planning layer between macroeconomic domain and confidence cell.

## Purpose

The Domain-Centric Repository Development Framework (DRDF) governs what MacroForge should expand next during Operational Repository Evolution.

DRDF answers:

```text
Which analytically meaningful macroeconomic domain should MacroForge develop now, and what domain gaps matter most?
```

CEF answers the different question:

```text
What is the largest ingestion scope inside the selected target that can now be executed with acceptable evidence-backed confidence?
```

Therefore DRDF and CEF are complementary:

```text
DRDF selects and governs the domain objective.
CEF sizes and constrains the ingestion campaign that advances it.
Existing source-specific workstreams execute the implementation.
```

DRDF is a planning/governance framework only. It is not runtime infrastructure, a source registry, a provider framework, a semantic ontology, a data catalog, a scoring engine, a production-ingestion system, a KnowledgeForge substitute, or authorization for broad ingestion.

## Accepted planning-unit hierarchy

TASK-168 refines the original DRDF hierarchy by inserting analytical capability between macroeconomic domain and confidence-cell scope. MacroForge should use the following hierarchy during repository-development planning:

```text
Strategic objective
  -> Macroeconomic domain
      -> Analytical capability
          -> Capability maturity / completeness gap
              -> Confidence cell
                  -> CEF-sized campaign / slice
                      -> Source-specific implementation task
```

The macroeconomic domain remains the portfolio-level planning unit because it connects MacroForge's constitutional purpose to coherent economic territory. The analytical capability is the operational planning unit inside that domain because it describes what downstream systems can actually do. Provider, dataset family, confidence cell, and campaign remain valid subordinate units, but they are not sufficient as the top-level repository-development objective.

### Why domain is the primary planning unit

A domain is the most useful planning abstraction because it:

- corresponds to how macroeconomic analysis asks questions;
- preserves repository coherence better than opportunistic provider breadth;
- allows analytical-completeness judgments without requiring exhaustive collection;
- makes downstream consumption by KnowledgeForge, InsightForge, BriefForge, and future EIP workflows more direct;
- still leaves implementation authority with CEF and source-specific workstreams;
- avoids treating data count, provider count, or indicator count as value by themselves.

### Why other units are subordinate

- Provider: useful for acquisition confidence, but provider-first planning drifts toward mirrors and can produce shallow unrelated coverage.
- Dataset family: useful for source-specific implementation, but may not cover the conceptual relationships needed for analysis.
- Confidence cell: necessary for CEF scope sizing, but confidence alone does not decide which economic domain matters next.
- Campaign: useful execution bundle, but a campaign is a means, not the durable repository objective.
- Capability: analytical capabilities now govern workflow-level repository usefulness inside domains; durable platform capabilities still govern infrastructure maturity. Analytical capability is subordinate to domain portfolio selection and above CEF confidence cells.

## Canonical domain model

DRDF adopts a lightweight canonical domain model. This model is for planning, coverage assessment, and maturity tracking only. It does not create canonical semantic identities, domain ontologies, runtime routing, schemas, source frameworks, KnowledgeForge concepts, or implementation backlogs.

The model is derived from three evidence sources:

1. MacroForge constitutional purpose and implemented evidence.
2. Authoritative macro-statistical organization patterns such as the System of National Accounts, IMF dissemination/data-category structure, and World Bank WDI topical categories.
3. Existing MacroForge coverage artifacts: `docs/architecture/domain-coverage-assessment.md`, `docs/capability-atlas.md`, and `docs/architecture/long-term-domain-vision.md`.

### Primary analytical domains

1. National Accounts and Real Activity
   - GDP, GNI, output, expenditure components, income, saving, consumption, investment, industrial production, capacity, inventories, productivity, business-cycle activity.

2. Prices, Inflation, and Costs
   - Consumer prices, producer prices, inflation rates, price levels, cost indexes, wage-cost/productivity links, commodity-price context where used for inflation analysis.

3. Labour, Employment, Wages, and Household Income
   - Employment, unemployment, participation, labor force, payrolls, vacancies, turnover, wages, hours, income, household financial stress where analytically tied to labor/households.

4. Demographics, Human Capital, and Population Structure
   - Population, age structure, fertility, mortality, migration, education, health-capacity indicators, dependency burden, urbanization.

5. Government Finance and Public Debt
   - Revenue, expenditure, deficit/surplus, debt stocks, interest costs, fiscal operations, sovereign debt burden, public-sector balance-sheet context.

6. Monetary, Banking, Credit, and Financial Intermediation
   - Monetary aggregates, policy rates where monetary-policy variables, banking credit, deposits, financial access, payment infrastructure, household and sector credit, financial soundness where source-backed.

7. Financial Markets, Asset Prices, and Market Reference Data
   - Yield curves, interest-rate curves, FX quotes, market capitalization, equity-market structure, market prices used as macro-financial reference observations.

8. External Sector and Cross-Border Finance
   - Balance of payments, current/capital/financial accounts, IIP, reserves, external debt, remittances, FDI/portfolio/cross-border banking flows and positions.

9. International Trade, Tourism, and Supply Chains
   - Goods/services trade, bilateral reporter-partner flows, product classifications, trade direction, tourism receipts/arrivals, logistics/supply-chain performance when tied to external flows.

10. Industry, Production Structure, Agriculture, and Input-Output
    - Sector value added, production, industry/product classifications, supply-use/input-output matrices, agriculture and food production where used as production-domain evidence.

11. Energy, Commodities, Environment, and Climate Exposure
    - Energy balances, energy use, electricity mix, commodities, environmental exposure, climate/resource indicators where they affect macro production, inflation, external vulnerability, or transition analysis.

12. Housing, Real Estate, and Construction
    - Housing construction pipeline, permits/starts/completions, housing prices, residential investment proxies, affordability/rent evidence where source-backed.

13. Firms, Issuers, Business Formation, and Market Structure
    - Company/issuer financial-statement facts, filings, business formation, listings, regulated institution certification, branch networks, market-structure facts. This domain remains constrained by Companies/canonical identity freeze and may develop only through explicitly bounded source-backed observations until identity research authorizes broader work.

### Cross-domain support domains

These are not primary macroeconomic domains but are necessary to make domain evidence analytically usable:

- Classification and reference evidence: geography, sector, product, industry, instrument, unit, frequency, country grouping, classification-version membership.
- Release, revision, vintage, and publication-event evidence: point-in-time observations, release calendars, revision histories, projection/vintage evidence.
- Validation and lineage evidence: source evidence, checksums, observed packages, load reports, quality checks, replay, and provenance.

Cross-domain support should be developed only when it directly improves one or more primary domains or reduces recurring implementation uncertainty. It must not become a generic catalog or ontology project.

## Domain maturity methodology

DRDF rejects one aggregate maturity score. Domain maturity is multidimensional because different dimensions answer different questions and should not be collapsed without evidence.

Track each domain using these dimensions:

1. Conceptual core coverage
   - Does MacroForge represent the domain's core concepts, not merely peripheral indicators?

2. Analytical relationship coverage
   - Does MacroForge represent enough related variables to support meaningful analysis inside the domain?

3. Geographic coverage
   - Are the relevant countries/regions/territories represented for the intended analytical use?

4. Historical and frequency coverage
   - Is the time span and frequency adequate for the intended analysis?

5. Provider/source coverage
   - Is there enough source diversity or authoritative-provider support for confidence and comparison?

6. Representation maturity
   - Do existing observation structures preserve the domain's grain, roles, units, dimensions, and metadata without distortion?

7. Operational maturity
   - Can the domain evidence be refreshed, replayed, loaded, and validated deterministically where scoped?

8. Validation maturity
   - Are checks strong enough to detect wrong ingestion, missing evidence, duplicate grains, mapping drift, and source/provider anomalies?

9. Canonical/loading maturity
   - Is the domain loaded into the accepted canonical/storage path where required, and are mapping statuses explicit?

10. Downstream readiness
    - Can KnowledgeForge, InsightForge, BriefForge, or future EIP workflows consume the domain without redoing basic data collection, provenance tracing, or coverage reasoning?

Use labels such as Initial, Developing, Operationally Useful, Analytically Complete for Current Scope, and Frozen/Blocked. These labels must be accompanied by dimensional evidence and gap notes.

## Analytical completeness framework

An analytically complete domain is not an exhaustive domain. It is a domain whose current MacroForge evidence is sufficient to support the intended class of downstream analysis without forcing every downstream workflow to reconstruct basic context, provenance, and core relationships.

A domain is analytically complete for a stated scope when MacroForge has:

1. Core concept set
   - The minimum variables that define the domain's main analytical questions.

2. Relationship set
   - Enough related variables to answer first-order relationships, such as flow/stock, price/quantity, supply/demand, domestic/external, public/private, nominal/real, level/rate, or sector/counterparty relationships where relevant.

3. Context set
   - Geographic, temporal, unit, frequency, classification, provider, and source metadata needed to interpret observations.

4. Validation set
   - Deterministic checks proving source evidence, row counts, uniqueness/grain, quality status, fingerprints, lineage, replay/load behavior where scoped, and known caveats.

5. Boundary set
   - Explicit non-goals and known missing concepts so downstream consumers know what not to infer.

6. Diminishing-return threshold
   - Additional data would mostly add breadth, detail, or convenience rather than change the domain's ability to support the intended analysis.

Analytical completeness must always name its scope. Examples:

- `Operationally useful for WDI annual country-panel descriptive macro context, 2000-2023`.
- `Analytically complete for narrow USA labor-core monthly national monitoring, 2015-M01 through 2024-M12`.
- `Not analytically complete for cross-provider GDP comparability because conversion/frequency policy remains unresolved`.

Completeness does not authorize investment conclusions, causal claims, KnowledgeForge semantic identities, generic source frameworks, or production/live ingestion.

## Domain roadmaps

Roadmaps are strategic planning guides, not implementation backlogs. CEF must still select the concrete scope before any ingestion task begins.

### 1. National Accounts and Real Activity

Current maturity: Operationally useful for bounded GDP/macro-indicator paths; Established across real-activity slices.

Implemented providers/evidence: WDI, OECD, Eurostat, BEA/FRED-style national-account and real-activity slices, industrial production, retail, PCE, income/saving, productivity, corporate profits, inventories/orders.

Major gaps: GDP-component comparability, nominal/real/current-price policies, frequency conversion/aggregation policy, broader national-account table coverage, cross-source canonical comparability.

Logical expansion sequence: stabilize core GDP/component comparability evidence; add source-native BEA/OECD/Eurostat component tables where bounded; then expand productivity/real-activity relationships.

Downstream usefulness: highest for macro context, country comparisons, business-cycle explanation, BriefForge macro briefs, and KnowledgeForge claim grounding.

### 2. Prices, Inflation, and Costs

Current maturity: Established evidence, not analytically complete.

Implemented providers/evidence: BLS CPI, FRED producer-price/commodity-price style slices, WDI inflation, WEO projection inflation evidence.

Major gaps: country breadth beyond current operational macro panel, CPI/PPI component detail, core/headline distinctions, price-level/index-base comparability, inflation expectations, wage-cost relationship integration.

Logical expansion sequence: define inflation core concept set; use CEF to select high-confidence CPI/PPI/provider-family expansion; then add component and expectation evidence only if needed.

Downstream usefulness: inflation regime analysis, macro briefs, policy-rate interpretation, real-income/real-rate context.

### 3. Labour, Employment, Wages, and Household Income

Current maturity: Operationally Useful for USA labor-core monitoring; Mature representation evidence; not globally complete.

Implemented providers/evidence: ILOSTAT, FRED state unemployment, BLS CES/CPS/JOLTS/wages/hours, LAUS state labor-force evidence, BLS labor-core operational dataset.

Major gaps: country breadth, demographic breakdowns, occupation/industry structure, full JOLTS turnover set, cross-provider employment comparison, labor productivity/income integration.

Logical expansion sequence: expand high-confidence BLS labor core if USA focus; add ILO/OECD cross-country labor core if cross-country focus; add JOLTS/wages/hours detail after core employment/participation coverage.

Downstream usefulness: employment-cycle analysis, wage-pressure context, household-sector narratives, policy briefs.

### 4. Demographics, Human Capital, and Population Structure

Current maturity: Operationally useful for WDI annual country demographic foundation after WDI Phase 1/TASK-165, but not complete for cohort/migration analysis.

Implemented providers/evidence: WDI demographics, dependency ratios, education, health, migration/remittances, urbanization-related indicators.

Major gaps: age/sex cohorts, migration flows and stocks, mortality detail, educational attainment, health outcomes, UN Population Division comparison, population projections.

Logical expansion sequence: treat WDI broad annual demographics as base; add UN Population Division or equivalent authoritative demographic source; then add cohort/projection evidence if downstream workflows need demographic decomposition.

Downstream usefulness: denominators, dependency and labor-supply context, country comparison, structural macro background for KnowledgeForge.

### 5. Government Finance and Public Debt

Current maturity: Established bounded evidence; not operationally complete.

Implemented providers/evidence: U.S. Treasury Fiscal Data, FRED federal receipts/outlays, FRED debt/interest, IMF GDD sector debt, WDI fiscal-adjacent indicators where present.

Major gaps: cross-country government finance, deficit/surplus, revenue/spending category detail, maturity/currency structure, debt-service and debt-sustainability context, IMF GFS evidence.

Logical expansion sequence: add bounded IMF GFS or cross-country fiscal core if available; integrate debt stock/flow/interest burden relationships; defer fiscal-framework extraction until recurring mapping pain appears.

Downstream usefulness: sovereign risk, fiscal impulse context, public debt narratives, macro-financial vulnerability analysis.

### 6. Monetary, Banking, Credit, and Financial Intermediation

Current maturity: Established/Developing, with several operational refresh slices.

Implemented providers/evidence: IMF MFS interest rates, BIS policy rates, FRED monetary aggregates, WDI broad money/domestic credit, IMF FAS payment cards, IMF GDD sector debt, bank credit and household finance slices.

Major gaps: banking-system balance sheets, deposits/loans by sector, credit conditions, financial soundness indicators, cross-country monetary aggregates, frequency harmonization.

Logical expansion sequence: strengthen core monetary/credit panels; add financial-soundness/banking-system evidence if source path is clear; preserve source-specific interpretation and avoid monetary/banking ontology extraction.

Downstream usefulness: credit-cycle analysis, policy transmission, financial-stability briefs, external vulnerability context.

### 7. Financial Markets, Asset Prices, and Market Reference Data

Current maturity: Established for bounded reference observations; not complete for daily/market microstructure.

Implemented providers/evidence: ECB SDW, IMF MFS, BIS policy rates, FRED yield curve, FRED FX, WDI market capitalization/listed companies.

Major gaps: daily frequency, full yield curves, equity/index prices, credit spreads, market calendars, instrument metadata, curve construction policy.

Logical expansion sequence: maintain monthly/annual reference-data posture unless a downstream blocker requires daily data; if needed, run CEF Stage 1/2 daily-frequency tests before broader market expansion.

Downstream usefulness: monetary-policy context, financial-condition narratives, FX/rate regime analysis.

### 8. External Sector and Cross-Border Finance

Current maturity: Developing and strategically important.

Implemented providers/evidence: IMF BOP financial-account flows, IMF IIP positions, IMF IRFCL reserves, WDI remittances, external-sector WDI indicators, G7 BOP/IIP operational panels.

Major gaps: current account and capital account, full BOP component coverage, external debt, reserves adequacy, CPIS/CDIS, counterparty/instrument/sector detail, quarterly/monthly coverage.

Logical expansion sequence: deepen BOP/IIP core relationship set: current account + financial account + IIP + reserves + external debt; add CPIS/CDIS/BIS counterparty evidence later.

Downstream usefulness: balance-of-payments diagnostics, external vulnerability, capital-flow narratives, country-risk briefs.

### 9. International Trade, Tourism, and Supply Chains

Current maturity: Developing.

Implemented providers/evidence: WDI trade core, WDI services-trade intensity, UN Comtrade USA-Japan operational dataset, IMF IMTS bounded bilateral trade, WDI tourism/logistics/high-tech export indicators.

Major gaps: product-level HS coverage, broader bilateral partner network, mirror reconciliation, quantities/weights, services categories, customs/re-export semantics, product classifications.

Logical expansion sequence: decide whether the active objective is macro trade openness or product/partner trade structure; for structure, expand UN Comtrade product/partner evidence with CEF; for macro openness, strengthen WDI/IMF aggregate trade coverage.

Downstream usefulness: external-demand analysis, supply-chain exposure, trade war/tariff context, country-sector narratives.

### 10. Industry, Production Structure, Agriculture, and Input-Output

Current maturity: Initial/Established depending on subarea; input-output remains initial bounded matrix evidence.

Implemented providers/evidence: Eurostat input-output matrix, industrial production/capacity, manufacturers' orders, agriculture/food WDI, high-tech exports, business inventories, productivity.

Major gaps: industry classifications, supply-use tables, sector value-added/employment/investment links, product/industry hierarchy, multi-country input-output, agriculture detail.

Logical expansion sequence: add a second matrix/cube or supply-use evidence only if production-structure analysis becomes active; otherwise deepen scalar industry/production indicators first.

Downstream usefulness: sector decomposition, production-chain analysis, productivity narratives, supply shock context.

### 11. Energy, Commodities, Environment, and Climate Exposure

Current maturity: Established for selected energy/commodity/environment scalar observations; not analytically complete.

Implemented providers/evidence: Eurostat energy balance, WDI energy phase, FRED crude oil, WDI environment/climate exposure, electricity-mix and energy-use indicators.

Major gaps: full energy balances, production/consumption/trade/inventory relationships, renewable/fuel detail, emissions, commodity breadth, energy-price/fiscal/external-sector links.

Logical expansion sequence: define whether active domain goal is energy macro vulnerability, inflation commodity context, or climate/environment exposure; then select source family accordingly.

Downstream usefulness: inflation/shock analysis, external vulnerability, transition-risk context, energy-security briefs.

### 12. Housing, Real Estate, and Construction

Current maturity: Developing.

Implemented providers/evidence: Census housing pipeline, FRED housing construction core, FRED housing prices.

Major gaps: regional detail, rents, affordability, mortgage rates/credit, existing-home sales, inventories, construction costs, longer official Census stage history.

Logical expansion sequence: complete construction pipeline + price + financing/affordability relationship set before adding fine regional detail.

Downstream usefulness: rate-sensitive sector analysis, household balance-sheet context, construction-cycle narratives.

### 13. Firms, Issuers, Business Formation, and Market Structure

Current maturity: Developing for bounded SEC/source-backed observations; Frozen for canonical identity/general company infrastructure.

Implemented providers/evidence: SEC company facts, AAPL/MSFT statement panel, filing events, 13F stock positions, exchange listings, FDIC bank certifications/branches, business applications.

Major gaps: issuer identity authority, broad company coverage, security master, XBRL framework, restatement/revision behavior, ownership graph, firm registry.

Logical expansion sequence: do not broaden into company/entity infrastructure until MetaHarvest canonical identity research and explicit future review authorize it. Bounded source-backed observations may continue only if they do not require canonical identity claims.

Downstream usefulness: eventually high for investment workflows, but currently boundary-constrained.

## Integration with CEF

TASK-168 refines the DRDF/CEF integration sequence:

```text
Select or continue active macroeconomic domain
        -> Specify the target analytical capability
        -> Assess capability maturity and analytical-completeness gaps
        -> Identify required capability dependencies and blockers
        -> Translate the capability gap into one or more candidate confidence cells
        -> CEF selects the largest safe next scope within the chosen cell
        -> Execute with existing source-specific workstreams
        -> Update CEF confidence, capability maturity, and domain maturity evidence
        -> Decide whether to continue, hold, or transition domain/capability focus
```

Important constraints:

- DRDF must not override CEF confidence constraints.
- CEF must not choose broad repository expansion that lacks a domain and analytical-capability objective.
- ACPF must not become runtime infrastructure, a semantic ontology, or a provider/source framework.
- Existing architecture remains authoritative over all planning frameworks.
- Implementation remains source-specific unless extraction gates are independently satisfied.
- Domain and capability maturity updates must be evidence-based and lightweight.

## Transition methodology between domains

MacroForge should move from an active domain to another domain when one or more evidence-backed transition criteria hold:

1. Analytical completeness for the current stated scope is achieved.
2. The remaining gaps require blocked authority, such as canonical identity, conversion policy, high-impact semantic review, paid access, production/live authority, or a provider/source not yet justified.
3. CEF evidence says safe next scope inside the domain is too small or too uncertain relative to another domain's higher-confidence/high-value gap.
4. Additional data in the domain would mainly add breadth/detail without improving downstream analytical readiness.
5. Downstream EIP workflows can already consume the domain for the intended use and would benefit more from another domain becoming similarly coherent.
6. A cross-domain dependency blocks further usefulness, e.g. external-sector analysis requires government debt or FX context.

Avoid arbitrary completion percentages. A domain transition must name the scope that is complete, blocked, or diminishing-return.

## Downstream validation

Domain-centric planning improves downstream EIP usefulness because mature domains can be consumed as coherent evidence packages rather than as unrelated provider artifacts.

KnowledgeForge can consume mature domains by referencing validated observation families, provenance, caveats, and explicit gaps when forming concepts, claims, hypotheses, and confidence assessments.

InsightForge or future analytical workflows can consume mature domains as ready analytical substrates with known coverage, validation, and boundaries rather than rebuilding source inventories.

BriefForge can use mature domains to create brief-ready evidence packs: current state, history, geography/country scope, source lineage, validation status, caveats, and missing evidence.

A shallow breadth-first expansion across unrelated areas creates more data but forces downstream systems to rediscover whether variables belong together, whether enough context exists, and which gaps invalidate analysis. DRDF makes those judgments first-class MacroForge artifacts.

## Governance rules

1. DRDF is accepted as planning/governance policy, not implementation infrastructure.
2. Future repository-expansion planning should identify the target domain and maturity gap before CEF scopes the campaign.
3. `docs/architecture/domain-coverage-assessment.md` remains the lightweight factual map; update only affected sections after implementations.
4. Domain maturity should remain dimensional; do not create a single score unless repeated planning work proves a deterministic scoring method reduces effort without hiding uncertainty.
5. Analytical completeness claims must be scope-qualified and evidence-backed.
6. Domain roadmaps are strategic guides, not implementation backlogs.
7. DRDF does not authorize ingestion, provider mirrors, exhaustive collection, generic frameworks, KnowledgeForge semantics, company identity work, production ingestion, or schema changes.
