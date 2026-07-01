# data/raw/alfred_gdp_vintage Summary

Status: TASK-058 bounded raw evidence fixture.

This directory contains the recorded ALFRED GDP release-vintage CSV fixture used by the bounded revision-vintage architectural experiment.

Fixture:

- `alfred-gdp-20260528-20260625-2025q4-2026q1.csv`

Scope:

- Provider: ALFRED.
- Series: GDP.
- Vintages: 2026-05-28 and 2026-06-25.
- Economic periods: 2025-Q4 and 2026-Q1.
- Rows: four source-backed observed values.
- Revision behavior: 2026-Q1 changes from 31819.464 to 31865.721; 2025-Q4 remains 31422.526 in both vintages as the unchanged control.

Boundary:

- Fixture evidence only.
- No broad ALFRED/FRED support.
- No API-key infrastructure.
- No canonical loading.
- No generic revision infrastructure.
