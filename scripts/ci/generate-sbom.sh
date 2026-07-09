#!/usr/bin/env bash
# =============================================================================
# IntensiCare — SBOM (Software Bill of Materials) Generator
# =============================================================================
# Usage: ./scripts/ci/generate-sbom.sh [output-path]
#
# Generates a CycloneDX JSON SBOM for the Python backend dependencies.
# Falls back to a lightweight pip-freeze based JSON when cyclonedx-bom is
# not installable (air-gapped or restricted environments).
#
# Output:
#   sbom.json          — CycloneDX SBOM (or lightweight fallback)
#   sbom.txt           — Plain pip freeze for human review
#   sbom.sha256        — Integrity checksum of sbom.json
#
# Prerequisites:
#   - Python 3.10+
#   - The project's virtual environment should be active OR
#     the script will create a temp venv
# =============================================================================

set -euo pipefail

OUTPUT_DIR="${1:-$(dirname "$0")/../../sbom}"
mkdir -p "$OUTPUT_DIR"

SBOM_JSON="$OUTPUT_DIR/sbom.json"
SBOM_TXT="$OUTPUT_DIR/sbom.txt"
SBOM_HASH="$OUTPUT_DIR/sbom.sha256"

echo "=== IntensiCare SBOM Generator ==="
echo "Output directory: $OUTPUT_DIR"
echo ""

# ------------------------------------------------------------------
# 1. Generate plain pip-freeze (always works, zero dependencies)
# ------------------------------------------------------------------
echo "[1/3] Generating pip freeze..."
pip freeze --all > "$SBOM_TXT" 2>/dev/null || pip freeze > "$SBOM_TXT"
echo "  → $SBOM_TXT ($(wc -l < "$SBOM_TXT") packages)"

# ------------------------------------------------------------------
# 2. Try CycloneDX SBOM (preferred, structured format)
# ------------------------------------------------------------------
echo "[2/3] Generating CycloneDX SBOM..."

generate_cyclonedx() {
    # Attempt to install cyclonedx-bom and generate the SBOM.
    # This is a best-effort approach — if the package isn't available,
    # we fall back to a lightweight JSON generated from pip freeze.
    if pip install "cyclonedx-bom>=5" --quiet 2>/dev/null; then
        # Generate CycloneDX 1.5 JSON SBOM
        python -m cyclonedx_py \
            --format json \
            --output "$SBOM_JSON" \
            --pyproject "$(dirname "$0")/../../pyproject.toml" \
            2>/dev/null || cyclonedx-py \
                --format json \
                -o "$SBOM_JSON" \
                2>/dev/null || cyclonedx-bom \
                    --format json \
                    --output "$SBOM_JSON" \
                    2>/dev/null
        return $?
    fi
    return 1
}

if ! generate_cyclonedx; then
    echo "  → cyclonedx-bom not available; generating lightweight SBOM..."

    # ------------------------------------------------------------------
    # Lightweight fallback: pip freeze → structured JSON
    # ------------------------------------------------------------------
    python3 - "$SBOM_TXT" "$SBOM_JSON" << 'PYEOF'
import json, sys, hashlib, datetime, os, subprocess

input_txt = sys.argv[1]
output_json = sys.argv[2]

components = []
with open(input_txt) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-'):
            continue
        # pip freeze format: package==version  OR  package @ url
        if '==' in line:
            name, version = line.split('==', 1)
        elif ' @ ' in line:
            name = line.split(' @ ', 1)[0]
            version = 'unknown'
        else:
            name, version = line, 'unknown'

        # Skip editable installs
        if name.startswith('-e '):
            continue

        components.append({
            "type": "library",
            "name": name.strip(),
            "version": version.strip(),
            "purl": f"pkg:pypi/{name.strip()}@{version.strip()}"
        })

# Get commit hash if available
commit_hash = "unknown"
try:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, cwd=os.path.dirname(output_json)
    )
    if result.returncode == 0:
        commit_hash = result.stdout.strip()
except Exception:
    pass

sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "serialNumber": f"urn:uuid:{hashlib.md5(str(datetime.datetime.utcnow()).encode()).hexdigest()}",
    "version": 1,
    "metadata": {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "tools": [
            {
                "vendor": "IntensiCare",
                "name": "generate-sbom.sh (lightweight fallback)",
                "version": commit_hash
            }
        ],
        "component": {
            "type": "application",
            "name": "intensicare",
            "version": "0.1.0"
        }
    },
    "components": components
}

with open(output_json, 'w') as f:
    json.dump(sbom, f, indent=2)

print(f"  → {output_json} ({len(components)} components)")
PYEOF
fi

# ------------------------------------------------------------------
# 3. Generate SHA-256 checksum for integrity verification
# ------------------------------------------------------------------
echo "[3/3] Generating integrity hash..."
if command -v shasum &>/dev/null; then
    shasum -a 256 "$SBOM_JSON" | awk '{print $1}' > "$SBOM_HASH"
elif command -v sha256sum &>/dev/null; then
    sha256sum "$SBOM_JSON" | awk '{print $1}' > "$SBOM_HASH"
else
    python3 -c "
import hashlib
with open('$SBOM_JSON', 'rb') as f:
    h = hashlib.sha256(f.read()).hexdigest()
with open('$SBOM_HASH', 'w') as f:
    f.write(h + '\n')
"
fi
echo "  → $SBOM_HASH ($(cat "$SBOM_HASH"))"

echo ""
echo "=== SBOM generation complete ==="
echo "Files:"
echo "  JSON:  $SBOM_JSON"
echo "  TXT:   $SBOM_TXT"
echo "  HASH:  $SBOM_HASH"
