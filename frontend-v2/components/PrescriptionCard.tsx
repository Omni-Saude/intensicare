'use client';

import React, { useState, useCallback } from 'react';
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Syringe,
  Pill,
  Droplet,
  Stethoscope,
  FlaskConical,
  SprayCan,
  User,
  Calendar,
} from 'lucide-react';
import type {
  Prescription,
  PrescriptionStatus,
  DrugInteraction,
} from '@/lib/prescription-types';
import {
  ROUTE_LABELS,
  STATUS_LABELS,
  formatDose,
  getRouteIcon,
  getStatusColor,
} from '@/lib/prescription-types';

// ─── Props ───────────────────────────────────────────────────────────────────

interface PrescriptionCardProps {
  prescription: Prescription;
  onStatusChange?: (id: string, newStatus: PrescriptionStatus) => void;
  isLoading?: boolean;
  /** Interação medicamentosa relevante, se houver */
  interaction?: DrugInteraction | null;
}

// ─── Status Badge ────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: PrescriptionStatus }) {
  const bgColor = getStatusColor(status, 'bg');
  const textColor = getStatusColor(status, 'text');
  const borderColor = getStatusColor(status, 'border');

  const Icon = status === 'active' ? Clock : status === 'completed' ? CheckCircle : XCircle;

  return (
    <span
      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border"
      style={{
        backgroundColor: bgColor,
        color: textColor,
        borderColor,
      }}
    >
      <Icon className="w-3 h-3 flex-shrink-0" aria-hidden="true" />
      {STATUS_LABELS[status]}
    </span>
  );
}

// ─── Drug Interaction Alert Banner ───────────────────────────────────────────

function DrugInteractionAlert({ interaction }: { interaction: DrugInteraction }) {
  if (!interaction) return null;

  const severityColor =
    interaction.severity === 'contraindicado'
      ? 'var(--clinical-severity-critical-signal)'
      : interaction.severity === 'grave'
        ? 'var(--clinical-severity-urgent-signal)'
        : 'var(--clinical-severity-watch-signal)';

  const severityBg =
    interaction.severity === 'contraindicado'
      ? 'var(--clinical-severity-critical-wash)'
      : interaction.severity === 'grave'
        ? 'var(--clinical-severity-urgent-wash)'
        : 'var(--clinical-severity-watch-wash)';

  const severityText =
    interaction.severity === 'contraindicado'
      ? 'var(--clinical-severity-critical-on-surface)'
      : interaction.severity === 'grave'
        ? 'var(--clinical-severity-urgent-on-surface)'
        : 'var(--clinical-severity-watch-on-surface)';

  const label =
    interaction.severity === 'contraindicado'
      ? 'Contraindicado'
      : interaction.severity === 'grave'
        ? 'Grave'
        : 'Moderado';

  return (
    <div
      role="alert"
      className="flex items-start gap-2 px-3 py-2 rounded-lg border text-xs mb-3"
      style={{
        backgroundColor: severityBg,
        borderColor: severityColor,
        color: severityText,
      }}
    >
      <AlertTriangle
        className="w-4 h-4 flex-shrink-0 mt-0.5"
        style={{ color: severityColor }}
        aria-hidden="true"
      />
      <div className="min-w-0">
        <span className="font-semibold">Interação {label}:</span>{' '}
        {interaction.description}
      </div>
    </div>
  );
}

// ─── Loading Skeleton ────────────────────────────────────────────────────────

function PrescriptionCardSkeleton() {
  return (
    <div
      className="rounded-xl border p-5 animate-pulse"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      role="status"
      aria-label="Carregando prescrição"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="space-y-2 flex-1">
          <div
            className="h-5 rounded w-40"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-4 rounded w-24"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
        <div
          className="h-6 rounded-full w-20"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
      <div className="flex gap-2 mb-3">
        <div
          className="h-6 rounded-full w-28"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="h-6 rounded-full w-20"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
      <div className="flex items-center justify-between mt-4 pt-3 border-t"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      >
        <div
          className="h-3 rounded w-48"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="flex gap-2">
          <div
            className="h-8 rounded-lg w-24"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-8 rounded-lg w-28"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      </div>
    </div>
  );
}

// ─── Prescription Card ───────────────────────────────────────────────────────

export default function PrescriptionCard({
  prescription,
  onStatusChange,
  isLoading = false,
  interaction = null,
}: PrescriptionCardProps) {
  const [isUpdating, setIsUpdating] = useState(false);

  const handleStatusChange = useCallback(
    async (newStatus: PrescriptionStatus) => {
      if (!onStatusChange) return;
      setIsUpdating(true);
      // Simula latência de rede
      await new Promise((r) => setTimeout(r, 400));
      onStatusChange(prescription.id, newStatus);
      setIsUpdating(false);
    },
    [onStatusChange, prescription.id],
  );

  // ── Loading State ──────────────────────────────────────────────────────────
  if (isLoading) {
    return <PrescriptionCardSkeleton />;
  }

  // ── Derived Values ─────────────────────────────────────────────────────────
  const RouteIcon = getRouteIcon(prescription.route);
  const isActive = prescription.status === 'active';
  const createdAtDate = new Date(prescription.created_at);
  const formattedDate = createdAtDate.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });

  return (
    <div
      className="rounded-xl border p-5 transition-shadow hover:shadow-md"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      aria-label={`Prescrição: ${prescription.drug} — ${STATUS_LABELS[prescription.status]}`}
    >
      {/* ── Drug Interaction Alert ──────────────────────────────────────────── */}
      {interaction && <DrugInteractionAlert interaction={interaction} />}

      {/* ── Header: Drug Name + Status ─────────────────────────────────────── */}
      <div className="flex items-start justify-between mb-3">
        <div className="min-w-0 flex-1">
          <h3
            className="text-base font-bold truncate"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            {prescription.drug}
          </h3>
          <p
            className="text-sm mt-0.5"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            {formatDose(prescription.dose, prescription.unit)}
          </p>
        </div>
        <StatusBadge status={prescription.status} />
      </div>

      {/* ── Route + Frequency Badges ────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-2 mb-3">
        {/* Route badge */}
        <span
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border"
          style={{
            backgroundColor: 'var(--semantic-surface-overlay)',
            color: 'var(--semantic-text-primary)',
            borderColor: 'var(--semantic-border-default)',
          }}
        >
          <RouteIcon className="w-3 h-3 flex-shrink-0" aria-hidden="true" />
          {ROUTE_LABELS[prescription.route]}
        </span>

        {/* Frequency badge */}
        <span
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border"
          style={{
            backgroundColor: 'var(--semantic-surface-overlay)',
            color: 'var(--semantic-text-secondary)',
            borderColor: 'var(--semantic-border-default)',
          }}
        >
          <Clock className="w-3 h-3 flex-shrink-0" aria-hidden="true" />
          {prescription.frequency}
        </span>
      </div>

      {/* ── Notes ──────────────────────────────────────────────────────────── */}
      {prescription.notes && (
        <p
          className="text-xs mb-3 italic"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {prescription.notes}
        </p>
      )}

      {/* ── Footer: Timestamp + Actions ────────────────────────────────────── */}
      <div
        className="flex items-center justify-between mt-4 pt-3 border-t"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      >
        <div
          className="flex items-center gap-1.5 text-xs"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          <Calendar className="w-3 h-3 flex-shrink-0" aria-hidden="true" />
          <span>
            Prescrito em {formattedDate} por{' '}
            <span className="font-medium">{prescription.prescribed_by}</span>
          </span>
        </div>

        {/* ── Action Buttons (only for active) ─────────────────────────────── */}
        {isActive && onStatusChange && (
          <div className="flex gap-2 flex-shrink-0">
            <button
              onClick={() => handleStatusChange('completed')}
              disabled={isUpdating}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50"
              style={{
                color: 'var(--clinical-severity-watch-on-fill)',
                borderColor: 'var(--clinical-severity-watch-signal)',
                backgroundColor: 'transparent',
              }}
              aria-label={`Concluir ${prescription.drug}`}
            >
              <CheckCircle className="w-3.5 h-3.5" aria-hidden="true" />
              Concluir
            </button>
            <button
              onClick={() => handleStatusChange('discontinued')}
              disabled={isUpdating}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50"
              style={{
                color: 'var(--semantic-text-secondary)',
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'transparent',
              }}
              aria-label={`Descontinuar ${prescription.drug}`}
            >
              <XCircle className="w-3.5 h-3.5" aria-hidden="true" />
              Descontinuar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Re-export types for convenience
export type { Prescription, PrescriptionStatus, DrugInteraction };
