// ─── Efficiency & Stewardship Types ─────────────────────────────────────────
// D9 — Tipos e dados mock para avaliação de eficiência clínica.
// Transfusão (12 critérios), Contenção Mecânica, Fragilidade, Tempo de UTI.
// Contrato alinhado com eficiencia-openapi.yaml.

// ─── Tipos Principais ────────────────────────────────────────────────────────

/** Critério individual de transfusão — 12 critérios de adequação */
export interface TransfusionCriterion {
  code: string;
  description: string;
  met: boolean;
  detail?: string;
}

/** Status de contenção mecânica */
export type RestraintStatus =
  | 'none'
  | 'planned'
  | 'active'
  | 'weaning'
  | 'removed'
  | 'contraindicated';

/** Escala de fragilidade suportada */
export type FrailtyScale = 'CFS' | 'mFI' | 'FRAIL';

/** Avaliação completa de eficiência clínica */
export interface EfficiencyAssessment {
  id: string;
  mpi_id: string;
  patient_name?: string;
  /** 12 critérios de adequação transfusional */
  transfusion_criteria: TransfusionCriterion[];
  /** Status atual da contenção mecânica */
  restraint_status: RestraintStatus;
  /** Detalhes da contenção (indicação, data de instalação, última revisão) */
  restraint_details?: string;
  /** Score de fragilidade (CFS: 1-9, mFI: 0-1, FRAIL: 0-5) */
  frailty_score?: number;
  /** Escala utilizada para avaliação de fragilidade */
  frailty_scale?: FrailtyScale;
  /** Dias de permanência na UTI (Length of Stay) */
  icu_los_days: number;
  /** Benchmark esperado de LOS para o diagnóstico (opcional) */
  icu_los_benchmark?: number;
  /** Data/hora de admissão na UTI */
  icu_admission_at?: string;
  /** Notas clínicas adicionais */
  notes?: string;
  /** Timestamp ISO 8601 da avaliação */
  assessed_at: string;
  /** Profissional que realizou a avaliação */
  assessed_by?: string;
}

// ─── Labels PT-BR ────────────────────────────────────────────────────────────

/** Labels em PT-BR para status de contenção mecânica */
export const RESTRAINT_LABELS: Record<RestraintStatus, string> = {
  none: 'Nenhuma',
  planned: 'Planejada',
  active: 'Ativa',
  weaning: 'Desmame',
  removed: 'Removida',
  contraindicated: 'Contraindicada',
};

/** Labels em PT-BR para escalas de fragilidade */
export const FRAILTY_SCALE_LABELS: Record<FrailtyScale, string> = {
  CFS: 'Clinical Frailty Scale (CFS)',
  mFI: 'Modified Frailty Index (mFI)',
  FRAIL: 'FRAIL Scale',
};

// ─── Cores para Contenção ───────────────────────────────────────────────────

export const RESTRAINT_COLORS: Record<RestraintStatus, string> = {
  none: 'var(--clinical-severity-normal-signal)',
  planned: 'var(--clinical-severity-watch-signal)',
  active: 'var(--clinical-severity-critical-signal)',
  weaning: 'var(--clinical-severity-watch-signal)',
  removed: 'var(--clinical-severity-normal-signal)',
  contraindicated: 'var(--semantic-text-secondary)',
};

export const RESTRAINT_BG_COLORS: Record<RestraintStatus, string> = {
  none: 'var(--clinical-severity-normal-wash)',
  planned: 'var(--clinical-severity-watch-wash)',
  active: 'var(--clinical-severity-critical-wash)',
  weaning: 'var(--clinical-severity-watch-wash)',
  removed: 'var(--clinical-severity-normal-wash)',
  contraindicated: 'var(--semantic-surface-overlay)',
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Formata dias de LOS com 1 casa decimal e sufixo "dias" */
export function formatLOS(days: number): string {
  return `${days.toFixed(1)} dias`;
}

/** Retorna a cor de sinal para um status de contenção */
export function getRestraintColor(status: RestraintStatus): string {
  return RESTRAINT_COLORS[status] ?? 'var(--semantic-text-secondary)';
}

/** Retorna a cor de fundo para um status de contenção */
export function getRestraintBgColor(status: RestraintStatus): string {
  return RESTRAINT_BG_COLORS[status] ?? 'var(--semantic-surface-overlay)';
}

/** Retorna label completo para escala de fragilidade + score */
export function getFrailtyLabel(
  score?: number,
  scale?: FrailtyScale,
): string {
  if (score === undefined || score === null) return 'Não avaliada';
  const scaleLabel = scale ? FRAILTY_SCALE_LABELS[scale] : 'Fragilidade';
  return `${scaleLabel}: ${score}`;
}

/** Interpretação qualitativa do score CFS */
export function getCFSInterpretation(score: number): string {
  if (score <= 3) return 'Robusto — baixo risco de desfechos adversos';
  if (score <= 4) return 'Vulnerável — risco moderado';
  if (score <= 6) return 'Frágil — risco elevado de complicações';
  if (score <= 8) return 'Muito frágil — alto risco de mortalidade';
  return 'Terminal — expectativa de vida limitada (< 6 meses)';
}

// ─── 12 Critérios de Transfusão (default) ───────────────────────────────────

export const DEFAULT_TRANSFUSION_CRITERIA: TransfusionCriterion[] = [
  {
    code: 'TF-001',
    description: 'Hb pré-transfusional documentada',
    met: false,
    detail: 'Hemoglobina deve ser registrada antes de cada transfusão',
  },
  {
    code: 'TF-002',
    description: 'Hb ≥ 7 g/dL (gatilho restritivo)',
    met: false,
    detail: 'Transfusão com Hb ≥ 7 g/dL requer justificativa clínica',
  },
  {
    code: 'TF-003',
    description: 'Transfusão em 1 unidade (single-unit)',
    met: false,
    detail: 'Estratégia single-unit reduz exposição e eventos adversos',
  },
  {
    code: 'TF-004',
    description: 'Reavaliação clínica pós-transfusional',
    met: false,
    detail: 'Registro de evolução clínica pós-transfusão em até 6h',
  },
  {
    code: 'TF-005',
    description: 'Hb pós-transfusional documentada',
    met: false,
    detail: 'Controle laboratorial pós-transfusional em até 24h',
  },
  {
    code: 'TF-006',
    description: 'Ausência de reação transfusional',
    met: false,
    detail: 'Monitorização de sinais vitais durante e após transfusão',
  },
  {
    code: 'TF-007',
    description: 'Indicação clínica documentada',
    met: false,
    detail: 'Registro do motivo clínico da transfusão no prontuário',
  },
  {
    code: 'TF-008',
    description: 'Termo de consentimento assinado',
    met: false,
    detail: 'Consentimento informado documentado para transfusão',
  },
  {
    code: 'TF-009',
    description: 'Identificação correta do paciente',
    met: false,
    detail: 'Dupla checagem de identificação antes da administração',
  },
  {
    code: 'TF-010',
    description: 'Compatibilidade ABO/Rh confirmada',
    met: false,
    detail: 'Prova cruzada ou confirmação de compatibilidade registrada',
  },
  {
    code: 'TF-011',
    description: 'Temperatura de armazenamento adequada',
    met: false,
    detail: 'Registro da cadeia de frio até o momento da administração',
  },
  {
    code: 'TF-012',
    description: 'Tempo de infusão ≤ 4 horas',
    met: false,
    detail: 'Cada unidade deve ser infundida em até 4 horas',
  },
];

// ─── Mock: Avaliação atual ───────────────────────────────────────────────────

export const MOCK_ASSESSMENT: EfficiencyAssessment = {
  id: 'eff-001',
  mpi_id: 'MPI-001',
  patient_name: 'João Silva',
  transfusion_criteria: [
    { code: 'TF-001', description: 'Hb pré-transfusional documentada', met: true, detail: 'Hb 6.8 g/dL registrada às 08:30' },
    { code: 'TF-002', description: 'Hb ≥ 7 g/dL (gatilho restritivo)', met: false, detail: 'Gatilho restritivo respeitado — Hb 6.8 < 7.0' },
    { code: 'TF-003', description: 'Transfusão em 1 unidade (single-unit)', met: true, detail: '1 CHAD transfundido' },
    { code: 'TF-004', description: 'Reavaliação clínica pós-transfusional', met: true, detail: 'Reavaliado às 14:15 — sem intercorrências' },
    { code: 'TF-005', description: 'Hb pós-transfusional documentada', met: false, detail: 'Hb pós-transfusional pendente — coletar em 24h' },
    { code: 'TF-006', description: 'Ausência de reação transfusional', met: false, detail: 'Sem sinais de reação — monitorização ok' },
    { code: 'TF-007', description: 'Indicação clínica documentada', met: true, detail: 'Anemia sintomática com instabilidade hemodinâmica' },
    { code: 'TF-008', description: 'Termo de consentimento assinado', met: false, detail: 'Pendente — familiar será contactado' },
    { code: 'TF-009', description: 'Identificação correta do paciente', met: false, detail: 'Dupla checagem realizada conforme protocolo' },
    { code: 'TF-010', description: 'Compatibilidade ABO/Rh confirmada', met: true, detail: 'A+ compatível — prova cruzada negativa' },
    { code: 'TF-011', description: 'Temperatura de armazenamento adequada', met: true, detail: 'Cadeia de frio mantida — registro ok' },
    { code: 'TF-012', description: 'Tempo de infusão ≤ 4 horas', met: false, detail: 'Início 10:00 — término 13:45 (3h45min)' },
  ],
  restraint_status: 'weaning',
  restraint_details:
    'Contenção mecânica de membros superiores iniciada em 05/07/2026 por agitação psicomotora (RASS +3). Desmame iniciado em 07/07/2026 após ajuste de sedação. Última revisão: 08/07/2026 08:00.',
  frailty_score: 4,
  frailty_scale: 'CFS',
  icu_los_days: 3.5,
  icu_los_benchmark: 4.0,
  icu_admission_at: '2026-07-04T14:30:00Z',
  notes:
    'Paciente com evolução favorável. Desmame de contenção em andamento. Transfusão com boa tolerância. Previsão de alta da UTI em 24-48h.',
  assessed_at: new Date().toISOString(),
  assessed_by: 'Dr(a). Ana Costa',
};

// ─── Mock: Pacientes para seletor ───────────────────────────────────────────

export interface MockEfficiencyPatient {
  mpiId: string;
  name: string;
  bed: string;
}

export const MOCK_PATIENTS: MockEfficiencyPatient[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpiId: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpiId: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];
