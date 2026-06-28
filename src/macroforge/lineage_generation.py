from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from macroforge.db_helpers import jsonb_literal, sql_literal


@dataclass(frozen=True)
class CanonicalLineageEvent:
    """Storage-independent canonical lineage event semantics.

    `row_count_sql` is an already-scoped SQL expression owned by the loader's
    persistence layer. This module defines the converged two-step lineage
    semantics; loaders remain responsible for inserting into storage.
    """

    event_type: str
    from_artifact: str | None
    to_artifact: str
    row_count_sql: str
    details: Mapping[str, Any]
    checksum_sha256: str | None = None


def canonical_lineage_events(
    *,
    raw_artifact_path: str | None,
    staging_artifact: str,
    staging_row_count_sql: str,
    curated_row_count_sql: str,
    details: Mapping[str, Any],
    curated_artifact: str = "curated.fact_observation",
    raw_checksum_sha256: str | None = None,
) -> tuple[CanonicalLineageEvent, CanonicalLineageEvent]:
    """Build the converged raw->staging and staging->curated lineage events.

    This is intentionally narrower than a lineage framework: no source registry,
    no persistence, no graph model, and no source-specific conditionals.
    """

    return (
        CanonicalLineageEvent(
            event_type="raw_to_staging",
            from_artifact=raw_artifact_path,
            to_artifact=staging_artifact,
            checksum_sha256=raw_checksum_sha256,
            row_count_sql=staging_row_count_sql,
            details=details,
        ),
        CanonicalLineageEvent(
            event_type="staging_to_curated",
            from_artifact=staging_artifact,
            to_artifact=curated_artifact,
            checksum_sha256=None,
            row_count_sql=curated_row_count_sql,
            details=details,
        ),
    )


def lineage_values_sql(events: tuple[CanonicalLineageEvent, ...], *, include_checksum: bool) -> str:
    """Render event specs as a VALUES clause for existing loader-owned inserts."""

    rows: list[str] = []
    for event in events:
        fields = [
            sql_literal(event.event_type),
            sql_literal(event.from_artifact),
            sql_literal(event.to_artifact),
        ]
        if include_checksum:
            fields.append(sql_literal(event.checksum_sha256))
        fields.extend([event.row_count_sql, jsonb_literal(dict(event.details))])
        rows.append("      (" + ", ".join(fields) + ")")
    return "VALUES\n" + ",\n".join(rows)
