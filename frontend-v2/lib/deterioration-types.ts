// ─── Deterioration Types ─────────────────────────────────────────────────────
// FASE 4 — Tipos e dados mock para detecção precoce de piora clínica multi-domínio.
// Contrato deterioration-openapi.yaml alinhado com design-tokens.

import type React from 'react';

// ─── Domain ─────────────────────────────────────────────────────────────────

export type DeteriorationDomain =
  | 'respiratory'
  | 'hemodynamic'
  | 'sepsis'
  | 'neurologic'
  | 'renal';

// ─── Criteria status ────────────────────────────────────────────────────────

export type CriteriaStatus = 'normal' | 'alert' | 'critical';

// ─── Trend ──────────────────────────────────────────────────────────────────

export type DeteriorationTrend = 'improving' | 'stable' | 'worsening' | 'none';

// ─── Score categórico ───────────────────────────────────────────────────────

export type DeteriorationScoreValue = '0' | '1+' | '1-' | '3+' | '3-';

// ─── Criteria ───────────────────────────────────────────────────────────────

export interface DeteriorationCriteria {
  domain: DeteriorationDomain;
  name: string;
  status: CriteriaStatus;
  value?: string;
  threshold?: string;
  alert_id?: string;
}

// ─── Score ──────────────────────────────────────────────────────────────────

export interface DeteriorationScore {
  id: string;
  mpi_id: string;
  score: DeteriorationScoreValue;
  trend: DeteriorationTrend;
  criteria: DeteriorationCriteria[];
  domains_affected: number;
  recommendation: string;
  assessed_at: string;
  assessed_by: string;
}

// ─── Score Labels (PT-BR) ───────────────────────────────────────────────────

export const SCORE_LABELS: Record<DeteriorationScoreValue, string> = {
  '0': 'Sem deterioração detectada',
  '1+': 'Deterioração Leve (melhorando)',
  '1-': 'Deterioração Leve (piorando)',
  '3+': 'Deterioração Moderada/Grave (melhorando)',
  '3-': 'Deterioração Moderada/Grave (piorando)',
};

// ─── Score Short Labels (PT-BR) ─────────────────────────────────────────────

export const SCORE_SHORT_LABELS: Record<DeteriorationScoreValue, string> = {
  '0': 'Sem deterioração',
  '1+': 'Leve ↑',
  '1-': 'Leve ↓',
  '3+': 'Moderada ↑',
  '3-': 'Moderada ↓',
};

// ─── Score Colors (design tokens) ───────────────────────────────────────────

export interface ScoreColorTokens {
  signal: string;
  fill: string;
  onFill: string;
  wash: string;
  onSurface: string;
}

function scoreToken(scoreKey: string, variant: string): string {
  return `var(--clinical-deterioration-score-${scoreKey}-${variant})`;
}

export const SCORE_COLORS: Record<DeteriorationScoreValue, ScoreColorTokens> = {
  '0': {
    signal: scoreToken('0', 'signal-dark'),
    fill: scoreToken('0', 'fill'),
    onFill: scoreToken('0', 'on-fill'),
    wash: scoreToken('0', 'wash'),
    onSurface: scoreToken('0', 'on-surface-dark'),
  },
  '1+': {
    signal: scoreToken('1-plus', 'signal-dark'),
    fill: scoreToken('1-plus', 'fill'),
    onFill: scoreToken('1-plus', 'on-fill'),
    wash: scoreToken('1-plus', 'wash'),
    onSurface: scoreToken('1-plus', 'on-surface-dark'),
  },
  '1-': {
    signal: scoreToken('1-minus', 'signal-dark'),
    fill: scoreToken('1-minus', 'fill'),
    onFill: scoreToken('1-minus', 'on-fill'),
    wash: scoreToken('1-minus', 'wash'),
    onSurface: scoreToken('1-minus', 'on-surface-dark'),
  },
  '3+': {
    signal: scoreToken('3-plus', 'signal-dark'),
    fill: scoreToken('3-plus', 'fill'),
    onFill: scoreToken('3-plus', 'on-fill'),
    wash: scoreToken('3-plus', 'wash'),
    onSurface: scoreToken('3-plus', 'on-surface-dark'),
  },
  '3-': {
    signal: scoreToken('3-minus', 'signal-dark'),
    fill: scoreToken('3-minus', 'fill'),
    onFill: scoreToken('3-minus', 'on-fill'),
    wash: scoreToken('3-minus', 'wash'),
    onSurface: scoreToken('3-minus', 'on-surface-dark'),
  },
};

// ─── Domain Labels (PT-BR) ──────────────────────────────────────────────────

export const DOMAIN_LABELS: Record<DeteriorationDomain, string> = {
  respiratory: 'Respiratório',
  hemodynamic: 'Hemodinâmico',
  sepsis: 'Sepse',
  neurologic: 'Neurológico',
  renal: 'Renal',
};

// ─── Domain Icons (icon name mapping for Lucide) ────────────────────────────

export const DOMAIN_ICON_NAMES: Record<DeteriorationDomain, string> = {
  respiratory: 'Wind',
  hemodynamic: 'Heart',
  sepsis: 'Activity',
  neurologic: 'Brain',
  renal: 'Droplets',
};

// ─── Status Labels (PT-BR) ─────────────────────────────────────────────────

export const STATUS_LABELS: Record<CriteriaStatus, string> = {
  normal: 'Normal',
  alert: 'Alerta',
  critical: 'Crítico',
};

// ─── Status Colors ──────────────────────────────────────────────────────────

export const STATUS_COLORS: Record<CriteriaStatus, string> = {
  normal: 'var(--clinical-severity-normal-signal)',
  alert: 'var(--clinical-severity-watch-signal)',
  critical: 'var(--clinical-severity-critical-signal)',
};

// ─── Trend Labels (PT-BR) ───────────────────────────────────────────────────

export const TREND_LABELS: Record<DeteriorationTrend, string> = {
  improving: 'Melhorando',
  stable: 'Estável',
  worsening: 'Piorando',
  none: 'Sem tendência',
};

// ─── Helpers ────────────────────────────────────────────────────────────────

export function getScoreLabel(score: DeteriorationScoreValue): string {
  return SCORE_LABELS[score];
}

export function getScoreColor(score: DeteriorationScoreValue): ScoreColorTokens {
  return SCORE_COLORS[score];
}

export function getDomainLabel(domain: DeteriorationDomain): string {
  return DOMAIN_LABELS[domain];
}

export function getTrendIcon(trend: DeteriorationTrend): string {
  switch (trend) {
    case 'improving':
      return 'TrendingDown';
    case 'worsening':
      return 'TrendingUp';
    case 'stable':
      return 'Minus';
    default:
      return 'Minus';
  }
}

// ─── Score Order (for gauge positioning) ────────────────────────────────────

export const SCORE_ORDER: DeteriorationScoreValue[] = [
  '0',
  '1+',
  '1-',
  '3+',
  '3-',
];

// ─── Mock Data ──────────────────────────────────────────────────────────────

const now = new Date();
const hoursAgo = (h: number): string =>
  new Date(now.getTime() - h * 60 * 60 * 1000).toISOString();

/** Score atual — deterioração leve com tendência de piora */
export const MOCK_SCORE: DeteriorationScore = {
  id: 'det-2026-07-07-001',
  mpi_id: 'MPI-001',
  score: '1-',
  trend: 'worsening',
  domains_affected: 3,
  recommendation:
    'Paciente com deterioração leve em 3 domínios e tendência de piora. Recomenda-se reavaliação clínica em 4-6h, coleta de novos exames laboratoriais e monitorização contínua dos sinais vitais. Considerar escalonamento para UTI se houver progressão.',
  assessed_at: hoursAgo(1),
  assessed_by: 'Dr. Ana Costa',
  criteria: [
    {
      domain: 'respiratory',
      name: 'Frequência Respiratória',
      status: 'alert',
      value: '26 irpm',
      threshold: '≤ 20',
    },
    {
      domain: 'respiratory',
      name: 'SpO₂ / FiO₂',
      status: 'alert',
      value: '92%',
      threshold: '≥ 94%',
    },
    {
      domain: 'hemodynamic',
      name: 'Pressão Arterial Média',
      status: 'normal',
      value: '78 mmHg',
      threshold: '≥ 65',
    },
    {
      domain: 'hemodynamic',
      name: 'Lactato Sérico',
      status: 'critical',
      value: '3.2 mmol/L',
      threshold: '≤ 2.0',
      alert_id: 'alt-2026-07-07-042',
    },
    {
      domain: 'sepsis',
      name: 'qSOFA',
      status: 'alert',
      value: '2',
      threshold: '≤ 1',
    },
    {
      domain: 'neurologic',
      name: 'Escala de Glasgow',
      status: 'normal',
      value: '14',
      threshold: '≥ 13',
    },
    {
      domain: 'renal',
      name: 'Creatinina',
      status: 'critical',
      value: '2.1 mg/dL',
      threshold: '≤ 1.2',
      alert_id: 'alt-2026-07-07-043',
    },
    {
      domain: 'renal',
      name: 'Débito Urinário',
      status: 'alert',
      value: '0.4 mL/kg/h',
      threshold: '≥ 0.5',
    },
  ],
};

/** 10 scores históricos mostrando progressão temporal */
export const MOCK_HISTORY: DeteriorationScore[] = [
  {
    id: 'det-2026-07-01-001',
    mpi_id: 'MPI-001',
    score: '0',
    trend: 'none',
    domains_affected: 0,
    recommendation: 'Paciente estável, sem sinais de deterioração. Manter monitorização de rotina.',
    assessed_at: hoursAgo(144),
    assessed_by: 'Dr. Ana Costa',
    criteria: [],
  },
  {
    id: 'det-2026-07-02-001',
    mpi_id: 'MPI-001',
    score: '0',
    trend: 'stable',
    domains_affected: 0,
    recommendation: 'Sem alterações significativas. Monitorização mantida.',
    assessed_at: hoursAgo(120),
    assessed_by: 'Dr. Carlos Lima',
    criteria: [],
  },
  {
    id: 'det-2026-07-03-001',
    mpi_id: 'MPI-001',
    score: '1+',
    trend: 'improving',
    domains_affected: 1,
    recommendation: 'Leve alteração respiratória observada, com tendência de melhora. Observar.',
    assessed_at: hoursAgo(96),
    assessed_by: 'Dr. Ana Costa',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '22 irpm', threshold: '≤ 20' },
    ],
  },
  {
    id: 'det-2026-07-03-002',
    mpi_id: 'MPI-001',
    score: '1-',
    trend: 'worsening',
    domains_affected: 2,
    recommendation: 'Piora respiratória e início de instabilidade hemodinâmica. Aumentar vigilância.',
    assessed_at: hoursAgo(72),
    assessed_by: 'Dr. Carlos Lima',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '24 irpm', threshold: '≤ 20' },
      { domain: 'hemodynamic', name: 'Pressão Arterial Média', status: 'alert', value: '64 mmHg', threshold: '≥ 65' },
    ],
  },
  {
    id: 'det-2026-07-04-001',
    mpi_id: 'MPI-001',
    score: '1+',
    trend: 'improving',
    domains_affected: 1,
    recommendation: 'Melhora hemodinâmica após ajuste de fluidos. FR ainda elevada.',
    assessed_at: hoursAgo(48),
    assessed_by: 'Dr. Ana Costa',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '22 irpm', threshold: '≤ 20' },
    ],
  },
  {
    id: 'det-2026-07-05-001',
    mpi_id: 'MPI-001',
    score: '3-',
    trend: 'worsening',
    domains_affected: 3,
    recommendation: 'Piora significativa em múltiplos domínios. Avaliar transferência para UTI.',
    assessed_at: hoursAgo(36),
    assessed_by: 'Dr. Carlos Lima',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'critical', value: '32 irpm', threshold: '≤ 20', alert_id: 'alt-2026-07-05-010' },
      { domain: 'hemodynamic', name: 'Pressão Arterial Média', status: 'critical', value: '58 mmHg', threshold: '≥ 65', alert_id: 'alt-2026-07-05-011' },
      { domain: 'sepsis', name: 'qSOFA', status: 'critical', value: '3', threshold: '≤ 1', alert_id: 'alt-2026-07-05-012' },
    ],
  },
  {
    id: 'det-2026-07-05-002',
    mpi_id: 'MPI-001',
    score: '3+',
    trend: 'improving',
    domains_affected: 2,
    recommendation: 'Resposta positiva às intervenções. Hemodinâmica estabilizando.',
    assessed_at: hoursAgo(24),
    assessed_by: 'Dr. Ana Costa',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '24 irpm', threshold: '≤ 20' },
      { domain: 'hemodynamic', name: 'Pressão Arterial Média', status: 'alert', value: '66 mmHg', threshold: '≥ 65' },
    ],
  },
  {
    id: 'det-2026-07-06-001',
    mpi_id: 'MPI-001',
    score: '1+',
    trend: 'improving',
    domains_affected: 2,
    recommendation: 'Continua melhorando. FR ainda levemente elevada.',
    assessed_at: hoursAgo(12),
    assessed_by: 'Dr. Carlos Lima',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '22 irpm', threshold: '≤ 20' },
      { domain: 'renal', name: 'Creatinina', status: 'alert', value: '1.5 mg/dL', threshold: '≤ 1.2' },
    ],
  },
  {
    id: 'det-2026-07-07-000',
    mpi_id: 'MPI-001',
    score: '1-',
    trend: 'worsening',
    domains_affected: 2,
    recommendation: 'Nova piora observada. FR e creatinina em elevação. Coletar novos exames.',
    assessed_at: hoursAgo(4),
    assessed_by: 'Dr. Ana Costa',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '24 irpm', threshold: '≤ 20' },
      { domain: 'renal', name: 'Creatinina', status: 'alert', value: '1.8 mg/dL', threshold: '≤ 1.2' },
    ],
  },
  {
    id: 'det-2026-07-07-001',
    mpi_id: 'MPI-001',
    score: '1-',
    trend: 'worsening',
    domains_affected: 3,
    recommendation:
      'Paciente com deterioração leve em 3 domínios e tendência de piora. Recomenda-se reavaliação clínica em 4-6h, coleta de novos exames laboratoriais e monitorização contínua dos sinais vitais. Considerar escalonamento para UTI se houver progressão.',
    assessed_at: hoursAgo(1),
    assessed_by: 'Dr. Ana Costa',
    criteria: [
      { domain: 'respiratory', name: 'Frequência Respiratória', status: 'alert', value: '26 irpm', threshold: '≤ 20' },
      { domain: 'respiratory', name: 'SpO₂ / FiO₂', status: 'alert', value: '92%', threshold: '≥ 94%' },
      { domain: 'hemodynamic', name: 'Pressão Arterial Média', status: 'normal', value: '78 mmHg', threshold: '≥ 65' },
      { domain: 'hemodynamic', name: 'Lactato Sérico', status: 'critical', value: '3.2 mmol/L', threshold: '≤ 2.0', alert_id: 'alt-2026-07-07-042' },
      { domain: 'sepsis', name: 'qSOFA', status: 'alert', value: '2', threshold: '≤ 1' },
      { domain: 'neurologic', name: 'Escala de Glasgow', status: 'normal', value: '14', threshold: '≥ 13' },
      { domain: 'renal', name: 'Creatinina', status: 'critical', value: '2.1 mg/dL', threshold: '≤ 1.2', alert_id: 'alt-2026-07-07-043' },
      { domain: 'renal', name: 'Débito Urinário', status: 'alert', value: '0.4 mL/kg/h', threshold: '≥ 0.5' },
    ],
  },
];
