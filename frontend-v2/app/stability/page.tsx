'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Heart,
  Activity,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  AlertCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  Minus,
  Filter,
  Users,
  ChevronDown,
  Clock,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import StabilityHeatmap from '@/components/StabilityHeatmap';
import {
  type StabilityCriterion,
  type StabilityCategory,
  type StabilitySeverity,
  type StabilityTrend,
  type StabilityTrendPoint,
  type StabilityDirection,
  STABILITY_CATEGORIES,
  CATEGORY_LABELS,
  MOCK_STATUS,
  MOCK_TREND,
  MOCK_CRITERIA,
  getCategoryLabel,
  getSeverityLabel,
  getSeveritySignalToken,
  getSeverityFillToken,
  getSeverityOnFillToken,
  getSeverityOnSurfaceToken,
  getSeverityWashToken,
  getDirectionLabel,
  countAlteredCriteria,
  computeSeverity,
} from '@/lib/stability-types';

// ─── Mock Patients ──────────────────────────────────────────────────────────

interface PatientOption {
  mpiId: string;
  displayName: string;
  bedId: string;
}

const MOCK_PATIENTS: PatientOption[] = [
  { mpiId: 'MPI-2026-0742', displayName: 'João Silva', bedId: 'UTI-1-03' },
  { mpiId: 'MPI-2026-0815', displayName: 'Maria Santos', bedId: 'UTI-2-07' },
  { mpiId: 'MPI-2026-0829', displayName: 'Carlos Oliveira', bedId: 'UTI-1-05' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatDatePT(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  } catch {
    return '--/--';
  }
}

function getDirectionIcon(direction: StabilityDirection): React.ReactElement {
  if (direction === 'improving') {
    return <TrendingDown className="w-5 h-5" aria-hidden="true" />;
  }
  if (direction === 'worsening') {
    return <TrendingUp className="w-5 h-5" aria-hidden="true" />;
  }
  return <Minus className="w-5 h-5" aria-hidden="true" />;
}

function getDirectionColor(direction: StabilityDirection): string {
  if (direction === 'improving') return 'var(--clinical-stability-estavel-signal-dark)';
  if (direction === 'worsening') return 'var(--clinical-stability-critico-signal-dark)';
  return 'var(--semantic-text-secondary)';
}

// ─── Severity Badge ─────────────────────────────────────────────────────────

function StabilitySeverityBadge({
  severity,
}: {
  severity: StabilitySeverity;
}): React.ReactElement {
  const label = getSeverityLabel(severity);
  const fillBg = getSeverityFillToken(severity);
  const fillText = getSeverityOnFillToken(severity);
  const pulse = severity === 'critico';

  const Icon =
    severity === 'estavel'
      ? CheckCircle2
      : severity === 'atencao'
      ? AlertCircle
      : XCircle;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
        pulse ? 'animate-pulse-critical' : ''
      }`}
      style={{ backgroundColor: fillBg, color: fillText }}
      aria-label={`Severidade: ${label}`}
    >
      <Icon className="w-3.5 h-3.5" aria-hidden="true" />
      {label}
    </span>
  );
}

// ─── Score Card ─────────────────────────────────────────────────────────────

function ScoreCard({
  score,
  severity,
  isLoading,
}: {
  score: number;
  severity: StabilitySeverity;
  isLoading: boolean;
}): React.ReactElement {
  if (isLoading) {
    return (
      <div
        className="animate-pulse rounded-xl border p-5"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label="Carregando score de estabilidade"
      >
        <div
          className="h-4 w-36 rounded mb-3"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="flex items-center gap-3">
          <div
            className="h-10 w-24 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-6 w-20 rounded-full"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      </div>
    );
  }

  const borderColor = getSeveritySignalToken(severity);
  const numericColor = getSeverityOnSurfaceToken(severity);

  return (
    <div
      className="rounded-xl border p-5"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      <p
        className="text-xs font-medium uppercase tracking-wider mb-2"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        Score de Estabilidade
      </p>
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-baseline gap-1">
          <span
            className="text-3xl font-bold tabular-nums"
            style={{ color: numericColor }}
          >
            {score}
          </span>
          <span
            className="text-sm"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            /27
          </span>
        </div>
        <span
          className="text-sm"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          critérios alterados
        </span>
        <StabilitySeverityBadge severity={severity} />
      </div>
    </div>
  );
}

// ─── 7-Day Trend Mini Chart ─────────────────────────────────────────────────

function TrendMiniChart({
  trend,
  isLoading,
}: {
  trend: StabilityTrend | null;
  isLoading: boolean;
}): React.ReactElement {
  if (isLoading) {
    return (
      <div
        className="animate-pulse rounded-xl border p-5"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label="Carregando tendência 7 dias"
      >
        <div
          className="h-4 w-32 rounded mb-4"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="flex items-end gap-2 h-24">
          {Array.from({ length: 7 }).map((_, i) => {
            const seed = i * 37 + 13;
            const pseudo = ((seed * 9301 + 49297) % 233280) / 233280;
            return (
              <div
                key={i}
                className="flex-1 rounded-t"
                style={{
                  height: `${30 + pseudo * 60}%`,
                  backgroundColor: 'var(--semantic-surface-overlay)',
                }}
              />
            );
          })}
        </div>
      </div>
    );
  }

  if (!trend || trend.trend.length === 0) {
    return (
      <div
        className="rounded-xl border p-5"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <p
          className="text-xs font-medium uppercase tracking-wider mb-4"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Tendência 7 Dias
        </p>
        <p
          className="text-sm text-center py-6"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Sem dados de tendência
        </p>
      </div>
    );
  }

  const points = trend.trend;
  const maxScore = Math.max(...points.map((p) => p.score), 1);
  const maxBarHeight = 80; // px

  return (
    <div
      className="rounded-xl border p-5"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <p
          className="text-xs font-medium uppercase tracking-wider"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Tendência 7 Dias
        </p>
        {/* Direction indicator */}
        <div
          className="flex items-center gap-1.5 text-xs font-semibold"
          style={{ color: getDirectionColor(trend.direction) }}
        >
          {getDirectionIcon(trend.direction)}
          <span>{getDirectionLabel(trend.direction)}</span>
          {trend.delta_7d !== 0 && (
            <span className="tabular-nums">
              ({trend.delta_7d > 0 ? '+' : ''}{trend.delta_7d})
            </span>
          )}
        </div>
      </div>

      {/* Bar chart */}
      <div className="flex items-end gap-1.5" style={{ height: `${maxBarHeight + 20}px` }}>
        {points.map((point, idx) => {
          const heightPercent = Math.max((point.score / maxScore) * 100, 4);
          const barColor =
            point.severity === 'critico'
              ? 'var(--clinical-stability-critico-fill)'
              : point.severity === 'atencao'
              ? 'var(--clinical-stability-atencao-fill)'
              : 'var(--clinical-stability-estavel-fill)';

          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-1 min-w-0">
              <span
                className="text-[10px] font-medium tabular-nums"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {point.score}
              </span>
              <div
                className="w-full rounded-t transition-all"
                style={{
                  height: `${(heightPercent / 100) * maxBarHeight}px`,
                  backgroundColor: barColor,
                  opacity: 0.85,
                  minWidth: '8px',
                }}
                title={`${formatDatePT(point.date)}: ${point.score} critérios (${getSeverityLabel(point.severity)})`}
              />
              <span
                className="text-[9px] mt-1"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {formatDatePT(point.date)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Recommendation Card ─────────────────────────────────────────────────────

function RecommendationCard({
  recommendation,
  severity,
  isLoading,
}: {
  recommendation: string;
  severity: StabilitySeverity;
  isLoading: boolean;
}): React.ReactElement {
  if (isLoading) {
    return (
      <div
        className="animate-pulse rounded-xl border p-4"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label="Carregando recomendação"
      >
        <div
          className="h-4 w-28 rounded mb-2"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="space-y-1.5">
          <div
            className="h-3 w-full rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-3 w-3/4 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      </div>
    );
  }

  const washColor = getSeverityWashToken(severity);
  const signalColor = getSeveritySignalToken(severity);
  const onSurfaceColor = getSeverityOnSurfaceToken(severity);

  const Icon =
    severity === 'critico'
      ? AlertTriangle
      : severity === 'atencao'
      ? AlertCircle
      : CheckCircle2;

  return (
    <div
      className="rounded-xl border p-4"
      style={{
        borderColor: signalColor,
        backgroundColor: washColor,
      }}
    >
      <div className="flex items-start gap-3">
        <Icon
          className="w-5 h-5 flex-shrink-0 mt-0.5"
          style={{ color: signalColor }}
          aria-hidden="true"
        />
        <div>
          <h3
            className="text-sm font-semibold mb-1"
            style={{ color: onSurfaceColor }}
          >
            Recomendação Clínica
          </h3>
          <p className="text-sm leading-relaxed" style={{ color: onSurfaceColor }}>
            {recommendation}
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Patient Selector ────────────────────────────────────────────────────────

function PatientSelector({
  patients,
  selectedMpiId,
  onSelect,
  isLoading,
}: {
  patients: PatientOption[];
  selectedMpiId: string;
  onSelect: (mpiId: string) => void;
  isLoading: boolean;
}): React.ReactElement {
  return (
    <div className="relative">
      <label
        className="block text-xs font-medium uppercase tracking-wider mb-1.5"
        style={{ color: 'var(--semantic-text-secondary)' }}
        htmlFor="stability-patient-select"
      >
        Paciente
      </label>
      <div className="relative">
        <select
          id="stability-patient-select"
          value={selectedMpiId}
          onChange={(e) => onSelect(e.target.value)}
          disabled={isLoading}
          className="appearance-none w-full pl-9 pr-8 py-2 rounded-lg text-sm font-medium
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          style={{
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
            borderColor: 'var(--semantic-border-default)',
            borderWidth: '1px',
          }}
          aria-label="Selecionar paciente"
        >
          {patients.map((p) => (
            <option key={p.mpiId} value={p.mpiId}>
              {p.displayName} — {p.bedId}
            </option>
          ))}
        </select>
        <Users
          className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
          style={{ color: 'var(--semantic-text-secondary)' }}
          aria-hidden="true"
        />
        <ChevronDown
          className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
          style={{ color: 'var(--semantic-text-secondary)' }}
          aria-hidden="true"
        />
      </div>
    </div>
  );
}

// ─── Full Loading Skeleton ───────────────────────────────────────────────────

function PageSkeleton(): React.ReactElement {
  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header skeleton */}
        <div className="animate-pulse space-y-2">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-lg"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div
              className="h-7 w-72 rounded"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
          </div>
          <div
            className="h-5 w-48 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>

        {/* Patient selector skeleton */}
        <div
          className="h-16 rounded-lg"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />

        {/* Score card skeleton */}
        <ScoreCard score={0} severity="estavel" isLoading />

        {/* Heatmap skeleton */}
        <StabilityHeatmap criteria={[]} isLoading />

        {/* Trend skeleton */}
        <TrendMiniChart trend={null} isLoading />

        {/* Recommendation skeleton */}
        <RecommendationCard recommendation="" severity="estavel" isLoading />
      </div>
    </Layout>
  );
}

// ─── Error Alert ─────────────────────────────────────────────────────────────

function ErrorAlert({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}): React.ReactElement {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border p-5"
      style={{
        borderColor: 'var(--clinical-severity-critical-signal)',
        backgroundColor: 'var(--clinical-severity-critical-wash)',
        color: 'var(--clinical-severity-critical-on-surface)',
      }}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
        <div>
          <h3 className="font-semibold text-sm mb-1">Erro ao carregar dados</h3>
          <p className="text-sm opacity-90">{message}</p>
          <button
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              color: 'var(--semantic-text-primary)',
              borderColor: 'var(--semantic-border-default)',
              borderWidth: '1px',
            }}
          >
            <Loader2 className="w-4 h-4" aria-hidden="true" />
            Tentar novamente
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Empty State ─────────────────────────────────────────────────────────────

function EmptyState(): React.ReactElement {
  return (
    <div
      className="flex flex-col items-center justify-center gap-3 py-16 text-center"
      role="status"
    >
      <Heart className="w-12 h-12 opacity-20" aria-hidden="true" />
      <p
        className="text-sm font-medium"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        Sem dados de estabilidade para este paciente
      </p>
    </div>
  );
}

// ─── Assement Timestamp ─────────────────────────────────────────────────────

function AssessedAt({
  iso,
  isLoading,
}: {
  iso: string;
  isLoading: boolean;
}): React.ReactElement | null {
  if (isLoading) {
    return (
      <div
        className="animate-pulse h-4 w-44 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    );
  }

  try {
    const d = new Date(iso);
    const formatted = d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
    return (
      <div className="flex items-center gap-1.5" style={{ color: 'var(--semantic-text-secondary)' }}>
        <Clock className="w-3.5 h-3.5" aria-hidden="true" />
        <span className="text-xs">Avaliado em {formatted}</span>
      </div>
    );
  } catch {
    return null;
  }
}

// ─── Page Component ─────────────────────────────────────────────────────────

export default function StabilityPage(): React.ReactElement {
  const [selectedMpiId, setSelectedMpiId] = useState<string>(MOCK_PATIENTS[0]!.mpiId);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  // ── Derived data ─────────────────────────────────────────────────────────
  const selectedPatient = useMemo(
    () => MOCK_PATIENTS.find((p) => p.mpiId === selectedMpiId) || MOCK_PATIENTS[0],
    [selectedMpiId],
  );

  const status = MOCK_STATUS;
  const trend = MOCK_TREND;

  const alteredCount = useMemo(
    () => countAlteredCriteria(status.criteria),
    [status.criteria],
  );

  const severity = useMemo(
    () => computeSeverity(alteredCount),
    [alteredCount],
  );

  // ── Filtered criteria ────────────────────────────────────────────────────
  const filteredCriteria = useMemo(() => {
    if (!categoryFilter) return status.criteria;
    return status.criteria.filter((c) => c.category === categoryFilter);
  }, [categoryFilter, status.criteria]);

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handlePatientChange = useCallback((mpiId: string) => {
    setSelectedMpiId(mpiId);
    setError(null);
    // Simula loading
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 600);
  }, []);

  const handleRetry = useCallback(() => {
    setError(null);
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 600);
  }, []);

  const handleFilterCategory = useCallback((cat: string) => {
    setCategoryFilter((prev) => (prev === cat ? '' : cat));
  }, []);

  // ── Loading state ────────────────────────────────────────────────────────
  if (isLoading && !status) {
    return <PageSkeleton />;
  }

  // ── Error state ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <Layout>
        <div className="max-w-5xl mx-auto">
          <ErrorAlert message={error} onRetry={handleRetry} />
        </div>
      </Layout>
    );
  }

  // ── Empty state ──────────────────────────────────────────────────────────
  if (!status || status.criteria.length === 0) {
    return (
      <Layout>
        <div className="max-w-5xl mx-auto">
          <EmptyState />
        </div>
      </Layout>
    );
  }

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-5xl mx-auto space-y-6">
          {/* ── Header ──────────────────────────────────────────────────── */}
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center"
                style={{
                  backgroundColor: 'var(--clinical-stability-atencao-fill)',
                  color: 'var(--clinical-stability-atencao-on-fill)',
                }}
              >
                <Heart className="w-5 h-5" aria-hidden="true" />
              </div>
              <h1
                className="text-xl font-bold"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                Estabilidade Hemodinâmica
              </h1>
            </div>
            <p
              className="text-sm"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Monitoramento contínuo de 27 critérios em 6 domínios fisiológicos
            </p>
          </div>

          {/* ── Patient Selector ────────────────────────────────────────── */}
          <PatientSelector
            patients={MOCK_PATIENTS}
            selectedMpiId={selectedMpiId}
            onSelect={handlePatientChange}
            isLoading={isLoading}
          />

          {/* ── Score Card ──────────────────────────────────────────────── */}
          <ScoreCard
            score={alteredCount}
            severity={severity}
            isLoading={isLoading}
          />

          <AssessedAt iso={status.assessed_at} isLoading={isLoading} />

          {/* ── Category Filter Tabs ────────────────────────────────────── */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Filter
                className="w-4 h-4"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <span
                className="text-xs font-medium uppercase tracking-wider"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Filtrar por categoria
              </span>
            </div>
            <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filtrar por categoria de estabilidade">
              <button
                role="tab"
                aria-selected={categoryFilter === ''}
                onClick={() => setCategoryFilter('')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                style={{
                  backgroundColor: categoryFilter === ''
                    ? 'var(--clinical-stability-atencao-fill)'
                    : 'var(--semantic-surface-overlay)',
                  color: categoryFilter === ''
                    ? 'var(--clinical-stability-atencao-on-fill)'
                    : 'var(--semantic-text-primary)',
                }}
              >
                Todos
              </button>
              {STABILITY_CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  role="tab"
                  aria-selected={categoryFilter === cat}
                  onClick={() => handleFilterCategory(cat)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  style={{
                    backgroundColor: categoryFilter === cat
                      ? 'var(--clinical-stability-atencao-fill)'
                      : 'var(--semantic-surface-overlay)',
                    color: categoryFilter === cat
                      ? 'var(--clinical-stability-atencao-on-fill)'
                      : 'var(--semantic-text-primary)',
                  }}
                >
                  {getCategoryLabel(cat)}
                </button>
              ))}
            </div>
          </div>

          {/* ── Stability Heatmap ──────────────────────────────────────── */}
          <StabilityHeatmap
            criteria={filteredCriteria}
            categoryFilter={categoryFilter}
            isLoading={isLoading}
            error={null}
          />

          {/* ── Trend 7 Days ───────────────────────────────────────────── */}
          <TrendMiniChart trend={trend} isLoading={isLoading} />

          {/* ── Recommendation ──────────────────────────────────────────── */}
          <RecommendationCard
            recommendation={status.recommendation}
            severity={severity}
            isLoading={isLoading}
          />
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
