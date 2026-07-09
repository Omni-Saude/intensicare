// ─── Clinical Notes Types ───────────────────────────────────────────────────
// D3 — Tipos e dados mock para evoluções clínicas (diário médico).
// Contrato: evolucoes-openapi.yaml

import {
  LogIn,
  Calendar,
  LogOut,
  HeartOff,
  AlertCircle,
  type LucideIcon,
} from 'lucide-react';

// ─── Core Types ─────────────────────────────────────────────────────────────

export type EvolutionType =
  | 'admissao'
  | 'diaria'
  | 'alta'
  | 'obito'
  | 'intercorrencia';

export interface Evolucao {
  id: string;
  mpi_id: string;
  type: EvolutionType;
  content: string; // markdown, max 50000 chars
  created_at: string;
  created_by: string;
  updated_at?: string;
}

export interface EvolucaoCreate {
  type: EvolutionType;
  content: string;
}

// ─── Patient Type ───────────────────────────────────────────────────────────

export interface NotePatient {
  mpiId: string;
  name: string;
  bed: string;
}

// ─── Labels, Icons & Colors ─────────────────────────────────────────────────

export const TYPE_LABELS: Record<EvolutionType, string> = {
  admissao: 'Admissão',
  diaria: 'Diária',
  alta: 'Alta',
  obito: 'Óbito',
  intercorrencia: 'Intercorrência',
};

export const TYPE_ICONS: Record<EvolutionType, LucideIcon> = {
  admissao: LogIn,
  diaria: Calendar,
  alta: LogOut,
  obito: HeartOff,
  intercorrencia: AlertCircle,
};

/** Cores para cada tipo de evolução (CSS custom property tokens ou fallback hex). */
export const TYPE_COLORS: Record<
  EvolutionType,
  { signal: string; fill: string; onFill: string }
> = {
  admissao: {
    signal: 'var(--clinical-type-admissao, #2563EB)',
    fill: 'var(--clinical-type-admissao-fill, #DBEAFE)',
    onFill: 'var(--clinical-type-admissao-on-fill, #1E40AF)',
  },
  diaria: {
    signal: 'var(--clinical-type-diaria, #16A34A)',
    fill: 'var(--clinical-type-diaria-fill, #DCFCE7)',
    onFill: 'var(--clinical-type-diaria-on-fill, #166534)',
  },
  alta: {
    signal: 'var(--clinical-type-alta, #0D9488)',
    fill: 'var(--clinical-type-alta-fill, #CCFBF1)',
    onFill: 'var(--clinical-type-alta-on-fill, #115E59)',
  },
  obito: {
    signal: 'var(--clinical-type-obito, #374151)',
    fill: 'var(--clinical-type-obito-fill, #F3F4F6)',
    onFill: 'var(--clinical-type-obito-on-fill, #1F2937)',
  },
  intercorrencia: {
    signal: 'var(--clinical-type-intercorrencia, #D97706)',
    fill: 'var(--clinical-type-intercorrencia-fill, #FEF3C7)',
    onFill: 'var(--clinical-type-intercorrencia-on-fill, #92400E)',
  },
};

// ─── Helpers ────────────────────────────────────────────────────────────────

export function formatNoteType(type: EvolutionType): string {
  return TYPE_LABELS[type] ?? type;
}

export function getTypeColor(type: EvolutionType): (typeof TYPE_COLORS)[EvolutionType] {
  return TYPE_COLORS[type] ?? TYPE_COLORS.intercorrencia;
}

export function getTypeIcon(type: EvolutionType): LucideIcon {
  return TYPE_ICONS[type] ?? AlertCircle;
}

// ─── Mock Patients ──────────────────────────────────────────────────────────

export const MOCK_PATIENTS: NotePatient[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpiId: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpiId: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];

// ─── Mock Notes (8 evoluções para 3 pacientes) ──────────────────────────────

export const MOCK_NOTES: Evolucao[] = [
  // ───── MPI-001: João Silva ─────
  {
    id: 'evol-001',
    mpi_id: 'MPI-001',
    type: 'admissao',
    content: `# Admissão — João Silva

**Data:** 07/07/2026 08:30
**Procedência:** Emergência
**Diagnóstico de Admissão:** Pneumonia comunitária grave + Insuficiência respiratória aguda

## Sinais Vitais
- **PA:** 100/60 mmHg
- **FC:** 112 bpm
- **FR:** 28 irpm
- **SpO₂:** 88% (ar ambiente)
- **Tax:** 38,7 °C

## Exame Físico
Paciente em regular estado geral, taquipneico, uso de musculatura acessória. MV diminuído em base direita, com estertores crepitantes. Ausculta cardíaca: ritmo regular em 2T, sem sopros. Abdome flácido, indolor. Extremidades aquecidas, perfusão lentificada (TEC 4s).

## Conduta
- Oxigenoterapia por máscara de Venturi 50%
- Coleta de hemoculturas (2 pares) + cultura de escarro
- Iniciar Ceftriaxona 2g IV + Claritromicina 500 mg IV
- Solicitar gasometria arterial + RX tórax
- Avaliar necessidade de VNI`,
    created_at: '2026-07-07T08:30:00Z',
    created_by: 'Dr. Ricardo Mendes',
  },
  {
    id: 'evol-002',
    mpi_id: 'MPI-001',
    type: 'diaria',
    content: `# Evolução Diária — João Silva (D2 de internação)

**Data:** 08/07/2026 09:15

## Sinais Vitais
- **PA:** 115/70 mmHg
- **FC:** 96 bpm
- **FR:** 22 irpm
- **SpO₂:** 95% (Venturi 40%)
- **Tax:** 37,2 °C

## Evolução Clínica
Paciente apresenta **melhora clínica** significativa. Redução da taquipneia e da febre. Mantém oxigenoterapia com menor FiO₂. Diurese presente, balanço hídrico positivo (+800 mL/24h).

## Exames
- **Gasometria:** pH 7,38 / pCO₂ 38 / pO₂ 88 / HCO₃ 24 / SatO₂ 96%
- **RX Tórax:** infiltrado em base direita, sem derrame pleural
- **Hemoculturas:** pendentes (48h)

## Conduta
- Manter Ceftriaxona + Claritromicina conforme prescrição
- Desmame progressivo da oxigenoterapia
- Fisioterapia respiratória motora 2x/dia
- Reavaliar culturas em 24h`,
    created_at: '2026-07-08T09:15:00Z',
    created_by: 'Dr. Ricardo Mendes',
  },
  {
    id: 'evol-003',
    mpi_id: 'MPI-001',
    type: 'diaria',
    content: `# Evolução Diária — João Silva (D3)

**Data:** 09/07/2026 10:00

Paciente evolui com **boa resposta** ao tratamento. Afebril há 24h, em ar ambiente com SpO₂ 94%. Sinais vitais estáveis. Hemoculturas negativas até o momento.

**Conduta:** Manter antibioticoterapia. Alta programada para amanhã se mantiver estabilidade.`,
    created_at: '2026-07-09T10:00:00Z',
    created_by: 'Dra. Fernanda Lima',
  },
  {
    id: 'evol-004',
    mpi_id: 'MPI-001',
    type: 'alta',
    content: `# Alta Hospitalar — João Silva

**Data:** 10/07/2026 11:00
**Dias de internação:** 4 dias

## Resumo da Internação
Paciente internado por **pneumonia comunitária grave**, evoluindo com boa resposta à antibioticoterapia com Ceftriaxona + Claritromicina. Hemoculturas negativas. Desmame completo de O₂ no D3.

## Orientações de Alta
- Retornar para reavaliação ambulatorial em 7 dias
- Manter hidratação oral adequada
- Retomar atividades progressivamente

## Medicações de Alta
- Azitromicina 500 mg VO 1x/dia por mais 3 dias`,
    created_at: '2026-07-10T11:00:00Z',
    created_by: 'Dr. Ricardo Mendes',
  },
  // ───── MPI-002: Maria Oliveira ─────
  {
    id: 'evol-005',
    mpi_id: 'MPI-002',
    type: 'admissao',
    content: `# Admissão — Maria Oliveira

**Data:** 06/07/2026 22:00
**Procedência:** Centro Cirúrgico
**Diagnóstico:** Pós-operatório de laparotomia exploradora por abdome agudo perfurativo

## Sinais Vitais
- **PA:** 90/55 mmHg (em uso de noradrenalina 0,3 mcg/kg/min)
- **FC:** 118 bpm
- **FR:** 24 irpm (VM em PSV)
- **SpO₂:** 96%
- **Tax:** 36,1 °C

## Exame Físico
Paciente sedada (RASS -4), em ventilação mecânica. Abdome com curativo cirúrgico limpo e seco, dreno de Blake em flanco direito com débito sero-hemático (80 mL/12h). Extremidades frias, com livedo reticular.

## Conduta
- Manter noradrenalina para PAM ≥ 65 mmHg
- Iniciar Piperacilina-Tazobactam 4,5g IV 6/6h
- Controle laboratorial seriado (lactato, gasometria)
- Sondagem vesical de demora — controle de diurese horária`,
    created_at: '2026-07-06T22:00:00Z',
    created_by: 'Dra. Fernanda Lima',
  },
  {
    id: 'evol-006',
    mpi_id: 'MPI-002',
    type: 'intercorrencia',
    content: `# Intercorrência — Maria Oliveira (D1 PO)

**Data:** 07/07/2026 14:30
**Evento:** Piora hemodinâmica súbita

Paciente apresentou **hipotensão refratária** com necessidade de aumento progressivo de noradrenalina (até 0,8 mcg/kg/min). Lactato elevado (4,8 mmol/L). Realizada expansão volêmica com cristaloide (1000 mL) e iniciada vasopressina como segundo vasopressor.

**Hipótese:** Sepse de foco abdominal vs. choque hemorrágico.

**Conduta Imediata:**
- Coleta de novas hemoculturas + procalcitonina
- TC de abdome com contraste (urgente)
- Reserva de concentrado de hemácias (2 UI)
- Acionar cirurgião de sobreaviso`,
    created_at: '2026-07-07T14:30:00Z',
    created_by: 'Dra. Fernanda Lima',
  },
  {
    id: 'evol-007',
    mpi_id: 'MPI-002',
    type: 'obito',
    content: `# Óbito — Maria Oliveira

**Data:** 08/07/2026 03:45
**Causa mortis:** Choque séptico refratário de foco abdominal

Paciente evoluiu com **piora progressiva** do choque séptico, refratário a múltiplos vasopressores (noradrenalina 1,2 mcg/kg/min + vasopressina 0,04 UI/min). Acidose metabólica grave (pH 6,98 / lactato 12 mmol/L). Parada cardiorrespiratória em AESP às 03:12. Manobras de RCP por 30 minutos sem sucesso. Óbito constatado às 03:45.

Familiares comunicados pela Dra. Fernanda Lima.`,
    created_at: '2026-07-08T03:45:00Z',
    created_by: 'Dra. Fernanda Lima',
  },
  // ───── MPI-003: Carlos Santos ─────
  {
    id: 'evol-008',
    mpi_id: 'MPI-003',
    type: 'diaria',
    content: `# Evolução Diária — Carlos Santos (D5)

**Data:** 07/07/2026 08:00

## Sinais Vitais
- **PA:** 130/80 mmHg
- **FC:** 88 bpm
- **FR:** 18 irpm
- **SpO₂:** 97% (ar ambiente)
- **Tax:** 36,5 °C

## Exame Físico
Paciente acordado, orientado, sem queixas álgicas. MV presente bilateralmente sem ruídos adventícios. ACV: RCR 2T sem sopros. Abdome flácido, indolor, RHA+. MMII sem edema, pulsos presentes.

## Conduta
- Paciente estável, mantendo cuidados de enfermagem
- Aguardando vaga de enfermaria para desocupar leito de UTI
- Revisão de exames laboratoriais pela manhã`,
    created_at: '2026-07-07T08:00:00Z',
    created_by: 'Dr. Ricardo Mendes',
  },
];
