"""API v1 routes."""

from intensicare.api.patients import router as patients_router
from intensicare.api.vitals import router as vitals_router

# Use relative imports within the same package to avoid circular dependency
from .admin import router as admin_router
from .alerts import router as alerts_router
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .health import router as health_router
from .ws import router as ws_router

__all__ = [
    "admin_router",
    "alerts_router",
    "auth_router",
    "dashboard_router",
    "health_router",
    "patients_router",
    "vitals_router",
    "ws_router",
]
