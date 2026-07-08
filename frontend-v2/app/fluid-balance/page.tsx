'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Droplets,
  TrendingUp,
  TrendingDown,
  Minus,
  Activity,
  AlertTriangle,
  Loader2,
  Clock,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import FluidBalanceChart from '@/components/FluidBalanceChart';
import {
  type FluidBalanceTrend,
  type FluidBalanceSummary,
  type FluidBalanceRecord,
  type BalanceStatus,
  MOCK_SUMMARY,
  MOCK_TREND,
  MOCK_RECORDS,
  classifyBalance,
  formatVolume,
  BALANCE_STATUS_LABELS,
  CATEGORY_LABELS_FLUID,
} from '@/lib/fluid-balance-types';

// ─── View mode ──────────────────────────────────────────────────────────────

type ViewMode = '24h' | '7d';

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Formata timestamp ISO → HH:mm (PT-BR) */
function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '--:--';
  }
}

/** Status → tokens para estilização dinâmica */
function getBalanceTokens(status: BalanceStatus) {
  switch (status) {
    case 'positive':
      return {
        signal: 'var(--clinical-fluid-balance-positive-signal-dark)',
        onSurface: 'var(--clinical-fluid-balance-positive-on-surface-dark)',
        was: 'var(--clinical-fluid-balance-positive-wash)',
        fill: 'var(--clinical-fluid-balance-positive-fill)',
        onFill: 'var(--clinical-fluid-balance-positive-on-fill)',
      };
    case 'negative':
      return {
        signal: 'var(--clinical-fluid-balance-negative-signal-dark)',
        onSurface: 'var(--clinical-fluid-balance-negative-on-surface-dark)',
        was: 'var(--clinical-fluid-balance-negative-wash)',
        fill: 'var(--clinical-fluid-balance-negative-fill)',
        onFill: 'var(--clinical-fluid-balance-negative-on-fill)',
      };
    case 'neutral':
      return {
        signal: 'var(--clinical-fluid-balance-neutral-signal-dark)',
        onSurface: 'var(--clinical-fluid-balance-neutral-on-surface-dark)',
        was: 'var(--clinical-fluid-balance-neutral-wash)',
        fill: 'var(--clinical-fluid-balance-neutral-fill)',
        onFill: 'var(--clinical-fluid-balance-neutral-on-fill)',
      };
  }
}

// ─── Summary Card ───────────────────────────────────────────────────────────

interface SummaryCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  /** Cor de fundo/accento */
  accentColor: string;
  accentBg: string;
  isLoading?: boolean;
}

function SummaryCard({
  title,
  value,
  subtitle,
  icon,
  accentColor,
  accentBg,
  isLoading = false,
}: SummaryCardProps): React.ReactElement {
  if (isLoading) {
    return (
      <div
        className="animate-pulse rounded-xl border p-4 flex items-start gap-3"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label={`Carregando ${title}`}
      >
        <div
          className="w-10 h-10 rounded-lg flex-shrink-0"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="flex-1 space-y-2">
          <div
            className="h-4 w-20 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-6 w-28 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      </div>
    );
  }

  return (
    <div
      className="rounded-xl border p-4 flex items-start gap-3"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: accentBg, color: accentColor }}
      >
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <p
          className="text-xs font-medium uppercase tracking-wider"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {title}
        </p>
        <p
          className="text-xl font-bold tabular-nums mt-0.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {value}
        </p>
        {subtitle && (
          <p
            className="text-xs mt-0.5"
            style={{ color: accentColor }}
          >
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

// ─── Toggle Button Group ────────────────────────────────────────────────────

interface ToggleGroupProps {
  options: Array<{ value: ViewMode; label: string }>;
  active: ViewMode;
  onChange: (value: ViewMode) => void;
  disabled?: boolean;
}

function ToggleGroup({
  options,
  active,
  onChange,
  disabled = false,
}: ToggleGroupProps): React.ReactElement {
  return (
    <div
      className="inline-flex rounded-lg border overflow-hidden"
      style={{ borderColor: 'var(--semantic-border-default)' }}
      role="radiogroup"
      aria-label="Período de visualização"
    >
      {options.map((opt) => {
        const isActive = opt.value === active;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={isActive}
            disabled={disabled}
            onClick={() => onChange(opt.value)}
            className="px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: isActive
                ? 'var(--action-primary-bg-dark)'
                : 'transparent',
              color: isActive
                ? 'var(--action-primary-text-dark)'
                : 'var(--semantic-text-secondary)',
            }}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

// ─── Skeleton de tabela ─────────────────────────────────────────────────────

function TableSkeleton(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-2" role="status" aria-label="Carregando registros">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="h-10 rounded-lg"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      ))}
    </div>
  );
}

// ─── Full loading skeleton ──────────────────────────────────────────────────

function PageSkeleton(): React.ReactElement {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header skeleton */}
        <div className="animate-pulse space-y-3">
          <div
            className="h-8 w-64 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-5 w-48 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>

        {/* Summary cards skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <SummaryCard
            title="Entradas"
            value=""
            icon={null}
            accentColor=""
            accentBg=""
            isLoading
          />
          <SummaryCard
            title="Saídas"
            value=""
            icon={null}
            accentColor=""
            accentBg=""
            isLoading
          />
          <SummaryCard
            title="Balanço Líquido"
            value=""
            icon={null}
            accentColor=""
            accentBg=""
            isLoading
          />
        </div>

        {/* Chart skeleton */}
        <div
          className="animate-pulse rounded-xl"
          style={{
            height: '300px',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
          role="status"
          aria-label="Carregando gráfico"
        />

        {/* Table skeleton */}
        <TableSkeleton />
      </div>
    </Layout>
  );
}

// ─── Empty State ────────────────────────────────────────────────────────────

function EmptyState(): React.ReactElement {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-xl border py-12 px-6 text-center"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      <Droplets
        className="w-12 h-12 mb-4 opacity-30"
        style={{ color: 'var(--semantic-text-secondary)' }}
        aria-hidden="true"
      />
      <p
        className="text-lg font-semibold mb-1"
        style={{ color: 'var(--semantic-text-primary)' }}
      >
        Nenhum registro de balanço hídrico
      </p>
      <p className="text-sm" style={{ color: 'var(--semantic-text-secondary)' }}>
        Nenhum registro de balanço hídrico no período selecionado.
      </p>
    </div>
  );
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function FluidBalancePage(): React.ReactElement {
  const [viewMode, setViewMode] = useState<ViewMode>('24h');
  const [isLoading, setIsLoading] = useState(false);
  const [simulatedError, setSimulatedError] = useState<string | null>(null);
  const [isEmpty, setIsEmpty] = useState(false);

  // ── Derived state ─────────────────────────────────────────────────────
  const summary: FluidBalanceSummary = useMemo(() => MOCK_SUMMARY, []);
  const trendData: FluidBalanceTrend[] = useMemo(() => MOCK_TREND, []);
  const records: FluidBalanceRecord[] = useMemo(() => MOCK_RECORDS, []);

  const balanceStatus: BalanceStatus = useMemo(
    () => classifyBalance(summary.net_balance_ml),
    [summary.net_balance_ml],
  );

  const balanceTokens = useMemo(
    () => getBalanceTokens(balanceStatus),
    [balanceStatus],
  );

  // ── Simulators ────────────────────────────────────────────────────────
  const simulateLoading = useCallback(() => {
    setIsLoading(true);
    setSimulatedError(null);
    setIsEmpty(false);
    setTimeout(() => setIsLoading(false), 1500);
  }, []);

  const simulateError = useCallback(() => {
    setIsLoading(false);
    setIsEmpty(false);
    setSimulatedError(
      'Erro ao carregar dados de balanço hídrico. Verifique a conexão com o servidor e tente novamente.',
    );
  }, []);

  const simulateEmpty = useCallback(() => {
    setIsLoading(false);
    setSimulatedError(null);
    setIsEmpty(true);
  }, []);

  const restoreData = useCallback(() => {
    setIsLoading(false);
    setSimulatedError(null);
    setIsEmpty(false);
  }, []);

  // ── Loading state ─────────────────────────────────────────────────────
  if (isLoading) {
    return <PageSkeleton />;
  }

  // ── Main render ───────────────────────────────────────────────────────
  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-4xl mx-auto space-y-6 pb-12">
          {/* ── Header ─────────────────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor:
                      'var(--clinical-fluid-balance-positive-fill)',
                    color:
                      'var(--clinical-fluid-balance-positive-on-fill)',
                  }}
                >
                  <Droplets className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Balanço Hídrico
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Monitoramento de entradas, saídas e balanço líquido
              </p>
            </div>

            {/* Demo state toggles */}
            <div className="flex gap-2">
              <button
                onClick={simulateLoading}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50"
                style={{
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-secondary)',
                  borderColor: 'var(--semantic-border-default)',
                }}
                aria-label="Simular carregamento"
              >
                <Loader2
                  className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`}
                  aria-hidden="true"
                />
                Loading
              </button>
              <button
                onClick={simulateError}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
                style={{
                  backgroundColor: 'var(--feedback-error-bg-dark)',
                  color: 'var(--feedback-error-text-dark)',
                  borderColor: 'var(--feedback-error-border-dark)',
                }}
                aria-label="Simular erro"
              >
                <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
                Error
              </button>
              <button
                onClick={simulateEmpty}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
                style={{
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-secondary)',
                  borderColor: 'var(--semantic-border-default)',
                }}
                aria-label="Simular vazio"
              >
                <Droplets className="w-3.5 h-3.5" aria-hidden="true" />
                Empty
              </button>
              {(simulatedError || isEmpty) && (
                <button
                  onClick={restoreData}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
                  style={{
                    backgroundColor: 'var(--feedback-success-bg-dark)',
                    color: 'var(--feedback-success-text-dark)',
                    borderColor: 'var(--feedback-success-border-dark)',
                  }}
                  aria-label="Restaurar dados"
                >
                  Restaurar
                </button>
              )}
            </div>
          </div>

          {/* ── Error state (simulated) ─────────────────────────────────── */}
          {simulatedError && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex items-start gap-3 px-4 py-3 rounded-xl border text-sm"
              style={{
                backgroundColor: 'var(--feedback-error-bg-dark)',
                color: 'var(--feedback-error-text-dark)',
                borderColor: 'var(--feedback-error-border-dark)',
              }}
            >
              <AlertTriangle
                className="w-5 h-5 flex-shrink-0 mt-0.5"
                aria-hidden="true"
              />
              <span className="flex-1">{simulatedError}</span>
              <button
                onClick={() => setSimulatedError(null)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-opacity hover:opacity-80"
                style={{
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
              >
                Fechar
              </button>
            </div>
          )}

          {/* ── Empty state ────────────────────────────────────────────── */}
          {isEmpty && !simulatedError && <EmptyState />}

          {/* ── Main content ───────────────────────────────────────────── */}
          {!isEmpty && !simulatedError && (
            <>
              {/* ── Summary Cards ─────────────────────────────────────── */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Entradas */}
                <SummaryCard
                  title="Entradas"
                  value={`${summary.total_intake_ml.toLocaleString('pt-BR')} ml`}
                  subtitle="Total nas últimas 24h"
                  icon={
                    <TrendingUp
                      className="w-5 h-5"
                      aria-hidden="true"
                    />
                  }
                  accentColor="var(--clinical-fluid-balance-positive-signal-dark)"
                  accentBg="var(--clinical-fluid-balance-positive-wash)"
                />

                {/* Saídas */}
                <SummaryCard
                  title="Saídas"
                  value={`${summary.total_output_ml.toLocaleString('pt-BR')} ml`}
                  subtitle="Total nas últimas 24h"
                  icon={
                    <TrendingDown
                      className="w-5 h-5"
                      aria-hidden="true"
                    />
                  }
                  accentColor="var(--clinical-fluid-balance-negative-signal-dark)"
                  accentBg="var(--clinical-fluid-balance-negative-wash)"
                />

                {/* Balanço Líquido */}
                <SummaryCard
                  title="Balanço Líquido"
                  value={formatVolume(summary.net_balance_ml)}
                  subtitle={BALANCE_STATUS_LABELS[balanceStatus]}
                  icon={
                    balanceStatus === 'positive' ? (
                      <TrendingUp className="w-5 h-5" aria-hidden="true" />
                    ) : balanceStatus === 'negative' ? (
                      <TrendingDown className="w-5 h-5" aria-hidden="true" />
                    ) : (
                      <Minus className="w-5 h-5" aria-hidden="true" />
                    )
                  }
                  accentColor={balanceTokens.signal}
                  accentBg={balanceTokens.was}
                />
              </div>

              {/* ── Chart Section ──────────────────────────────────────── */}
              <div
                className="rounded-xl border p-4"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2
                    className="text-sm font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    Tendência de Balanço Hídrico
                  </h2>
                  <ToggleGroup
                    options={[
                      { value: '24h', label: '24 horas' },
                      { value: '7d', label: '7 dias' },
                    ]}
                    active={viewMode}
                    onChange={setViewMode}
                  />
                </div>

                {viewMode === '7d' ? (
                  <FluidBalanceChart
                    data={trendData}
                    isLoading={false}
                    error={null}
                  />
                ) : (
                  /* 24h: mostra gráfico com dados mock truncados (ex: últimos 2 dias para visualização) */
                  <FluidBalanceChart
                    data={trendData.slice(-2)}
                    isLoading={false}
                    error={null}
                  />
                )}
              </div>

              {/* ── Recent Records Table ────────────────────────────────── */}
              <div
                className="rounded-xl border overflow-hidden"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
              >
                <div
                  className="flex items-center gap-2 px-4 py-3 border-b"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-overlay)',
                  }}
                >
                  <Clock
                    className="w-4 h-4"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                    aria-hidden="true"
                  />
                  <h2
                    className="text-sm font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    Registros Recentes
                  </h2>
                  <span
                    className="text-xs ml-auto tabular-nums"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {records.length} registros
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr
                        className="border-b"
                        style={{
                          borderColor: 'var(--semantic-border-default)',
                        }}
                      >
                        <th
                          className="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          Horário
                        </th>
                        <th
                          className="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          Tipo
                        </th>
                        <th
                          className="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          Categoria
                        </th>
                        <th
                          className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          Volume
                        </th>
                        <th
                          className="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {records.map((record, idx) => {
                        const isIntake = record.intake_ml > 0;
                        const recStatus = classifyBalance(record.balance_ml);
                        const recTokens = getBalanceTokens(recStatus);

                        return (
                          <tr
                            key={idx}
                            className="border-b transition-colors hover:opacity-80"
                            style={{
                              borderColor: 'var(--semantic-border-default)',
                            }}
                          >
                            <td
                              className="px-4 py-2.5 tabular-nums"
                              style={{
                                color: 'var(--semantic-text-secondary)',
                              }}
                            >
                              {formatTime(record.timestamp)}
                            </td>
                            <td
                              className="px-4 py-2.5 font-medium"
                              style={{ color: 'var(--semantic-text-primary)' }}
                            >
                              {isIntake ? 'Entrada' : 'Saída'}
                            </td>
                            <td
                              className="px-4 py-2.5"
                              style={{ color: 'var(--semantic-text-secondary)' }}
                            >
                              {CATEGORY_LABELS_FLUID[record.category]}
                            </td>
                            <td
                              className="px-4 py-2.5 text-right tabular-nums font-medium"
                              style={{
                                color: isIntake
                                  ? 'var(--clinical-fluid-balance-positive-signal-dark)'
                                  : 'var(--clinical-fluid-balance-negative-signal-dark)',
                              }}
                            >
                              {isIntake
                                ? `+${record.intake_ml.toLocaleString('pt-BR')} ml`
                                : `-${record.output_ml.toLocaleString('pt-BR')} ml`}
                            </td>
                            <td className="px-4 py-2.5">
                              <span
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                                style={{
                                  backgroundColor: recTokens.was,
                                  color: recTokens.onSurface,
                                }}
                              >
                                {BALANCE_STATUS_LABELS[recStatus]}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
