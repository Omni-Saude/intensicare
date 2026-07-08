'use client';

import React, { useState, useMemo, useCallback } from 'react';
import {
  Activity,
  TrendingDown,
  TrendingUp,
  Minus,
  Brain,
  Heart,
  Wind,
  AlertTriangle,
  Loader2,
  Clock,
  Shield,
  Droplets,
  ChevronDown,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import ClinicalTimeline, {
  type TimelineEvent,
  type TimelineStatus,
} from '@/components/ClinicalTimeline';
import {
  type DeteriorationScore,
  type DeteriorationScoreValue,
  type DeteriorationDomain,
  type DeteriorationCriteria,
  type CriteriaStatus,
  type DeteriorationTrend,
  SCORE_LABELS,
  SCORE_SHORT_LABELS,
  SCORE_COLORS,
  SCORE_ORDER,
  DOMAIN_LABELS,
  DOMAIN_ICON_NAMES,
  STATUS_LABELS,
  STATUS_COLORS,
  TREND_LABELS,
  MOCK_SCORE,
  MOCK_HISTORY,
  getScoreColor,
  getDomainLabel,
  getTrendIcon,
} from '@/lib/deterioration-types';

// ─── Domain Icon Component ─────────────────────────────────────────────────

const domainIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  Wind,
  Heart,
  Activity,
  Brain,
  Droplets,
};

function DomainIcon({
  domain,
  className,
  style,
}: {
  domain: DeteriorationDomain;
  className?: string;
  style?: React.CSSProperties;
}): React.ReactElement {
  const iconName = DOMAIN_ICON_NAMES[domain];
  const Icon = domainIcons[iconName] ?? Activity;
  return <Icon className={className} style={style} aria-hidden="true" />;
}

// ─── Trend Icon Component ──────────────────────────────────────────────────

const trendIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  TrendingDown,
  TrendingUp,
  Minus,
};

function TrendIconComponent({
  trend,
  className,
  style,
}: {
  trend: DeteriorationTrend;
  className?: string;
  style?: React.CSSProperties;
}): React.ReactElement {
  const iconName = getTrendIcon(trend);
  const Icon = trendIcons[iconName] ?? Minus;
  return <Icon className={className} style={style} aria-hidden="true" />;
}

// ─── Score Gauge ───────────────────────────────────────────────────────────

function ScoreGauge({
  score,
  trend,
}: {
  score: DeteriorationScoreValue;
  trend: DeteriorationTrend;
}): React.ReactElement {
  const colors = getScoreColor(score);
  const scoreIndex = SCORE_ORDER.indexOf(score);
  const cx = 150;
  const cy = 150;
  const outerR = 130;
  const innerR = 90;
  const strokeWidth = outerR - innerR; // 40

  // Build 5 arc segments for the donut
  const totalSegments = SCORE_ORDER.length;
  const gapAngle = 4; // degrees between segments
  const usableAngle = 270; // total angle span
  const segmentSpan = (usableAngle - gapAngle * (totalSegments - 1)) / totalSegments;
  const startAngleOffset = 135; // start from bottom-left (225-90=135 in SVG coords)

  function polarToCartesian(
    cx: number,
    cy: number,
    r: number,
    angleDeg: number,
  ): { x: number; y: number } {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  }

  function describeArc(
    cx: number,
    cy: number,
    r: number,
    startAngle: number,
    endAngle: number,
  ): string {
    const start = polarToCartesian(cx, cy, r, endAngle);
    const end = polarToCartesian(cx, cy, r, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    return [
      'M',
      start.x,
      start.y,
      'A',
      r,
      r,
      0,
      largeArcFlag,
      0,
      end.x,
      end.y,
    ].join(' ');
  }

  // Needle angle: point to the middle of the active segment
  const needleAngle =
    startAngleOffset + scoreIndex * (segmentSpan + gapAngle) + segmentSpan / 2;

  const needleLen = outerR - 10;
  const needleTip = polarToCartesian(cx, cy, needleLen, needleAngle);
  const needleBaseLeft = polarToCartesian(cx, cy, 15, needleAngle - 90);
  const needleBaseRight = polarToCartesian(cx, cy, 15, needleAngle + 90);

  return (
    <div className="flex flex-col items-center" role="img" aria-label={`Score de deterioração: ${SCORE_LABELS[score]}`}>
      <svg
        viewBox="0 0 300 260"
        className="w-full max-w-[300px] h-auto"
        aria-hidden="true"
      >
        {/* Background arcs (all segments) */}
        {SCORE_ORDER.map((s, i) => {
          const segStart = startAngleOffset + i * (segmentSpan + gapAngle);
          const segEnd = segStart + segmentSpan;
          const segColors = SCORE_COLORS[s];
          const isActive = i === scoreIndex;
          const midR = (outerR + innerR) / 2;

          return (
            <g key={s}>
              {/* Outer arc */}
              <path
                d={describeArc(cx, cy, outerR, segStart, segEnd)}
                fill="none"
                stroke={isActive ? segColors.signal : 'var(--semantic-surface-overlay)'}
                strokeWidth={strokeWidth}
                strokeLinecap="butt"
                opacity={isActive ? 1 : 0.35}
              />
              {/* Score label for active segment */}
              {isActive && (
                <text
                  x={polarToCartesian(cx, cy, midR, (segStart + segEnd) / 2).x}
                  y={polarToCartesian(cx, cy, midR, (segStart + segEnd) / 2).y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  className="text-xs font-bold"
                  fill={segColors.onFill}
                  fontSize="12"
                >
                  {s}
                </text>
              )}
            </g>
          );
        })}

        {/* Needle */}
        <polygon
          points={`${needleTip.x},${needleTip.y} ${needleBaseLeft.x},${needleBaseLeft.y} ${needleBaseRight.x},${needleBaseRight.y}`}
          fill="var(--semantic-text-primary)"
        />

        {/* Center dot */}
        <circle
          cx={cx}
          cy={cy}
          r={10}
          fill="var(--semantic-text-primary)"
        />

        {/* Center score value */}
        <text
          x={cx}
          y={cy - 15}
          textAnchor="middle"
          dominantBaseline="central"
          style={{ fill: colors.signal }}
          fontSize="36"
          fontWeight="bold"
        >
          {score}
        </text>

        {/* Center label */}
        <text
          x={cx}
          y={cy + 55}
          textAnchor="middle"
          dominantBaseline="central"
          style={{ fill: 'var(--semantic-text-secondary)' }}
          fontSize="11"
        >
          {SCORE_SHORT_LABELS[score]}
        </text>
      </svg>

      {/* Trend indicator below gauge */}
      <div className="flex items-center gap-1.5 mt-2">
        <TrendIconComponent
          trend={trend}
          className="w-4 h-4"
          style={{ color: colors.signal }}
        />
        <span
          className="text-sm font-medium"
          style={{ color: colors.signal }}
        >
          {TREND_LABELS[trend]}
        </span>
      </div>
    </div>
  );
}

// ─── Skeleton ──────────────────────────────────────────────────────────────

function DeteriorationSkeleton(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-6" role="status" aria-label="Carregando avaliação de deterioração">
      {/* Gauge skeleton */}
      <div className="flex justify-center">
        <div
          className="rounded-full"
          style={{
            width: '260px',
            height: '260px',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
        />
      </div>

      {/* Domain cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-xl border p-4"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className="w-8 h-8 rounded-lg"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div
                className="h-4 rounded w-24"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            </div>
            <div className="space-y-2">
              <div
                className="h-3 rounded w-full"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div
                className="h-3 rounded w-3/4"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Domain Criteria Badge ─────────────────────────────────────────────────

function StatusBadge({ status }: { status: CriteriaStatus }): React.ReactElement {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
      style={{
        backgroundColor:
          status === 'critical'
            ? 'var(--clinical-severity-critical-wash)'
            : status === 'alert'
              ? 'var(--clinical-severity-watch-wash)'
              : 'var(--clinical-severity-normal-wash)',
        color:
          status === 'critical'
            ? 'var(--clinical-severity-critical-on-surface)'
            : status === 'alert'
              ? 'var(--clinical-severity-watch-on-surface)'
              : 'var(--clinical-severity-normal-on-surface)',
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
        style={{ backgroundColor: STATUS_COLORS[status] }}
        aria-hidden="true"
      />
      {STATUS_LABELS[status]}
    </span>
  );
}

// ─── Domain Card ────────────────────────────────────────────────────────────

function DomainCard({
  domain,
  criteria,
}: {
  domain: DeteriorationDomain;
  criteria: DeteriorationCriteria[];
}): React.ReactElement {
  const [expanded, setExpanded] = useState(false);

  const normalCount = criteria.filter((c) => c.status === 'normal').length;
  const alertCount = criteria.filter((c) => c.status === 'alert').length;
  const criticalCount = criteria.filter((c) => c.status === 'critical').length;

  // Determine overall domain status
  const domainStatus: CriteriaStatus =
    criticalCount > 0 ? 'critical' : alertCount > 0 ? 'alert' : 'normal';

  const statusColor =
    domainStatus === 'critical'
      ? 'var(--clinical-severity-critical-signal)'
      : domainStatus === 'alert'
        ? 'var(--clinical-severity-watch-signal)'
        : 'var(--clinical-severity-normal-signal)';

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
        aria-expanded={expanded}
        aria-label={`${getDomainLabel(domain)} — ${STATUS_LABELS[domainStatus]}`}
      >
        <div className="flex items-center gap-3 min-w-0">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: `${statusColor}20` }}
          >
            <DomainIcon domain={domain} className="w-4 h-4" style={{ color: statusColor }} />
          </div>
          <div className="min-w-0">
            <h3
              className="text-sm font-semibold truncate"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              {getDomainLabel(domain)}
            </h3>
            <div className="flex items-center gap-2 mt-0.5">
              <StatusBadge status={domainStatus} />
              <span
                className="text-xs"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {normalCount} normal · {alertCount} alerta · {criticalCount} crítico
              </span>
            </div>
          </div>
        </div>
        {expanded ? (
          <ChevronDown
            className="w-4 h-4 flex-shrink-0"
            style={{ color: 'var(--semantic-text-secondary)' }}
            aria-hidden="true"
          />
        ) : (
          <ChevronRight
            className="w-4 h-4 flex-shrink-0"
            style={{ color: 'var(--semantic-text-secondary)' }}
            aria-hidden="true"
          />
        )}
      </button>

      {/* Status bar */}
      <div className="px-4 pb-2">
        <div className="flex h-1.5 rounded-full overflow-hidden gap-0.5">
          {normalCount > 0 && (
            <div
              className="h-full rounded-full"
              style={{
                backgroundColor: 'var(--clinical-severity-normal-signal)',
                flex: normalCount,
              }}
            />
          )}
          {alertCount > 0 && (
            <div
              className="h-full rounded-full"
              style={{
                backgroundColor: 'var(--clinical-severity-watch-signal)',
                flex: alertCount,
              }}
            />
          )}
          {criticalCount > 0 && (
            <div
              className="h-full rounded-full"
              style={{
                backgroundColor: 'var(--clinical-severity-critical-signal)',
                flex: criticalCount,
              }}
            />
          )}
        </div>
      </div>

      {/* Expanded criteria list */}
      {expanded && (
        <div
          className="border-t px-4 py-3 space-y-2"
          style={{ borderColor: 'var(--semantic-border-default)' }}
        >
          {criteria.map((criterion) => (
            <div
              key={`${criterion.domain}-${criterion.name}`}
              className="flex items-start justify-between gap-2 py-1.5"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <StatusBadge status={criterion.status} />
                  <span
                    className="text-sm font-medium truncate"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {criterion.name}
                  </span>
                </div>
                {(criterion.value || criterion.threshold || criterion.alert_id) && (
                  <div className="flex items-center gap-2 mt-1 ml-1">
                    {criterion.value && (
                      <span
                        className="text-xs"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        Valor: <span className="font-mono font-medium">{criterion.value}</span>
                      </span>
                    )}
                    {criterion.threshold && (
                      <span
                        className="text-xs"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        Limiar: <span className="font-mono">{criterion.threshold}</span>
                      </span>
                    )}
                    {criterion.alert_id && (
                      <span
                        className="text-xs px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 font-mono"
                      >
                        {criterion.alert_id}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────

function ClinicalDeteriorationPage(): React.ReactElement {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // In a real app, these would come from API; using mock data per spec
  const score: DeteriorationScore | null = MOCK_SCORE;
  const history: DeteriorationScore[] = MOCK_HISTORY;

  const handleRetry = useCallback(() => {
    setError(null);
    setLoading(true);
    // Simulate retry
    setTimeout(() => setLoading(false), 800);
  }, []);

  // Build timeline events from history
  const timelineEvents: TimelineEvent[] = useMemo(() => {
    return history
      .map((entry) => {
        const trendIconName = getTrendIcon(entry.trend);
        const trendArrow =
          entry.trend === 'worsening'
            ? ' ↑'
            : entry.trend === 'improving'
              ? ' ↓'
              : entry.trend === 'stable'
                ? ' →'
                : '';

        let status: TimelineStatus = 'completed';
        if (entry.score === '3-') status = 'overdue';
        else if (entry.score === '3+' || entry.score === '1-') status = 'in-progress';

        return {
          id: entry.id,
          status,
          label: `Score ${entry.score}${trendArrow} — ${SCORE_SHORT_LABELS[entry.score]}`,
          description: `${entry.domains_affected} domínio(s) afetado(s) · ${TREND_LABELS[entry.trend]}`,
          timestamp: entry.assessed_at,
        };
      })
      .sort(
        (a, b) =>
          new Date(b.timestamp || 0).getTime() -
          new Date(a.timestamp || 0).getTime(),
      );
  }, [history]);

  // Group criteria by domain for domain breakdown
  const domainCriteria = useMemo(() => {
    const map: Record<DeteriorationDomain, DeteriorationCriteria[]> = {
      respiratory: [],
      hemodynamic: [],
      sepsis: [],
      neurologic: [],
      renal: [],
    };
    if (score) {
      for (const c of score.criteria) {
        map[c.domain].push(c);
      }
    }
    return map;
  }, [score]);

  // Domains that have criteria
  const affectedDomains = useMemo(
    () =>
      (Object.entries(domainCriteria) as [DeteriorationDomain, DeteriorationCriteria[]][]).filter(
        ([, criteria]) => criteria.length > 0,
      ),
    [domainCriteria],
  );

  // ─── Loading ──────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="mb-6">
            <h1
              className="text-2xl font-bold"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              Deterioração Clínica
            </h1>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Detecção precoce de piora clínica multi-domínio
            </p>
          </div>
          <DeteriorationSkeleton />
        </div>
      </Layout>
    );
  }

  // ─── Error ────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="mb-6">
            <h1
              className="text-2xl font-bold"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              Deterioração Clínica
            </h1>
          </div>
          <div
            className="border rounded-xl p-6"
            style={{
              color: 'var(--clinical-severity-critical-on-surface)',
              backgroundColor: 'var(--clinical-severity-critical-wash)',
              borderColor: 'var(--clinical-severity-critical-signal)',
            }}
            role="alert"
            aria-live="assertive"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle
                className="w-6 h-6 flex-shrink-0 mt-0.5"
                style={{ color: 'var(--clinical-severity-critical-signal)' }}
                aria-hidden="true"
              />
              <div>
                <h2 className="font-semibold text-lg">Falha ao carregar avaliação</h2>
                <p className="text-sm mt-1 opacity-90">{error}</p>
                <button
                  onClick={handleRetry}
                  className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                  style={{
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                    borderColor: 'var(--semantic-border-default)',
                    border: '1px solid var(--semantic-border-default)',
                  }}
                >
                  <RefreshCw className="w-4 h-4" aria-hidden="true" />
                  Tentar novamente
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // ─── Empty ────────────────────────────────────────────────────────────────
  if (!score) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-20">
            <Shield
              className="w-12 h-12 mx-auto mb-4"
              style={{ color: 'var(--semantic-text-secondary)', opacity: 0.5 }}
              aria-hidden="true"
            />
            <p
              className="font-medium"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Nenhuma avaliação de deterioração disponível
            </p>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Nenhum paciente apresenta critérios de deterioração no momento.
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  // ─── Main Content ────────────────────────────────────────────────────────
  const scoreColors = getScoreColor(score.score);

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* ── Header ─────────────────────────────────────────────────────── */}
        <div className="mb-6">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: `${scoreColors.signal}20` }}
            >
              <Activity className="w-5 h-5" style={{ color: scoreColors.signal }} aria-hidden="true" />
            </div>
            <div>
              <h1
                className="text-2xl font-bold"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                Deterioração Clínica
              </h1>
              <p
                className="text-sm mt-0.5"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Detecção precoce de piora clínica multi-domínio
              </p>
            </div>
          </div>

          {/* Assessment meta */}
          <div
            className="flex flex-wrap items-center gap-4 mt-3 text-xs"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" aria-hidden="true" />
              {new Date(score.assessed_at).toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            <span>Avaliado por: {score.assessed_by}</span>
            <span>MPI: {score.mpi_id}</span>
          </div>
        </div>

        {/* ── Gauge + Summary row ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Gauge */}
          <div className="flex justify-center lg:col-span-1">
            <ScoreGauge score={score.score} trend={score.trend} />
          </div>

          {/* Summary panel */}
          <div className="lg:col-span-2 space-y-4">
            {/* Score info card */}
            <div
              className="rounded-xl border p-5"
              style={{
                borderColor: scoreColors.signal,
                backgroundColor: `${scoreColors.wash}18`,
              }}
            >
              <h2
                className="text-lg font-bold mb-1"
                style={{ color: scoreColors.onSurface }}
              >
                {SCORE_LABELS[score.score]}
              </h2>

              {/* Domains affected */}
              <div className="flex items-center gap-2 mt-3">
                <span
                  className="text-sm font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  {score.domains_affected} domínio{score.domains_affected !== 1 ? 's' : ''} afetado{score.domains_affected !== 1 ? 's' : ''}
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {affectedDomains.map(([domain]) => {
                  const critList = domainCriteria[domain];
                  const hasCritical = critList.some((c) => c.status === 'critical');
                  const hasAlert = critList.some((c) => c.status === 'alert');
                  const badgeColor = hasCritical
                    ? 'var(--clinical-severity-critical-signal)'
                    : hasAlert
                      ? 'var(--clinical-severity-watch-signal)'
                      : 'var(--clinical-severity-normal-signal)';
                  return (
                    <span
                      key={domain}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium"
                      style={{
                        backgroundColor: `${badgeColor}18`,
                        color: badgeColor,
                        borderColor: `${badgeColor}40`,
                        border: '1px solid',
                      }}
                    >
                      <DomainIcon domain={domain} className="w-3 h-3" />
                      {getDomainLabel(domain)}
                    </span>
                  );
                })}
              </div>

              {/* Trend */}
              <div className="flex items-center gap-2 mt-3">
                <TrendIconComponent
                  trend={score.trend}
                  className="w-4 h-4"
                  style={{ color: scoreColors.signal }}
                />
                <span
                  className="text-sm font-medium"
                  style={{ color: scoreColors.signal }}
                >
                  Tendência: {TREND_LABELS[score.trend]}
                </span>
              </div>
            </div>

            {/* Recommendation card */}
            <div
              className="rounded-xl border p-5"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <h3
                className="text-sm font-semibold mb-2 flex items-center gap-2"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                <AlertTriangle className="w-4 h-4" style={{ color: scoreColors.signal }} aria-hidden="true" />
                Recomendação Clínica
              </h3>
              <p
                className="text-sm leading-relaxed"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {score.recommendation}
              </p>
            </div>
          </div>
        </div>

        {/* ── Domain Breakdown ───────────────────────────────────────────── */}
        <section>
          <h2
            className="text-lg font-bold mb-4"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Discriminação por Domínio
          </h2>
          {affectedDomains.length === 0 ? (
            <div
              className="rounded-xl border p-6 text-center"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <p style={{ color: 'var(--semantic-text-secondary)' }}>
                Nenhum critério de deterioração identificado nos domínios monitorados.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {affectedDomains.map(([domain, criteria]) => (
                <DomainCard key={domain} domain={domain} criteria={criteria} />
              ))}
            </div>
          )}
        </section>

        {/* ── Timeline ───────────────────────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Clock
              className="w-5 h-5"
              style={{ color: 'var(--semantic-text-secondary)' }}
              aria-hidden="true"
            />
            <h2
              className="text-lg font-bold"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              Histórico de Avaliações
            </h2>
          </div>
          <div
            className="rounded-xl border p-4"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <ClinicalTimeline
              events={timelineEvents}
              domain="general"
              isLoading={false}
              error={null}
            />
          </div>
        </section>
      </div>
    </Layout>
  );
}

// ─── Export (wrapped in ErrorBoundary per padrão) ──────────────────────────

export default function ClinicalDeteriorationPageWithBoundary(): React.ReactElement {
  return (
    <ErrorBoundary>
      <ClinicalDeteriorationPage />
    </ErrorBoundary>
  );
}
