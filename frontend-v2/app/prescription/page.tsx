'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Pill,
  Plus,
  AlertTriangle,
  Loader2,
  CheckCircle,
  Clock,
  XCircle,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import DrawerBuilder from '@/components/DrawerBuilder';
import PrescriptionCard from '@/components/PrescriptionCard';
import type {
  Prescription,
  PrescriptionStatus,
  PrescriptionCreate,
  DrugInteraction,
} from '@/lib/prescription-types';
import {
  MOCK_PRESCRIPTIONS,
  MOCK_PATIENTS,
  MOCK_DRUG_INTERACTIONS,
  ROUTE_LABELS,
  STATUS_LABELS,
  findInteraction,
  type PrescriptionRoute,
} from '@/lib/prescription-types';

// ─── Route options for select ────────────────────────────────────────────────

const ROUTE_OPTIONS: PrescriptionRoute[] = ['IV', 'IM', 'SC', 'PO', 'SN', 'IT', 'TOP', 'INAL'];

// ─── Status Tab Definition ───────────────────────────────────────────────────

interface StatusTab {
  key: PrescriptionStatus | 'all';
  label: string;
}

const STATUS_TABS: StatusTab[] = [
  { key: 'active', label: 'Ativas' },
  { key: 'completed', label: 'Concluídas' },
  { key: 'discontinued', label: 'Descontinuadas' },
  { key: 'all', label: 'Todas' },
];

// ─── Loading Skeleton ────────────────────────────────────────────────────────

function LoadingSkeleton() {
  return (
    <div className="space-y-4" role="status" aria-label="Carregando prescrições">
      {Array.from({ length: 4 }).map((_, i) => (
        <PrescriptionCard
          key={i}
          prescription={{
            id: `skel-${i}`,
            mpi_id: '',
            drug: '',
            dose: 0,
            unit: '',
            route: 'IV',
            frequency: '',
            start_time: '',
            status: 'active',
            prescribed_by: '',
            created_at: new Date().toISOString(),
          }}
          isLoading
        />
      ))}
    </div>
  );
}

// ─── Error Display ───────────────────────────────────────────────────────────

function ErrorDisplay({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="border rounded-xl p-6 m-4"
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
        <div className="min-w-0">
          <h2 className="font-semibold text-lg">Erro ao carregar prescrições</h2>
          <p className="text-sm mt-1 opacity-90">{message}</p>
          <button
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              color: 'var(--semantic-text-primary)',
              border: '1px solid var(--semantic-border-default)',
            }}
          >
            <Loader2 className="w-4 h-4" aria-hidden="true" />
            Tentar novamente
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Empty State ─────────────────────────────────────────────────────────────

function EmptyState({ activeTab }: { activeTab: PrescriptionStatus | 'all' }) {
  const label = activeTab === 'all' ? '' : STATUS_LABELS[activeTab].toLowerCase() + 's';

  return (
    <div className="text-center py-16" role="status">
      <Pill
        className="w-16 h-16 mx-auto mb-4"
        style={{ color: 'var(--semantic-text-secondary)', opacity: 0.3 }}
        aria-hidden="true"
      />
      <p
        className="text-lg font-medium"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {activeTab === 'all'
          ? 'Nenhuma prescrição cadastrada'
          : `Nenhuma prescrição ${label}`}
      </p>
      <p
        className="text-sm mt-1"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        Clique em &quot;Nova Prescrição&quot; para adicionar um medicamento.
      </p>
    </div>
  );
}

// ─── Prescription Form (inside DrawerBuilder) ────────────────────────────────

interface PrescriptionFormProps {
  onSubmit: (data: PrescriptionCreate) => void;
  onCancel: () => void;
}

function PrescriptionForm({ onSubmit, onCancel }: PrescriptionFormProps) {
  const [formData, setFormData] = useState<PrescriptionCreate>({
    mpi_id: MOCK_PATIENTS[0]?.mpi_id ?? '',
    drug: '',
    dose: 0,
    unit: 'mg',
    route: 'IV',
    frequency: '',
    start_time: new Date().toISOString().slice(0, 16),
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateField = useCallback(
    <K extends keyof PrescriptionCreate>(field: K, value: PrescriptionCreate[K]) => {
      setFormData((prev) => ({ ...prev, [field]: value }));
      // Clear error on change
      if (errors[field]) {
        setErrors((prev) => {
          const next = { ...prev };
          delete next[field];
          return next;
        });
      }
    },
    [errors],
  );

  const validate = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.drug.trim()) {
      newErrors.drug = 'Nome do fármaco é obrigatório';
    }
    if (!formData.dose || formData.dose <= 0) {
      newErrors.dose = 'Dose deve ser maior que zero';
    }
    if (!formData.route) {
      newErrors.route = 'Via de administração é obrigatória';
    }
    if (!formData.frequency.trim()) {
      newErrors.frequency = 'Frequência é obrigatória';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!validate()) return;

      setIsSubmitting(true);
      // Simula chamada à API
      await new Promise((r) => setTimeout(r, 800));
      onSubmit({ ...formData });
      setIsSubmitting(false);
    },
    [validate, onSubmit, formData],
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      {/* Patient selector */}
      <div>
        <label
          className="block text-sm font-semibold mb-1.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Paciente
        </label>
        <select
          value={formData.mpi_id}
          onChange={(e) => updateField('mpi_id', e.target.value)}
          className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
            color: 'var(--semantic-text-primary)',
          }}
        >
          {MOCK_PATIENTS.map((p) => (
            <option key={p.mpi_id} value={p.mpi_id}>
              {p.name} — {p.bed}
            </option>
          ))}
        </select>
      </div>

      {/* Drug name */}
      <div>
        <label
          className="block text-sm font-semibold mb-1.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Fármaco <span style={{ color: 'var(--clinical-severity-critical-signal)' }}>*</span>
        </label>
        <input
          type="text"
          value={formData.drug}
          onChange={(e) => updateField('drug', e.target.value)}
          placeholder="Ex: Ceftriaxona, Meropenem..."
          className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            borderColor: errors.drug
              ? 'var(--clinical-severity-critical-signal)'
              : 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
            color: 'var(--semantic-text-primary)',
          }}
          aria-invalid={!!errors.drug}
          aria-describedby={errors.drug ? 'drug-error' : undefined}
        />
        {errors.drug && (
          <p
            id="drug-error"
            className="text-xs mt-1"
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
            role="alert"
          >
            {errors.drug}
          </p>
        )}
      </div>

      {/* Dose + Unit (inline) */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label
            className="block text-sm font-semibold mb-1.5"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Dose <span style={{ color: 'var(--clinical-severity-critical-signal)' }}>*</span>
          </label>
          <input
            type="number"
            value={formData.dose || ''}
            onChange={(e) => updateField('dose', parseFloat(e.target.value) || 0)}
            placeholder="2"
            min={0}
            step="any"
            className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{
              borderColor: errors.dose
                ? 'var(--clinical-severity-critical-signal)'
                : 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-canvas)',
              color: 'var(--semantic-text-primary)',
            }}
            aria-invalid={!!errors.dose}
            aria-describedby={errors.dose ? 'dose-error' : undefined}
          />
          {errors.dose && (
            <p
              id="dose-error"
              className="text-xs mt-1"
              style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
              role="alert"
            >
              {errors.dose}
            </p>
          )}
        </div>
        <div>
          <label
            className="block text-sm font-semibold mb-1.5"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Unidade
          </label>
          <select
            value={formData.unit}
            onChange={(e) => updateField('unit', e.target.value)}
            className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-canvas)',
              color: 'var(--semantic-text-primary)',
            }}
          >
            <option value="mg">mg</option>
            <option value="g">g</option>
            <option value="mcg">mcg</option>
            <option value="UI">UI</option>
            <option value="mcg/kg/min">mcg/kg/min</option>
            <option value="mg/h">mg/h</option>
            <option value="UI/h">UI/h</option>
            <option value="mL">mL</option>
          </select>
        </div>
      </div>

      {/* Route */}
      <div>
        <label
          className="block text-sm font-semibold mb-1.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Via de Administração{' '}
          <span style={{ color: 'var(--clinical-severity-critical-signal)' }}>*</span>
        </label>
        <select
          value={formData.route}
          onChange={(e) => updateField('route', e.target.value as PrescriptionRoute)}
          className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            borderColor: errors.route
              ? 'var(--clinical-severity-critical-signal)'
              : 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
            color: 'var(--semantic-text-primary)',
          }}
          aria-invalid={!!errors.route}
          aria-describedby={errors.route ? 'route-error' : undefined}
        >
          {ROUTE_OPTIONS.map((r) => (
            <option key={r} value={r}>
              {ROUTE_LABELS[r]} ({r})
            </option>
          ))}
        </select>
        {errors.route && (
          <p
            id="route-error"
            className="text-xs mt-1"
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
            role="alert"
          >
            {errors.route}
          </p>
        )}
      </div>

      {/* Frequency */}
      <div>
        <label
          className="block text-sm font-semibold mb-1.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Frequência <span style={{ color: 'var(--clinical-severity-critical-signal)' }}>*</span>
        </label>
        <input
          type="text"
          value={formData.frequency}
          onChange={(e) => updateField('frequency', e.target.value)}
          placeholder="Ex: 8/8h, 12/12h, Contínua"
          className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            borderColor: errors.frequency
              ? 'var(--clinical-severity-critical-signal)'
              : 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
            color: 'var(--semantic-text-primary)',
          }}
          aria-invalid={!!errors.frequency}
          aria-describedby={errors.frequency ? 'frequency-error' : undefined}
        />
        {errors.frequency && (
          <p
            id="frequency-error"
            className="text-xs mt-1"
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
            role="alert"
          >
            {errors.frequency}
          </p>
        )}
      </div>

      {/* Start time */}
      <div>
        <label
          className="block text-sm font-semibold mb-1.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Início
        </label>
        <input
          type="datetime-local"
          value={formData.start_time ?? ''}
          onChange={(e) => updateField('start_time', e.target.value)}
          className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
            color: 'var(--semantic-text-primary)',
          }}
        />
      </div>

      {/* Notes */}
      <div>
        <label
          className="block text-sm font-semibold mb-1.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Observações
        </label>
        <textarea
          value={formData.notes ?? ''}
          onChange={(e) => updateField('notes', e.target.value)}
          placeholder="Instruções clínicas, ajustes..."
          rows={3}
          className="w-full rounded-lg border px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
            color: 'var(--semantic-text-primary)',
          }}
        />
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors"
          style={{
            color: 'var(--semantic-text-secondary)',
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'transparent',
          }}
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all disabled:opacity-50"
          style={{
            backgroundColor: 'var(--clinical-severity-normal-fill)',
            color: 'var(--clinical-severity-normal-on-fill)',
          }}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              Salvando...
            </>
          ) : (
            <>
              <CheckCircle className="w-4 h-4" aria-hidden="true" />
              Salvar Prescrição
            </>
          )}
        </button>
      </div>
    </form>
  );
}

// ─── Global Interaction Alert Banner ─────────────────────────────────────────

function GlobalInteractionAlert({ interactions }: { interactions: DrugInteraction[] }) {
  if (interactions.length === 0) return null;

  return (
    <div
      role="alert"
      aria-live="polite"
      className="flex items-start gap-3 px-4 py-3 rounded-lg border mb-6"
      style={{
        backgroundColor: 'var(--clinical-severity-urgent-wash)',
        borderColor: 'var(--clinical-severity-urgent-signal)',
        color: 'var(--clinical-severity-urgent-on-surface)',
      }}
    >
      <AlertTriangle
        className="w-5 h-5 flex-shrink-0 mt-0.5"
        style={{ color: 'var(--clinical-severity-urgent-signal)' }}
        aria-hidden="true"
      />
      <div className="min-w-0">
        <p className="font-semibold text-sm">
          Alerta de Interação Medicamentosa
        </p>
        <p className="text-xs mt-0.5">
          {interactions.length === 1
            ? `${interactions[0]?.drugPair.join(' + ')}: ${interactions[0]?.description ?? ''}`
            : `${interactions.length} interações medicamentosas detectadas. Verifique os cards com ícone de alerta.`}
        </p>
      </div>
    </div>
  );
}

// ─── Toast / Notification (simple inline) ────────────────────────────────────

function ToastNotification({
  message,
  visible,
}: {
  message: string;
  visible: boolean;
}) {
  if (!visible) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2 animate-[fadeIn_200ms_ease-out]"
      style={{
        backgroundColor: 'var(--clinical-severity-normal-fill)',
        color: 'var(--clinical-severity-normal-on-fill)',
      }}
    >
      <CheckCircle className="w-4 h-4" aria-hidden="true" />
      {message}
    </div>
  );
}

// ─── Page Component ──────────────────────────────────────────────────────────

function PrescriptionPage() {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>(MOCK_PRESCRIPTIONS);
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<PrescriptionStatus | 'all'>('active');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; visible: boolean }>({
    message: '',
    visible: false,
  });

  // ── Toast helper ───────────────────────────────────────────────────────────
  const showToast = useCallback((message: string) => {
    setToast({ message, visible: true });
    setTimeout(() => setToast({ message: '', visible: false }), 3500);
  }, []);

  // ── Status change handler ──────────────────────────────────────────────────
  const handleStatusChange = useCallback(
    (id: string, newStatus: PrescriptionStatus) => {
      setPrescriptions((prev) =>
        prev.map((rx) =>
          rx.id === id
            ? { ...rx, status: newStatus, end_time: newStatus !== 'active' ? new Date().toISOString() : undefined }
            : rx,
        ),
      );
      const label = STATUS_LABELS[newStatus];
      showToast(`Prescrição marcada como "${label}"`);
    },
    [showToast],
  );

  // ── New prescription handler ───────────────────────────────────────────────
  const handleNewPrescription = useCallback(
    (data: PrescriptionCreate) => {
      const newRx: Prescription = {
        id: `rx-${Date.now()}`,
        mpi_id: data.mpi_id,
        drug: data.drug.trim(),
        dose: data.dose,
        unit: data.unit,
        route: data.route,
        frequency: data.frequency.trim(),
        start_time: data.start_time ?? new Date().toISOString(),
        status: 'active',
        notes: data.notes?.trim() || undefined,
        prescribed_by: 'Você (mock)',
        created_at: new Date().toISOString(),
      };

      setPrescriptions((prev) => [newRx, ...prev]);
      setDrawerOpen(false);
      showToast(`Prescrição de ${newRx.drug} criada com sucesso!`);
    },
    [showToast],
  );

  // ── Simulate loading & error ───────────────────────────────────────────────
  const simulateLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
    setTimeout(() => setIsLoading(false), 1500);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  // ── Filtered prescriptions ─────────────────────────────────────────────────
  const filteredPrescriptions = useMemo(() => {
    let filtered = prescriptions;

    // Filter by patient
    if (selectedPatient) {
      filtered = filtered.filter((rx) => rx.mpi_id === selectedPatient);
    }

    // Filter by status tab
    if (activeTab !== 'all') {
      filtered = filtered.filter((rx) => rx.status === activeTab);
    }

    return filtered;
  }, [prescriptions, selectedPatient, activeTab]);

  // ── Drug interactions for the global banner ────────────────────────────────
  const activeInteractions = useMemo(() => {
    // Only for active prescriptions
    const activeDrugs = prescriptions
      .filter((rx) => rx.status === 'active')
      .map((rx) => rx.drug);

    return MOCK_DRUG_INTERACTIONS.filter((ix) => {
      const [a, b] = ix.drugPair;
      return activeDrugs.some((d) => d === a) && activeDrugs.some((d) => d === b);
    });
  }, [prescriptions]);

  // ── Counts ─────────────────────────────────────────────────────────────────
  const counts = useMemo(
    () => ({
      active: prescriptions.filter((rx) => rx.status === 'active').length,
      completed: prescriptions.filter((rx) => rx.status === 'completed').length,
      discontinued: prescriptions.filter((rx) => rx.status === 'discontinued').length,
      total: prescriptions.length,
    }),
    [prescriptions],
  );

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* ── Header ───────────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1
              className="text-2xl font-bold flex items-center gap-2"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <Pill className="w-6 h-6" aria-hidden="true" />
              Prescrições
            </h1>
            <p className="text-sm mt-1" style={{ color: 'var(--semantic-text-secondary)' }}>
              {counts.total} prescrições &middot; {counts.active} ativas &middot;{' '}
              {counts.completed} concluídas &middot; {counts.discontinued} descontinuadas
            </p>
          </div>

          <div className="flex gap-2">
            {/* Demo: simulate loading */}
            <button
              onClick={simulateLoading}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-secondary)',
                borderColor: 'var(--semantic-border-default)',
              }}
              aria-label="Simular carregamento"
            >
              <Loader2 className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} aria-hidden="true" />
              Loading
            </button>
            {/* New prescription button */}
            <button
              onClick={() => setDrawerOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all"
              style={{
                backgroundColor: 'var(--clinical-severity-normal-fill)',
                color: 'var(--clinical-severity-normal-on-fill)',
              }}
              aria-label="Nova prescrição"
            >
              <Plus className="w-4 h-4" aria-hidden="true" />
              Nova Prescrição
            </button>
          </div>
        </div>

        {/* ── Global Interaction Alert ──────────────────────────────────────── */}
        {activeInteractions.length > 0 && (
          <GlobalInteractionAlert interactions={activeInteractions} />
        )}

        {/* ── Error ────────────────────────────────────────────────────────── */}
        {error && (
          <ErrorDisplay
            message={error}
            onRetry={() => {
              clearError();
              simulateLoading();
            }}
          />
        )}

        {/* ── Loading ──────────────────────────────────────────────────────── */}
        {isLoading && <LoadingSkeleton />}

        {/* ── Main Content ─────────────────────────────────────────────────── */}
        {!error && !isLoading && (
          <>
            {/* Patient Selector + Status Tabs */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
              {/* Patient dropdown */}
              <div
                className="flex items-center gap-2 rounded-lg border px-3 py-2"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
              >
                <Pill className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
                <select
                  value={selectedPatient ?? ''}
                  onChange={(e) => setSelectedPatient(e.target.value || null)}
                  className="text-sm bg-transparent border-none outline-none"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <option value="">Todos os pacientes</option>
                  {MOCK_PATIENTS.map((p) => (
                    <option key={p.mpi_id} value={p.mpi_id}>
                      {p.name} ({p.bed})
                    </option>
                  ))}
                </select>
              </div>

              {/* Status tabs */}
              <div
                className="flex overflow-x-auto border-b gap-1 flex-1"
                style={{ borderColor: 'var(--semantic-border-default)' }}
                role="tablist"
                aria-label="Filtrar por status da prescrição"
              >
                {STATUS_TABS.map((tab) => {
                  const isActiveTab = activeTab === tab.key;
                  const count =
                    tab.key === 'all'
                      ? counts.total
                      : counts[tab.key as keyof typeof counts];

                  // Status → color mapping for active tab indicator
                  let activeColor = 'var(--semantic-text-primary)';
                  let activeBorderColor = 'var(--semantic-text-primary)';
                  if (tab.key === 'active') {
                    activeColor = 'var(--clinical-severity-normal-on-surface)';
                    activeBorderColor = 'var(--clinical-severity-normal-signal)';
                  } else if (tab.key === 'completed') {
                    activeColor = 'var(--clinical-severity-watch-on-surface)';
                    activeBorderColor = 'var(--clinical-severity-watch-signal)';
                  }

                  // Icon per tab
                  const TabIcon =
                    tab.key === 'active'
                      ? Clock
                      : tab.key === 'completed'
                        ? CheckCircle
                        : tab.key === 'discontinued'
                          ? XCircle
                          : Pill;

                  return (
                    <button
                      key={tab.key}
                      role="tab"
                      aria-selected={isActiveTab}
                      aria-controls={`panel-${tab.key}`}
                      id={`tab-${tab.key}`}
                      tabIndex={isActiveTab ? 0 : -1}
                      onClick={() => setActiveTab(tab.key)}
                      className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium whitespace-nowrap rounded-t-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset ${
                        isActiveTab ? '-mb-[1px] border-b-2' : 'border-b-2 border-transparent'
                      }`}
                      style={{
                        color: isActiveTab ? activeColor : 'var(--semantic-text-secondary)',
                        backgroundColor: isActiveTab
                          ? 'var(--semantic-surface-canvas)'
                          : 'transparent',
                        borderBottomColor: isActiveTab
                          ? activeBorderColor
                          : 'transparent',
                      }}
                    >
                      <TabIcon className="w-3.5 h-3.5" aria-hidden="true" />
                      {tab.label}
                      <span
                        className="ml-1 text-xs rounded-full px-1.5 py-0.5"
                        style={{
                          backgroundColor: isActiveTab
                            ? 'var(--semantic-surface-overlay)'
                            : 'transparent',
                        }}
                      >
                        {count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* ── Prescription Cards ───────────────────────────────────────── */}
            {filteredPrescriptions.length === 0 ? (
              <EmptyState activeTab={activeTab} />
            ) : (
              <div
                id={`panel-${activeTab}`}
                role="tabpanel"
                aria-labelledby={`tab-${activeTab}`}
                className="space-y-4"
              >
                {filteredPrescriptions.map((rx) => {
                  const interaction = findInteraction(rx.drug, MOCK_DRUG_INTERACTIONS);
                  return (
                    <PrescriptionCard
                      key={rx.id}
                      prescription={rx}
                      onStatusChange={handleStatusChange}
                      interaction={interaction}
                    />
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>

      {/* ── New Prescription Drawer ─────────────────────────────────────────── */}
      <DrawerBuilder
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Nova Prescrição"
        size="md"
      >
        <PrescriptionForm
          onSubmit={handleNewPrescription}
          onCancel={() => setDrawerOpen(false)}
        />
      </DrawerBuilder>

      {/* ── Toast Notification ──────────────────────────────────────────────── */}
      <ToastNotification message={toast.message} visible={toast.visible} />
    </Layout>
  );
}

// ─── Page Export with ErrorBoundary ──────────────────────────────────────────

export default function PrescriptionPageWithErrorBoundary() {
  return (
    <ErrorBoundary
      fallback={
        <div
          className="flex items-center justify-center min-h-[50vh]"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 mx-auto mb-3" style={{ opacity: 0.4 }} aria-hidden="true" />
            <p className="text-lg font-medium">Erro inesperado no módulo de prescrições</p>
            <p className="text-sm mt-1">Tente recarregar a página.</p>
          </div>
        </div>
      }
    >
      <PrescriptionPage />
    </ErrorBoundary>
  );
}
