#!/usr/bin/env python3
"""
IntensiCare — Alert Registry Builder (F-ARCH-002)

Reads all YAML alert definitions from _work/alerts/, computes SHA-256
content hashes for each definition, validates uniqueness of IDs, and
outputs a content-addressed registry to _work/alerts/registry.json.

Per ADR-021: content-addressed, YAML-defined alerts.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ALERTS_DIR = ROOT / "_work" / "alerts"
REGISTRY_PATH = ALERTS_DIR / "registry.json"


def load_alert_definitions(alerts_dir: Path) -> list[dict]:
    """Load all YAML files from the alerts directory.

    Each YAML file is expected to contain a list of alert definition dicts
    at the top level.

    Args:
        alerts_dir: Directory containing *.yaml alert definition files.

    Returns:
        Flat list of all alert definition dicts across all YAML files.
    """
    definitions: list[dict] = []

    yaml_files = sorted(alerts_dir.glob("*.yaml"))
    if not yaml_files:
        print(f"[WARN] No YAML files found in {alerts_dir}")
        return definitions

    for yaml_file in yaml_files:
        print(f"[LOAD] {yaml_file.relative_to(ROOT)}")
        with open(yaml_file, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        if data is None:
            print(f"  -> (empty file, skipping)")
            continue

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item["_source_file"] = str(yaml_file.relative_to(ROOT))
                    definitions.append(item)
                else:
                    print(f"  [WARN] Skipping non-dict item in {yaml_file.name}")
        elif isinstance(data, dict):
            data["_source_file"] = str(yaml_file.relative_to(ROOT))
            definitions.append(data)
        else:
            print(f"  [WARN] Unexpected YAML structure in {yaml_file.name}")

    return definitions


def compute_content_hash(definition: dict) -> str:
    """Compute SHA-256 content hash for a single alert definition.

    The hash is computed over the canonical JSON representation of the
    definition, excluding the _source_file metadata marker.

    Args:
        definition: Alert definition dict (may include _source_file).

    Returns:
        Hexadecimal SHA-256 hash string.
    """
    # Strip internal marker before hashing
    clean = {k: v for k, v in definition.items() if not k.startswith("_")}
    # Canonical JSON with sorted keys for deterministic hashing
    canonical = json.dumps(clean, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_registry(alerts_dir: Path, registry_path: Path) -> int:
    """Build the content-addressed alert registry.

    Args:
        alerts_dir: Directory with YAML alert definitions.
        registry_path: Output path for registry.json.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    # 1. Load all definitions
    definitions = load_alert_definitions(alerts_dir)
    if not definitions:
        print("[ERROR] No alert definitions found. Aborting.")
        return 1

    # 2. Validate ID uniqueness
    ids_seen: dict[str, str] = {}  # id -> source_file
    for d in definitions:
        alert_id = d.get("id")
        if not alert_id:
            print(f"[ERROR] Alert definition missing 'id' field in {d.get('_source_file', '?')}")
            return 1
        if alert_id in ids_seen:
            print(
                f"[ERROR] Duplicate alert ID '{alert_id}': "
                f"found in {ids_seen[alert_id]} and {d.get('_source_file', '?')}"
            )
            return 1
        ids_seen[alert_id] = d.get("_source_file", "?")

    print(f"\n[OK] {len(definitions)} alert definitions loaded, all IDs unique.")

    # 3. Compute hashes
    registry_entries: list[dict] = []
    for d in definitions:
        content_hash = compute_content_hash(d)
        entry = {
            "id": d["id"],
            "name": d.get("name", d["id"]),
            "description": d.get("description", ""),
            "severity": d.get("severity", "info"),
            "sha256": content_hash,
            "source_file": d.get("_source_file", "?"),
            "guideline_source": d.get("guideline_source", ""),
        }
        registry_entries.append(entry)

    # 4. Build registry document
    registry = {
        "schema_version": "1.0.0",
        "adr": "ADR-021",
        "total_alerts": len(registry_entries),
        "alerts": registry_entries,
    }

    # 5. Write registry.json
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"\n[DONE] Registry written to {registry_path.relative_to(ROOT)}")
    print(f"       {len(registry_entries)} alerts indexed with SHA-256 content hashes.")

    # 6. Print summary table
    print("\n── Alert Registry Summary ──")
    print(f"{'ID':<30} {'Severity':<10} {'Hash (first 16)'}")
    print("-" * 58)
    for entry in registry_entries:
        short_hash = entry["sha256"][:16]
        print(f"{entry['id']:<30} {entry['severity']:<10} {short_hash}")

    return 0


def main() -> int:
    """Entry point."""
    print("=" * 60)
    print("  IntensiCare — Alert Registry Builder")
    print("=" * 60)
    print()

    if not ALERTS_DIR.is_dir():
        print(f"[ERROR] Alerts directory not found: {ALERTS_DIR}")
        print("         Create _work/alerts/ with YAML alert definitions first.")
        return 1

    return build_registry(ALERTS_DIR, REGISTRY_PATH)


if __name__ == "__main__":
    sys.exit(main())
