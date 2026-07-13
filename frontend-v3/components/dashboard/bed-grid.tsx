'use client';

import { useMemo } from 'react';
import type { PatientBedSummary, SeverityLevel } from '@/lib/api';
import { BedCard } from './bed-card';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface BedGridProps {
  patients: PatientBedSummary[];
  onSelect: (mpiId: string) => void;
  isLoading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
}

// RF-007: hierarquia de criticidade — leitos críticos primeiro, para que o
// intensivista não precise fazer scroll manual pela grade inteira em 320px
// para localizar os pacientes que mais precisam de atenção imediata.
const SEVERITY_RANK: Record<SeverityLevel, number> = {
  critical: 0,
  urgent: 1,
  watch: 2,
  normal: 3,
};

function bySeverityThenBed(a: PatientBedSummary, b: PatientBedSummary): number {
  const rankDiff = SEVERITY_RANK[a.severity ?? 'normal'] - SEVERITY_RANK[b.severity ?? 'normal'];
  if (rankDiff !== 0) return rankDiff;
  // Empate de severidade: ordem estável e previsível por leito.
  return a.bed.localeCompare(b.bed, undefined, { numeric: true });
}

function SkeletonCard() {
  return (
    <div
      className="flex flex-col gap-3 p-4 rounded-[var(--radius-lg)] animate-pulse"
      style={{
        backgroundColor: 'var(--surface-raised)',
        borderColor: 'var(--border-default)',
        borderWidth: '1px',
        borderStyle: 'solid',
      }}
    >
      <div className="flex items-center gap-2">
        <div
          className="size-2.5 shrink-0 rounded-full"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
        <div
          className="h-4 w-32 rounded"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
        <div
          className="h-3 w-16 rounded ml-auto"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
      </div>
      <div
        className="h-3 w-24 rounded"
        style={{ backgroundColor: 'var(--surface-overlay)' }}
      />
      <div
        className="h-3 w-40 rounded"
        style={{ backgroundColor: 'var(--surface-overlay)' }}
      />
    </div>
  );
}

export function BedGrid({
  patients,
  onSelect,
  isLoading = false,
  error = null,
  onRetry,
}: BedGridProps) {
  // RF-007: ordena por hierarquia de criticidade antes de renderizar (hook
  // incondicional, antes dos early-returns, para respeitar Rules of Hooks).
  const sortedPatients = useMemo(() => [...patients].sort(bySeverityThenBed), [patients]);

  // Error state
  if (error) {
    return (
      <div
        role="alert"
        className="flex flex-col items-center justify-center gap-4 py-16 px-4 rounded-[var(--radius-lg)]"
        style={{
          backgroundColor: 'var(--severity-critical-wash)',
          borderColor: 'var(--severity-critical)',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
      >
        <AlertTriangle
          className="size-10"
          style={{ color: 'var(--severity-critical)' }}
        />
        <p
          className="text-sm font-medium text-center"
          style={{ color: 'var(--severity-critical)' }}
        >
          Erro ao carregar dashboard
        </p>
        <p
          className="text-xs text-center"
          style={{ color: 'var(--text-secondary)' }}
        >
          {error.message}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-[var(--radius-sm)] transition-colors hover:opacity-80"
            style={{
              backgroundColor: 'var(--surface-overlay)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border-default)',
              borderWidth: '1px',
              borderStyle: 'solid',
            }}
            aria-label="Tentar novamente"
          >
            <RefreshCw className="size-4" />
            Tentar novamente
          </button>
        )}
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        }}
        aria-label="Carregando pacientes"
        aria-busy="true"
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  // Empty state
  if (!sortedPatients || sortedPatients.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-16 px-4 rounded-[var(--radius-lg)]"
        style={{
          backgroundColor: 'var(--surface-raised)',
          borderColor: 'var(--border-default)',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
      >
        <p
          className="text-sm font-medium"
          style={{ color: 'var(--text-secondary)' }}
        >
          Nenhum paciente internado
        </p>
      </div>
    );
  }

  // Normal state
  return (
    <div
      className="grid gap-4"
      style={{
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
      }}
      role="list"
      aria-label="Lista de pacientes"
    >
      {sortedPatients.map((patient) => (
        <div key={patient.mpi_id} role="listitem">
          <BedCard
            patient={patient}
            onClick={() => onSelect(patient.mpi_id)}
          />
        </div>
      ))}
    </div>
  );
}
