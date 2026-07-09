'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Circle, Clock, Droplets } from 'lucide-react';
import type { BedStatus, BedStatusType } from '@/lib/movement-types';
import { STATUS_LABELS, getBedStatusColor } from '@/lib/movement-types';

// ─── Props ──────────────────────────────────────────────────────────────────

interface BedGridCardProps {
  bed: BedStatus;
  onSelect?: (bed: BedStatus) => void;
  isLoading?: boolean;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatDateTime(iso?: string): string {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '—';
  }
}

// ─── Skeleton Card ──────────────────────────────────────────────────────────

function BedCardSkeleton(): React.ReactElement {
  return (
    <div
      className="animate-pulse rounded-xl border p-3"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      role="status"
      aria-label="Carregando leito"
    >
      <div className="flex items-center gap-2">
        <div
          className="w-8 h-8 rounded-full flex-shrink-0"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="flex-1 space-y-1.5">
          <div
            className="h-4 w-16 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-3 w-24 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      </div>
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function BedGridCard({
  bed,
  onSelect,
  isLoading = false,
}: BedGridCardProps): React.ReactElement {
  const [expanded, setExpanded] = useState(false);
  const colors = getBedStatusColor(bed.status);
  const statusLabel = STATUS_LABELS[bed.status];

  // ── Loading state ─────────────────────────────────────────────────────
  if (isLoading) return <BedCardSkeleton />;

  // ── Expand/collapse toggle ────────────────────────────────────────────
  const toggleExpanded = () => setExpanded((prev) => !prev);

  const handleClick = () => {
    toggleExpanded();
    onSelect?.(bed);
  };

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <button
      onClick={handleClick}
      className="w-full text-left rounded-xl border p-3 transition-all hover:shadow-md focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[64px]"
      style={{
        borderColor: colors.border,
        backgroundColor: colors.bg,
        color: colors.text,
      }}
      aria-label={`Leito ${bed.room} — ${statusLabel}${bed.current_patient_name ? `, paciente ${bed.current_patient_name}` : ''}`}
      title={`${bed.unit} / ${bed.room} — ${statusLabel}`}
    >
      {/* ── Compact Row ───────────────────────────────────────────────── */}
      <div className="flex items-center gap-2">
        {/* Status dot */}
        <span
          className="w-3 h-3 rounded-full flex-shrink-0"
          style={{ backgroundColor: colors.dot }}
          aria-hidden="true"
        />

        {/* Bed ID */}
        <span
          className="text-xs font-semibold uppercase tracking-wider flex-shrink-0"
          style={{ color: colors.text, opacity: 0.85 }}
        >
          {bed.room}
        </span>

        {/* Spacer */}
        <div className="flex-1 min-w-0" />

        {/* Patient name (if occupied) */}
        {bed.status === 'occupied' && bed.current_patient_name ? (
          <span className="text-xs font-medium truncate max-w-[120px]">
            {bed.current_patient_name}
          </span>
        ) : (
          <span className="text-xs" style={{ opacity: 0.75 }}>
            {statusLabel}
          </span>
        )}

        {/* Expand chevron */}
        {expanded ? (
          <ChevronUp className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
        )}
      </div>

      {/* ── Expanded Details ───────────────────────────────────────────── */}
      {expanded && (
        <div
          className="mt-2 pt-2 border-t space-y-1"
          style={{ borderColor: colors.border }}
        >
          {/* Status badge */}
          <div className="flex items-center gap-1.5">
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
              style={{
                backgroundColor: colors.dot,
                color: '#ffffff',
              }}
            >
              {statusLabel}
            </span>
            <span className="text-[11px]" style={{ opacity: 0.7 }}>
              {bed.unit}
            </span>
          </div>

          {/* Occupied detail */}
          {bed.status === 'occupied' && (
            <div className="text-[11px] space-y-0.5">
              {bed.current_patient_name && (
                <p>
                  <span style={{ opacity: 0.6 }}>Paciente: </span>
                  <span className="font-medium">{bed.current_patient_name}</span>
                </p>
              )}
              {bed.occupied_since && (
                <p className="flex items-center gap-1">
                  <Clock className="w-3 h-3" aria-hidden="true" />
                  <span style={{ opacity: 0.6 }}>
                    Desde: {formatDateTime(bed.occupied_since)}
                  </span>
                </p>
              )}
            </div>
          )}

          {/* Cleaning detail */}
          {bed.status === 'cleaning' && bed.last_cleaned_at && (
            <p className="text-[11px] flex items-center gap-1">
              <Droplets className="w-3 h-3" aria-hidden="true" />
              <span style={{ opacity: 0.6 }}>
                Última limpeza: {formatDateTime(bed.last_cleaned_at)}
              </span>
            </p>
          )}

          {/* Notes */}
          {bed.notes && (
            <p
              className="text-[11px] mt-1"
              style={{ opacity: 0.75 }}
            >
              {bed.notes}
            </p>
          )}
        </div>
      )}
    </button>
  );
}

// ─── Bed Grid Skeleton ──────────────────────────────────────────────────────

export function BedGridSkeleton({ count = 12 }: { count?: number }): React.ReactElement {
  return (
    <div
      className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3"
      role="status"
      aria-label="Carregando grade de leitos"
    >
      {Array.from({ length: count }).map((_, i) => (
        <BedCardSkeleton key={i} />
      ))}
    </div>
  );
}

// ─── Empty Bed Grid ─────────────────────────────────────────────────────────

export function BedGridEmpty(): React.ReactElement {
  return (
    <div
      className="flex flex-col items-center justify-center gap-2 py-10 text-sm rounded-xl border border-dashed"
      style={{
        borderColor: 'var(--semantic-border-default)',
        color: 'var(--semantic-text-secondary)',
      }}
      role="status"
      aria-label="Nenhum leito encontrado"
    >
      <Circle className="w-10 h-10 opacity-20" aria-hidden="true" />
      <p>Nenhum leito disponível nesta unidade</p>
    </div>
  );
}
