'use client';

import React, { useState, useMemo, useCallback } from 'react';
import {
  FileText,
  Plus,
  Calendar,
  AlertTriangle,
  User,
  Clock,
  DollarSign,
  FileWarning,
  Stethoscope,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import DrawerBuilder from '@/components/DrawerBuilder';
import GlosaStatusBadge from '@/components/GlosaStatusBadge';
import {
  type Documentacao,
  type DocumentacaoCreate,
  type GlosaStatus,
  type DocType,
  GLOSA_STATUS_LABELS,
  GLOSA_STATUS_COLORS,
  DOC_TYPE_LABELS,
  MOCK_DOCS,
  MOCK_PATIENTS,
  formatCurrency,
} from '@/lib/doc-types';

// ─── Constants ───────────────────────────────────────────────────────────────

const GLOSA_STATUS_FILTERS: Array<'TODOS' | GlosaStatus> = [
  'TODOS',
  'pendente',
  'em_analise',
  'glosado',
  'liberado',
  'recorrido',
];

const DOC_TYPE_OPTIONS: Array<{ value: DocType; label: string }> = (
  Object.keys(DOC_TYPE_LABELS) as DocType[]
).map((key) => ({ value: key, label: DOC_TYPE_LABELS[key] }));

// ─── Skeleton ────────────────────────────────────────────────────────────────

function SkeletonHeader(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-3" role="status" aria-label="Carregando documentação">
      <div
        className="h-8 w-56 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div
        className="h-5 w-72 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

function SkeletonCard(): React.ReactElement {
  return (
    <div
      className="animate-pulse p-4 rounded-xl border space-y-3"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      role="status"
      aria-label="Carregando documento"
    >
      <div className="flex items-center gap-2">
        <div
          className="h-5 w-28 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="h-5 w-20 rounded ml-auto"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
      <div
        className="h-4 w-full rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div className="flex items-center gap-4">
        <div
          className="h-3 w-32 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="h-3 w-24 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
    </div>
  );
}

// ─── DocumentCard ────────────────────────────────────────────────────────────

interface DocumentCardProps {
  doc: Documentacao;
  onClick: () => void;
}

function DocumentCard({ doc, onClick }: DocumentCardProps): React.ReactElement {
  const typeLabel = DOC_TYPE_LABELS[doc.type];
  const showValor = doc.glosa_valor && doc.glosa_valor > 0;

  const truncatedContent =
    doc.content.length > 80
      ? doc.content.slice(0, 80) + '...'
      : doc.content;

  const formattedDate = new Date(doc.created_at).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 rounded-xl border transition-all hover:shadow-md focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      aria-label={`Documento: ${typeLabel} — ${GLOSA_STATUS_LABELS[doc.glosa_status]}`}
    >
      {/* Top row: type badge + glosa status */}
      <div className="flex items-center gap-2 mb-2">
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold"
          style={{
            backgroundColor: 'var(--semantic-surface-overlay)',
            color: 'var(--semantic-text-primary)',
          }}
        >
          <FileText className="w-3 h-3" aria-hidden="true" />
          {typeLabel}
        </span>
        <span className="flex-1" />
        <GlosaStatusBadge status={doc.glosa_status} valor={doc.glosa_valor} />
      </div>

      {/* Content preview */}
      <p
        className="text-sm leading-relaxed mb-2"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {truncatedContent}
      </p>

      {/* Bottom row: date + valor */}
      <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
        <span className="inline-flex items-center gap-1">
          <Calendar className="w-3 h-3" aria-hidden="true" />
          {formattedDate}
        </span>
        {showValor && (
          <span className="inline-flex items-center gap-1 font-semibold" style={{ color: 'var(--feedback-warning-icon-dark)' }}>
            <DollarSign className="w-3 h-3" aria-hidden="true" />
            {formatCurrency(doc.glosa_valor!)}
          </span>
        )}
      </div>
    </button>
  );
}

// ─── Detail Drawer ───────────────────────────────────────────────────────────

interface DetailDrawerProps {
  doc: Documentacao;
  patientName: string;
  onClose: () => void;
}

function DetailContent({ doc, patientName }: DetailDrawerProps): React.ReactElement {
  const typeLabel = DOC_TYPE_LABELS[doc.type];
  const statusLabel = GLOSA_STATUS_LABELS[doc.glosa_status];

  const formattedCreated = new Date(doc.created_at).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const formattedUpdated = doc.updated_at
    ? new Date(doc.updated_at).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

  return (
    <div className="space-y-5">
      {/* Metadata cards */}
      <div className="grid grid-cols-2 gap-3">
        <div
          className="p-3 rounded-lg border"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
        >
          <span
            className="text-xs font-semibold uppercase tracking-wider block mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Paciente
          </span>
          <span className="text-sm font-medium" style={{ color: 'var(--semantic-text-primary)' }}>
            {patientName}
          </span>
        </div>

        <div
          className="p-3 rounded-lg border"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
        >
          <span
            className="text-xs font-semibold uppercase tracking-wider block mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Tipo
          </span>
          <span className="text-sm font-medium" style={{ color: 'var(--semantic-text-primary)' }}>
            {typeLabel}
          </span>
        </div>

        <div
          className="p-3 rounded-lg border"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
        >
          <span
            className="text-xs font-semibold uppercase tracking-wider block mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Status Glosa
          </span>
          <div className="mt-0.5">
            <GlosaStatusBadge status={doc.glosa_status} valor={doc.glosa_valor} />
          </div>
        </div>

        <div
          className="p-3 rounded-lg border"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
        >
          <span
            className="text-xs font-semibold uppercase tracking-wider block mb-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Valor Glosado
          </span>
          <span
            className="text-sm font-semibold tabular-nums"
            style={{
              color: doc.glosa_valor && doc.glosa_valor > 0
                ? 'var(--feedback-warning-icon-dark)'
                : 'var(--semantic-text-secondary)',
            }}
          >
            {doc.glosa_valor && doc.glosa_valor > 0
              ? formatCurrency(doc.glosa_valor)
              : 'Nenhum'}
          </span>
        </div>
      </div>

      {/* Glosa motivo */}
      {doc.glosa_motivo && (
        <div
          className="p-4 rounded-xl border"
          style={{
            borderColor: 'var(--feedback-warning-border-dark)',
            backgroundColor: 'var(--feedback-warning-bg-dark)',
          }}
        >
          <div className="flex items-center gap-2 mb-2">
            <FileWarning
              className="w-4 h-4"
              style={{ color: 'var(--feedback-warning-icon-dark)' }}
              aria-hidden="true"
            />
            <span
              className="text-sm font-semibold"
              style={{ color: 'var(--feedback-warning-text-dark)' }}
            >
              Motivo da Glosa
            </span>
          </div>
          <p
            className="text-sm"
            style={{ color: 'var(--feedback-warning-text-dark)' }}
          >
            {doc.glosa_motivo}
          </p>
        </div>
      )}

      {/* Content */}
      <div>
        <span
          className="text-xs font-semibold uppercase tracking-wider block mb-2"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Conteúdo Completo
        </span>
        <div
          className="p-4 rounded-xl border text-sm leading-relaxed whitespace-pre-wrap"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-overlay)',
            color: 'var(--semantic-text-primary)',
          }}
        >
          {doc.content}
        </div>
      </div>

      {/* Dates */}
      <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
        <span className="inline-flex items-center gap-1">
          <Clock className="w-3 h-3" aria-hidden="true" />
          Criado: {formattedCreated}
        </span>
        {formattedUpdated && (
          <span className="inline-flex items-center gap-1">
            <Clock className="w-3 h-3" aria-hidden="true" />
            Atualizado: {formattedUpdated}
          </span>
        )}
      </div>
    </div>
  );
}

// ─── New Document Form ───────────────────────────────────────────────────────

interface NewDocFormProps {
  selectedPatient: string;
  onClose: () => void;
}

function NewDocForm({ selectedPatient, onClose }: NewDocFormProps): React.ReactElement {
  const [type, setType] = useState<DocType>('relatorio_medico');
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const canSubmit = type && content.trim().length > 0 && !submitting;

  const handleSubmit = useCallback(() => {
    if (!canSubmit) return;
    setSubmitting(true);

    // Mock submit
    const timer = setTimeout(() => {
      const newDoc: DocumentacaoCreate = {
        mpi_id: selectedPatient,
        type,
        content,
      };
      console.log('[Documentation] Novo documento:', newDoc);
      setSubmitting(false);
      setSuccess(true);

      // Close after delay
      setTimeout(() => onClose(), 1000);
    }, 600);

    return () => clearTimeout(timer);
  }, [canSubmit, selectedPatient, type, content, onClose]);

  return (
    <div className="space-y-4">
      {/* Type select */}
      <div>
        <label
          className="text-xs font-semibold uppercase tracking-wider block mb-1.5"
          style={{ color: 'var(--semantic-text-secondary)' }}
          htmlFor="doc-type"
        >
          Tipo de Documento
        </label>
        <select
          id="doc-type"
          value={type}
          onChange={(e) => setType(e.target.value as DocType)}
          className="w-full text-sm rounded-lg border px-3 py-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          aria-label="Tipo de documento"
        >
          {DOC_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Content textarea */}
      <div>
        <label
          className="text-xs font-semibold uppercase tracking-wider block mb-1.5"
          style={{ color: 'var(--semantic-text-secondary)' }}
          htmlFor="doc-content"
        >
          Conteúdo
        </label>
        <textarea
          id="doc-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={10}
          className="w-full text-sm rounded-lg border px-3 py-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1 resize-y"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          placeholder="Descreva o conteúdo do documento..."
          aria-label="Conteúdo do documento"
        />
      </div>

      {/* Submit button */}
      <div className="flex items-center gap-3 pt-2">
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: 'var(--action-primary-bg-light)',
            color: 'var(--action-primary-text-light)',
          }}
        >
          <Plus className="w-4 h-4" aria-hidden="true" />
          {submitting ? 'Salvando...' : 'Criar Documento'}
        </button>

        <button
          onClick={onClose}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 hover:opacity-80"
          style={{
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
            borderColor: 'var(--semantic-border-default)',
            borderWidth: '1px',
          }}
        >
          Cancelar
        </button>

        {success && (
          <span
            className="text-sm font-medium"
            style={{ color: 'var(--feedback-success-icon-light)' }}
          >
            Documento criado com sucesso!
          </span>
        )}
      </div>
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function DocumentationPage(): React.ReactElement {
  const [selectedPatient, setSelectedPatient] = useState<string>(
    MOCK_PATIENTS[0]!.mpiId,
  );
  const [filterStatus, setFilterStatus] = useState<'TODOS' | GlosaStatus>('TODOS');
  const [isLoading, setIsLoading] = useState(false);

  // Drawer state
  const [detailDoc, setDetailDoc] = useState<Documentacao | null>(null);
  const [newDocOpen, setNewDocOpen] = useState(false);

  // ─── Derived state ───────────────────────────────────────────────────────

  const selectedPatientData = useMemo(
    () => MOCK_PATIENTS.find((p) => p.mpiId === selectedPatient),
    [selectedPatient],
  );

  const filteredDocs = useMemo(() => {
    let docs = MOCK_DOCS.filter((d) => d.mpi_id === selectedPatient);
    if (filterStatus !== 'TODOS') {
      docs = docs.filter((d) => d.glosa_status === filterStatus);
    }
    return docs;
  }, [selectedPatient, filterStatus]);

  // Status counters for tabs
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { TODOS: 0 };
    for (const status of GLOSA_STATUS_FILTERS) {
      if (status === 'TODOS') {
        counts['TODOS'] = MOCK_DOCS.filter((d) => d.mpi_id === selectedPatient).length;
      } else {
        counts[status] = MOCK_DOCS.filter(
          (d) => d.mpi_id === selectedPatient && d.glosa_status === status,
        ).length;
      }
    }
    return counts;
  }, [selectedPatient]);

  // ─── Loading state ───────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto space-y-6">
          <SkeletonHeader />
          {[1, 2, 3].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </Layout>
    );
  }

  // ─── Main render ─────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-3xl mx-auto space-y-6 pb-12">
          {/* ── Header ─────────────────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: 'var(--feedback-info-bg-dark)',
                    color: 'var(--feedback-info-icon-dark)',
                  }}
                >
                  <FileText className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Documentação
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Registros clínicos e faturamento
              </p>
            </div>

            {/* Patient selector */}
            <div className="flex items-center gap-2">
              <User
                className="w-4 h-4 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <select
                value={selectedPatient}
                onChange={(e) => setSelectedPatient(e.target.value)}
                className="text-sm rounded-lg border px-3 py-2 min-w-[200px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
                aria-label="Selecionar paciente"
              >
                {MOCK_PATIENTS.map((p) => (
                  <option key={p.mpiId} value={p.mpiId}>
                    {p.name} — {p.bed}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* ── Patient info bar ──────────────────────────────────────── */}
          {selectedPatientData && (
            <div
              className="flex items-center gap-3 px-4 py-3 rounded-xl border text-sm"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <Stethoscope
                className="w-4 h-4 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <span style={{ color: 'var(--semantic-text-primary)' }}>
                <strong>{selectedPatientData.name}</strong>
              </span>
              <span
                className="tabular-nums"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                MPI: {selectedPatientData.mpiId}
              </span>
              <span
                className="tabular-nums ml-auto"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Leito: {selectedPatientData.bed}
              </span>
            </div>
          )}


          {/* ── Actions bar ───────────────────────────────────────────── */}
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <button
              onClick={() => setNewDocOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
              style={{
                backgroundColor: 'var(--action-primary-bg-light)',
                color: 'var(--action-primary-text-light)',
              }}
            >
              <Plus className="w-4 h-4" aria-hidden="true" />
              Novo Documento
            </button>

          </div>

          {/* ── Status filter tabs ───────────────────────────────────── */}
          <div
            className="flex items-center gap-1 overflow-x-auto p-1 rounded-xl"
            style={{
              backgroundColor: 'var(--semantic-surface-overlay)',
              borderColor: 'var(--semantic-border-default)',
              borderWidth: '1px',
            }}
            role="tablist"
            aria-label="Filtrar por status de glosa"
          >
            {GLOSA_STATUS_FILTERS.map((status) => {
              const isActive = filterStatus === status;
              const label = status === 'TODOS' ? 'Todos' : GLOSA_STATUS_LABELS[status];
              const count = statusCounts[status] ?? 0;

              return (
                <button
                  key={status}
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setFilterStatus(status)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  style={{
                    backgroundColor: isActive ? 'var(--semantic-surface-raised)' : 'transparent',
                    color: isActive
                      ? 'var(--semantic-text-primary)'
                      : 'var(--semantic-text-secondary)',
                    boxShadow: isActive
                      ? '0 1px 3px rgba(0,0,0,0.1)'
                      : 'none',
                  }}
                >
                  {label}
                  <span
                    className="inline-flex items-center justify-center min-w-[20px] h-5 px-1 rounded-full text-[10px] font-bold tabular-nums"
                    style={{
                      backgroundColor: isActive
                        ? 'var(--semantic-surface-overlay)'
                        : 'var(--semantic-surface-raised)',
                      color: isActive
                        ? 'var(--semantic-text-primary)'
                        : 'var(--semantic-text-secondary)',
                    }}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* ── Document list ─────────────────────────────────────────── */}
          <div>
            <h2
              className="text-sm font-semibold uppercase tracking-wider mb-3"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {filterStatus === 'TODOS'
                ? 'Todos os Documentos'
                : GLOSA_STATUS_LABELS[filterStatus]}
              <span className="ml-2 font-normal normal-case">
                ({filteredDocs.length})
              </span>
            </h2>

            {filteredDocs.length === 0 ? (
              /* ── Empty state ───────────────────────────────────── */
              <div
                className="text-center py-12 px-4 rounded-xl border"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
              >
                <FileText
                  className="w-12 h-12 mx-auto mb-3"
                  style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
                  aria-hidden="true"
                />
                <p
                  className="text-sm font-medium mb-1"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Nenhum documento encontrado
                </p>
                <p
                  className="text-xs"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {filterStatus === 'TODOS'
                    ? 'Este paciente não possui documentos registrados.'
                    : `Nenhum documento com status "${GLOSA_STATUS_LABELS[filterStatus]}".`}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredDocs.map((doc) => (
                  <DocumentCard
                    key={doc.id}
                    doc={doc}
                    onClick={() => setDetailDoc(doc)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* ── Detail Drawer ─────────────────────────────────────────── */}
          <DrawerBuilder
            open={detailDoc !== null}
            onClose={() => setDetailDoc(null)}
            title={detailDoc ? DOC_TYPE_LABELS[detailDoc.type] : ''}
            size="lg"
          >
            {detailDoc && (
              <DetailContent
                doc={detailDoc}
                patientName={selectedPatientData?.name ?? 'Paciente'}
                onClose={() => setDetailDoc(null)}
              />
            )}
          </DrawerBuilder>

          {/* ── New Document Drawer ───────────────────────────────────── */}
          <DrawerBuilder
            open={newDocOpen}
            onClose={() => setNewDocOpen(false)}
            title="Novo Documento"
            size="md"
          >
            <NewDocForm
              selectedPatient={selectedPatient}
              onClose={() => setNewDocOpen(false)}
            />
          </DrawerBuilder>
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
