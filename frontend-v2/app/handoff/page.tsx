'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  FileText,
  AlertTriangle,
  Clock,
  Pill,
  ClipboardList,
  Printer,
  Download,
  CheckCircle,
  Search,
  Edit3,
  Save,
  ShieldAlert,
  RefreshCw,
} from 'lucide-react';
import Layout from '@/components/Layout';
import { fetchHandoff, submitHandoff, type HandoffPatient } from '@/lib/api';

// ─── Types ──────────────────────────────────────────────────────────────────

type SectionName = 'summary' | 'activeIssues' | 'pendingActions' | 'medications';

interface HandoffSection {
  name: SectionName;
  label: string;
  icon: React.ReactNode;
  content: string;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function statusColour(status: HandoffPatient['status']): string {
  switch (status) {
    case 'critical':
      return 'var(--clinical-severity-critical-signal)';
    case 'watch':
      return 'var(--clinical-severity-watch-signal)';
    default:
      return 'var(--clinical-severity-normal-signal)';
  }
}

function statusWash(status: HandoffPatient['status']): string {
  switch (status) {
    case 'critical':
      return 'var(--clinical-severity-critical-wash)';
    case 'watch':
      return 'var(--clinical-severity-watch-wash)';
    default:
      return 'var(--clinical-severity-normal-wash)';
  }
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function HandoffPage() {
  const [patients, setPatients] = useState<HandoffPatient[]>([]);
  const [selectedPatients, setSelectedPatients] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingSection, setEditingSection] = useState<SectionName | null>(null);
  const [lastHandoffTimestamp, setLastHandoffTimestamp] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // ── Fetch patients from API ───────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchHandoff()
      .then((data) => {
        if (cancelled) return;
        setPatients(data.patients);
        setLastHandoffTimestamp(data.last_handoff_at);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Erro ao carregar dados da passagem');
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const [sections, setSections] = useState<HandoffSection[]>([
    { name: 'summary', label: 'Resumo', icon: <FileText className="w-4 h-4" aria-hidden="true" />, content: '' },
    {
      name: 'activeIssues',
      label: 'Problemas Ativos',
      icon: <AlertTriangle className="w-4 h-4" aria-hidden="true" />,
      content: '',
    },
    {
      name: 'pendingActions',
      label: 'Ações Pendentes',
      icon: <ClipboardList className="w-4 h-4" aria-hidden="true" />,
      content: '',
    },
    {
      name: 'medications',
      label: 'Medicações',
      icon: <Pill className="w-4 h-4" aria-hidden="true" />,
      content: '',
    },
  ]);

  const filteredPatients = patients.filter(
    (p) =>
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.mpi_id.toLowerCase().includes(search.toLowerCase()),
  );

  const togglePatient = (mpiId: string) => {
    setSelectedPatients((prev) => {
      const next = new Set(prev);
      if (next.has(mpiId)) {
        next.delete(mpiId);
      } else {
        next.add(mpiId);
      }
      return next;
    });
  };

  const updateSection = (name: SectionName, content: string) => {
    setSections((prev) =>
      prev.map((s) => (s.name === name ? { ...s, content } : s)),
    );
  };

  const formatTimestamp = (iso: string | null): string => {
    if (!iso) return 'Nenhuma passagem anterior';
    return new Date(iso).toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    const text = sections
      .map((s) => `=== ${s.label} ===\n${s.content || '(empty)'}`)
      .join('\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `handoff-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleConcluirPassagem = async () => {
    setSubmitting(true);
    try {
      const result = await submitHandoff({
        mpi_ids: Array.from(selectedPatients),
        summary: sections.find((s) => s.name === 'summary')?.content,
        active_issues: sections.find((s) => s.name === 'activeIssues')?.content,
        pending_actions: sections.find((s) => s.name === 'pendingActions')?.content,
        medications: sections.find((s) => s.name === 'medications')?.content,
      });
      setLastHandoffTimestamp(result.timestamp);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao enviar passagem');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3" style={{ color: 'var(--semantic-text-secondary)' }}>
            <RefreshCw className="w-5 h-5 animate-spin" aria-hidden="true" />
            <span>Carregando dados da passagem...</span>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div
          className="border rounded-xl p-6"
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          role="alert"
          aria-live="assertive"
        >
          <h2 className="font-semibold">Erro ao carregar dados da passagem</h2>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={() => { setError(null); setLoading(true); }}
            className="mt-3 text-sm underline"
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
          >
            Tentar novamente
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Relatório de Passagem
          </h1>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Passagem de turno
            {lastHandoffTimestamp && (
              <span
                className="inline-flex items-center gap-1 ml-3 text-xs"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <Clock className="w-3 h-3" aria-hidden="true" />
                Última passagem: {formatTimestamp(lastHandoffTimestamp)}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            aria-label="Imprimir relatório de passagem"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <Printer className="w-4 h-4" aria-hidden="true" />
            Imprimir
          </button>
          <button
            onClick={handleExport}
            aria-label="Exportar relatório de passagem"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <Download className="w-4 h-4" aria-hidden="true" />
            Exportar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Patient quick-select */}
        <div className="lg:col-span-1">
          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <h2
              className="text-sm font-semibold uppercase tracking-wider mb-4"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              <Users className="w-4 h-4 inline mr-1.5" aria-hidden="true" />
              Pacientes
            </h2>

            <div className="relative mb-4">
              <Search
                aria-hidden="true"
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                style={{ color: 'var(--semantic-text-secondary)' }}
              />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar pacientes..."
                aria-label="Buscar pacientes para passagem"
                className="w-full pl-10 pr-4 py-2 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              />
            </div>

            <div className="space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto">
              {filteredPatients.map((patient) => {
                const isSelected = selectedPatients.has(patient.mpi_id);
                return (
                  <button
                    key={patient.mpi_id}
                    onClick={() => togglePatient(patient.mpi_id)}
                    aria-label={`${isSelected ? 'Desselecionar' : 'Selecionar'} paciente ${patient.name}`}
                    aria-pressed={isSelected}
                    className="w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between"
                    style={{
                      borderColor: isSelected
                        ? statusColour(patient.status)
                        : 'var(--semantic-border-default)',
                      backgroundColor: isSelected
                        ? statusWash(patient.status)
                        : 'var(--semantic-surface-canvas)',
                    }}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: statusColour(patient.status) }}
                      />
                      <div className="min-w-0">
                        <p
                          className="text-sm font-medium truncate"
                          style={{ color: 'var(--semantic-text-primary)' }}
                        >
                          {patient.name}
                        </p>
                        <p
                          className="text-xs"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          {patient.mpi_id}
                          {patient.bed_id && ` · ${patient.bed_id}`}
                        </p>
                      </div>
                    </div>
                    {isSelected && (
                      <CheckCircle
                        aria-hidden="true"
                        className="w-5 h-5 flex-shrink-0"
                        style={{ color: statusColour(patient.status) }}
                      />
                    )}
                  </button>
                );
              })}
            </div>

            {selectedPatients.size > 0 && (
              <div
                className="mt-4 px-3 py-2 rounded-lg text-xs font-medium"
                style={{
                  backgroundColor: 'var(--clinical-severity-normal-wash)',
                  color: 'var(--clinical-severity-normal-on-surface)',
                }}
              >
                {selectedPatients.size} paciente{selectedPatients.size !== 1 ? 's' : ''} selecionado{selectedPatients.size !== 1 ? 's' : ''}
              </div>
            )}
          </div>
        </div>

        {/* Right: Structured sections */}
        <div className="lg:col-span-2 space-y-4">
          {sections.map((section) => {
            const isEditing = editingSection === section.name;
            return (
              <div
                key={section.name}
                className="rounded-xl border p-5"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
                aria-label={`Handoff section: ${section.label}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3
                    className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {section.icon}
                    {section.label}
                  </h3>
                  <button
                    onClick={() =>
                      setEditingSection(isEditing ? null : section.name)
                    }
                    aria-label={`${isEditing ? 'Salvar' : 'Editar'} seção ${section.label}`}
                    className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-all"
                    style={{
                      borderColor: 'var(--semantic-border-default)',
                      color: 'var(--semantic-text-secondary)',
                      backgroundColor: isEditing
                        ? 'var(--clinical-severity-normal-wash)'
                        : 'var(--semantic-surface-canvas)',
                    }}
                  >
                    {isEditing ? (
                      <>
                        <Save className="w-3.5 h-3.5" aria-hidden="true" />
                        Salvar
                      </>
                    ) : (
                      <>
                        <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
                        Editar
                      </>
                    )}
                  </button>
                </div>

                {isEditing ? (
                  <textarea
                    value={section.content}
                    onChange={(e) => updateSection(section.name, e.target.value)}
                    placeholder={`Digite notas de ${section.label.toLowerCase()}...`}
                    rows={5}
                    aria-label={`Editar ${section.label}`}
                    className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
                    style={{
                      borderColor: 'var(--semantic-border-default)',
                      color: 'var(--semantic-text-primary)',
                      backgroundColor: 'var(--semantic-surface-canvas)',
                    }}
                    autoFocus
                  />
                ) : (
                  <div
                    className="text-sm leading-relaxed min-h-[2rem]"
                    style={{
                      color: section.content
                        ? 'var(--semantic-text-primary)'
                        : 'var(--semantic-text-secondary)',
                    }}
                  >
                    {section.content || (
                      <em>Nenhum(a) {section.label.toLowerCase()} registrado(a). Clique em Editar para adicionar notas.</em>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Handoff completion status */}
          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h3
                  className="text-sm font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Status da Passagem
                </h3>
                <p
                  className="text-xs mt-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {sections.some((s) => s.content)
                    ? `${sections.filter((s) => s.content).length} de ${sections.length} seções preenchidas`
                    : 'Nenhuma seção preenchida'}
                  {selectedPatients.size > 0 &&
                    ` · ${selectedPatients.size} paciente${selectedPatients.size !== 1 ? 's' : ''} selecionado${selectedPatients.size !== 1 ? 's' : ''}`}
                </p>
              </div>
              <button
                disabled={submitting || selectedPatients.size === 0 || !sections.some((s) => s.content)}
                aria-label="Enviar relatório de passagem"
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                style={{
                  backgroundColor: 'var(--clinical-severity-normal-fill)',
                  color: 'var(--clinical-severity-normal-on-fill)',
                }}
                onClick={handleConcluirPassagem}
              >
                <ShieldAlert className="w-4 h-4" aria-hidden="true" />
                {submitting ? 'Enviando...' : 'Concluir Passagem'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
