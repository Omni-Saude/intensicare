'use client';

import { useState, useCallback } from 'react';
import { Search, X, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AlertStatusFilter, SeverityLevel } from '@/lib/api';

export interface AlertFilterValues {
  severity: SeverityLevel | '';
  // Mirrors the backend contract's AlertStatusFilter exactly, so page.tsx
  // can pass filters.status straight through to fetchAlerts without
  // translation. 'all' is what lets the user review processed alerts
  // (acknowledged/escalated/resolved) that the default 'active' view hides.
  status: AlertStatusFilter;
  unit: string;
  pathway: string;
  period: 'all' | '1h' | '6h' | '24h' | '7d';
}

const DEFAULT_STATUS: AlertStatusFilter = 'active';

interface FilterBarProps {
  filters: AlertFilterValues;
  onChange: (filters: AlertFilterValues) => void;
}

const SEVERITY_OPTIONS: { value: SeverityLevel | ''; label: string }[] = [
  { value: '', label: 'Todas severidades' },
  { value: 'normal', label: 'Normal' },
  { value: 'watch', label: 'Observação' },
  { value: 'urgent', label: 'Urgente' },
  { value: 'critical', label: 'Crítico' },
];

const STATUS_OPTIONS: { value: AlertStatusFilter; label: string }[] = [
  { value: 'all', label: 'Todos status' },
  { value: 'active', label: 'Pendentes' },
  { value: 'acknowledged', label: 'Reconhecidos' },
  { value: 'escalated', label: 'Escalados' },
  { value: 'resolved', label: 'Resolvidos' },
];

const PERIOD_OPTIONS = [
  { value: 'all', label: 'Qualquer período' },
  { value: '1h', label: 'Última hora' },
  { value: '6h', label: 'Últimas 6h' },
  { value: '24h', label: 'Últimas 24h' },
  { value: '7d', label: 'Últimos 7 dias' },
];

export function FilterBar({ filters, onChange }: FilterBarProps) {
  const [showExtra, setShowExtra] = useState(false);

  const update = useCallback(
    (patch: Partial<AlertFilterValues>) => {
      onChange({ ...filters, ...patch });
    },
    [filters, onChange],
  );

  const clearFilters = useCallback(() => {
    onChange({
      severity: '',
      status: DEFAULT_STATUS,
      unit: '',
      pathway: '',
      period: 'all',
    });
  }, [onChange]);

  const hasActiveFilters =
    filters.severity !== '' ||
    filters.status !== DEFAULT_STATUS ||
    filters.unit !== '' ||
    filters.pathway !== '' ||
    filters.period !== 'all';

  return (
    <div
      className="flex flex-col gap-3 rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-4"
      role="search"
      aria-label="Filtros de alertas"
    >
      {/* Primary row — always visible */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Severidade */}
        <div className="flex-1 min-w-[140px]">
          <select
            value={filters.severity}
            onChange={(e) =>
              update({ severity: e.target.value as SeverityLevel | '' })
            }
            className={cn(
              'w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)]',
              'h-8 px-2.5 text-xs text-[var(--text-primary)]',
              'focus:outline-none focus:border-[var(--severity-watch)]',
              'appearance-none cursor-pointer',
            )}
            aria-label="Filtrar por severidade"
          >
            {SEVERITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div className="flex-1 min-w-[120px]">
          <select
            value={filters.status}
            onChange={(e) =>
              update({ status: e.target.value as AlertFilterValues['status'] })
            }
            className={cn(
              'w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)]',
              'h-8 px-2.5 text-xs text-[var(--text-primary)]',
              'focus:outline-none focus:border-[var(--severity-watch)]',
              'appearance-none cursor-pointer',
            )}
            aria-label="Filtrar por status"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Período */}
        <div className="flex-1 min-w-[120px]">
          <select
            value={filters.period}
            onChange={(e) =>
              update({ period: e.target.value as AlertFilterValues['period'] })
            }
            className={cn(
              'w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)]',
              'h-8 px-2.5 text-xs text-[var(--text-primary)]',
              'focus:outline-none focus:border-[var(--severity-watch)]',
              'appearance-none cursor-pointer',
            )}
            aria-label="Filtrar por período"
          >
            {PERIOD_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Toggle extra filters */}
        <button
          onClick={() => setShowExtra(!showExtra)}
          className={cn(
            'inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-xs',
            'border border-[var(--border-default)] text-[var(--text-secondary)]',
            'hover:text-[var(--text-primary)] hover:border-[var(--text-primary)]',
            'transition-colors',
          )}
          aria-label={showExtra ? 'Ocultar filtros extras' : 'Mostrar filtros extras'}
          aria-expanded={showExtra}
        >
          <Filter className="h-3.5 w-3.5" aria-hidden="true" />
          Filtros
          {hasActiveFilters && (
            <span className="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--severity-urgent)] text-2xs text-[var(--surface-canvas)]">
              !
            </span>
          )}
        </button>

        {/* Clear */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-[var(--severity-critical)] hover:bg-[var(--severity-critical-wash)] transition-colors"
            aria-label="Limpar todos os filtros"
          >
            <X className="h-3.5 w-3.5" aria-hidden="true" />
            Limpar
          </button>
        )}
      </div>

      {/* Extended row — togglable */}
      {showExtra && (
        <div className="flex flex-wrap items-center gap-2 border-t border-[var(--border-default)] pt-3">
          {/* Unidade */}
          <div className="flex-1 min-w-[140px]">
            <label
              className="mb-1 block text-2xs font-medium uppercase tracking-wider text-[var(--text-secondary)]"
              htmlFor="filter-unit"
            >
              Unidade
            </label>
            <div className="relative">
              <Search
                className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-[var(--text-secondary)]"
                aria-hidden="true"
              />
              <input
                id="filter-unit"
                type="text"
                value={filters.unit}
                onChange={(e) => update({ unit: e.target.value })}
                placeholder="Ex: UTI 1, Enfermaria…"
                className={cn(
                  'w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)]',
                  'h-8 pl-7 pr-2.5 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]',
                  'focus:outline-none focus:border-[var(--severity-watch)]',
                )}
              />
            </div>
          </div>

          {/* Trilha */}
          <div className="flex-1 min-w-[140px]">
            <label
              className="mb-1 block text-2xs font-medium uppercase tracking-wider text-[var(--text-secondary)]"
              htmlFor="filter-pathway"
            >
              Trilha
            </label>
            <div className="relative">
              <Search
                className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-[var(--text-secondary)]"
                aria-hidden="true"
              />
              <input
                id="filter-pathway"
                type="text"
                value={filters.pathway}
                onChange={(e) => update({ pathway: e.target.value })}
                placeholder="Ex: SEPSE, DVA…"
                className={cn(
                  'w-full rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)]',
                  'h-8 pl-7 pr-2.5 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]',
                  'focus:outline-none focus:border-[var(--severity-watch)]',
                )}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
