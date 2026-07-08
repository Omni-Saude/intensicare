// ─── Pathway Types ─────────────────────────────────────────────────────────
// Trilhas-Engine domain types + mock data + helpers
// PT-BR labels throughout

import type { TimelineEvent } from '@/components/ClinicalTimeline';
import type { Criterion } from '@/components/CriteriaChecklist';

// ─── Core Types ────────────────────────────────────────────────────────────

export interface PathwayState {
  id: string;
  name: string;
  order: number;
  description: string;
  is_terminal: boolean;
}

export interface PathwayCriteria {
  id: string;
  name: string;
  category: string;
  description: string;
  unit?: string;
  normal_range?: string;
  alert_threshold?: string;
  met: boolean;
  value?: string;
  evaluated_at?: string;
}

export interface Pathway {
  id: string;
  name: string;
  description: string;
  slug: string;
  active: boolean;
  states: PathwayState[];
  criteria: PathwayCriteria[];
}

export interface PatientPathway {
  id: string;
  mpi_id: string;
  pathway: Pathway;
  current_state: PathwayState;
  criteria: PathwayCriteria[];
  status: 'active' | 'completed' | 'archived';
  severity: 'normal' | 'watch' | 'urgent' | 'critical';
  enrolled_at: string;
  enrolled_by: string;
  completed_at?: string;
  updated_at: string;
}

export interface StateHistoryEntry {
  from_state: string;
  to_state: string;
  changed_at: string;
  reason: string;
}

export interface PathwayProgress {
  patient_pathway_id: string;
  mpi_id: string;
  pathway_name: string;
  current_state: string;
  criteria_summary: {
    total: number;
    met: number;
    not_met: number;
    pending: number;
  };
  criteria: PathwayCriteria[];
  state_history: StateHistoryEntry[];
  trend: 'improving' | 'stable' | 'worsening' | 'none';
  recommendation: string;
}

// ─── Status / Severity Helpers (PT-BR) ────────────────────────────────────

export function getStatusLabel(status: PatientPathway['status']): string {
  const map: Record<PatientPathway['status'], string> = {
    active: 'Ativo',
    completed: 'Concluído',
    archived: 'Arquivado',
  };
  return map[status];
}

export function getSeverityLabel(severity: PatientPathway['severity']): string {
  const map: Record<PatientPathway['severity'], string> = {
    normal: 'Normal',
    watch: 'Observação',
    urgent: 'Urgente',
    critical: 'Crítico',
  };
  return map[severity];
}

export function getStateLabel(state: PathwayState): string {
  return state.name;
}

export function computeProgress(
  criteria: PathwayCriteria[],
): { total: number; met: number; notMet: number; pending: number; percent: number } {
  const total = criteria.length;
  const met = criteria.filter((c) => c.met).length;
  const notMet = criteria.filter((c) => !c.met).length;
  const pending = 0; // all criteria have a boolean met state in mock data
  const percent = total > 0 ? Math.round((met / total) * 100) : 0;
  return { total, met, notMet: notMet, pending, percent };
}

// ─── Convert state history → ClinicalTimeline events ──────────────────────

export function stateHistoryToTimeline(
  history: StateHistoryEntry[],
  currentState: string,
): TimelineEvent[] {
  return history.map((entry) => {
    const isCurrent = entry.to_state === currentState;
    return {
      id: `state-${entry.changed_at}`,
      status: isCurrent ? ('in-progress' as const) : ('completed' as const),
      label: `${entry.from_state} → ${entry.to_state}`,
      description: entry.reason,
      timestamp: entry.changed_at,
    };
  });
}

// ─── Convert PathwayCriteria → Criterion[] for CriteriaChecklist ──────────

export function pathwayCriteriaToChecklistItems(
  criteria: PathwayCriteria[],
): Criterion[] {
  return criteria.map((c) => ({
    id: c.id,
    label: c.name,
    description: c.description,
    category: c.category,
    met: c.met,
    value: c.value,
    threshold: c.alert_threshold,
  }));
}

// ─── Mock Pathways ─────────────────────────────────────────────────────────

export const MOCK_PATHWAYS: Pathway[] = [
  // 1. Sepse
  {
    id: 'pw-sepse',
    name: 'Protocolo de Sepse',
    description:
      'Detecção precoce e tratamento da sepse conforme Surviving Sepsis Campaign. Bundle de 1h com antibiótico, lactato, hemoculturas e fluidos.',
    slug: 'sepse',
    active: true,
    states: [
      {
        id: 'screening',
        name: 'Triagem',
        order: 0,
        description: 'Paciente monitorado para sinais de sepse',
        is_terminal: false,
      },
      {
        id: 'identified',
        name: 'Identificada',
        order: 1,
        description: 'Sepse identificada — iniciar bundle 1h',
        is_terminal: false,
      },
      {
        id: 'bundle',
        name: 'Bundle 1h',
        order: 2,
        description: 'Execução do bundle de 1 hora',
        is_terminal: false,
      },
      {
        id: 'completed',
        name: 'Concluído',
        order: 3,
        description: 'Bundle concluído com sucesso',
        is_terminal: true,
      },
    ],
    criteria: [
      {
        id: 'sepse-lactato',
        name: 'Lactato sérico',
        category: 'Laboratorial',
        description: 'Dosagem de lactato na primeira hora',
        unit: 'mmol/L',
        normal_range: '< 2.0',
        alert_threshold: '> 4.0',
        met: true,
        value: '3.2',
        evaluated_at: '2026-07-07T08:30:00Z',
      },
      {
        id: 'sepse-hemocultura',
        name: 'Hemoculturas',
        category: 'Microbiologia',
        description: 'Coleta de 2 pares de hemoculturas antes do antibiótico',
        met: true,
        evaluated_at: '2026-07-07T08:45:00Z',
      },
      {
        id: 'sepse-antibiotico',
        name: 'Antibiótico IV',
        category: 'Medicação',
        description: 'Antibioticoterapia endovenosa de amplo espectro iniciada',
        met: true,
        evaluated_at: '2026-07-07T09:00:00Z',
      },
      {
        id: 'sepse-fluidos',
        name: 'Fluidos EV',
        category: 'Intervenção',
        description: 'Ressuscitação volêmica com 30 mL/kg de cristaloide',
        met: false,
        value: '1000 mL',
        alert_threshold: '30 mL/kg',
        evaluated_at: '2026-07-07T09:15:00Z',
      },
      {
        id: 'sepse-vasopressor',
        name: 'Vasopressor',
        category: 'Intervenção',
        description: 'Iniciar vasopressor se PAM < 65 mmHg após fluidos',
        met: false,
        evaluated_at: '2026-07-07T09:20:00Z',
      },
    ],
  },

  // 2. Ventilação Mecânica
  {
    id: 'pw-ventilacao',
    name: 'Ventilação Mecânica Protetora',
    description:
      'Estratégia de ventilação protetora com volume corrente 6 mL/kg, PEEP otimizada e avaliação diária de desmame.',
    slug: 'ventilacao-mecanica',
    active: true,
    states: [
      {
        id: 'intubado',
        name: 'Intubado',
        order: 0,
        description: 'Paciente em ventilação mecânica',
        is_terminal: false,
      },
      {
        id: 'protetora',
        name: 'Ventilação Protetora',
        order: 1,
        description: 'Parâmetros protetores ajustados (VC ≤ 6 mL/kg)',
        is_terminal: false,
      },
      {
        id: 'desmame',
        name: 'Desmame',
        order: 2,
        description: 'Teste de respiração espontânea',
        is_terminal: false,
      },
      {
        id: 'extubado',
        name: 'Extubado',
        order: 3,
        description: 'Paciente extubado com sucesso',
        is_terminal: true,
      },
    ],
    criteria: [
      {
        id: 'vent-vc',
        name: 'Volume Corrente ≤ 6 mL/kg',
        category: 'Parâmetros',
        description: 'Volume corrente ajustado para peso predito',
        unit: 'mL/kg',
        normal_range: '≤ 6',
        alert_threshold: '> 8',
        met: true,
        value: '5.8',
        evaluated_at: '2026-07-07T10:00:00Z',
      },
      {
        id: 'vent-peep',
        name: 'PEEP Otimizada',
        category: 'Parâmetros',
        description: 'PEEP ajustada conforme FiO₂ (tabela ARDSNet)',
        unit: 'cmH₂O',
        normal_range: '≥ 5',
        met: true,
        value: '10',
        evaluated_at: '2026-07-07T10:00:00Z',
      },
      {
        id: 'vent-plateau',
        name: 'Pressão de Platô ≤ 30',
        category: 'Parâmetros',
        description: 'Pressão de platô mantida abaixo de 30 cmH₂O',
        unit: 'cmH₂O',
        normal_range: '< 30',
        alert_threshold: '> 30',
        met: true,
        value: '26',
        evaluated_at: '2026-07-07T10:00:00Z',
      },
      {
        id: 'vent-cabceira',
        name: 'Cabeceira Elevada 30-45°',
        category: 'Posicionamento',
        description: 'Cabeceira elevada para prevenção de PAV',
        met: false,
        evaluated_at: '2026-07-07T10:15:00Z',
      },
    ],
  },

  // 3. Profilaxia TEV
  {
    id: 'pw-tev',
    name: 'Profilaxia de TEV',
    description:
      'Profilaxia de tromboembolismo venoso com avaliação de risco, anticoagulação farmacológica ou compressão mecânica.',
    slug: 'profilaxia-tev',
    active: true,
    states: [
      {
        id: 'avaliado',
        name: 'Avaliado',
        order: 0,
        description: 'Risco de TEV avaliado (Padua Score)',
        is_terminal: false,
      },
      {
        id: 'prescrito',
        name: 'Prescrito',
        order: 1,
        description: 'Profilaxia prescrita conforme risco',
        is_terminal: false,
      },
      {
        id: 'administrado',
        name: 'Administrado',
        order: 2,
        description: 'Medicação ou dispositivo aplicado',
        is_terminal: true,
      },
    ],
    criteria: [
      {
        id: 'tev-score',
        name: 'Padua Score',
        category: 'Avaliação',
        description: 'Escore de risco de TEV (Padua ≥ 4 indica profilaxia)',
        met: true,
        value: '6',
        alert_threshold: '≥ 4',
        evaluated_at: '2026-07-07T07:00:00Z',
      },
      {
        id: 'tev-prescricao',
        name: 'Prescrição de Profilaxia',
        category: 'Prescrição',
        description: 'Enoxaparina 40 mg SC ou HNF 5000 UI SC 8/8h',
        met: true,
        evaluated_at: '2026-07-07T07:15:00Z',
      },
      {
        id: 'tev-administracao',
        name: 'Administração Registrada',
        category: 'Administração',
        description: 'Registro de administração no prontuário eletrônico',
        met: false,
        evaluated_at: '2026-07-07T09:00:00Z',
      },
    ],
  },

  // 4. Nutrição Enteral
  {
    id: 'pw-nutricao',
    name: 'Nutrição Enteral Precoce',
    description:
      'Início de nutrição enteral nas primeiras 24-48h, avaliação de tolerância e progressão para meta calórica.',
    slug: 'nutricao-enteral',
    active: true,
    states: [
      {
        id: 'avaliacao',
        name: 'Avaliação Nutricional',
        order: 0,
        description: 'Triagem nutricional e indicação de NE',
        is_terminal: false,
      },
      {
        id: 'sonda',
        name: 'Sonda Posicionada',
        order: 1,
        description: 'Sonda nasoenteral posicionada e confirmada',
        is_terminal: false,
      },
      {
        id: 'iniciada',
        name: 'Dieta Iniciada',
        order: 2,
        description: 'Dieta enteral iniciada em infusão contínua',
        is_terminal: false,
      },
      {
        id: 'meta',
        name: 'Meta Calórica',
        order: 3,
        description: 'Meta calórica atingida (> 80% do estimado)',
        is_terminal: true,
      },
    ],
    criteria: [
      {
        id: 'nut-avaliacao',
        name: 'Triagem Nutricional (NRS-2002)',
        category: 'Avaliação',
        description: 'Triagem nutricional realizada em até 24h da admissão',
        met: true,
        value: '5',
        alert_threshold: '≥ 3',
        evaluated_at: '2026-07-06T18:00:00Z',
      },
      {
        id: 'nut-sonda',
        name: 'Confirmação de Posição da Sonda',
        category: 'Procedimento',
        description: 'Raio-X ou teste de pH confirmatório',
        met: true,
        evaluated_at: '2026-07-07T06:00:00Z',
      },
      {
        id: 'nut-inicio',
        name: 'Início em 48h',
        category: 'Prazo',
        description: 'Nutrição enteral iniciada em até 48h da admissão',
        met: true,
        value: '36h',
        alert_threshold: '> 48h',
        evaluated_at: '2026-07-07T08:00:00Z',
      },
      {
        id: 'nut-residuo',
        name: 'Resíduo Gástrico < 500 mL',
        category: 'Tolerância',
        description: 'Medição de resíduo gástrico a cada 6h',
        unit: 'mL',
        normal_range: '< 500',
        met: true,
        value: '120',
        evaluated_at: '2026-07-07T08:00:00Z',
      },
      {
        id: 'nut-progressao',
        name: 'Progressão da Dieta',
        category: 'Nutrição',
        description: 'Aumento progressivo até meta calórica em 72h',
        met: false,
        value: '55%',
        alert_threshold: '> 80%',
        evaluated_at: '2026-07-07T08:30:00Z',
      },
    ],
  },
];

// ─── Mock Patients ─────────────────────────────────────────────────────────

export interface PathwayPatient {
  id: string;
  mpi_id: string;
  name: string;
  bed: string;
  age: number;
  admission_diagnosis: string;
  pathway_count: number;
  has_overdue: boolean;
}

export const MOCK_PATIENTS: PathwayPatient[] = [
  {
    id: 'pat-001',
    mpi_id: 'MPI-00042',
    name: 'Carlos Alberto Silva',
    bed: 'UTI-1 Leito 3',
    age: 68,
    admission_diagnosis: 'Pneumonia adquirida na comunidade + choque séptico',
    pathway_count: 2,
    has_overdue: false,
  },
  {
    id: 'pat-002',
    mpi_id: 'MPI-00158',
    name: 'Maria Helena Costa',
    bed: 'UTI-1 Leito 7',
    age: 72,
    admission_diagnosis: 'Pós-operatório de revascularização miocárdica',
    pathway_count: 2,
    has_overdue: true,
  },
  {
    id: 'pat-003',
    mpi_id: 'MPI-00231',
    name: 'José Roberto Nunes',
    bed: 'UTI-2 Leito 2',
    age: 45,
    admission_diagnosis: 'TCE grave + ventilação mecânica',
    pathway_count: 1,
    has_overdue: false,
  },
  {
    id: 'pat-004',
    mpi_id: 'MPI-00305',
    name: 'Ana Beatriz Ferreira',
    bed: 'UTI-2 Leito 5',
    age: 59,
    admission_diagnosis: 'Pancreatite aguda grave',
    pathway_count: 0,
    has_overdue: false,
  },
];

// ─── Mock Patient-Pathway Assignments ──────────────────────────────────────

export const MOCK_PATIENT_PATHWAYS: PatientPathway[] = [
  // Carlos — Sepse (active) + Profilaxia TEV (active)
  {
    id: 'pp-001',
    mpi_id: 'MPI-00042',
    pathway: MOCK_PATHWAYS[0]!, // Sepse
    current_state: MOCK_PATHWAYS[0]!.states[2]!, // Bundle 1h
    criteria: MOCK_PATHWAYS[0]!.criteria,
    status: 'active',
    severity: 'urgent',
    enrolled_at: '2026-07-06T14:00:00Z',
    enrolled_by: 'Dr. Ricardo Mendes',
    updated_at: '2026-07-07T09:20:00Z',
  },
  {
    id: 'pp-002',
    mpi_id: 'MPI-00042',
    pathway: MOCK_PATHWAYS[2]!, // Profilaxia TEV
    current_state: MOCK_PATHWAYS[2]!.states[1]!, // Prescrito
    criteria: MOCK_PATHWAYS[2]!.criteria,
    status: 'active',
    severity: 'normal',
    enrolled_at: '2026-07-06T07:00:00Z',
    enrolled_by: 'Dra. Juliana Costa',
    updated_at: '2026-07-07T09:00:00Z',
  },
  // Maria Helena — Ventilação (active) + Profilaxia TEV (overdue)
  {
    id: 'pp-003',
    mpi_id: 'MPI-00158',
    pathway: MOCK_PATHWAYS[1]!, // Ventilação Mecânica
    current_state: MOCK_PATHWAYS[1]!.states[1]!, // Ventilação Protetora
    criteria: MOCK_PATHWAYS[1]!.criteria,
    status: 'active',
    severity: 'watch',
    enrolled_at: '2026-07-05T20:00:00Z',
    enrolled_by: 'Dr. Ricardo Mendes',
    updated_at: '2026-07-07T10:15:00Z',
  },
  {
    id: 'pp-004',
    mpi_id: 'MPI-00158',
    pathway: MOCK_PATHWAYS[2]!, // Profilaxia TEV
    current_state: MOCK_PATHWAYS[2]!.states[0]!, // Avaliado (stuck — overdue)
    criteria: MOCK_PATHWAYS[2]!.criteria.map((c) => ({
      ...c,
      met: c.id === 'tev-score' ? c.met : false,
    })),
    status: 'active',
    severity: 'critical',
    enrolled_at: '2026-07-05T07:00:00Z',
    enrolled_by: 'Dra. Juliana Costa',
    updated_at: '2026-07-07T08:00:00Z',
  },
  // José — Ventilação (active)
  {
    id: 'pp-005',
    mpi_id: 'MPI-00231',
    pathway: MOCK_PATHWAYS[1]!, // Ventilação Mecânica
    current_state: MOCK_PATHWAYS[1]!.states[2]!, // Desmame
    criteria: MOCK_PATHWAYS[1]!.criteria.map((c) => ({
      ...c,
      met: true,
    })),
    status: 'active',
    severity: 'normal',
    enrolled_at: '2026-07-04T10:00:00Z',
    enrolled_by: 'Dr. Ricardo Mendes',
    updated_at: '2026-07-07T10:00:00Z',
  },
];

// ─── Mock Pathway Progress (state history + recommendation) ───────────────

export const MOCK_PROGRESS: Record<string, PathwayProgress> = {
  'pp-001': {
    patient_pathway_id: 'pp-001',
    mpi_id: 'MPI-00042',
    pathway_name: 'Protocolo de Sepse',
    current_state: 'Bundle 1h',
    criteria_summary: {
      total: 5,
      met: 3,
      not_met: 2,
      pending: 0,
    },
    criteria: MOCK_PATHWAYS[0]!.criteria,
    state_history: [
      {
        from_state: 'Início',
        to_state: 'Triagem',
        changed_at: '2026-07-06T14:00:00Z',
        reason: 'Paciente admitido com suspeita de sepse — escore SOFA ≥ 2',
      },
      {
        from_state: 'Triagem',
        to_state: 'Identificada',
        changed_at: '2026-07-06T14:30:00Z',
        reason:
          'Lactato 4.1 mmol/L, hipotensão refratária a volume — sepse identificada',
      },
      {
        from_state: 'Identificada',
        to_state: 'Bundle 1h',
        changed_at: '2026-07-06T14:45:00Z',
        reason:
          'Início do bundle 1h: antibiótico, hemoculturas e fluidos em andamento',
      },
    ],
    trend: 'improving',
    recommendation:
      'Priorizar ressuscitação volêmica e iniciar vasopressor. Reavaliar lactato em 2-4h após conclusão do bundle.',
  },
  'pp-002': {
    patient_pathway_id: 'pp-002',
    mpi_id: 'MPI-00042',
    pathway_name: 'Profilaxia de TEV',
    current_state: 'Prescrito',
    criteria_summary: {
      total: 3,
      met: 2,
      not_met: 1,
      pending: 0,
    },
    criteria: MOCK_PATHWAYS[2]!.criteria,
    state_history: [
      {
        from_state: 'Início',
        to_state: 'Avaliado',
        changed_at: '2026-07-06T07:00:00Z',
        reason: 'Admissão na UTI — Padua Score = 6, alto risco',
      },
      {
        from_state: 'Avaliado',
        to_state: 'Prescrito',
        changed_at: '2026-07-06T07:15:00Z',
        reason: 'Enoxaparina 40 mg SC prescrita',
      },
    ],
    trend: 'stable',
    recommendation:
      'Registrar administração da enoxaparina no prontuário eletrônico. Próxima dose em 24h.',
  },
  'pp-003': {
    patient_pathway_id: 'pp-003',
    mpi_id: 'MPI-00158',
    pathway_name: 'Ventilação Mecânica Protetora',
    current_state: 'Ventilação Protetora',
    criteria_summary: {
      total: 4,
      met: 3,
      not_met: 1,
      pending: 0,
    },
    criteria: MOCK_PATHWAYS[1]!.criteria,
    state_history: [
      {
        from_state: 'Início',
        to_state: 'Intubado',
        changed_at: '2026-07-05T20:00:00Z',
        reason: 'Pós-operatório — IOT em centro cirúrgico',
      },
      {
        from_state: 'Intubado',
        to_state: 'Ventilação Protetora',
        changed_at: '2026-07-05T22:00:00Z',
        reason: 'Parâmetros ajustados: VC 5.8 mL/kg, PEEP 10 cmH₂O',
      },
    ],
    trend: 'stable',
    recommendation:
      'Elevar cabeceira para 30-45°. Iniciar avaliação diária de desmame com teste de respiração espontânea.',
  },
  'pp-004': {
    patient_pathway_id: 'pp-004',
    mpi_id: 'MPI-00158',
    pathway_name: 'Profilaxia de TEV',
    current_state: 'Avaliado',
    criteria_summary: {
      total: 3,
      met: 1,
      not_met: 2,
      pending: 0,
    },
    criteria: MOCK_PATHWAYS[2]!.criteria.map((c) => ({
      ...c,
      met: c.id === 'tev-score',
    })),
    state_history: [
      {
        from_state: 'Início',
        to_state: 'Avaliado',
        changed_at: '2026-07-05T07:00:00Z',
        reason: 'Admissão na UTI — Padua Score = 6, alto risco',
      },
    ],
    trend: 'worsening',
    recommendation:
      '⚠️ ATENÇÃO: Profilaxia de TEV com mais de 48h sem prescrição. Prescrever enoxaparina imediatamente.',
  },
  'pp-005': {
    patient_pathway_id: 'pp-005',
    mpi_id: 'MPI-00231',
    pathway_name: 'Ventilação Mecânica Protetora',
    current_state: 'Desmame',
    criteria_summary: {
      total: 4,
      met: 4,
      not_met: 0,
      pending: 0,
    },
    criteria: MOCK_PATHWAYS[1]!.criteria.map((c) => ({
      ...c,
      met: true,
    })),
    state_history: [
      {
        from_state: 'Início',
        to_state: 'Intubado',
        changed_at: '2026-07-04T10:00:00Z',
        reason: 'TCE grave — IOT na emergência',
      },
      {
        from_state: 'Intubado',
        to_state: 'Ventilação Protetora',
        changed_at: '2026-07-04T12:00:00Z',
        reason: 'Parâmetros protetores ajustados',
      },
      {
        from_state: 'Ventilação Protetora',
        to_state: 'Desmame',
        changed_at: '2026-07-06T09:00:00Z',
        reason:
          'Paciente estável, teste de respiração espontânea bem-sucedido — desmame em andamento',
      },
    ],
    trend: 'improving',
    recommendation:
      'Evolução favorável no desmame. Considerar extubação nas próximas 24h se mantiver padrão respiratório adequado.',
  },
};
