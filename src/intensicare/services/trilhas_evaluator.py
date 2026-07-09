"""Stateless evaluation loop for Trilhas Engine.

Evaluates compiled predicates against patient data and returns firing decisions
with definition_version + content_hash stamping per ADR-0020/ADR-021.

Pipeline:  YAML definitions -> Compiler -> Predicate AST -> Evaluator -> Firing decisions

Suppression tracking (cooldown, rate limit) is Redis-backed with an in-memory
fallback when Redis is unavailable.

Reference: _work/alerts/schema/pathway.schema.json
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import redis.asyncio as aioredis

from intensicare.services.trilhas_compiler import (
    CompiledPredicate,
    EvaluationResult,
    PredicateCompiler,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CriterionFiring:
    """A single criterion that fired (or was suppressed) during evaluation.

    Stamped with definition_version + content_hash per ADR-021 for
    content-addressed traceability.
    """

    pathway_id: int
    pathway_name: str
    pathway_slug: str
    definition_version: str
    content_hash: str
    criterion_id: str
    criterion_name: str
    category: str
    result: EvaluationResult
    suppressed: bool = False
    suppress_reason: str = ""


@dataclass
class AlertFiring:
    """Aggregated alert for a patient-pathway evaluation.

    Contains all criterion firings for one pathway evaluation,
    plus aggregated severity and recommendations.
    """

    mpi_id: str
    pathway_id: int
    pathway_name: str
    pathway_slug: str
    definition_version: str
    content_hash: str
    firings: list[CriterionFiring] = field(default_factory=list)
    overall_severity: str = "normal"
    total_score: int = 0
    recommendations: list[str] = field(default_factory=list)
    suppressed_count: int = 0


# ---------------------------------------------------------------------------
# Suppression Tracker (Redis-backed with in-memory fallback)
# ---------------------------------------------------------------------------


class SuppressionTracker:
    """Redis-backed cooldown and rate-limit tracker with in-memory fallback.

    Tracks per (mpi_id, pathway_id, criterion_id):
      - cooldown: Redis key with TTL (or in-memory timestamp)
      - rate limit: Redis counter with 1h TTL (or in-memory timestamp list)

    When Redis is available, operations are atomic and shared across workers.
    Falls back to thread-safe in-memory dicts when Redis is unreachable.
    """

    COOLDOWN_PREFIX = "suppress:cooldown"
    RATE_PREFIX = "suppress:rate"
    RATE_TTL_SECONDS = 3600  # 1 hour

    def __init__(self) -> None:
        # Redis client — lazily initialised
        self._redis: aioredis.Redis | None = None
        self._redis_attempted: bool = False
        # In-memory fallback
        self._lock = threading.Lock()
        self._last_fired: dict[tuple[str, int, str], datetime] = {}
        self._hourly_fires: dict[tuple[str, int], list[datetime]] = defaultdict(list)

    def _get_redis(self) -> aioredis.Redis | None:
        """Lazily get Redis client. Returns None if unavailable."""
        if self._redis_attempted:
            return self._redis
        self._redis_attempted = True
        try:
            from intensicare.core.redis import get_redis

            self._redis = get_redis()
            logger.debug("SuppressionTracker: using Redis backend")
        except Exception:
            logger.warning(
                "SuppressionTracker: Redis unavailable, falling back to in-memory"
            )
        return self._redis

    @staticmethod
    def _cooldown_key(mpi_id: str, pathway_id: int, criterion_id: str) -> str:
        return f"{SuppressionTracker.COOLDOWN_PREFIX}:{mpi_id}:{pathway_id}:{criterion_id}"

    @staticmethod
    def _rate_key(mpi_id: str, pathway_id: int, criterion_id: str) -> str:
        return f"{SuppressionTracker.RATE_PREFIX}:{mpi_id}:{pathway_id}:{criterion_id}"

    async def check_and_record(
        self,
        mpi_id: str,
        pathway_id: int,
        criterion_id: str,
        cooldown_minutes: int,
        rate_limit_per_hour: int,
    ) -> tuple[bool, str]:
        """Check if firing is suppressed and record it if not.

        Args:
            mpi_id: Patient identifier.
            pathway_id: Pathway ID.
            criterion_id: Criterion ID.
            cooldown_minutes: Minimum minutes between repeated firings.
            rate_limit_per_hour: Maximum firings per hour.

        Returns:
            Tuple of (allowed: bool, reason: str).
        """
        r = self._get_redis()

        if r is not None:
            return await self._check_and_record_redis(
                mpi_id, pathway_id, criterion_id,
                cooldown_minutes, rate_limit_per_hour,
                r,
            )
        return self._check_and_record_memory(
            mpi_id, pathway_id, criterion_id,
            cooldown_minutes, rate_limit_per_hour,
        )

    async def _check_and_record_redis(
        self,
        mpi_id: str,
        pathway_id: int,
        criterion_id: str,
        cooldown_minutes: int,
        rate_limit_per_hour: int,
        r: aioredis.Redis,
    ) -> tuple[bool, str]:
        """Redis-backed suppression check."""
        cooldown_key = self._cooldown_key(mpi_id, pathway_id, criterion_id)
        rate_key = self._rate_key(mpi_id, pathway_id, criterion_id)

        # ── Cooldown check ──
        if cooldown_minutes > 0:
            exists: int = await r.exists(cooldown_key)
            if exists:
                ttl: int = await r.ttl(cooldown_key)
                remaining = ttl if ttl > 0 else 0
                return False, (
                    f"Cooldown: {cooldown_minutes}min not elapsed "
                    f"({remaining}s remaining)"
                )

        # ── Rate limit check ──
        if rate_limit_per_hour > 0:
            count: int = await r.incr(rate_key)
            if count == 1:
                await r.expire(rate_key, self.RATE_TTL_SECONDS)
            if count > rate_limit_per_hour:
                return False, (
                    f"Rate limit: {rate_limit_per_hour}/hour exceeded "
                    f"({count - 1} fires in last hour)"
                )

        # ── Record cooldown ──
        if cooldown_minutes > 0:
            cooldown_seconds = cooldown_minutes * 60
            await r.setex(cooldown_key, cooldown_seconds, "1")

        return True, ""

    def _check_and_record_memory(
        self,
        mpi_id: str,
        pathway_id: int,
        criterion_id: str,
        cooldown_minutes: int,
        rate_limit_per_hour: int,
    ) -> tuple[bool, str]:
        """In-memory fallback suppression check (thread-safe)."""
        now = datetime.now(timezone.utc)

        with self._lock:
            # ── Cooldown check ──
            key: tuple[str, int, str] = (mpi_id, pathway_id, criterion_id)
            if cooldown_minutes > 0 and key in self._last_fired:
                elapsed = now - self._last_fired[key]
                if elapsed < timedelta(minutes=cooldown_minutes):
                    remaining = int(
                        (timedelta(minutes=cooldown_minutes) - elapsed).total_seconds()
                    )
                    return False, (
                        f"Cooldown: {cooldown_minutes}min not elapsed "
                        f"({remaining}s remaining)"
                    )

            # ── Rate limit check ──
            rl_key: tuple[str, int] = (mpi_id, pathway_id)
            if rate_limit_per_hour > 0:
                cutoff = now - timedelta(hours=1)
                # Prune old entries
                fires = self._hourly_fires[rl_key]
                fires[:] = [t for t in fires if t > cutoff]

                if len(fires) >= rate_limit_per_hour:
                    return False, (
                        f"Rate limit: {rate_limit_per_hour}/hour exceeded "
                        f"({len(fires)} fires in last hour)"
                    )

                fires.append(now)

            # ── Record fire ──
            if cooldown_minutes > 0:
                self._last_fired[key] = now

            return True, ""

    async def reset(self) -> None:
        """Reset all tracking state (useful for tests)."""
        r = self._get_redis()
        if r is not None:
            # Delete all keys with our prefixes
            # Use SCAN to avoid blocking Redis with KEYS in production
            cursor = 0
            while True:
                cursor, keys = await r.scan(
                    cursor, match=f"{self.COOLDOWN_PREFIX}:*", count=100,
                )
                if keys:
                    await r.delete(*keys)
                if cursor == 0:
                    break
            cursor = 0
            while True:
                cursor, keys = await r.scan(
                    cursor, match=f"{self.RATE_PREFIX}:*", count=100,
                )
                if keys:
                    await r.delete(*keys)
                if cursor == 0:
                    break
        else:
            with self._lock:
                self._last_fired.clear()
                self._hourly_fires.clear()


# ---------------------------------------------------------------------------
# TrilhasEvaluator
# ---------------------------------------------------------------------------

# Canonical severity ordering for aggregation
_SEVERITY_ORDER: dict[str, int] = {
    "normal": 0,
    "watch": 1,
    "urgent": 2,
    "critical": 3,
}


class TrilhasEvaluator:
    """Stateless predicate evaluator for care pathways.

    Evaluates compiled predicates against patient data, stamps results
    with definition_version + content_hash, and applies suppression rules.

    Usage::

        evaluator = TrilhasEvaluator()
        firings = await evaluator.evaluate_pathway(pathway_def, mpi_id, patient_data)
        alert = evaluator.build_alert(mpi_id, pathway_def, firings)
    """

    def __init__(self, compiler: PredicateCompiler | None = None) -> None:
        """Initialize evaluator with optional compiler.

        Args:
            compiler: PredicateCompiler instance. Creates default if None.
        """
        self._compiler = compiler or PredicateCompiler()
        self._suppression = SuppressionTracker()

    # ── Public API ───────────────────────────────────────────────────────

    async def evaluate_pathway(
        self,
        pathway_def: dict[str, Any],
        mpi_id: str,
        patient_data: dict[str, Any],
        *,
        apply_suppression: bool = True,
    ) -> list[CriterionFiring]:
        """Evaluate all criteria in a pathway definition against patient data.

        Args:
            pathway_def: Raw YAML pathway definition dict (with pathway, criteria,
                         suppression keys).
            mpi_id: Patient identifier.
            patient_data: Dict mapping input names to values.
            apply_suppression: If False, skip cooldown/rate-limit checks.

        Returns:
            List of CriterionFiring for criteria that were met (or suppressed).
            Criteria that are not met return no firing.
        """
        pathway_meta: dict[str, Any] = pathway_def.get("pathway", {})
        criteria: list[dict[str, Any]] = pathway_def.get("criteria", [])
        suppression: dict[str, Any] = pathway_def.get("suppression", {})

        pathway_id: int = pathway_meta.get("id", 0)
        pathway_name: str = pathway_meta.get("name", "")
        pathway_slug: str = pathway_meta.get("slug", "")
        definition_version: str = pathway_meta.get("version", "0.0.0")
        content_hash: str = pathway_meta.get("content_hash", "")

        cooldown_minutes: int = suppression.get("cooldown_minutes", 0)
        rate_limit_per_hour: int = suppression.get("rate_limit_per_hour", 0)

        firings: list[CriterionFiring] = []

        for criterion in criteria:
            criterion_id: str = criterion.get("id", "")
            criterion_name: str = criterion.get("name", "")
            category: str = criterion.get("category", "")
            predicate_dict: dict[str, Any] = criterion.get("predicate", {})

            if not predicate_dict:
                logger.debug(
                    "Criterion %s in pathway %s has no predicate, skipping",
                    criterion_id, pathway_name,
                )
                continue

            # Compile predicate (could be pre-compiled and cached by engine)
            try:
                compiled = self._compiler.compile(predicate_dict)
            except ValueError as exc:
                logger.warning(
                    "Failed to compile predicate for criterion %s in pathway %s: %s",
                    criterion_id, pathway_name, exc,
                )
                continue

            # Evaluate against patient data
            try:
                result = self._compiler.evaluate(compiled, patient_data)
            except KeyError:
                logger.debug(
                    "Input '%s' not in patient_data for criterion %s in pathway %s",
                    compiled.input_name, criterion_id, pathway_name,
                )
                continue

            # Only fire if the criterion is met
            if not result.met:
                continue

            firing = CriterionFiring(
                pathway_id=pathway_id,
                pathway_name=pathway_name,
                pathway_slug=pathway_slug,
                definition_version=definition_version,
                content_hash=content_hash,
                criterion_id=criterion_id,
                criterion_name=criterion_name,
                category=category,
                result=result,
                suppressed=False,
                suppress_reason="",
            )

            # Apply suppression
            if apply_suppression:
                allowed, reason = await self._suppression.check_and_record(
                    mpi_id=mpi_id,
                    pathway_id=pathway_id,
                    criterion_id=criterion_id,
                    cooldown_minutes=cooldown_minutes,
                    rate_limit_per_hour=rate_limit_per_hour,
                )
                if not allowed:
                    firing.suppressed = True
                    firing.suppress_reason = reason
                    logger.debug(
                        "Suppressed criterion %s for patient %s in pathway %s: %s",
                        criterion_id, mpi_id, pathway_name, reason,
                    )

            firings.append(firing)

        return firings

    def build_alert(
        self,
        mpi_id: str,
        pathway_def: dict[str, Any],
        firings: list[CriterionFiring],
    ) -> AlertFiring:
        """Build an AlertFiring from evaluated criterion firings.

        Aggregates severity as the maximum across all firings and sums scores.

        Args:
            mpi_id: Patient identifier.
            pathway_def: Raw YAML pathway definition.
            firings: List of CriterionFiring from evaluate_pathway().

        Returns:
            AlertFiring with aggregated severity, score, and recommendations.
        """
        pathway_meta: dict[str, Any] = pathway_def.get("pathway", {})
        evidence: dict[str, Any] = pathway_def.get("evidence", {})

        pathway_id: int = pathway_meta.get("id", 0)
        pathway_name: str = pathway_meta.get("name", "")
        pathway_slug: str = pathway_meta.get("slug", "")
        definition_version: str = pathway_meta.get("version", "0.0.0")
        content_hash: str = pathway_meta.get("content_hash", "")

        # Filter out suppressed firings for severity/score computation
        active_firings = [f for f in firings if not f.suppressed]
        suppressed_count = sum(1 for f in firings if f.suppressed)

        # Aggregate severity: maximum across active firings
        overall_severity = "normal"
        if active_firings:
            for f in active_firings:
                if _SEVERITY_ORDER.get(f.result.severity, 0) > _SEVERITY_ORDER.get(
                    overall_severity, 0
                ):
                    overall_severity = f.result.severity

        total_score = sum(f.result.score for f in active_firings)

        # Extract recommendations from evidence
        recommendations: list[str] = evidence.get("recommendations", [])

        return AlertFiring(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            pathway_name=pathway_name,
            pathway_slug=pathway_slug,
            definition_version=definition_version,
            content_hash=content_hash,
            firings=firings,
            overall_severity=overall_severity,
            total_score=total_score,
            recommendations=recommendations,
            suppressed_count=suppressed_count,
        )

    async def evaluate_and_build(
        self,
        pathway_def: dict[str, Any],
        mpi_id: str,
        patient_data: dict[str, Any],
        *,
        apply_suppression: bool = True,
    ) -> AlertFiring:
        """Convenience: evaluate pathway and build alert in one call.

        Args:
            pathway_def: Raw YAML pathway definition.
            mpi_id: Patient identifier.
            patient_data: Dict mapping input names to values.
            apply_suppression: If False, skip cooldown/rate-limit checks.

        Returns:
            AlertFiring with all firings and aggregated metadata.
        """
        firings = await self.evaluate_pathway(
            pathway_def, mpi_id, patient_data, apply_suppression=apply_suppression,
        )
        return self.build_alert(mpi_id, pathway_def, firings)

    async def reset_suppression(self) -> None:
        """Reset suppression state (useful for tests)."""
        await self._suppression.reset()
