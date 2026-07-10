'use client';

import { GitBranch, ChevronDown, ChevronRight, Layers, ListChecks } from 'lucide-react';
import type { Pathway } from '@/lib/api';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface PathwayDefCardProps {
  pathway: Pathway;
  isExpanded: boolean;
  onToggle: () => void;
}

// ---------------------------------------------------------------------------
// PathwayDefCard
// ---------------------------------------------------------------------------

export function PathwayDefCard({
  pathway,
  isExpanded,
  onToggle,
}: PathwayDefCardProps) {
  const stateCount = pathway.states?.length ?? 0;
  const criteriaCount = pathway.criteria?.length ?? 0;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onToggle();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-expanded={isExpanded}
      aria-label={`${pathway.name} — ${stateCount} estados, ${criteriaCount} critérios. Clique para ${isExpanded ? 'recolher' : 'expandir'} detalhes`}
      onClick={onToggle}
      onKeyDown={handleKeyDown}
      className={`
        group relative flex flex-col gap-3 p-4 rounded-lg border cursor-pointer
        transition-all duration-150 select-none outline-none
        focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2
        focus-visible:ring-offset-[var(--surface-canvas)]
        ${isExpanded
          ? 'border-[var(--severity-normal)] bg-[var(--severity-normal-wash)] shadow-sm'
          : 'border-[var(--border-default)] bg-[var(--surface-raised)] hover:border-[var(--text-secondary)] hover:bg-[var(--surface-overlay)]'
        }
      `}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          {/* Icon */}
          <div className={`
            flex items-center justify-center h-9 w-9 rounded-lg shrink-0
            transition-colors
            ${isExpanded
              ? 'bg-[var(--severity-normal)] text-[var(--surface-canvas)]'
              : 'bg-[var(--surface-overlay)] text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]'
            }
          `}>
            <GitBranch className="h-4.5 w-4.5" />
          </div>

          {/* Name + description */}
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-[var(--text-primary)] truncate leading-snug">
              {pathway.name}
            </h3>
            {pathway.slug && (
              <p className="text-xs text-[var(--text-secondary)] font-mono mt-0.5 truncate">
                {pathway.slug}
              </p>
            )}
            {pathway.description && (
              <p className="text-xs text-[var(--text-secondary)] mt-1 line-clamp-2 leading-relaxed">
                {pathway.description}
              </p>
            )}
          </div>
        </div>

        {/* Toggle chevron */}
        <div className="shrink-0 mt-1">
          {isExpanded
            ? <ChevronDown className="h-4 w-4 text-[var(--severity-normal)]" />
            : <ChevronRight className="h-4 w-4 text-[var(--text-secondary)] group-hover:text-[var(--text-primary)] transition-colors" />
          }
        </div>
      </div>

      {/* Footer badges */}
      <div className="flex items-center gap-3 text-xs">
        {/* Status badge */}
        <span className={`
          inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium
          ${pathway.active !== false
            ? 'bg-[var(--severity-normal-wash)] text-[var(--severity-normal)]'
            : 'bg-[var(--surface-overlay)] text-[var(--text-secondary)]'
          }
        `}>
          <span className={`
            h-1.5 w-1.5 rounded-full
            ${pathway.active !== false ? 'bg-[var(--severity-normal)]' : 'bg-[var(--text-secondary)]'}
          `} />
          {pathway.active !== false ? 'Ativa' : 'Inativa'}
        </span>

        {/* States badge */}
        <span className="inline-flex items-center gap-1 text-[var(--text-secondary)]">
          <Layers className="h-3 w-3" />
          {stateCount} {stateCount === 1 ? 'estado' : 'estados'}
        </span>

        {/* Criteria badge */}
        <span className="inline-flex items-center gap-1 text-[var(--text-secondary)]">
          <ListChecks className="h-3 w-3" />
          {criteriaCount} {criteriaCount === 1 ? 'critério' : 'critérios'}
        </span>
      </div>
    </div>
  );
}
