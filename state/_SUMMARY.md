# Folder Summary: state

## Purpose
Current project state files: active goal, architecture posture, project state, issues, lessons, and recent changes.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `active_goal.md`
- `architecture.md`
- `known_issues.md`
- `lessons.md`
- `project_state.md`
- `recent_changes.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `active_goal.md` identifies the current direction: next-ten-source Evidence-Accumulating Source Expansion after completed TASK-054 bounded U.S. Treasury Fiscal Data evidence slice.
- `project_state.md` and `architecture.md` record Observed Boundary and Contract Stability, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback as Verified, plus an emerging Deterministic Ingestion Substrate architectural layer/execution model after `ObservedIngestionPackage`.
- DEC-022 records the accepted default assumption: the current post-boundary architecture is correct unless repeated heterogeneous implementations falsify it; future tasks should reduce engineering, human, or LLM effort for future trustworthy datasets.
- `known_issues.md` records low-priority technical debt that `project_state.md` and `architecture.md` are increasingly mixing operational state with accumulated architectural history.
- Deterministic Change Verification remains Verified; TASK-046's `ObservedIngestionPackage` v1 remains the public internal contract.

## Needs Attention
- Future tasks should be evaluated by reduction in deterministic engineering, human effort, LLM reasoning, and uncertainty; confidence increase; knowledge accumulated; leverage; complexity; and maintenance burden.
- Do not advance Observed Boundary and Contract Stability, Canonical Lineage Event Generation, Contract Validation and Drift Detection, or Deterministic Ingestion Feedback beyond Verified without separate adoption tasks.
- TASK-054 is complete: bounded U.S. Treasury Fiscal Data through `ObservedIngestionPackage`; use substrate evolution reactively and evidence-gated when selecting TASK-055.
