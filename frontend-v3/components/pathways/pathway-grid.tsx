'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { Loader2, AlertTriangle, Search, ToggleLeft, ToggleRight } from 'lucide-react';
import { fetchPathways } from '@/lib/api';
import type { Pathway } from '@/lib/api';
import { PathwayDefCard } from './pathway-def-card';
import { PathwayDetail } from './pathway-detail';

// ---------------------------------------------------------------------------
// States
// ---------------------------------------------------------------------------

function GridLoading() {
  return (
    <div
      className="flex flex-col items-center justify-center py-20 gap-3 text-[var(--text-secondary)]"
      role="status"
      aria-label="Carregando trilhas clínicas"
    >
      <Loader2 className="h-8 w-8 animate-spin" />
      <span className="text-sm">Carregando catálogo de trilhas...</span>
    </div>
  );
}

function GridError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      className="flex flex-col items-center justify-center py-20 gap-4"
      role="alert"
      aria-label="Erro ao carregar trilhas"
    >
      <AlertTriangle className="h-10 w-10 text-[var(--severity-urgent)]" />
      <div className="text-center">
        <p className="text-sm font-medium text-[var(--text-primary)]">
          Erro ao carregar trilhas
        </p>
        <p className="text-xs text-[var(--text-secondary)] mt-1 max-w-md">
          {message}
        </p>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="px-4 py-2 text-sm font-medium rounded-md bg-[var(--surface-overlay)] text-[var(--text-primary)] hover:bg-[var(--surface-raised)] border border-[var(--border-default)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--severity-normal)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--surface-canvas)] outline-none"
        aria-label="Tentar carregar novamente"
      >
        Tentar novamente
      </button>
    </div>
  );
}

function GridEmpty({ activeOnly, onToggle }: { activeOnly: boolean; onToggle: () => void }) {
  return (
    <div
      className="flex flex-col items-center justify-center py-20 gap-4"
      role="status"
      aria-label="Nenhuma trilha encontrada"
    >
      <Search className="h-10 w-10 text-[var(--text-secondary)] opacity-40" />
      <div className="text-center">
        <p className="text-sm font-medium text-[var(--text-primary)]">
          Nenhuma trilha encontrada
        </p>
        <p className="text-xs text-[var(--text-secondary)] mt-1">
          {activeOnly
            ? 'Não há trilhas ativas no momento. Experimente mostrar todas as trilhas.'
            : 'O catálogo de trilhas está vazio.'
          }
        </p>
      </div>
      {activeOnly && (
        <button
          type="button"
          onClick={onToggle}
          className="px-4 py-2 text-sm font-medium rounded-md bg-[var(--surface-overlay)] text-[var(--text-primary)] hover:bg-[var(--surface-raised)] border border-[var(--border-default)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--severity-normal)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--surface-canvas)] outline-none"
          aria-label="Mostrar todas as trilhas"
        >
          Mostrar todas as trilhas
        </button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// PathwayGrid
// ---------------------------------------------------------------------------

export function PathwayGrid() {
  const [activeOnly, setActiveOnly] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const {
    data,
    error,
    isLoading,
    mutate,
  } = useSWR(
    ['pathways', activeOnly],
    () => fetchPathways(activeOnly),
    {
      revalidateOnFocus: false,
      dedupingInterval: 30_000,
    },
  );

  const pathways: Pathway[] = data?.items ?? [];
  const total = data?.total ?? 0;

  const handleToggleExpand = (id: number) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const handleToggleActive = () => {
    setActiveOnly((prev) => !prev);
    setExpandedId(null);
  };

  const handleRetry = () => {
    mutate();
  };

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Trilhas Clínicas
          </h1>
          {!isLoading && !error && (
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              {total} {total === 1 ? 'trilha' : 'trilhas'} {activeOnly ? 'ativas' : 'cadastradas'}
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={handleToggleActive}
          className={`
            flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border
            transition-all duration-150 outline-none
            focus-visible:ring-2 focus-visible:ring-[var(--severity-normal)] focus-visible:ring-offset-1
            focus-visible:ring-offset-[var(--surface-canvas)]
            ${activeOnly
              ? 'border-[var(--severity-normal)] bg-[var(--severity-normal-wash)] text-[var(--severity-normal)]'
              : 'border-[var(--border-default)] bg-[var(--surface-raised)] text-[var(--text-secondary)] hover:border-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }
          `}
          aria-label={activeOnly ? 'Mostrar todas as trilhas' : 'Mostrar apenas ativas'}
          aria-pressed={activeOnly}
        >
          {activeOnly ? <ToggleRight className="h-4 w-4" /> : <ToggleLeft className="h-4 w-4" />}
          {activeOnly ? 'Ativas' : 'Todas'}
        </button>
      </div>

      {/* Loading */}
      {isLoading && <GridLoading />}

      {/* Error */}
      {error && !isLoading && (
        <GridError
          message={error instanceof Error ? error.message : 'Erro desconhecido'}
          onRetry={handleRetry}
        />
      )}

      {/* Empty */}
      {!isLoading && !error && pathways.length === 0 && (
        <GridEmpty activeOnly={activeOnly} onToggle={handleToggleActive} />
      )}

      {/* Grid */}
      {!isLoading && !error && pathways.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {pathways.map((pathway) => (
            <div key={pathway.id}>
              <PathwayDefCard
                pathway={pathway}
                isExpanded={expandedId === pathway.id}
                onToggle={() => handleToggleExpand(pathway.id)}
              />
              {expandedId === pathway.id && (
                <PathwayDetail pathway={pathway} />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
