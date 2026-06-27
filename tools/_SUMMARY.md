# Folder Summary: tools

## Purpose
This folder is part of the ProjectForge file-backed operating system for `tools`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `analyze_metrics.py`
- `architecture_reality_audit.py`
- `build_context.py`
- `check_coherence.py`
- `context_health.py`
- `consult_metaharvest.py`
- `create_question.py`
- `detect_hardware.py`
- `dry_run.py`
- `escalate.py`
- `git_autopush.py`
- `install.sh`
- `log_run.py`
- `record_metric.py`
- `recover_session.py`
- `register_project.py`
- `review_metrics.py`
- `run.py`
- `select_model.py`
- `telegram_notifier_stub.py`
- `update_context_summaries.py`
- `update_state.py`
- `validate_dry_run.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `tools/consult_metaharvest.py` implements the trigger-gated MetaHarvest consultation preflight helper. It is advisory-only and runs only for scoped task/governance classification, with versioned structured classification, separate Consultation/Retrieval Contracts, bounded retrieval, non-blocking failure, and mandatory Authority note. Classification v2 includes `foundational_capability_extraction` for proposed implementation expected to become a reusable dependency of multiple future capabilities.
- `tools/recover_session.py` provides bounded fresh-session recovery; `tools/check_coherence.py` now treats the continuity framework files as generated-project requirements.

## Needs Attention
- No folder-specific issues recorded.
