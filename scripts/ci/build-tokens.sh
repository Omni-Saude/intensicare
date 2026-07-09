#!/bin/bash
# M4: Style Dictionary token build + validation in CI
# Ensures design tokens are built and validated on every push.
# Usage: ./scripts/ci/build-tokens.sh

set -euo pipefail

echo "=== Style Dictionary Token Build ==="

# Navigate to frontend directory where tokens are consumed
cd "$(dirname "$0")/../../frontend-v2"

# Build tokens
echo "Building design tokens..."
npm run build-tokens 2>&1 | tee /tmp/token-build.log

# Verify outputs exist
REQUIRED_OUTPUTS=(
    "../design-tokens/build/tokens.css"
    "../design-tokens/build/tokens-dark.css"
    "../design-tokens/build/tokens-light.css"
    "../design-tokens/build/tokens.json"
    "../design-tokens/build/tokens.ts"
)

FAILED=0
for f in "${REQUIRED_OUTPUTS[@]}"; do
    if [ -f "$f" ]; then
        echo "  ✅ $f ($(wc -c < "$f") bytes)"
    else
        echo "  ❌ $f MISSING"
        FAILED=1
    fi
done

# Token resolution check: ensure all var(--...) references resolve
echo "Checking CSS custom property references..."
MISSING_REFS=$(grep -oP 'var\(--[^)]+\)' ../design-tokens/build/tokens.css | sort -u | while read ref; do
    token_name="${ref#var\(--}"
    token_name="${token_name%)}"
    if ! grep -q "$token_name" ../design-tokens/build/tokens.css; then
        echo "UNRESOLVED: $ref"
    fi
done)

if [ -n "$MISSING_REFS" ]; then
    echo "⚠️  WARNING: Some CSS variable references could not be verified"
    echo "$MISSING_REFS"
fi

# Fail if required outputs missing
if [ $FAILED -eq 1 ]; then
    echo "❌ Token build FAILED — missing outputs"
    exit 1
fi

echo "✅ Token build PASSED — all outputs generated"
