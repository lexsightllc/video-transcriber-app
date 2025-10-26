#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Pre-commit helper to insert SPDX-License-Identifier headers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

SPDX_IDENTIFIER = "SPDX-License-Identifier: MPL-2.0"

COMMENT_STYLES = {
    ".py": "#",
    ".sh": "#",
    ".bash": "#",
    ".ps1": "#",
    ".psm1": "#",
    ".psd1": "#",
    ".toml": "#",
    ".cfg": "#",
    ".ini": "#",
    ".yaml": "#",
    ".yml": "#",
    ".json": "#",
    ".env": "#",
    ".txt": "#",
    ".md": "<!-- -->",
}

SPECIAL_CASES = {
    "Makefile": "#",
    "Dockerfile": "#",
}


def render_spdx(style: str) -> tuple[str, str | None]:
    """Return lines to insert for the requested comment style."""

    if style == "<!-- -->":
        return f"<!-- {SPDX_IDENTIFIER} -->", None
    return f"{style} {SPDX_IDENTIFIER}", ""


def determine_style(path: Path, first_line: str) -> str | None:
    """Infer the comment style for a given file."""

    if path.name in SPECIAL_CASES:
        return SPECIAL_CASES[path.name]
    suffix = path.suffix.lower()
    if suffix in COMMENT_STYLES:
        return COMMENT_STYLES[suffix]
    if first_line.startswith("#!"):
        return "#"
    return None


def ensure_spdx(path: Path) -> bool:
    """Ensure the file at *path* contains the SPDX identifier.

    Returns True if a change was made.
    """

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    if SPDX_IDENTIFIER in text:
        return False

    lines = text.splitlines()
    if not lines:
        return False

    style = determine_style(path, lines[0])
    if style is None:
        return False

    spdx_line, extra_blank = render_spdx(style)

    if lines[0].startswith("#!"):
        new_lines = [lines[0], spdx_line]
        if extra_blank is not None:
            new_lines.append(extra_blank)
        new_lines.extend(lines[1:])
    else:
        new_lines = [spdx_line]
        if extra_blank is not None:
            new_lines.append(extra_blank)
        new_lines.extend(lines)

    newline = "\n" if text.endswith("\n") else ""
    path.write_text("\n".join(new_lines) + newline, encoding="utf-8")
    return True


def main(args: Iterable[str]) -> int:
    changed = False
    for arg in args:
        path = Path(arg)
        if not path.is_file():
            continue
        if ensure_spdx(path):
            changed = True
    return 0 if changed or not args else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
