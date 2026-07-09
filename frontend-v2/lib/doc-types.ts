// ─── Documentation Types ────────────────────────────────────────────────────
// D4 — Tipos e dados mock para registros de documentação clínica.
// Contrato: documentacao-openapi.yaml

// ─── Enums ───────────────────────────────────────────────────────────────────

export type GlosaStatus =
  | 'pendente'
  | 'em_analise'
  | 'glosado'
  | 'liberado'
  | 'recorrido';

export type DocType =
  | 'sumario_alta'
  | 'prescricao'
  | 'relatorio_medico'
  | 'conta_hospitalar';

// ─── Interfaces ──────────────────────────────────────────────────────────────

export interface Documentacao {
  id: string;
  mpi_id: string;
  type: DocType;
  content: string;
  glosa_status: GlosaStatus;
  glosa_motivo?: string;
  glosa_valor?: number;
  created_at: string;
  updated_at?: string;
}

export interface DocumentacaoCreate {
  mpi_id: string;
  type: DocType;
  content: string;
  glosa_status?: GlosaStatus;
  glosa_motivo?: string;
  glosa_valor?: number;
}

// ─── Labels (PT-BR) ──────────────────────────────────────────────────────────

export const GLOSA_STATUS_LABELS: Record<GlosaStatus, string> = {
  pendente: 'Pendente',
  em_analise: 'Em Análise',
  glosado: 'Glosado',
  liberado: 'Liberado',
  recorrido: 'Recorrido',
};

export const DOC_TYPE_LABELS: Record<DocType, string> = {
  sumario_alta: 'Sumário de Alta',
  prescricao: 'Prescrição',
  relatorio_medico: 'Relatório Médico',
  conta_hospitalar: 'Conta Hospitalar',
};

// ─── Color Tokens ────────────────────────────────────────────────────────────

export interface GlosaColorSet {
  bg: string;
  text: string;
  border: string;
  icon: string;
}

export const GLOSA_STATUS_COLORS: Record<GlosaStatus, GlosaColorSet> = {
  pendente: {
    bg: 'var(--feedback-warning-bg-dark)',
    text: 'var(--feedback-warning-text-dark)',
    border: 'var(--feedback-warning-border-dark)',
    icon: 'var(--feedback-warning-icon-dark)',
  },
  em_analise: {
    bg: 'var(--feedback-info-bg-dark)',
    text: 'var(--feedback-info-text-dark)',
    border: 'var(--feedback-info-border-dark)',
    icon: 'var(--feedback-info-icon-dark)',
  },
  glosado: {
    bg: 'var(--feedback-error-bg-dark)',
    text: 'var(--feedback-error-text-dark)',
    border: 'var(--feedback-error-border-dark)',
    icon: 'var(--feedback-error-icon-dark)',
  },
  liberado: {
    bg: 'var(--feedback-success-bg-dark)',
    text: 'var(--feedback-success-text-dark)',
    border: 'var(--feedback-success-border-dark)',
    icon: 'var(--feedback-success-icon-dark)',
  },
  recorrido: {
    bg: 'var(--semantic-surface-overlay)',
    text: 'var(--semantic-text-secondary)',
    border: 'var(--semantic-border-default)',
    icon: 'var(--semantic-text-secondary)',
  },
};

// ─── Mock Patients ──────────────────────────────────────────────────────────

export interface MockPatient {
  mpiId: string;
  name: string;
  bed: string;
}

export const MOCK_PATIENTS: MockPatient[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpiId: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpiId: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];

// ─── Mock Documents (8 docs, 3 patients) ────────────────────────────────────

export const MOCK_DOCS: Documentacao[] = [
  {
    id: 'doc-001',
    mpi_id: 'MPI-001',
    type: 'sumario_alta',
    content:
      'Paciente João Silva, 67 anos, internado por pneumonia adquirida na comunidade. Apresentou boa evolução clínica com antibioticoterapia guiada por culturas. Alta hospitalar programada para 15/07/2026 com orientações de acompanhamento ambulatorial e retorno em 7 dias para reavaliação.',
    glosa_status: 'liberado',
    created_at: '2026-07-01T08:00:00Z',
    updated_at: '2026-07-02T14:30:00Z',
  },
  {
    id: 'doc-002',
    mpi_id: 'MPI-001',
    type: 'prescricao',
    content:
      'Ceftriaxona 2g EV 12/12h — Dia 5 de tratamento. Vancomicina 1g EV 12/12h — ajustado para função renal (CrCl 45 mL/min). Enoxaparina 40mg SC 1x/dia. Omeprazol 40mg EV 1x/dia. Dipirona 1g EV 6/6h se dor.',
    glosa_status: 'glosado',
    glosa_motivo: 'Vancomicina sem nível sérico documentado após 72h de uso',
    glosa_valor: 1250.75,
    created_at: '2026-07-02T10:00:00Z',
  },
  {
    id: 'doc-003',
    mpi_id: 'MPI-001',
    type: 'relatorio_medico',
    content:
      'Relatório de evolução diária — 04/07/2026. Paciente mantém estabilidade hemodinâmica, afebril há 48h. Gasometria arterial dentro da normalidade. Em desmame ventilatório, extubação programada para amanhã. Culturas de 02/07 negativas até o momento.',
    glosa_status: 'pendente',
    created_at: '2026-07-04T16:00:00Z',
  },
  {
    id: 'doc-004',
    mpi_id: 'MPI-002',
    type: 'conta_hospitalar',
    content:
      'Conta hospitalar referente ao período de 01/07 a 05/07/2026. Diárias de UTI: 5 x R$ 2.800,00. Medicamentos: R$ 4.520,30. Exames laboratoriais: R$ 1.890,00. Exames de imagem: R$ 3.200,00. Taxas e materiais: R$ 1.150,50. Total: R$ 24.760,80.',
    glosa_status: 'em_analise',
    glosa_valor: 4520.3,
    created_at: '2026-07-05T18:00:00Z',
  },
  {
    id: 'doc-005',
    mpi_id: 'MPI-002',
    type: 'prescricao',
    content:
      'Meropenem 1g EV 8/8h — Dia 3. Metronidazol 500mg EV 8/8h. Fluidoterapia: Ringer Lactato 80 mL/h. Noradrenalina 0,1 mcg/kg/min — em desmame. Insulina regular SC conforme HGT.',
    glosa_status: 'pendente',
    created_at: '2026-07-06T09:00:00Z',
  },
  {
    id: 'doc-006',
    mpi_id: 'MPI-002',
    type: 'sumario_alta',
    content:
      'Paciente Maria Oliveira, 54 anos, internada por sepse de foco abdominal. Realizada laparotomia exploradora em 03/07. Evolução favorável, antibioticoterapia direcionada conforme culturas. Alta prevista para 10/07/2026.',
    glosa_status: 'recorrido',
    glosa_motivo: 'Revisão de glosa anterior: justificativa de prorrogação aceita',
    glosa_valor: 890.5,
    created_at: '2026-07-04T20:00:00Z',
    updated_at: '2026-07-07T11:00:00Z',
  },
  {
    id: 'doc-007',
    mpi_id: 'MPI-003',
    type: 'relatorio_medico',
    content:
      'Relatório de admissão — 03/07/2026. Paciente Carlos Santos, 45 anos, vítima de politrauma automobilístico. Admitido em UTI para monitorização neurológica e suporte ventilatório. TC crânio sem alterações agudas. Fratura de fêmur D — programada fixação cirúrgica.',
    glosa_status: 'liberado',
    created_at: '2026-07-03T22:00:00Z',
    updated_at: '2026-07-04T08:00:00Z',
  },
  {
    id: 'doc-008',
    mpi_id: 'MPI-003',
    type: 'conta_hospitalar',
    content:
      'Conta hospitalar parcial — 03/07 a 07/07/2026. Diárias de UTI: 4 x R$ 2.800,00 = R$ 11.200,00. Procedimentos cirúrgicos: R$ 8.500,00. Hemocomponentes: R$ 2.340,00. Medicamentos: R$ 6.780,45. Total parcial: R$ 28.820,45.',
    glosa_status: 'pendente',
    created_at: '2026-07-07T14:00:00Z',
  },
];

// ─── Helper Functions ───────────────────────────────────────────────────────

/** Retorna o label PT-BR para um status de glosa. */
export function formatGlosaStatus(status: GlosaStatus): string {
  return GLOSA_STATUS_LABELS[status];
}

/** Retorna o conjunto de cores (tokens CSS) para um status de glosa. */
export function getGlosaColor(status: GlosaStatus): GlosaColorSet {
  return GLOSA_STATUS_COLORS[status];
}

/** Formata um valor numérico como moeda brasileira (R$). */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}
