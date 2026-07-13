#!/usr/bin/env python3
"""Architecture-to-Reality Audit for ProjectForge projects.

This is a lightweight automated drift detector. It does not replace human or
cloud-governance review; it creates an evidence-backed checklist and catches the
mechanical cases that routinely cause architecture/governance drift.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

AUDIT_CATEGORIES = [
    "architecture_vs_implementation",
    "state_files_vs_reality",
    "agent_instructions_vs_behavior",
    "logging_systems",
    "context_management_systems",
    "governance_processes",
    "automation_workflows",
    "templates_vs_generated_projects",
]

DRIFT_TYPES = [
    "drift",
    "obsolete_documentation",
    "duplicated_systems",
    "unused_systems",
    "missing_implementation",
    "implementation_without_documentation",
    "documentation_without_implementation",
]

REQUIRED_PROCESS_PHRASES = [
    "Architecture-to-Reality Audit",
    "every 5-10 completed tasks",
    "before major architecture changes",
    "before major governance reviews",
]

ROOT_TOOL_REQUIRED = [
    "tools/check_coherence.py",
    "tools/context_health.py",
    "tools/build_context.py",
    "tools/architecture_reality_audit.py",
]

GENERATED_TOOL_REQUIRED = [
    "tools/check_coherence.py",
    "tools/context_health.py",
    "tools/build_context.py",
    "tools/architecture_reality_audit.py",
]

POLICY_FILES = [
    "CONSTITUTION.md",
    "AGENTS.md",
    "context/context_policy.yaml",
    "docs/OPERATOR_MANUAL.md",
    "automation/orchestration_schedule.yaml",
]

TEMPLATE_POLICY_FILES = [
    "templates/_shared_project/AGENTS.md",
    "templates/_shared_project/context/context_policy.yaml",
    "templates/_shared_project/instructions/GENERAL_INSTRUCTIONS.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def has(path: Path, text: str) -> bool:
    return text.lower() in read(path).lower()


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4) if text else 0


def add(items: list[dict[str, str]], severity: str, category: str, drift_type: str, message: str, remediation: str) -> None:
    items.append({
        "severity": severity,
        "category": category,
        "drift_type": drift_type,
        "message": message,
        "remediation": remediation,
    })


def latest_architecture_audit(project: Path) -> Path | None:
    reports = sorted((project / "artifacts" / "reports").glob("R-*-architecture-reality-audit.md"))
    return reports[-1] if reports else None


def project_identity(project: Path) -> str:
    project_yaml = read(project / "project.yaml")
    match = re.search(r'^\s*name:\s*["\']?([^"\'\n]+)', project_yaml, flags=re.M)
    return match.group(1).strip() if match else project.name


def artifact_date(path: Path | None) -> dt.date | None:
    if path is None:
        return None
    match = re.search(r"(20\d{6})", path.name)
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def parse_date_token(value: str) -> dt.date | None:
    value = value.strip()
    for pattern, fmt in ((r"(20\d{2}-\d{2}-\d{2})", "%Y-%m-%d"), (r"(20\d{6})", "%Y%m%d")):
        match = re.search(pattern, value)
        if not match:
            continue
        try:
            return dt.datetime.strptime(match.group(1), fmt).date()
        except ValueError:
            continue
    return None


def explicit_task_completion_date(text: str) -> dt.date | None:
    patterns = [
        r"(?im)^\s*(?:completed|completed_at|completed_on|completion_date|date_completed|closed|closed_at|finished)\s*[:=]\s*([^\n#]+)",
        r"(?im)^\s*status\s*[:=]\s*completed\s+on\s+([^\n#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            parsed = parse_date_token(match.group(1))
            if parsed:
                return parsed
    return None


def task_filename_date(path: Path) -> dt.date | None:
    # Authoritative only for task identities that explicitly embed a YYYYMMDD date token.
    return parse_date_token(path.stem)


def tracked_file_commit_date(project: Path, path: Path) -> dt.date | None:
    try:
        rel = path.relative_to(project)
    except ValueError:
        rel = path
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(rel)],
            cwd=project,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except Exception:
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        return dt.date.fromisoformat(proc.stdout.strip().splitlines()[0])
    except ValueError:
        return None


def task_date_evidence(project: Path, task: Path, text: str, *, allow_mtime: bool) -> tuple[dt.date | None, str]:
    explicit = explicit_task_completion_date(text)
    if explicit:
        return explicit, "explicit_completion_date"
    named = task_filename_date(task)
    if named:
        return named, "dated_task_filename"
    committed = tracked_file_commit_date(project, task)
    if committed:
        return committed, "git_last_commit_date"
    if allow_mtime:
        return dt.date.fromtimestamp(task.stat().st_mtime), "legacy_mtime_fallback"
    return None, "unknown"


def completed_tasks_since(project: Path, since: Path | None) -> dict[str, Any]:
    since_date = artifact_date(since)
    allow_mtime = since is not None and since.exists() and since_date is None
    since_mtime_date = dt.date.fromtimestamp(since.stat().st_mtime) if allow_mtime else None
    known_after: list[dict[str, str]] = []
    known_before_or_on: list[dict[str, str]] = []
    unknown: list[dict[str, str]] = []
    modes: set[str] = set()
    for task in (project / "artifacts" / "tasks").glob("*.md"):
        if task.name == "_SUMMARY.md":
            continue
        raw = read(task)
        text = raw.lower()
        if not ("status: completed" in text or "status: done" in text or "completed:" in text):
            continue
        task_date, mode = task_date_evidence(project, task, raw, allow_mtime=allow_mtime)
        modes.add(mode)
        rel = str(task.relative_to(project))
        item = {"path": rel, "evidence_mode": mode}
        if task_date is not None:
            item["date"] = task_date.isoformat()
        if since_date is not None:
            if task_date is None:
                unknown.append(item)
            elif task_date > since_date:
                known_after.append(item)
            else:
                known_before_or_on.append(item)
        elif since_mtime_date is not None:
            item["audit_mtime_date"] = since_mtime_date.isoformat()
            if task_date is None:
                unknown.append(item)
            elif task_date >= since_mtime_date:
                known_after.append(item)
            else:
                known_before_or_on.append(item)
        else:
            unknown.append(item)
    ordered_modes = sorted(modes) if modes else []
    return {
        "known_completed_tasks_after_latest_audit": len(known_after),
        "completed_tasks_since_latest_audit": len(known_after),
        "completed_tasks_unknown_temporal_position": len(unknown),
        "cadence_fully_determined": not unknown,
        "cadence_evidence_mode": ",".join(ordered_modes) if ordered_modes else "no_completed_tasks",
        "known_after_tasks": known_after,
        "known_before_or_on_tasks": known_before_or_on,
        "unknown_temporal_tasks": unknown,
    }


def detect_mode(project: Path) -> str:
    return "root" if (project / "projectforge.yaml").exists() else "generated"


def check_process_documented(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    files = POLICY_FILES if mode == "root" else ["AGENTS.md", "context/context_policy.yaml", "instructions/GENERAL_INSTRUCTIONS.md"]
    combined = "\n".join(read(project / rel) for rel in files)
    for phrase in REQUIRED_PROCESS_PHRASES:
        if phrase.lower() not in combined.lower():
            add(
                findings,
                "block" if phrase == "Architecture-to-Reality Audit" else "warn",
                "governance_processes",
                "documentation_without_implementation",
                f"Architecture audit process phrase missing from policy/instructions: {phrase}",
                "Document the Architecture-to-Reality Audit cadence, triggers, recording location, and remediation workflow in AGENTS/context policy/operator instructions.",
            )


def check_tools_and_automation(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    required = ROOT_TOOL_REQUIRED if mode == "root" else GENERATED_TOOL_REQUIRED
    for rel in required:
        if not (project / rel).exists():
            add(findings, "block", "automation_workflows", "missing_implementation", f"Required audit/coherence tool missing: {rel}", "Copy the current ProjectForge tool from templates or restore it before relying on automated governance checks.")

    if mode == "root":
        schedule = project / "automation" / "orchestration_schedule.yaml"
        if not has(schedule, "architecture_reality_audit"):
            add(findings, "block", "automation_workflows", "missing_implementation", "orchestration schedule does not run architecture_reality_audit", "Add Architecture-to-Reality Audit to periodic and pre-major-governance automation.")
        hygiene = project / "tools" / "orchestrator_hygiene.py"
        if not has(hygiene, "architecture_reality_audit.py"):
            add(findings, "warn", "automation_workflows", "implementation_without_documentation", "orchestrator_hygiene.py does not invoke architecture_reality_audit.py", "Add the audit command to periodic/all hygiene phases so routine automation can execute it.")


def check_context_and_state(project: Path, findings: list[dict[str, str]]) -> None:
    state_files = ["state/active_goal.md", "state/project_state.md", "state/architecture.md"]
    for rel in state_files:
        p = project / rel
        if not p.exists():
            add(findings, "block", "state_files_vs_reality", "missing_implementation", f"Missing primary state file: {rel}", "Restore the primary state artifact or regenerate the project scaffold.")
            continue
        text = read(p)
        if estimate_tokens(text) > 3500:
            add(findings, "warn", "state_files_vs_reality", "drift", f"{rel} is large for a current-state artifact (~{estimate_tokens(text)} tokens)", "Summarize current truth in state and move history/evidence to task artifacts, reports, handoffs, or derived logs.")
        historical_markers = len(re.findall(r"\b(completed|implemented|verification|changed files|diff|commit|log)\b", text, flags=re.I))
        if historical_markers > 20:
            add(findings, "warn", "state_files_vs_reality", "obsolete_documentation", f"{rel} appears to accumulate implementation history", "Keep only active/current pointers in state; move historical details to reports or task artifacts.")

    if not has(project / "context" / "context_policy.yaml", "context_loading_hierarchy"):
        add(findings, "block", "context_management_systems", "documentation_without_implementation", "context policy lacks explicit context_loading_hierarchy", "Upgrade context/context_policy.yaml from current ProjectForge templates.")
    if not has(project / "context" / "context_policy.yaml", "architecture_reality_audit"):
        add(findings, "warn", "governance_processes", "documentation_without_implementation", "context policy lacks Architecture-to-Reality Audit governance settings", "Add architecture_reality_audit policy with cadence, categories, and report location.")


def declares_responsibility(project: Path, responsibility: str) -> bool:
    tokens = {
        "agent_role_instructions": [
            "owns_agent_role_instructions: true",
            "agent_role_instructions: required",
            "requires_agent_role_instructions: true",
            "macroforge owns agent role instructions",
        ],
        "metrics_policy": [
            "owns_metrics_policy: true",
            "metrics_policy: required",
            "requires_metrics_policy: true",
            "macroforge owns project-local metrics policy",
        ],
    }[responsibility]
    files = [
        project / "project.yaml",
        project / "CONSTITUTION.md",
        project / "AGENTS.md",
        project / "state" / "architecture.md",
        project / "context" / "context_policy.yaml",
        project / "architecture" / "architecture_state.md",
    ]
    combined = "\n".join(read(path).lower() for path in files if path.exists())
    return any(token in combined for token in tokens)


def check_agent_instruction_alignment(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    agent_files = list((project / "agents").glob("*.md")) if (project / "agents").exists() else []
    owns_agents = declares_responsibility(project, "agent_role_instructions")
    if not agent_files:
        if owns_agents:
            add(findings, "warn", "agent_instructions_vs_behavior", "missing_implementation", "Declared agent-role instruction responsibility has no role files under agents/", "Either restore owned role instruction files or remove the declared responsibility.")
        return
    for p in agent_files:
        if p.name.startswith("_"):
            continue
        txt = read(p).lower()
        if "context used" not in txt:
            add(findings, "warn", "agent_instructions_vs_behavior", "drift", f"{p.relative_to(project)} does not require Context used reporting", "Update owned role prompt or remove the project-local role-instruction responsibility.")
        if "architecture-to-reality" not in txt and p.name in {"auditor.md", "reviewer.md", "planner.md"}:
            add(findings, "warn", "agent_instructions_vs_behavior", "documentation_without_implementation", f"{p.relative_to(project)} does not mention Architecture-to-Reality Audit triggers", "Add audit-trigger guidance to owned governance/review/planning roles.")


def check_logging_and_metrics(project: Path, findings: list[dict[str, str]]) -> None:
    if not has(project / "logs" / "logging_policy.yaml", "raw"):
        add(findings, "warn", "logging_systems", "obsolete_documentation", "logging policy does not clearly define raw operational logs", "Clarify logs/raw vs logs/derived separation in logs/logging_policy.yaml.")
    if declares_responsibility(project, "metrics_policy") and not has(project / "metrics" / "metrics_policy.yaml", "derived"):
        add(findings, "warn", "logging_systems", "obsolete_documentation", "Declared metrics-policy responsibility is missing or does not clearly define metrics as derived evidence", "Clarify the owned metrics policy as derived evidence or remove the declared responsibility.")


def check_templates(project: Path, mode: str, findings: list[dict[str, str]]) -> None:
    if mode != "root":
        return
    for rel in TEMPLATE_POLICY_FILES:
        if not (project / rel).exists():
            add(findings, "block", "templates_vs_generated_projects", "missing_implementation", f"Template policy file missing: {rel}", "Restore shared generated-project template file.")
            continue
        if not has(project / rel, "Architecture-to-Reality Audit"):
            add(findings, "block", "templates_vs_generated_projects", "documentation_without_implementation", f"Template does not inherit Architecture-to-Reality Audit guidance: {rel}", "Patch shared template so future generated projects inherit the audit process.")
    for rel in ["templates/_shared_project/tools/architecture_reality_audit.py", "templates/_shared_project/tools/check_coherence.py"]:
        if not (project / rel).exists():
            add(findings, "block", "templates_vs_generated_projects", "missing_implementation", f"Generated-project template missing tool: {rel}", "Copy root tool into templates/_shared_project/tools/.")


def check_architecture_docs(project: Path, findings: list[dict[str, str]]) -> None:
    arch = project / "state" / "architecture.md"
    if not arch.exists():
        return
    arch_text = read(arch).lower()
    implementation_markers = ["tools/", "context/", "agents/", "templates/", "logs/", "metrics/"]
    missing = [m for m in implementation_markers if m.rstrip("/") in arch_text and not (project / m).exists()]
    for marker in missing:
        add(findings, "warn", "architecture_vs_implementation", "documentation_without_implementation", f"architecture.md references {marker} but path is missing", "Either restore the implementation path or update architecture.md to reflect current reality.")
    if "architecture-to-reality" in "\n".join(read(project / rel) for rel in POLICY_FILES if (project / rel).exists()).lower() and not (project / "tools" / "architecture_reality_audit.py").exists():
        add(findings, "block", "architecture_vs_implementation", "documentation_without_implementation", "Architecture-to-Reality Audit is documented but the tool is missing", "Restore tools/architecture_reality_audit.py.")


def check(project: Path) -> dict[str, Any]:
    project = project.resolve()
    mode = detect_mode(project)
    findings: list[dict[str, str]] = []
    latest = latest_architecture_audit(project)
    cadence = completed_tasks_since(project, latest)
    completed = cadence["completed_tasks_since_latest_audit"]
    unknown_completed = cadence["completed_tasks_unknown_temporal_position"]

    check_process_documented(project, mode, findings)
    check_tools_and_automation(project, mode, findings)
    check_context_and_state(project, findings)
    check_agent_instruction_alignment(project, mode, findings)
    check_logging_and_metrics(project, findings)
    check_templates(project, mode, findings)
    check_architecture_docs(project, findings)

    if completed >= 10:
        add(findings, "block", "governance_processes", "drift", f"{completed} completed task(s) since last Architecture-to-Reality Audit", "Run and record an Architecture-to-Reality Audit before continuing major work.")
    elif completed >= 5:
        add(findings, "warn", "governance_processes", "drift", f"{completed} completed task(s) since last Architecture-to-Reality Audit", "Schedule an Architecture-to-Reality Audit soon; cadence is every 5-10 completed tasks.")
    if unknown_completed:
        add(findings, "warn", "governance_processes", "drift", f"{unknown_completed} completed task artifact(s) have unknown temporal position relative to latest Architecture-to-Reality Audit", "Record explicit completion dates, commit the task artifacts, or run a fresh audit after resolving cadence indeterminacy.")

    blocks = [f for f in findings if f["severity"] == "block"]
    warnings = [f for f in findings if f["severity"] == "warn"]
    return {
        "project": project_identity(project),
        "mode": mode,
        "timestamp": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "audit_categories": AUDIT_CATEGORIES,
        "drift_types": DRIFT_TYPES,
        "latest_architecture_reality_audit": str(latest.relative_to(project)) if latest else None,
        "completed_tasks_since_latest_audit": completed,
        "known_completed_tasks_after_latest_audit": cadence["known_completed_tasks_after_latest_audit"],
        "completed_tasks_unknown_temporal_position": unknown_completed,
        "cadence_evidence_mode": cadence["cadence_evidence_mode"],
        "cadence_fully_determined": cadence["cadence_fully_determined"],
        "cadence_known_after_tasks": cadence["known_after_tasks"],
        "cadence_unknown_temporal_tasks": cadence["unknown_temporal_tasks"],
        "blocks": blocks,
        "warnings": warnings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Architecture-to-Reality Audit",
        "",
        f"Date: {report['timestamp']}",
        f"Project: {report['project']}",
        f"Mode: {report['mode']}",
        f"Latest previous audit: {report['latest_architecture_reality_audit'] or 'none'}",
        f"Completed tasks since latest audit: {report['completed_tasks_since_latest_audit']}",
        f"Completed tasks with unknown temporal position: {report.get('completed_tasks_unknown_temporal_position', 0)}",
        f"Cadence evidence mode: {report.get('cadence_evidence_mode', 'unknown')}",
        f"Cadence fully determined: {report.get('cadence_fully_determined', False)}",
        "",
        "## Scope",
        "",
        "This audit checks documented architecture, governance rules, operating procedures, state artifacts, templates, automation, logging/context systems, and available implementation for drift.",
        "",
        "## Categories",
        "",
    ]
    lines.extend(f"- {cat}" for cat in report["audit_categories"])
    lines.extend(["", "## Drift types", ""])
    lines.extend(f"- {kind}" for kind in report["drift_types"])
    for title, key in [("Blocks", "blocks"), ("Warnings", "warnings")]:
        lines.extend(["", f"## {title}", ""])
        if not report[key]:
            lines.append("None.")
        for item in report[key]:
            lines.extend([
                f"- Category: {item['category']}",
                f"  Drift type: {item['drift_type']}",
                f"  Finding: {item['message']}",
                f"  Remediation: {item['remediation']}",
            ])
    lines.extend([
        "",
        "## Remediation workflow",
        "",
        "1. Fix blocks before major architecture/governance work continues.",
        "2. Convert durable policy or architecture changes into decision artifacts.",
        "3. Update implementation, templates, docs, and state together so future projects inherit the correction.",
        "4. Refresh affected folder summaries and latest handoff.",
        "5. Rerun `tools/architecture_reality_audit.py`, `tools/check_coherence.py`, and relevant tests.",
    ])
    return "\n".join(lines) + "\n"


def write_report(project: Path, report: dict[str, Any]) -> Path:
    today = dt.date.today().isoformat().replace("-", "")
    out = project / "artifacts" / "reports" / f"R-{today}-architecture-reality-audit.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(report), encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Run ProjectForge Architecture-to-Reality Audit.")
    ap.add_argument("--project", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-report", action="store_true", help="Write artifacts/reports/R-YYYYMMDD-architecture-reality-audit.md")
    ns = ap.parse_args()

    project = Path(ns.project).resolve()
    report = check(project)
    report_path = None
    if ns.write_report:
        report_path = write_report(project, report)
        report["report_path"] = str(report_path)

    if ns.json:
        print(json.dumps(report, indent=2))
    else:
        if report_path:
            print(f"Report: {report_path}")
        for item in report["blocks"]:
            print(f"BLOCK: {item['message']}", file=sys.stderr)
        for item in report["warnings"]:
            print(f"WARN: {item['message']}")
        print(f"architecture-reality-audit: {len(report['blocks'])} block(s), {len(report['warnings'])} warning(s)")
    return 2 if report["blocks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
