'use client';

import { useRef } from 'react';
import { cn } from '@/lib/utils';

interface UnitFilterProps {
  units: string[];
  selected: string | null;
  onChange: (unit: string | null) => void;
}

export function UnitFilter({ units, selected, onChange }: UnitFilterProps) {
  // Roving tabindex per WAI-ARIA APG (Tabs pattern, manual activation):
  // https://www.w3.org/WAI/ARIA/apg/patterns/tabs/
  // Arrow keys only move DOM focus between tab buttons; they never call
  // onChange. Activation stays on Enter/Space/click (native <button>
  // behavior) so navigating the tabs with arrows can't fire N fetches —
  // selecting a tab here triggers fetchDashboard(unit) in the parent.
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([]);

  if (!units || units.length === 0) return null;

  const allUnits = [null, ...units] as const;
  // Array grows naturally via ref callbacks (line 68-70); no manual pruning needed

  const focusTab = (index: number) => {
    const count = allUnits.length;
    const nextIndex = ((index % count) + count) % count;
    buttonRefs.current[nextIndex]?.focus();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
    switch (event.key) {
      case 'ArrowRight':
        event.preventDefault();
        focusTab(index + 1);
        break;
      case 'ArrowLeft':
        event.preventDefault();
        focusTab(index - 1);
        break;
      case 'Home':
        event.preventDefault();
        focusTab(0);
        break;
      case 'End':
        event.preventDefault();
        focusTab(allUnits.length - 1);
        break;
      default:
        break;
    }
  };

  return (
    <nav
      role="tablist"
      aria-label="Filtrar por unidade"
      className="flex flex-wrap items-center gap-1"
    >
      {allUnits.map((unit, index) => {
        const isSelected = unit === selected;
        const label = unit ?? 'Todos';

        return (
          <button
            key={unit ?? '__all__'}
            ref={(el) => {
              buttonRefs.current[index] = el;
            }}
            role="tab"
            aria-selected={isSelected}
            aria-label={unit ? `Filtrar por ${unit}` : 'Mostrar todas unidades'}
            tabIndex={isSelected ? 0 : -1}
            onClick={() => onChange(unit)}
            onKeyDown={(event) => handleKeyDown(event, index)}
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
