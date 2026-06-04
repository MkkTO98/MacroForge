# Architecture Assessment

## Assessment

The strongest path is to map historical MacroForge AI-project concepts into ProjectForge-native folders rather than recreating a separate legacy `ai/` hierarchy.

ProjectForge handles:

- state;
- context summaries;
- decisions;
- tasks;
- handoffs;
- logs and run evidence;
- agent instructions and permissions.

MacroForge domain code should focus on:

- data extraction;
- raw evidence preservation;
- PostgreSQL migrations;
- staging/curated loading;
- validation;
- reproducible reports and future research products.

## Main risks

- Context/token bloat from importing raw chat exports or old scaffold zips.
- Premature generalization before at least one real source is implemented and verified.
- Under-specified DB environment/secrets.
- Confusion between historical completed tasks and current live state after deletion.
- Overbuilt wrapper/agent system before recurring commands are understood.

## Simplifications accepted for v1

- WDI first.
- Raw SQL migrations before Alembic.
- Manual/local pipeline runs before schedulers.
- ProjectForge-native operating artifacts.
- Compact recovery summaries rather than raw full exports.
