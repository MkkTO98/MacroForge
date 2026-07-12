from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.validate_publication_boundary_json import validate_boundary, validate_json_file


def test_valid_json_accepted(tmp_path: Path) -> None:
    path = tmp_path / "valid.json"
    path.write_text('{"ok": true}\n', encoding="utf-8")
    assert validate_json_file(path) is None


def test_malformed_json_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"ok": }', encoding="utf-8")
    failure = validate_json_file(path)
    assert failure is not None
    assert "invalid JSON" in failure.message


def test_psql_chatter_before_json_rejected(tmp_path: Path) -> None:
    path = tmp_path / "psql-before.json"
    path.write_text('BEGIN\nSELECT 2\n{"ok": true}\n', encoding="utf-8")
    failure = validate_json_file(path)
    assert failure is not None
    assert "invalid JSON" in failure.message


def test_json_followed_by_trailing_chatter_rejected(tmp_path: Path) -> None:
    path = tmp_path / "psql-after.json"
    path.write_text('{"ok": true}\n(1 row)\nCOMMIT\n', encoding="utf-8")
    failure = validate_json_file(path)
    assert failure is not None
    assert "trailing non-whitespace" in failure.message


def test_unrelated_files_outside_boundary_ignored(tmp_path: Path) -> None:
    valid = tmp_path / "valid.json"
    ignored = tmp_path / "ignored.json"
    valid.write_text('{"ok": true}\n', encoding="utf-8")
    ignored.write_text('not json', encoding="utf-8")
    assert validate_boundary([valid]) == []


def test_paths_containing_spaces_supported_by_boundary_file(tmp_path: Path) -> None:
    path = tmp_path / "path with spaces.json"
    boundary = tmp_path / "boundary.txt"
    path.write_text('{"ok": true}\n', encoding="utf-8")
    boundary.write_text(str(path) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "tools/validate_publication_boundary_json.py", "--boundary-file", str(boundary)],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "json_boundary_validated=1" in result.stdout
