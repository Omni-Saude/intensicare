"""API v1 routes."""

from intensicare.api.patients import router as patients_router
from intensicare.api.vitals import router as vitals_router

# Use relative imports within the same package to avoid circular dependency
from .admin import router as admin_router
from .alert_routing import router as alert_routing_router
from .alerts import router as alerts_router
from .antimicrobial import router as antimicrobial_router
from .auth import router as auth_router
from .auth import api_v1_auth_router
from .dashboard import router as dashboard_router
from .deterioration import router as deterioration_router
from .documentacao import router as documentacao_router
from .efficiency import router as efficiency_router
from .events import router as events_router
from .evolucoes import router as evolucoes_router
from .formularios import router as formularios_router
from .health import router as health_router
from .indicators import router as indicators_router
from .movimentacao import router as movimentacao_router
from .pathways import router as pathways_router
from .prescricao import router as prescricao_router
from .prophylaxis import router as prophylaxis_router
from .registry import router as registry_router
from .sedacao import router as sedacao_router
from .stability import router as stability_router
from .ventilation import router as ventilation_router
from .ws import router as ws_router

__all__ = [
    "admin_router",
    "alert_routing_router",
    "alerts_router",
    "antimicrobial_router",
    "auth_router",
    "api_v1_auth_router",
    "dashboard_router",
    "deterioration_router",
    "documentacao_router",
    "efficiency_router",
    "events_router",
    "evolucoes_router",
    "formularios_router",
    "health_router",
    "indicators_router",
    "movimentacao_router",
    "patients_router",
    "pathways_router",
    "prescricao_router",
    "prophylaxis_router",
    "registry_router",
    "sedacao_router",
    "stability_router",
    "ventilation_router",
    "vitals_router",
    "ws_router",
]
