# Python Version Compatibility

**Date:** 2026-07-09
**Document:** L2 gap closure

## Current State

| Environment | Python | Status |
|------------|--------|--------|
| `pyproject.toml` requires | `>=3.12` | Specified |
| macOS local | 3.11 | ⚠️ Mismatch |
| CI (GitHub Actions) | 3.12 | ✅ via `actions/setup-python` |
| Docker | 3.12-slim | ✅ via `Dockerfile` |

## Impact

Local development with Python 3.11 causes:
- `pip install -e ".[dev]"` may fail due to syntax features
- Some type annotations (PEP 695) not available on 3.11

## Workaround

1. **Preferred:** Update local Python to 3.12:
   ```bash
   brew install python@3.12
   ```
2. **Alternative:** Use Docker for development:
   ```bash
   docker compose up api
   ```
3. **CI-only testing:** Run tests with `--noconftest` locally and let CI handle full suite

## Resolution

This is an **accepted risk** for local dev. Production (Docker) and CI both use Python 3.12. Documented for developer awareness.
