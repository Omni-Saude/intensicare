'use client';

import React, { useCallback, useRef } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  HelpCircle,
} from 'lucide-react';
import ClinicalTooltip from '@/components/ClinicalTooltip';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Criterion {
  id: string;
  label: string;
  description?: string;
  category?: string;
  met: boolean;
  value?: string;
  threshold?: string;
}

export type CriteriaDomain = 'sepsis' | 'antimicrobial' | 'nutrition' | 'pathway';

interface CriteriaChecklistProps {
  items: Criterion[];
  domain: CriteriaDomain;
  onToggle?: (id: string, met: boolean) => void;
  readOnly?: boolean;
  isLoading?: boolean;
  error?: string | null;
}

// ─── Domain → Token maps ────────────────────────────────────────────────────

interface CriterionTokenSet {
  metOnSurface: string;
  metSignal: string;
  notMetOnSurface: string;
  notMetSignal: string;
}

const domainTokens: Record<CriteriaDomain, CriterionTokenSet> = {
  sepsis: {
    metOnSurface: 'var(--clinical-sepsis-criteria-met-on-surface)',
    metSignal: 'var(--clinical-sepsis-criteria-met-signal)',
    notMetOnSurface: 'var(--clinical-sepsis-criteria-not-met-on-surface)',
    notMetSignal: 'var(--clinical-sepsis-criteria-not-met-signal)',
  },
  antimicrobial: {
    metOnSurface: 'var(--clinical-antimicrobial-stewardship-optimal-on-surface)',
    metSignal: 'var(--clinical-antimicrobial-stewardship-optimal-signal)',
    notMetOnSurface: 'var(--clinical-sepsis-criteria-not-met-on-surface)',
    notMetSignal: 'var(--clinical-sepsis-criteria-not-met-signal)',
  },
  nutrition: {
    metOnSurface: 'var(--clinical-nutrition-optimal-on-surface)',
    metSignal: 'var(--clinical-nutrition-optimal-signal)',
    notMetOnSurface: 'var(--clinical-nutrition-at-risk-on-surface)',
    notMetSignal: 'var(--clinical-nutrition-at-risk-signal)',
  },
  pathway: {
    metOnSurface: 'var(--clinical-pathway-active-on-surface)',
    metSignal: 'var(--clinical-pathway-active-signal)',
    notMetOnSurface: 'var(--clinical-pathway-overdue-on-surface)',
    notMetSignal: 'var(--clinical-pathway-overdue-signal)',
  },
};

// ─── Skeleton ────────────────────────────────────────────────────────────────

function SkeletonRow({ index }: { index: number }): React.ReactElement {
  return (
    <div
      className="flex items-center gap-3 px-3 py-2.5 animate-pulse"
      role="status"
      aria-label="Loading criteria"
    >
      <div
        className="w-5 h-5 rounded flex-shrink-0"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div className="flex-1 space-y-1.5">
        <div
          className="h-3.5 rounded w-3/4"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        {index % 3 === 0 && (
          <div
            className="h-2.5 rounded w-1/2"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        )}
      </div>
      <div
        className="h-3 w-12 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function CriteriaChecklist({
  items,
  domain,
  onToggle,
  readOnly = false,
  isLoading = false,
  error = null,
}: CriteriaChecklistProps): React.ReactElement {
  const tokens = domainTokens[domain];
  const listRef = useRef<HTMLUListElement>(null);

  const handleToggle = useCallback(
    (id: string, checked: boolean) => {
      onToggle?.(id, checked);
    },
    [onToggle],
  );

  // ─── Loading state ────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div
        className="space-y-1"
        role="status"
        aria-label={`Loading ${domain} criteria checklist`}
      >
        <SkeletonRow index={0} />
        <SkeletonRow index={1} />
        <SkeletonRow index={2} />
        <SkeletonRow index={3} />
        <SkeletonRow index={4} />
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

  // ─── Empty state ──────────────────────────────────────────────────────────
  if (items.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-8 text-sm"
        style={{ color: 'var(--semantic-text-secondary)' }}
        role="status"
        aria-label="No criteria configured"
      >
        <HelpCircle className="w-10 h-10 opacity-30" aria-hidden="true" />
        <p>Nenhum critério configurado</p>
      </div>
    );
  }

  // ─── Checklist ────────────────────────────────────────────────────────────
  return (
    <ul
      ref={listRef}
      className="space-y-1 list-none p-0 m-0"
      role="list"
      aria-label={`${domain === 'sepsis' ? 'Sepsis' : domain === 'antimicrobial' ? 'Antimicrobial' : domain === 'nutrition' ? 'Nutrition' : 'Pathway'} criteria checklist`}
    >
      {items.map((item) => {
        const criterionId = `criterion-${item.id}`;
        const descriptionId = item.description
          ? `criterion-desc-${item.id}`
          : undefined;

        const criterionContent = (
          <li key={item.id}>
            {/* eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions */}
            <label
              htmlFor={criterionId}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors cursor-pointer select-none group ${
                readOnly ? 'cursor-default' : 'hover:bg-black/5 dark:hover:bg-white/5'
              }`}
              style={readOnly ? { cursor: 'default' } : undefined}
            >
              {/* Checkbox or read-only icon */}
              {readOnly ? (
                <span
                  className="flex-shrink-0 flex items-center justify-center w-5 h-5"
                  aria-hidden="true"
                >
                  {item.met ? (
                    <CheckCircle
                      className="w-5 h-5"
                      style={{ color: tokens.metSignal }}
                    />
                  ) : (
                    <XCircle
                      className="w-5 h-5"
                      style={{ color: tokens.notMetSignal }}
                    />
                  )}
                </span>
              ) : (
                <input
                  id={criterionId}
                  type="checkbox"
                  checked={item.met}
                  onChange={(e) => handleToggle(item.id, e.target.checked)}
                  className="flex-shrink-0 w-5 h-5 rounded border-2 cursor-pointer
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1
                    accent-current"
                  style={
                    {
                      borderColor: item.met ? tokens.metSignal : tokens.notMetSignal,
                      backgroundColor: item.met ? tokens.metSignal : 'transparent',
                      accentColor: tokens.metSignal,
                      minWidth: '20px',
                      minHeight: '20px',
                    } as React.CSSProperties
                  }
                  aria-describedby={descriptionId}
                  aria-label={item.label}
                />
              )}

              {/* Label + optional value/threshold */}
              <div className="flex-1 min-w-0 flex items-center gap-2 flex-wrap">
                <span
                  className="text-sm font-medium truncate"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  {item.label}
                </span>
                {item.value && item.threshold && (
                  <span
                    className="text-xs tabular-nums whitespace-nowrap"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    <span
                      style={{
                        color: item.met
                          ? tokens.metOnSurface
                          : tokens.notMetOnSurface,
                        fontWeight: 600,
                      }}
                    >
                      {item.value}
                    </span>
                    <span> / {item.threshold}</span>
                  </span>
                )}
              </div>

              {/* Status indicator */}
              <span
                className={`flex-shrink-0 flex items-center gap-1 text-xs font-semibold ${
                  readOnly ? '' : 'opacity-0 group-hover:opacity-100 transition-opacity'
                }`}
                style={{ color: item.met ? tokens.metOnSurface : tokens.notMetOnSurface }}
                aria-hidden="true"
              >
                {item.met ? (
                  <CheckCircle className="w-3.5 h-3.5" />
                ) : (
                  <XCircle className="w-3.5 h-3.5" />
                )}
                <span>{item.met ? 'Atendido' : 'Não atendido'}</span>
              </span>
            </label>
          </li>
        );

        // Wrap in tooltip if description exists
        if (item.description && descriptionId) {
          return (
            <ClinicalTooltip
              key={item.id}
              term={item.label}
            >
              <div
                id={descriptionId}
                className="sr-only"
              >
                {item.description}
              </div>
              {criterionContent}
            </ClinicalTooltip>
          );
        }

        return criterionContent;
      })}
    </ul>
  );
}
