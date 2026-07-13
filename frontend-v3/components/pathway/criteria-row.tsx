'use client';

import type { PathwayCriteria } from '@/lib/api';
import { SeverityIcon } from './severity-icon';
import { CriteriaValue } from './criteria-value';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface CriteriaRowProps {
  criterion: PathwayCriteria;
  isExpanded: boolean;
  onToggle: () => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso?: string): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
}

function metLabel(met: boolean | null | undefined): string {
  if (met === true) return 'Atendido';
  if (met === false) return 'Não atendido';
  return 'Pendente';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CriteriaRow({ criterion, isExpanded, onToggle }: CriteriaRowProps) {
  const {
    name,
    category,
    description,
    unit,
    normal_range: normalRange,
    alert_threshold: threshold,
    met,
    value,
    evaluated_at: evaluatedAt,
  } = criterion;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onToggle();
    }
  };

  return (
    <div className="border-b border-[var(--border-default)] last:border-b-0" role="listitem">
      {/* Collapsible header */}
      <button
        type="button"
        role="button"
        aria-expanded={isExpanded}
        aria-label={`Critério ${name}: ${metLabel(met)}${value ? `, valor ${value} ${unit ?? ''}` : ''}`}
        onClick={onToggle}
        onKeyDown={handleKeyDown}
        className={cn(
          'flex w-full items-center gap-3 px-4 py-3 text-left transition-colors',
          'hover:bg-[var(--surface-overlay)]',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[var(--severity-watch)]',
        )}
      >
        {/* Severity / status icon */}
        <SeverityIcon met={met} severity={null} criterionName={name} className="mt-0.5" />

        {/* Name + category */}
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium text-[var(--text-primary)] block truncate">
            {name}
          </span>
          {category && (
            <span className="text-xs text-[var(--text-secondary)] block">
              {category}
            </span>
          )}
        </div>

        {/* Value */}
        <div className="hidden sm:block text-right shrink-0">
          <CriteriaValue
            value={value ?? null}
            unit={unit}
            threshold={threshold}
            normalRange={normalRange}
          />
        </div>

        {/* Expand chevron */}
        <ChevronDown
          className={cn(
            'h-4 w-4 text-[var(--text-secondary)] shrink-0 transition-transform duration-200',
            isExpanded && 'rotate-180',
          )}
          aria-hidden="true"
        />
      </button>

      {/* Mobile value (visible only below sm) */}
      <div className="sm:hidden px-4 pb-1 pl-13">
        <CriteriaValue
          value={value ?? null}
          unit={unit}
          threshold={threshold}
          normalRange={normalRange}
        />
      </div>

      {/* Expanded detail */}
      {isExpanded && (
        <div
          className="px-4 pb-4 pl-13 space-y-2 text-sm text-[var(--text-secondary)]"
          role="region"
          aria-label={`Detalhes do critério ${name}`}
        >
          {description && (
            <p>{description}</p>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-1 text-xs">
            {normalRange && (
              <div>
                <span className="font-medium text-[var(--text-primary)]">Faixa normal:</span>{' '}
                {normalRange}
              </div>
            )}

            {threshold && (
              <div>
                <span className="font-medium text-[var(--text-primary)]">Limiar de alerta:</span>{' '}
                {threshold}
              </div>
            )}

            {unit && (
              <div>
                <span className="font-medium text-[var(--text-primary)]">Unidade:</span>{' '}
                {unit}
              </div>
            )}
          </div>

          {/* Severity band indicator */}
          <div className="flex items-center gap-2 pt-1">
            <span className="text-xs font-medium text-[var(--text-primary)]">Estado:</span>
            <SeverityIcon met={met} severity={null} />
            <span className="text-xs">{metLabel(met)}</span>
          </div>

          {evaluatedAt && (
            <p className="text-xs text-[var(--text-secondary)] pt-1">
              Avaliado em: {formatDate(evaluatedAt)}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
