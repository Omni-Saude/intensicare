// ─── Registry Types & Mocks ──────────────────────────────────────────────────
// Domain model: Empresa → Estabelecimento → Setor
// Used by app/admin/registry/page.tsx for CRUD management.
// Aligned with cadastros-ui-openapi.yaml contract.

// ─── Core Types ───────────────────────────────────────────────────────────────

export interface Empresa {
  id: string;
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Estabelecimento {
  id: string;
  empresa_id: string;
  cnes: string;
  nome: string;
  endereco: string;
  ativo: boolean;
}

export type SetorTipo =
  | 'uti'
  | 'semi_intensiva'
  | 'enfermaria'
  | 'pronto_socorro'
  | 'centro_cirurgico'
  | 'ambulatorio'
  | 'diagnostico'
  | 'outro';

export interface Setor {
  id: string;
  estabelecimento_id: string;
  nome: string;
  sigla: string;
  tipo: SetorTipo;
  leitos_operacionais: number;
  ativo: boolean;
}

// ─── Create Types (without server-generated fields) ───────────────────────────

export interface EmpresaCreate {
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
}

export interface EstabelecimentoCreate {
  empresa_id: string;
  cnes: string;
  nome: string;
  endereco: string;
}

export interface SetorCreate {
  estabelecimento_id: string;
  nome: string;
  sigla: string;
  tipo: SetorTipo;
  leitos_operacionais: number;
}

// ─── Labels ───────────────────────────────────────────────────────────────────

export const SETOR_TIPO_LABELS: Record<SetorTipo, string> = {
  uti: 'UTI',
  semi_intensiva: 'Semi-Intensiva',
  enfermaria: 'Enfermaria',
  pronto_socorro: 'Pronto Socorro',
  centro_cirurgico: 'Centro Cirúrgico',
  ambulatorio: 'Ambulatório',
  diagnostico: 'Diagnóstico',
  outro: 'Outro',
};

// ─── Mock Data ────────────────────────────────────────────────────────────────

export const MOCK_EMPRESAS: Empresa[] = [
  {
    id: 'emp-001',
    cnpj: '12.345.678/0001-90',
    razao_social: 'Hospital São Lucas S.A.',
    nome_fantasia: 'Hospital São Lucas',
    ativo: true,
    created_at: '2025-01-15T10:00:00Z',
    updated_at: '2026-06-20T14:30:00Z',
  },
  {
    id: 'emp-002',
    cnpj: '98.765.432/0001-21',
    razao_social: 'Clínica Vida & Saúde Ltda.',
    nome_fantasia: 'Clínica Vida & Saúde',
    ativo: true,
    created_at: '2025-03-10T08:00:00Z',
    updated_at: '2026-05-12T11:15:00Z',
  },
];

export const MOCK_ESTABELECIMENTOS: Estabelecimento[] = [
  {
    id: 'est-001',
    empresa_id: 'emp-001',
    cnes: '1234567',
    nome: 'Matriz — Unidade Central',
    endereco: 'Av. Paulista, 1000 — São Paulo/SP',
    ativo: true,
  },
  {
    id: 'est-002',
    empresa_id: 'emp-001',
    cnes: '7654321',
    nome: 'Filial Norte',
    endereco: 'Rua das Oliveiras, 500 — São Paulo/SP',
    ativo: true,
  },
  {
    id: 'est-003',
    empresa_id: 'emp-002',
    cnes: '3456789',
    nome: 'Unidade Centro',
    endereco: 'Rua da Consolação, 250 — São Paulo/SP',
    ativo: true,
  },
];

export const MOCK_SETORES: Setor[] = [
  {
    id: 'set-001',
    estabelecimento_id: 'est-001',
    nome: 'UTI Geral Adulto',
    sigla: 'UTI-GA',
    tipo: 'uti',
    leitos_operacionais: 20,
    ativo: true,
  },
  {
    id: 'set-002',
    estabelecimento_id: 'est-001',
    nome: 'UTI Coronariana',
    sigla: 'UTI-CO',
    tipo: 'uti',
    leitos_operacionais: 10,
    ativo: true,
  },
  {
    id: 'set-003',
    estabelecimento_id: 'est-001',
    nome: 'Semi-Intensiva Adulto',
    sigla: 'SIA',
    tipo: 'semi_intensiva',
    leitos_operacionais: 15,
    ativo: true,
  },
  {
    id: 'set-004',
    estabelecimento_id: 'est-002',
    nome: 'Enfermaria Clínica',
    sigla: 'ENF-C',
    tipo: 'enfermaria',
    leitos_operacionais: 30,
    ativo: true,
  },
  {
    id: 'set-005',
    estabelecimento_id: 'est-002',
    nome: 'Pronto Socorro',
    sigla: 'PS',
    tipo: 'pronto_socorro',
    leitos_operacionais: 12,
    ativo: false,
  },
  {
    id: 'set-006',
    estabelecimento_id: 'est-003',
    nome: 'Centro Cirúrgico',
    sigla: 'CC',
    tipo: 'centro_cirurgico',
    leitos_operacionais: 8,
    ativo: true,
  },
];

// ─── Tree Type ────────────────────────────────────────────────────────────────

export interface OrgTreeNode {
  empresa: Empresa;
  estabelecimentos: EstabTreeNode[];
}

export interface EstabTreeNode {
  estabelecimento: Estabelecimento;
  setores: Setor[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Formats a raw CNPJ string into the XX.XXX.XXX/XXXX-XX pattern. */
export function formatCNPJ(cnpj: string): string {
  // Remove non-digits
  const digits = cnpj.replace(/\D/g, '');
  if (digits.length !== 14) return cnpj; // return as-is if malformed
  return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12, 14)}`;
}

/** Returns the PT-BR label for a SetorTipo. */
export function getTipoLabel(tipo: SetorTipo): string {
  return SETOR_TIPO_LABELS[tipo];
}

/** Builds a hierarchical organization tree from flat mock data. */
export function buildOrgTree(): OrgTreeNode[] {
  return MOCK_EMPRESAS.map((empresa) => ({
    empresa,
    estabelecimentos: MOCK_ESTABELECIMENTOS.filter(
      (e) => e.empresa_id === empresa.id,
    ).map((estabelecimento) => ({
      estabelecimento,
      setores: MOCK_SETORES.filter(
        (s) => s.estabelecimento_id === estabelecimento.id,
      ),
    })),
  }));
}

/** Generates a simple unique ID for mock CRUD operations (deterministic). */
let _idCounter = 0;
export function generateId(prefix: string): string {
  _idCounter++;
  return `${prefix}-${Date.now().toString(36)}-${_idCounter.toString(36)}`;
}
