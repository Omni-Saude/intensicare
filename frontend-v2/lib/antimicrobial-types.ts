// ─── Antimicrobial Stewardship Types ────────────────────────────────────────
// M4 — Tipos e dados mock para avaliação de stewardship antimicrobiano.
// Contrato OpenAPI pendente; estrutura provisória.

export type CriterionCategory =
  | 'duracao'
  | 'espectro'
  | 'dose'
  | 'cvc'
  | 'candidemia'
  | 'culturas'
  | 'cap_covid';

export interface AntimicrobialCriterion {
  id: string;
  name: string;
  category: CriterionCategory;
  description: string;
  met: boolean;
}

export type StewardshipSeverity = 'VERMELHO' | 'AMARELO' | 'NEUTRO';

export interface AntimicrobialAssessment {
  patientMpiId: string;
  criteria: AntimicrobialCriterion[];
  score: number;
  severity: StewardshipSeverity;
  recommendation: string;
  assessedAt: string;
  assessedBy: string;
}

// ─── Default Criteria (12 critérios) ────────────────────────────────────────

export const DEFAULT_CRITERIA: AntimicrobialCriterion[] = [
  {
    id: 'crit-001',
    name: 'Duração > 7 dias',
    category: 'duracao',
    description:
      'Tratamento antimicrobiano superior a 7 dias sem reavaliação documentada',
    met: false,
  },
  {
    id: 'crit-002',
    name: 'Espectro muito amplo',
    category: 'espectro',
    description:
      'Cobertura empírica excessiva sem descalonamento guiado por culturas',
    met: false,
  },
  {
    id: 'crit-003',
    name: 'Dose inadequada',
    category: 'dose',
    description:
      'Dose não ajustada para função renal e/ou hepática do paciente',
    met: false,
  },
  {
    id: 'crit-004',
    name: 'CVC > 7 dias',
    category: 'cvc',
    description:
      'Cateter venoso central mantido além de 7 dias sem indicação documentada',
    met: false,
  },
  {
    id: 'crit-005',
    name: 'Candidemia sem descalonamento',
    category: 'candidemia',
    description:
      'Candidemia documentada sem adequação terapêutica após antifungigrama',
    met: false,
  },
  {
    id: 'crit-006',
    name: 'Culturas pendentes > 72h',
    category: 'culturas',
    description:
      'Antibioticoterapia mantida sem resultado de culturas por mais de 72 horas',
    met: false,
  },
  {
    id: 'crit-007',
    name: 'CAP sem critério de gravidade',
    category: 'cap_covid',
    description:
      'Pneumonia adquirida na comunidade com antibioticoterapia excessiva sem critérios de gravidade',
    met: false,
  },
  {
    id: 'crit-008',
    name: 'Dupla cobertura gram-negativo',
    category: 'espectro',
    description:
      'Dois agentes com mesmo espectro gram-negativo sem indicação clínica',
    met: false,
  },
  {
    id: 'crit-009',
    name: 'Vancomicina > 72h sem MRSA',
    category: 'espectro',
    description:
      'Vancomicina mantida por mais de 72 horas sem confirmação microbiológica de MRSA',
    met: false,
  },
  {
    id: 'crit-010',
    name: 'Duração cirúrgica > 24h',
    category: 'duracao',
    description:
      'Profilaxia cirúrgica estendida além do período preconizado de 24 horas',
    met: false,
  },
  {
    id: 'crit-011',
    name: 'Sem nível sérico (vanco/aminog)',
    category: 'dose',
    description:
      'Drogas com janela terapêutica estreita (vancomicina, aminoglicosídeos) sem monitorização de nível sérico',
    met: false,
  },
  {
    id: 'crit-012',
    name: 'CVC sem curativo documentado',
    category: 'cvc',
    description:
      'Cateter venoso central sem registro de curativo ou troca no período preconizado',
    met: false,
  },
];

// ─── Scoring Helpers ────────────────────────────────────────────────────────

/** Conta quantos critérios estão marcados como "met" (não conformidades). */
export function computeScore(criteria: AntimicrobialCriterion[]): number {
  return criteria.filter((c) => c.met).length;
}

/**
 * Classifica a severidade baseada no número de critérios não atendidos:
 * 0-3 → NEUTRO (prescrição adequada)
 * 4-7 → AMARELO (revisão recomendada)
 * 8-12 → VERMELHO (intervenção imediata)
 */
export function computeSeverity(score: number): StewardshipSeverity {
  if (score <= 3) return 'NEUTRO';
  if (score <= 7) return 'AMARELO';
  return 'VERMELHO';
}

/** Gera recomendação dinâmica baseada na severidade e score. */
export function getRecommendation(
  severity: StewardshipSeverity,
  score: number,
): string {
  switch (severity) {
    case 'NEUTRO':
      return 'Prescrição antimicrobiana dentro dos parâmetros adequados. Manter monitorização de rotina e reavaliar em 72h.';
    case 'AMARELO':
      return `Foram identificados ${score} critério(s) que requerem atenção. Recomenda-se revisão estruturada e descalonamento nas próximas 24-48h.`;
    case 'VERMELHO':
      return `INTERVENÇÃO IMEDIATA necessária — ${score} critérios críticos identificados. Acionar equipe de stewardship e reavaliar todos os antimicrobianos em até 12h.`;
  }
}

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

// ─── Category Labels (PT-BR) ────────────────────────────────────────────────

export const CATEGORY_LABELS: Record<CriterionCategory, string> = {
  duracao: 'Duração',
  espectro: 'Espectro',
  dose: 'Dose / Monitorização',
  cvc: 'Cateter Venoso Central',
  candidemia: 'Candidemia',
  culturas: 'Culturas',
  cap_covid: 'CAP / COVID',
};
