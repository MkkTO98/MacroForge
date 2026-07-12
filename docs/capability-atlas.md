# MacroForge Capability Atlas

Status: factual inventory of implemented capability
Created: 2026-07-02
Evidence boundary: completed implementation artifacts through TASK-129

This atlas answers one question: what can MacroForge already represent?

It records implemented capability only. It does not replace Domain Coverage, Architectural Confidence, Long-Term Domain Vision, task artifacts, implementation lessons, or source-specific tests. It excludes future plans, desired capabilities, unimplemented observation families, architecture proposals, governance changes, and methodology discussion.

Maturity labels:

- Initial: represented by one or a small number of bounded implementations.
- Established: represented by multiple completed implementations or by a well-tested source family across related concepts.
- Mature: represented by canonical-loaded paths or many completed bounded implementations across related concepts.

Maintenance rule: update this atlas only when a completed implementation materially expands MacroForge's implemented capability. Do not update it for routine extensions of an already mature capability.

## Capability inventory

### 1. Canonical GDP and macro-indicator ingestion

- Representative implementations: WDI (`TASK-005` through `TASK-009`), OECD SDMX (`TASK-011` through `TASK-015`), Eurostat NAMQ GDP (`TASK-020` through `TASK-024`), combined-source canonical smoke (`TASK-026`), canonical GDP snapshot (`TASK-028`).
- Observational structure represented: provider macroeconomic indicator observations promoted through staging/curated/canonical paths, with territory, period, indicator, unit, source/provider identity, and canonical GDP reporting support.
- Current maturity: Mature.
- Important limitations: mature only for the implemented narrow GDP/source paths; does not imply broad canonical loading for later bounded evidence-only slices.

### 2. Observed ingestion packages and deterministic replay

- Representative implementations: `TASK-046`, `TASK-048`, `TASK-050`, `TASK-052`, source-slice tests from `TASK-051` through `TASK-101`.
- Observational structure represented: source-specific evidence normalized into `ObservedIngestionPackage` objects with raw evidence, input filters, observations, attributes, deterministic fingerprints, comparison, contract validation, lineage, and ingestion feedback.
- Current maturity: Mature.
- Important limitations: represents observed evidence packages; it is not by itself canonical semantic mapping, investment interpretation, or broad provider abstraction.

### 3. Consumer and producer price observations

- Representative implementations: `TASK-051` BLS CPI, `TASK-080` FRED producer prices.
- Observational structure represented: scalar price-index time-series observations with provider indicator, period, territory/source context, unit/index basis, and source-specific price concept metadata.
- Current maturity: Established.
- Important limitations: does not include a general inflation framework, pass-through model, price-index ontology, or broad price-source coverage.

### 4. National accounts, output, consumption, income, and saving

- Representative implementations: `TASK-053` BEA NIPA, `TASK-076` industrial production/capacity utilization, `TASK-077` retail sales, `TASK-078` personal consumption expenditures, `TASK-079` personal income/saving, `TASK-087` manufacturers' orders, `TASK-092` productivity/unit labor cost, `TASK-093` corporate profits.
- Observational structure represented: scalar time-series observations for production, utilization, demand, consumption, personal income, saving, order flow, productivity, labor-cost, and aggregate profit concepts.
- Current maturity: Established.
- Important limitations: no general national-accounts ontology, GDP-component mapping, demand framework, business-cycle model, sector ontology, or canonical loading beyond earlier narrow canonical GDP paths.

### 5. Fiscal flows, public debt, and government finance

- Representative implementations: `TASK-054` Treasury Fiscal Data, `TASK-094` federal fiscal receipts/outlays, `TASK-095` federal debt and federal interest cost, `TASK-201` WDI public-sector fiscal/governance expansion.
- Observational structure represented: government fiscal scalar observations for flows, debt stock, interest cost, public finance/tax/debt measures, governance-quality indicators, institutional-risk/stability measures, and related WDI public-sector annual country-period evidence with source-specific fiscal role/government-sector/unit metadata.
- Current maturity: Operationally Useful inside the WDI annual-scalar public-sector fiscal/governance confidence cell; established for bounded U.S. federal fiscal flows/debt/interest evidence.
- Important limitations: full government-finance-statistics accounts and deficit/debt decomposition, subnational public finance, institutional/governance methodology and uncertainty handling, high-frequency budget execution, cross-provider reconciliation, and canonical public-sector fiscal/governance taxonomy remain bounded; no broad fiscal framework, deficit accounting framework, government-finance ontology, fiscal impulse model, debt-sustainability model, or general Treasury/FRED fiscal client.

### 6. Labor-market level, rate, demand, wage, and hour observations

- Representative implementations: `TASK-059` ILOSTAT unemployment, `TASK-070` FRED state unemployment, `TASK-071` BLS payroll employment, `TASK-084` BLS JOLTS labor demand/turnover, `TASK-089` BLS CES wages/hours, `TASK-128` BLS LAUS state labor force, `TASK-141` BLS labor-core operational dataset, `TASK-193` WDI/ILO global labor closure expansion, `TASK-207` BLS monthly labor proof campaign, `TASK-208` BLS U.S. labor breadth monthly campaign.
- Observational structure represented: labor scalar observations across unemployment rates, labor-force participation, civilian employment levels, civilian labor-force levels, nonparticipation, part-time-for-economic-reasons underemployment, unemployment duration, subnational labor rates and labor-force levels, payroll employment levels, industry payroll employment, openings/hiring/turnover-style measures, industry job openings, wages, hours, global annual unemployment/youth-unemployment by sex, labor-force stocks, employment-population ratios, vulnerable/self/wage employment, NEET shares, prime-age and education-specific participation, and broad-sector employment shares.
- Current maturity: Mature for bounded U.S. monthly labor-core monitoring; broader BLS monthly U.S. labor breadth is operationally useful after TASK-208; substantially complete inside WDI/ILO annual country-level labor status/utilization/structure scope; broader labor domain remains Developing.
- Important limitations: no labor-market ontology, detailed occupation hierarchy, seasonal-adjustment framework beyond preserving provider SA metadata, global vacancy/turnover coverage, wage-distribution framework, broad wage/hour depth beyond selected CES sectors, cross-provider reconciliation, or canonical labor mapping beyond source-specific implemented paths.

### 7. Demographic foundation observations

- Representative implementations: `TASK-061` WDI demographics, `TASK-126` WDI dependency ratios.
- Observational structure represented: country-period demographic scalar observations such as population-style indicators, age structure, fertility/life-expectancy, urbanization, and dependency-burden ratios with WDI source metadata.
- Current maturity: Developing.
- Important limitations: limited to bounded implemented demographic slices; no demographic framework, cohort model, fertility/migration system, dependency-ratio model, projection system, or canonical demographic mapping.

### 8. Trade observations

- Representative implementations: `TASK-060` UN Comtrade bilateral total goods trade, `TASK-067` IMF IMTS bilateral trade, `TASK-099` WDI services trade intensity, `TASK-142` WDI trade core operational dataset, `TASK-170` WDI trade-balance capability package, `TASK-172` UN Comtrade product-level trade exposure slice.
- Observational/capability structure represented: country-period exports/imports of goods and services in current USD and percent of GDP; deterministic WDI package-layer net trade balance, balance direction/status, percent-of-GDP context, coverage/missingness, provenance, and caveats; bounded country-partner-period trade-flow observations with bilateral direction/flow/classification/source metadata; bounded product-level HS trade exposure rows preserving product code/description, reporter, partner, flow, value, and source caveats.
- Current maturity: Developing overall; annual WDI country-level goods-and-services trade-balance monitoring is Operationally Useful for current bounded scope; bounded bilateral product-level goods trade exposure monitoring is Supported for the narrow TASK-172 USA-Japan 2023 three-code scope.
- Important limitations: broad operational WDI trade-balance monitoring exists only as source-backed package/report evidence; bilateral partner/product-level coverage remains bounded; no product-level taxonomy, partner hierarchy, mirror reconciliation, trade infrastructure, customs-regime model, broad trade canonicalization, canonical product identity, or canonical derived trade-balance fact insertion.

### 9. Services trade intensity observations

- Representative implementations: `TASK-099` WDI services trade intensity, now partially subsumed by `TASK-142` WDI trade core operational coverage.
- Observational structure represented: country-period services-trade/trade-openness percent-of-GDP scalar observations.
- Current maturity: Developing as part of the broader Trade repository section.
- Important limitations: not a full services-trade framework; does not represent services categories, partner flows, BPM components, or canonical external-sector mapping.

### 10. Financial-account, monetary-depth, and market-structure observations

- Representative implementations: `TASK-063` IMF BOP financial account, `TASK-088` IMF IIP positions, `TASK-143` WDI financial accounts core operational dataset, `TASK-148` IMF IIP G7 operational dataset, `TASK-189` WDI external vulnerability and financial openness expansion, `TASK-192` WDI/GFDD financial-system depth/access/stability expansion, `TASK-199` WDI external debt expansion.
- Observational structure represented: annual country-period-side-category financial-account flow observations, operational G7 external position stocks, financial-account flow refresh artifacts, broad WDI macro-financial/external-vulnerability country-year observations, broad GFDD financial-system country-year observations for inclusion/access, institutional depth, market depth, bank efficiency, bank stability, ownership/concentration, market structure, remittance, and nonresident-bank exposure signals, and WDI annual-scalar external-debt stocks/flows/debt-service/vulnerability observations.
- Current maturity: Operationally Useful inside WDI/GFDD annual-scalar external-vulnerability, financial-system, and external-debt confidence cells; Developing beyond WDI/GFDD for detailed instrument/counterparty, quarterly, supervisory, relationship, security-level, contract-term, and cross-provider evidence.
- Important limitations: detailed flow/position categories, instrument/counterparty structure, quarterly frequency, bank-level supervisory data, security-level issuance/ownership/maturity data, debt contract terms, and cross-provider financial-account/banking/market-structure/debt coverage remain bounded; no general BOP/IIP/financial-accounts/debt framework, counterparty mapping, instrument hierarchy, market-structure ontology, or canonical external-account loading.

### 11. International investment-position stock observations

- Representative implementations: `TASK-088` IMF IIP positions, `TASK-135` IMF IIP G7 position panel, `TASK-148` IMF IIP G7 operational dataset.
- Observational structure represented: annual external asset, liability, and net position stock observations with position-side and stock-basis metadata, now operationalized for G7 countries across 2015-2023.
- Current maturity: Developing.
- Important limitations: no currency composition, counterparty breakdown, instrument maturity, valuation framework, or general IIP ontology.

### 12. Matrix observations

- Representative implementations: `TASK-062` Eurostat input-output matrix.
- Observational structure represented: matrix-cell observations for input-output style row/column roles and period/geography context.
- Current maturity: Initial.
- Important limitations: no generalized matrix engine, input-output ontology, industry taxonomy, or canonical matrix loading.

### 13. Energy balance, energy intensity, electricity mix, and commodity price observations

- Representative implementations: `TASK-064` Eurostat energy balance, `TASK-069` FRED crude oil prices, `TASK-096` WDI energy use / coal-electricity, `TASK-191` WDI energy transition/access expansion.
- Observational structure represented: source-specific scalar energy/electricity observations and commodity-price observations with energy concept, balance item, electricity-mix, access, clean-cooking, renewable-energy, electricity-loss, energy-intensity/productivity, net-import-dependence, or commodity metadata.
- Current maturity: Operationally Useful inside the WDI annual-scalar energy-transition/access cell; Established overall; Developing beyond WDI for detailed energy-system/balance evidence.
- Important limitations: no general energy framework, climate-transition model, commodity ontology, detailed electricity-system model, electricity-price/capacity/reliability coverage, cross-provider energy-system validation, or energy-balance canonicalization.

### 14. Market rates, curves, monetary policy, and foreign exchange

- Representative implementations: `TASK-055` ECB SDW, `TASK-056` IMF MFS interest rate, `TASK-057` BIS central-bank policy rates, `TASK-065` FRED yield curve, `TASK-074` FRED foreign exchange rates, `TASK-213` BIS WS_CBPOL broad monthly policy-rate campaign.
- Observational structure represented: scalar or curve-point market/monetary observations with period, tenor/maturity or rate role, instrument/rate concept, currency/quote context, and provider metadata; after TASK-213 this includes broad cross-country monthly central-bank policy-rate facts for 37 accepted territories from 2015-M01 through 2026-M06 with one canonical source-scoped policy-rate indicator, BIS series-key, source, compilation, observation-status, unit, and territory evidence preserved.
- Current maturity: Operationally Useful for BIS WS_CBPOL monthly policy-rate monitoring; Established across broader market-rates/FX evidence.
- Important limitations: no broad market-data framework, curve engine, currency ontology, trading-calendar support, daily-frequency contract expansion, monetary-policy model, or broad BIS financial-condition substrate beyond the coherent WS_CBPOL policy-rate family.

### 15. Monetary aggregates, bank credit, household finance, credit quality, and household balance sheets

- Representative implementations: `TASK-072` monetary aggregates, `TASK-073` household debt-service burden, `TASK-081` household credit-quality/delinquency, `TASK-086` bank credit, `TASK-122` household balance-sheet stocks, `TASK-214` BIS cross-country debt-service ratios by borrower sector, `TASK-215` BIS cross-country credit-to-GDP gaps.
- Observational structure represented: scalar monetary stock, household credit burden, delinquency-rate, commercial-bank loan-stock, household/nonprofit balance-sheet stock, quarterly BIS country-sector debt-service-ratio observations, and quarterly BIS country credit-to-GDP-gap observations with source-specific borrower-sector/lender-sector/measure, unit, frequency, provider-series-key, observation-status, and snapshot/as-of metadata.
- Current maturity: Operationally Useful for cross-country BIS debt-service-ratio and credit-gap monitoring; Established for earlier bounded monetary/household-finance evidence.
- Important limitations: no broad household-finance framework, sector-balance-sheet framework, wealth model, leverage analytics, consumer-credit ontology, banking-risk model, lender registry, loan hierarchy, monetary framework, or general credit-cycle analytics. TASK-215 adds a narrow BIS-specific helper substrate for repeated BIS evidence-handling invariants but not a universal SDMX adapter, general provider framework, or multidimensional credit ontology.

### 16. Housing construction and housing-price observations

- Representative implementations: `TASK-066` Census housing construction, `TASK-090` FRED housing prices, `TASK-145` FRED housing construction core operational dataset, `TASK-147` Census housing pipeline operational evolution slice.
- Observational structure represented: housing construction workbook evidence, scalar residential housing price observations, an operational U.S. monthly building-permit panel, and an official Census construction-pipeline stage panel with deterministic normalization, replay, PostgreSQL loading, and refresh verification.
- Current maturity: Developing.
- Important limitations: no broad housing framework, no long Census stage history, no regional housing detail, no rent/affordability coverage, no housing-market ontology, no price-distribution framework, and no generic FRED/Census loader.

### 17. Subnational observations

- Representative implementations: `TASK-070` FRED state unemployment, `TASK-128` BLS LAUS state labor force.
- Observational structure represented: subnational territory-period scalar observations including unemployment rates and BLS-native labor-force levels.
- Current maturity: Developing.
- Important limitations: limited to bounded state labor evidence; no geography registry, subnational hierarchy, spatial model, LAUS framework, labor-market ontology, or canonical regional mapping.

### 18. Revision-aware vintage observations

- Representative implementations: `TASK-058` ALFRED GDP vintage.
- Observational structure represented: revision/vintage-aware scalar macro observations retaining vintage/realtime evidence.
- Current maturity: Initial.
- Important limitations: no generalized revision infrastructure, release-calendar model, vintage comparison analytics, or canonical real-time database.

### 19. Company and issuer financial-statement observations

- Representative implementations: `TASK-068` SEC Company Facts, `TASK-120` SEC company cash-flow statement, `TASK-121` SEC company balance-sheet capital structure, `TASK-125` SEC company income statement, `TASK-138` SEC AAPL/MSFT financial-statement panel, `TASK-144` SEC company core operational dataset.
- Observational structure represented: issuer/company fact observations from SEC/XBRL-style company facts, cash-flow statement facts, balance-sheet capital-structure facts, income-statement profitability/revenue facts, and an operational AAPL/MSFT FY2025 company-statement panel with deterministic normalization, replay, PostgreSQL loading, and refresh verification.
- Current maturity: Developing.
- Important limitations: issuer coverage remains narrow; quarterly/revision/restatement behavior remains bounded; no broad SEC/XBRL framework, issuer registry, security master, financial-statement ontology, equity-market framework, or final canonical company identity model.

### 20. Survey expectations, confidence, and performance-index observations

- Representative implementations: `TASK-075` consumer sentiment/expectations, `TASK-091` business confidence, `TASK-097` logistics performance index.
- Observational structure represented: scalar survey/index observations for household sentiment/expectations, business confidence, and logistics/supply-chain performance dimensions.
- Current maturity: Established.
- Important limitations: no survey framework, expectations ontology, confidence-index ontology, PMI framework, nowcasting logic, supply-chain framework, or logistics ontology.

### 21. Business inventories, orders, production pressure, and profitability observations

- Representative implementations: `TASK-076` industrial production/capacity, `TASK-085` business inventories, `TASK-087` manufacturers' orders, `TASK-092` productivity/unit labor cost, `TASK-093` corporate profits.
- Observational structure represented: scalar business-cycle-related observations for production, utilization, stock-vs-ratio inventory concepts, orders, productivity/cost efficiency, and profits.
- Current maturity: Established.
- Important limitations: no business-cycle model, inventory framework, order-book framework, margin framework, or investment signal.

### 22. Digital-connectivity, infrastructure, and basic-services observations

- Representative implementations: `TASK-098` WDI fixed broadband, `TASK-203` WDI infrastructure/connectivity expansion.
- Observational structure represented: annual country-period WDI infrastructure scalar observations for telecommunications, ICT investment, transport/logistics infrastructure, water infrastructure access, and infrastructure-service measures, including WDI request metadata and source indicator/country evidence.
- Current maturity: Operationally Useful inside the WDI annual-scalar infrastructure confidence cell after TASK-203 loaded 212,660 canonical facts across 28 compatible indicators, 217 countries, and 1990-2024.
- Important limitations: physical network asset registries and geospatial topology, subnational infrastructure access and reliability, infrastructure prices/capacity/outages/service quality, project-level infrastructure investment/PPP evidence, high-frequency transport/electricity/telecom utilization, cross-provider reconciliation, and canonical infrastructure taxonomy remain bounded; no digital-infrastructure framework, technology adoption model, telecom provider ontology, or canonical infrastructure mapping.

### 23. Logistics and supply-chain performance observations

- Representative implementations: `TASK-097` WDI Logistics Performance Index, `TASK-203` WDI infrastructure/connectivity expansion.
- Observational structure represented: country-survey-year logistics performance score observations across overall, infrastructure, and logistics-service dimensions, plus annual country-period WDI infrastructure/connectivity scalars where supported.
- Current maturity: Operationally Useful inside the WDI annual-scalar infrastructure confidence cell; supply-chain relationship/role architecture remains unscaled.
- Important limitations: no logistics framework, supply-chain model, infrastructure-quality ontology, transport-network representation, relationship/role model, or canonical supply-chain mapping.

### 24. Sector debt and balance-sheet burden observations

- Representative implementations: `TASK-101` IMF Global Debt Database sector debt.
- Observational structure represented: annual country-sector debt-instruments-as-percent-of-GDP observations for general government, private sector, nonfinancial corporations, and households.
- Current maturity: Initial.
- Important limitations: no debt-sustainability framework, balance-sheet ontology, maturity/currency/instrument decomposition, counterparty exposure, debt-service burden integration, or canonical sector mapping.

### 25. Reserve-assets and foreign-currency-liquidity observations

- Representative implementations: `TASK-102` IMF IRFCL reserve assets.
- Observational structure represented: monthly country-period reserve/liquidity scalar observations for official reserve assets and other foreign-currency assets, including IMF sector, methodology, scale, currency, and source metadata.
- Current maturity: Initial.
- Important limitations: no reserve-adequacy framework, liquidity-buffer model, external-vulnerability signal, currency-composition ontology, counterparty exposure, or canonical reserve mapping.

### 26. Payment-card access observations

- Representative implementations: `TASK-103` IMF FAS payment cards.
- Observational structure represented: annual territory-period financial-access scalar observations for credit-card and debit-card counts, including IMF FAS transformation, scale, provider metadata, and observed/empty series counts for the bounded query.
- Current maturity: Initial.
- Important limitations: no financial-inclusion score, payment-system model, retail-payments ontology, card-usage volume, account ownership, demographics, or canonical access mapping.

### 27. Education and human-capital observations

- Representative implementations: `TASK-104` WDI education human-capital, `TASK-190` WDI human capital foundations expansion, `TASK-194` WDI/Barro-Lee education attainment closure expansion.
- Observational structure represented: annual country-period education and human-capital scalar observations for primary/secondary/tertiary enrollment, teacher resources, education progression/completion/out-of-school indicators, gender parity, HCI-style expected/learning-adjusted years and overall index signals, and Barro-Lee educational-attainment distribution/schooling-stock context for 15+, 20-24, and 25+ age groups by sex/total where supported.
- Current maturity: Operationally Useful inside WDI annual-scalar scope; substantially complete inside the WDI/Barro-Lee educational-attainment confidence cell; Developing beyond WDI.
- Important limitations: no education framework, human-capital model, school-system ontology, learning-outcome source depth outside HCI-style indicators, subnational evidence, labor-quality model, or canonical education mapping.

### 27a. Gender equality and sex-disaggregated development observations

- Representative implementations: `TASK-204` WDI gender equality expansion.
- Observational structure represented: annual country-period WDI gender and sex-disaggregated development scalar observations for education, literacy, health, labor, demographic structure, legal rights, and social-development measures where supported, including WDI request metadata and source indicator/country evidence.
- Current maturity: Operationally Useful inside the WDI annual-scalar gender confidence cell after audit-corrected TASK-204 loaded 1,410,500 canonical facts across 186 compatible indicators, 217 countries, and 1990-2024.
- Important limitations: household/survey microdata and respondent-level sex/gender variables, subnational gender-disaggregated evidence, time-use/unpaid-work/care-burden evidence, violence/safety and legal-rights methodology/revision evidence, sex-disaggregated labor-market wages/hours/occupation depth, cross-provider reconciliation, and canonical gender equality taxonomy remain bounded.

### 28. Health-system resource observations

- Representative implementations: `TASK-105` WDI health-system resources, `TASK-190` WDI human capital foundations expansion, `TASK-196` WDI health/population-health expansion.
- Observational structure represented: annual country-period health-resource/outcome/access scalar observations for health expenditure, private/out-of-pocket spending, mortality, tuberculosis/malaria/HIV burden, immunization, sanitation/water/hygiene access, selected medical workforce measures, population-health outcomes, service access constraints, reproductive/maternal/child health, communicable-disease signals, risk factors, and age/sex health-context indicators, including WDI request metadata and source indicator/country evidence.
- Status after latest implementation: Operationally Useful inside the WDI annual-scalar health/population-health confidence cell after TASK-196 loaded 910,063 canonical facts across 120 compatible indicators, 217 countries, and 1990-2024.
- Important limitations: no health-system framework, healthcare ontology, deep medical-capacity model, subnational health-demographics breakdown, clinical/administrative depth, high-frequency surveillance, cross-provider validation, fiscal-health model, or canonical health mapping.

### 29. Environment and climate-exposure observations

- Representative implementations: `TASK-106` WDI environment-climate exposure, `TASK-197` WDI environment/climate expansion.
- Observational structure represented: annual country-period environmental scalar observations for PM2.5, forest/land/natural-capital, emissions and greenhouse-gas indicators where available, water/sanitation infrastructure, environmental exposure, and climate-relevant macro context, including WDI request metadata and source indicator/country evidence.
- Current maturity: Operationally Useful inside the WDI annual-scalar environment/climate confidence cell after TASK-197 loaded 843,045 canonical facts across 111 compatible indicators, 217 countries, and 1990-2024.
- Important limitations: no physical climate hazard model, disaster exposure evidence, geospatial/subnational environmental mapping, high-frequency pollution/weather/hydrology, satellite/gridded datasets, detailed sectoral emissions inventories, cross-provider validation, or canonical environmental ontology.

### 30. Distributional welfare observations

- Representative implementations: `TASK-107` WDI poverty and inequality, `TASK-200` WDI poverty and inequality expansion.
- Observational structure represented: annual country-period distributional welfare scalar observations for poverty headcount/gap/severity, Gini inequality, income distribution, shared prosperity, and related WDI poverty/welfare measures, including WDI request metadata and source indicator/country evidence.
- Current maturity: Operationally Useful inside the WDI annual-scalar poverty/distributional-welfare confidence cell after TASK-200 loaded 136,710 canonical facts across 18 compatible indicators, 217 countries, and 1990-2024.
- Important limitations: household/survey microdata and survey-version metadata, subnational poverty and inequality coverage, consumption/income welfare aggregate harmonization, nowcast/high-frequency poverty signals, cross-provider reconciliation, and canonical distributional taxonomy remain bounded; no general poverty framework, inequality framework, welfare model, household-distribution ontology, poverty-line registry, PPP framework, social-risk score, or canonical welfare mapping.

### 30a. Social protection, labor-market protection, and household-transfer observations

- Representative implementations: `TASK-206` WDI Social Protection and Labor aggregate all-program expansion.
- Observational structure represented: annual country-period WDI scalar observations for aggregate All Social Protection and Labor program coverage, adequacy, and benefit incidence/distribution where provider-supported, including WDI request metadata and source indicator/country evidence.
- Current maturity: Supported but sparse inside the WDI annual-scalar aggregate all-program social-protection confidence cell after corrected TASK-206 loaded 30,380 facts across 4 compatible indicators for 217 non-aggregate WDI countries/entities over 1990:2024.
- Important limitations: broad Social Protection & Labor domain closure is not claimed; corrected TASK-206 withdrew the original provider-empty interpretation. Most aggregate ASPIRE all-program WDI candidates have accepted non-aggregate rows but include non-annual survey-period labels outside the mature WDI annual-scalar confidence cell. Detailed program-type families, survey/microdata evidence, revision/methodology metadata, non-annual/survey-period modeling, subnational evidence, targeting rules, fiscal program accounts, cross-provider reconciliation, and canonical social-protection taxonomy remain bounded or deferred.

### 31. Innovation and knowledge-production observations

- Representative implementations: `TASK-108` WDI innovation and R&D.
- Observational structure represented: annual country-period innovation scalar observations for R&D expenditure as percent of GDP and resident patent applications, including WDI request metadata and source indicator/country evidence.
- Current maturity: Initial.
- Important limitations: no innovation framework, R&D accounting model, patent ontology, intangible-capital framework, technology-adoption model, productivity-causality claim, or canonical innovation mapping.

### 32. Migration and remittance observations

- Representative implementations: `TASK-109` WDI migration and remittances.
- Observational structure represented: annual country-period migration/remittance scalar observations for net migration and personal remittances received as percent of GDP, including WDI request metadata and source indicator/country evidence.
- Current maturity: Initial.
- Important limitations: no migration framework, remittance framework, diaspora model, population-flow ontology, external-household-transfer model, canonical migration mapping, or KnowledgeForge semantics.

### 33. Agriculture and food-production observations

- Representative implementations: `TASK-110` WDI agriculture and food; `TASK-205` WDI agriculture, food systems, land use, and rural development expansion.
- Observational structure represented: annual country-period agriculture/food scalar observations for food production, agriculture value added, fertilizer consumption, agricultural/arable/cereal/cropland land use, cereal yield/production, rural population growth, and related rural-development measures, including WDI request metadata and source indicator/country evidence.
- Current maturity: Operationally Useful inside the WDI annual-scalar agriculture/rural-development confidence cell after TASK-205 loaded 98,735 facts across 13 compatible indicators for 217 non-aggregate WDI countries/entities over 1990:2024.
- Important limitations: no agriculture framework, food-security model, commodity model, land-use ontology, crop model, sector-accounting framework, FAO/OECD/national-source reconciliation, canonical agriculture mapping, or KnowledgeForge semantics.

### 34. Tourism and travel-flow observations

- Representative implementations: `TASK-111` WDI tourism/travel flows.
- Observational structure represented: annual country-period tourism/travel scalar observations for international tourism arrivals and international tourism receipts in current US dollars, including WDI request metadata and source indicator/country evidence.
- Current maturity: Initial.
- Important limitations: no tourism framework, travel-demand model, services-export model, mobility ontology, pandemic/reopening model, travel-sector-risk model, canonical tourism mapping, or KnowledgeForge semantics.

### 35. High-technology export observations

- Representative implementations: `TASK-112` WDI high-technology exports.
- Observational structure represented: annual country-period scalar observations for high-technology exports in current US dollars and as percent of manufactured exports, including WDI request metadata and source indicator/country evidence.
- Current maturity: Initial.
- Important limitations: no high-technology export framework, industrial-policy model, trade-competitiveness model, technology-classification ontology, innovation-commercialization model, canonical trade mapping, or KnowledgeForge semantics.

### 36. Projection observations

- Representative implementations: `TASK-113` IMF WEO projections.
- Observational structure represented: annual country-period official projection observations for future real GDP growth and inflation, including projection horizon and WEO source/vintage metadata as source-specific attributes.
- Current maturity: Initial.
- Important limitations: no forecasting framework, WEO framework, broad IMF client, scenario model, projection-vintage system, nowcasting, canonical forecast table, investment conclusion, or KnowledgeForge semantics.

### 37. Filing-event observations

- Representative implementations: `TASK-114` SEC filing events.
- Observational structure represented: dated company filing-event observations for SEC 10-K and 10-Q filings, preserving CIK, form, accession number, filing date, report date, primary document, and issuer metadata.
- Current maturity: Initial.
- Important limitations: no SEC client, EDGAR crawler, filing parser, XBRL framework, event framework, issuer registry, ownership graph, company-reporting ontology, canonical event store, investment conclusion, or KnowledgeForge semantics.

### 38. Stock-position observations

- Representative implementations: `TASK-115` SEC 13F stock positions.
- Observational structure represented: manager-period-security position observations preserving manager CIK/name, issuer, CUSIP, report date, reported 13F value, share/principal amount, and voting/discretion metadata.
- Current maturity: Initial.
- Important limitations: no SEC client, 13F crawler, portfolio analytics, ownership graph, issuer registry, CUSIP resolver, security master, valuation model, holdings aggregation, investment recommendation, canonical position store, or KnowledgeForge semantics.

### 39. Classification-membership observations

- Representative implementations: `TASK-116` World Bank country classifications.
- Observational structure represented: country-classification membership observations preserving country, classification axis, membership code/label, and source metadata.
- Current maturity: Initial.
- Important limitations: no country registry, region ontology, World Bank client, WDI framework, classification hierarchy engine, canonical taxonomy, graph store, geospatial framework, peer-group analytics, or KnowledgeForge semantics.

### 40. Exchange-listing relationship observations

- Representative implementations: `TASK-117` SEC exchange listings.
- Observational structure represented: issuer-to-exchange/ticker listing relationships preserving CIK, issuer name, ticker, exchange, source URL, raw artifact path, and SHA-256 lineage.
- Current maturity: Initial.
- Important limitations: no SEC client, exchange registry, ticker registry, security master, issuer registry, listing lifecycle model, market-microstructure model, canonical relationship graph, or KnowledgeForge semantics.

### 41. Regulated-institution certification relationship observations

- Representative implementations: `TASK-118` FDIC bank certifications.
- Observational structure represented: regulated bank-to-FDIC-certificate relationships preserving certificate ID, institution name, city/state, active flag, charter, selected asset/deposit metadata, source URL, raw artifact path, and SHA-256 lineage.
- Current maturity: Initial.
- Important limitations: no FDIC client, bank registry, regulator registry, charter ontology, bank balance-sheet model, bank-risk analytics, regulatory perimeter framework, canonical relationship graph, or KnowledgeForge semantics.

### 42. Physical branch-location relationship observations

- Representative implementations: `TASK-119` FDIC branch locations.
- Observational structure represented: regulated bank-to-branch-location relationships preserving certificate ID, bank name, source-native branch unique number, address, city/state/ZIP, main-office flag, latitude/longitude, source URL, raw artifact path, and SHA-256 lineage.
- Current maturity: Initial.
- Important limitations: no FDIC client, bank registry, branch registry, geocoder, GIS framework, geospatial ontology, branch-network analytics, service-area model, relationship graph, registry abstraction, or KnowledgeForge semantics.

### 43. Company cash-flow statement fact observations

- Representative implementations: `TASK-120` SEC company cash-flow facts.
- Observational structure represented: issuer × fiscal period × cash-flow statement concept × USD value, preserving CIK, entity name, accession, form, filed date, period start/end, taxonomy, concept metadata, source URL, raw artifact path, and SHA-256 lineage.
- Current maturity: Initial.
- Important limitations: no broad SEC client, XBRL framework, company registry, financial-statement abstraction, cash-flow model, capex analytics, issuer universe, canonical loader, relationship framework, graph model, registry abstraction, or KnowledgeForge semantics.

### 44. Company capital-structure statement fact observations

- Representative implementations: `TASK-121` SEC company capital-structure facts.
- Observational structure represented: issuer × fiscal period × balance-sheet capital-structure concept × USD value, preserving CIK, entity name, accession, form, filed date, period end, taxonomy, concept metadata, source URL, raw artifact path, and SHA-256 lineage.
- Current maturity: Initial.
- Important limitations: no broad SEC client, XBRL framework, company registry, financial-statement abstraction, capital-structure model, leverage analytics, issuer universe, canonical loader, relationship framework, graph model, registry abstraction, or KnowledgeForge semantics.

## Evidence index

Implemented bounded evidence-only tasks covered by this atlas include `TASK-051` through `TASK-081`, `TASK-084` through `TASK-099`, `TASK-101`, `TASK-102`, `TASK-103`, `TASK-104`, `TASK-105`, `TASK-106`, `TASK-107`, `TASK-108`, `TASK-109`, `TASK-110`, `TASK-111`, `TASK-112`, `TASK-113`, `TASK-114`, `TASK-115`, `TASK-116`, `TASK-117`, `TASK-118`, `TASK-119`, `TASK-120`, and `TASK-121`, plus later repository-expansion campaigns such as `TASK-202`, `TASK-203`, `TASK-204`, `TASK-205`, and `TASK-206`, plus canonical-loader and observed-substrate tasks cited above. `TASK-082`, `TASK-083`, and `TASK-100` are not counted as new represented economic capabilities because they are implementation-architecture migration or retrospective tasks rather than source-evidence expansions.

### 25. Business formation, private-sector conditions, and entrepreneurial entry

- Representative implementations: `TASK-123` FRED/Census business applications, `TASK-202` WDI private-sector/business-environment expansion.
- Observational structure represented: monthly business-application flow observations for all business applications and high-propensity business applications with source-specific seasonal-adjustment and business-application-role metadata, plus annual country-period WDI private-sector/business-environment scalar observations covering firm entry, credit information, infrastructure constraints, trade competitiveness, and private-sector development measures.
- Current maturity: Operationally Useful inside the WDI annual-scalar private-sector/business-environment confidence cell; bounded U.S. monthly business-formation evidence remains implemented.
- Important limitations: firm/establishment microdata and registry identity, business-demography births/deaths/survival beyond bounded sources, regulatory event history and methodology/revision metadata, enterprise survey sample metadata, subnational business environment, cross-provider reconciliation, and canonical firm/private-sector taxonomy remain bounded; no broad FRED client, Census BFS client, business-dynamics framework, firm registry, operational ingestion, relationship framework, graph model, registry abstraction, startup model, or firm-birth analytics.

### 26. Vehicle sales and durable-goods demand

- Representative implementations: `TASK-124` FRED vehicle sales.
- Observational structure represented: monthly vehicle-sales flow observations for total light vehicles and autos/light trucks with source-specific seasonal-adjustment and vehicle-sales-role metadata.
- Important limitations: no broad FRED client, auto-sector framework, durable-goods demand model, operational ingestion, relationship framework, graph model, registry abstraction, or Controlled Expansion work.

## Capability: Housing Construction

Status: Developing
Representative implementations: `TASK-127` FRED housing construction, `TASK-145` FRED housing construction core operational dataset, `TASK-147` Census housing pipeline operational evolution slice.

What MacroForge can currently observe: bounded monthly US housing starts and building permits as residential construction/supply-pipeline flow evidence, a long FRED building-permit operational panel, and a bounded official Census construction-pipeline stage panel covering permits, authorized-not-started, starts, under-construction, and completions.

Important limitations: bounded source-specific slices only; no housing framework, real-estate-cycle model, long official Census stage history, permit-to-start relationship model, regional decomposition, Controlled Expansion pipeline, or KnowledgeForge semantics.
- Representative implementations: `TASK-004`-`TASK-006` canonical WDI smoke, multiple bounded WDI domain slices, `TASK-129` operational WDI macro indicators.

## Operational WDI macro indicators

- Representative implementation: `TASK-129` operational WDI macro indicators.
- Observational structure represented: annual country-period macro scalar observations for GDP, population, and inflation.
- Current maturity: Operational-v1 bounded.
- Operational evidence: deterministic raw fixture, normalized artifact, refresh manifest, package fingerprint, isolated PostgreSQL load report, and 90 canonical facts loaded in verification.
- Important limitations: 6 countries, 3 indicators, 5 years only; no all-country/all-indicator ingestion, scheduled refresh, broad WDI client, canonical indicator ontology, KnowledgeForge API, or project-wide Controlled Expansion.

## TASK-132 WDI Phase 1 Operational Expansion

WDI macro indicators now have bounded operational Phase 1 coverage: 217 non-aggregate WDI countries/territories, validated indicators `NY.GDP.MKTP.CD`, `SP.POP.TOTL`, and `FP.CPI.TOTL.ZG`, annual years 2000–2023, 15,624 observed-package rows, deterministic refresh manifest/delta report, and isolated PostgreSQL load/reload evidence. This is Operational Capability Expansion, not full WDI catalog ingestion or Controlled Expansion.

## TASK-133 WDI Demographics Phase 1

WDI demographics now has bounded operational Phase 1 coverage: 217 non-aggregate WDI countries/territories, eight demographic foundation indicators, annual years 2000–2023, 41,664 observed-package rows, deterministic refresh manifest/delta report, and isolated PostgreSQL load/reload evidence. This is Operational Capability Expansion selected for Knowledge Leverage, not full WDI catalog ingestion, Controlled Expansion, or KnowledgeForge implementation.

## TASK-134 WDI Energy Phase 1

WDI energy now has bounded operational Phase 1 coverage: 217 non-aggregate WDI countries/territories, two validated energy indicators, annual years 2000–2023, 10,416 observed-package rows, deterministic refresh manifest/delta report, and isolated PostgreSQL load/reload evidence. This is Operational Capability Expansion selected for Knowledge Leverage, not full WDI catalog ingestion, Controlled Expansion, or KnowledgeForge implementation.

## TASK-135 IMF IIP G7 Position Panel

IMF IIP external-position stock evidence now includes a bounded G7 annual 2015–2023 panel covering asset positions, liability positions, and net international investment position. This deepens the prior TASK-088 two-country IIP proof into a more useful macro-financial substrate while remaining source-specific and architecture-preserving.

## TASK-136 IMF BOP G7 Financial Account Flow Panel

IMF BOP financial-account flow evidence now includes a bounded G7 annual 2015–2023 panel covering asset/liability financial-account sides. This complements TASK-135 IIP external-position stocks with annual flow evidence while remaining source-specific and architecture-preserving.

## TASK-137 IMF GDD G7 Sector Debt Panel

IMF GDD sector-debt evidence now includes a bounded G7 annual 2015–2023 panel covering general government, private sector, non-financial corporations, and households debt instruments as percent of GDP. This complements IMF IIP stock and BOP flow evidence with domestic debt-burden context.

## TASK-138 SEC AAPL/MSFT Company Financial Statement Panel

SEC Company Facts evidence now includes a bounded integrated company financial statement panel for Apple and Microsoft 2025 10-K facts across income statement, cash flow, liabilities, and equity. This deepens company fundamentals substrate while remaining source-specific and non-analytical.

## TASK-149 UN Comtrade Trade Operational Dataset

UN Comtrade trade evidence now has a bounded operational dataset covering USA-Japan 2023 total-goods imports and exports. This strengthens Trade with reporter-partner flow structure that complements WDI country-level aggregate trade coverage while remaining source-specific and architecture-preserving.

## TASK-150 FRED Housing Prices Operational Dataset

FRED housing price evidence now has a bounded operational dataset covering USA 2024-Q1/Q2 median and average new-home sales prices. This strengthens Housing by adding price-level evidence to existing construction and pipeline-stage operational data while remaining source-specific and architecture-preserving.
