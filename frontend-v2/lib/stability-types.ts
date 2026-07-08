// ─── Stability Types ─────────────────────────────────────────────────────
// Contrato: stability-openapi.yaml
// Domínio: Estabilidade Hemodinâmica (27 critérios, 6 categorias)

// ─── Stability Criterion ──────────────────────────────────────────────────

export type StabilityCriterionStatus = 'normal' | 'warning' | 'critical';

export type StabilityCategory =
  | 'vasopressor'
  | 'perfusion'
  | 'cardiac_output'
  | 'fluid_balance'
  | 'lactate'
  | 'combined';

export interface StabilityCriterion {
  name: string;
  value: number;
  threshold: number;
  status: StabilityCriterionStatus;
  category: StabilityCategory;
  alert_id: string;
}

// ─── Stability Status ─────────────────────────────────────────────────────

export type StabilitySeverity = 'estavel' | 'atencao' | 'critico';

export interface StabilityStatus {
  mpi_id: string;
  score: number; // 0-27
  severity: StabilitySeverity;
  criteria: StabilityCriterion[]; // sempre 27
  recommendation: string;
  assessed_at: string;
}

// ─── Stability Trend ──────────────────────────────────────────────────────

export type StabilityDirection = 'improving' | 'stable' | 'worsening';

export interface StabilityTrendPoint {
  date: string;
  score: number;
  severity: StabilitySeverity;
  criteria_triggered: number;
}

export interface StabilityTrend {
  mpi_id: string;
  current: StabilityStatus;
  trend: StabilityTrendPoint[];
  direction: StabilityDirection;
  delta_7d: number;
}

// ─── Category Labels (PT-BR) ──────────────────────────────────────────────

export const STABILITY_CATEGORIES: StabilityCategory[] = [
  'vasopressor',
  'perfusion',
  'cardiac_output',
  'fluid_balance',
  'lactate',
  'combined',
];

export const CATEGORY_LABELS: Record<StabilityCategory, string> = {
  vasopressor: 'Vasopressor',
  perfusion: 'Perfusão',
  cardiac_output: 'Débito Cardíaco',
  fluid_balance: 'Balanço Hídrico',
  lactate: 'Lactato',
  combined: 'Combinados',
};

// ─── Helpers ──────────────────────────────────────────────────────────────

export function getCategoryLabel(category: StabilityCategory): string {
  return CATEGORY_LABELS[category];
}

export function getStatusEmoji(status: StabilityCriterionStatus): string {
  switch (status) {
    case 'normal':
      return '✅';
    case 'warning':
      return '⚠️';
    case 'critical':
      return '🚨';
  }
}

export function getSeverityLabel(severity: StabilitySeverity): string {
  switch (severity) {
    case 'estavel':
      return 'Estável';
    case 'atencao':
      return 'Atenção';
    case 'critico':
      return 'Crítico';
  }
}

// ─── Mock Data: 27 Critérios ──────────────────────────────────────────────

export const MOCK_CRITERIA: StabilityCriterion[] = [
  // ── Vasopressor (5) ───────────────────────────────────────────────────
  {
    name: 'Noradrenalina > 0.2 mcg/kg/min',
    value: 0.35,
    threshold: 0.2,
    status: 'critical',
    category: 'vasopressor',
    alert_id: 'stability-vaso-001',
  },
  {
    name: 'Vasopressina em uso',
    value: 1,
    threshold: 0,
    status: 'critical',
    category: 'vasopressor',
    alert_id: 'stability-vaso-002',
  },
  {
    name: 'Dose vasopressor escalonando (24h)',
    value: 1,
    threshold: 0,
    status: 'warning',
    category: 'vasopressor',
    alert_id: 'stability-vaso-003',
  },
  {
    name: 'Tempo de vasopressor > 24h',
    value: 18,
    threshold: 24,
    status: 'normal',
    category: 'vasopressor',
    alert_id: 'stability-vaso-004',
  },
  {
    name: 'Associação de vasopressores (≥ 2)',
    value: 2,
    threshold: 1,
    status: 'warning',
    category: 'vasopressor',
    alert_id: 'stability-vaso-005',
  },

  // ── Perfusão (5) ──────────────────────────────────────────────────────
  {
    name: 'TEC > 3s',
    value: 4.2,
    threshold: 3,
    status: 'critical',
    category: 'perfusion',
    alert_id: 'stability-perf-001',
  },
  {
    name: 'Lactato > 2 mmol/L',
    value: 3.8,
    threshold: 2,
    status: 'critical',
    category: 'perfusion',
    alert_id: 'stability-perf-002',
  },
  {
    name: 'Máculas cutâneas (mottling)',
    value: 1,
    threshold: 0,
    status: 'warning',
    category: 'perfusion',
    alert_id: 'stability-perf-003',
  },
  {
    name: 'PAM < 65 mmHg',
    value: 58,
    threshold: 65,
    status: 'critical',
    category: 'perfusion',
    alert_id: 'stability-perf-004',
  },
  {
    name: 'Índice de choque > 1.0',
    value: 1.3,
    threshold: 1.0,
    status: 'warning',
    category: 'perfusion',
    alert_id: 'stability-perf-005',
  },

  // ── Débito Cardíaco (4) ───────────────────────────────────────────────
  {
    name: 'IC < 2.2 L/min/m²',
    value: 1.9,
    threshold: 2.2,
    status: 'critical',
    category: 'cardiac_output',
    alert_id: 'stability-co-001',
  },
  {
    name: 'SvcO₂ < 65%',
    value: 58,
    threshold: 65,
    status: 'warning',
    category: 'cardiac_output',
    alert_id: 'stability-co-002',
  },
  {
    name: 'FEVE < 40% (ECO)',
    value: 45,
    threshold: 40,
    status: 'normal',
    category: 'cardiac_output',
    alert_id: 'stability-co-003',
  },
  {
    name: 'Variação de pressão de pulso > 13%',
    value: 15,
    threshold: 13,
    status: 'warning',
    category: 'cardiac_output',
    alert_id: 'stability-co-004',
  },

  // ── Balanço Hídrico (5) ───────────────────────────────────────────────
  {
    name: 'Balanço hídrico < -1000 mL/24h',
    value: -1450,
    threshold: -1000,
    status: 'warning',
    category: 'fluid_balance',
    alert_id: 'stability-fb-001',
  },
  {
    name: 'Edema agudo de pulmão',
    value: 0,
    threshold: 0,
    status: 'normal',
    category: 'fluid_balance',
    alert_id: 'stability-fb-002',
  },
  {
    name: 'Reposição volêmica > 30 mL/kg',
    value: 28,
    threshold: 30,
    status: 'normal',
    category: 'fluid_balance',
    alert_id: 'stability-fb-003',
  },
  {
    name: 'PVC > 12 mmHg',
    value: 10,
    threshold: 12,
    status: 'normal',
    category: 'fluid_balance',
    alert_id: 'stability-fb-004',
  },
  {
    name: 'Diurese < 0.5 mL/kg/h (6h)',
    value: 0.3,
    threshold: 0.5,
    status: 'warning',
    category: 'fluid_balance',
    alert_id: 'stability-fb-005',
  },

  // ── Lactato (4) ───────────────────────────────────────────────────────
  {
    name: 'Lactato > 4 mmol/L',
    value: 4.5,
    threshold: 4,
    status: 'critical',
    category: 'lactate',
    alert_id: 'stability-lac-001',
  },
  {
    name: 'Clearance lactato < 10% (2h)',
    value: 6,
    threshold: 10,
    status: 'critical',
    category: 'lactate',
    alert_id: 'stability-lac-002',
  },
  {
    name: 'Lactato > 2 mmol/L (> 24h)',
    value: 0,
    threshold: 0,
    status: 'normal',
    category: 'lactate',
    alert_id: 'stability-lac-003',
  },
  {
    name: 'Clearance lactato < 20% (6h)',
    value: 15,
    threshold: 20,
    status: 'warning',
    category: 'lactate',
    alert_id: 'stability-lac-004',
  },

  // ── Combinados (4) ────────────────────────────────────────────────────
  {
    name: 'Vasopressor + balanço negativo',
    value: 1,
    threshold: 0,
    status: 'critical',
    category: 'combined',
    alert_id: 'stability-comb-001',
  },
  {
    name: 'IC baixo + lactato alto',
    value: 1,
    threshold: 0,
    status: 'critical',
    category: 'combined',
    alert_id: 'stability-comb-002',
  },
  {
    name: 'TEC aumentado + PAM baixa',
    value: 1,
    threshold: 0,
    status: 'warning',
    category: 'combined',
    alert_id: 'stability-comb-003',
  },
  {
    name: 'PVC alta + diurese baixa',
    value: 0,
    threshold: 0,
    status: 'normal',
    category: 'combined',
    alert_id: 'stability-comb-004',
  },
];

// ─── Mock Status ──────────────────────────────────────────────────────────

export const MOCK_STATUS: StabilityStatus = {
  mpi_id: 'MPI-2026-0742',
  score: 14,
  severity: 'critico',
  criteria: MOCK_CRITERIA,
  recommendation:
    'Otimizar vasopressor guiado por PAM. Solicitar ECO para avaliar responsividade a volume. Coletar lactato seriado (2/2h). Considerar início de dobutamina se IC < 2.2 mantido após volume.',
  assessed_at: new Date().toISOString(),
};

// ─── Mock Trend (7 dias) ──────────────────────────────────────────────────

export const MOCK_TREND: StabilityTrend = {
  mpi_id: 'MPI-2026-0742',
  current: MOCK_STATUS,
  direction: 'worsening',
  delta_7d: 6,
  trend: [
    {
      date: new Date(Date.now() - 6 * 86400000).toISOString(),
      score: 8,
      severity: 'atencao',
      criteria_triggered: 8,
    },
    {
      date: new Date(Date.now() - 5 * 86400000).toISOString(),
      score: 7,
      severity: 'atencao',
      criteria_triggered: 7,
    },
    {
      date: new Date(Date.now() - 4 * 86400000).toISOString(),
      score: 10,
      severity: 'atencao',
      criteria_triggered: 10,
    },
    {
      date: new Date(Date.now() - 3 * 86400000).toISOString(),
      score: 11,
      severity: 'atencao',
      criteria_triggered: 11,
    },
    {
      date: new Date(Date.now() - 2 * 86400000).toISOString(),
      score: 12,
      severity: 'atencao',
      criteria_triggered: 12,
    },
    {
      date: new Date(Date.now() - 1 * 86400000).toISOString(),
      score: 13,
      severity: 'critico',
      criteria_triggered: 13,
    },
    {
      date: new Date().toISOString(),
      score: 14,
      severity: 'critico',
      criteria_triggered: 14,
    },
  ],
};

// ─── Severity helpers ─────────────────────────────────────────────────────

/** Computa severidade a partir do score (0-27) */
export function computeSeverity(score: number): StabilitySeverity {
  if (score >= 10) return 'critico';
  if (score >= 4) return 'atencao';
  return 'estavel';
}

/** Retorna a cor de fundo (wash) conforme severidade, usando tokens CSS */
export function getSeverityWashToken(severity: StabilitySeverity): string {
  switch (severity) {
    case 'estavel':
      return 'var(--clinical-stability-estavel-wash)';
    case 'atencao':
      return 'var(--clinical-stability-atencao-wash)';
    case 'critico':
      return 'var(--clinical-stability-critico-wash)';
  }
}

/** Retorna a cor de signal conforme severidade */
export function getSeveritySignalToken(severity: StabilitySeverity): string {
  switch (severity) {
    case 'estavel':
      return 'var(--clinical-stability-estavel-signal-dark)';
    case 'atencao':
      return 'var(--clinical-stability-atencao-signal-dark)';
    case 'critico':
      return 'var(--clinical-stability-critico-signal-dark)';
  }
}

/** Retorna a cor de on-surface conforme severidade */
export function getSeverityOnSurfaceToken(severity: StabilitySeverity): string {
  switch (severity) {
    case 'estavel':
      return 'var(--clinical-stability-estavel-on-surface-dark)';
    case 'atencao':
      return 'var(--clinical-stability-atencao-on-surface-dark)';
    case 'critico':
      return 'var(--clinical-stability-critico-on-surface-dark)';
  }
}

/** Retorna a cor de fill conforme severidade */
export function getSeverityFillToken(severity: StabilitySeverity): string {
  switch (severity) {
    case 'estavel':
      return 'var(--clinical-stability-estavel-fill)';
    case 'atencao':
      return 'var(--clinical-stability-atencao-fill)';
    case 'critico':
      return 'var(--clinical-stability-critico-fill)';
  }
}

/** Retorna a cor de on-fill conforme severidade */
export function getSeverityOnFillToken(severity: StabilitySeverity): string {
  switch (severity) {
    case 'estavel':
      return 'var(--clinical-stability-estavel-on-fill)';
    case 'atencao':
      return 'var(--clinical-stability-atencao-on-fill)';
    case 'critico':
      return 'var(--clinical-stability-critico-on-fill)';
  }
}

/** Retorna a cor de status (wash) para um critério especifico */
export function getCriterionWashToken(status: StabilityCriterionStatus): string {
  switch (status) {
    case 'normal':
      return 'var(--clinical-stability-estavel-wash)';
    case 'warning':
      return 'var(--clinical-stability-atencao-wash)';
    case 'critical':
      return 'var(--clinical-stability-critico-wash)';
  }
}

/** Retorna a cor de signal para um critério especifico */
export function getCriterionSignalToken(status: StabilityCriterionStatus): string {
  switch (status) {
    case 'normal':
      return 'var(--clinical-stability-estavel-signal-dark)';
    case 'warning':
      return 'var(--clinical-stability-atencao-signal-dark)';
    case 'critical':
      return 'var(--clinical-stability-critico-signal-dark)';
  }
}

/** Retorna label para direção da tendência */
export function getDirectionLabel(direction: StabilityDirection): string {
  switch (direction) {
    case 'improving':
      return 'Melhorando';
    case 'stable':
      return 'Estável';
    case 'worsening':
      return 'Piorando';
  }
}

/** Retorna o número de critérios alterados (warning + critical) */
export function countAlteredCriteria(criteria: StabilityCriterion[]): number {
  return criteria.filter((c) => c.status === 'warning' || c.status === 'critical').length;
}
