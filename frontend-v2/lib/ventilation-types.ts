// ─── Ventilation Types ───────────────────────────────────────────────────────
// FASE 2 — Tipos e dados mock para monitoramento de parâmetros ventilatórios.
// Contrato alinhado com ventilation-openapi.yaml.

// ─── Modos Ventilatórios ────────────────────────────────────────────────────

export type VentilationMode =
  | 'PCV'
  | 'VCV'
  | 'PSV'
  | 'SIMV'
  | 'CPAP'
  | 'BIPAP'
  | 'PRVC'
  | 'APRV'
  | 'NAVA'
  | 'ASV'
  | 'spontaneous';

/** Labels em PT-BR para cada modo ventilatório */
export const MODE_LABELS: Record<VentilationMode, string> = {
  PCV: 'Pressão Controlada',
  VCV: 'Volume Controlado',
  PSV: 'Pressão de Suporte',
  SIMV: 'Ventilação Mandatória Intermitente Sincronizada',
  CPAP: 'CPAP',
  BIPAP: 'BIPAP',
  PRVC: 'Volume Controlado com Pressão Regulada',
  APRV: 'Ventilação com Liberação de Pressão em Via Aérea',
  NAVA: 'Assistência Ventilatória Ajustada Neuralmente',
  ASV: 'Ventilação de Suporte Adaptativa',
  spontaneous: 'Espontânea',
};

// ─── Direção da tendência ──────────────────────────────────────────────────

export type TrendDirection = 'rising' | 'falling' | 'stable';

// ─── Parâmetros atuais ──────────────────────────────────────────────────────

export interface VentilationParameters {
  /** Modo ventilatório atual */
  mode: VentilationMode;
  /** Fração inspirada de oxigênio (0.21 a 1.00) */
  FiO2: number;
  /** Pressão positiva expiratória final (cmH₂O) */
  PEEP: number;
  /** Volume corrente (mL) */
  VC: number;
  /** Frequência respiratória (rpm) */
  FR: number;
  /** Pressão de platô (cmH₂O) */
  Pplat: number;
  /** Driving pressure = Pplat − PEEP (cmH₂O) */
  driving_pressure: number;
  /** Relação PaO₂/FiO₂ (índice de oxigenação) */
  PaO2_FiO2_ratio: number;
  /** Saturação periférica de oxigênio (%) */
  SpO2: number;
  /** Volume corrente por kg de peso corporal ideal (mL/kg) — opcional */
  tidal_volume_per_kg_pbw?: number;
  /** Frequência respiratória espontânea (rpm) — opcional */
  spontaneous_rate?: number;
  /** Timestamp ISO 8601 da coleta */
  collected_at: string;
  /** Origem dos dados (ex: 'ventilator', 'manual', 'lab') */
  source: string;
}

// ─── Série temporal de um parâmetro ─────────────────────────────────────────

export interface TrendPoint {
  /** Valor do parâmetro no momento da coleta */
  value: number;
  /** Timestamp ISO 8601 da coleta */
  collected_at: string;
}

export interface ParameterTrend {
  /** Valor atual (última aferição) */
  current: number;
  /** Valor mínimo no período */
  min: number;
  /** Valor máximo no período */
  max: number;
  /** Média no período */
  avg: number;
  /** Direção da tendência */
  direction: TrendDirection;
  /** Percentual de mudança no período */
  change_pct: number;
  /** Série temporal horária */
  series: TrendPoint[];
}

// ─── Tendência ventilatória (agregado) ──────────────────────────────────────

export interface VentilationTrend {
  /** Período em horas (24, 48 ou 72) */
  period_hours: number;
  /** Início do período (ISO 8601) */
  start_time: string;
  /** Fim do período (ISO 8601) */
  end_time: string;
  /** Tendências por parâmetro */
  parameters: {
    FiO2: ParameterTrend;
    PEEP: ParameterTrend;
    VC: ParameterTrend;
    FR: ParameterTrend;
    Pplat: ParameterTrend;
    driving_pressure: ParameterTrend;
    PaO2_FiO2_ratio: ParameterTrend;
  };
}

// ─── Helpers de formatação ──────────────────────────────────────────────────

/** Formata FiO₂: 0.40 → "40%" */
export function formatFiO2(val: number): string {
  return `${Math.round(val * 100)}%`;
}

/** Formata pressão em cmH₂O */
export function formatPressure(val: number): string {
  return `${val} cmH₂O`;
}

/** Formata volume em mL */
export function formatVolume(val: number): string {
  return `${val} mL`;
}

/** Formata FR em rpm */
export function formatFR(val: number): string {
  return `${val} rpm`;
}

/** Formata SpO₂ em % */
export function formatSpO2(val: number): string {
  return `${val}%`;
}

/** Formata relação P/F */
export function formatPFRatio(val: number): string {
  return val.toLocaleString('pt-BR');
}

/** Retorna cor do token clínico para cada modo ventilatório */
export function getModeColor(mode: VentilationMode): string {
  switch (mode) {
    case 'PCV':
    case 'PRVC':
    case 'BIPAP':
    case 'APRV':
      return 'var(--clinical-ventilation-pressure)';
    case 'VCV':
    case 'ASV':
      return 'var(--clinical-ventilation-volume)';
    case 'PSV':
    case 'NAVA':
      return 'var(--clinical-ventilation-support)';
    case 'SIMV':
      return 'var(--clinical-ventilation-mixed)';
    case 'CPAP':
    case 'spontaneous':
      return 'var(--clinical-ventilation-spontaneous)';
  }
}

/** Classifica gravidade da relação P/F (ARDS Berlin Definition) */
export type PFClass = 'normal' | 'mild' | 'moderate' | 'severe';

export function classifyPFRatio(ratio: number): PFClass {
  if (ratio > 300) return 'normal';
  if (ratio > 200) return 'mild';
  if (ratio > 100) return 'moderate';
  return 'severe';
}

export const PF_CLASS_LABELS: Record<PFClass, string> = {
  normal: 'Normal',
  mild: 'Leve',
  moderate: 'Moderado',
  severe: 'Grave',
};

/** Retorna cor para classificação P/F */
export function getPFColor(ratio: number): string {
  const cls = classifyPFRatio(ratio);
  switch (cls) {
    case 'normal':
      return 'var(--clinical-ventilation-pf-normal)';
    case 'mild':
      return 'var(--clinical-ventilation-pf-mild)';
    case 'moderate':
      return 'var(--clinical-ventilation-pf-moderate)';
    case 'severe':
      return 'var(--clinical-ventilation-pf-severe)';
  }
}

// ─── Mock: Parâmetros atuais ────────────────────────────────────────────────

export const MOCK_PARAMETERS: VentilationParameters = {
  mode: 'PCV',
  FiO2: 0.4,
  PEEP: 8,
  VC: 420,
  FR: 18,
  Pplat: 22,
  driving_pressure: 14,
  PaO2_FiO2_ratio: 185,
  SpO2: 94,
  tidal_volume_per_kg_pbw: 6.2,
  spontaneous_rate: 4,
  collected_at: new Date().toISOString(),
  source: 'ventilator',
};

// ─── Mock: Histórico de parâmetros ──────────────────────────────────────────

/** Gerador determinístico — substitui Math.random() para reprodutibilidade */
function seededRandom(seed: number): number {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function generateMockHistory(count: number): VentilationParameters[] {
  const now = Date.now();
  const records: VentilationParameters[] = [];

  for (let i = count - 1; i >= 0; i--) {
    const t = new Date(now - i * 2 * 60 * 60 * 1000); // a cada 2h
    records.push({
      mode: (['PCV', 'PCV', 'PCV', 'VCV', 'PCV', 'PSV', 'PCV', 'PCV', 'SIMV', 'PCV'] as VentilationMode[])[i] ?? 'PCV',
      FiO2: 0.35 + Math.round((seededRandom(i * 10 + 0) * 0.15) * 100) / 100,
      PEEP: 6 + Math.floor(seededRandom(i * 10 + 1) * 5),
      VC: 380 + Math.floor(seededRandom(i * 10 + 2) * 80),
      FR: 14 + Math.floor(seededRandom(i * 10 + 3) * 10),
      Pplat: 18 + Math.floor(seededRandom(i * 10 + 4) * 8),
      driving_pressure: 10 + Math.floor(seededRandom(i * 10 + 5) * 8),
      PaO2_FiO2_ratio: 150 + Math.floor(seededRandom(i * 10 + 6) * 100),
      SpO2: 92 + Math.floor(seededRandom(i * 10 + 7) * 7),
      tidal_volume_per_kg_pbw: 5.5 + Math.round(seededRandom(i * 10 + 8) * 2 * 10) / 10,
      spontaneous_rate: seededRandom(i * 10 + 9) > 0.5 ? Math.floor(seededRandom(i * 10 + 10) * 6) : undefined,
      collected_at: t.toISOString(),
      source: 'ventilator',
    });
  }

  return records;
}

export const MOCK_HISTORY: VentilationParameters[] = generateMockHistory(10);

// ─── Mock: Tendência 24h ───────────────────────────────────────────────────

function generateTrendSeries(
  baseValue: number,
  amplitude: number,
  count: number,
  hoursBack: number,
): TrendPoint[] {
  const now = Date.now();
  const series: TrendPoint[] = [];

  for (let i = count - 1; i >= 0; i--) {
    const t = new Date(now - i * (hoursBack / count) * 60 * 60 * 1000);
    const variation = (Math.sin(i / (count / 4)) * amplitude) + (seededRandom(i * 1000) - 0.5) * amplitude * 0.5;
    series.push({
      value: Math.round((baseValue + variation) * 10) / 10,
      collected_at: t.toISOString(),
    });
  }

  return series;
}

function makeParameterTrend(
  series: TrendPoint[],
): ParameterTrend {
  const values = series.map((s) => s.value);
  const current = values[values.length - 1] ?? 0;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const avg = Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 10) / 10;
  const first = values[0] ?? current;
  const change_pct = first !== 0 ? Math.round(((current - first) / Math.abs(first)) * 1000) / 10 : 0;

  let direction: TrendDirection = 'stable';
  if (change_pct > 3) direction = 'rising';
  else if (change_pct < -3) direction = 'falling';

  return { current, min, max, avg, direction, change_pct, series };
}

export function generateMockTrend(periodHours: number): VentilationTrend {
  const now = Date.now();
  const pointCount = periodHours; // 1 ponto por hora

  return {
    period_hours: periodHours,
    start_time: new Date(now - periodHours * 60 * 60 * 1000).toISOString(),
    end_time: new Date(now).toISOString(),
    parameters: {
      FiO2: makeParameterTrend(generateTrendSeries(0.40, 0.05, pointCount, periodHours)),
      PEEP: makeParameterTrend(generateTrendSeries(8, 1.5, pointCount, periodHours)),
      VC: makeParameterTrend(generateTrendSeries(420, 20, pointCount, periodHours)),
      FR: makeParameterTrend(generateTrendSeries(18, 3, pointCount, periodHours)),
      Pplat: makeParameterTrend(generateTrendSeries(22, 2, pointCount, periodHours)),
      driving_pressure: makeParameterTrend(generateTrendSeries(14, 2, pointCount, periodHours)),
      PaO2_FiO2_ratio: makeParameterTrend(generateTrendSeries(185, 25, pointCount, periodHours)),
    },
  };
}

export const MOCK_TREND: VentilationTrend = generateMockTrend(24);

// ─── Mock: Pacientes para seletor ───────────────────────────────────────────

export interface MockVentPatient {
  mpiId: string;
  name: string;
  bed: string;
}

export const MOCK_VENT_PATIENTS: MockVentPatient[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpiId: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpiId: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];

// ─── Labels de parâmetros em PT-BR ──────────────────────────────────────────

export const PARAM_LABELS: Record<string, string> = {
  FiO2: 'FiO₂',
  PEEP: 'PEEP',
  VC: 'Volume Corrente',
  FR: 'Frequência Respiratória',
  Pplat: 'Pressão de Platô',
  driving_pressure: 'Driving Pressure',
  PaO2_FiO2_ratio: 'Relação P/F',
};

export const PARAM_UNITS: Record<string, string> = {
  FiO2: '%',
  PEEP: 'cmH₂O',
  VC: 'mL',
  FR: 'rpm',
  Pplat: 'cmH₂O',
  driving_pressure: 'cmH₂O',
  PaO2_FiO2_ratio: '',
};
