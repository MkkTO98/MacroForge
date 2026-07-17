# TASK-198 Operational Benchmark Report

Measured TASK-198 execution:

- 262 candidates in 4 chunks of 80/80/80/22.
- First full fetch/materialization command: 8:35.71 elapsed, reported fetch phase 425.473 seconds, max RSS 4,937,804 KB.
- Checkpoint rerun/materialization command: 1:57.20 elapsed, reported fetch phase 27.299 seconds, max RSS 3,306,832 KB.
- Largest raw chunk: about 244.5 MB.
- Largest normalized chunk: about 505.7 MB.
- Aggregate loaded facts: 1,587,355.

Measured improvement: a 262-candidate campaign completed under the 600-second command limit using chunked artifacts where the prior monolithic 155-candidate TASK-197 run had hit the limit once. Artifact pressure moved from one monolithic artifact to deterministic chunks.
