'use client';

import React, { useState, useMemo, useEffect } from 'react';
import {
  FileText,
  Plus,
  Search,
  UserCheck,
  AlertTriangle,
  Loader2,
  CheckCircle,
  Edit3,
  Eye,
  Send,
} from 'lucide-react';
import Layout from '@/components/Layout';
import DrawerBuilder from '@/components/DrawerBuilder';
import NotesTimeline from '@/components/NotesTimeline';
import type { Evolucao, EvolucaoCreate, EvolutionType } from '@/lib/clinical-notes-types';
import {
  MOCK_NOTES,
  MOCK_PATIENTS,
  TYPE_LABELS,
  TYPE_ICONS,
  getTypeColor,
  formatNoteType,
} from '@/lib/clinical-notes-types';

// ─── Types for filters ───────────────────────────────────────────────────────

type TypeFilter = 'todas' | EvolutionType;

const FILTER_TABS: { key: TypeFilter; label: string }[] = [
  { key: 'todas', label: 'Todas' },
  { key: 'admissao', label: 'Admissão' },
  { key: 'diaria', label: 'Diária' },
  { key: 'alta', label: 'Alta' },
  { key: 'obito', label: 'Óbito' },
  { key: 'intercorrencia', label: 'Intercorrência' },
];

// ─── Simple markdown renderer (shared logic for preview tab) ─────────────────

function renderSimplePreview(content: string): React.ReactNode {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let paraLines: React.ReactNode[] = [];
  const keyPrefix = `preview-${Date.now()}-`;

  const flushParagraph = (idx: number) => {
    if (paraLines.length > 0) {
      elements.push(
        <p key={`${keyPrefix}p-${idx}`} className="mb-2 leading-relaxed">
          {paraLines.map((node, i) => (
            <React.Fragment key={i}>
              {i > 0 && <br />}
              {node}
            </React.Fragment>
          ))}
        </p>,
      );
      paraLines = [];
    }
  };

  lines.forEach((line, lineIdx) => {
    const h2 = line.match(/^##\s+(.+)/);
    if (h2) {
      flushParagraph(lineIdx);
      elements.push(
        <h3 key={`${keyPrefix}h2-${lineIdx}`} className="text-base font-semibold mt-3 mb-1">
          {renderInlineBold(h2[1]!)}
        </h3>,
      );
      return;
    }
    const h1 = line.match(/^#\s+(.+)/);
    if (h1) {
      flushParagraph(lineIdx);
      elements.push(
        <h2 key={`${keyPrefix}h1-${lineIdx}`} className="text-lg font-bold mt-3 mb-2">
          {renderInlineBold(h1[1]!)}
        </h2>,
      );
      return;
    }
    if (/-{3,}/.test(line.trim())) {
      flushParagraph(lineIdx);
      elements.push(
        <hr key={`${keyPrefix}hr-${lineIdx}`} className="my-2" />,
      );
      return;
    }
    if (line.trim() === '') {
      flushParagraph(lineIdx);
      return;
    }
    paraLines.push(<span key={`${keyPrefix}span-${lineIdx}`}>{renderInlineBold(line)}</span>);
  });
  flushParagraph(lines.length);

  return <div className="text-sm">{elements}</div>;
}

function renderInlineBold(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    const m = part.match(/^\*\*(.+)\*\*$/);
    if (m) return <strong key={i} className="font-semibold">{m[1]}</strong>;
    return <span key={i}>{part}</span>;
  });
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function ClinicalNotesPage() {
  // Patient state
  const [selectedMpiId, setSelectedMpiId] = useState<string>(MOCK_PATIENTS[0]!.mpiId);
  const [patientSearch, setPatientSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  // Filter
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('todas');

  // Loading & error (simulated)
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Notes state (mutable for mock submit)
  const [notes, setNotes] = useState<Evolucao[]>(MOCK_NOTES);

  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [newNoteType, setNewNoteType] = useState<EvolutionType>('diaria');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<'success' | 'error' | null>(null);
  const [previewMode, setPreviewMode] = useState<'edit' | 'preview'>('edit');

  // ─── Simulate initial load ─────────────────────────────────────────────────
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  // ─── Filtered notes ───────────────────────────────────────────────────────
  const filteredNotes = useMemo(() => {
    let result = notes.filter((n) => n.mpi_id === selectedMpiId);
    if (typeFilter !== 'todas') {
      result = result.filter((n) => n.type === typeFilter);
    }
    // Sort by created_at descending
    return result.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    );
  }, [notes, selectedMpiId, typeFilter]);

  // ─── Selected patient info ─────────────────────────────────────────────────
  const selectedPatient = MOCK_PATIENTS.find((p) => p.mpiId === selectedMpiId);

  // ─── Patient search ────────────────────────────────────────────────────────
  const filteredPatients = MOCK_PATIENTS.filter(
    (p) =>
      !patientSearch ||
      p.name.toLowerCase().includes(patientSearch.toLowerCase()) ||
      p.mpiId.toLowerCase().includes(patientSearch.toLowerCase()),
  );

  // ─── Submit handler ────────────────────────────────────────────────────────
  const handleSubmitNote = async () => {
    if (!newNoteContent.trim()) return;

    setSubmitting(true);
    setSubmitResult(null);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));

    try {
      const newNote: Evolucao = {
        id: `evol-${Date.now()}`,
        mpi_id: selectedMpiId,
        type: newNoteType,
        content: newNoteContent.trim(),
        created_at: new Date().toISOString(),
        created_by: 'Dr. Usuário Atual',
      };

      setNotes((prev) => [newNote, ...prev]);
      setSubmitResult('success');

      // Reset form after short delay
      setTimeout(() => {
        setNewNoteContent('');
        setNewNoteType('diaria');
        setSubmitResult(null);
        setDrawerOpen(false);
        setPreviewMode('edit');
      }, 1200);
    } catch {
      setSubmitResult('error');
    } finally {
      setSubmitting(false);
    }
  };

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Evoluções Clínicas
          </h1>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Diário médico — registro cronológico das evoluções dos pacientes
          </p>
        </div>
        <button
          onClick={() => {
            setSubmitResult(null);
            setNewNoteContent('');
            setNewNoteType('diaria');
            setPreviewMode('edit');
            setDrawerOpen(true);
          }}
          aria-label="Criar nova evolução clínica"
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
          style={{
            backgroundColor: 'var(--clinical-severity-normal-fill)',
            color: 'var(--clinical-severity-normal-on-fill)',
          }}
        >
          <Plus className="w-4 h-4" aria-hidden="true" />
          Nova Evolução
        </button>
      </div>

      {/* Patient selector */}
      <div
        className="rounded-xl border p-5 mb-6"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <label
          className="text-sm font-semibold uppercase tracking-wider mb-3 block"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Paciente
        </label>
        <div className="relative">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
            style={{ color: 'var(--semantic-text-secondary)' }}
            aria-hidden="true"
          />
          <input
            type="text"
            value={patientSearch}
            onChange={(e) => {
              setPatientSearch(e.target.value);
              setShowDropdown(true);
            }}
            onFocus={() => setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder="Buscar por nome ou MPI ID..."
            aria-label="Buscar pacientes"
            className="w-full pl-10 pr-4 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-canvas)',
            }}
          />
          {showDropdown && filteredPatients.length > 0 && (
            <div
              className="absolute z-10 w-full mt-1 rounded-lg border shadow-lg max-h-48 overflow-y-auto"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              {filteredPatients.map((patient) => (
                <button
                  key={patient.mpiId}
                  onMouseDown={() => {
                    setSelectedMpiId(patient.mpiId);
                    setPatientSearch('');
                    setShowDropdown(false);
                    setTypeFilter('todas');
                  }}
                  className={`w-full text-left px-4 py-3 text-sm transition-colors flex items-center justify-between ${
                    patient.mpiId === selectedMpiId ? 'font-semibold' : ''
                  }`}
                  style={{
                    color: 'var(--semantic-text-primary)',
                    borderBottom: '1px solid var(--semantic-border-default)',
                    backgroundColor:
                      patient.mpiId === selectedMpiId
                        ? 'var(--clinical-severity-normal-wash)'
                        : 'transparent',
                  }}
                  aria-label={`Selecionar paciente ${patient.name}`}
                >
                  <span className="flex items-center gap-2">
                    <UserCheck
                      className="w-4 h-4"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                      aria-hidden="true"
                    />
                    {patient.name}
                  </span>
                  <span
                    className="text-xs"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {patient.bed}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
        {selectedPatient && (
          <div
            className="mt-3 flex items-center gap-2 text-sm font-medium"
            style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
          >
            <CheckCircle className="w-4 h-4" aria-hidden="true" />
            Selecionado: {selectedPatient.name} ({selectedPatient.mpiId}) · {selectedPatient.bed}
          </div>
        )}
      </div>

      {/* Filter tabs */}
      <div
        className="flex gap-1 mb-6 overflow-x-auto border-b"
        style={{ borderColor: 'var(--semantic-border-default)' }}
        role="tablist"
        aria-label="Filtrar por tipo de evolução"
      >
        {FILTER_TABS.map((tab) => {
          const isActive = typeFilter === tab.key;
          const Icon = tab.key !== 'todas' ? TYPE_ICONS[tab.key] : null;

          return (
            <button
              key={tab.key}
              onClick={() => setTypeFilter(tab.key)}
              role="tab"
              aria-selected={isActive}
              aria-label={`Filtrar ${tab.label}`}
              className="flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-all border-b-2 -mb-px focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
              style={{
                color: isActive
                  ? 'var(--semantic-text-primary)'
                  : 'var(--semantic-text-secondary)',
                borderBottomColor: isActive
                  ? 'var(--clinical-status-attended-color)'
                  : 'transparent',
              }}
            >
              {Icon && <Icon className="w-3.5 h-3.5" aria-hidden="true" />}
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Notes Timeline */}
      <div
        className="rounded-xl border p-6"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <NotesTimeline
          notes={filteredNotes}
          isLoading={loading}
          error={error}
          emptyMessage="Nenhuma evolução para este paciente"
        />
      </div>

      {/* ─── Drawer: Nova Evolução ─────────────────────────────────────────── */}
      <DrawerBuilder
        open={drawerOpen}
        onClose={() => {
          if (!submitting) {
            setDrawerOpen(false);
            setSubmitResult(null);
          }
        }}
        title="Nova Evolução Clínica"
        size="lg"
      >
        <div className="space-y-5">
          {/* Type selector */}
          <div>
            <label
              className="text-sm font-semibold mb-2 block"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Tipo de Evolução
            </label>
            <select
              value={newNoteType}
              onChange={(e) => setNewNoteType(e.target.value as EvolutionType)}
              aria-label="Tipo de evolução"
              className="w-full px-4 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
              style={{
                borderColor: 'var(--semantic-border-default)',
                color: 'var(--semantic-text-primary)',
                backgroundColor: 'var(--semantic-surface-canvas)',
              }}
            >
              {(Object.entries(TYPE_LABELS) as [EvolutionType, string][]).map(
                ([key, label]) => {
                  const Icon = TYPE_ICONS[key];
                  return (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  );
                },
              )}
            </select>
          </div>

          {/* Content tabs: Edit | Preview */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label
                className="text-sm font-semibold"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Conteúdo (Markdown)
              </label>
              <div className="flex gap-1">
                <button
                  onClick={() => setPreviewMode('edit')}
                  aria-pressed={previewMode === 'edit'}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                    previewMode === 'edit' ? 'ring-1' : ''
                  }`}
                  style={{
                    color:
                      previewMode === 'edit'
                        ? 'var(--clinical-severity-normal-on-fill)'
                        : 'var(--semantic-text-secondary)',
                    backgroundColor:
                      previewMode === 'edit'
                        ? 'var(--clinical-severity-normal-fill)'
                        : 'transparent',
                    borderColor: 'var(--semantic-border-default)',
                    borderWidth: '1px',
                    borderStyle: 'solid',
                  }}
                >
                  <Edit3 className="w-3 h-3" aria-hidden="true" />
                  Editar
                </button>
                <button
                  onClick={() => setPreviewMode('preview')}
                  aria-pressed={previewMode === 'preview'}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                    previewMode === 'preview' ? 'ring-1' : ''
                  }`}
                  style={{
                    color:
                      previewMode === 'preview'
                        ? 'var(--clinical-severity-normal-on-fill)'
                        : 'var(--semantic-text-secondary)',
                    backgroundColor:
                      previewMode === 'preview'
                        ? 'var(--clinical-severity-normal-fill)'
                        : 'transparent',
                    borderColor: 'var(--semantic-border-default)',
                    borderWidth: '1px',
                    borderStyle: 'solid',
                  }}
                >
                  <Eye className="w-3 h-3" aria-hidden="true" />
                  Preview
                </button>
              </div>
            </div>

            {previewMode === 'edit' ? (
              <textarea
                value={newNoteContent}
                onChange={(e) => setNewNoteContent(e.target.value)}
                placeholder={`Digite a evolução em formato markdown...

**Exemplo:**
# Título da Evolução

## Sinais Vitais
- **PA:** 120/80 mmHg
- **FC:** 88 bpm

## Conduta
- Manter tratamento conforme prescrição`}
                rows={15}
                aria-label="Conteúdo da evolução clínica"
                className="w-full px-4 py-3 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y font-mono"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              />
            ) : (
              <div
                className="w-full min-h-[300px] px-4 py-3 rounded-lg border text-sm"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              >
                {newNoteContent.trim() ? (
                  renderSimplePreview(newNoteContent)
                ) : (
                  <p
                    className="italic"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    Nenhum conteúdo para preview. Escreva no modo Editar.
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Submit + status */}
          <div className="flex items-center gap-4 pt-2">
            <button
              onClick={handleSubmitNote}
              disabled={submitting || !newNoteContent.trim()}
              aria-label="Registrar evolução clínica"
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
              style={{
                backgroundColor: 'var(--clinical-severity-normal-fill)',
                color: 'var(--clinical-severity-normal-on-fill)',
              }}
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  Registrando...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" aria-hidden="true" />
                  Registrar Evolução
                </>
              )}
            </button>

            {/* Feedback */}
            {submitResult === 'success' && (
              <div
                className="flex items-center gap-2 text-sm font-medium"
                style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
                role="status"
                aria-live="polite"
              >
                <CheckCircle className="w-4 h-4" aria-hidden="true" />
                Evolução registrada com sucesso!
              </div>
            )}

            {submitResult === 'error' && (
              <div
                className="flex items-center gap-2 text-sm font-medium"
                style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                role="alert"
                aria-live="assertive"
              >
                <AlertTriangle className="w-4 h-4" aria-hidden="true" />
                Falha ao registrar evolução. Tente novamente.
              </div>
            )}
          </div>

          {/* Character count */}
          <div
            className="text-xs"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            {newNoteContent.length} / 50000 caracteres
            {newNoteContent.length > 50000 && (
              <span
                className="ml-2 font-semibold"
                style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
              >
                Limite excedido!
              </span>
            )}
          </div>
        </div>
      </DrawerBuilder>
    </Layout>
  );
}
