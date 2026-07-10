'use client';

import type { AlertInfo } from '@/lib/api';
import { AlertItem } from './alert-item';
import { BellOff } from 'lucide-react';
import { useState } from 'react';

interface AlertsPanelProps {
  alerts: AlertInfo[];
  isLoading?: boolean;
  error?: string | null;
  onAcknowledge?: (id: number) => Promise<void>;
  onEscalate?: (id: number) => Promise<void>;
}

export function AlertsPanel({ alerts, isLoading, error, onAcknowledge, onEscalate }: AlertsPanelProps) {
  const [actingIds, setActingIds] = useState<Set<number>>(new Set());

  const handleAcknowledge = async (id: number) => {
    if (!onAcknowledge) return;
    setActingIds((prev) => new Set(prev).add(id));
    try {
      await onAcknowledge(id);
    } finally {
      setActingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const handleEscalate = async (id: number) => {
    if (!onEscalate) return;
    setActingIds((prev) => new Set(prev).add(id));
    try {
      await onEscalate(id);
    } finally {
      setActingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  return (
    <section aria-label="Alertas do paciente" className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        Alertas
      </h2>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-[120px] animate-pulse rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]"
              aria-hidden="true"
            />
          ))}
        </div>
      )}

      {error && (
        <div
          className="rounded-lg border border-[var(--severity-critical)] bg-[var(--severity-critical-wash)] p-4 text-sm text-[var(--severity-critical)]"
          role="alert"
        >
          Erro ao carregar alertas: {error}
        </div>
      )}

      {!isLoading && !error && alerts.length === 0 && (
        <div className="rounded-lg border border-dashed border-[var(--border-default)] bg-[var(--surface-raised)] p-6 text-center">
          <BellOff className="mx-auto h-8 w-8 text-[var(--text-secondary)] mb-2" aria-hidden="true" />
          <p className="text-sm text-[var(--text-secondary)]">
            Nenhum alerta ativo para este paciente.
          </p>
        </div>
      )}

      {!isLoading && !error && alerts.length > 0 && (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onAcknowledge={onAcknowledge ? handleAcknowledge : undefined}
              onEscalate={onEscalate ? handleEscalate : undefined}
              disabled={actingIds.has(alert.id)}
            />
          ))}
        </div>
      )}
    </section>
  );
}
