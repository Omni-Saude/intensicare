"""Gate: end-game staging safety. --preflight before staging, default after `git add`.

Preflight: correct branch/base, nothing staged, dirty set == baseline, new untracked
only under docs/plan/. Post-stage: every staged path under docs/plan/, matches the
commit allowlist, and the unstaged dirty set is still byte-identical to baseline.
"""
from __future__ import annotations

import fnmatch
import json
import subprocess
import sys

from _lib import ROOT, WORK, Gate, sha256_file

COMMIT_ALLOW = [
    "docs/plan/*.md", "docs/plan/product/*", "docs/plan/clinical/*",
    "docs/plan/architecture/*", "docs/plan/design/*", "docs/plan/delivery/*",
    "docs/plan/_work/dispositions/*", "docs/plan/_work/escalations/*",
    "docs/plan/_work/coverage/*", "docs/plan/_work/budgets/*", "docs/plan/_work/safety/*",
    "docs/plan/_work/panels/*", "docs/plan/_work/barriers/*", "docs/plan/_work/redteam/*",
    "docs/plan/_work/units/*", "docs/plan/_work/platform/*", "docs/plan/_work/scripts/*",
    "docs/plan/_work/schemas/*", "docs/plan/_work/constraints/*", "docs/plan/_work/gates/*",
    "docs/plan/_work/state/handoff.md", "docs/plan/_work/adrs/*",
    "docs/plan/_work/domain-interfaces/*", "docs/plan/_work/alerts/*",
    "docs/plan/_work/traceability/*", "docs/plan/_work/editorial/*",
]
COMMIT_DENY = ["docs/plan/_work/briefs/*", "docs/plan/_work/catalog/*",
               "docs/plan/_work/state/state.json", "docs/plan/_work/state/journal.ndjson",
               "docs/plan/_work/preflight/*", "docs/plan/_work/reviews/samples/*",
               "*.tmp", "*.DS_Store"]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout


def main() -> int:
    pre = "--preflight" in sys.argv
    g = Gate("check_staged" + ("_preflight" if pre else ""))
    baseline = json.loads((WORK / "gates/dirty-tree-baseline.json").read_text())

    lines = [l for l in git("status", "--porcelain=v1").splitlines() if l.strip()]
    tracked = sorted(l for l in lines if not l.startswith("??"))
    staged = [l for l in tracked if l[0] not in " ?"]

    if pre:
        branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
        g.add("STG-BRANCH", branch == "audit/legacy-rule-extraction",
              "on audit/legacy-rule-extraction before branching", branch)
        g.add("STG-NOTHING-STAGED", not staged, "index clean", f"{len(staged)}", staged)
    else:
        bad = [l for l in staged if not l[3:].strip().startswith("docs/plan/")]
        g.add("STG-SCOPE", not bad, "every staged path under docs/plan/", f"{len(bad)}", bad)
        denied, unlisted = [], []
        for l in staged:
            path = l[3:].strip()
            if any(fnmatch.fnmatch(path, pat) for pat in COMMIT_DENY):
                denied.append(path)
            elif not any(fnmatch.fnmatch(path, pat) or
                         fnmatch.fnmatch(path, pat.rstrip("*") + "**") for pat in COMMIT_ALLOW):
                unlisted.append(path)
        g.add("STG-DENYLIST", not denied, "no denied artifacts staged", f"{len(denied)}", denied)
        g.add("STG-ALLOWLIST", not unlisted, "every staged path in the allowlist",
              f"{len(unlisted)}", unlisted, warn=True)
        g.add("STG-NONEMPTY", len(staged) > 30, ">30 files staged", str(len(staged)))

    unstaged_tracked = sorted(l for l in tracked if l[0] in " ?")
    base_unstaged = [l for l in baseline["tracked_dirty"] if not l[3:].startswith("docs/plan/")]
    missing = [l for l in base_unstaged if l not in unstaged_tracked and l not in staged]
    g.add("STG-BASELINE-SET", not missing, "pre-existing dirty set untouched",
          f"{len(missing)} disappeared", missing)
    touched = []
    for path, rec in baseline["hashes"].items():
        p = ROOT / path
        cur = sha256_file(p) if p.exists() else None
        if cur != rec["sha256"]:
            touched.append(path)
    g.add("STG-BASELINE-CONTENT", not touched, "pre-existing dirty files byte-identical",
          f"{len(touched)}", touched)
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
