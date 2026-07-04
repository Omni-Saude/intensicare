"""Gate: environment + ground-truth freeze + dirty-tree tripwire.

--init : record baselines (inputs manifest + dirty-tree baseline + pinned HEAD).
default: compare current state against baselines. FAIL if authoritative inputs
changed, pre-existing dirty files were touched, or new dirt appeared outside
docs/plan/.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _lib import ROOT, WORK, Gate, dump_json, sha256_file
import json

AUTHORITATIVE = (
    sorted((ROOT / "docs/rules/extraction/phase2/catalog").glob("*.yaml"))
    + [
        ROOT / p
        for p in [
            "docs/rules/ESCALATIONS.md",
            "docs/rules/AUDIT-REPORT.md",
            "docs/rules/README.md",
            "docs/rules/catalog-index.json",
            "docs/product/vision.md",
            "docs/product/personas.md",
            "docs/data/model.md",
            "docs/implementation-plan.md",
            "docs/architecture/adr/ADR-001-amh-data-platform-consumer.md",
            "docs/design/design-system-inventory.md",
            "docs/clinical/alert-catalog.md",
            "docs/review-queue.md",
            "docs/prompts/intensicare-build-plan-orchestrator-prompt.md",
        ]
    ]
    + sorted((ROOT / "docs/adr").glob("*.md"))
)

ALLOWED_BRANCHES = {"plan/intensicare-v2-build-plan"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout


def porcelain() -> tuple[list[str], list[str]]:
    lines = [l for l in git("status", "--porcelain=v1").splitlines() if l.strip()]
    tracked = sorted(l for l in lines if not l.startswith("??"))
    untracked = sorted(l for l in lines if l.startswith("??"))
    return tracked, untracked


def dirty_file_hashes(tracked: list[str]) -> dict:
    out = {}
    for line in tracked:
        path = line[3:].strip()
        p = ROOT / path
        out[path] = {"status": line[:2], "sha256": sha256_file(p) if p.exists() else None}
    return out


def main() -> int:
    init = "--init" in sys.argv
    pre = WORK / "preflight"
    pre.mkdir(parents=True, exist_ok=True)
    inputs_path = WORK / "gates/inputs-manifest.json"
    dirty_path = WORK / "gates/dirty-tree-baseline.json"

    if init:
        manifest = {str(p.relative_to(ROOT)): sha256_file(p) for p in AUTHORITATIVE}
        (WORK / "gates").mkdir(parents=True, exist_ok=True)
        dump_json(manifest, inputs_path)
        tracked, untracked = porcelain()
        dump_json(
            {
                "head": git("rev-parse", "HEAD").strip(),
                "branch": git("rev-parse", "--abbrev-ref", "HEAD").strip(),
                "tracked_dirty": tracked,
                "untracked": untracked,
                "hashes": dirty_file_hashes(tracked),
            },
            dirty_path,
        )
        print(f"[check_env --init] recorded {len(manifest)} input hashes, "
              f"{len(tracked)} tracked-dirty + {len(untracked)} untracked baseline entries, "
              f"HEAD {git('rev-parse', '--short', 'HEAD').strip()}")
        return 0

    g = Gate("check_env")
    manifest = json.loads(inputs_path.read_text())
    baseline = json.loads(dirty_path.read_text())

    changed = []
    for rel, h in manifest.items():
        p = ROOT / rel
        if not p.exists():
            changed.append(f"MISSING {rel}")
        elif sha256_file(p) != h:
            changed.append(f"CHANGED {rel}")
    g.add("ENV-INPUTS-FROZEN", not changed, "all authoritative inputs unchanged",
          f"{len(changed)} changed/missing", changed)

    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    head = git("rev-parse", "HEAD").strip()
    base_ok = head == baseline["head"] or baseline["head"] in git("rev-list", "HEAD").split()
    g.add("ENV-BRANCH", branch in ALLOWED_BRANCHES and base_ok,
          f"branch in {sorted(ALLOWED_BRANCHES)}, HEAD descends from pinned base",
          f"branch={branch} head={head[:9]} base_ok={base_ok}")

    tracked, untracked = porcelain()
    staged = [l for l in tracked if l[0] not in " ?"]
    g.add("ENV-NOTHING-STAGED", not staged,
          "index clean until Phase E end-game", f"{len(staged)} staged entries", staged)
    base_tracked = baseline["tracked_dirty"]
    missing = [l for l in base_tracked if l not in tracked]
    extra = [l for l in tracked if l not in base_tracked]
    g.add("ENV-DIRTY-SET-INTACT", not missing and not extra,
          "tracked-dirty set identical to baseline",
          f"{len(missing)} disappeared, {len(extra)} new",
          [f"gone: {l}" for l in missing] + [f"new: {l}" for l in extra])

    touched = []
    for path, rec in baseline["hashes"].items():
        p = ROOT / path
        cur = sha256_file(p) if p.exists() else None
        if cur != rec["sha256"]:
            touched.append(path)
    g.add("ENV-DIRTY-CONTENT-INTACT", not touched,
          "pre-existing dirty files byte-identical", f"{len(touched)} touched", touched)

    base_untracked = set(baseline["untracked"])
    bad_untracked = [
        l for l in untracked
        if l not in base_untracked and not l[3:].startswith(("docs/plan/", ".claude/"))
    ]
    g.add("ENV-NO-STRAY-UNTRACKED", not bad_untracked,
          "new untracked paths only under docs/plan/", f"{len(bad_untracked)} strays", bad_untracked)

    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
