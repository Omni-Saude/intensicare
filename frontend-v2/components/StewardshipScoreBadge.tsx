'use client';

import React from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  TrendingUp,
  Loader2,
  AlertOctagon,
} from 'lucide-react';

// ─── Types ──────────────────────────────────────────────────────────────────

export type StewardshipSeverity = 'VERMELHO' | 'AMARELO' | 'NEUTRO';

interface StewardshipScoreBadgeProps {
  score: number;
  totalCriteria: number;
  severity: StewardshipSeverity;
  recommendation?: string;
  isLoading?: boolean;
  error?: string | null;
}

// ─── Severity → Token mapping ───────────────────────────────────────────────

interface SeverityTokenSet {
  signal: string;
  onSurface: string;
  fill: string;
  onFill: string;
  wash: string;
}

const severityTokens: Record<StewardshipSeverity, SeverityTokenSet> = {
  VERMELHO: {
    signal: 'var(--clinical-antimicrobial-stewardship-intervention-signal)',
    onSurface:
      'var(--clinical-antimicrobial-stewardship-intervention-on-surface)',
    fill: 'var(--clinical-antimicrobial-stewardship-intervention-fill)',
    onFill: 'var(--clinical-antimicrobial-stewardship-intervention-on-fill)',
    wash: 'var(--clinical-antimicrobial-stewardship-intervention-wash)',
  },
  AMARELO: {
    signal: 'var(--clinical-antimicrobial-stewardship-review-signal)',
    onSurface: 'var(--clinical-antimicrobial-stewardship-review-on-surface)',
    fill: 'var(--clinical-antimicrobial-stewardship-review-fill)',
    onFill: 'var(--clinical-antimicrobial-stewardship-review-on-fill)',
    wash: 'var(--clinical-antimicrobial-stewardship-review-wash)',
  },
  NEUTRO: {
    signal: 'var(--clinical-antimicrobial-stewardship-optimal-signal)',
    onSurface: 'var(--clinical-antimicrobial-stewardship-optimal-on-surface)',
    fill: 'var(--clinical-antimicrobial-stewardship-optimal-fill)',
    onFill: 'var(--clinical-antimicrobial-stewardship-optimal-on-fill)',
    wash: 'var(--clinical-antimicrobial-stewardship-optimal-wash)',
  },
};

const severityLabels: Record<StewardshipSeverity, string> = {
  VERMELHO: 'Intervenção Imediata',
  AMARELO: 'Revisão Recomendada',
  NEUTRO: 'Prescrição Adequada',
};

const severityIcons: Record<
  StewardshipSeverity,
  React.ComponentType<{ className?: string }>
> = {
  VERMELHO: AlertOctagon,
  AMARELO: AlertTriangle,
  NEUTRO: ShieldCheck,
};

// ─── Component ──────────────────────────────────────────────────────────────

export default function StewardshipScoreBadge({
  score,
  totalCriteria,
  severity,
  recommendation,
  isLoading = false,
  error = null,
}: StewardshipScoreBadgeProps): React.ReactElement {
  const tokens = severityTokens[severity];
  const Icon = severityIcons[severity];
  const label = severityLabels[severity];

  const ariaLabel = `Pontuação de stewardship: ${score} de ${totalCriteria} — ${label}${
    recommendation ? `. ${recommendation}` : ''
  }`;

  // ─── Loading state ────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div
        className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border animate-pulse"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label="Carregando pontuação de stewardship"
      >
        <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
        <div
          className="h-4 w-16 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="h-2 w-24 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>
    );
  }

  // ─── Error state ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-2 px-3 py-3 rounded-lg text-sm"
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

  // ─── Bounds validation ────────────────────────────────────────────────────
  const validTotal = totalCriteria > 0;
  const displayScore = validTotal ? score : 'N/A';
  const displayTotal = validTotal ? totalCriteria : 'N/A';
  const scoreExceedsTotal = validTotal && score > totalCriteria;

  // ─── Badge ────────────────────────────────────────────────────────────────
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={ariaLabel}
      className="inline-flex flex-col gap-1.5 p-3 rounded-xl border min-w-[180px]"
      style={{
        borderColor: tokens.signal,
        backgroundColor: tokens.wash,
        borderWidth: '2px',
        boxShadow: `0 0 0 1px ${tokens.wash}`,
      }}
    >
      {/* Score row */}
      <div className="flex items-center gap-2">
        <div
          className="flex items-center justify-center w-10 h-10 rounded-full flex-shrink-0"
          style={{
            backgroundColor: tokens.fill,
            color: tokens.onFill,
            minWidth: '44px',
            minHeight: '44px',
          }}
          aria-hidden="true"
        >
          <Icon className="w-5 h-5" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-1">
            <span
              className="text-xl font-bold tabular-nums leading-none"
              style={{ color: tokens.onSurface }}
            >
              {displayScore}
            </span>
            <span
              className="text-sm tabular-nums"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              / {displayTotal}
            </span>
          </div>

          <div
            className="text-xs font-semibold mt-0.5"
            style={{ color: tokens.onSurface }}
          >
            {label}
          </div>
        </div>
      </div>

      {/* Score exceeds bounds warning */}
      {scoreExceedsTotal && (
        <div
          className="text-[10px] italic"
          style={{ color: 'var(--feedback-warning-text-dark, var(--semantic-text-secondary))' }}
        >
          Pontuação excede o total de critérios
        </div>
      )}

      {/* Recommendation */}
      {recommendation && (
        <div
          className="text-[11px] leading-relaxed pt-1.5 mt-0.5"
          style={{
            borderTopWidth: '1px',
            borderTopColor: tokens.signal,
            borderTopStyle: 'solid',
            color: tokens.onSurface,
            opacity: 0.9,
          }}
        >
          <TrendingUp
            className="w-3 h-3 inline-block mr-1 -mt-0.5"
            aria-hidden="true"
          />
          {recommendation}
        </div>
      )}
    </div>
  );
}
