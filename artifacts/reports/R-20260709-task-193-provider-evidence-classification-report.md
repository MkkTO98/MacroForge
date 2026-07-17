# TASK-193 Provider Evidence Classification Report

Excluded datasets: 3.

- `SL.TLF.TOTL.MA.IN`: classification `provider_unavailable`, provider evidence category `zero_observations_within_requested_scope`; evidence: Metadata exists from World Bank source 11/Africa Development Indicators; data response total=0 after requested 1990-2024/non-aggregate scope despite 1,380 rows before non-aggregate filter.
- `SL.EMP.TOTL.SP.NE.MA.ZS`: classification `provider_unavailable`, provider evidence category `provider_unavailable_invalid_indicator`; evidence: World Bank data and metadata endpoints returned Invalid value / parameter value is not valid.
- `SL.EMP.TOTL.SP.NE.FE.ZS`: classification `provider_unavailable`, provider evidence category `provider_unavailable_invalid_indicator`; evidence: World Bank data and metadata endpoints returned Invalid value / parameter value is not valid.

Raw acquisition evidence for included and excluded indicators was preserved in `data/raw/task193_wdi_labor_closure/task-193-wdi-labor-closure-51i-1990-2024.json`.
