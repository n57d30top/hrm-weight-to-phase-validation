#!/usr/bin/env python3
"""Fail when tracked text artifacts contain local absolute path fragments."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PATTERNS = [
    (b"/" + b"Users" + b"/", "macOS user absolute path"),
    (b"/" + b"home" + b"/", "Linux home absolute path"),
    (b"Desktop" + b"/", "desktop-local path"),
    (b"C:" + bytes([92]), "Windows drive absolute path"),
    (b"file:" + b"//", "file URI"),
]

SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}


def main() -> int:
    paths = _tracked_files()
    findings = []
    for path in paths:
        if not path.is_file() or SKIP_PARTS.intersection(path.parts):
            continue
        data = path.read_bytes()
        for line_number, line in enumerate(data.splitlines(), start=1):
            for pattern, reason in PATTERNS:
                if pattern in line:
                    findings.append(f"{path}:{line_number}: {reason}")

    if findings:
        print("local path hygiene check failed:", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    return 0


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    return [Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]


if __name__ == "__main__":
    raise SystemExit(main())
