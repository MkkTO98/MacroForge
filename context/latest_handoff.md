# Latest Handoff

TASK-215 BIS credit-to-GDP-gap Phase 2 repository expansion is complete and uncommitted.

Capability: `BIS_PUBLIC_SDMX_API` / `BIS:WS_CREDIT_GAP` (`WS_CREDIT_GAP` v1.0), selected key `Q..P.A.C` = quarterly private-nonfinancial-sector credit-to-GDP gap, all lenders, actual-minus-trend, percentage points. Series-key dimensions: `FREQ`, `BORROWERS_CTY`, `TC_BORROWERS`, `TC_LENDERS`, `CG_DTYPE`; territory dimension: `BORROWERS_CTY`.

Scope/results: 2010-Q1..2025-Q4, 43 accepted territories, 43 provider-advertised series, 2,752 cells/facts, 0 missing, 0 acquisition errors, 0 incompatible series, `XM` Euro area aggregate excluded. Snapshot `bis-ws-credit-gap-snapshot-prepared-20260712t162752z` is provider `Prepared` acquired-response evidence, not official release. Run: `task-215-bis-credit-gap-phase2`. Indicator: `BIS:WS_CREDIT_GAP:CREDIT_TO_GDP_GAP_ACTUAL_MINUS_TREND:PRIVATE_NONFINANCIAL_SECTOR:ALL_SECTORS:PERCENTAGE_POINTS:Q`.

Shared-BIS verification before commit narrowed `src/macroforge/bis_sdmx.py`: missing/malformed `Prepared` now raises instead of falling back to raw-checksum snapshot keys. Dedicated substrate tests added in `tests/test_bis_sdmx.py`.

Verification: dedicated substrate `15 passed in 0.07s`; TASK-215+BIS/TASK-213/TASK-214 compatibility `32 passed in 0.62s`; full suite `830 passed in 805.95s (0:13:25)`; JSON/checksum `json_validated=8 checksum_entries=10 checksum_mismatches=0`; DB source/snapshot/staging/facts/observed/missing/indicators/territories/periods/failed-quality/duplicates/repository-facts = 1/1/2752/2752/2752/0/1/43/64/0/0/10605067; coherence/context health/architecture audit all 0 blocks and 0 warnings; `git diff --check` clean.

Changed boundary: TASK-215 implementation/reports/processed artifacts/state/docs plus `src/macroforge/bis_sdmx.py` and `tests/test_bis_sdmx.py`. Active raw evidence remains ignored under `data/raw/task215_bis_credit_gap_phase2_campaign/active/`; failed attempts remain under `_attempts/`.

Guardrail: do not stage, commit, push, clean, restore, move, or delete without explicit authorization. If publishing, normal-add TASK-215 boundary files and force-add only the two active raw evidence files; exclude `_attempts/`, caches, FRED-detour files, completed BLS/WEO/TASK-213/TASK-214 files, and unrelated working-tree changes.
