from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CLEAN_CLONE_FIXTURES = [
    PROJECT_ROOT / "data" / "raw" / "oecd_sdmx" / "oecd_sdmx_naag_2020_2021_raw.xml",
    PROJECT_ROOT / "data" / "raw" / "oecd_sdmx" / "oecd_sdmx_naag_structure_20260604.xml",
    PROJECT_ROOT / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json",
    PROJECT_ROOT / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-codelist-labels-20260604.json",
    PROJECT_ROOT / "data" / "raw" / "eurostat" / "eurostat-namq-10-gdp-2023q1-2023q2-raw.json",
    PROJECT_ROOT / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json",
]


def test_required_oecd_and_eurostat_fixture_files_exist_and_are_not_gitignored():
    missing = [path.relative_to(PROJECT_ROOT).as_posix() for path in REQUIRED_CLEAN_CLONE_FIXTURES if not path.exists()]
    assert missing == []

    ignored: list[str] = []
    for path in REQUIRED_CLEAN_CLONE_FIXTURES:
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", relative],
            cwd=PROJECT_ROOT,
            text=True,
        )
        if result.returncode == 0:
            ignored.append(relative)
        else:
            assert result.returncode == 1

    assert ignored == []
