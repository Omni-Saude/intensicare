'use client';

import React from 'react';
import {
  Clock,
  Search,
  Ban,
  CheckCircle,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { type GlosaStatus, GLOSA_STATUS_LABELS, GLOSA_STATUS_COLORS, formatCurrency } from '@/lib/doc-types';

// ─── Types ──────────────────────────────────────────────────────────────────

interface GlosaStatusBadgeProps {
  status: GlosaStatus;
  valor?: number;
  isLoading?: boolean;
}

// ─── Icon mapping ───────────────────────────────────────────────────────────

const statusIcons: Record<GlosaStatus, React.ComponentType<{ className?: string }>> = {
  pendente: Clock,
  em_analise: Search,
  glosado: Ban,
  liberado: CheckCircle,
  recorrido: RefreshCw,
};

// ─── Component ──────────────────────────────────────────────────────────────

export default function GlosaStatusBadge({
  status,
  valor,
  isLoading = false,
}: GlosaStatusBadgeProps): React.ReactElement {
  const colors = GLOSA_STATUS_COLORS[status];
  const label = GLOSA_STATUS_LABELS[status];
  const Icon = statusIcons[status];

  // ─── Loading state ──────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border animate-pulse"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label="Carregando status de glosa"
      >
        <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
        <div
          className="h-4 w-20 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
    );
  }

  // ─── Badge ──────────────────────────────────────────────────────────────
  const ariaLabel = `Status de glosa: ${label}${valor !== undefined && valor > 0 ? ` — Valor glosado: ${formatCurrency(valor)}` : ''}`;

  return (
    <div
      role="status"
      aria-label={ariaLabel}
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border text-xs font-semibold"
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
        borderColor: colors.border,
        borderWidth: '1px',
      }}
    >
      <Icon className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
      <span>{label}</span>
      {status === 'glosado' && valor !== undefined && valor > 0 && (
        <span
          className="tabular-nums ml-0.5 opacity-90"
          style={{ color: colors.icon }}
        >
          {formatCurrency(valor)}
        </span>
      )}
      {status === 'recorrido' && valor !== undefined && valor > 0 && (
        <span
          className="tabular-nums ml-0.5 opacity-80"
          style={{ color: colors.icon }}
        >
          {formatCurrency(valor)}
        </span>
      )}
    </div>
  );
}
