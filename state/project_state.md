# Project State

MacroForge remains in Phase 2 diverse-source repository expansion.

Current state: TASK-209 is complete. It added a substantive non-BLS, non-trade, non-company, non-asset macroeconomic campaign from the proven IMF provider path: IMF WEO DataMapper API v1 G20 macroeconomic projections.

TASK-209 PostgreSQL evidence:

- canonical source: `IMF_WEO_DATAMAPPER_API_V1`;
- run key: `task-209-imf-weo-g20-projection-phase2-world-economic-outlook-april-2026`;
- staging rows: 342;
- curated facts: 342;
- indicators: 6;
- territories: 19;
- annual projection periods: 3 (`2026:2028`);
- lineage events: 2;
- quality checks: 2;
- failed quality checks: 0;
- duplicate canonical-key groups: 0;
- observed/provider-valued facts: 339;
- explicit-missing facts: 3;
- idempotent rerun: true.

Provider evidence: 342 candidate observation cells were attempted. IMF DataMapper returned 339 provider-valued facts, no acquisition errors, and 3 explicit-missing Saudi Arabia `LUR` facts for 2026-2028. A bounded forecast-vintage audit corrected TASK-209 to use deterministic release key `world-economic-outlook-april-2026` and release-specific run key `task-209-imf-weo-g20-projection-phase2-world-economic-outlook-april-2026`.

TASK-208 remains deferred. Do not run or report TASK-208 again before the scheduled return time. Do not touch the four TASK-207 FRED-detour files or unrelated working-tree changes.
