# OECD unit-basis comparability split

TASK-040 records a deterministic split of existing OECD GDP unit-basis evidence.

Status: succeeded
Source requirements: `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json`

## Basis candidates

- `USD_EXC` -> `current_usd_exchange_rate_basis`
  - basis: `exchange_rate`
  - report integration: `deferred`
  - auto apply: `False`
  - caveats: Exchange-rate USD and PPP USD are separate comparability profiles.
- `USD_PPP` -> `current_usd_ppp_basis`
  - basis: `ppp`
  - report integration: `deferred`
  - auto apply: `False`
  - caveats: PPP-basis USD and exchange-rate USD are separate comparability profiles.

## Boundary result

No accepted mapping state was mutated.
No canonical asset manifest base file was mutated.
No unit/currency conversion, frequency aggregation, or report integration was implemented.

## Checks

- oecd_evidence_found: pass
- usd_exchange_rate_and_ppp_split: pass
- basis_caveats_preserved: pass
- no_conversion_or_aggregation: pass
- no_accepted_state_or_manifest_mutation: pass
- no_auto_apply_or_report_integration: pass
- task_039_requirements_linked: pass
