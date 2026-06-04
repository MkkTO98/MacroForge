# DEC-001 — Import Precedence and Reconstruction

Status: Accepted
Date: 2026-06-02

## Decision

MacroForge will be rebuilt as a fresh ProjectForge-managed project using curated reconstruction evidence. Raw ChatGPT exports, old scaffold archives, and deleted prior implementation files are evidence only, not canonical project truth.

## Precedence

1. Current user instruction and current MacroForge artifacts.
2. Curated reconstruction docs in `context/reconstruction/`.
3. ProjectForge setup answers and generated setup decisions.
4. Historical exports/scaffold archives as evidence only.
5. Deleted old implementation artifacts as historical design evidence only.

## Consequences

- Do not blindly restore deleted schema/WDI files.
- Promote recovered facts into docs, decisions, state, and tasks before implementation.
- Keep raw exports out of normal context and git unless a later explicit recovery decision says otherwise.
