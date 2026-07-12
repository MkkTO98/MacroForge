# Project State

## Current status
No active implementation in progress. TASK-211 WEO substrate and artifact-scaling remediation is complete pending only human review/commit decision.

## Recent completed work
- TASK-211 IMF WEO/DataMapper broad macro repository expansion was implemented as TASK-211 to preserve the existing TASK-210 neutral evidence-release exporter.
- TASK-211 remediation consolidated WEO provider dataset identity to `IMF:WEO:DATAMAPPER`, preserving TASK-209 and TASK-211 as distinct runs under the shared April 2026 release.
- Narrow WEO/DataMapper-specific substrate added in `src/macroforge/imf_weo_datamapper.py`.
- TASK-211 normalized evidence partitioned by indicator: 12 partitions, 31,074 rows, 30,539 observed, 535 explicit missing, maximum partition size 12,002,505 bytes.
- Loader-based staging remediation refreshed obsolete dataset-release references through normal reruns.
- Exactly two approved obsolete dataset-release rows were deleted after zero external references were verified; canonical April 2026 WEO release remains.
- Architecture state was compacted; context health now has 0 warnings.

## Verification snapshot
- Focused remediation/TASK-209/TASK-211 tests: `21 passed in 0.49s`.
- Full suite: `787 passed, 1 skipped in 849.60s`.
- JSON validation: passed.
- PostgreSQL post-delete: obsolete rows 0; canonical release rows 1; canonical staging refs 31,416; TASK-209 facts 342/339/3; TASK-211 facts 31,074/30,539/535; duplicate canonical-key groups 0; repository facts 10,594,305.
- Context health: 0 blocks, 0 warnings.
- Coherence: 0 blocks, 0 warnings.
- Architecture reality audit: 0 blocks, 0 warnings.
- `git diff --check`: passed.

## Guardrails
No commit or push has been performed. Do not call BLS, resume TASK-208, touch TASK-207 FRED-detour files, start unrelated ingestion, or modify unrelated working-tree changes.
