"""Shared helpers for the IntensiCare v2 build-plan gate/tool scripts.

stdlib + PyYAML only. Every gate writes a machine JSON result to
docs/plan/_work/gates/<gate>.json and prints a one-line human summary.
Exit codes: 0 PASS, 1 FAIL, 2 PASS-WITH-WARNINGS.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    )
    return Path(out.stdout.strip())


ROOT = repo_root()
WORK = ROOT / "docs/plan/_work"
GATES = WORK / "gates"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(obj, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False, width=110)
    tmp.rename(path)


def dump_json(obj, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=False)
    tmp.rename(path)


class Gate:
    def __init__(self, name: str):
        self.name = name
        self.checks: list[dict] = []

    def add(self, check_id: str, ok: bool, expected: str, actual: str, details=None, warn=False):
        status = "PASS" if ok else ("WARN" if warn else "FAIL")
        self.checks.append(
            {
                "id": check_id,
                "status": status,
                "expected": expected,
                "actual": actual,
                "details": (details or [])[:40],
            }
        )

    def finish(self) -> int:
        n_fail = sum(1 for c in self.checks if c["status"] == "FAIL")
        n_warn = sum(1 for c in self.checks if c["status"] == "WARN")
        n_pass = sum(1 for c in self.checks if c["status"] == "PASS")
        status = "FAIL" if n_fail else ("WARN" if n_warn else "PASS")
        GATES.mkdir(parents=True, exist_ok=True)
        dump_json(
            {
                "gate": self.name,
                "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "status": status,
                "checks": self.checks,
                "counts": {"pass": n_pass, "fail": n_fail, "warn": n_warn},
            },
            GATES / f"{self.name}.json",
        )
        first_bad = next((c for c in self.checks if c["status"] == "FAIL"), None)
        extra = f" — first failure: {first_bad['id']} ({first_bad['actual']})" if first_bad else ""
        print(f"[GATE {self.name}] {status} — {n_pass} pass / {n_fail} fail / {n_warn} warn{extra}")
        for c in self.checks:
            if c["status"] != "PASS":
                print(f"  {c['status']} {c['id']}: expected {c['expected']}; actual {c['actual']}")
                for d in c["details"][:20]:
                    print(f"    - {d}")
        return 1 if n_fail else (2 if n_warn else 0)


def journal(event: str, payload: dict) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        "payload": payload,
    }
    state_dir = WORK / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    with open(state_dir / "journal.ndjson", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
