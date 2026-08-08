# Continuity and Recovery Framework

Purpose: preserve work continuity across Hermes sessions while spending the fewest possible tokens needed to recover useful state.

This framework extends existing ProjectForge state, task, decision, context-health, and handoff mechanisms. It is not a new governance layer, database, vector store, index, or parallel source of truth.

## Recovery contract

A fresh agent session should recover by reading, in order:

1. `CONSTITUTION.md`
2. `state/active_goal.md`
3. `state/project_state.md`
4. `state/architecture.md`
5. `context/latest_handoff.md` when present
6. the active task artifact only when named by the startup files or recovery report
7. only relevant decisions and folder summaries

Repository-wide scanning is not a startup step. Raw logs, session JSONL, previous full conversations, generated context bundles, unrelated folders, and large artifacts are excluded from normal recovery.

Use the deterministic helper when a compact recovery snapshot is useful:

```bash
python3 tools/recover_session.py --project .
python3 tools/recover_session.py --project . --json
```

The helper reads a bounded set of fixed files plus only recent direct children of `artifacts/tasks/`, `artifacts/decisions/`, and `question_queue/pending/` when the on-demand question queue exists. It does not inspect raw logs or walk the repository.

## What the recovery snapshot must answer

The recovery snapshot must expose:

- current project state;
- active goal or active/recent task;
- recent decisions;
- current blockers and pending questions;
- next recommended actions;
- recommended resume procedure;
- files consulted.

If these answers are missing or stale, update the existing state/task/handoff artifacts. Do not create a new state artifact just because a current one was poorly maintained.

## Standard ProjectForge closeout contract

The following user command is sufficient to end a normal session safely:

```text
Perform standard ProjectForge closeout. Follow the continuity framework. Run required verification if project files changed. Then stop.
```

When receiving that command, the agent must not ask the user for a custom closeout checklist. It must execute the standard file-backed closeout sequence below, using the current project root:

1. Identify the active task from `state/active_goal.md`, `state/project_state.md`, `context/latest_handoff.md`, or `python3 tools/recover_session.py --project . --json`.
2. Update the active task artifact with current status, outcome/evidence, blockers or open questions, incomplete acceptance criteria, and next recommended action. If no active task exists, record the reason in `context/latest_handoff.md` instead of inventing one.
3. Update `context/latest_handoff.md` with context used, files changed, decisions/tasks updated, tests/checks actually run with real output, blockers, next recommended actions, and the exact resume command.
4. Update `state/active_goal.md` and `state/project_state.md` when their current-state pointers changed. Keep them concise; move history to task, decision, report, or handoff artifacts.
5. Refresh affected `_SUMMARY.md` files when summaries are affected; inspect curated `Active Work`, `Needs Attention`, and task-status sections; patch stale curated notes manually.
6. Run the narrowest meaningful verification after the task/state/handoff/summary edits. For ProjectForge framework/template changes this normally includes tests, root coherence, generated-project inheritance/recovery smoke checks, MacroForge checks when MacroForge was touched, and Architecture-to-Reality Audit for governance/template changes.
7. Replace any `pending verification` placeholders with real verification output, or explicitly record remaining verification as a blocker before stopping.

This standard closeout replaces ad hoc user-provided closeout procedures. User instructions may narrow scope or add checks, but they should not be required to restate the standard task/state/handoff/summary/verification sequence.

### Forward output-family closeout sufficiency

For new tasks and explicitly reopened historical tasks, closeout should account for material output families at family level rather than creating one lifecycle row per file. Legacy completed tasks that predate this structure remain valid historical evidence; do not rewrite them merely to add new fields.

When a task creates or changes material outputs, the active task artifact, closeout note, publication manifest, or equivalent accepted evidence should identify each relevant family with:

- family name or purpose;
- representative/root paths or exact publication-manifest reference;
- owning task/source;
- role: authoritative project truth, local/provider evidence, generated output, temporary attempt/checkpoint, release/export material, or unresolved material;
- terminal disposition: `git-durable project truth`, `local/provider evidence`, `generated/rebuildable`, `external archive`, or `pending decision`;
- publication expectation: publish now, local-only, generated/rebuildable, external-only, or deferred with bounded exception;
- reconstruction/recovery source when applicable.

Relevant ignored and non-Git outputs must be accounted for when they are material to recovery, reproducibility, provider evidence, or publication safety. Caches, bytecode, routine temporary files, and bulk generated material may be covered by path/family inheritance and do not need to be listed individually unless they are the task's substantive output.

Publication verification must distinguish exact staged/commit boundary from completeness. A boundary check proves only what was included. Before publication, declared `git-durable project truth` families must be compared with the authorized staged/commit boundary. Missing declared durable paths and unauthorized extra paths are blockers unless an explicit bounded exception records the reason, owner, recovery evidence, and reconsideration trigger. Local/provider evidence and generated/rebuildable outputs are not required to be committed solely because they were used for validation.

Forward closeout validation is operational, not only doctrinal. For a new task, an explicitly reopened historical task, or a publication boundary that claims completeness, run the project-local validator against the task closeout JSON or equivalent machine-readable closeout report:

```bash
python3 tools/check_coherence.py --project . --lifecycle-closeout /path/to/closeout.json --publication-boundary /path/to/publication-boundary.json
```

The closeout JSON may reuse the active task closeout report format, but it must include a non-empty `output_families` list for forward work. Omitted or empty `output_families` is a blocker in normal mode; an empty list is not a no-output attestation. Legacy completed records may be accepted without rewriting historical artifacts only with explicit historical handling:

```bash
python3 tools/check_coherence.py --project . --lifecycle-closeout /path/to/historical-closeout.json --legacy-record
```

A reopened historical task is forward work for closeout purposes and must not use the legacy bypass.

The ignored-artifact governance lifecycle record uses the versioned record-specific profile `macroforge-ignored-artifact-governance-lifecycle-v3`. It rejects every output-family cardinality except one, compares both the lifecycle declaration and any supplied publication boundary with one code-owned canonical 15-path tuple, preserves the exact ordered correction/review history, and rejects unknown claim-bearing fields. Its `publication` and `candidate_state` objects are transition invariants, not mutable live-verdict assertions. The candidate bytes therefore do not claim that a review is pending, that review is invariably the sole next gate, that local commit proves publication, or that a successor is automatically activated.

For this profile, derive the current transition from independently authenticated Git state plus byte-recoverable external review evidence and evaluate it with `evaluate_publication_transition` in `tools/check_coherence.py`:

- working-tree candidate with no authenticated exact-byte review: independent publication review required;
- working-tree candidate with authenticated exact-byte `BLOCK`: correction required and publication prohibited;
- working-tree candidate with authenticated exact-byte `PASS`: bounded publication permitted without editing the reviewed bytes;
- local commit ahead of the authoritative remote, with the exact-byte `PASS`: push and authoritative-remote verification required; local commit is not publication;
- exact approved commit verified at the authoritative remote: workstream closed without implicit successor activation.

Missing, malformed, ambiguous, unauthenticated, non-recoverable, or different-byte evidence fails closed. A review verdict changes external authority, not repository-byte truth. Historical event state is explicitly temporal and remains unchanged after later transitions.

Provider-originated payloads require a recorded rights/permitted-use status before new public publication. Public accessibility is not redistribution permission. Use existing source metadata such as `meta.source.license_note`, provider/source manifests, publication manifests, or backlog-owned rights evidence where available. Distinguish authored code/tests/tools, synthetic fixtures, provider-originated payloads, derived/normalized provider payloads, already committed legacy fixtures, and newly proposed provider-payload publication. For newly proposed provider-originated or derived provider payloads, `unknown` or `pending review` is not permitted for public publication. A permitted provider-payload publication must include a rights evidence reference. This rule is forward-looking and does not automatically remove or relabel committed legacy fixtures.

A task that changes production PostgreSQL state must not be closed as fully reproducible while necessary authored source, tests, or tools remain non-durable unless the closeout records a bounded exception with reason, owner, recovery evidence, and reconsideration trigger. Raw/provider evidence may remain local/provider evidence; this requirement targets authored implementation needed to recover the production change.

Content-sensitive mutation verification should supplement, not replace, Git path/status fingerprints. For publication or reconciliation in a dirty worktree, capture the path/status fingerprint, complete tracked-diff hash, per-authorized-path content hashes, exact staged boundary, untracked path manifest, bounded untracked/ignored stat fingerprints, and explicit pre/post non-target preservation. The lifecycle validator can emit bounded per-path content fingerprints with repeated `--fingerprint-path PATH`; project-relative paths resolve against `--project`, and an unavailable, symlink, or non-regular requested path blocks rather than producing passing null evidence. Lifecycle-only options such as `--fingerprint-path` require `--lifecycle-closeout`. This is for authorized paths and preservation checks, not a routine hash of all multi-gigabyte provider evidence. Avoid naive substring scans for secrets, SQL mutation, or provider payloads; use context-aware checks.

For ignored and untracked material, `tools/check_coherence.py` is also the canonical capture/comparison route. Supply `--ignored-artifact-policy POLICY.json`; comparison additionally requires both `--ignored-artifact-baseline SNAPSHOT.json` and its caller-supplied `--ignored-artifact-baseline-identity SHA256`. Current capture establishes completeness through independent canonical `git ls-files -z` discovery. Programmatic caller-supplied ignored/untracked NUL streams are fixture transport, not discovery authority: both arguments must actually be supplied, canonically framed, ordered, duplicate-free, scoped, and exactly matched against both independently discovered populations before completeness can be true. Omitted input is distinct from explicitly supplied empty bytes; every one-sided call fails with incomplete `caller-supplied-unverified` semantics. Record the emitted `evidence_identity` outside the snapshot in a task, handoff, or closeout before later comparison. The supplied value is an invocation assertion: it detects mismatch with that value but does not authenticate the caller or establish durable external authority; a self-hash inside a mutable baseline is only an integrity check. A separate `--publication-boundary BOUNDARY.json` may identify authored candidates. Every declared candidate must exist as a safely inspected regular file and belong to the applicable tracked, ignored, or untracked population; publication scope remains separate from preservation classification. Policy schema `macroforge-ignored-artifact-policy-v1` declares exact protected artifacts and explicitly enables recognized disposable classes. Protected declarations require path, classification, reason, owner/producer, lifecycle semantics, content origin, publication expectation, and, for provider evidence, an existing canonical rights classification; regular-file bytes, size, and safe Git executable mode enter the protected identity, while timestamps do not. Disposable classification is limited to structurally validated classes: pytest cache with a complete standardized signature line in a regular `CACHEDIR.TAG` no larger than 512 bytes, and current-interpreter Python bytecode with a bounded size, current magic number, valid PEP 552 flags/header, exactly one non-executed code object, and no trailing bytes. Final paths are first pinned with descriptor-relative, no-follow metadata access; only verified ordinary regular inodes are reopened through their pinned descriptors, with device/inode/type/mode revalidation before bounded reading, so FIFOs and other special files are rejected before any blocking or side-effecting read-open. Cross-interpreter bytecode is not claimed and is rejected. Unclassified ignored or untracked paths, absolute/traversal/`.git`-component paths, unsafe types or special modes, symlinks, missing or excluded candidates, and authored candidates disguised as caches fail closed. Historical snapshots with incomplete ignored enumeration must retain an explicit qualification; comparison may accept later recognized cache churn but must not upgrade the historical completeness claim. The same options may accompany `--lifecycle-closeout`, so publication validation and preservation evidence share one coherence result; recovery should reference that durable result rather than rescan broad trees.

Example capture or comparison:

```bash
python3 tools/check_coherence.py --project . \
  --ignored-artifact-policy /path/to/policy.json \
  --ignored-artifact-baseline /path/to/prior-snapshot.json \
  --ignored-artifact-baseline-identity "$CALLER_SUPPLIED_EVIDENCE_IDENTITY" \
  --publication-boundary /path/to/candidate-boundary.json
```

Historical navigation remains summary-first. Reports, decisions, tasks, and final evidence remain institutional memory even when not loaded in normal active context. Use state, handoff, `_SUMMARY.md`, `recover_session.py`, `build_context.py`, context policy, task/decision folders, and targeted search to reach historical evidence. Do not add a parallel historical index or delete reports merely to reduce normal context size.

## Near-quota shutdown priority

When a session is near token, tool, time, or quota exhaustion, continuity beats optional cleanup. Perform these in order:

1. Update the active task artifact with status, outcome so far, and incomplete acceptance criteria.
2. Record blockers, open questions, or approval needs in the active task or an on-demand `question_queue/pending/` file as appropriate.
3. Update `context/latest_handoff.md` with context used, files changed, tests/checks actually run, current blockers, next recommended actions, and exact resume command.
4. Update `state/active_goal.md` and `state/project_state.md` only if their current-state pointers changed.
5. If time remains, refresh affected summaries and run final verification.

Do not spend the last usable budget on broad scans, cosmetic summary rewrites, raw-log reading, optional narrative, or new design work.

## Resume procedure for the next agent

The following user command is sufficient to resume safely:

```text
Recover project state and continue work.
```

When receiving that command, the agent must run or emulate the bounded recovery workflow below before editing files. It should not ask the user to restate project status unless the recovered artifacts reveal a blocking ambiguity.

1. Run `python3 tools/recover_session.py --project . --json` or read the Markdown output.
2. Read the named active/recent task artifact, if any.
3. Read only the decisions and folder summaries relevant to that task.
4. Run `python3 tools/context_health.py --project . --json` or `python3 tools/check_coherence.py --project . --json` when state/handoff freshness is uncertain.
5. Continue from the next recommended action, preserving any recorded blockers or safety boundaries.

## Adoption by existing projects

Existing generated projects are autonomous. They adopt this framework through a project-local governance task or explicit user-approved migration:

- copy or recreate `tools/recover_session.py`;
- add this document under `recovery/continuity_framework.md`;
- update local `AGENTS.md` and `context/context_policy.yaml` with the recovery contract;
- run the project-local recovery smoke check and coherence check;
- record the adoption in local task/state/handoff artifacts.

ProjectForge must not silently mutate an existing project just because the template changed. MacroForge adoption is permitted only because it is explicitly named in the implementation request.
