// ─── Sedation Types ──────────────────────────────────────────────────────────
// FASE 2 — Tipos e dados mock para monitoramento de sedação (RASS, BPS/NRS, CAM-ICU).
// Contrato alinhado com sedacao-openapi.yaml.

// ─── Tipos Principais ────────────────────────────────────────────────────────

export interface SedationAssessment {
  id: string;
  mpi_id: string;
  /** Richmond Agitation-Sedation Scale: -5 (incapaz de despertar) a +4 (combativo) */
  rass_score: number;
  /** Behavioral Pain Scale (3-12) ou Numeric Rating Scale (0-10). Opcional. */
  bps_nrs_score?: number;
  /** Indica qual escala de dor foi utilizada. null se não avaliada */
  bps_nrs_type?: 'BPS' | 'NRS';
  /** CAM-ICU positivo para delirium? null = não avaliado */
  cam_icu_positive?: boolean | null;
  /** Timestamp ISO 8601 da avaliação */
  assessed_at: string;
  /** Nome do profissional que realizou a avaliação (opcional) */
  assessed_by?: string;
  /** Notas clínicas adicionais (opcional) */
  notes?: string;
}

export interface SedationAssessmentCreate {
  mpi_id: string;
  rass_score: number;
  bps_nrs_score?: number;
  bps_nrs_type?: 'BPS' | 'NRS';
  cam_icu_positive?: boolean | null;
  assessed_by?: string;
  notes?: string;
}

// ─── RASS Labels (PT-BR) ────────────────────────────────────────────────────

/** Labels em PT-BR para cada valor da escala RASS (-5 a +4) */
export const RASS_LABELS: Record<number, string> = {
  [-5]: 'Incapaz de despertar',
  [-4]: 'Sedação profunda',
  [-3]: 'Sedação moderada',
  [-2]: 'Sedação leve',
  [-1]: 'Sonolento',
  [0]: 'Alerta e calmo',
  [1]: 'Inquieto',
  [2]: 'Agitado',
  [3]: 'Muito agitado',
  [4]: 'Combativo',
};

// ─── RASS Colors ─────────────────────────────────────────────────────────────

/**
 * Cores para a escala RASS:
 * -5 a -4: vermelho (sedação profunda — risco)
 * -3 a -1: âmbar (sedação leve a moderada — atenção)
 * 0: verde (alvo terapêutico)
 * +1 a +4: vermelho (agitação — risco)
 */
export const RASS_COLORS: Record<number, string> = {
  [-5]: 'var(--clinical-severity-critical-signal)',
  [-4]: 'var(--clinical-severity-critical-signal)',
  [-3]: 'var(--clinical-severity-watch-signal)',
  [-2]: 'var(--clinical-severity-watch-signal)',
  [-1]: 'var(--clinical-severity-watch-signal)',
  [0]: 'var(--clinical-severity-normal-signal)',
  [1]: 'var(--clinical-severity-critical-signal)',
  [2]: 'var(--clinical-severity-critical-signal)',
  [3]: 'var(--clinical-severity-critical-signal)',
  [4]: 'var(--clinical-severity-critical-signal)',
};

/** Cores de fundo (wash) para RASS */
export const RASS_BG_COLORS: Record<number, string> = {
  [-5]: 'var(--clinical-severity-critical-wash)',
  [-4]: 'var(--clinical-severity-critical-wash)',
  [-3]: 'var(--clinical-severity-watch-wash)',
  [-2]: 'var(--clinical-severity-watch-wash)',
  [-1]: 'var(--clinical-severity-watch-wash)',
  [0]: 'var(--clinical-severity-normal-wash)',
  [1]: 'var(--clinical-severity-critical-wash)',
  [2]: 'var(--clinical-severity-critical-wash)',
  [3]: 'var(--clinical-severity-critical-wash)',
  [4]: 'var(--clinical-severity-critical-wash)',
};

// ─── CAM-ICU Labels ─────────────────────────────────────────────────────────

export type CAMICUResult = 'positive' | 'negative' | 'not_assessed';

export const CAM_ICU_LABELS: Record<CAMICUResult, string> = {
  positive: 'Delirium positivo',
  negative: 'Sem delirium',
  not_assessed: 'Não avaliado',
};

export const CAM_ICU_COLORS: Record<CAMICUResult, string> = {
  positive: 'var(--clinical-severity-critical-signal)',
  negative: 'var(--clinical-severity-normal-signal)',
  not_assessed: 'var(--semantic-text-secondary)',
};

export const CAM_ICU_BG_COLORS: Record<CAMICUResult, string> = {
  positive: 'var(--clinical-severity-critical-wash)',
  negative: 'var(--clinical-severity-normal-wash)',
  not_assessed: 'var(--semantic-surface-overlay)',
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Retorna o label PT-BR para um valor RASS */
export function getRASSLabel(score: number): string {
  return RASS_LABELS[score] ?? `RASS ${score > 0 ? '+' : ''}${score}`;
}

/** Retorna a cor de sinal (signal) para um valor RASS */
export function getRASSColor(score: number): string {
  return RASS_COLORS[score] ?? 'var(--semantic-text-secondary)';
}

/** Retorna a cor de fundo (wash) para um valor RASS */
export function getRASSBgColor(score: number): string {
  return RASS_BG_COLORS[score] ?? 'var(--semantic-surface-overlay)';
}

/** Classifica o score BPS/NRS em categoria de dor */
export type PainCategory = 'sem_dor' | 'leve' | 'moderada' | 'intensa' | 'nao_avaliada';

export function getBPSNRSCategory(
  score?: number,
  type?: 'BPS' | 'NRS',
): PainCategory {
  if (score === undefined || score === null) return 'nao_avaliada';
  if (type === 'BPS') {
    // BPS: 3-12. 3=sem dor, 4-6=leve, 7-9=moderada, 10-12=intensa
    if (score <= 3) return 'sem_dor';
    if (score <= 6) return 'leve';
    if (score <= 9) return 'moderada';
    return 'intensa';
  }
  // NRS: 0-10. 0=sem dor, 1-3=leve, 4-6=moderada, 7-10=intensa
  if (score === 0) return 'sem_dor';
  if (score <= 3) return 'leve';
  if (score <= 6) return 'moderada';
  return 'intensa';
}

export const PAIN_CATEGORY_LABELS: Record<PainCategory, string> = {
  sem_dor: 'Sem dor',
  leve: 'Dor leve',
  moderada: 'Dor moderada',
  intensa: 'Dor intensa',
  nao_avaliada: 'Não avaliada',
};

export const PAIN_CATEGORY_COLORS: Record<PainCategory, string> = {
  sem_dor: 'var(--clinical-severity-normal-signal)',
  leve: 'var(--clinical-severity-watch-signal)',
  moderada: 'var(--clinical-severity-watch-signal)',
  intensa: 'var(--clinical-severity-critical-signal)',
  nao_avaliada: 'var(--semantic-text-secondary)',
};

/** Formata o resultado CAM-ICU para exibição */
export function formatCAMICU(value?: boolean | null): CAMICUResult {
  if (value === true) return 'positive';
  if (value === false) return 'negative';
  return 'not_assessed';
}

/** Retorna label para CAM-ICU */
export function getCAMICULabel(value?: boolean | null): string {
  return CAM_ICU_LABELS[formatCAMICU(value)];
}

/** Retorna cor de sinal para CAM-ICU */
export function getCAMICUIColor(value?: boolean | null): string {
  return CAM_ICU_COLORS[formatCAMICU(value)];
}

/** Retorna cor de fundo para CAM-ICU */
export function getCAMICUBgColor(value?: boolean | null): string {
  return CAM_ICU_BG_COLORS[formatCAMICU(value)];
}

/** Formata timestamp ISO → dd/MM/yyyy HH:mm (PT-BR) */
export function formatSedationTimestamp(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '--/--/---- --:--';
  }
}

// ─── Mock: Avaliação atual ───────────────────────────────────────────────────

export const MOCK_ASSESSMENT: SedationAssessment = {
  id: 'sed-001',
  mpi_id: 'MPI-001',
  rass_score: -2,
  bps_nrs_score: 4,
  bps_nrs_type: 'BPS',
  cam_icu_positive: false,
  assessed_at: new Date().toISOString(),
  assessed_by: 'Dr(a). Ana Costa',
  notes: 'Paciente em sedação leve conforme protocolo. BPS 4 — sem dor significativa.',
};

// ─── Mock: Histórico de avaliações (10 registros) ────────────────────────────

function generateMockHistory(): SedationAssessment[] {
  const now = Date.now();
  const records: SedationAssessment[] = [];

  // RASS variation pattern: -4 → -3 → -2 → -1 → -2 → -2 → -1 → 0 → -1 → -2
  const rassValues = [-4, -3, -2, -1, -2, -2, -1, 0, -1, -2];
  const bpsValues = [6, 5, 5, 4, 3, 4, 4, 3, 4, 4];
  const bpsTypes: Array<'BPS' | 'NRS'> = ['BPS', 'BPS', 'BPS', 'BPS', 'BPS', 'NRS', 'BPS', 'BPS', 'BPS', 'BPS'];
  const camIcuValues: Array<boolean | null> = [true, false, false, false, false, false, null, false, false, false];
  const assessors = [
    'Dr(a). Ana Costa',
    'Dr. Pedro Lima',
    'Dr(a). Ana Costa',
    'Enf. Maria Silva',
    'Enf. Maria Silva',
    'Dr(a). Ana Costa',
    'Dr. Pedro Lima',
    'Dr(a). Ana Costa',
    'Enf. João Santos',
    'Dr(a). Ana Costa',
  ];

  for (let i = 9; i >= 0; i--) {
    const t = new Date(now - i * 4 * 60 * 60 * 1000); // a cada 4h
    const idx = 9 - i;
    records.push({
      id: `sed-hist-${String(idx + 1).padStart(3, '0')}`,
      mpi_id: 'MPI-001',
      rass_score: rassValues[idx] ?? -2,
      bps_nrs_score: bpsValues[idx] ?? 4,
      bps_nrs_type: bpsTypes[idx] ?? 'BPS',
      cam_icu_positive: camIcuValues[idx] ?? false,
      assessed_at: t.toISOString(),
      assessed_by: assessors[idx] ?? 'Dr(a). Ana Costa',
      notes: idx === 9 ? 'Sedação mantida conforme protocolo.' : undefined,
    });
  }

  return records;
}

export const MOCK_HISTORY: SedationAssessment[] = generateMockHistory();

// ─── Mock: Pacientes para seletor ───────────────────────────────────────────

export interface MockSedationPatient {
  mpiId: string;
  name: string;
  bed: string;
}

export const MOCK_PATIENTS: MockSedationPatient[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpiId: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpiId: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];
