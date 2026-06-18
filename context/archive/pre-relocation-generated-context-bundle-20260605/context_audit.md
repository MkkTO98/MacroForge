# Context Audit Report

Task: TASK-033
Task type: architecture_decision
Context mode: project_wide_review
Review justification: TASK-033 is a strategic next-scope governance decision after the canonicalization-state foundation; user explicitly requested option comparison for uncertainty reduction, including deferring AI dependence and validating workflow before complexity.
Model target: cloud
Model selected: gpt-5.5
Model reason: TASK-033 is governance/architecture next-scope analysis optimizing uncertainty reduction after canonicalization-state foundation.
Estimated tokens: 32188
Budget tokens: 64000
Within budget: True
Raw logs excluded: True
Summaries used: True

## Included files
- `context/PROJECT_CONTEXT.md` (441 tokens): project summary/current state
- `state/project_state.md` (1008 tokens): project summary/current state
- `state/active_goal.md` (595 tokens): project summary/current state
- `state/architecture.md` (1008 tokens): project summary/current state
- `context/latest_handoff.md` (750 tokens): short recent handoff summary
- `state/recent_changes.md` (25 tokens): short recent handoff summary
- `artifacts/tasks/TASK-033-decide-next-scope-after-canonicalization-state-foundation.md` (678 tokens): active task file
- `_SUMMARY.md` (252 tokens): project-wide governance review folder map
- `agents/_SUMMARY.md` (124 tokens): project-wide governance review folder map
- `artifacts/_SUMMARY.md` (99 tokens): summary for explicitly retrieved source file parent
- `artifacts/decisions/_SUMMARY.md` (693 tokens): explicitly requested relevant folder summary
- `artifacts/handoffs/_SUMMARY.md` (112 tokens): project-wide governance review folder map
- `artifacts/reports/_SUMMARY.md` (486 tokens): summary for explicitly retrieved source file parent
- `artifacts/reviews/_SUMMARY.md` (91 tokens): project-wide governance review folder map
- `artifacts/tasks/_SUMMARY.md` (744 tokens): summary for explicitly retrieved source file parent
- `confidence/_SUMMARY.md` (100 tokens): project-wide governance review folder map
- `config/_SUMMARY.md` (95 tokens): project-wide governance review folder map
- `context/_SUMMARY.md` (227 tokens): summary for explicitly retrieved source file parent
- `context/imports/_SUMMARY.md` (90 tokens): project-wide governance review folder map
- `context/imports/chatgpt_export_recovery/_SUMMARY.md` (61 tokens): project-wide governance review folder map
- `context/reconstruction/_SUMMARY.md` (155 tokens): project-wide governance review folder map
- `data/_SUMMARY.md` (174 tokens): project-wide governance review folder map
- `data/curated/_SUMMARY.md` (95 tokens): project-wide governance review folder map
- `data/metadata/_SUMMARY.md` (194 tokens): project-wide governance review folder map
- `data/metadata/eurostat/_SUMMARY.md` (104 tokens): project-wide governance review folder map
- `data/metadata/oecd_sdmx/_SUMMARY.md` (109 tokens): project-wide governance review folder map
- `data/metadata/wdi/_SUMMARY.md` (101 tokens): project-wide governance review folder map
- `data/staging/_SUMMARY.md` (99 tokens): project-wide governance review folder map
- `db/_SUMMARY.md` (186 tokens): project-wide governance review folder map
- `db/migrations/_SUMMARY.md` (244 tokens): project-wide governance review folder map
- `db/queries/_SUMMARY.md` (103 tokens): project-wide governance review folder map
- `db/schema/_SUMMARY.md` (100 tokens): project-wide governance review folder map
- `docs/_SUMMARY.md` (201 tokens): summary for explicitly retrieved source file parent
- `docs/architecture/_SUMMARY.md` (311 tokens): summary for explicitly retrieved source file parent
- `docs/data/_SUMMARY.md` (131 tokens): project-wide governance review folder map
- `docs/runbooks/_SUMMARY.md` (95 tokens): project-wide governance review folder map
- `hardware/_SUMMARY.md` (96 tokens): project-wide governance review folder map
- `instructions/_SUMMARY.md` (134 tokens): project-wide governance review folder map
- `knowledge/_SUMMARY.md` (96 tokens): project-wide governance review folder map
- `logs/_SUMMARY.md` (155 tokens): project-wide governance review folder map
- `logs/derived/_SUMMARY.md` (87 tokens): project-wide governance review folder map
- `memory/_SUMMARY.md` (97 tokens): project-wide governance review folder map
- `memory/archive/_SUMMARY.md` (88 tokens): project-wide governance review folder map
- `memory/deprecated_decisions/_SUMMARY.md` (95 tokens): project-wide governance review folder map
- `metrics/_SUMMARY.md` (100 tokens): project-wide governance review folder map
- `metrics/recommendations/_SUMMARY.md` (96 tokens): project-wide governance review folder map
- `metrics/reports/_SUMMARY.md` (92 tokens): project-wide governance review folder map
- `models/_SUMMARY.md` (96 tokens): project-wide governance review folder map
- `permissions/_SUMMARY.md` (133 tokens): project-wide governance review folder map
- `pipelines/_SUMMARY.md` (81 tokens): project-wide governance review folder map
- `pipelines/wdi/_SUMMARY.md` (134 tokens): project-wide governance review folder map
- `policies/_SUMMARY.md` (89 tokens): project-wide governance review folder map
- `question_queue/_SUMMARY.md` (95 tokens): project-wide governance review folder map
- `question_queue/answered/_SUMMARY.md` (93 tokens): project-wide governance review folder map
- `question_queue/archive/_SUMMARY.md` (92 tokens): project-wide governance review folder map
- `question_queue/pending/_SUMMARY.md` (92 tokens): project-wide governance review folder map
- `recovery/_SUMMARY.md` (103 tokens): project-wide governance review folder map
- `simulation/_SUMMARY.md` (105 tokens): project-wide governance review folder map
- `simulation/dry_runs/_SUMMARY.md` (452 tokens): project-wide governance review folder map
- `skills/_SUMMARY.md` (165 tokens): project-wide governance review folder map
- `src/_SUMMARY.md` (83 tokens): summary for explicitly retrieved source file parent
- `src/macroforge/_SUMMARY.md` (326 tokens): summary for explicitly retrieved source file parent
- `state/_SUMMARY.md` (231 tokens): summary for explicitly retrieved source file parent
- `tests/_SUMMARY.md` (334 tokens): summary for explicitly retrieved source file parent
- `tests/fixtures/_SUMMARY.md` (102 tokens): project-wide governance review folder map
- `tests/invariants/_SUMMARY.md` (93 tokens): project-wide governance review folder map
- `tools/_SUMMARY.md` (224 tokens): project-wide governance review folder map
- `artifacts/decisions/DEC-015-next-scope-canonical-indicator-unit-comparability.md` (1508 tokens): explicitly requested decision record
- `artifacts/decisions/DEC-016-ai-assisted-canonicalization-layer.md` (1508 tokens): explicitly requested decision record
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md` (1367 tokens): explicitly requested decision record
- `artifacts/tasks/TASK-032-implement-minimal-canonicalization-state-foundation.md` (930 tokens): explicitly retrieved source file
- `artifacts/reports/canonicalization-state-foundation-20260605.json` (3008 tokens): explicitly retrieved source file
- `src/macroforge/canonicalization_state.py` (3008 tokens): explicitly retrieved source file
- `tests/test_canonicalization_state.py` (1651 tokens): explicitly retrieved source file
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md` (3008 tokens): explicitly retrieved source file

## Excluded files
- `data/raw/_SUMMARY.md`: raw data excluded unless explicitly relevant
- `data/raw/eurostat/_SUMMARY.md`: raw data excluded unless explicitly relevant
- `data/raw/oecd_sdmx/_SUMMARY.md`: raw data excluded unless explicitly relevant
- `data/raw/wdi/_SUMMARY.md`: raw data excluded unless explicitly relevant
- `logs/agents/_SUMMARY.md`: raw logs/session transcripts excluded from normal context
- `logs/raw/_SUMMARY.md`: raw logs/session transcripts excluded from normal context
