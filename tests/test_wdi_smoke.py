from __future__ import annotations

from pathlib import Path

from macroforge import wdi_smoke


class FakeRunner:
    def __init__(self):
        self.commands: list[list[str]] = []
        self.dropped: list[str] = []

    def run(self, command, **kwargs):
        self.commands.append(list(command))

    def dropdb(self, db_name: str) -> None:
        self.dropped.append(db_name)


def test_isolated_smoke_plan_uses_unique_non_live_database_and_required_steps(tmp_path):
    plan = wdi_smoke.build_smoke_plan(project_root=tmp_path, db_name="macroforge_wdi_smoke_test")

    assert plan.db_name == "macroforge_wdi_smoke_test"
    assert plan.db_name != "macro"
    assert plan.migration_paths == (
        tmp_path / "db" / "migrations" / "001_v0_schema_foundation.sql",
        tmp_path / "db" / "migrations" / "003_canonical_domain_dimensions.sql",
    )
    assert plan.normalized_path == tmp_path / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"
    assert plan.run_key.startswith("wdi-smoke-rerun-")


def test_run_isolated_smoke_executes_create_migrate_double_load_validate_and_cleanup(tmp_path):
    runner = FakeRunner()

    result = wdi_smoke.run_isolated_smoke(
        project_root=tmp_path,
        db_name="macroforge_wdi_smoke_test",
        runner=runner,
    )

    command_text = [" ".join(command) for command in runner.commands]
    assert command_text[0] == "createdb macroforge_wdi_smoke_test"
    assert "psql -v ON_ERROR_STOP=1 -d macroforge_wdi_smoke_test -f" in command_text[1]
    assert "001_v0_schema_foundation.sql" in command_text[1]
    assert "psql -v ON_ERROR_STOP=1 -d macroforge_wdi_smoke_test -f" in command_text[2]
    assert "003_canonical_domain_dimensions.sql" in command_text[2]
    assert sum("macroforge.wdi_loader" in text for text in command_text) == 2
    assert any("macroforge.wdi_validation" in text for text in command_text)
    assert runner.dropped == ["macroforge_wdi_smoke_test"]
    assert result["status"] == "succeeded"
    assert result["database"] == "macroforge_wdi_smoke_test"
    assert result["loader_runs"] == 2


def test_run_isolated_smoke_refuses_live_macro_database(tmp_path):
    runner = FakeRunner()

    try:
        wdi_smoke.run_isolated_smoke(project_root=tmp_path, db_name="macro", runner=runner)
    except ValueError as exc:
        assert "live `macro` database" in str(exc)
    else:
        raise AssertionError("expected live database refusal")

    assert runner.commands == []
    assert runner.dropped == []
