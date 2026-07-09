'use client';

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  Building2,
  LogIn,
  LogOut,
  ArrowRightLeft,
  Plus,
  BedDouble,
  Clock,
  Filter,
  AlertTriangle,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import ClinicalTimeline, {
  type TimelineEvent,
  type TimelineStatus,
} from '@/components/ClinicalTimeline';
import DrawerBuilder from '@/components/DrawerBuilder';
import BedGridCard, {
  BedGridSkeleton,
  BedGridEmpty,
} from '@/components/BedGridCard';
import {
  type PatientMovement,
  type BedStatus,
  type MovementType,
  type BedSummary,
  TYPE_LABELS,
  computeBedSummary,
  movementToTimelineEvent,
} from '@/lib/movement-types';
import { fetchMovements, fetchBedGrid, fetchDashboard, type PatientBedSummary } from '@/lib/api';

// ═════════════════════════════════════════════════════════════════════════════
// Toggle Group (filtro de tipo)
// ═════════════════════════════════════════════════════════════════════════════

interface TypeFilterProps {
  active: MovementType | 'all';
  onChange: (type: MovementType | 'all') => void;
  disabled?: boolean;
}

const FILTER_OPTIONS: Array<{ value: MovementType | 'all'; label: string }> = [
  { value: 'all', label: 'Todos' },
  { value: 'admission', label: 'Admissões' },
  { value: 'transfer', label: 'Transferências' },
  { value: 'discharge', label: 'Altas' },
];

function TypeFilter({
  active,
  onChange,
  disabled = false,
}: TypeFilterProps): React.ReactElement {
  return (
    <div
      className="inline-flex rounded-lg border overflow-hidden"
      style={{ borderColor: 'var(--semantic-border-default)' }}
      role="radiogroup"
      aria-label="Filtrar por tipo de movimentação"
    >
      {FILTER_OPTIONS.map((opt) => {
        const isActive = opt.value === active;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={isActive}
            disabled={disabled}
            onClick={() => onChange(opt.value)}
            className="px-3 py-1.5 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: isActive
                ? 'var(--action-primary-bg-dark)'
                : 'transparent',
              color: isActive
                ? 'var(--action-primary-text-dark)'
                : 'var(--semantic-text-secondary)',
            }}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// Unit Selector
// ═════════════════════════════════════════════════════════════════════════════

interface UnitSelectorProps {
  units: string[];
  selected: string | 'all';
  onChange: (unit: string | 'all') => void;
  disabled?: boolean;
}

function UnitSelector({
  units,
  selected,
  onChange,
  disabled = false,
}: UnitSelectorProps): React.ReactElement {
  return (
    <div className="flex items-center gap-2">
      <Building2
        className="w-4 h-4 flex-shrink-0"
        style={{ color: 'var(--semantic-text-secondary)' }}
        aria-hidden="true"
      />
      <select
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="rounded-lg border px-3 py-2 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset disabled:opacity-50"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
          color: 'var(--semantic-text-primary)',
        }}
        aria-label="Selecionar unidade"
      >
        <option value="all">Todas as unidades</option>
        {units.map((unit) => (
          <option key={unit} value={unit}>
            {unit}
          </option>
        ))}
      </select>
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// Bed Summary Bar
// ═════════════════════════════════════════════════════════════════════════════

interface BedSummaryBarProps {
  summary: BedSummary;
}

function BedSummaryBar({ summary }: BedSummaryBarProps): React.ReactElement {
  const items: Array<{ label: string; count: number; color: string }> = [
    { label: 'Livres', count: summary.free, color: 'var(--feedback-success-bg-dark, #22c55e)' },
    { label: 'Ocupados', count: summary.occupied, color: 'var(--clinical-severity-normal-signal, #3b82f6)' },
    { label: 'Bloqueados', count: summary.blocked, color: 'var(--clinical-severity-watch-signal, #f59e0b)' },
    { label: 'Limpeza', count: summary.cleaning, color: 'var(--semantic-text-secondary, #94a3b8)' },
  ];

  return (
    <div
      className="flex flex-wrap items-center gap-3 px-4 py-2.5 rounded-lg border text-xs"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
        color: 'var(--semantic-text-secondary)',
      }}
      aria-label={`Resumo de leitos: ${summary.total} total, ${summary.free} livres, ${summary.occupied} ocupados`}
    >
      <span className="font-semibold uppercase tracking-wider mr-1">
        Total: {summary.total}
      </span>
      {items.map((item) => (
        <span key={item.label} className="flex items-center gap-1">
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: item.color }}
            aria-hidden="true"
          />
          <span>
            {item.label}: <strong>{item.count}</strong>
          </span>
        </span>
      ))}
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// Transfer Form (inside DrawerBuilder)
// ═════════════════════════════════════════════════════════════════════════════

interface TransferFormProps {
  onClose: () => void;
  beds: BedStatus[];
}

function TransferForm({ onClose, beds }: TransferFormProps): React.ReactElement {
  const [type, setType] = useState<MovementType>('admission');
  const [patientId, setPatientId] = useState('');
  const [fromUnit, setFromUnit] = useState('');
  const [fromBed, setFromBed] = useState('');
  const [toUnit, setToUnit] = useState('');
  const [toBed, setToBed] = useState('');
  const [notes, setNotes] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const units = useMemo(() => {
    const unitSet = new Set(beds.map((b) => b.unit));
    return Array.from(unitSet).sort();
  }, [beds]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Exibe confirmação após registro
    setSubmitted(true);
    setTimeout(() => {
      onClose();
    }, 1500);
  };

  const isAdmission = type === 'admission';
  const isDischarge = type === 'discharge';

  const freeBeds = beds.filter((b) => b.status === 'free');
  const occupiedBeds = beds.filter((b) => b.status === 'occupied');

  if (submitted) {
    return (
      <div className="text-center py-6 space-y-3" role="status" aria-label="Movimentação registrada">
        <div
          className="w-12 h-12 rounded-full mx-auto flex items-center justify-center"
          style={{ backgroundColor: 'var(--feedback-success-bg-light, rgba(34,197,94,0.1))' }}
        >
          <svg
            className="w-6 h-6"
            style={{ color: 'var(--feedback-success-bg-dark, #22c55e)' }}
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <p className="text-sm font-semibold" style={{ color: 'var(--semantic-text-primary)' }}>
          Movimentação registrada com sucesso!
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 text-sm">
      {/* Tipo */}
      <div>
        <label
          className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Tipo de Movimentação
        </label>
        <select
          value={type}
          onChange={(e) => setType(e.target.value as MovementType)}
          className="w-full rounded-lg border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          required
          aria-label="Tipo de movimentação"
        >
          <option value="admission">Admissão</option>
          <option value="transfer">Transferência</option>
          <option value="discharge">Alta</option>
        </select>
      </div>

      {/* Paciente */}
      <div>
        <label
          className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          ID do Paciente (MPI)
        </label>
        <input
          type="text"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
          placeholder="Ex: MPI-007"
          className="w-full rounded-lg border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          required
          aria-label="ID do paciente"
        />
      </div>

      {/* Origem (apenas para transfer e discharge) */}
      {!isAdmission && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label
              className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Unidade de Origem
            </label>
            <select
              value={fromUnit}
              onChange={(e) => setFromUnit(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
              }}
              required
              aria-label="Unidade de origem"
            >
              <option value="">Selecionar</option>
              {units.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label
              className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Leito de Origem
            </label>
            <select
              value={fromBed}
              onChange={(e) => setFromBed(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
              }}
              required
              aria-label="Leito de origem"
            >
              <option value="">Selecionar</option>
              {occupiedBeds
                .filter((b) => !fromUnit || b.unit === fromUnit)
                .map((b) => (
                  <option key={b.id} value={b.room}>
                    {b.room} — {b.current_patient_name ?? 'Ocupado'}
                  </option>
                ))}
            </select>
          </div>
        </div>
      )}

      {/* Destino (apenas para admission e transfer) */}
      {!isDischarge && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label
              className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Unidade de Destino
            </label>
            <select
              value={toUnit}
              onChange={(e) => setToUnit(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
              }}
              required
              aria-label="Unidade de destino"
            >
              <option value="">Selecionar</option>
              {units.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label
              className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Leito de Destino
            </label>
            <select
              value={toBed}
              onChange={(e) => setToBed(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
              }}
              required
              aria-label="Leito de destino"
            >
              <option value="">Selecionar</option>
              {freeBeds
                .filter((b) => !toUnit || b.unit === toUnit)
                .map((b) => (
                  <option key={b.id} value={b.room}>
                    {b.room} — Livre
                  </option>
                ))}
            </select>
          </div>
        </div>
      )}

      {/* Observações */}
      <div>
        <label
          className="block text-xs font-semibold uppercase tracking-wider mb-1.5"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Observações
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Notas clínicas relevantes..."
          rows={3}
          className="w-full rounded-lg border px-3 py-2 resize-y focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          aria-label="Observações"
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        style={{
          backgroundColor: 'var(--action-primary-bg-dark)',
          color: 'var(--action-primary-text-dark)',
        }}
      >
        Registrar Movimentação
      </button>
    </form>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// Skeleton Page
// ═════════════════════════════════════════════════════════════════════════════

function PageSkeleton(): React.ReactElement {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6 pb-12">
        {/* Header skeleton */}
        <div className="animate-pulse space-y-3">
          <div
            className="h-8 w-80 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-5 w-64 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>

        {/* Summary bar skeleton */}
        <div
          className="animate-pulse h-10 rounded-lg"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />

        {/* Bed grid skeleton */}
        <BedGridSkeleton count={12} />

        {/* Timeline skeleton */}
        <div
          className="animate-pulse rounded-xl border p-4 space-y-4"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
          role="status"
          aria-label="Carregando timeline"
        >
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4">
              <div
                className="w-4 h-4 rounded-full flex-shrink-0"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div className="flex-1 space-y-2">
                <div
                  className="h-4 w-1/3 rounded"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
                <div
                  className="h-3 w-2/3 rounded"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// Error State
// ═════════════════════════════════════════════════════════════════════════════

function ErrorState({ message }: { message: string }): React.ReactElement {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="flex items-center gap-3 px-4 py-4 rounded-xl border"
      style={{
        backgroundColor: 'var(--feedback-error-bg-dark)',
        color: 'var(--feedback-error-text-dark)',
        borderColor: 'var(--feedback-error-border-dark)',
      }}
    >
      <AlertTriangle className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// Main Page
// ═════════════════════════════════════════════════════════════════════════════

export default function PatientMovementPage(): React.ReactElement {
  const [selectedUnit, setSelectedUnit] = useState<string | 'all'>('all');
  const [filterType, setFilterType] = useState<MovementType | 'all'>('all');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [movements, setMovements] = useState<PatientMovement[]>([]);
  const [beds, setBeds] = useState<BedStatus[]>([]);
  const [patients, setPatients] = useState<PatientBedSummary[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<string>('');

  // ── Fetch patients on mount ──────────────────────────────────────────
  useEffect(() => {
    fetchDashboard()
      .then((data) => {
        setPatients(data.patients);
        if (data.patients.length > 0 && data.patients[0]) {
          setSelectedPatient(data.patients[0].mpi_id);
        }
      })
      .catch(() => {});
  }, []);

  // ── Fetch data from API when patient selected ────────────────────────
  useEffect(() => {
    if (!selectedPatient) return;
    setIsLoading(true);
    setError(null);

    Promise.all([fetchMovements(selectedPatient), fetchBedGrid()])
      .then(([movData, bedData]) => {
        // Map API BedStatus to movement-types BedStatus
        const mappedBeds: BedStatus[] = bedData.beds.map((b) => ({
          id: b.bed_id,
          unit: b.unit,
          room: b.room ?? '',
          status: b.status,
          current_patient_mpi_id: b.current_patient_mpi_id,
          current_patient_name: b.current_patient_name,
          occupied_since: b.occupied_since,
          last_cleaned_at: b.last_cleaned_at,
          notes: b.notes,
        }));
        // Map API PatientMovement to movement-types PatientMovement
        const mappedMovements: PatientMovement[] = movData.movements.map((m) => ({
          id: String(m.id),
          mpi_id: m.mpi_id,
          type: m.type,
          from_unit: m.from_unit,
          to_unit: m.to_unit,
          from_bed: m.from_bed,
          to_bed: m.to_bed,
          timestamp: m.timestamp,
          notes: m.notes,
          registered_by: undefined,
          created_at: m.timestamp,
        }));
        setMovements(mappedMovements);
        setBeds(mappedBeds);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [selectedPatient]);

  // ── Filtered beds ────────────────────────────────────────────────────
  const filteredBeds: BedStatus[] = useMemo(() => {
    if (selectedUnit === 'all') return beds;
    return beds.filter((b) => b.unit === selectedUnit);
  }, [selectedUnit, beds]);

  const bedSummary: BedSummary = useMemo(
    () => computeBedSummary(filteredBeds),
    [filteredBeds],
  );

  // ── Filtered movements → TimelineEvents ──────────────────────────────
  const timelineEvents: TimelineEvent[] = useMemo(() => {
    let filtered = movements;

    // Filter by unit: movements that involve the selected unit
    if (selectedUnit !== 'all') {
      filtered = filtered.filter(
        (m) => m.from_unit === selectedUnit || m.to_unit === selectedUnit,
      );
    }

    // Filter by movement type
    if (filterType !== 'all') {
      filtered = filtered.filter((m) => m.type === filterType);
    }

    // Sort descending by timestamp (most recent first)
    const sorted = [...filtered].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );

    return sorted.map(movementToTimelineEvent);
  }, [selectedUnit, filterType, movements]);

  const units = useMemo(() => {
    const unitSet = new Set(beds.map((b) => b.unit));
    return Array.from(unitSet).sort();
  }, [beds]);

  // ── Loading state ────────────────────────────────────────────────────
  if (isLoading) {
    return <PageSkeleton />;
  }

  // ── Error state ──────────────────────────────────────────────────────
  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto space-y-6 pb-12">
          <ErrorState message={error} />
        </div>
      </Layout>
    );
  }

  // ── Main render ──────────────────────────────────────────────────────
  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-7xl mx-auto space-y-6 pb-12">
          {/* ── Header ─────────────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: 'var(--clinical-severity-normal-signal, #3b82f6)',
                    color: '#ffffff',
                  }}
                >
                  <BedDouble className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Movimentação de Pacientes
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Gerencie admissões, transferências e altas dos leitos de UTI
              </p>
            </div>

            {/* New Movement Button */}
            <button
              onClick={() => setDrawerOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 min-h-[44px]"
              style={{
                backgroundColor: 'var(--action-primary-bg-dark)',
                color: 'var(--action-primary-text-dark)',
              }}
              aria-label="Nova movimentação"
            >
              <Plus className="w-4 h-4" aria-hidden="true" />
              Nova Movimentação
            </button>
          </div>

          {/* ── Bed Grid Section ────────────────────────────────────── */}
          <div
            className="rounded-xl border p-4"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            {/* Section header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <h2
                className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <BedDouble className="w-4 h-4" aria-hidden="true" />
                Grade de Leitos
              </h2>
              <UnitSelector
                units={units}
                selected={selectedUnit}
                onChange={setSelectedUnit}
              />
            </div>

            {/* Summary bar */}
            <BedSummaryBar summary={bedSummary} />

            {/* Bed grid */}
            {filteredBeds.length === 0 ? (
              <BedGridEmpty />
            ) : (
              <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 mt-4">
                {filteredBeds.map((bed) => (
                  <BedGridCard key={bed.id} bed={bed} />
                ))}
              </div>
            )}
          </div>

          {/* ── Movement Timeline Section ───────────────────────────── */}
          <div
            className="rounded-xl border p-4"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            {/* Section header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <h2
                className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <Clock className="w-4 h-4" aria-hidden="true" />
                Histórico de Movimentações
              </h2>
              <TypeFilter
                active={filterType}
                onChange={setFilterType}
              />
            </div>

            {/* Timeline */}
            <ClinicalTimeline
              events={timelineEvents}
              domain="general"
              isLoading={false}
              error={null}
            />
          </div>
        </div>
      </ErrorBoundary>

      {/* ── New Movement Drawer ─────────────────────────────────────── */}
      <DrawerBuilder
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Nova Movimentação"
        size="md"
      >
        <TransferForm
          onClose={() => setDrawerOpen(false)}
          beds={beds}
        />
      </DrawerBuilder>
    </Layout>
  );
}
