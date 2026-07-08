'use client';

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { VentilationTrend, TrendDirection } from '@/lib/ventilation-types';
import { PARAM_LABELS, PARAM_UNITS } from '@/lib/ventilation-types';

// ─── Parâmetros disponíveis para o gráfico ──────────────────────────────────

const CHART_PARAMS = [
  { key: 'FiO2', color: 'var(--clinical-ventilation-fio2)' },
  { key: 'PEEP', color: 'var(--clinical-ventilation-peep)' },
  { key: 'VC', color: 'var(--clinical-ventilation-vc)' },
  { key: 'FR', color: 'var(--clinical-ventilation-fr)' },
  { key: 'Pplat', color: 'var(--clinical-ventilation-pplat)' },
  { key: 'driving_pressure', color: 'var(--clinical-ventilation-dp)' },
  { key: 'PaO2_FiO2_ratio', color: 'var(--clinical-ventilation-pf)' },
] as const;

type ParamKey = (typeof CHART_PARAMS)[number]['key'];

// ─── Props ──────────────────────────────────────────────────────────────────

interface VentilationTrendChartProps {
  /** Dados da tendência ventilatória (série temporal horária) */
  trend: VentilationTrend | null;
  /** Chave do parâmetro selecionado para visualização */
  selectedParam: string;
  /** Callback para mudança de parâmetro */
  onParamChange?: (param: string) => void;
  /** Exibe skeleton de carregamento */
  isLoading?: boolean;
  /** Mensagem de erro (exibe alerta no lugar do gráfico) */
  error?: string | null;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Formata valor + unidade no tooltip */
function formatChartValue(value: number, param: string): string {
  const unit = PARAM_UNITS[param] ?? '';
  if (param === 'FiO2') {
    return `${Math.round(value * 100)}${unit}`;
  }
  return `${value}${unit ? ` ${unit}` : ''}`;
}

/** Formata timestamp ISO → HH:mm (PT-BR) */
function formatHour(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '--:--';
  }
}

/** Ícone de direção da tendência */
function TrendIcon({ direction }: { direction: TrendDirection }): React.ReactElement {
  if (direction === 'rising') {
    return <TrendingUp className="w-3.5 h-3.5" aria-hidden="true" />;
  }
  if (direction === 'falling') {
    return <TrendingDown className="w-3.5 h-3.5" aria-hidden="true" />;
  }
  return <Minus className="w-3.5 h-3.5" aria-hidden="true" />;
}

// ─── Tooltip customizado ────────────────────────────────────────────────────

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
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
        {label ? formatHour(label) : ''}
      </p>
      {payload.map((entry) => (
        <p
          key={entry.name}
          className="flex items-center gap-1.5"
          style={{ color: entry.color }}
        >
          <span
            className="inline-block w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: entry.color }}
          />
          {entry.name}: {formatChartValue(entry.value, entry.name)}
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
      aria-label="Carregando gráfico de tendência ventilatória"
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
      <p className="text-sm">Sem dados de tendência</p>
    </div>
  );
}

// ─── Transforma dados para Recharts ─────────────────────────────────────────

interface ChartDataPoint {
  time: string;
  value: number;
}

function buildChartData(
  trend: VentilationTrend,
  param: string,
): ChartDataPoint[] {
  const paramKey = param as keyof typeof trend.parameters;
  const paramTrend = trend.parameters[paramKey];
  if (!paramTrend || !paramTrend.series) return [];

  return paramTrend.series.map((point) => ({
    time: point.collected_at,
    value: param === 'FiO2' ? Math.round(point.value * 100) : point.value,
  }));
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function VentilationTrendChart({
  trend,
  selectedParam,
  onParamChange,
  isLoading = false,
  error = null,
}: VentilationTrendChartProps): React.ReactElement {
  // ── Transform data ─────────────────────────────────────────────────────
  const chartData = useMemo(
    () => (trend ? buildChartData(trend, selectedParam) : []),
    [trend, selectedParam],
  );

  // ── Info do parâmetro selecionado ───────────────────────────────────────
  const paramInfo = useMemo(
    () => (trend?.parameters as Record<string, { direction: TrendDirection; change_pct: number; avg: number; min: number; max: number }> | undefined)?.[selectedParam],
    [trend, selectedParam],
  );

  const paramColor = useMemo(
    () => CHART_PARAMS.find((p) => p.key === selectedParam)?.color ?? 'var(--action-primary-bg-dark)',
    [selectedParam],
  );

  // ── Loading ───────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="space-y-3">
        {/* Param selector skeleton */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-8 w-28 rounded-lg animate-pulse flex-shrink-0"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
          ))}
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  // ── Error ─────────────────────────────────────────────────────────────
  if (error) {
    return <ChartError message={error} />;
  }

  // ── Empty ─────────────────────────────────────────────────────────────
  if (!trend || chartData.length === 0) {
    return <ChartEmpty />;
  }

  // ── Chart ─────────────────────────────────────────────────────────────
  return (
    <div className="space-y-3">
      {/* ── Parameter Selector Tabs ─────────────────────────────────── */}
      <div
        className="flex gap-1.5 overflow-x-auto pb-1"
        role="tablist"
        aria-label="Selecionar parâmetro do gráfico"
      >
        {CHART_PARAMS.map((param) => {
          const isActive = param.key === selectedParam;
          return (
            <button
              key={param.key}
              role="tab"
              aria-selected={isActive}
              onClick={() => onParamChange?.(param.key)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset"
              style={{
                backgroundColor: isActive ? param.color : 'var(--semantic-surface-overlay)',
                color: isActive ? '#ffffff' : 'var(--semantic-text-secondary)',
              }}
            >
              {PARAM_LABELS[param.key] ?? param.key}
            </button>
          );
        })}
      </div>

      {/* ── Trend Summary ───────────────────────────────────────────── */}
      {paramInfo && (
        <div
          className="flex items-center gap-4 text-xs px-1"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          <span className="flex items-center gap-1">
            <TrendIcon direction={paramInfo.direction} />
            {paramInfo.change_pct > 0 ? '+' : ''}{paramInfo.change_pct}%
          </span>
          <span>
            Média: {formatChartValue(paramInfo.avg, selectedParam)}
          </span>
          <span>
            Mín: {formatChartValue(paramInfo.min, selectedParam)}
          </span>
          <span>
            Máx: {formatChartValue(paramInfo.max, selectedParam)}
          </span>
        </div>
      )}

      {/* ── Chart ───────────────────────────────────────────────────── */}
      <div
        role="img"
        aria-label={`Tendência de ${PARAM_LABELS[selectedParam] ?? selectedParam}: média ${paramInfo ? formatChartValue(paramInfo.avg, selectedParam) : '--'}, mín ${paramInfo ? formatChartValue(paramInfo.min, selectedParam) : '--'}, máx ${paramInfo ? formatChartValue(paramInfo.max, selectedParam) : '--'} no período`}
      >
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--semantic-border-default)"
            />

            <XAxis
              dataKey="time"
              tickFormatter={formatHour}
              tick={{
                fontSize: 11,
                fill: 'var(--semantic-text-secondary)',
              }}
              axisLine={{ stroke: 'var(--semantic-border-default)' }}
              tickLine={false}
              interval="preserveStartEnd"
            />

            <YAxis
              tick={{
                fontSize: 11,
                fill: 'var(--semantic-text-secondary)',
              }}
              axisLine={false}
              tickLine={false}
              width={50}
            />

            <Tooltip content={<CustomTooltip />} />

            <Legend
              wrapperStyle={{
                fontSize: '12px',
                color: 'var(--semantic-text-secondary)',
              }}
              formatter={(value: string) => PARAM_LABELS[value] ?? value}
            />

            <Line
              type="monotone"
              dataKey="value"
              name={selectedParam}
              stroke={paramColor}
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 5,
                fill: paramColor,
                strokeWidth: 2,
                stroke: 'var(--semantic-surface-raised)',
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
