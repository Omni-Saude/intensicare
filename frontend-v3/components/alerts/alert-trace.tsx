'use client';

import { GitBranch, Activity, Gauge, ListChecks } from 'lucide-react';
import type { AlertInfo } from '@/lib/api';

interface AlertTraceProps {
  alert: AlertInfo;
}

/**
 * AlertTrace — rastreabilidade expandida:
 * alerta ← threshold ← score ← critério
 *
 * Como o backend ainda não expõe uma API de trace granular,
 * exibimos os dados disponíveis no alerta com a estrutura
 * hierárquica visual esperada.
 */
export function AlertTrace({ alert }: AlertTraceProps) {
  const traceSteps = [
    {
      icon: ListChecks,
      label: 'Critério avaliado',
      value: alert.type || '—',
      detail: alert.message,
    },
    {
      icon: Gauge,
      label: 'Score calculado',
      value: alert.severity.toUpperCase(),
      detail: `Severidade: ${alert.severity}`,
    },
    {
      icon: Activity,
      label: 'Threshold atingido',
      value: alert.title,
      detail: alert.pathway_name
        ? `Trilha: ${alert.pathway_name}`
        : 'Sem trilha associada',
    },
    {
      icon: GitBranch,
      label: 'Alerta gerado',
      value: `Alert #${alert.id}`,
      detail: new Date(alert.created_at).toLocaleString('pt-BR'),
    },
  ];

  return (
    <div
      className="mt-3 border-t border-[var(--border-default)] pt-3"
      role="region"
      aria-label="Rastreabilidade do alerta"
    >
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        Rastreabilidade
      </h4>
      <div className="flex flex-wrap items-start gap-2">
        {traceSteps.map((step, i) => (
          <div key={i} className="flex items-center gap-0">
            <div
              className="flex min-w-[140px] flex-col rounded-lg border border-[var(--border-default)] bg-[var(--surface-canvas)] p-2.5"
              role="listitem"
            >
              <div className="mb-1 flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
                <step.icon className="h-3 w-3" aria-hidden="true" />
                {step.label}
              </div>
              <div className="text-sm font-medium text-[var(--text-primary)]">
                {step.value}
              </div>
              <div className="mt-0.5 text-xs text-[var(--text-secondary)]">
                {step.detail}
              </div>
            </div>
            {i < traceSteps.length - 1 && (
              <span
                className="mx-1 mt-4 text-[var(--text-secondary)]"
                aria-hidden="true"
              >
                ←
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
