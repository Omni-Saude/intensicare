'use client';

import React from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { AlertTriangle } from 'lucide-react';
import type { FluidBalanceTrend } from '@/lib/fluid-balance-types';

// ─── Props ──────────────────────────────────────────────────────────────────

interface FluidBalanceChartProps {
  /** Dados da série temporal (7 dias) */
  data: FluidBalanceTrend[];
  /** Exibe skeleton de carregamento */
  isLoading?: boolean;
  /** Mensagem de erro (exibe alerta no lugar do gráfico) */
  error?: string | null;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Formata valor ml no tooltip */
function formatTooltipValue(value: number): string {
  return `${value.toLocaleString('pt-BR')} ml`;
}

/** Formata data YYYY-MM-DD → DD/MM curto */
function formatShortDate(dateStr: string): string {
  const [y, m, d] = dateStr.split('-');
  if (!y || !m || !d) return dateStr;
  return `${d}/${m}`;
}

// ─── Tooltip customizado ────────────────────────────────────────────────────

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
    dataKey: string;
  }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps): React.ReactElement | null {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div
      className="rounded-lg border px-3 py-2 text-xs shadow-lg"
      style={{
        backgroundColor: 'var(--semantic-surface-raised)',
        borderColor: 'var(--semantic-border-default)',
        color: 'var(--semantic-text-primary)',
      }}
      role="tooltip"
    >
      <p
        className="font-semibold mb-1"
        style={{ color: 'var(--semantic-text-primary)' }}
      >
        {label ? formatShortDate(label) : ''}
      </p>
      {payload.map((entry) => (
        <p
          key={entry.dataKey}
          className="flex items-center gap-1.5"
          style={{ color: entry.color }}
        >
          <span
            className="inline-block w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: entry.color }}
          />
          {entry.name}: {formatTooltipValue(entry.value)}
        </p>
      ))}
    </div>
  );
}

// ─── Loading Skeleton ───────────────────────────────────────────────────────

function ChartSkeleton(): React.ReactElement {
  return (
    <div
      className="animate-pulse rounded-xl"
      style={{
        height: '300px',
        backgroundColor: 'var(--semantic-surface-overlay)',
      }}
      role="status"
      aria-label="Carregando gráfico de balanço hídrico"
    />
  );
}

// ─── Error State ────────────────────────────────────────────────────────────

function ChartError({ message }: { message: string }): React.ReactElement {
  return (
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
      <span>{message}</span>
    </div>
  );
}

// ─── Empty State ────────────────────────────────────────────────────────────

function ChartEmpty(): React.ReactElement {
  return (
    <div
      className="flex items-center justify-center rounded-xl border"
      style={{
        height: '300px',
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
        color: 'var(--semantic-text-secondary)',
      }}
    >
      <p className="text-sm">Sem dados de balanço hídrico</p>
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function FluidBalanceChart({
  data,
  isLoading = false,
  error = null,
}: FluidBalanceChartProps): React.ReactElement {
  // ── Loading ───────────────────────────────────────────────────────────
  if (isLoading) {
    return <ChartSkeleton />;
  }

  // ── Error ─────────────────────────────────────────────────────────────
  if (error) {
    return <ChartError message={error} />;
  }

  // ── Empty ─────────────────────────────────────────────────────────────
  if (!data || data.length === 0) {
    return <ChartEmpty />;
  }

  // ── Chart ─────────────────────────────────────────────────────────────
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart
        data={data}
        margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="var(--semantic-border-default)"
        />

        <XAxis
          dataKey="date"
          tickFormatter={formatShortDate}
          tick={{
            fontSize: 11,
            fill: 'var(--semantic-text-secondary)',
          }}
          axisLine={{ stroke: 'var(--semantic-border-default)' }}
          tickLine={false}
        />

        <YAxis
          yAxisId="volume"
          orientation="left"
          tick={{
            fontSize: 11,
            fill: 'var(--semantic-text-secondary)',
          }}
          axisLine={false}
          tickLine={false}
          label={{
            value: 'Volume (ml)',
            angle: -90,
            position: 'insideLeft',
            style: {
              fontSize: 11,
              fill: 'var(--semantic-text-secondary)',
            },
          }}
        />

        <YAxis
          yAxisId="balance"
          orientation="right"
          tick={{
            fontSize: 11,
            fill: 'var(--semantic-text-secondary)',
          }}
          axisLine={false}
          tickLine={false}
          label={{
            value: 'Balanço (ml)',
            angle: 90,
            position: 'insideRight',
            style: {
              fontSize: 11,
              fill: 'var(--semantic-text-secondary)',
            },
          }}
        />

        <Tooltip content={<CustomTooltip />} />

        <Legend
          wrapperStyle={{
            fontSize: '12px',
            color: 'var(--semantic-text-secondary)',
          }}
        />

        {/* Bar: Entradas (intake) — verde */}
        <Bar
          yAxisId="volume"
          dataKey="intake_ml"
          name="Entradas"
          fill="var(--clinical-fluid-balance-positive-signal-dark)"
          radius={[4, 4, 0, 0]}
          barSize={24}
        />

        {/* Bar: Saídas (output) — laranja/âmbar */}
        <Bar
          yAxisId="volume"
          dataKey="output_ml"
          name="Saídas"
          fill="var(--clinical-fluid-balance-negative-signal-dark)"
          radius={[4, 4, 0, 0]}
          barSize={24}
        />

        {/* Line: Balanço líquido — azul */}
        <Line
          yAxisId="balance"
          type="monotone"
          dataKey="balance_ml"
          name="Balanço"
          stroke="var(--action-primary-bg-dark)"
          strokeWidth={2}
          dot={{
            r: 4,
            fill: 'var(--action-primary-bg-dark)',
            strokeWidth: 0,
          }}
          activeDot={{
            r: 6,
            fill: 'var(--action-primary-bg-dark)',
            strokeWidth: 2,
            stroke: 'var(--semantic-surface-raised)',
          }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
