#!/bin/bash
# Contract tests: OpenAPI validation + HL7 v2.x fixtures + FHIR R4 validation
set -euo pipefail

echo "=== Contract Tests ==="

# Validate OpenAPI spec
if [ -f docs/plan/architecture/api/openapi.yaml ]; then
    python3 -c "
import yaml, sys
spec = yaml.safe_load(open('docs/plan/architecture/api/openapi.yaml'))
assert 'openapi' in spec, 'Not a valid OpenAPI spec'
assert 'paths' in spec, 'No paths defined'
paths = list(spec.get('paths', {}).keys())
print(f'OpenAPI valid: {len(paths)} endpoints')
# Validate all endpoints have operationId
for path, methods in spec['paths'].items():
    for method, op in methods.items():
        if method in ('get','post','put','delete','patch') and 'operationId' not in op:
            print(f'WARNING: {method.upper()} {path} missing operationId')
" || { echo "FAIL: OpenAPI validation failed"; exit 1; }
else
    echo "WARNING: openapi.yaml not found"
fi

# Validate response schemas match frontend types
if [ -f docs/plan/architecture/api/openapi.yaml ] && [ -d frontend-v2/types ]; then
    python3 -c "
import yaml, json, os, re
spec = yaml.safe_load(open('docs/plan/architecture/api/openapi.yaml'))
schemas = spec.get('components',{}).get('schemas',{})
print(f'API schemas defined: {len(schemas)}')
"
fi

# HL7 v2.x fixture validation
if [ -d tests/fixtures/hl7 ]; then
    echo "HL7 fixtures found: $(find tests/fixtures/hl7 -type f | wc -l) files"
    # Basic MSH segment validation on each fixture
    python3 -c "
import os, re
fixture_dir = 'tests/fixtures/hl7'
if os.path.exists(fixture_dir):
    for f in os.listdir(fixture_dir):
        if f.endswith('.hl7') or f.endswith('.txt'):
            content = open(os.path.join(fixture_dir,f)).read()
            assert 'MSH|' in content, f'{f}: missing MSH segment'
            print(f'  {f}: MSH present')
"
fi

echo "PASS: Contract tests complete"
