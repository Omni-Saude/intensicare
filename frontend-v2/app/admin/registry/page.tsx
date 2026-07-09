'use client';

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  Building2,
  Hospital,
  DoorOpen,
  Plus,
  RefreshCw,
  Pencil,
  Power,
  PowerOff,
  AlertTriangle,
  Hash,
  MapPin,
  BedDouble,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import DrawerBuilder from '@/components/DrawerBuilder';
import {
  fetchEmpresas,
  createEmpresa,
  updateEmpresa,
  fetchEstabelecimentos,
  createEstabelecimento,
  updateEstabelecimento,
  fetchSetores,
  createSetor,
  updateSetor,
} from '@/lib/api';
import {
  SETOR_TIPO_LABELS,
  formatCNPJ,
  type Empresa,
  type EmpresaCreate,
  type Estabelecimento,
  type EstabelecimentoCreate,
  type Setor,
  type SetorCreate,
  type SetorTipo,
} from '@/lib/registry-types';

// ─── Tab Types ────────────────────────────────────────────────────────────────

type TabKey = 'empresas' | 'estabelecimentos' | 'setores';

const TABS: { key: TabKey; label: string }[] = [
  { key: 'empresas', label: 'Empresas' },
  { key: 'estabelecimentos', label: 'Estabelecimentos' },
  { key: 'setores', label: 'Setores' },
];

// ─── Badge de Ativo/Inativo ───────────────────────────────────────────────────

function AtivoBadge({ ativo }: { ativo: boolean }) {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: ativo
          ? 'var(--clinical-severity-normal-wash)'
          : 'var(--clinical-severity-critical-wash)',
        color: ativo
          ? 'var(--clinical-severity-normal-on-surface)'
          : 'var(--clinical-severity-critical-on-surface)',
      }}
    >
      {ativo ? 'Ativo' : 'Inativo'}
    </span>
  );
}

// ─── Tipo Badge para Setores ──────────────────────────────────────────────────

function TipoBadge({ tipo }: { tipo: SetorTipo }) {
  const colorMap: Record<SetorTipo, { bg: string; fg: string }> = {
    uti: {
      bg: 'var(--clinical-severity-critical-wash)',
      fg: 'var(--clinical-severity-critical-on-surface)',
    },
    semi_intensiva: {
      bg: 'var(--clinical-severity-urgent-wash)',
      fg: 'var(--clinical-severity-urgent-on-surface)',
    },
    enfermaria: {
      bg: 'var(--clinical-severity-watch-wash)',
      fg: 'var(--clinical-severity-watch-on-surface)',
    },
    pronto_socorro: {
      bg: 'var(--clinical-severity-critical-wash)',
      fg: 'var(--clinical-severity-critical-on-surface)',
    },
    centro_cirurgico: {
      bg: 'var(--color-brand-primary-wash)',
      fg: 'var(--color-brand-primary-on-surface)',
    },
    ambulatorio: {
      bg: 'var(--clinical-severity-normal-wash)',
      fg: 'var(--clinical-severity-normal-on-surface)',
    },
    diagnostico: {
      bg: 'var(--color-brand-secondary-wash)',
      fg: 'var(--color-brand-secondary-on-surface)',
    },
    outro: {
      bg: 'var(--semantic-surface-canvas)',
      fg: 'var(--semantic-text-secondary)',
    },
  };

  const colors = colorMap[tipo] ?? colorMap.outro;

  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      style={{ backgroundColor: colors.bg, color: colors.fg }}
    >
      {SETOR_TIPO_LABELS[tipo]}
    </span>
  );
}

// ─── Skeleton Table ───────────────────────────────────────────────────────────

function SkeletonTable({ cols }: { cols: number }) {
  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        backgroundColor: 'var(--semantic-surface-raised)',
        borderColor: 'var(--semantic-border-default)',
      }}
    >
      <div
        className="grid gap-4 px-6 py-3 border-b text-xs font-semibold uppercase tracking-wider"
        style={{
          gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
          backgroundColor: 'var(--semantic-surface-canvas)',
          borderColor: 'var(--semantic-border-default)',
          color: 'var(--semantic-text-secondary)',
        }}
      >
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="h-3 rounded animate-pulse" style={{ backgroundColor: 'var(--semantic-surface-raised)' }} />
        ))}
      </div>
      {Array.from({ length: 5 }).map((_, row) => (
        <div
          key={row}
          className="grid gap-4 px-6 py-3 border-b"
          style={{
            gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
            borderColor: 'var(--semantic-border-default)',
          }}
        >
          {Array.from({ length: cols }).map((_, col) => (
            <div
              key={col}
              className="h-4 rounded animate-pulse"
              style={{
                backgroundColor: 'var(--semantic-surface-canvas)',
                width: col === 0 ? '60%' : '80%',
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function AdminRegistryPage() {
  // ── State ──────────────────────────────────────────────────────────────────

  const [activeTab, setActiveTab] = useState<TabKey>('empresas');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Data state (fetched from API)
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [estabelecimentos, setEstabelecimentos] = useState<Estabelecimento[]>([]);
  const [setores, setSetores] = useState<Setor[]>([]);

  // ── Fetch data from API ──────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchEmpresas(),
      fetchEstabelecimentos(),
      fetchSetores(),
    ])
      .then(([empData, estabData, setorData]) => {
        if (cancelled) return;
        setEmpresas(empData as Empresa[]);
        setEstabelecimentos(estabData as Estabelecimento[]);
        setSetores(setorData as Setor[]);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerEntity, setDrawerEntity] = useState<TabKey | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Form state
  const [empresaForm, setEmpresaForm] = useState<EmpresaCreate>({
    cnpj: '',
    razao_social: '',
    nome_fantasia: '',
  });
  const [estabelecimentoForm, setEstabelecimentoForm] = useState<EstabelecimentoCreate>({
    empresa_id: '',
    cnes: '',
    nome: '',
    endereco: '',
  });
  const [setorForm, setSetorForm] = useState<SetorCreate>({
    estabelecimento_id: '',
    nome: '',
    sigla: '',
    tipo: 'enfermaria',
    leitos_operacionais: 0,
  });

  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // ── Derived data ───────────────────────────────────────────────────────────

  const empresaMap = useMemo(() => {
    const map = new Map<string, Empresa>();
    empresas.forEach((e) => map.set(e.id, e));
    return map;
  }, [empresas]);

  const estabMap = useMemo(() => {
    const map = new Map<string, Estabelecimento>();
    estabelecimentos.forEach((e) => map.set(e.id, e));
    return map;
  }, [estabelecimentos]);

  // ── Handlers: Open Drawer ──────────────────────────────────────────────────

  const openCreate = useCallback((entity: TabKey) => {
    setEditingId(null);
    setDrawerEntity(entity);
    setFormError(null);
    // Reset form
    setEmpresaForm({ cnpj: '', razao_social: '', nome_fantasia: '' });
    setEstabelecimentoForm({ empresa_id: empresas[0]?.id ?? '', cnes: '', nome: '', endereco: '' });
    setSetorForm({ estabelecimento_id: estabelecimentos[0]?.id ?? '', nome: '', sigla: '', tipo: 'enfermaria', leitos_operacionais: 0 });
    setDrawerOpen(true);
  }, [empresas, estabelecimentos]);

  const openEdit = useCallback(
    (entity: TabKey, id: string) => {
      setEditingId(id);
      setDrawerEntity(entity);
      setFormError(null);

      if (entity === 'empresas') {
        const e = empresas.find((x) => x.id === id);
        if (e) setEmpresaForm({ cnpj: e.cnpj, razao_social: e.razao_social, nome_fantasia: e.nome_fantasia });
      } else if (entity === 'estabelecimentos') {
        const e = estabelecimentos.find((x) => x.id === id);
        if (e) setEstabelecimentoForm({ empresa_id: e.empresa_id, cnes: e.cnes, nome: e.nome, endereco: e.endereco });
      } else {
        const s = setores.find((x) => x.id === id);
        if (s) setSetorForm({ estabelecimento_id: s.estabelecimento_id, nome: s.nome, sigla: s.sigla, tipo: s.tipo, leitos_operacionais: s.leitos_operacionais });
      }

      setDrawerOpen(true);
    },
    [empresas, estabelecimentos, setores],
  );

  // ── Handlers: Submit ───────────────────────────────────────────────────────

  const handleSubmit = useCallback(async () => {
    setFormError(null);

    if (drawerEntity === 'empresas') {
      if (!empresaForm.cnpj || !empresaForm.razao_social || !empresaForm.nome_fantasia) {
        setFormError('Todos os campos são obrigatórios.');
        return;
      }
      setSubmitting(true);
      try {
        if (editingId) {
          const updated = await updateEmpresa(editingId, empresaForm) as Empresa;
          setEmpresas((prev) => prev.map((e) => (e.id === editingId ? updated : e)));
        } else {
          const nova = await createEmpresa(empresaForm) as Empresa;
          setEmpresas((prev) => [...prev, nova]);
        }
        setSubmitting(false);
        setDrawerOpen(false);
      } catch (err: unknown) {
        setFormError(err instanceof Error ? err.message : 'Erro ao salvar');
        setSubmitting(false);
      }
    } else if (drawerEntity === 'estabelecimentos') {
      if (!estabelecimentoForm.empresa_id || !estabelecimentoForm.cnes || !estabelecimentoForm.nome || !estabelecimentoForm.endereco) {
        setFormError('Todos os campos são obrigatórios.');
        return;
      }
      setSubmitting(true);
      try {
        if (editingId) {
          const updated = await updateEstabelecimento(editingId, estabelecimentoForm) as Estabelecimento;
          setEstabelecimentos((prev) => prev.map((e) => (e.id === editingId ? updated : e)));
        } else {
          const novo = await createEstabelecimento(estabelecimentoForm) as Estabelecimento;
          setEstabelecimentos((prev) => [...prev, novo]);
        }
        setSubmitting(false);
        setDrawerOpen(false);
      } catch (err: unknown) {
        setFormError(err instanceof Error ? err.message : 'Erro ao salvar');
        setSubmitting(false);
      }
    } else if (drawerEntity === 'setores') {
      if (!setorForm.estabelecimento_id || !setorForm.nome || !setorForm.sigla) {
        setFormError('Nome, sigla e estabelecimento são obrigatórios.');
        return;
      }
      setSubmitting(true);
      try {
        if (editingId) {
          const updated = await updateSetor(editingId, setorForm) as Setor;
          setSetores((prev) => prev.map((s) => (s.id === editingId ? updated : s)));
        } else {
          const novo = await createSetor(setorForm) as Setor;
          setSetores((prev) => [...prev, novo]);
        }
        setSubmitting(false);
        setDrawerOpen(false);
      } catch (err: unknown) {
        setFormError(err instanceof Error ? err.message : 'Erro ao salvar');
        setSubmitting(false);
      }
    }
  }, [drawerEntity, empresaForm, estabelecimentoForm, setorForm, editingId]);

  // ── Handlers: Toggle Ativo ─────────────────────────────────────────────────

  const toggleAtivo = useCallback(
    async (entity: TabKey, id: string) => {
      if (entity === 'empresas') {
        const emp = empresas.find((e) => e.id === id);
        if (!emp) return;
        const updated = { ...emp, ativo: !emp.ativo };
        // Optimistic update
        setEmpresas((prev) => prev.map((e) => (e.id === id ? updated : e)));
        try {
          await updateEmpresa(id, { ativo: updated.ativo } as unknown as Record<string, unknown>);
        } catch {
          // Revert on error
          setEmpresas((prev) => prev.map((e) => (e.id === id ? emp : e)));
        }
      } else if (entity === 'estabelecimentos') {
        const est = estabelecimentos.find((e) => e.id === id);
        if (!est) return;
        const updated = { ...est, ativo: !est.ativo };
        setEstabelecimentos((prev) => prev.map((e) => (e.id === id ? updated : e)));
        try {
          await updateEstabelecimento(id, { ativo: updated.ativo } as unknown as Record<string, unknown>);
        } catch {
          setEstabelecimentos((prev) => prev.map((e) => (e.id === id ? est : e)));
        }
      } else {
        const set = setores.find((s) => s.id === id);
        if (!set) return;
        const updated = { ...set, ativo: !set.ativo };
        setSetores((prev) => prev.map((s) => (s.id === id ? updated : s)));
        try {
          await updateSetor(id, { ativo: updated.ativo } as unknown as Record<string, unknown>);
        } catch {
          setSetores((prev) => prev.map((s) => (s.id === id ? set : s)));
        }
      }
    },
    [empresas, estabelecimentos, setores],
  );

  // ── Drawer Title ────────────────────────────────────────────────────────────

  const drawerTitle = useMemo(() => {
    const entityLabel =
      drawerEntity === 'empresas'
        ? 'Empresa'
        : drawerEntity === 'estabelecimentos'
          ? 'Estabelecimento'
          : 'Setor';
    return editingId ? `Editar ${entityLabel}` : `Nova ${entityLabel}`;
  }, [drawerEntity, editingId]);

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-6xl mx-auto">
          {/* ── Header ────────────────────────────────────────────────── */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: 'var(--color-brand-primary-fill)' }}
              >
                <Building2
                  className="w-5 h-5"
                  style={{ color: 'var(--color-brand-primary-on-fill)' }}
                  aria-hidden="true"
                />
              </div>
              <div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Cadastros
                </h1>
                <p
                  className="text-sm mt-0.5"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Gerenciamento de organizações, estabelecimentos e setores
                </p>
              </div>
            </div>
          </div>

          {/* ── Tabs ──────────────────────────────────────────────────── */}
          <div
            className="flex items-center border-b mb-6"
            style={{ borderColor: 'var(--semantic-border-default)' }}
            role="tablist"
            aria-label="Seções de cadastro"
          >
            {TABS.map((tab) => (
              <button
                key={tab.key}
                role="tab"
                aria-selected={activeTab === tab.key}
                onClick={() => setActiveTab(tab.key)}
                className="px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                style={{
                  color:
                    activeTab === tab.key
                      ? 'var(--color-brand-primary-on-surface)'
                      : 'var(--semantic-text-secondary)',
                  borderColor:
                    activeTab === tab.key
                      ? 'var(--color-brand-primary-fill)'
                      : 'transparent',
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* ── Loading State ─────────────────────────────────────────── */}
          {loading && (
            <SkeletonTable
              cols={activeTab === 'setores' ? 6 : activeTab === 'estabelecimentos' ? 5 : 5}
            />
          )}

          {/* ── Error State ───────────────────────────────────────────── */}
          {!loading && error && (
            <div
              role="alert"
              aria-live="assertive"
              className="border rounded-xl p-6"
              style={{
                backgroundColor: 'var(--clinical-severity-critical-wash)',
                borderColor: 'var(--clinical-severity-critical-signal)',
                color: 'var(--clinical-severity-critical-on-surface)',
              }}
            >
              <div className="flex items-start gap-3">
                <AlertTriangle
                  className="w-6 h-6 flex-shrink-0 mt-0.5"
                  style={{ color: 'var(--clinical-severity-critical-signal)' }}
                  aria-hidden="true"
                />
                <div>
                  <p className="font-semibold text-lg">Erro ao carregar dados</p>
                  <p className="text-sm mt-1 opacity-90">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* ── Content ──────────────────────────────────────────────── */}
          {!loading && !error && (
            <>
              {/* Toolbar */}
              <div className="flex items-center justify-between mb-4">
                <span
                  className="text-sm"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {activeTab === 'empresas'
                    ? `${empresas.length} empresa${empresas.length !== 1 ? 's' : ''}`
                    : activeTab === 'estabelecimentos'
                      ? `${estabelecimentos.length} estabelecimento${estabelecimentos.length !== 1 ? 's' : ''}`
                      : `${setores.length} setor${setores.length !== 1 ? 'es' : ''}`}
                </span>
                <button
                  onClick={() => openCreate(activeTab)}
                  disabled={activeTab === 'estabelecimentos' && empresas.length === 0}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg transition-all shadow-md disabled:opacity-50"
                  style={{
                    background:
                      'linear-gradient(to right, var(--color-brand-primary-fill, #3b82f6), var(--color-brand-secondary-fill, #6366f1))',
                  }}
                >
                  <Plus className="w-4 h-4" aria-hidden="true" />
                  Novo
                </button>
              </div>

              {/* ── Empresas Table ──────────────────────────────────── */}
              {activeTab === 'empresas' && (
                <>
                  {empresas.length === 0 ? (
                    <div
                      className="rounded-xl border p-12 text-center"
                      style={{
                        backgroundColor: 'var(--semantic-surface-raised)',
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      <Building2
                        className="w-16 h-16 mx-auto mb-4"
                        style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
                        aria-hidden="true"
                      />
                      <p
                        className="text-lg font-medium"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        Nenhuma empresa cadastrada
                      </p>
                      <p
                        className="text-sm mt-1"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        Adicione uma empresa para começar.
                      </p>
                    </div>
                  ) : (
                    <div
                      className="rounded-xl border overflow-hidden"
                      style={{
                        backgroundColor: 'var(--semantic-surface-raised)',
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      {/* Header */}
                      <div
                        className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 border-b text-xs font-semibold uppercase tracking-wider"
                        style={{
                          backgroundColor: 'var(--semantic-surface-canvas)',
                          borderColor: 'var(--semantic-border-default)',
                          color: 'var(--semantic-text-secondary)',
                        }}
                      >
                        <div className="col-span-2">CNPJ</div>
                        <div className="col-span-3">Razão Social</div>
                        <div className="col-span-3">Nome Fantasia</div>
                        <div className="col-span-2 text-center">Status</div>
                        <div className="col-span-2 text-center">Ações</div>
                      </div>

                      {/* Rows */}
                      <div
                        className="divide-y"
                        style={{ borderColor: 'var(--semantic-border-default)' }}
                      >
                        {empresas.map((emp) => (
                          <div
                            key={emp.id}
                            className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-6 py-4 items-center"
                          >
                            <div className="md:col-span-2 flex items-center gap-1.5">
                              <Hash
                                className="w-3.5 h-3.5 flex-shrink-0"
                                style={{ color: 'var(--semantic-text-secondary)' }}
                                aria-hidden="true"
                              />
                              <span
                                className="text-sm font-mono"
                                style={{ color: 'var(--semantic-text-primary)' }}
                              >
                                {formatCNPJ(emp.cnpj)}
                              </span>
                            </div>
                            <div
                              className="md:col-span-3 text-sm truncate"
                              style={{ color: 'var(--semantic-text-primary)' }}
                              title={emp.razao_social}
                            >
                              {emp.razao_social}
                            </div>
                            <div
                              className="md:col-span-3 text-sm truncate"
                              style={{ color: 'var(--semantic-text-secondary)' }}
                              title={emp.nome_fantasia}
                            >
                              {emp.nome_fantasia}
                            </div>
                            <div className="md:col-span-2 flex justify-center">
                              <AtivoBadge ativo={emp.ativo} />
                            </div>
                            <div className="md:col-span-2 flex justify-center gap-2">
                              <button
                                onClick={() => openEdit('empresas', emp.id)}
                                className="p-2 rounded-lg hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                                aria-label={`Editar ${emp.nome_fantasia}`}
                                title="Editar"
                              >
                                <Pencil
                                  className="w-4 h-4"
                                  style={{ color: 'var(--semantic-text-secondary)' }}
                                />
                              </button>
                              <button
                                onClick={() => toggleAtivo('empresas', emp.id)}
                                className="p-2 rounded-lg hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                                aria-label={emp.ativo ? 'Desativar' : 'Ativar'}
                                title={emp.ativo ? 'Desativar' : 'Ativar'}
                              >
                                {emp.ativo ? (
                                  <PowerOff
                                    className="w-4 h-4"
                                    style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                                  />
                                ) : (
                                  <Power
                                    className="w-4 h-4"
                                    style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
                                  />
                                )}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* ── Estabelecimentos Table ────────────────────────────── */}
              {activeTab === 'estabelecimentos' && (
                <>
                  {estabelecimentos.length === 0 ? (
                    <div
                      className="rounded-xl border p-12 text-center"
                      style={{
                        backgroundColor: 'var(--semantic-surface-raised)',
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      <Hospital
                        className="w-16 h-16 mx-auto mb-4"
                        style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
                        aria-hidden="true"
                      />
                      <p
                        className="text-lg font-medium"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        Nenhum estabelecimento cadastrado
                      </p>
                      <p
                        className="text-sm mt-1"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {empresas.length === 0
                          ? 'Cadastre uma empresa antes de adicionar estabelecimentos.'
                          : 'Adicione um estabelecimento para começar.'}
                      </p>
                    </div>
                  ) : (
                    <div
                      className="rounded-xl border overflow-hidden"
                      style={{
                        backgroundColor: 'var(--semantic-surface-raised)',
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      {/* Header */}
                      <div
                        className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 border-b text-xs font-semibold uppercase tracking-wider"
                        style={{
                          backgroundColor: 'var(--semantic-surface-canvas)',
                          borderColor: 'var(--semantic-border-default)',
                          color: 'var(--semantic-text-secondary)',
                        }}
                      >
                        <div className="col-span-2">CNES</div>
                        <div className="col-span-3">Nome</div>
                        <div className="col-span-3">Endereço</div>
                        <div className="col-span-2 text-center">Empresa</div>
                        <div className="col-span-1 text-center">Status</div>
                        <div className="col-span-1 text-center">Ações</div>
                      </div>

                      {/* Rows */}
                      <div
                        className="divide-y"
                        style={{ borderColor: 'var(--semantic-border-default)' }}
                      >
                        {estabelecimentos.map((est) => {
                          const empresa = empresaMap.get(est.empresa_id);
                          return (
                            <div
                              key={est.id}
                              className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-6 py-4 items-center"
                            >
                              <div
                                className="md:col-span-2 text-sm font-mono"
                                style={{ color: 'var(--semantic-text-primary)' }}
                              >
                                {est.cnes}
                              </div>
                              <div
                                className="md:col-span-3 text-sm truncate"
                                style={{ color: 'var(--semantic-text-primary)' }}
                                title={est.nome}
                              >
                                {est.nome}
                              </div>
                              <div
                                className="md:col-span-3 text-sm truncate flex items-center gap-1.5"
                                style={{ color: 'var(--semantic-text-secondary)' }}
                                title={est.endereco}
                              >
                                <MapPin
                                  className="w-3.5 h-3.5 flex-shrink-0"
                                  style={{ color: 'var(--semantic-text-secondary)' }}
                                  aria-hidden="true"
                                />
                                {est.endereco}
                              </div>
                              <div className="md:col-span-2 flex justify-center">
                                <span
                                  className="text-sm truncate max-w-[120px]"
                                  style={{ color: 'var(--semantic-text-secondary)' }}
                                  title={empresa?.nome_fantasia ?? est.empresa_id}
                                >
                                  {empresa?.nome_fantasia ?? '—'}
                                </span>
                              </div>
                              <div className="md:col-span-1 flex justify-center">
                                <AtivoBadge ativo={est.ativo} />
                              </div>
                              <div className="md:col-span-1 flex justify-center gap-1">
                                <button
                                  onClick={() => openEdit('estabelecimentos', est.id)}
                                  className="p-2 rounded-lg hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                                  aria-label={`Editar ${est.nome}`}
                                  title="Editar"
                                >
                                  <Pencil
                                    className="w-4 h-4"
                                    style={{ color: 'var(--semantic-text-secondary)' }}
                                  />
                                </button>
                                <button
                                  onClick={() => toggleAtivo('estabelecimentos', est.id)}
                                  className="p-2 rounded-lg hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                                  aria-label={est.ativo ? 'Desativar' : 'Ativar'}
                                  title={est.ativo ? 'Desativar' : 'Ativar'}
                                >
                                  {est.ativo ? (
                                    <PowerOff
                                      className="w-4 h-4"
                                      style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                                    />
                                  ) : (
                                    <Power
                                      className="w-4 h-4"
                                      style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
                                    />
                                  )}
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* ── Setores Table ────────────────────────────────────── */}
              {activeTab === 'setores' && (
                <>
                  {setores.length === 0 ? (
                    <div
                      className="rounded-xl border p-12 text-center"
                      style={{
                        backgroundColor: 'var(--semantic-surface-raised)',
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      <DoorOpen
                        className="w-16 h-16 mx-auto mb-4"
                        style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
                        aria-hidden="true"
                      />
                      <p
                        className="text-lg font-medium"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        Nenhum setor cadastrado
                      </p>
                      <p
                        className="text-sm mt-1"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {estabelecimentos.length === 0
                          ? 'Cadastre um estabelecimento antes de adicionar setores.'
                          : 'Adicione um setor para começar.'}
                      </p>
                    </div>
                  ) : (
                    <div
                      className="rounded-xl border overflow-hidden"
                      style={{
                        backgroundColor: 'var(--semantic-surface-raised)',
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      {/* Header */}
                      <div
                        className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 border-b text-xs font-semibold uppercase tracking-wider"
                        style={{
                          backgroundColor: 'var(--semantic-surface-canvas)',
                          borderColor: 'var(--semantic-border-default)',
                          color: 'var(--semantic-text-secondary)',
                        }}
                      >
                        <div className="col-span-1">Sigla</div>
                        <div className="col-span-3">Nome</div>
                        <div className="col-span-2 text-center">Tipo</div>
                        <div className="col-span-2 text-center">Estabelecimento</div>
                        <div className="col-span-1 text-center">Leitos</div>
                        <div className="col-span-1 text-center">Status</div>
                        <div className="col-span-2 text-center">Ações</div>
                      </div>

                      {/* Rows */}
                      <div
                        className="divide-y"
                        style={{ borderColor: 'var(--semantic-border-default)' }}
                      >
                        {setores.map((set) => {
                          const estab = estabMap.get(set.estabelecimento_id);
                          return (
                            <div
                              key={set.id}
                              className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-6 py-4 items-center"
                            >
                              <div
                                className="md:col-span-1 text-sm font-semibold"
                                style={{ color: 'var(--semantic-text-primary)' }}
                              >
                                {set.sigla}
                              </div>
                              <div
                                className="md:col-span-3 text-sm truncate"
                                style={{ color: 'var(--semantic-text-primary)' }}
                                title={set.nome}
                              >
                                {set.nome}
                              </div>
                              <div className="md:col-span-2 flex justify-center">
                                <TipoBadge tipo={set.tipo} />
                              </div>
                              <div className="md:col-span-2 flex justify-center">
                                <span
                                  className="text-sm truncate max-w-[140px]"
                                  style={{ color: 'var(--semantic-text-secondary)' }}
                                  title={estab?.nome ?? set.estabelecimento_id}
                                >
                                  {estab?.nome ?? '—'}
                                </span>
                              </div>
                              <div className="md:col-span-1 flex justify-center items-center gap-1">
                                <BedDouble
                                  className="w-3.5 h-3.5"
                                  style={{ color: 'var(--semantic-text-secondary)' }}
                                  aria-hidden="true"
                                />
                                <span
                                  className="text-sm"
                                  style={{ color: 'var(--semantic-text-primary)' }}
                                >
                                  {set.leitos_operacionais}
                                </span>
                              </div>
                              <div className="md:col-span-1 flex justify-center">
                                <AtivoBadge ativo={set.ativo} />
                              </div>
                              <div className="md:col-span-2 flex justify-center gap-1">
                                <button
                                  onClick={() => openEdit('setores', set.id)}
                                  className="p-2 rounded-lg hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                                  aria-label={`Editar ${set.nome}`}
                                  title="Editar"
                                >
                                  <Pencil
                                    className="w-4 h-4"
                                    style={{ color: 'var(--semantic-text-secondary)' }}
                                  />
                                </button>
                                <button
                                  onClick={() => toggleAtivo('setores', set.id)}
                                  className="p-2 rounded-lg hover:bg-black/5 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                                  aria-label={set.ativo ? 'Desativar' : 'Ativar'}
                                  title={set.ativo ? 'Desativar' : 'Ativar'}
                                >
                                  {set.ativo ? (
                                    <PowerOff
                                      className="w-4 h-4"
                                      style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                                    />
                                  ) : (
                                    <Power
                                      className="w-4 h-4"
                                      style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
                                    />
                                  )}
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </ErrorBoundary>

      {/* ── Drawer: Create / Edit Form ────────────────────────────────── */}
      <DrawerBuilder
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={drawerTitle}
        size="md"
      >
        {/* Form Error */}
        {formError && (
          <div
            role="alert"
            className="border rounded-lg p-3 text-sm mb-4"
            style={{
              backgroundColor: 'var(--clinical-severity-critical-wash)',
              borderColor: 'var(--clinical-severity-critical-signal)',
              color: 'var(--clinical-severity-critical-on-surface)',
            }}
          >
            {formError}
          </div>
        )}

        <div className="space-y-3">
          {/* ── Empresa Form ─────────────────────────────────────────── */}
          {drawerEntity === 'empresas' && (
            <>
              <div>
                <label
                  htmlFor="reg-cnpj"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  CNPJ *
                </label>
                <input
                  id="reg-cnpj"
                  type="text"
                  value={empresaForm.cnpj}
                  onChange={(e) =>
                    setEmpresaForm((f) => ({ ...f, cnpj: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="00.000.000/0000-00"
                />
              </div>
              <div>
                <label
                  htmlFor="reg-razao"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Razão Social *
                </label>
                <input
                  id="reg-razao"
                  type="text"
                  value={empresaForm.razao_social}
                  onChange={(e) =>
                    setEmpresaForm((f) => ({ ...f, razao_social: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="Hospital São Lucas S.A."
                />
              </div>
              <div>
                <label
                  htmlFor="reg-fantasia"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Nome Fantasia *
                </label>
                <input
                  id="reg-fantasia"
                  type="text"
                  value={empresaForm.nome_fantasia}
                  onChange={(e) =>
                    setEmpresaForm((f) => ({ ...f, nome_fantasia: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="Hospital São Lucas"
                />
              </div>
            </>
          )}

          {/* ── Estabelecimento Form ──────────────────────────────────── */}
          {drawerEntity === 'estabelecimentos' && (
            <>
              <div>
                <label
                  htmlFor="reg-est-empresa"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Empresa *
                </label>
                <select
                  id="reg-est-empresa"
                  value={estabelecimentoForm.empresa_id}
                  onChange={(e) =>
                    setEstabelecimentoForm((f) => ({ ...f, empresa_id: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                >
                  <option value="" disabled>
                    Selecione uma empresa
                  </option>
                  {empresas.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.nome_fantasia}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label
                  htmlFor="reg-cnes"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  CNES *
                </label>
                <input
                  id="reg-cnes"
                  type="text"
                  value={estabelecimentoForm.cnes}
                  onChange={(e) =>
                    setEstabelecimentoForm((f) => ({ ...f, cnes: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="1234567"
                />
              </div>
              <div>
                <label
                  htmlFor="reg-est-nome"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Nome *
                </label>
                <input
                  id="reg-est-nome"
                  type="text"
                  value={estabelecimentoForm.nome}
                  onChange={(e) =>
                    setEstabelecimentoForm((f) => ({ ...f, nome: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="Matriz — Unidade Central"
                />
              </div>
              <div>
                <label
                  htmlFor="reg-endereco"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Endereço *
                </label>
                <input
                  id="reg-endereco"
                  type="text"
                  value={estabelecimentoForm.endereco}
                  onChange={(e) =>
                    setEstabelecimentoForm((f) => ({ ...f, endereco: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="Av. Paulista, 1000 — São Paulo/SP"
                />
              </div>
            </>
          )}

          {/* ── Setor Form ────────────────────────────────────────────── */}
          {drawerEntity === 'setores' && (
            <>
              <div>
                <label
                  htmlFor="reg-set-estab"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Estabelecimento *
                </label>
                <select
                  id="reg-set-estab"
                  value={setorForm.estabelecimento_id}
                  onChange={(e) =>
                    setSetorForm((f) => ({ ...f, estabelecimento_id: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                >
                  <option value="" disabled>
                    Selecione um estabelecimento
                  </option>
                  {estabelecimentos.map((est) => (
                    <option key={est.id} value={est.id}>
                      {est.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label
                  htmlFor="reg-set-nome"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Nome *
                </label>
                <input
                  id="reg-set-nome"
                  type="text"
                  value={setorForm.nome}
                  onChange={(e) =>
                    setSetorForm((f) => ({ ...f, nome: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="UTI Geral Adulto"
                />
              </div>
              <div>
                <label
                  htmlFor="reg-set-sigla"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Sigla *
                </label>
                <input
                  id="reg-set-sigla"
                  type="text"
                  value={setorForm.sigla}
                  onChange={(e) =>
                    setSetorForm((f) => ({ ...f, sigla: e.target.value }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="UTI-GA"
                />
              </div>
              <div>
                <label
                  htmlFor="reg-set-tipo"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Tipo
                </label>
                <select
                  id="reg-set-tipo"
                  value={setorForm.tipo}
                  onChange={(e) =>
                    setSetorForm((f) => ({ ...f, tipo: e.target.value as SetorTipo }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                >
                  {Object.entries(SETOR_TIPO_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label
                  htmlFor="reg-set-leitos"
                  className="text-xs font-semibold uppercase tracking-wider block mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Leitos Operacionais
                </label>
                <input
                  id="reg-set-leitos"
                  type="number"
                  min={0}
                  value={setorForm.leitos_operacionais}
                  onChange={(e) =>
                    setSetorForm((f) => ({
                      ...f,
                      leitos_operacionais: Math.max(0, parseInt(e.target.value, 10) || 0),
                    }))
                  }
                  className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                  placeholder="20"
                />
              </div>
            </>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={() => setDrawerOpen(false)}
            disabled={submitting}
            className="flex-1 px-4 py-2 text-sm font-medium border rounded-lg hover:bg-black/5 transition-colors disabled:opacity-50"
            style={{
              color: 'var(--semantic-text-secondary)',
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="flex-1 px-4 py-2 text-sm font-medium text-white rounded-lg shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
            style={{
              background:
                'linear-gradient(to right, var(--color-brand-primary-fill, #3b82f6), var(--color-brand-secondary-fill, #6366f1))',
            }}
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" aria-hidden="true" />
                Salvando...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" aria-hidden="true" />
                {editingId ? 'Salvar' : 'Criar'}
              </>
            )}
          </button>
        </div>
      </DrawerBuilder>
    </Layout>
  );
}
