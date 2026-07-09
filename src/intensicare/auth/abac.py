"""ABAC — Attribute-Based Access Control via Lake Formation grants (Fase 3 / WO-037).

Modelo de autorização que substitui RBAC binário (admin/não-admin) por
políticas baseadas em atributos do usuário (tenant, role, groups, departamento).

Integração com AWS Lake Formation:
    - Mapeia ``tenant_id`` → LF tag ``tenant`` nas tabelas catalogadas.
    - Mapeia ``role`` clínico → LF tag ``clinical_role``.
    - Gera grants temporários via LF ``GrantPermissions`` API.

Fallback local:
    Quando Lake Formation não está configurado, as políticas ABAC são
    avaliadas localmente (útil para dev/test).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from intensicare.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos e Enums
# ---------------------------------------------------------------------------


class ClinicalRole(str, Enum):
    """Roles clínicos usados nas políticas ABAC."""

    PHYSICIAN = "physician"       # Médico — acesso pleno aos pacientes do tenant
    NURSE = "nurse"               # Enfermeiro — leitura + escrita de vitals
    PHARMACIST = "pharmacist"     # Farmacêutico — somente domínio pharmaco
    LAB_TECH = "lab_tech"         # Técnico de laboratório — somente lab results
    ADMIN = "admin"               # Administrador — acesso global (multi-tenant)
    VIEWER = "viewer"             # Visualizador — somente leitura, dashboards
    AUDITOR = "auditor"           # Auditor — somente audit_trail, sem PHI


class ResourceType(str, Enum):
    """Tipos de recursos protegidos por ABAC."""

    VITALS = "vitals"
    LAB_RESULTS = "lab_results"
    MEDICATIONS = "medications"
    CLINICAL_SCORES = "clinical_scores"
    PATIENT_DEMOGRAPHICS = "patient_demographics"
    AUDIT_TRAIL = "audit_trail"
    DASHBOARD = "dashboard"
    ALERTS = "alerts"
    THRESHOLDS = "thresholds"
    USER = "user"
    TENANT = "tenant"


class Action(str, Enum):
    """Ações permitidas/negadas pelas políticas ABAC."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ACKNOWLEDGE = "acknowledge"
    EXPORT = "export"
    ADMIN = "admin"


# ---------------------------------------------------------------------------
# Políticas ABAC
# ---------------------------------------------------------------------------


@dataclass
class ABACPolicy:
    """Uma regra ABAC individual."""

    role: ClinicalRole
    resource: ResourceType
    allowed_actions: set[Action] = field(default_factory=set)
    # Se definido, restringe a tenant específicos (vazio = todos)
    tenant_constraint: set[str] = field(default_factory=set)


# Matriz de políticas ABAC (pode ser externalizada para DynamoDB/Config em produção)
_ABAC_POLICY_MATRIX: list[ABACPolicy] = [
    # Physician: acesso pleno aos pacientes do tenant
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.VITALS,
        allowed_actions={Action.READ, Action.WRITE},
    ),
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.LAB_RESULTS,
        allowed_actions={Action.READ, Action.WRITE, Action.EXPORT},
    ),
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.MEDICATIONS,
        allowed_actions={Action.READ, Action.WRITE},
    ),
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.CLINICAL_SCORES,
        allowed_actions={Action.READ, Action.WRITE},
    ),
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.PATIENT_DEMOGRAPHICS,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.ALERTS,
        allowed_actions={Action.READ, Action.ACKNOWLEDGE},
    ),
    ABACPolicy(
        role=ClinicalRole.PHYSICIAN,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ},
    ),

    # Nurse: leitura + escrita de vitals, leitura de scores/labs
    ABACPolicy(
        role=ClinicalRole.NURSE,
        resource=ResourceType.VITALS,
        allowed_actions={Action.READ, Action.WRITE},
    ),
    ABACPolicy(
        role=ClinicalRole.NURSE,
        resource=ResourceType.CLINICAL_SCORES,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.NURSE,
        resource=ResourceType.LAB_RESULTS,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.NURSE,
        resource=ResourceType.PATIENT_DEMOGRAPHICS,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.NURSE,
        resource=ResourceType.ALERTS,
        allowed_actions={Action.READ, Action.ACKNOWLEDGE},
    ),
    ABACPolicy(
        role=ClinicalRole.NURSE,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ},
    ),

    # Pharmacist: somente domínio pharmaco
    ABACPolicy(
        role=ClinicalRole.PHARMACIST,
        resource=ResourceType.MEDICATIONS,
        allowed_actions={Action.READ, Action.WRITE},
    ),
    ABACPolicy(
        role=ClinicalRole.PHARMACIST,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.PHARMACIST,
        resource=ResourceType.ALERTS,
        allowed_actions={Action.READ},
    ),

    # Lab Tech: somente lab results
    ABACPolicy(
        role=ClinicalRole.LAB_TECH,
        resource=ResourceType.LAB_RESULTS,
        allowed_actions={Action.READ, Action.WRITE},
    ),
    ABACPolicy(
        role=ClinicalRole.LAB_TECH,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ},
    ),

    # Admin: acesso global multi-tenant
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.VITALS,
        allowed_actions={Action.READ, Action.WRITE, Action.DELETE, Action.EXPORT},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.LAB_RESULTS,
        allowed_actions={Action.READ, Action.WRITE, Action.DELETE, Action.EXPORT},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.MEDICATIONS,
        allowed_actions={Action.READ, Action.WRITE, Action.DELETE, Action.EXPORT},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.CLINICAL_SCORES,
        allowed_actions={Action.READ, Action.WRITE, Action.DELETE},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.PATIENT_DEMOGRAPHICS,
        allowed_actions={Action.READ, Action.WRITE, Action.EXPORT, Action.ADMIN},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.AUDIT_TRAIL,
        allowed_actions={Action.READ, Action.EXPORT},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.THRESHOLDS,
        allowed_actions={Action.READ, Action.WRITE, Action.ADMIN},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.ALERTS,
        allowed_actions={Action.READ, Action.WRITE, Action.ACKNOWLEDGE, Action.ADMIN},
    ),
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ, Action.ADMIN},
    ),
    # Admin: user management
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.USER,
        allowed_actions={Action.READ, Action.WRITE, Action.DELETE, Action.ADMIN},
    ),
    # Admin: tenant management
    ABACPolicy(
        role=ClinicalRole.ADMIN,
        resource=ResourceType.TENANT,
        allowed_actions={Action.READ, Action.WRITE, Action.DELETE, Action.ADMIN},
    ),

    # Viewer: somente leitura
    ABACPolicy(
        role=ClinicalRole.VIEWER,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.VIEWER,
        resource=ResourceType.CLINICAL_SCORES,
        allowed_actions={Action.READ},
    ),
    ABACPolicy(
        role=ClinicalRole.VIEWER,
        resource=ResourceType.ALERTS,
        allowed_actions={Action.READ},
    ),

    # Auditor: somente audit_trail, sem PHI
    ABACPolicy(
        role=ClinicalRole.AUDITOR,
        resource=ResourceType.AUDIT_TRAIL,
        allowed_actions={Action.READ, Action.EXPORT},
    ),
    ABACPolicy(
        role=ClinicalRole.AUDITOR,
        resource=ResourceType.DASHBOARD,
        allowed_actions={Action.READ},
    ),
]


# ---------------------------------------------------------------------------
# Lake Formation grant engine (stub — produção integra com boto3 LF)
# ---------------------------------------------------------------------------


class LakeFormationClient(Protocol):
    """Interface para o cliente AWS Lake Formation (produção: boto3)."""

    async def grant_permissions(
        self,
        principal: str,
        resource: dict[str, Any],
        permissions: list[str],
    ) -> None: ...

    async def revoke_permissions(
        self,
        principal: str,
        resource: dict[str, Any],
        permissions: list[str],
    ) -> None: ...


class _LFGrantEngine:
    """Motor de grants Lake Formation.

    Em produção, usa boto3 para chamar a API GrantPermissions.
    O stub local gera grants no-op para dev/test.
    """

    def __init__(self) -> None:
        self._lf_client: LakeFormationClient | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Inicializa o cliente Lake Formation (lazy)."""
        if self._initialized:
            return
        if settings.lake_formation_data_catalog_id:
            try:
                import boto3  # type: ignore[import-untyped]
                self._lf_client = boto3.client(
                    "lakeformation",
                    region_name=settings.iam_region,
                )
                logger.info(
                    "Lake Formation client initialized for catalog %s",
                    settings.lake_formation_data_catalog_id,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to initialize Lake Formation client: %s. "
                    "Falling back to local ABAC evaluation.",
                    exc,
                )
                self._lf_client = None
        self._initialized = True

    async def grant_table_access(
        self,
        principal_arn: str,
        database: str,
        table: str,
        permissions: list[str],
    ) -> None:
        """Concede acesso Lake Formation a uma tabela específica."""
        if self._lf_client is None:
            logger.debug(
                "LF grant skipped (no client): %s → %s.%s [%s]",
                principal_arn, database, table, permissions,
            )
            return

        try:
            await self._lf_client.grant_permissions(
                Principal={"DataLakePrincipalIdentifier": principal_arn},
                Resource={
                    "Table": {
                        "DatabaseName": database,
                        "CatalogId": settings.lake_formation_data_catalog_id,
                        "Name": table,
                    }
                },
                Permissions=permissions,
            )
            logger.info(
                "LF grant: %s → %s.%s [%s]",
                principal_arn, database, table, permissions,
            )
        except Exception as exc:
            logger.error("LF grant failed: %s", exc)
            raise


# Singleton
_lf_grants = _LFGrantEngine()


async def get_lf_grant_engine() -> _LFGrantEngine:
    """Retorna o motor de grants Lake Formation (inicializado lazy)."""
    await _lf_grants.initialize()
    return _lf_grants


# ---------------------------------------------------------------------------
# Avaliador ABAC local
# ---------------------------------------------------------------------------


class ABACAccessDenied(Exception):
    """Acesso negado pela política ABAC."""

    def __init__(
        self,
        role: str,
        resource: str,
        action: str,
        tenant: str | None = None,
    ) -> None:
        self.role = role
        self.resource = resource
        self.action = action
        self.tenant = tenant
        super().__init__(
            f"ABAC denied: role={role!r} cannot {action} on {resource}"
            + (f" (tenant={tenant!r})" if tenant else "")
        )


def evaluate_abac(
    role_str: str,
    resource: ResourceType,
    action: Action,
    tenant_id: str,
    resource_tenant: str,
) -> bool:
    """Avalia se uma ação é permitida pelas políticas ABAC.

    Args:
        role_str: Role clínico do usuário (string; mapeado para ClinicalRole).
        resource: Tipo de recurso acessado.
        action: Ação solicitada.
        tenant_id: Tenant do usuário autenticado.
        resource_tenant: Tenant proprietário do recurso.

    Returns:
        True se a ação é permitida, False caso contrário.
    """
    try:
        role = ClinicalRole(role_str)
    except ValueError:
        logger.warning("Unknown clinical role: %r — defaulting to VIEWER", role_str)
        role = ClinicalRole.VIEWER

    # Admin tem acesso cross-tenant
    if role == ClinicalRole.ADMIN:
        for policy in _ABAC_POLICY_MATRIX:
            if policy.role == role and policy.resource == resource:
                if action in policy.allowed_actions:
                    return True

    # Demais roles: tenant deve bater
    if tenant_id != resource_tenant:
        logger.debug(
            "ABAC tenant mismatch: user=%s, resource=%s",
            tenant_id, resource_tenant,
        )
        return False

    for policy in _ABAC_POLICY_MATRIX:
        if policy.role != role:
            continue
        if policy.resource != resource:
            continue
        if action in policy.allowed_actions:
            # Se há tenant_constraint, verifica
            if policy.tenant_constraint and tenant_id not in policy.tenant_constraint:
                continue
            return True

    return False


def require_abac(
    role_str: str,
    resource: ResourceType,
    action: Action,
    tenant_id: str,
    resource_tenant: str,
) -> None:
    """Avalia ABAC e levanta ABACAccessDenied se negado.

    Args:
        role_str: Role do usuário.
        resource: Tipo de recurso.
        action: Ação solicitada.
        tenant_id: Tenant do usuário.
        resource_tenant: Tenant do recurso.

    Raises:
        ABACAccessDenied: Se a política não permitir a ação.
    """
    if not evaluate_abac(role_str, resource, action, tenant_id, resource_tenant):
        raise ABACAccessDenied(
            role=role_str,
            resource=resource.value,
            action=action.value,
            tenant=tenant_id,
        )


# ---------------------------------------------------------------------------
# Mapeamento Lake Formation tags → ABAC
# ---------------------------------------------------------------------------


def build_lf_tag_expression(
    tenant_id: str,
    clinical_role: str,
) -> str:
    """Constrói expressão de tags Lake Formation para filtragem ABAC.

    Exemplo de saída:
        ``tenant=UTI-Alpha AND clinical_role IN (physician,nurse,admin)``

    Args:
        tenant_id: Tenant do usuário.
        clinical_role: Role clínico.

    Returns:
        Expressão de tag LF compatível com a API GrantPermissions.
    """
    # Roles que podem ver dados do tenant (hierarquia de visibilidade)
    visible_roles: set[str] = {clinical_role}
    if clinical_role in (ClinicalRole.ADMIN.value, ClinicalRole.AUDITOR.value):
        # Admin e Auditor veem todos os dados do tenant
        visible_roles = {r.value for r in ClinicalRole}
    elif clinical_role == ClinicalRole.PHYSICIAN.value:
        visible_roles = {
            ClinicalRole.PHYSICIAN.value,
            ClinicalRole.NURSE.value,
            ClinicalRole.LAB_TECH.value,
            ClinicalRole.PHARMACIST.value,
            ClinicalRole.VIEWER.value,
        }

    roles_str = ",".join(sorted(visible_roles))
    return f"tenant={tenant_id} AND clinical_role IN ({roles_str})"
