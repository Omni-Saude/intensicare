'use client';

import { useState } from 'react';
import { Layers, ListChecks, ChevronDown, ChevronRight, GitBranch, ArrowRight, AlertCircle } from 'lucide-react';
import type { Pathway, PathwayState, PathwayCriteria } from '@/lib/api';
import { YamlViewer } from './yaml-viewer';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface PathwayDetailProps {
  pathway: Pathway;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function groupCriteriaByCategory(criteria: PathwayCriteria[]): Map<string, PathwayCriteria[]> {
  const map = new Map<string, PathwayCriteria[]>();
  for (const c of criteria) {
    const cat = c.category || 'Geral';
    const existing = map.get(cat);
    if (existing) {
      existing.push(c);
    } else {
      map.set(cat, [c]);
    }
  }
  return map;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StateItem({ state, index }: { state: PathwayState; index: number }) {
  return (
    <div className="flex items-start gap-3 py-3 px-4 rounded-md bg-[var(--surface-canvas)] border border-[var(--border-default)]">
      {/* Order badge */}
      <div className={`
        flex items-center justify-center h-6 w-6 rounded-full text-xs font-bold shrink-0 mt-0.5
        ${state.is_terminal
          ? 'bg-[var(--severity-critical-wash)] text-[var(--severity-critical)]'
          : 'bg-[var(--surface-overlay)] text-[var(--text-secondary)]'
        }
      `}>
        {state.order ?? index + 1}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-[var(--text-primary)]">
            {state.name}
          </span>
          {state.is_terminal && (
            <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-2xs font-semibold uppercase tracking-wide bg-[var(--severity-critical-wash)] text-[var(--severity-critical)]">
              <AlertCircle className="h-2.5 w-2.5" />
              Terminal
            </span>
          )}
        </div>
        {state.description && (
          <p className="text-xs text-[var(--text-secondary)] mt-1 leading-relaxed">
            {state.description}
          </p>
        )}
      </div>
    </div>
  );
}

function CriteriaGroup({ category, criteria }: { category: string; criteria: PathwayCriteria[] }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 w-full px-4 py-2.5 bg-[var(--surface-overlay)] hover:bg-[var(--surface-raised)] transition-colors text-left"
        aria-expanded={isOpen}
        aria-label={`${isOpen ? 'Recolher' : 'Expandir'} critérios da categoria ${category}`}
      >
        {isOpen
          ? <ChevronDown className="h-3.5 w-3.5 text-[var(--text-secondary)]" />
          : <ChevronRight className="h-3.5 w-3.5 text-[var(--text-secondary)]" />
        }
        <span className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wide">
          {category}
        </span>
        <span className="text-2xs text-[var(--text-secondary)] ml-auto">
          {criteria.length} {criteria.length === 1 ? 'critério' : 'critérios'}
        </span>
      </button>

      {isOpen && (
        <div className="divide-y divide-[var(--border-default)]">
          {criteria.map((crit) => (
            <div
              key={crit.id}
              className="flex items-start gap-3 px-4 py-3 hover:bg-[var(--surface-overlay)] transition-colors"
            >
              <ArrowRight className="h-3.5 w-3.5 text-[var(--text-secondary)] mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <span className="text-sm text-[var(--text-primary)] block">
                  {crit.name}
                </span>
                {crit.description && (
                  <span className="text-xs text-[var(--text-secondary)] mt-0.5 line-clamp-2 leading-relaxed">
                    {crit.description}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {crit.unit && (
                  <span className="text-2xs text-[var(--text-secondary)] bg-[var(--surface-overlay)] px-1.5 py-0.5 rounded font-mono">
                    {crit.unit}
                  </span>
                )}
                {crit.normal_range && (
                  <span className="text-2xs text-[var(--severity-normal)] bg-[var(--severity-normal-wash)] px-1.5 py-0.5 rounded font-mono">
                    {crit.normal_range}
                  </span>
                )}
                {crit.alert_threshold && (
                  <span className="text-2xs text-[var(--severity-urgent)] bg-[var(--severity-urgent-wash)] px-1.5 py-0.5 rounded font-mono">
                    &ge; {crit.alert_threshold}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// PathwayDetail
// ---------------------------------------------------------------------------

type DetailTab = 'detail' | 'yaml';

export function PathwayDetail({ pathway }: PathwayDetailProps) {
  const [activeTab, setActiveTab] = useState<DetailTab>('detail');
  const criteriaByCategory = pathway.criteria
    ? groupCriteriaByCategory(pathway.criteria)
    : new Map<string, PathwayCriteria[]>();

  return (
    <div
      className="mt-2 rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] overflow-hidden"
      role="region"
      aria-label={`Detalhes da trilha ${pathway.name}`}
    >
      {/* Tab bar */}
      <div className="flex border-b border-[var(--border-default)] bg-[var(--surface-canvas)]">
        <button
          type="button"
          onClick={() => setActiveTab('detail')}
          className={`
            flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            border-b-2 -mb-[1px]
            ${activeTab === 'detail'
              ? 'border-[var(--severity-normal)] text-[var(--severity-normal)]'
              : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }
          `}
          role="tab"
          aria-selected={activeTab === 'detail'}
          aria-controls="pathway-detail-panel"
        >
          <ListChecks className="h-4 w-4" />
          Detalhes
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('yaml')}
          className={`
            flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            border-b-2 -mb-[1px]
            ${activeTab === 'yaml'
              ? 'border-[var(--severity-normal)] text-[var(--severity-normal)]'
              : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }
          `}
          role="tab"
          aria-selected={activeTab === 'yaml'}
          aria-controls="pathway-yaml-panel"
        >
          <GitBranch className="h-4 w-4" />
          YAML
        </button>
      </div>

      {/* Detail tab panel */}
      {activeTab === 'detail' && (
        <div
          id="pathway-detail-panel"
          role="tabpanel"
          aria-label="Detalhes da trilha"
          className="p-5 space-y-5"
        >
          {/* Description */}
          {pathway.description && (
            <div>
              <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide mb-2">
                Descrição
              </h4>
              <p className="text-sm text-[var(--text-primary)] leading-relaxed">
                {pathway.description}
              </p>
            </div>
          )}

          {/* States section */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Layers className="h-4 w-4 text-[var(--text-secondary)]" />
              <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide">
                Estados ({pathway.states?.length ?? 0})
              </h4>
            </div>

            {pathway.states && pathway.states.length > 0 ? (
              <div className="space-y-2">
                {pathway.states
                  .sort((a, b) => a.order - b.order)
                  .map((state, idx) => (
                    <StateItem key={state.id} state={state} index={idx} />
                  ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--text-secondary)] italic">
                Nenhum estado definido para esta trilha.
              </p>
            )}
          </div>

          {/* Criteria section */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ListChecks className="h-4 w-4 text-[var(--text-secondary)]" />
              <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wide">
                Critérios ({pathway.criteria?.length ?? 0})
              </h4>
            </div>

            {criteriaByCategory.size > 0 ? (
              <div className="space-y-2">
                {Array.from(criteriaByCategory.entries()).map(([category, criteria]) => (
                  <CriteriaGroup key={category} category={category} criteria={criteria} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--text-secondary)] italic">
                Nenhum critério definido para esta trilha.
              </p>
            )}
          </div>
        </div>
      )}

      {/* YAML tab panel */}
      {activeTab === 'yaml' && (
        <div
          id="pathway-yaml-panel"
          role="tabpanel"
          aria-label="Definição YAML da trilha"
          className="p-5"
        >
          <YamlViewer
            pathway={pathway}
            isLoading={false}
          />
        </div>
      )}
    </div>
  );
}
