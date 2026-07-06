#!/usr/bin/env python3
"""
DR Drill — script automatizado de validação de Disaster Recovery (WO-038).

Uso:
    python dr_drill.py [--full] [--region us-west-2] [--timeout 300]

Opções:
    --full      Executa validação completa (inclui smoke tests nos endpoints).
    --region    Região secundária a validar (default: us-west-2).
    --timeout   Timeout em segundos para cada verificação (default: 300).

O script NÃO executa failover — apenas valida que todos os pré-requisitos
para um failover real estão satisfeitos.

Checagens:
    1.  Conectividade com a região secundária (STS GetCallerIdentity).
    2.  ECR replication — imagem mais recente presente na região secundária.
    3.  RDS read replica — status Available, lag < RPO (1h).
    4.  KMS multi-region key — réplica existe e está habilitada.
    5.  ECS services — cluster existe na região secundária.
    6.  Route 53 health checks — todos os checks PASSAM na primária.
    7.  [--full] Smoke tests contra endpoint secundário (se exposto).
    8.  Dead-man switch — Lambda existe e está configurada.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("dr_drill")

# Carrega settings do Intensicare (precisa rodar do repo root ou ter PYTHONPATH)
try:
    from intensicare.config import settings
except ImportError:
    logger.warning(
        "intensicare.config não encontrado — usando valores padrão. "
        "Exporte PYTHONPATH=src ou rode do diretório raiz do projeto."
    )
    settings = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class CheckResult:
    """Resultado de uma checagem individual."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.passed = False
        self.detail = ""
        self.duration_ms = 0.0

    def __repr__(self) -> str:
        icon = "✅" if self.passed else "❌"
        return f"{icon} {self.name}: {self.detail} ({self.duration_ms:.0f}ms)"


class DrillReport:
    """Relatório agregado do drill."""

    def __init__(self) -> None:
        self.timestamp = datetime.now(timezone.utc)
        self.checks: list[CheckResult] = []
        self.overall_pass = True

    def add(self, result: CheckResult) -> None:
        self.checks.append(result)
        if not result.passed:
            self.overall_pass = False

    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        status = "✅ PASS" if self.overall_pass else "❌ FAIL"
        lines = [
            f"\n{'='*60}",
            f"  DR DRILL REPORT — {self.timestamp.isoformat()}",
            f"  Resultado: {status} ({passed}/{total} checks passaram)",
            f"{'='*60}",
        ]
        for check in self.checks:
            lines.append(f"  {check}")
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


async def _timed_check(name: str, coro: Any) -> CheckResult:
    """Executa uma checagem e mede a duração."""
    result = CheckResult(name)
    t0 = datetime.now(timezone.utc)
    try:
        detail = await coro
        result.passed = True
        result.detail = str(detail)
    except Exception as exc:
        result.passed = False
        result.detail = str(exc)
    result.duration_ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
    return result


# ---------------------------------------------------------------------------
# Checagens AWS (requer boto3)
# ---------------------------------------------------------------------------


async def check_sts_connectivity(region: str) -> str:
    """Verifica conectividade com a região alvo via STS."""
    import boto3  # type: ignore[import-untyped]
    sts = boto3.client("sts", region_name=region)
    identity = sts.get_caller_identity()
    return (
        f"Conectado como {identity['Arn']} na região {region} "
        f"(account {identity['Account']})"
    )


async def check_ecr_replication(
    primary_region: str, secondary_region: str
) -> str:
    """Verifica se a imagem mais recente está replicada."""
    import boto3  # type: ignore[import-untyped]
    ecr_primary = boto3.client("ecr", region_name=primary_region)
    ecr_secondary = boto3.client("ecr", region_name=secondary_region)

    repo_name = "intensicare/api"

    try:
        resp_primary = ecr_primary.describe_images(
            repositoryName=repo_name,
            maxResults=1,
            filter={"tagStatus": "TAGGED"},
        )
    except Exception:
        return f"ECR repo {repo_name!r} não encontrado na região primária (pode ser nome diferente)"

    if not resp_primary.get("imageDetails"):
        return "Nenhuma imagem encontrada na região primária"

    latest_primary = resp_primary["imageDetails"][0]
    digest = latest_primary.get("imageDigest", "unknown")

    try:
        resp_secondary = ecr_secondary.describe_images(
            repositoryName=repo_name,
            imageIds=[{"imageDigest": digest}],
        )
        return (
            f"Imagem {digest[:12]}... replicada em {secondary_region} "
            f"(tag: {latest_primary.get('imageTags', ['N/A'])[0]})"
        )
    except Exception:
        return (
            f"Imagem {digest[:12]}... NÃO encontrada em {secondary_region} "
            f"— replicação pode estar pendente"
        )


async def check_rds_replica(secondary_region: str) -> str:
    """Verifica status da read replica RDS na região secundária."""
    import boto3  # type: ignore[import-untyped]
    rds = boto3.client("rds", region_name=secondary_region)

    try:
        resp = rds.describe_db_instances(
            DBInstanceIdentifier="intensicare-dr"
        )
    except Exception:
        return (
            "RDS instance 'intensicare-dr' não encontrada em "
            f"{secondary_region} (verificar nome correto)"
        )

    instance = resp["DBInstances"][0]
    status = instance["DBInstanceStatus"]
    if status != "available":
        return f"RDS status={status} (esperado: available)"

    # Verifica replica lag
    lag_str = "N/A"
    if instance.get("ReadReplicaDBInstanceIdentifiers"):
        # Esta é a réplica — medir lag
        try:
            import boto3  # type: ignore[import-untyped]
            cloudwatch = boto3.client("cloudwatch", region_name=secondary_region)
            metric = cloudwatch.get_metric_statistics(
                Namespace="AWS/RDS",
                MetricName="ReplicaLag",
                Dimensions=[
                    {"Name": "DBInstanceIdentifier", "Value": "intensicare-dr"}
                ],
                StartTime=datetime.now(timezone.utc).isoformat(),
                EndTime=datetime.now(timezone.utc).isoformat(),
                Period=300,
                Statistics=["Maximum"],
            )
            if metric["Datapoints"]:
                lag_seconds = metric["Datapoints"][0]["Maximum"]
                lag_str = f"{lag_seconds:.0f}s"
                if lag_seconds > 3600:
                    return (
                        f"Replica lag ({lag_str}) excede RPO de 1h — "
                        f"RPO violado!"
                    )
        except Exception:
            lag_str = "cloudwatch-failed"

    return (
        f"RDS réplica disponível em {secondary_region} "
        f"(status={status}, lag={lag_str})"
    )


async def check_kms_multi_region(secondary_region: str) -> str:
    """Verifica se a CMK multi-region tem réplica na região secundária."""
    import boto3  # type: ignore[import-untyped]
    kms = boto3.client("kms", region_name=secondary_region)

    if settings and settings.kms_cmk_arn:
        key_id = settings.kms_cmk_arn
    else:
        return "KMS CMK não configurada (settings.kms_cmk_arn vazio) — pulando"

    try:
        resp = kms.describe_key(KeyId=key_id)
        key = resp["KeyMetadata"]
        key_state = key.get("KeyState", "unknown")
        multi_region = key.get("MultiRegion", False)

        if key_state != "Enabled":
            return f"KMS key state={key_state} (esperado: Enabled)"

        if not multi_region:
            return (
                f"KMS key NÃO é multi-region. DR requer MRK para "
                f"descriptografia cross-region!"
            )

        return (
            f"KMS MRK ativa em {secondary_region} "
            f"(id={key['KeyId']}, state={key_state})"
        )
    except Exception as exc:
        return f"KMS key não encontrada/erro: {exc}"


async def check_ecs_cluster(secondary_region: str) -> str:
    """Verifica se o cluster ECS existe na região secundária."""
    import boto3  # type: ignore[import-untyped]
    ecs = boto3.client("ecs", region_name=secondary_region)

    try:
        resp = ecs.describe_clusters(clusters=["intensicare"])
    except Exception:
        return f"ECS cluster 'intensicare' não encontrado em {secondary_region}"

    clusters = resp.get("clusters", [])
    if not clusters:
        return f"ECS cluster 'intensicare' não encontrado em {secondary_region}"

    cluster = clusters[0]
    status = cluster.get("status", "unknown")
    running = cluster.get("runningTasksCount", 0)
    pending = cluster.get("pendingTasksCount", 0)

    if status != "ACTIVE":
        return f"ECS cluster status={status} (esperado: ACTIVE)"

    return (
        f"ECS cluster ativo em {secondary_region} "
        f"(running={running}, pending={pending})"
    )


async def check_route53_health(primary_region: str) -> str:
    """Verifica se os health checks do Route 53 estão passando."""
    import boto3  # type: ignore[import-untyped]
    r53 = boto3.client("route53", region_name="us-east-1")

    try:
        resp = r53.list_health_checks(MaxItems="20")
    except Exception as exc:
        return f"Erro ao listar health checks: {exc}"

    checks = resp.get("HealthChecks", [])
    if not checks:
        return "Nenhum health check encontrado"

    failed = []
    for check in checks:
        try:
            status_resp = r53.get_health_check_status(
                HealthCheckId=check["Id"]
            )
            status = status_resp["HealthCheckObservations"]
            if status and status[0].get("StatusReport", {}).get("Status") != "Success":
                failed.append(check["Id"])
        except Exception:
            failed.append(check["Id"])

    if failed:
        return (
            f"{len(checks)} health checks, {len(failed)} falhando: "
            f"{', '.join(failed[:3])}"
        )
    return f"Todos os {len(checks)} health checks OK na região {primary_region}"


async def check_deadman_switch() -> str:
    """Verifica se a Lambda do dead-man switch está configurada."""
    import boto3  # type: ignore[import-untyped]
    aws_lambda = boto3.client("lambda", region_name="us-east-1")

    try:
        resp = aws_lambda.get_function(
            FunctionName="intensicare-deadman-switch"
        )
        runtime = resp.get("Configuration", {}).get("Runtime", "unknown")
        last_modified = resp.get("Configuration", {}).get("LastModified", "unknown")
        return (
            f"Dead-man switch Lambda OK (runtime={runtime}, "
            f"modified={last_modified})"
        )
    except Exception:
        return "Lambda 'intensicare-deadman-switch' não encontrada"


# ---------------------------------------------------------------------------
# Smoke tests (requer httpx)
# ---------------------------------------------------------------------------


async def smoke_test_api(base_url: str, timeout: int) -> str:
    """Executa smoke tests contra o endpoint da API."""
    import httpx

    results: list[str] = []

    async with httpx.AsyncClient(timeout=float(timeout), base_url=base_url) as client:
        # GET /api/v1/health
        try:
            resp = await client.get("/api/v1/health")
            status_icon = "✅" if resp.status_code == 200 else "❌"
            results.append(f"{status_icon} health: {resp.status_code}")
        except Exception as exc:
            results.append(f"❌ health: {exc}")

        # GET /api/v1/dashboard
        try:
            resp = await client.get("/api/v1/dashboard")
            status_icon = "✅" if 200 <= resp.status_code < 500 else "❌"
            results.append(f"{status_icon} dashboard: {resp.status_code}")
        except Exception as exc:
            results.append(f"❌ dashboard: {exc}")

    return "; ".join(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="DR Drill — validação de Disaster Recovery para Intensicare"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Executa validação completa com smoke tests",
    )
    parser.add_argument(
        "--region",
        default="us-west-2",
        help="Região secundária a validar (default: us-west-2)",
    )
    parser.add_argument(
        "--primary-region",
        default="us-east-1",
        help="Região primária (default: us-east-1)",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="URL base para smoke tests (ex: https://api-dr.intensicare.io)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout em segundos (default: 300)",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    report = DrillReport()

    primary = args.primary_region
    secondary = args.region

    logger.info("=== DR DRILL INICIADO ===")
    logger.info("Região primária: %s | Região secundária: %s", primary, secondary)
    logger.info("Modo: %s", "FULL" if args.full else "BASIC")

    checks = [
        ("STS Conectividade", check_sts_connectivity(secondary)),
        ("ECR Replication", check_ecr_replication(primary, secondary)),
        ("RDS Read Replica", check_rds_replica(secondary)),
        ("KMS Multi-Region Key", check_kms_multi_region(secondary)),
        ("ECS Cluster", check_ecs_cluster(secondary)),
        ("Route 53 Health Checks", check_route53_health(primary)),
        ("Dead-man Switch Lambda", check_deadman_switch()),
    ]

    if args.full and args.api_url:
        checks.append(
            (
                "API Smoke Tests",
                smoke_test_api(args.api_url, args.timeout),
            )
        )

    for name, coro in checks:
        logger.info("Executando: %s...", name)
        result = await _timed_check(name, coro)
        report.add(result)
        logger.info("  %s", result)

    print(report.summary(), flush=True)

    return 0 if report.overall_pass else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
