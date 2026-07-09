'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  BarChart3,
  Target,
  TrendingDown,
  TrendingUp,
  Minus,
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  XCircle,
  X,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import DrawerBuilder from '@/components/DrawerBuilder';
import IndicatorCard from '@/components/IndicatorCard';
import type { Indicator, IndicatorDetail, IndicatorCategory, Trend } from '@/lib/indicators-types';
import {
  MOCK_INDICATORS,
  MOCK_DETAILS,
  CATEGORY_LABELS,
  TREND_LABELS,
  TREND_ICONS,
  CATEGORY_COLORS,
  CATEGORY_BG_COLORS,
  formatValue,
  getTrendColor,
  isWithinRange,
  getRangePercentage,
} from '@/lib/indicators-types';

// ─── Constantes ───────────────────────────────────────────────────────────────

const ALL_CATEGORIES: Array<'Todos' | IndicatorCategory> = [
  'Todos',
  'TLP',
  'occupancy',
  'sedation',
  'ventilation',
  'stewardship',
  'safety',
  'efficiency',
];

// ─── Sub-componentes ─────────────────────────────────────────────────────────

/** Mini gráfico de barras com divs (sem Recharts) */
function MiniBarChart({
  history,
  referenceRange,
  unit,
}: {
  history: IndicatorDetail['history'];
  referenceRange: { low: number; high: number };
  unit: string;
}) {
  if (history.length === 0) {
    return (
      <div
        className="text-center py-8 text-sm"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        Sem dados históricos disponíveis.
      </div>
    );
  }

  const values = history.map((p) => p.value);
  const minVal = Math.min(referenceRange.low, ...values);
  const maxVal = Math.max(referenceRange.high, ...values);
  const span = maxVal - minVal || 1;

  return (
    <div className="space-y-2">
      {/* Chart area */}
      <div className="flex items-end gap-1 h-32" role="img" aria-label="Gráfico de tendência do indicador">
        {history.map((point, i) => {
          const heightPct = ((point.value - minVal) / span) * 100;
          const inRange = isWithinRange(point.value, referenceRange);
          return (
            <div
              key={i}
              className="flex-1 flex flex-col items-center justify-end h-full"
              title={`${new Date(point.timestamp).toLocaleDateString('pt-BR')}: ${point.value}${unit}`}
            >
              <div
                className="w-full rounded-t-sm transition-all duration-300 min-h-[2px]"
                style={{
                  height: `${Math.max(2, heightPct)}%`,
                  backgroundColor: inRange
                    ? 'var(--clinical-severity-normal-signal)'
                    : 'var(--clinical-severity-critical-signal)',
                }}
              />
            </div>
          );
        })}
      </div>

      {/* Range reference line */}
      <div className="relative h-0.5 w-full rounded" style={{ backgroundColor: 'var(--semantic-border-default)' }}>
        {/* Low marker */}
        <div
          className="absolute top-1/2 -translate-y-1/2"
          style={{
            left: `${((referenceRange.low - minVal) / span) * 100}%`,
          }}
        >
          <div className="w-0.5 h-3 -translate-y-full" style={{ backgroundColor: 'var(--semantic-text-secondary)' }} />
        </div>
        {/* High marker */}
        <div
          className="absolute top-1/2 -translate-y-1/2"
          style={{
            left: `${((referenceRange.high - minVal) / span) * 100}%`,
          }}
        >
          <div className="w-0.5 h-3 -translate-y-full" style={{ backgroundColor: 'var(--semantic-text-secondary)' }} />
        </div>
      </div>

      {/* Labels */}
      <div className="flex justify-between text-[10px]" style={{ color: 'var(--semantic-text-secondary)' }}>
        <span>{history.length} dias</span>
        <span>
          Ref: {referenceRange.low}–{referenceRange.high}{unit}
        </span>
      </div>
    </div>
  );
}

/** Tabela de últimos valores */
function HistoryTable({
  history,
  referenceRange,
  unit,
}: {
  history: IndicatorDetail['history'];
  referenceRange: { low: number; high: number };
  unit: string;
}) {
  const recent = history.slice(-10).reverse(); // últimos 10, mais recente primeiro

  return (
    <div className="space-y-1">
      <h4
        className="text-xs font-semibold uppercase tracking-wider mb-2"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        Últimos Valores
      </h4>
      <div className="max-h-48 overflow-y-auto">
        <table className="w-full text-xs">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--semantic-border-default)' }}>
              <th
                className="text-left py-1.5 font-medium"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Data
              </th>
              <th
                className="text-right py-1.5 font-medium"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Valor
              </th>
              <th
                className="text-right py-1.5 font-medium"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {recent.map((point, i) => {
              const inRange = isWithinRange(point.value, referenceRange);
              return (
                <tr
                  key={i}
                  style={{ borderBottom: '1px solid var(--semantic-border-default)' }}
                >
                  <td
                    className="py-1.5"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {new Date(point.timestamp).toLocaleDateString('pt-BR')}
                  </td>
                  <td
                    className="py-1.5 text-right font-medium"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {formatValue(point.value, unit)}
                  </td>
                  <td className="py-1.5 text-right">
                    {inRange ? (
                      <CheckCircle2
                        className="w-3.5 h-3.5 inline"
                        style={{ color: 'var(--clinical-severity-normal-signal)' }}
                        aria-label="Dentro da faixa"
                      />
                    ) : (
                      <XCircle
                        className="w-3.5 h-3.5 inline"
                        style={{ color: 'var(--clinical-severity-critical-signal)' }}
                        aria-label="Fora da faixa"
                      />
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** Painel de detalhes exibido no Drawer */
function IndicatorDetailPanel({
  indicatorId,
  onClose,
}: {
  indicatorId: string;
  onClose: () => void;
}) {
  const [detail, setDetail] = useState<IndicatorDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simula fetch — usa mock com delay
    const timer = setTimeout(() => {
      const found =
        MOCK_DETAILS[indicatorId] ??
        ({
          ...MOCK_INDICATORS.find((i) => i.id === indicatorId),
          history: [],
        } as IndicatorDetail);

      // Se não tem history mockado, gera um
      if (!found.history || found.history.length === 0) {
        const base = MOCK_INDICATORS.find((i) => i.id === indicatorId);
        if (base) {
          found.history = generateFallbackHistory(base.current_value, 30, indicatorId);
        }
      }

      setDetail(found);
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [indicatorId]);

  if (loading || !detail) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-6 rounded w-48" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
        <div className="h-32 rounded" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
        <div className="h-20 rounded" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
      </div>
    );
  }

  const { name, category, current_value, target, trend, unit, reference_range, history } =
    detail;

  const TrendIcon = TREND_ICONS[trend];
  const trendColor = getTrendColor(trend);
  const categoryColor = CATEGORY_COLORS[category];
  const categoryBg = CATEGORY_BG_COLORS[category];

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
            style={{ backgroundColor: categoryBg, color: categoryColor }}
          >
            {CATEGORY_LABELS[category]}
          </span>
        </div>
        <h2 className="text-xl font-bold" style={{ color: 'var(--semantic-text-primary)' }}>
          {name}
        </h2>
      </div>

      {/* Métricas principais */}
      <div className="grid grid-cols-3 gap-4">
        {/* Valor atual */}
        <div
          className="rounded-xl border p-4 text-center"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
        >
          <div
            className="text-xs font-semibold uppercase mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Valor Atual
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            {formatValue(current_value, unit)}
          </div>
        </div>

        {/* Meta */}
        <div
          className="rounded-xl border p-4 text-center"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
        >
          <div
            className="text-xs font-semibold uppercase mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Meta
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            {target !== undefined && target !== null
              ? formatValue(target, unit)
              : '—'}
          </div>
        </div>

        {/* Tendência */}
        <div
          className="rounded-xl border p-4 text-center"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
        >
          <div
            className="text-xs font-semibold uppercase mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Tendência
          </div>
          <div
            className="flex items-center justify-center gap-1 text-lg font-bold"
            style={{ color: trendColor }}
          >
            <TrendIcon className="w-5 h-5" />
            <span>{TREND_LABELS[trend]}</span>
          </div>
        </div>
      </div>

      {/* Faixa de referência */}
      <div
        className="rounded-xl border p-4"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <h3
          className="text-xs font-semibold uppercase tracking-wider mb-2"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Faixa de Referência
        </h3>
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="relative w-full h-3 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--semantic-border-default)' }}>
              {/* Range bar */}
              <div
                className="absolute top-0 h-full rounded-full opacity-40"
                style={{
                  left: '0%',
                  width: '100%',
                  backgroundColor: 'var(--clinical-severity-normal-signal)',
                }}
              />
              {/* Current value indicator */}
              <div
                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white shadow"
                style={{
                  left: `${Math.min(100, Math.max(0, getRangePercentage(current_value, reference_range)))}%`,
                  backgroundColor: isWithinRange(current_value, reference_range)
                    ? 'var(--clinical-severity-normal-signal)'
                    : 'var(--clinical-severity-critical-signal)',
                }}
              />
            </div>
            <div className="flex justify-between text-[10px] mt-1" style={{ color: 'var(--semantic-text-secondary)' }}>
              <span>{reference_range.low}{unit}</span>
              <span>{reference_range.high}{unit}</span>
            </div>
          </div>
          <span
            className="text-sm font-semibold"
            style={{
              color: isWithinRange(current_value, reference_range)
                ? 'var(--clinical-severity-normal-on-surface)'
                : 'var(--clinical-severity-critical-on-surface)',
            }}
          >
            {isWithinRange(current_value, reference_range) ? 'Na faixa' : 'Fora da faixa'}
          </span>
        </div>
      </div>

      {/* Gráfico de tendência */}
      <div
        className="rounded-xl border p-4"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <h3
          className="text-xs font-semibold uppercase tracking-wider mb-3"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Histórico (30 dias)
        </h3>
        <MiniBarChart history={history} referenceRange={reference_range} unit={unit} />
      </div>

      {/* Tabela de últimos valores */}
      <div
        className="rounded-xl border p-4"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <HistoryTable history={history} referenceRange={reference_range} unit={unit} />
      </div>

      {/* Última atualização */}
      <div className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
        Atualizado em:{' '}
        {new Date(detail.updated_at).toLocaleString('pt-BR')}
      </div>
    </div>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Hash determinístico baseado em string — substitui Math.random() para reprodutibilidade */
function seededRandom(seed: string): number {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return (Math.abs(hash) % 10000) / 10000;
}

function generateFallbackHistory(
  baseValue: number,
  daysBack: number,
  indicatorId: string,
): IndicatorDetail['history'] {
  const now = Date.now();
  const points: IndicatorDetail['history'] = [];
  for (let i = daysBack - 1; i >= 0; i--) {
    const t = new Date(now - i * 24 * 60 * 60 * 1000);
    const noise = (seededRandom(indicatorId + '-noise-' + i) - 0.5) * baseValue * 0.15;
    points.push({
      timestamp: t.toISOString(),
      value: Math.round((baseValue + noise) * 10) / 10,
    });
  }
  return points;
}

// ─── Página Principal ────────────────────────────────────────────────────────

function IndicatorsPageContent() {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<
    'Todos' | IndicatorCategory
  >('Todos');
  const [selectedIndicatorId, setSelectedIndicatorId] = useState<string | null>(
    null,
  );

  const loadIndicators = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Simula fetch — usa dados mock
      await new Promise((resolve) => setTimeout(resolve, 800));

      // Validação: dados mock devem existir
      if (!MOCK_INDICATORS || MOCK_INDICATORS.length === 0) {
        throw new Error('Dados de indicadores indisponíveis');
      }

      setIndicators(MOCK_INDICATORS);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : 'Erro ao carregar indicadores',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIndicators();
  }, [loadIndicators]);

  // Filtro por categoria
  const filtered =
    selectedCategory === 'Todos'
      ? indicators
      : indicators.filter((i) => i.category === selectedCategory);

  // Meta summary
  const indicatorsInRange = filtered.filter((i) =>
    isWithinRange(i.current_value, i.reference_range),
  ).length;
  const totalFiltered = filtered.length;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1
              className="text-2xl font-bold"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              Indicadores
            </h1>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Métricas de qualidade assistencial
            </p>
          </div>
          <button
            onClick={loadIndicators}
            disabled={loading}
            className="p-2 rounded-lg border hover:opacity-80 disabled:opacity-50 transition-colors"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
            title="Atualizar"
          >
            <RefreshCw
              style={{ color: 'var(--semantic-text-secondary)' }}
              className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
          </button>
        </div>

        {/* Meta summary */}
        {!loading && !error && filtered.length > 0 && (
          <div
            className="rounded-xl border p-4 flex items-center gap-4"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{
                backgroundColor:
                  indicatorsInRange === totalFiltered
                    ? 'var(--clinical-severity-normal-wash)'
                    : 'var(--clinical-severity-watch-wash)',
              }}
            >
              <Target
                className="w-5 h-5"
                style={{
                  color:
                    indicatorsInRange === totalFiltered
                      ? 'var(--clinical-severity-normal-signal)'
                      : 'var(--clinical-severity-watch-signal)',
                }}
                aria-hidden="true"
              />
            </div>
            <div>
              <p
                className="text-sm font-semibold"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {indicatorsInRange} de {totalFiltered} indicadores dentro da meta
              </p>
              <p
                className="text-xs"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {indicatorsInRange === totalFiltered
                  ? 'Todos os indicadores estão dentro da faixa de referência.'
                  : `${totalFiltered - indicatorsInRange} indicadores requerem atenção.`}
              </p>
            </div>
          </div>
        )}

        {/* Category filter tabs */}
        {!loading && !error && (
          <div className="flex flex-wrap gap-2">
            {ALL_CATEGORIES.map((cat) => {
              const isActive = selectedCategory === cat;
              const catKey = cat as IndicatorCategory;
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none`}
                  style={{
                    backgroundColor: isActive
                      ? cat === 'Todos'
                        ? 'var(--semantic-surface-raised)'
                        : CATEGORY_BG_COLORS[catKey]
                      : 'transparent',
                    color: isActive
                      ? cat === 'Todos'
                        ? 'var(--semantic-text-primary)'
                        : CATEGORY_COLORS[catKey]
                      : 'var(--semantic-text-secondary)',
                    borderColor: isActive
                      ? cat === 'Todos'
                        ? 'var(--semantic-border-default)'
                        : CATEGORY_COLORS[catKey]
                      : 'var(--semantic-border-default)',
                    border: '1px solid',
                  }}
                >
                  {cat === 'Todos' ? 'Todos' : CATEGORY_LABELS[catKey]}
                  {cat !== 'Todos' && (
                    <span className="ml-1.5 text-xs opacity-70">
                      {indicators.filter((i) => i.category === cat).length}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {/* Loading state — skeleton grid */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <IndicatorCard
                key={i}
                indicator={MOCK_INDICATORS[0]!}
                isLoading
              />
            ))}
          </div>
        )}

        {/* Error state */}
        {error && (
          <div
            role="alert"
            aria-live="assertive"
            style={{
              backgroundColor: 'var(--clinical-severity-critical-wash)',
              borderColor: 'var(--clinical-severity-critical-signal)',
              color: 'var(--clinical-severity-critical-on-surface)',
            }}
            className="border rounded-xl p-6"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle
                className="w-6 h-6 flex-shrink-0 mt-0.5"
                style={{ color: 'var(--clinical-severity-critical-signal)' }}
                aria-hidden="true"
              />
              <div>
                <h2 className="font-semibold text-lg">Erro ao carregar indicadores</h2>
                <p className="text-sm mt-1 opacity-90">{error}</p>
                <button
                  onClick={loadIndicators}
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
        )}

        {/* Empty state */}
        {!loading && !error && filtered.length === 0 && (
          <div className="text-center py-20">
            <BarChart3
              className="w-12 h-12 mx-auto mb-4"
              style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
              aria-hidden="true"
            />
            <p
              className="text-lg font-medium"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Nenhum indicador encontrado
            </p>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {selectedCategory !== 'Todos'
                ? `Nenhum indicador na categoria "${CATEGORY_LABELS[selectedCategory]}".`
                : 'Nenhum indicador disponível no momento.'}
            </p>
            {selectedCategory !== 'Todos' && (
              <button
                onClick={() => setSelectedCategory('Todos')}
                className="mt-3 text-sm underline hover:no-underline"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                Ver todos os indicadores
              </button>
            )}
          </div>
        )}

        {/* Indicator cards grid */}
        {!loading && !error && filtered.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((indicator) => (
              <IndicatorCard
                key={indicator.id}
                indicator={indicator}
                onClick={(ind) => setSelectedIndicatorId(ind.id)}
              />
            ))}
          </div>
        )}

        {/* Detail Drawer */}
        <DrawerBuilder
          open={!!selectedIndicatorId}
          onClose={() => setSelectedIndicatorId(null)}
          title=""
          size="lg"
        >
          {selectedIndicatorId && (
            <IndicatorDetailPanel
              indicatorId={selectedIndicatorId}
              onClose={() => setSelectedIndicatorId(null)}
            />
          )}
        </DrawerBuilder>
      </div>
    </Layout>
  );
}

// ─── Export com ErrorBoundary ─────────────────────────────────────────────────

export default function IndicatorsPage() {
  return (
    <ErrorBoundary>
      <IndicatorsPageContent />
    </ErrorBoundary>
  );
}
