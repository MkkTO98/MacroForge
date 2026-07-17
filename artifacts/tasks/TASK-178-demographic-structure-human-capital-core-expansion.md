# TASK-178 — Demographic Structure and Human Capital Core Repository Expansion Campaign

Status: complete
Date: 2026-07-08
Type: operational repository expansion campaign

## Objective

Execute the TASK-177 recommended WDI Demographic Structure and Human Capital Core bulk campaign inside the Demographics, Human Capital, and Population Structure domain. The campaign materially expands demographic/human-capital analytical capability while continuing to validate the WDI annual-scalar confidence cell under broader demographic indicator diversity.

## Scope

- Provider: World Bank WDI.
- Confidence cell: WDI public API v2 annual scalar country-indicator observations, non-aggregate country scope, PostgreSQL-loaded WDI path.
- Countries: 217 accepted non-aggregate WDI countries.
- Period: 1990-2024.
- Candidate indicators assessed: 30.
- Included indicators: 28.
- Excluded indicators: 2 (`SM.POP.REFG`, `SM.POP.REFG.OR`) because the World Bank API returned indicator-not-found errors indicating the indicators may have been deleted or archived.
- No new provider onboarding, schema change, canonical identity change, provider mirror, generic demographic framework, or production scheduling was performed.

## Baseline from TASK-177

Before TASK-178, demographic/human-capital-related canonical WDI coverage included:

- 18 indicators.
- 217 countries.
- 1990-2024 annual coverage.
- 136,710 country-year fact rows.
- 117,347 observed non-null values.

Operationally Useful before campaign:

- total population;
- population growth;
- broad age shares;
- dependency ratios;
- fertility;
- life expectancy;
- urbanization share.

First-order gaps before campaign:

- sex-specific structure;
- births/deaths;
- mortality depth;
- adolescent fertility;
- urban/rural stocks;
- density/land context;
- primary/literacy/completion education;
- health prevention/workforce/access;
- forced migration stocks.

## Result

PostgreSQL/WDI repository growth:

- Curated fact rows before: 648,475.
- Curated fact rows after first load: 861,135.
- Curated fact rows added: 212,660.
- WDI indicators before: 86.
- WDI indicators after: 114.
- WDI indicators added: 28.
- TASK-178 scope after load: 28 indicators, 217 countries, 1990-2024, 212,660 facts, 179,395 observed values, 33,265 missing-value evidence rows.

Validation:

- First load quality checks passed: staging rows and run-scoped curated fact rows both 212,660.
- Rerun added 0 curated facts.
- Duplicate canonical key groups after rerun: 0.
- Lineage preserved: true.
- Canonical TASK-178 scope fingerprint after rerun: `8f109ec016108a3035981a8180cd991d`.

## Capability improvement

TASK-178 materially advanced the Demographic Structure and Human Capital Core capability from broad-but-incomplete population foundation to Operationally Useful WDI annual country-year coverage across:

- sex-specific population stock and sex composition;
- crude birth and death rates;
- infant, child, adult, and maternal mortality;
- adolescent fertility;
- urban/rural population stock and rural share;
- population density and land-area denominator context;
- primary education enrollment/completion, adult literacy, and education fiscal effort;
- child immunization, physician density, and skilled birth attendance;
- labor-force participation by sex and total.

Remaining gaps:

- detailed age/sex cohort pyramids;
- projections/scenarios;
- subnational demographics;
- cross-source demographic validation;
- higher-resolution migration flow and forced-migration stock coverage because the TASK-177 refugee indicators were unavailable in the WDI API.

## Deliverables

Created:

- `tools/task178_demographic_structure_human_capital_campaign.py`
- `data/raw/demographic_structure_task178/task-178-wdi-demographic-structure-human-capital-1990-2024.json`
- `data/processed/demographic_structure_task178/task-178-wdi-demographic-structure-human-capital-normalized.json`
- `artifacts/reports/task-178-capability-baseline-assessment.json`
- `artifacts/reports/task-178-demographic-structure-preflight-report.json`
- `artifacts/reports/task-178-demographic-structure-classification-report.json`
- `artifacts/reports/task-178-demographic-structure-operational-report.json`
- `artifacts/reports/task-178-demographic-structure-coverage-report.json`
- `artifacts/reports/task-178-demographic-structure-exclusion-report.json`
- `artifacts/reports/task-178-demographic-structure-confidence-report.json`
- `artifacts/reports/task-178-inventory-before.json`
- `artifacts/reports/task-178-inventory-after.json`
- `artifacts/reports/task-178-load-report.json`
- `artifacts/reports/task-178-idempotence-validation-report.json`
- `artifacts/reports/task-178-final-campaign-report.json`
- `artifacts/reports/R-20260708-task-178-demographic-structure-human-capital-campaign.md`
- `artifacts/reports/R-20260708-task-178-postgresql-growth-report.md`
- `artifacts/reports/R-20260708-task-178-capability-improvement-report.md`
- `artifacts/reports/R-20260708-task-178-architectural-scaling-report.md`
- `artifacts/reports/R-20260708-task-178-capability-maturity-assessment.md`

Updated continuity/governance state:

- `docs/architecture/domain-coverage-assessment.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/recent_changes.md`
- `context/latest_handoff.md`
- affected task/report/folder summaries

## Verification

Primary operational commands:

```text
PYTHONPATH=src python3 tools/task178_demographic_structure_human_capital_campaign.py assess --db macroforge
PYTHONPATH=src python3 tools/task178_demographic_structure_human_capital_campaign.py fetch --db macroforge
PYTHONPATH=src python3 tools/task178_demographic_structure_human_capital_campaign.py artifacts
/usr/bin/time -f 'wall=%E maxrss_kb=%M' env PYTHONPATH=src python3 tools/task178_demographic_structure_human_capital_campaign.py load --db macroforge
/usr/bin/time -f 'wall=%E maxrss_kb=%M' env PYTHONPATH=src python3 tools/task178_demographic_structure_human_capital_campaign.py validate --db macroforge
PYTHONPATH=src python3 tools/task178_demographic_structure_human_capital_campaign.py reports --db macroforge
```

Measured load/validation:

- First load wall time: 1:04.27; command max RSS: 2,057,604 KB; Python process max RSS recorded in report: 1,406,792 KB.
- Rerun validation wall time: 0:27.47; command max RSS: 1,854,896 KB.

Final closeout verification rerun after continuity updates:

```text
python3 -m py_compile tools/task178_demographic_structure_human_capital_campaign.py
# passed

python3 - <<'PY'
import json
from pathlib import Path
paths = sorted(Path('artifacts/reports').glob('task-178-*.json'))
for path in paths:
    json.loads(path.read_text())
print(f'task-178 json reports valid: {len(paths)}')
PY
# task-178 json reports valid: 12

uvx pytest -q tests/test_wdi_loader.py tests/test_wdi_implemented_compatible_campaign.py tests/test_architectural_governance.py
# 11 passed in 4.20s

python3 tools/context_health.py
# context health: 0 block(s), 0 warning(s)

python3 tools/check_coherence.py
# coherence: 0 block(s), 0 warning(s)

python3 tools/architecture_reality_audit.py
# architecture-reality-audit: 0 block(s), 0 warning(s)

git diff --check
# passed, no output
```
