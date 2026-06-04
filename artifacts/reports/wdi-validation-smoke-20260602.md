# WDI validation report

- Task: TASK-007
- Database: `macroforge_wdi_smoke_2d46fe806c9f`
- Overall status: pass
- Expected rows: 8

| check | status | observed | expected |
| --- | --- | ---: | ---: |
| required_tables_exist | pass | 0 | 0 |
| staging_expected_rows | pass | 8 | 8 |
| fact_expected_rows | pass | 8 | 8 |
| no_duplicate_fact_grain | pass | 0 | 0 |
| quality_checks_pass | pass | 0 | 0 |
| lineage_events_present | pass | 2 | >=2 |
