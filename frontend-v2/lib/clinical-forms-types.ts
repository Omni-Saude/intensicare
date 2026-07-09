// ─── Clinical Forms Types & Helpers ─────────────────────────────────────────
// PT-BR — Tipos compartilhados para formulários clínicos (SOFA, Glasgow, RASS, CAM-ICU, BPS/NRS, LPP)

// ─── Enums / Unions ────────────────────────────────────────────────────────

export type FormType = 'rass' | 'cam_icu' | 'bps_nrs' | 'glasgow' | 'sofa' | 'lpp';

/** Catálogo de um tipo de formulário clínico */
export interface ClinicalFormType {
  id: FormType;
  name: string; // PT-BR
  description: string;
  scoreRange: {
    min: number;
    max: number;
  };
  fields: {
    name: string;
    label: string;
    type: 'select' | 'number' | 'checkbox' | 'string';
    options?: { value: string; label: string }[];
    min?: number;
    max?: number;
  }[];
}

/** Uma submissão de formulário clínico */
export interface ClinicalForm {
  id: string;
  mpiId: string;
  formType: FormType;
  data: Record<string, any>;
  score: number | null;
  createdAt: string; // ISO 8601
  createdBy?: string;
  notes?: string;
}

// ─── Labels & Descriptions (PT-BR) ─────────────────────────────────────────

export const FORM_LABELS: Record<FormType, string> = {
  rass: 'RASS',
  cam_icu: 'CAM-ICU',
  bps_nrs: 'BPS/NRS',
  glasgow: 'Glasgow',
  sofa: 'SOFA',
  lpp: 'Lesão por Pressão (Braden/NPUAP)',
};

export const FORM_DESCRIPTIONS: Record<FormType, string> = {
  rass: 'Richmond Agitation-Sedation Scale — Avaliação de sedação e agitação na UTI.',
  cam_icu: 'Confusion Assessment Method for ICU — Triagem de delirium.',
  bps_nrs: 'Behavioral Pain Scale / Numeric Rating Scale — Avaliação de dor.',
  glasgow: 'Escala de Coma de Glasgow — Avaliação do nível de consciência.',
  sofa: 'Sequential Organ Failure Assessment — Avaliação de disfunção orgânica.',
  lpp: 'Avaliação de risco para Lesão por Pressão — Escala de Braden e classificação NPUAP.',
};

export const FORM_SCORE_RANGES: Record<FormType, { min: number; max: number }> = {
  rass: { min: -5, max: 4 },
  cam_icu: { min: 0, max: 1 },
  bps_nrs: { min: 0, max: 12 },
  glasgow: { min: 3, max: 15 },
  sofa: { min: 0, max: 24 },
  lpp: { min: 6, max: 23 },
};

// ─── SOFA Systems ──────────────────────────────────────────────────────────

export interface SOFASystemScore {
  system: string;
  label: string;
  score: number; // 0–4
}

export const SOFA_SYSTEMS = [
  { key: 'sofaRespiratorio', label: 'Respiratório' },
  { key: 'sofaCoagulacao', label: 'Coagulação' },
  { key: 'sofaHepatico', label: 'Hepático' },
  { key: 'sofaCardiovascular', label: 'Cardiovascular' },
  { key: 'sofaNeurologico', label: 'Neurológico' },
  { key: 'sofaRenal', label: 'Renal' },
] as const;

// ─── Glasgow Components ────────────────────────────────────────────────────

export interface GlasgowComponentScore {
  component: string;
  label: string;
  score: number;
  maxScore: number;
}

export const GLASGOW_COMPONENTS = [
  { key: 'glasgowOcular', label: 'Abertura Ocular', maxScore: 4 },
  { key: 'glasgowVerbal', label: 'Resposta Verbal', maxScore: 5 },
  { key: 'glasgowMotora', label: 'Resposta Motora', maxScore: 6 },
] as const;

// ─── Mock Form Types Catalog ───────────────────────────────────────────────

export const MOCK_FORM_TYPES: ClinicalFormType[] = [
  {
    id: 'rass',
    name: 'RASS',
    description: FORM_DESCRIPTIONS.rass,
    scoreRange: { min: -5, max: 4 },
    fields: [
      { name: 'rassScore', label: 'Escore RASS', type: 'select', min: -5, max: 4 },
      { name: 'rassNote', label: 'Observação', type: 'string' },
    ],
  },
  {
    id: 'cam_icu',
    name: 'CAM-ICU',
    description: FORM_DESCRIPTIONS.cam_icu,
    scoreRange: { min: 0, max: 1 },
    fields: [
      { name: 'camFeature1', label: 'Início Agudo / Flutuante', type: 'checkbox' },
      { name: 'camFeature2', label: 'Desatenção', type: 'checkbox' },
      { name: 'camFeature3', label: 'Nível de Consciência Alterado', type: 'checkbox' },
      { name: 'camFeature4', label: 'Pensamento Desorganizado', type: 'checkbox' },
    ],
  },
  {
    id: 'bps_nrs',
    name: 'BPS/NRS',
    description: FORM_DESCRIPTIONS.bps_nrs,
    scoreRange: { min: 0, max: 12 },
    fields: [
      { name: 'bpsScore', label: 'Escore BPS', type: 'select', min: 3, max: 12 },
      { name: 'nrsScore', label: 'Escore NRS', type: 'select', min: 0, max: 10 },
    ],
  },
  {
    id: 'glasgow',
    name: 'Glasgow',
    description: FORM_DESCRIPTIONS.glasgow,
    scoreRange: { min: 3, max: 15 },
    fields: [
      { name: 'glasgowOcular', label: 'Abertura Ocular', type: 'select', min: 1, max: 4 },
      { name: 'glasgowVerbal', label: 'Resposta Verbal', type: 'select', min: 1, max: 5 },
      { name: 'glasgowMotora', label: 'Resposta Motora', type: 'select', min: 1, max: 6 },
    ],
  },
  {
    id: 'sofa',
    name: 'SOFA',
    description: FORM_DESCRIPTIONS.sofa,
    scoreRange: { min: 0, max: 24 },
    fields: SOFA_SYSTEMS.map((s) => ({
      name: s.key,
      label: s.label,
      type: 'select' as const,
      min: 0,
      max: 4,
    })),
  },
];

// ─── Mock Submitted Forms ──────────────────────────────────────────────────

export const MOCK_FORMS: ClinicalForm[] = [
  // Paciente MPI-001
  {
    id: 'form-001',
    mpiId: 'MPI-001',
    formType: 'rass',
    data: { rassScore: '-2', rassNote: 'Sedação leve após midazolam' },
    score: -2,
    createdAt: '2026-07-08T08:00:00Z',
    createdBy: 'Dr. Silva',
  },
  {
    id: 'form-002',
    mpiId: 'MPI-001',
    formType: 'cam_icu',
    data: { camFeature1: true, camFeature2: true, camFeature3: true, camFeature4: false },
    score: 0,
    createdAt: '2026-07-08T08:15:00Z',
    createdBy: 'Dr. Silva',
    notes: 'CAM-ICU negativo — sem delirium.',
  },
  {
    id: 'form-003',
    mpiId: 'MPI-001',
    formType: 'sofa',
    data: {
      sofaRespiratorio: '2',
      sofaCoagulacao: '1',
      sofaHepatico: '0',
      sofaCardiovascular: '3',
      sofaNeurologico: '1',
      sofaRenal: '2',
      sofaNote: 'Paciente em choque séptico. Piora cardiovascular.',
    },
    score: 9,
    createdAt: '2026-07-08T09:00:00Z',
    createdBy: 'Dr. Silva',
  },
  {
    id: 'form-004',
    mpiId: 'MPI-001',
    formType: 'glasgow',
    data: { glasgowOcular: '3', glasgowVerbal: '4', glasgowMotora: '5', glasgowNote: 'Paciente sedado (RASS -2).' },
    score: 12,
    createdAt: '2026-07-08T09:10:00Z',
    createdBy: 'Dr. Silva',
  },
  // Paciente MPI-002
  {
    id: 'form-005',
    mpiId: 'MPI-002',
    formType: 'rass',
    data: { rassScore: '0', rassNote: 'Alerta e calmo.' },
    score: 0,
    createdAt: '2026-07-08T07:30:00Z',
    createdBy: 'Enf. Costa',
  },
  {
    id: 'form-006',
    mpiId: 'MPI-002',
    formType: 'sofa',
    data: {
      sofaRespiratorio: '0',
      sofaCoagulacao: '0',
      sofaHepatico: '0',
      sofaCardiovascular: '0',
      sofaNeurologico: '0',
      sofaRenal: '0',
      sofaNote: 'Paciente estável, sem disfunções orgânicas.',
    },
    score: 0,
    createdAt: '2026-07-08T08:00:00Z',
    createdBy: 'Enf. Costa',
  },
  {
    id: 'form-007',
    mpiId: 'MPI-002',
    formType: 'glasgow',
    data: { glasgowOcular: '4', glasgowVerbal: '5', glasgowMotora: '6', glasgowNote: 'Glasgow normal.' },
    score: 15,
    createdAt: '2026-07-08T08:05:00Z',
    createdBy: 'Enf. Costa',
  },
  // Paciente MPI-003
  {
    id: 'form-008',
    mpiId: 'MPI-003',
    formType: 'sofa',
    data: {
      sofaRespiratorio: '4',
      sofaCoagulacao: '3',
      sofaHepatico: '2',
      sofaCardiovascular: '4',
      sofaNeurologico: '3',
      sofaRenal: '4',
      sofaNote: 'Falência múltipla de órgãos. Paciente crítico.',
    },
    score: 20,
    createdAt: '2026-07-08T06:00:00Z',
    createdBy: 'Dr. Oliveira',
  },
  {
    id: 'form-009',
    mpiId: 'MPI-003',
    formType: 'glasgow',
    data: { glasgowOcular: '1', glasgowVerbal: '1', glasgowMotora: '2', glasgowNote: 'Paciente grave, TCE.' },
    score: 4,
    createdAt: '2026-07-08T06:15:00Z',
    createdBy: 'Dr. Oliveira',
  },
  {
    id: 'form-010',
    mpiId: 'MPI-003',
    formType: 'rass',
    data: { rassScore: '-4', rassNote: 'Sedação profunda — protocolo TCE.' },
    score: -4,
    createdAt: '2026-07-08T06:30:00Z',
    createdBy: 'Dr. Oliveira',
  },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Computa o total SOFA a partir dos dados do formulário (0–24) */
export function computeSOFATotal(data: Record<string, any>): number {
  let total = 0;
  for (const system of SOFA_SYSTEMS) {
    const val = parseInt(data[system.key], 10);
    if (!isNaN(val) && val >= 0 && val <= 4) {
      total += val;
    }
  }
  return total;
}

/** Computa o total Glasgow a partir dos dados do formulário (3–15) */
export function computeGlasgowTotal(data: Record<string, any>): number {
  let total = 0;
  for (const comp of GLASGOW_COMPONENTS) {
    const val = parseInt(data[comp.key], 10);
    if (!isNaN(val) && val >= 1 && val <= comp.maxScore) {
      total += val;
    }
  }
  return total;
}

/** Retorna a cor CSS do score baseado no tipo de formulário e valor */
export function getScoreColor(formType: FormType, value: number): string {
  switch (formType) {
    case 'sofa':
      if (value >= 13) return 'var(--clinical-severity-critical-on-surface)';
      if (value >= 10) return 'var(--clinical-severity-urgent-on-surface)';
      if (value >= 7) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';

    case 'glasgow':
      if (value <= 8) return 'var(--clinical-severity-critical-on-surface)';
      if (value <= 12) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';

    case 'rass':
      if (value <= -4) return 'var(--clinical-severity-critical-on-surface)';
      if (value >= 3) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';

    case 'bps_nrs':
      if (value >= 9) return 'var(--clinical-severity-critical-on-surface)';
      if (value >= 6) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';

    case 'cam_icu':
      return value === 1
        ? 'var(--clinical-severity-watch-on-surface)'
        : 'var(--clinical-severity-normal-on-surface)';

    case 'lpp':
      // Braden inverted: lower = higher risk. 6-23.
      if (value <= 9) return 'var(--clinical-severity-critical-on-surface)';
      if (value <= 12) return 'var(--clinical-severity-urgent-on-surface)';
      if (value <= 14) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';

    default:
      return 'var(--semantic-text-primary)';
  }
}

/** Retorna label PT-BR de interpretação clínica do score */
export function getScoreInterpretation(formType: FormType, value: number): string {
  switch (formType) {
    case 'sofa':
      if (value >= 13) return 'Falência Múltipla de Órgãos';
      if (value >= 10) return 'Disfunção Grave';
      if (value >= 7) return 'Disfunção Moderada';
      if (value >= 2) return 'Disfunção Leve';
      return 'Sem Disfunção';

    case 'glasgow':
      if (value <= 8) return 'Coma / Grave';
      if (value <= 12) return 'Moderado';
      return 'Leve / Normal';

    case 'rass':
      if (value <= -4) return 'Sedação Profunda';
      if (value <= -1) return 'Sedação Leve';
      if (value === 0) return 'Alerta e Calmo';
      if (value >= 3) return 'Agitação';
      return 'Inquieto';

    case 'bps_nrs':
      if (value >= 9) return 'Dor Intensa';
      if (value >= 6) return 'Dor Moderada';
      if (value >= 3) return 'Dor Leve';
      return 'Sem Dor';

    case 'cam_icu':
      return value === 1 ? 'Delirium Positivo' : 'Delirium Negativo';

    case 'lpp':
      // Braden interpretation: lower = higher risk
      if (value <= 9) return 'Risco Muito Alto';
      if (value <= 12) return 'Risco Alto';
      if (value <= 14) return 'Risco Moderado';
      if (value <= 18) return 'Risco Baixo';
      return 'Sem Risco';

    default:
      return '';
  }
}
