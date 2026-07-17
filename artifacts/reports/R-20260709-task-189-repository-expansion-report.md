# TASK-189 Repository Expansion Report

Status: complete
Date: 2026-07-09

## Campaign

WDI External Vulnerability and Financial Openness Repository Expansion Campaign

## Scope executed

- Included indicators: 17.
- Countries/entities: 217 non-aggregate WDI countries.
- Temporal coverage: 1990:2024.
- Rows loaded: 129,115.
- Observed non-null values: 90,469.
- Missing-value rows preserved as provider evidence: 38,646.

## Campaign continuation after localized incompatibilities

Three candidates were excluded because they had no non-null observations in the requested provider window. The broader compatible campaign continued and loaded all validated observations.

## Deterministic package evidence

- Observed package fingerprint: `bbc809f6d98d453f61c96c1ee24fb60b03b26aa3bffb93fe710f49523fc0fdbb`.
- Self replay equivalent: `True`.
- PostgreSQL load counts: `{'fact_rows': 1506710, 'lineage_events': 18, 'quality_checks': 18, 'staging_rows': 3302776}`.
