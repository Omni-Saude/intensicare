// ─── Indicators Types ───────────────────────────────────────────────────────
// Tipos e dados mock para o dashboard de indicadores de qualidade assistencial.
// Contrato alinhado com indicadores-openapi.yaml (390 linhas, 31 regras legacy).
//
// Categorias: TLP, ocupação, sedação, ventilação, stewardship, segurança, eficiência.

import { TrendingDown, TrendingUp, Minus } from 'lucide-react';

// ─── Tipos Principais ────────────────────────────────────────────────────────

export type Trend = 'improving' | 'stable' | 'worsening';

export type IndicatorCategory =
  | 'TLP'
  | 'occupancy'
  | 'sedation'
  | 'ventilation'
  | 'stewardship'
  | 'safety'
  | 'efficiency';

export interface Indicator {
  id: string;
  name: string;
  category: IndicatorCategory;
  current_value: number;
  target?: number;
  trend: Trend;
  unit: string;
  reference_range: {
    low: number;
    high: number;
  };
  updated_at: string;
}

export interface IndicatorValuePoint {
  timestamp: string;
  value: number;
}

export interface IndicatorDetail extends Indicator {
  history: IndicatorValuePoint[];
}

// ─── Labels PT-BR ────────────────────────────────────────────────────────────

export const CATEGORY_LABELS: Record<IndicatorCategory, string> = {
  TLP: 'TLP',
  occupancy: 'Ocupação',
  sedation: 'Sedação',
  ventilation: 'Ventilação',
  stewardship: 'Stewardship',
  safety: 'Segurança',
  efficiency: 'Eficiência',
};

export const TREND_LABELS: Record<Trend, string> = {
  improving: 'Melhorando',
  stable: 'Estável',
  worsening: 'Piorando',
};

export const TREND_ICONS: Record<Trend, React.ComponentType<{ className?: string }>> = {
  improving: TrendingDown, // ↓ good — value decreasing toward target
  stable: Minus,
  worsening: TrendingUp, // ↑ bad — value moving away from target
};

// ─── Cores por Categoria ─────────────────────────────────────────────────────

export const CATEGORY_COLORS: Record<IndicatorCategory, string> = {
  TLP: '#6366f1', // indigo
  occupancy: '#3b82f6', // blue
  sedation: '#8b5cf6', // violet
  ventilation: '#06b6d4', // cyan
  stewardship: '#10b981', // emerald
  safety: '#ef4444', // red
  efficiency: '#f59e0b', // amber
};

export const CATEGORY_BG_COLORS: Record<IndicatorCategory, string> = {
  TLP: '#eef2ff',
  occupancy: '#eff6ff',
  sedation: '#f5f3ff',
  ventilation: '#ecfeff',
  stewardship: '#ecfdf5',
  safety: '#fef2f2',
  efficiency: '#fffbeb',
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Formata valor numérico com unidade para exibição */
export function formatValue(value: number, unit: string): string {
  if (unit === '%') {
    return `${value.toFixed(1)}%`;
  }
  if (unit === 'dias' || unit === 'horas') {
    return `${value.toFixed(1)} ${unit}`;
  }
  if (unit === 'eventos/1000') {
    return `${value.toFixed(2)}`;
  }
  return `${value.toFixed(1)} ${unit}`;
}

/** Retorna a cor CSS para o valor do indicador (within range = green, outside = red) */
export function getTrendColor(trend: Trend): string {
  switch (trend) {
    case 'improving':
      return 'var(--clinical-severity-normal-on-surface)';
    case 'stable':
      return 'var(--semantic-text-secondary)';
    case 'worsening':
      return 'var(--clinical-severity-critical-on-surface)';
  }
}

/** Retorna cor CSS da categoria */
export function getCategoryColor(category: IndicatorCategory): string {
  return CATEGORY_COLORS[category] ?? 'var(--semantic-text-secondary)';
}

/** Verifica se o valor está dentro do reference_range */
export function isWithinRange(value: number, range: { low: number; high: number }): boolean {
  return value >= range.low && value <= range.high;
}

/** Calcula a porcentagem do valor em relação ao reference_range (para barra de progresso) */
export function getRangePercentage(value: number, range: { low: number; high: number }): number {
  const span = range.high - range.low;
  if (span <= 0) return 50; // fallback
  const pct = ((value - range.low) / span) * 100;
  return Math.max(0, Math.min(100, pct));
}

// ─── Mock: 12 Indicadores ────────────────────────────────────────────────────

export const MOCK_INDICATORS: Indicator[] = [
  // TLP
  {
    id: 'tlp-adherence',
    name: 'Adesão ao TLP',
    category: 'TLP',
    current_value: 87.3,
    target: 90,
    trend: 'improving',
    unit: '%',
    reference_range: { low: 70, high: 95 },
    updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
  },
  {
    id: 'tlp-screening',
    name: 'Triagem TLP em 24h',
    category: 'TLP',
    current_value: 94.1,
    target: 95,
    trend: 'stable',
    unit: '%',
    reference_range: { low: 80, high: 100 },
    updated_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
  },
  // Ocupação
  {
    id: 'occupancy-rate',
    name: 'Taxa de Ocupação',
    category: 'occupancy',
    current_value: 82.5,
    target: 85,
    trend: 'stable',
    unit: '%',
    reference_range: { low: 75, high: 90 },
    updated_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
  },
  {
    id: 'avg-los',
    name: 'Tempo Médio de Permanência',
    category: 'occupancy',
    current_value: 7.2,
    target: 6.0,
    trend: 'worsening',
    unit: 'dias',
    reference_range: { low: 4, high: 8 },
    updated_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
  },
  // Sedação
  {
    id: 'rass-target',
    name: 'RASS no Alvo (0 a -2)',
    category: 'sedation',
    current_value: 72.8,
    target: 80,
    trend: 'improving',
    unit: '%',
    reference_range: { low: 60, high: 90 },
    updated_at: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
  },
  {
    id: 'daily-awakening',
    name: 'Despertar Diário Realizado',
    category: 'sedation',
    current_value: 65.4,
    target: 85,
    trend: 'worsening',
    unit: '%',
    reference_range: { low: 60, high: 100 },
    updated_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
  },
  // Ventilação
  {
    id: 'extubation-rate',
    name: 'Taxa de Extubação Acidental',
    category: 'ventilation',
    current_value: 1.8,
    target: 1.0,
    trend: 'worsening',
    unit: 'eventos/1000',
    reference_range: { low: 0, high: 2.5 },
    updated_at: new Date(Date.now() - 40 * 60 * 1000).toISOString(),
  },
  {
    id: 'vap-rate',
    name: 'Densidade de PAV',
    category: 'ventilation',
    current_value: 3.2,
    target: 3.0,
    trend: 'improving',
    unit: 'eventos/1000',
    reference_range: { low: 0, high: 5.0 },
    updated_at: new Date(Date.now() - 50 * 60 * 1000).toISOString(),
  },
  // Stewardship
  {
    id: 'antimicrobial-days',
    name: 'Dias de Antimicrobiano',
    category: 'stewardship',
    current_value: 580,
    target: 500,
    trend: 'stable',
    unit: 'dias',
    reference_range: { low: 400, high: 650 },
    updated_at: new Date(Date.now() - 55 * 60 * 1000).toISOString(),
  },
  // Segurança
  {
    id: 'clabsi-rate',
    name: 'Densidade de IPCS',
    category: 'safety',
    current_value: 1.4,
    target: 1.0,
    trend: 'improving',
    unit: 'eventos/1000',
    reference_range: { low: 0, high: 2.0 },
    updated_at: new Date(Date.now() - 35 * 60 * 1000).toISOString(),
  },
  {
    id: 'fall-rate',
    name: 'Taxa de Quedas',
    category: 'safety',
    current_value: 1.1,
    target: 0.5,
    trend: 'worsening',
    unit: 'eventos/1000',
    reference_range: { low: 0, high: 1.5 },
    updated_at: new Date(Date.now() - 65 * 60 * 1000).toISOString(),
  },
  // Eficiência
  {
    id: 'readmission-48h',
    name: 'Reinternação em 48h',
    category: 'efficiency',
    current_value: 3.5,
    target: 2.0,
    trend: 'improving',
    unit: '%',
    reference_range: { low: 0, high: 5.0 },
    updated_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
  },
];

// ─── Mock: Detalhe com Histórico (30 pontos) ─────────────────────────────────

function generateHistory(
  baseValue: number,
  trend: Trend,
  variance: number,
  daysBack: number,
): IndicatorValuePoint[] {
  const now = Date.now();
  const points: IndicatorValuePoint[] = [];

  for (let i = daysBack - 1; i >= 0; i--) {
    const t = new Date(now - i * 24 * 60 * 60 * 1000);
    // Trend bias: improving → slight decrease, worsening → slight increase
    const trendBias =
      trend === 'improving' ? -i * 0.02 : trend === 'worsening' ? i * 0.02 : 0;
    // Deterministic noise: seeded from baseValue + day index for reproducibility
    const seed = (baseValue * 31 + i * 17) % 10000;
    const noise = ((seed / 10000) - 0.5) * variance;
    const value = baseValue + trendBias + noise;

    points.push({
      timestamp: t.toISOString(),
      value: Math.round(value * 10) / 10,
    });
  }

  return points;
}

export const MOCK_DETAILS: Record<string, IndicatorDetail> = {
  'tlp-adherence': {
    ...MOCK_INDICATORS[0]!,
    history: generateHistory(87.3, 'improving', 3.0, 30),
  },
  'extubation-rate': {
    ...MOCK_INDICATORS[6]!,
    history: generateHistory(1.8, 'worsening', 0.4, 30),
  },
};
