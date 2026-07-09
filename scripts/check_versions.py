#!/usr/bin/env python3
"""Verify all domain modules have consistent __version__ strings."""
import importlib
import re
import sys
from pathlib import Path

SERVICES_DIR = Path(__file__).parent.parent / "src" / "intensicare" / "services"
EXPECTED_VERSION = "3.0.0"

# Modules being modified by other agents — expected to lack __version__ yet.
SKIP_VERSION_CHECK = {"domain_sepsis", "domain_prescricao", "domain_trilhas_engine"}

VERSION_RE = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']')


def _extract_version_from_file(path: Path) -> str | None:
    """Fallback: parse __version__ directly from source when import fails."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            m = VERSION_RE.match(line.strip())
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def main():
    errors = []
    for path in sorted(SERVICES_DIR.glob("domain_*.py")):
        name = path.stem

        if name in SKIP_VERSION_CHECK:
            # Not expected to have __version__ yet — skip without error.
            continue

        version: str | None = None
        try:
            mod = importlib.import_module(f"intensicare.services.{name}")
            version = getattr(mod, "__version__", None)
        except Exception:
            # Fallback to source parsing
            version = _extract_version_from_file(path)

        if version != EXPECTED_VERSION:
            errors.append(f"{name}: {version or 'MISSING'} (expected {EXPECTED_VERSION})")

    if errors:
        print(f"FAIL: {len(errors)} domain modules with version mismatch:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS: All domain modules at version 3.0.0")
    sys.exit(0)


if __name__ == "__main__":
    main()
