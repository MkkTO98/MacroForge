# Deterministic Ingestion Substrate Engineering-Effort Assessment

Date: 2026-06-27
Status: complete
Scope: implementation-driven effectiveness assessment; no production code changes

## Objective

Determine whether the currently implemented Deterministic Ingestion Substrate is measurably reducing the engineering effort required to support additional datasets and future dataset updates, using implementation evidence from the current WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP paths.

This is not an architectural review, not a governance task, and not a redesign. The assessment evaluates whether the substrate is achieving the Strategic Constitution's objective:

> Increase the amount of trustworthy economic knowledge that can be acquired, updated, verified, canonicalized, and maintained per unit of engineering effort without sacrificing determinism, auditability, provenance, reproducibility, or canonical consistency.

## Evidence inspected

Primary implementation evidence:

- `src/macroforge/observed_ingestion.py`
- `src/macroforge/contract_drift.py`
- `src/macroforge/deterministic_change_verification.py`
- `src/macroforge/lineage_generation.py`
- `src/macroforge/wdi_loader.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `src/macroforge/eurostat_namq_loader.py`

Primary test evidence:

- `tests/test_observed_ingestion.py`
- `tests/test_contract_drift.py`
- `tests/test_deterministic_change_verification.py`
- `tests/test_lineage_generation.py`

Primary continuity/evaluation evidence:

- `CONSTITUTION.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/reports/R-20260627-deterministic-ingestion-substrate-execution-model.md`
- `artifacts/reports/R-20260627-contract-validation-drift-detection-verification.md`

## 1. Substrate utilization assessment

### WDI

Source-specific only:

- WDI acquisition/normalized artifact production.
- WDI row semantics such as WDI country ISO3 field, indicator fields, annual period shape, WDI metadata, WDI raw artifact metadata, and `unknown`/`empty` conventions.
- WDI staging table and staging insert SQL.
- WDI provider period and territory mapping SQL.
- WDI canonical fact insertion SQL.
- WDI loader-owned lineage persistence SQL and WDI smoke quality checks.

Shared through the substrate:

- `build_wdi_observed_package(normalized)` produces the shared `ObservedIngestionPackage` contract used by the loader and tests.
- `ObservedObservation` provides the canonical-load-ready observation shape.
- `observed_package_fingerprint` and `compare_observed_packages` provide deterministic replay/equivalence evidence.
- `validate_observed_package_contract` validates WDI package and observation invariants without WDI-specific branching.
- `canonical_lineage_events` and `lineage_values_sql` generate the converged two-event lineage semantics used by the WDI loader.
- `verify_loaded_observed_package` and `verify_loaded_observed_package_contracts` verify WDI expected-vs-loaded equivalence and contract validity in isolated PostgreSQL.

Still duplicated:

- SQL load shape remains loader-specific.
- Staging and canonical insert scaffolding remains repeated in pattern, but not converged enough for extraction because field joins, mappings, and source semantics differ.
- Loader quality-check SQL remains source-specific.

Assessment: WDI now benefits from shared deterministic post-boundary mechanics, even though it still owns its source-specific loading and validation details.

### OECD_NAAG

Source-specific only:

- OECD/SDMX acquisition/normalized artifact production.
- OECD SDMX metadata interpretation, filter representation, `OBS_STATUS` interpretation, `DECIMALS`, units, measure/ref-area fields, and series dimensions.
- OECD staging table and staging insert SQL.
- OECD provider period and territory mapping SQL.
- OECD canonical fact insertion SQL.
- OECD loader-owned lineage persistence SQL and smoke quality checks.

Shared through the substrate:

- `build_oecd_observed_package(normalized)` emits the same `ObservedIngestionPackage` contract used by WDI and Eurostat.
- `canonical_attribute_hash` gives deterministic attribute-set hashing shared with Eurostat and contract validation.
- `validate_observed_package_contract` validates package and observation invariants through the same source-neutral issue model.
- `canonical_lineage_events` and `lineage_values_sql` generate the same two-event lineage semantics as WDI and Eurostat, with checksum included for OECD.
- `verify_loaded_observed_package` and `verify_loaded_observed_package_contracts` verify OECD loaded output against expected package evidence.

Still duplicated:

- OECD's observation status and decimal precision logic appears both in `observed_ingestion.py` and `oecd_sdmx_loader.py`; this is real duplication, but it is source-specific semantic logic rather than converged shared behavior.
- Provider mapping SQL and canonical load joins remain source-specific.
- Quality-check SQL remains repeated in shape, but source-specific in checks and naming.

Assessment: OECD demonstrates substrate reuse beyond WDI because a different provider/API shape now feeds the same package contract, validation, lineage generation, and deterministic verification path.

### EUROSTAT_NAMQ_GDP

Source-specific only:

- Eurostat JSON-stat acquisition/normalized artifact production.
- Eurostat dimension/code-list metadata handling.
- Eurostat quarterly period interpretation, `geo` to ISO3 mapping, seasonal adjustment attributes, status handling, and provider-code details.
- Eurostat staging table and staging insert SQL.
- Eurostat provider code-list, period, territory, indicator, unit, attribute-set, and canonical fact SQL.
- Eurostat loader-owned lineage persistence SQL and smoke quality checks.

Shared through the substrate:

- `build_eurostat_observed_package(normalized)` emits the same `ObservedIngestionPackage` contract for a quarterly source.
- `canonical_attribute_hash` is reused for deterministic attribute-set identity.
- `validate_observed_package_contract` validates quarterly-specific package invariants through source-neutral contract checks such as `period_quarter` validity.
- `canonical_lineage_events` and `lineage_values_sql` generate the same two-event lineage semantics, including checksum support.
- `verify_loaded_observed_package` and `verify_loaded_observed_package_contracts` verify Eurostat reconstructed output against expected package evidence.

Still duplicated:

- Eurostat `_attribute_payload` logic exists in both `observed_ingestion.py` and `eurostat_namq_loader.py`; this is source-specific semantic duplication and should not be extracted as a shared substrate capability yet.
- Quarterly period mapping and source-specific provider-code handling remain properly source-specific.
- Provider-code metadata handling has recurring shape but no converged shared contract/algorithm/implementation yet.

Assessment: Eurostat is the strongest evidence that the substrate is not merely WDI-shaped: quarterly observations, richer attributes, JSON-stat details, provider period mappings, and checksums all pass through the same shared post-boundary package, contract validation, lineage generation, and deterministic verification mechanics.

## 2. Reuse inventory

### ObservedIngestionPackage

Evidence of reuse:

- Implemented as shared dataclasses in `observed_ingestion.py`.
- Used by WDI, OECD, and Eurostat loaders through source-specific builders.
- Used by `contract_drift.py` as the validation input.
- Used by `deterministic_change_verification.py` as the expected package and reconstructed package shape.
- Tested directly across all three sources in `test_observed_ingestion.py`.

Measured reuse signal:

- One shared package contract supports three provider shapes: WDI annual API output, OECD SDMX annual output, and Eurostat JSON-stat quarterly output.
- The same fingerprint/comparison code is used for replay/equivalence rather than having per-source comparison code.

Conclusion: measurable reuse exists. This is the strongest substrate component.

### Contract Validation and Drift Detection

Evidence of reuse:

- `validate_observed_package_contract(package)` consumes only `ObservedIngestionPackage`.
- `test_contract_drift.py` verifies WDI, OECD, and Eurostat packages satisfy the same invariant model.
- `verify_loaded_observed_package_contracts` validates both expected and reconstructed loaded packages for all three sources in the deterministic verification path.

Measured reuse signal:

- A single issue/report model (`ContractDriftReport`, `ContractDriftIssue`) applies to all current source packages.
- The checks detect shared contract drift such as missing required fields, row-count mismatch, invalid attribute hashes, unsupported frequencies, missing periods, and invalid quarters.

Conclusion: measurable reuse exists for post-boundary contract safety. It reduces future reasoning about whether a package still satisfies the currently accepted boundary.

### Deterministic Change Verification

Evidence of reuse:

- `verify_loaded_observed_package` compares expected package evidence to reconstructed loaded output.
- `verify_loaded_observed_package_contracts` composes contract validation with loaded-package equivalence.
- `test_deterministic_change_verification.py` runs a single cross-source verification flow after loading WDI, OECD, and Eurostat into isolated PostgreSQL.

Measured reuse signal:

- The comparison/fingerprint/reporting logic is shared.
- The test uses the same verification assertions for WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP.

Limit:

- Reconstruction still contains source-specific SQL branches in `_loaded_observed_package`. This is acceptable for a proof helper but means deterministic verification is only partly shared.

Conclusion: measurable reuse exists in the verification result shape and comparison/contract assertions, but reconstruction remains source-specific.

### Canonical Lineage Event Generation

Evidence of reuse:

- WDI, OECD, and Eurostat loaders import `canonical_lineage_events` and `lineage_values_sql`.
- Each loader supplies source-specific artifacts and row-count SQL, while the helper emits the same `raw_to_staging` and `staging_to_curated` event semantics.
- `test_lineage_generation.py` verifies checksum and no-checksum SQL shapes.

Measured reuse signal:

- Three loaders reuse one storage-independent event generator instead of independently encoding the event semantics.
- Loader-owned persistence remains intact, preventing premature graph/catalog or orchestration coupling.

Conclusion: measurable reuse exists for lineage semantics, while persistence and row-count scoping remain correctly source-specific.

## 3. Engineering-effort assessment for a hypothetical fourth source

Compared with WDI at MacroForge v1 beginning, a fourth source would now require less effort in several specific ways.

### Less deterministic engineering effort

A fourth source would still need source-specific acquisition, parsing, normalization, staging SQL, mapping SQL, canonical load SQL, and source-specific smoke checks.

However, it could reuse:

- `ObservedIngestionPackage` / `ObservedObservation` as the post-normalization contract.
- `canonical_attribute_hash` and package fingerprinting.
- `compare_observed_packages` for replay/equivalence diagnostics.
- `validate_observed_package_contract` for package invariant checks.
- `canonical_lineage_events` / `lineage_values_sql` for two-step lineage event semantics.
- `verify_loaded_observed_package_contracts` as the target verification shape if reconstruction SQL is added.

Assessment: less deterministic engineering effort is required after the observed boundary, but source-specific pre-boundary and SQL work remain substantial.

### Less human reasoning

A human no longer needs to reason from scratch about:

- what the handoff representation should contain;
- whether package fingerprints are deterministic;
- how to compare expected and reconstructed packages;
- what minimal contract drift issues look like;
- what the two canonical lineage events mean;
- what verification evidence should prove for expected-vs-loaded equivalence.

Human reasoning remains necessary for:

- provider semantics;
- economic meaning;
- canonical mapping acceptance;
- source-specific staging and SQL joins;
- interpreting provider quirks;
- deciding whether a new source actually fits the current package contract or requires contract evolution.

Assessment: human reasoning is reduced materially for post-boundary mechanics, not for source semantics.

### Less LLM reasoning

A future LLM/agent does not need to infer the full verification pattern from ad hoc loader behavior. It can inspect/reuse existing substrate modules and tests.

Reduced LLM reasoning areas:

- package shape;
- deterministic issue/report model;
- lineage event semantics;
- expected-vs-reconstructed equivalence proof;
- regression test shape for supported sources.

Remaining LLM-heavy areas:

- translating a new provider's raw/normalized schema into package observations;
- source-specific metadata interpretation;
- mapping new provider dimensions to canonical dimensions;
- diagnosing loader-specific SQL failures without compact diagnostic artifacts.

Assessment: LLM reasoning is reduced, but not yet minimized. The absence of compact diagnostics/recovery evidence is now the main remaining post-boundary reasoning burden.

### Less deterministic verification effort

A fourth source would not need a new verification concept. It would need source-specific reconstruction SQL and fixture setup, then could use the same expected-vs-loaded comparison and contract verification assertions.

Assessment: verification effort is reduced conceptually and in assertion/reporting code. The source-specific reconstruction branch remains a concrete cost.

### Less maintenance effort

Future package-contract drift, fingerprint behavior, contract issue shape, and lineage event semantics can be maintained centrally.

Maintenance remains source-specific for:

- provider API/schema changes;
- staging table changes;
- mapping changes;
- canonical fact SQL changes;
- quality checks;
- source-specific reconstruction SQL.

Assessment: maintenance effort is reduced for shared post-boundary invariants and proof mechanics. It is not yet reduced for loader SQL or provider-specific semantics.

## 4. Remaining duplicated implementation inventory

The following duplication exists across WDI, OECD, and Eurostat, but should not be extracted unless the evidence threshold is later met.

### Loader SQL skeletons

Repeated pattern:

- source upsert;
- dataset release upsert;
- pipeline run creation;
- staging insert;
- provider period/territory mapping;
- canonical fact insert;
- lineage insert;
- quality-check insert;
- report query.

Why not extract now:

- Contract convergence: partial only.
- Algorithm convergence: partial only; each loader has different dimensions, staging fields, joins, mappings, and source semantics.
- Implementation convergence: not demonstrated; current SQL remains source-specific.
- Deterministic verification: current verification proves output equivalence, not generic loader-SQL abstraction safety.
- Coupling risk: high; extraction could create a premature source framework or SQL template layer.

Conclusion: keep source-specific.

### Provider mapping SQL

Repeated pattern:

- period mappings;
- territory mappings;
- provider labels;
- code systems.

Why not extract now:

- WDI, OECD, and Eurostat differ in period/frequency shape, territory code systems, provider labels, and metadata sources.
- Eurostat has richer provider code-list behavior not shared by WDI/OECD.
- Current implementation evidence supports canonical-domain concepts, not a shared provider metadata/mapping capability.

Conclusion: do not extract yet.

### Quality-check SQL

Repeated pattern:

- expected staging rows;
- expected canonical fact rows;
- source-specific provider/mapping checks.

Why not extract now:

- Shared row-count checks exist conceptually, but source-specific quality checks and severity details vary.
- Current contract validation and deterministic change verification already cover some post-boundary safety, but not loader quality-check semantics.
- No shared quality-check contract or deterministic reporting shape has converged.

Conclusion: defer. This may become evidence for future diagnostics/recovery work, but not for a quality-check framework now.

### Source-specific attribute/observation status logic

Repeated pattern:

- OECD and Eurostat each build attribute payloads/hashes in both observed-package and loader code.

Why not extract now:

- This is not cross-source semantic convergence; it is source-specific duplicated logic.
- Extracting it into shared infrastructure would improperly mix provider semantics into the substrate.

Conclusion: handle only if a future source-specific cleanup task is justified; do not treat as foundational substrate extraction.

### Deterministic verification reconstruction branches

Repeated pattern:

- `_loaded_observed_package` branches by source and uses source-specific reconstruction SQL.

Why not extract now:

- Comparison and report shape have converged; reconstruction has not.
- A generic reconstruction abstraction would need to encode source-specific joins/mappings and could become a source framework.

Conclusion: keep branches until more source evidence shows a safe reconstruction contract.

## 5. Constitutional assessment

The current Deterministic Ingestion Substrate is already producing measurable progress toward the Strategic Constitution's objective.

Evidence:

- Three heterogeneous sources now share one observed package contract.
- Three loaders reuse one lineage event generation algorithm for the converged two-event semantics.
- Three sources use one deterministic package fingerprint/comparison model.
- Three sources satisfy one deterministic contract validation model.
- Three sources are verified through one deterministic expected-vs-loaded equivalence test shape.
- Verification now composes expected package contract validation, reconstructed package contract validation, and package equivalence evidence.

What has improved:

- Trustworthy ingestion knowledge is accumulating in reusable substrate modules, not only in loader-local code.
- Future post-boundary work has clear reusable entry points.
- Human and LLM reasoning about deterministic verification is reduced.
- Lineage and contract drift semantics are no longer rediscovered independently per loader.
- The substrate preserves determinism, auditability, provenance, reproducibility, and canonical consistency because it uses deterministic code, fixture-backed tests, isolated PostgreSQL verification, explicit lineage events, and source-specific ownership for semantics.

What has not yet improved enough:

- Source onboarding still requires substantial source-specific acquisition, parsing, metadata interpretation, staging SQL, mapping SQL, and canonical load SQL.
- Reconstruction SQL remains source-specific.
- Diagnostics/recovery evidence is not yet compact enough; future agents still need to inspect several artifacts and test outputs to diagnose failures.

Constitutional determination:

```text
The substrate is already measurably reducing future engineering effort, but primarily after the observed ingestion boundary.
```

It is not yet a complete ingestion platform, and it should not be treated as one. Its current value is narrower but real: it reduces repeated deterministic engineering, verification, lineage, and contract reasoning after source-specific normalization.

## 6. Future implementation recommendation

Because implementation evidence shows that the substrate is already reducing future engineering effort, continue with the current next capability rather than redirecting to a new extraction.

Recommended next implementation capability:

```text
Ingestion Diagnostics and Recovery Evidence: Discovered -> Specified
```

Reason:

- The main remaining post-boundary effort is not absence of substrate reuse; it is recovery/debugging effort when deterministic verification fails.
- Existing verification evidence is powerful but scattered across package comparisons, contract reports, test assertions, loader output, and PostgreSQL reconstruction.
- A narrowly specified diagnostic evidence shape would reduce human reconstruction and LLM reasoning without extracting source-specific SQL or semantics.

Scope guardrails:

- Derive diagnostics only from existing deterministic verification evidence.
- Do not add orchestration.
- Do not add a source framework.
- Do not add economic validation.
- Do not add semantic quality rules.
- Do not add graph/catalog systems.
- Do not add new datasets.
- Do not extract loader SQL, provider mapping, canonical fact upsert mechanics, or reconstruction abstraction yet.

## Final assessment

The Deterministic Ingestion Substrate is not merely becoming more sophisticated. It is already delivering measurable reuse across WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP.

The improvement is bounded and post-boundary:

```text
source-specific acquisition/parsing/normalization remains source-specific;
ObservedIngestionPackage and downstream deterministic proof mechanics are increasingly shared.
```

This is consistent with the Strategic Constitution. The next implementation should improve the substrate's operational usefulness by specifying compact deterministic diagnostics/recovery evidence from the verification outputs already produced.
