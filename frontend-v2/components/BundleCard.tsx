'use client';

import React, { useCallback, useId } from 'react';
import {
  CheckCircle,
  Clock,
  AlertTriangle,
  HelpCircle,
  Loader2,
  Ban,
  Circle,
  XCircle,
} from 'lucide-react';
import SeverityBadge from '@/components/SeverityBadge';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface BundleCriterion {
  id: string;
  label: string;
  met: boolean;
  na?: boolean;
}

export type BundleStatus = 'complete' | 'partial' | 'pending' | 'na';

export interface BundleInfo {
  id: string;
  name: string;
  criteria: BundleCriterion[];
  status: BundleStatus;
  score?: number;
}

interface BundleCardProps {
  bundle: BundleInfo;
  onToggle?: (criterionId: string, met: boolean) => void;
  isLoading?: boolean;
  error?: string | null;
  readOnly?: boolean;
}

// ─── Status → Token mapping ─────────────────────────────────────────────────

interface BundleStatusTokenSet {
  onSurface: string;
  signal: string;
  fill: string;
  onFill: string;
}

const bundleStatusTokens: Record<BundleStatus, BundleStatusTokenSet> = {
  complete: {
    onSurface: 'var(--clinical-prophylaxis-complete-on-surface)',
    signal: 'var(--clinical-prophylaxis-complete-signal)',
    fill: 'var(--clinical-prophylaxis-complete-fill)',
    onFill: 'var(--clinical-prophylaxis-complete-on-fill)',
  },
  partial: {
    onSurface: 'var(--clinical-prophylaxis-partial-on-surface)',
    signal: 'var(--clinical-prophylaxis-partial-signal)',
    fill: 'var(--clinical-prophylaxis-partial-fill)',
    onFill: 'var(--clinical-prophylaxis-partial-on-fill)',
  },
  pending: {
    onSurface: 'var(--clinical-prophylaxis-pending-on-surface)',
    signal: 'var(--clinical-prophylaxis-pending-signal)',
    fill: 'var(--clinical-prophylaxis-pending-fill)',
    onFill: 'var(--clinical-prophylaxis-pending-on-fill)',
  },
  na: {
    onSurface: 'var(--clinical-prophylaxis-na-on-surface)',
    signal: 'var(--clinical-prophylaxis-na-signal)',
    fill: 'var(--clinical-prophylaxis-na-fill)',
    onFill: 'var(--clinical-prophylaxis-na-on-fill)',
  },
};

const statusLabels: Record<BundleStatus, string> = {
  complete: 'Completo',
  partial: 'Parcial',
  pending: 'Pendente',
  na: 'N/A',
};

const statusIcons: Record<BundleStatus, React.ComponentType<{ className?: string }>> = {
  complete: CheckCircle,
  partial: Clock,
  pending: Circle,
  na: Ban,
};

// ─── Skeleton ────────────────────────────────────────────────────────────────

function BundleCardSkeleton(): React.ReactElement {
  return (
    <div
      className="border rounded-xl p-4 animate-pulse space-y-3"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      role="status"
      aria-label="Loading bundle card"
    >
      <div className="flex items-center justify-between">
        <div
          className="h-4 rounded w-2/3"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="h-5 w-16 rounded-full"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
      <div
        className="h-2 rounded w-full"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded flex-shrink-0"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-3 rounded flex-1"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      ))}
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function BundleCard({
  bundle,
  onToggle,
  isLoading = false,
  error = null,
  readOnly = false,
}: BundleCardProps): React.ReactElement {
  const cardId = useId();
  const tokens = bundleStatusTokens[bundle.status];
  const StatusIcon = statusIcons[bundle.status];

  const handleToggle = useCallback(
    (criterionId: string, met: boolean) => {
      onToggle?.(criterionId, met);
    },
    [onToggle],
  );

  const activeCriteria = bundle.criteria.filter((c) => !c.na);
  const metCount = activeCriteria.filter((c) => c.met).length;
  const totalActive = activeCriteria.length;
  const progressPercent =
    totalActive > 0 ? Math.round((metCount / totalActive) * 100) : 0;

  // ─── Loading state ────────────────────────────────────────────────────────
  if (isLoading) {
    return <BundleCardSkeleton />;
  }

  // ─── Error state ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm"
        style={{
          backgroundColor: 'var(--feedback-error-bg-dark)',
          color: 'var(--feedback-error-text-dark)',
          borderColor: 'var(--feedback-error-border-dark)',
          borderWidth: '1px',
        }}
      >
        <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // ─── Card ─────────────────────────────────────────────────────────────────
  return (
    <div
      role="region"
      aria-label={`Bundle: ${bundle.name} — ${statusLabels[bundle.status]}`}
      className="border rounded-xl overflow-hidden transition-shadow hover:shadow-md"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 flex items-center justify-between gap-3"
        style={{
          borderBottomWidth: '1px',
          borderBottomColor: 'var(--semantic-border-default)',
        }}
      >
        <h3
          className="text-sm font-semibold truncate"
          style={{ color: 'var(--semantic-text-primary)' }}
          id={`${cardId}-title`}
        >
          {bundle.name}
        </h3>

        {/* Status badge */}
        <span
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold flex-shrink-0"
          style={{
            backgroundColor: tokens.fill,
            color: tokens.onFill,
          }}
        >
          <StatusIcon className="w-3.5 h-3.5" aria-hidden="true" />
          {statusLabels[bundle.status]}
        </span>
      </div>

      {/* Progress bar */}
      {bundle.status !== 'na' && totalActive > 0 && (
        <div className="px-4 pt-3">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span style={{ color: 'var(--semantic-text-secondary)' }}>
              {metCount} de {totalActive} critérios atendidos
            </span>
            <span
              className="font-semibold tabular-nums"
              style={{ color: tokens.onSurface }}
            >
              {bundle.score !== undefined ? `${bundle.score}%` : `${progressPercent}%`}
            </span>
          </div>
          <div
            className="h-2 rounded-full overflow-hidden"
            style={{
              backgroundColor: 'var(--semantic-surface-overlay)',
            }}
            role="progressbar"
            aria-valuenow={bundle.score ?? progressPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Progresso: ${bundle.score ?? progressPercent}% completado`}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${bundle.score ?? progressPercent}%`,
                backgroundColor: tokens.signal,
                minWidth: progressPercent > 0 ? '8px' : '0',
              }}
            />
          </div>
        </div>
      )}

      {/* Criteria list */}
      <ul className="px-4 py-3 space-y-2 list-none m-0" role="list" aria-label="Bundle criteria">
        {bundle.criteria.map((criterion) => {
          const criterionId = `${cardId}-crit-${criterion.id}`;

          return (
            <li key={criterion.id}>
              <label
                htmlFor={criterionId}
                className={`flex items-center gap-2.5 py-1 rounded select-none ${
                  readOnly ? 'cursor-default' : 'cursor-pointer'
                }`}
              >
                {/* Checkbox or read-only indicator */}
                {criterion.na ? (
                  <span className="flex-shrink-0" aria-hidden="true">
                    <Ban
                      className="w-4 h-4"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    />
                  </span>
                ) : readOnly ? (
                  <span className="flex-shrink-0" aria-hidden="true">
                    {criterion.met ? (
                      <CheckCircle
                        className="w-4 h-4"
                        style={{ color: tokens.signal }}
                      />
                    ) : (
                      <XCircle
                        className="w-4 h-4"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      />
                    )}
                  </span>
                ) : (
                  <input
                    id={criterionId}
                    type="checkbox"
                    checked={criterion.met}
                    onChange={(e) => handleToggle(criterion.id, e.target.checked)}
                    className="flex-shrink-0 w-4 h-4 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                    style={{
                      accentColor: tokens.signal,
                      borderColor: tokens.signal,
                    }}
                    aria-label={criterion.label}
                  />
                )}

                <span
                  className={`text-sm flex-1 ${
                    criterion.na ? 'line-through' : ''
                  } ${!criterion.met && !criterion.na ? '' : ''}`}
                  style={{
                    color: criterion.na
                      ? 'var(--semantic-text-secondary)'
                      : 'var(--semantic-text-primary)',
                    opacity: criterion.na ? 0.6 : 1,
                  }}
                >
                  {criterion.label}
                  {criterion.na && (
                    <span
                      className="ml-1 text-[10px] font-semibold uppercase"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      N/A
                    </span>
                  )}
                </span>
              </label>
            </li>
          );
        })}

        {bundle.criteria.length === 0 && (
          <li className="flex items-center justify-center py-4">
            <span
              className="text-xs flex items-center gap-1.5"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              <HelpCircle className="w-3.5 h-3.5" aria-hidden="true" />
              Nenhum critério definido
            </span>
          </li>
        )}
      </ul>
    </div>
  );
}
