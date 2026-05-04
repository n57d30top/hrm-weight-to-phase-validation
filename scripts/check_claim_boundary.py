#!/usr/bin/env python3
"""Fail when public docs/reports contain unsupported positive claims."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = [
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "dashboard",
    ROOT / "reports" / "future-work" / "hrm-neural-mapping",
]

STRICT_FALSE_FLAGS = {
    "hardwareValidated",
    "foundryCalibrated",
    "measuredTransferMatrixAvailable",
    "productionInferenceReady",
}

FORBIDDEN_POSITIVE_PHRASES = [
    "hardware validated",
    "foundry calibrated",
    "measured transfer matrix available",
    "production inference ready",
    "quantum advantage",
    "hardware-native intelligence",
    "power-free computation",
    "optical nonlinearities implemented",
]

NEGATIVE_CONTEXT_MARKERS = [
    "does not claim",
    "do not claim",
    "not claim",
    "not hardware evidence",
    "no ",
    "false",
    "blocked",
    "missing",
    "unless",
    "without",
    "is not",
    "are not",
    "not a",
    "not evidence",
    "should not",
    "claim boundary",
    "whatnottoclaim",
    "does not attempt",
]


def main(paths: Iterable[Path] | None = None) -> int:
    findings: List[str] = []
    for path in _iter_public_files(paths):
        findings.extend(check_file(path))
    if findings:
        print("claim-boundary check failed:", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    return 0


def check_file(path: Path) -> List[str]:
    findings: List[str] = []
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        findings.extend(check_json_flags(path, text))
    findings.extend(check_text_for_forbidden_claims(path, text))
    return findings


def check_json_flags(path: Path, text: str) -> List[str]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    findings: List[str] = []
    for location, key, value in _walk_json(data):
        if key in STRICT_FALSE_FLAGS and value is True:
            findings.append(f"{_relative(path)}:{location}: unsupported {key}=true")
    return findings


def check_text_for_forbidden_claims(path: Path, text: str) -> List[str]:
    findings: List[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        lower_line = line.lower()
        context = "\n".join(lines[max(0, index - 8):index + 1]).lower()
        for phrase in FORBIDDEN_POSITIVE_PHRASES:
            if phrase in lower_line and not _has_negative_context(context):
                findings.append(f"{_relative(path)}:{index + 1}: unsupported positive claim phrase: {phrase}")
    return findings


def _iter_public_files(paths: Iterable[Path] | None) -> List[Path]:
    roots = list(paths) if paths is not None else PUBLIC_PATHS
    files: List[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix in {".html", ".md", ".json", ".csv", ".txt"}:
                    files.append(path)
    return sorted(files)


def _walk_json(value: Any, prefix: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{prefix}.{key}"
            yield location, key, child
            yield from _walk_json(child, location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_json(child, f"{prefix}[{index}]")


def _has_negative_context(context: str) -> bool:
    return any(marker in context for marker in NEGATIVE_CONTEXT_MARKERS)


def _relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
