# TASK-180 — Demographic Structure Capability Closure Campaign

Status: complete
Date: 2026-07-09
Type: capability-closure repository expansion campaign

## Objective

Determine whether the Demographic Structure analytical capability can be operationally completed inside the proven WDI annual-scalar confidence cell, and ingest every compatible WDI annual-scalar indicator needed for that capability closure.

## Baseline

TASK-179 found Demographics Operationally Useful for national annual WDI historical core demographics but incomplete for detailed age-sex cohort structure. The selected next step was a WDI detailed age-sex cohort preflight and compatible ingestion campaign before considering UN Population Division or any other provider.

## WDI opportunity assessment

Deterministic WDI catalog assessment selected the full five-year female/male age-band cohort family covering 00-04 through 80+:

- Candidate selected indicators: 68.
- Already loaded candidates before campaign: 0.
- Remaining candidates fetched: 68.
- Outside capability-closure scope catalog indicators classified: 232.
- Outside-scope evidence included partial single-year WDI age 0-25 series and school-age/UN-derived overlapping ranges that do not improve the minimum full-age five-year cohort closure target.

The complete opportunity evidence is in `artifacts/reports/task-180-wdi-opportunity-assessment.json`.

## Implementation result

- Included indicators: 68.
- Provider-preflight exclusions: 0.
- Countries: 217 non-aggregate WDI countries.
- Period: 1990-2024.
- Normalized rows: 516,460.
- Observed values: 516,460.
- Missing-value evidence rows: 0.

## PostgreSQL result

- Curated fact rows before: 861,135.
- Curated fact rows after first load: 1,377,595.
- Curated fact rows added: 516,460.
- WDI indicators before: 114.
- WDI indicators after: 182.
- WDI indicators added: 68.
- Staging rows after validation rerun: 3,173,661.
- `meta.pipeline_run`: 8.
- `meta.lineage_event`: 16.
- `meta.quality_check`: 16.

## Validation

- First-load staging run check: passed at 516,460 rows.
- First-load curated run check: passed at 516,460 rows.
- Rerun staging run check: passed at 516,460 rows.
- Rerun curated run check: passed at 516,460 rows.
- Fact rows added by rerun: 0.
- Duplicate canonical key groups: 0.
- Lineage preserved: true.
- Canonical TASK-180 scope fingerprint: `4e008cfa8599c21b789c71e87ad35ccb`.

## Capability closure answer

Yes. The Demographic Structure capability can now be considered operationally complete within the WDI annual-scalar confidence cell for national annual historical five-year female/male age-cohort counts and within-sex shares over 1990-2024.

Qualification: this does not complete projection scenarios, single-year full-age distributions, subnational cohorts, or cross-source validation.

## Provider boundary answer

No additional provider is justified for historical national annual five-year age-sex structure. WDI has supplied the full compatible five-year cohort closure target. UN Population Division becomes justified only for projection/scenario semantics, release/versioned future periods, or cross-source validation beyond WDI.

## Architecture result

The existing WDI annual-scalar path handled the large same-family demographic cohort campaign without schema redesign, provider mirror, generic demographic framework, canonical identity change, partitioning, or production scheduling.

## Deliverables

- `tools/task180_demographic_structure_capability_closure.py`
- `data/raw/demographic_structure_task180/task-180-wdi-age-sex-cohort-1990-2024.json`
- `data/processed/demographic_structure_task180/task-180-wdi-age-sex-cohort-normalized.json`
- `artifacts/reports/task-180-final-campaign-report.json`
- `artifacts/reports/task-180-wdi-opportunity-assessment.json`
- `artifacts/reports/task-180-load-report.json`
- `artifacts/reports/task-180-idempotence-validation-report.json`
- `artifacts/reports/R-20260709-task-180-demographic-structure-campaign.md`
- `artifacts/reports/R-20260709-task-180-postgresql-growth-report.md`
- `artifacts/reports/R-20260709-task-180-capability-closure-assessment.md`
- `artifacts/reports/R-20260709-task-180-provider-boundary-assessment.md`
- `artifacts/reports/R-20260709-task-180-architectural-scaling-assessment.md`
- `artifacts/reports/R-20260709-task-180-updated-demographics-domain-assessment.md`

## Verification

Final closeout verification:

```text
python3 -m py_compile tools/task180_demographic_structure_capability_closure.py
# passed

python3 - <<'PY'
import json
from pathlib import Path
paths=sorted(Path('artifacts/reports').glob('task-180-*.json'))
for p in paths:
    json.loads(p.read_text())
print(f'task-180 json reports valid: {len(paths)}')
PY
# task-180 json reports valid: 11

uvx pytest -q tests/test_wdi_loader.py tests/test_wdi_implemented_compatible_campaign.py tests/test_architectural_governance.py
# 11 passed in 5.80s
```

Initial context/coherence checks after continuity edits found only size warnings. Primary state and handoff were compacted; final verification completed with `context_health.py`, `check_coherence.py`, and `architecture_reality_audit.py` all reporting 0 block(s), 0 warning(s), and `git diff --check` passing with no output.
