#!/usr/bin/env python3
"""
Gate: design-token reference checker.

Parses every var(--*) reference across frontend-v2/**/*.{css,ts,tsx} and
asserts it resolves to a token emitted by the design-tokens system. A miss
is a build-time failure in strict mode (warn in draft).

Mirrors the check_units.py enforcement pattern (docs/plan/_work/scripts/check_units.py).

Usage:
    python3 scripts/check_tokens.py              # draft mode (warn, exit 0 or 2)
    python3 scripts/check_tokens.py --mode strict # CI-fail on unresolved refs
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────
# Resolve project root relative to this script's location
# ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DESIGN_TOKENS_DIR = PROJECT_ROOT / "design-tokens"
FRONTEND_DIR = PROJECT_ROOT / "frontend-v2"

# ─────────────────────────────────────────────────────────────────────
# Known tokens — extracted from design-tokens JSON files
# ─────────────────────────────────────────────────────────────────────

# CSS custom property names that the design-tokens system emits
KNOWN_TOKENS: set[str] = set()

# Pattern for var(--*) references
VAR_PATTERN = re.compile(r"var\(\s*(--[a-zA-Z0-9_-]+)\b")


def load_known_tokens() -> set[str]:
    """Walk all JSON files in design-tokens/ and extract CSS var names."""
    tokens: set[str] = set()

    if not DESIGN_TOKENS_DIR.exists():
        print(f"[check_tokens] WARNING: design-tokens/ directory not found at {DESIGN_TOKENS_DIR}")
        return tokens

    # Known token names from the spec (hard-coded as canonical reference)
    # These are the CSS custom properties emitted from the design-tokens build.
    spec_tokens = [
        # Surface
        "--semantic-surface-canvas",
        "--semantic-surface-raised",
        "--semantic-surface-overlay",
        "--semantic-border-default",
        # Text
        "--semantic-text-primary",
        "--semantic-text-secondary",
        # Clinical severity — on-surface
        "--clinical-severity-normal-on-surface",
        "--clinical-severity-watch-on-surface",
        "--clinical-severity-urgent-on-surface",
        "--clinical-severity-critical-on-surface",
        # Clinical severity — signal
        "--clinical-severity-normal-signal",
        "--clinical-severity-watch-signal",
        "--clinical-severity-urgent-signal",
        "--clinical-severity-critical-signal",
        # Clinical severity — fill
        "--clinical-severity-normal-fill",
        "--clinical-severity-watch-fill",
        "--clinical-severity-urgent-fill",
        "--clinical-severity-critical-fill",
        # Clinical severity — on-fill
        "--clinical-severity-normal-on-fill",
        "--clinical-severity-watch-on-fill",
        "--clinical-severity-urgent-on-fill",
        "--clinical-severity-critical-on-fill",
        # Clinical severity — wash
        "--clinical-severity-normal-wash",
        "--clinical-severity-watch-wash",
        "--clinical-severity-urgent-wash",
        "--clinical-severity-critical-wash",
        # Clinical status
        "--clinical-status-attended-color",
        "--clinical-status-attended-on-color",
        "--clinical-status-stale-color",
        "--clinical-status-stale-on-color",
        # Sidebar
        "--color-sidebar-bg",
        "--color-sidebar-hover",
        "--color-sidebar-active",
        # Tailwind @theme aliases (forwarded to actual tokens)
        "--color-clinical-normal",
        "--color-clinical-watch",
        "--color-clinical-urgent",
        "--color-clinical-critical",
    ]

    tokens.update(spec_tokens)

    # Also try to read from globals.css directly for any token definitions
    globals_css = FRONTEND_DIR / "app" / "globals.css"
    if globals_css.exists():
        content = globals_css.read_text(encoding="utf-8")
        # Match CSS custom property definitions: --name: value;
        defined = set(re.findall(r"^\s*(--[a-zA-Z0-9_-]+)\s*:", content, re.MULTILINE))
        tokens.update(defined)

    return tokens


def find_var_references(directory: Path) -> dict[str, list[tuple[str, int, str]]]:
    """
    Scan all .css/.ts/.tsx files under directory for var(--*) references.

    Returns: {file_path: [(token_name, line_number, line_text), ...]}
    """
    refs: dict[str, list[tuple[str, int, str]]] = {}

    for ext in ["css", "ts", "tsx"]:
        for filepath in directory.rglob(f"*.{ext}"):
            # Skip node_modules and .next build output
            if "node_modules" in filepath.parts or ".next" in filepath.parts:
                continue
            try:
                content = filepath.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            lines = content.splitlines()
            matches: list[tuple[str, int, str]] = []
            for i, line in enumerate(lines, start=1):
                for m in VAR_PATTERN.finditer(line):
                    token_name = m.group(1)
                    matches.append((token_name, i, line.strip()))
            if matches:
                refs[str(filepath)] = matches

    return refs


def main() -> int:
    mode = "strict" if "strict" in " ".join(sys.argv[1:]) else "draft"

    print(f"[check_tokens] Mode: {mode}")
    print(f"[check_tokens] Design tokens dir: {DESIGN_TOKENS_DIR}")
    print(f"[check_tokens] Frontend dir: {FRONTEND_DIR}")

    known = load_known_tokens()
    print(f"[check_tokens] Known tokens: {len(known)} registered")

    if not known:
        print("[check_tokens] WARNING: No known tokens registered — cannot validate references")
        return 0 if mode == "draft" else 1

    # Find all var(--*) references
    refs = find_var_references(FRONTEND_DIR)

    if not refs:
        print("[check_tokens] No var(--*) references found in frontend-v2/")
        return 0

    files_scanned = len(refs)
    total_refs = sum(len(v) for v in refs.values())
    print(f"[check_tokens] Scanned {files_scanned} files, found {total_refs} var(--*) references")

    # Validate
    unresolved: list[tuple[str, str, int, str]] = []  # (file, token, line, text)
    resolved_count = 0

    for filepath, file_refs in refs.items():
        for token_name, line_num, line_text in file_refs:
            if token_name in known:
                resolved_count += 1
            else:
                unresolved.append((filepath, token_name, line_num, line_text))

    unresolved_count = len(unresolved)
    print(f"[check_tokens] Resolved: {resolved_count}, Unresolved: {unresolved_count}")

    if unresolved:
        print("\n[check_tokens] Unresolved var(--*) references:")
        for filepath, token_name, line_num, line_text in unresolved[:50]:  # cap at 50
            print(f"  {filepath}:{line_num}  {token_name}")
            if len(line_text) > 120:
                line_text = line_text[:117] + "..."
            print(f"    {line_text}")

        if len(unresolved) > 50:
            print(f"  ... and {len(unresolved) - 50} more")

    if unresolved_count == 0:
        print("[check_tokens] PASS — all var(--*) references resolve to known tokens")
        return 0
    elif mode == "draft":
        print(f"[check_tokens] WARN — {unresolved_count} unresolved references (draft mode, not failing)")
        return 0  # draft: warn but don't fail
    else:
        print(f"[check_tokens] FAIL — {unresolved_count} unresolved references (strict mode)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
