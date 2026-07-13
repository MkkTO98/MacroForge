# Folder Summary: tools

## Purpose
This folder is part of the ProjectForge file-backed operating system for `tools`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `analyze_metrics.py`
- `architecture_reality_audit.py`
- `build_context.py`
- `check_coherence.py`
- `consult_metaharvest.py`
- `context_health.py`
- `create_question.py`
- `detect_hardware.py`
- `dry_run.py`
- `escalate.py`
- `git_autopush.py`
- `install.sh`
- `log_run.py`
- `record_metric.py`
- `recover_session.py`
- `repository_execution_verifier.py`
- `review_metrics.py`
- `run.py`
- `select_model.py`
- `task174_domain_bulk_expansion.py`
- `task176_repository_growth_historical_scaling.py`
- `task178_demographic_structure_human_capital_campaign.py`
- `task180_demographic_structure_capability_closure.py`
- `task182_revision_aware_validation.py`
- `task184_three_vintage_validation.py`
- `task185_multi_series_alfred_validation.py`
- `task187_sparse_vintage_alfred_validation.py`
- `task189_wdi_external_vulnerability_expansion.py`
- `task190_wdi_human_capital_expansion.py`
- `task191_wdi_energy_transition_expansion.py`
- `task192_wdi_financial_system_expansion.py`
- `task193_wdi_labor_closure_expansion.py`
- `task194_wdi_education_attainment_closure_expansion.py`
- `task196_wdi_health_population_expansion.py`
- `task197_wdi_environment_climate_expansion.py`
- `task198_wdi_economy_growth_chunked_expansion.py`
- `task199_wdi_external_debt_chunked_expansion.py`
- `task200_wdi_poverty_inequality_chunked_expansion.py`
- `task201_wdi_public_sector_fiscal_governance_chunked_expansion.py`
- `task202_wdi_private_sector_business_environment_chunked_expansion.py`
- `task203_wdi_infrastructure_connectivity_chunked_expansion.py`
- `task204_wdi_gender_equality_chunked_expansion.py`
- `task205_wdi_agriculture_rural_development_chunked_expansion.py`
- `task206_wdi_social_protection_all_programs_chunked_expansion.py`
- `task207_bls_us_labor_monthly_phase2_campaign.py`
- `task207_fred_us_macro_monthly_phase2_campaign.py`
- `task208_bls_us_labor_breadth_monthly_phase2_campaign.py`
- `task209_imf_weo_g20_projection_phase2_campaign.py`
- `telegram_notifier_stub.py`
- `update_context_summaries.py`
- `update_state.py`
- `validate_dry_run.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `task209_imf_weo_g20_projection_phase2_campaign.py` builds/loads the release-aware IMF WEO April 2026 G20 projection campaign with explicit-missing semantics for absent requested year keys inside valid country-indicator series.
- `task208_bls_us_labor_breadth_monthly_phase2_campaign.py` remains deferred pending clean BLS regeneration.
- `task206_wdi_social_protection_all_programs_chunked_expansion.py` executes the corrected TASK-206 WDI aggregate social-protection all-program campaign with per-indicator checkpoints, per-chunk raw/normalized artifacts, bounded ASPIRE blank-`countryiso3code` territory fallback, provider classification, and acquisition-error completion semantics.
- `task205_wdi_agriculture_rural_development_chunked_expansion.py` executes the TASK-205 WDI Agriculture & Rural Development campaign with per-indicator checkpoints, per-chunk raw/normalized artifacts, provider classification, and acquisition-error completion semantics inherited from the corrected TASK-204 pattern.
- `task204_wdi_gender_equality_chunked_expansion.py` executes the TASK-204 WDI Gender Equality chunked campaign with checkpoints and per-chunk artifacts; it now records acquisition-error completion semantics and blocks completion claims when unresolved acquisition errors remain.
- `task203_wdi_infrastructure_connectivity_chunked_expansion.py` executes the TASK-203 WDI Infrastructure and Connectivity chunked campaign with checkpoints and per-chunk artifacts.
- `task202_wdi_private_sector_business_environment_chunked_expansion.py` executes the TASK-202 WDI Private Sector and Business Environment chunked campaign with checkpoints and per-chunk artifacts.
- `task201_wdi_public_sector_fiscal_governance_chunked_expansion.py` executes the TASK-201 WDI Public Sector Fiscal/Governance chunked campaign with checkpoints and per-chunk artifacts.
- `task200_wdi_poverty_inequality_chunked_expansion.py` executes the TASK-200 WDI Poverty/Inequality chunked campaign with checkpoints and per-chunk artifacts.
- `task199_wdi_external_debt_chunked_expansion.py` executes the TASK-199 WDI External Debt chunked campaign with checkpoints and per-chunk artifacts.
- `task198_wdi_economy_growth_chunked_expansion.py` implements chunked WDI large-campaign execution with per-indicator checkpoints and per-chunk artifacts.
- `task197_wdi_environment_climate_expansion.py` implements the TASK-197 WDI environment/climate campaign with per-indicator checkpoint/resume support.
- `task196_wdi_health_population_expansion.py` implements the TASK-196 WDI health/population-health campaign with per-indicator checkpoint/resume support.
- `repository_execution_verifier.py` packages repeated repository campaign closeout checks: artifacts, SHA-256, JSON reports, normalized evidence, provider classifications, PostgreSQL run-scope counts, and WDI duplicate-key checks.
- `task194_wdi_education_attainment_closure_expansion.py` fetches/classifies/normalizes TASK-194 WDI/Barro-Lee education-attainment campaign evidence using concurrent WDI requests and preserved response/metadata checksums.
- `task193_wdi_labor_closure_expansion.py` fetches/classifies/normalizes TASK-193 WDI/ILO labor closure campaign evidence and preserves response/metadata checksums.
- `task192_wdi_financial_system_expansion.py` fetches/classifies/normalizes TASK-192 WDI/GFDD financial-system campaign evidence and preserves response/metadata checksums.
- `task191_wdi_energy_transition_expansion.py` fetches/classifies/normalizes TASK-191 WDI energy-transition/access campaign evidence.
- `task190_wdi_human_capital_expansion.py` fetches/classifies/normalizes TASK-190 WDI human-capital foundations campaign evidence.
- `task189_wdi_external_vulnerability_expansion.py` fetches/classifies/normalizes TASK-189 WDI external-vulnerability campaign evidence.
- `task185_multi_series_alfred_validation.py` builds TASK-185 bounded ALFRED GDP+GDPC1 multi-series artifacts and JSON reports from local raw fixtures.
- `task184_three_vintage_validation.py` builds TASK-184 bounded ALFRED GDP three-vintage artifacts and JSON campaign/validation reports from the local raw fixture.
- `task182_revision_aware_validation.py` builds TASK-182 bounded ALFRED GDP revision-aware artifacts from the local raw fixture: normalized JSON, observed-package JSON, campaign report, stable fingerprints, and period/vintage value evidence.
- `tools/consult_metaharvest.py` implements the trigger-gated MetaHarvest consultation preflight helper. It is advisory-only and runs only for scoped task/governance classification, with versioned structured classification, separate Consultation/Retrieval Contracts, bounded retrieval, non-blocking failure, and mandatory Authority note. Classification v2 includes `foundational_capability_extraction` for proposed implementation expected to become a reusable dependency of multiple future capabilities.
- `tools/recover_session.py` provides bounded fresh-session recovery; `tools/check_coherence.py` now treats the continuity framework files as generated-project requirements.

## Needs Attention
- No folder-specific issues recorded.
- `task174_domain_bulk_expansion.py` runs the authorized WDI annual scalar domain bulk expansion campaign: inventory, fetch, preflight/artifacts, PostgreSQL load, and final report.
- `task176_repository_growth_historical_scaling.py` runs the TASK-176 WDI repository growth/historical scaling campaign: opportunity assessment, fetch, artifacts, PostgreSQL load, idempotence validation, and reports.
