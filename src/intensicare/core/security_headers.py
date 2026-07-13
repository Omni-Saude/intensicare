"""Security headers middleware — OWASP-recommended headers for healthcare.

Injects security headers into every HTTP response. Follows the same
BaseHTTPMiddleware pattern as RateLimitMiddleware in core/rate_limit.py.

Headers applied:
- Strict-Transport-Security (HSTS) — enforced in staging/production
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Content-Security-Policy (CSP) — strict healthcare defaults, configurable
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: disables camera, mic, geolocation, FLoC

Reference: OWASP Secure Headers Project / ASVS V14.4
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from intensicare.config import settings

# ---------------------------------------------------------------------------
# Default security headers — strict healthcare profile (OWASP ASVS L2+)
# ---------------------------------------------------------------------------

# CSP default: lock down to same-origin with minimal carve-outs.
# style-src 'unsafe-inline' is often required by frontend frameworks
# (React, MUI) that inline critical CSS for FCP performance.
_DEFAULT_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

DEFAULT_SECURITY_HEADERS: dict[str, str] = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": _DEFAULT_CSP,
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": ("camera=(), microphone=(), geolocation=(), interest-cohort=()"),
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that injects OWASP-recommended security headers.

    All headers are applied via ``response.headers.setdefault`` so they
    do not overwrite any headers already set by route handlers.

    Behaviour per environment:

    - **development**: HSTS is *not* injected (localhost over HTTP would
      break).  All other headers remain active so developers catch CSP
      violations early.
    - **staging / production**: Full set applied. CSP can be overridden
      via the ``SECURITY_CSP_HEADER`` env var / settings field.
    """

    def __init__(
        self,
        app: ASGIApp,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(app)

        # Start from the strict defaults …
        self._headers: dict[str, str] = dict(headers) if headers else dict(DEFAULT_SECURITY_HEADERS)

        # … then apply environment-specific overrides.
        self._apply_environment_overrides()

    def _apply_environment_overrides(self) -> None:
        """Apply environment-sensitive header adjustments."""

        # --- CSP override from settings (allow per-env customisation) ---
        if hasattr(settings, "security_csp_header") and settings.security_csp_header:
            self._headers["Content-Security-Policy"] = settings.security_csp_header

        # --- HSTS relaxed in development (no HTTPS on localhost) ---
        if settings.environment == "development":
            self._headers.pop("Strict-Transport-Security", None)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        response = await call_next(request)

        for header_name, header_value in self._headers.items():
            # setdefault: route handlers can set stricter per-response
            # headers without being overwritten.
            response.headers.setdefault(header_name, header_value)

        return response
