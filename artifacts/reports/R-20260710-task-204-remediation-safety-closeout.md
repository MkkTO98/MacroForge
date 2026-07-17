# TASK-204 remediation-safety closeout

Date: 2026-07-10
Type: bounded remediation safety verification
Status: complete

## Scope

This closeout verified the TASK-204 correction path only. It did not reopen provider selection, create a new campaign, create a gender taxonomy, or alter frozen architecture.

## Acquisition-error completion semantics

Executable enforcement was added to `tools/task204_wdi_gender_equality_chunked_expansion.py`:

- acquisition-error placeholders classify as `provider_evidence_category = acquisition_error`;
- campaign manifest generation records `completion_semantics`;
- unresolved acquisition errors set `status = blocked_unresolved_acquisition_errors`;
- unresolved acquisition errors make all completion claims false:
  - `can_claim_successful_completion = false`;
  - `can_claim_candidate_set_exhaustion = false`;
  - `can_claim_capability_closure = false`;
- `fetch` and `manifest` commands return non-zero when unresolved acquisition errors remain.

Regression coverage was added in `tests/test_task204_provider_exclusion_classification.py` for both blocked and complete completion semantics.

Current TASK-204 regenerated manifest output:

```text
{"row_count": 1410500, "status": "complete", "unresolved_acquisition_error_count": 0}
```

Current manifest summary:

```json
{"candidate_count": 220, "completion_semantics": {"can_claim_candidate_set_exhaustion": true, "can_claim_capability_closure": true, "can_claim_successful_completion": true, "status": "complete", "unresolved_acquisition_error_count": 0, "unresolved_acquisition_error_indicators": []}, "excluded_indicator_count": 34, "included_indicator_count": 186, "row_count": 1410500}
```

## Future WDI campaign applicability

The WDI loader remediation is inherited mechanically by future WDI campaigns because they call `src/macroforge/wdi_loader.py` for PostgreSQL promotion.

The acquisition-error completion guard is executable in the corrected TASK-204 chunked campaign path and will be inherited by future campaigns that copy forward the corrected TASK-204 chunked script pattern. There is no separate repository campaign-template module to patch without introducing a new abstraction/framework. This closeout therefore did not create a new orchestration framework; it kept the protection in the current copy-forward campaign script and its regression tests.

## Shared WDI loader safety

`src/macroforge/wdi_loader.py` was verified with a PostgreSQL-backed regression test covering corrected same-run reload behavior.

Findings:

- Obsolete staging rows are deleted only for the intended `pipeline_run_id` selected by the current run key.
- Obsolete curated facts are deleted only for the same current run key / pipeline run.
- Unrelated run rows and facts remain unchanged.
- Corrected reruns replace stale same-run facts.
- Staging `as_of_date` is refreshed on conflict update.
- Lineage and quality rows are deleted/reinserted for the run and do not duplicate.
- Repeated corrected reruns are idempotent.
- SQL generation wraps the replacement in `BEGIN; ... COMMIT;`, so an obvious mid-script failure cannot commit a partial destructive replacement under PostgreSQL transaction semantics.

Regression evidence from `tests/test_wdi_loader.py`:

- first corrected rerun result equals second corrected rerun result;
- corrected same-run staging/fact counts become 7/7 while unrelated-run counts remain 8/8 in the isolated test database;
- same-run staging `as_of_date` becomes `2028-01-01` while unrelated run remains `2027-01-01`;
- same-run lineage/quality rows remain 2/2 after repeated reruns;
- duplicate canonical-key groups remain 0.

## Tests and verification

Targeted tests:

```text
PYTHONPATH=src:. uvx pytest -q tests/test_task204_provider_exclusion_classification.py
3 passed in 0.03s

PYTHONPATH=src:. uvx pytest -q tests/test_wdi_loader.py::test_wdi_loader_corrected_same_run_reload_is_scoped_and_idempotent tests/test_wdi_loader.py::test_wdi_loader_sql_uses_transaction_and_run_scoped_replacement
2 passed in 0.73s

PYTHONPATH=src:. uvx pytest -q tests/test_task204_provider_exclusion_classification.py tests/test_wdi_loader.py tests/test_wdi_implemented_compatible_campaign.py tests/test_repository_execution_verifier.py
13 passed in 1.68s
```

Full suite:

```text
PYTHONPATH=src:. uvx pytest -q
715 passed in 482.02s (0:08:02)
```

Repository verifier:

- `task-204-remediation-safety-verifier-chunk-01.json`: pass, 607,215 run-scoped facts, 80 indicators, 217 territories, 1990:2024, 0 duplicate WDI canonical-key groups.
- `task-204-remediation-safety-verifier-chunk-02.json`: pass, 499,800 run-scoped facts, 66 indicators, 217 territories, 1990:2024, 0 duplicate WDI canonical-key groups.
- `task-204-remediation-safety-verifier-chunk-03.json`: pass, 303,485 run-scoped facts, 40 indicators, 217 territories, 1990:2024, 0 duplicate WDI canonical-key groups.

A first verifier invocation used the Markdown report glob by mistake and failed because Markdown files are not JSON; the verifier was immediately rerun with `artifacts/reports/task-204-*.json` and passed for all three chunks.

## Final repository verification

PostgreSQL verification:

```text
TASK-204 run scope: 1410500|186|217|1990:2024
Duplicate WDI canonical-key groups: 0
Final curated facts: 10424284
```

Required values reconfirmed:

- TASK-204 run-scoped facts: 1,410,500.
- Compatible indicators: 186.
- Territories: 217.
- Period range: 1990:2024.
- Duplicate WDI canonical-key groups: 0.
- Final repository facts: 10,424,284.
- No repository count changes were made by this closeout.

## Architecture verdict

Architecture remains frozen/evidence-maintained. The remediation confirmed an implementation hygiene defect in acquisition-error completion semantics and WDI same-run reload replacement, not a doctrine defect. No provider framework, taxonomy, optimization layer, or planning system was introduced.
