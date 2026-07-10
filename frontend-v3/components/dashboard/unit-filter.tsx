'use client';

import { cn } from '@/lib/utils';

interface UnitFilterProps {
  units: string[];
  selected: string | null;
  onChange: (unit: string | null) => void;
}

export function UnitFilter({ units, selected, onChange }: UnitFilterProps) {
  if (!units || units.length === 0) return null;

  const allUnits = [null, ...units] as const;

  return (
    <nav
      role="tablist"
      aria-label="Filtrar por unidade"
      className="flex items-center gap-1"
    >
      {allUnits.map((unit) => {
        const isSelected = unit === selected;
        const label = unit ?? 'Todos';

        return (
          <button
            key={unit ?? '__all__'}
            role="tab"
            aria-selected={isSelected}
            aria-label={unit ? `Filtrar por ${unit}` : 'Mostrar todas unidades'}
            tabIndex={isSelected ? 0 : -1}
            onClick={() => onChange(unit)}
            className={cn(
              'px-3 py-1.5 text-sm font-medium rounded-[var(--radius-sm)] transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
            )}
            style={{
              backgroundColor: isSelected ? 'var(--surface-overlay)' : 'transparent',
              color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
              borderColor: isSelected ? 'var(--border-default)' : 'transparent',
              borderWidth: '1px',
              borderStyle: 'solid',
            }}
          >
            {label}
          </button>
        );
      })}
    </nav>
  );
}
