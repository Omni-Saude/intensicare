#!/usr/bin/env python3
"""Detects OpenAPI contract drift between the live FastAPI app and docs/contracts/.

Sprint 3 sepsis governance (Dim A audit finding: 38% of live endpoints — 31 of
81 — had no OpenAPI contract). This script closes the loop by treating the
live app spec (`app.openapi()`) as the source of truth and failing CI when a
live endpoint has no matching contract declaration ("orphan").

Design:
  * Imports `intensicare.main:app` and calls `app.openapi()` directly — no
    running server / network calls required, so it is safe to run in CI
    without spinning up postgres/redis first.
  * Reads every `docs/contracts/*.yaml` file, resolves each file's `servers[0].url`
    (relative base path, e.g. `/api/v1`, or empty for absolute-path files) and
    builds the set of (METHOD, full_path) operations the contracts declare.
  * Path parameters are normalized (`{mpi_id}` -> `{}`) so that contracts using
    different parameter names than the live spec (e.g. `{id}` vs
    `{evolution_id}`) still match.
  * Operations marked `x-status: not-implemented` in a contract are excluded
    from the "contracted" set — they are intentionally-documented phantom
    operations (contracted but not yet built) and must not mask real orphans
    nor be misread as coverage.
  * Exits 1 (and prints the orphan list) if any live operation has no
    contract coverage. Exits 0 otherwise.

Usage:
    PYTHONPATH=src python3 scripts/ci/check_openapi_drift.py
"""

from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_GLOB = str(REPO_ROOT / "docs" / "contracts" / "*.yaml")
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def normalize_params(path: str) -> str:
    """Replace `{anything}` path params with `{}` so contracts and the live
    spec can use different parameter names and still be considered a match."""
    return re.sub(r"\{[^}]+\}", "{}", path)


def load_live_operations() -> set[tuple[str, str]]:
    """Import the FastAPI app and extract its live (METHOD, normalized-path)
    operations. Does not require a running server, DB, or Redis connection —
    `app.openapi()` only inspects route declarations."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from intensicare.main import app  # noqa: PLC0415

    spec = app.openapi()
    ops: set[tuple[str, str]] = set()
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method.lower() in HTTP_METHODS:
                ops.add((method.upper(), normalize_params(path)))
    return ops


def contract_base_path(contract: dict) -> str:
    """Return the relative base path declared by a contract's first server
    entry, or '' if the server is an absolute/external URL (in which case the
    contract's paths are expected to already be absolute, e.g. `/api/v1/...`)."""
    servers = contract.get("servers") or []
    if not servers:
        return ""
    url = servers[0].get("url", "")
    if url.startswith("http://") or url.startswith("https://"):
        return ""
    return url


def load_contracted_operations() -> set[tuple[str, str]]:
    """Read every docs/contracts/*.yaml file and return the set of
    (METHOD, normalized-full-path) operations they declare, excluding
    operations explicitly marked `x-status: not-implemented`."""
    ops: set[tuple[str, str]] = set()
    for file_path in sorted(glob.glob(CONTRACTS_GLOB)):
        with open(file_path) as f:
            contract = yaml.safe_load(f) or {}

        base = contract_base_path(contract)
        for path, methods in (contract.get("paths") or {}).items():
            # Files whose paths are already absolute (start with the base,
            # or the base is empty) are used as-is; otherwise the relative
            # server base path is prefixed.
            if base and not path.startswith(base):
                full_path = base + path
            else:
                full_path = path

            if not isinstance(methods, dict):
                continue
            for method, operation in methods.items():
                if method.lower() not in HTTP_METHODS:
                    continue
                if isinstance(operation, dict) and operation.get("x-status") == "not-implemented":
                    continue
                ops.add((method.upper(), normalize_params(full_path)))
    return ops


def main() -> int:
    live_ops = load_live_operations()
    contracted_ops = load_contracted_operations()

    orphans = sorted(live_ops - contracted_ops)

    print(f"Live operations (app.openapi()):   {len(live_ops)}")
    print(f"Contracted operations (docs/contracts/*.yaml, excl. x-status:not-implemented): {len(contracted_ops)}")
    print(f"Orphans (live, no contract):       {len(orphans)}")

    if orphans:
        print("\nFAIL: live endpoints without an OpenAPI contract:")
        for method, path in orphans:
            print(f"  {method:6} {path}")
        return 1

    print("\nPASS: every live endpoint has a matching contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
