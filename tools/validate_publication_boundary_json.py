#!/usr/bin/env python3
"""Validate JSON files in an explicit publication boundary.

This is deliberately small: it validates only files supplied by the caller,
and only JSON parseability. It is not a schema/governance framework.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class JsonValidationFailure:
    path: Path
    message: str


def _read_boundary_file(path: Path) -> list[Path]:
    return [Path(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def boundary_paths(paths: Iterable[str], boundary_file: str | None = None) -> list[Path]:
    selected = [Path(p) for p in paths]
    if boundary_file is not None:
        selected.extend(_read_boundary_file(Path(boundary_file)))
    return selected


def json_boundary_files(paths: Iterable[Path]) -> list[Path]:
    return [path for path in paths if path.suffix == ".json"]


def validate_json_file(path: Path) -> JsonValidationFailure | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return JsonValidationFailure(path, f"cannot read file: {exc}")

    decoder = json.JSONDecoder()
    try:
        _, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        return JsonValidationFailure(path, f"invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}")

    if text[end:].strip():
        return JsonValidationFailure(path, "invalid JSON: trailing non-whitespace content after JSON payload")
    return None


def validate_boundary(paths: Iterable[Path]) -> list[JsonValidationFailure]:
    return [failure for path in json_boundary_files(paths) if (failure := validate_json_file(path)) is not None]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate every .json file in an explicit publication boundary.")
    parser.add_argument("paths", nargs="*", help="Publication-boundary paths to scan; only .json files are parsed.")
    parser.add_argument("--boundary-file", help="Newline-delimited publication-boundary path list.")
    args = parser.parse_args(argv)

    selected = boundary_paths(args.paths, args.boundary_file)
    failures = validate_boundary(selected)
    if failures:
        for failure in failures:
            print(f"{failure.path}: {failure.message}", file=sys.stderr)
        return 1
    print(f"json_boundary_validated={len(json_boundary_files(selected))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
