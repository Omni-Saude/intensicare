'use client';

import type { AlertInfo } from '@/lib/api';
import { severityColor } from './severity-glow';
import { cn } from '@/lib/utils';
import { AlertTriangle, Bell, Clock, Check, ArrowUp, GitBranch } from 'lucide-react';

interface AlertItemProps {
  alert: AlertInfo;
  onAcknowledge?: (id: number) => void;
  onEscalate?: (id: number) => void;
  disabled?: boolean;
}

const SEVERITY_LABELS: Record<string, string> = {
  normal: 'Normal',
  watch: 'Observação',
  urgent: 'Urgente',
  critical: 'Crítico',
};

export function AlertItem({ alert, onAcknowledge, onEscalate, disabled }: AlertItemProps) {
  const color = severityColor(alert.severity);
  const isResolved = !!alert.resolved_at;
  const isAcknowledged = !!alert.acknowledged_at;

  return (
    <div
      className={cn(
        'rounded-lg border bg-[var(--surface-raised)] p-4 transition-all',
        isResolved ? 'opacity-60' : '',
      )}
      style={{
        borderColor: isResolved ? 'var(--border-default)' : color,
        borderLeftWidth: '3px',
        borderLeftColor: color,
      }}
      role="article"
      aria-label={`Alerta: ${alert.title}`}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle
          className="h-5 w-5 shrink-0 mt-0.5"
          style={{ color }}
          aria-hidden="true"
        />

        <div className="flex-1 min-w-0 space-y-1.5">
          {/* Title row */}
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">
              {alert.title}
            </h3>
            <span
              className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
              style={{
                backgroundColor: `${color}1A`,
                color,
                border: `1px solid ${color}33`,
              }}
            >
              {SEVERITY_LABELS[alert.severity] ?? alert.severity}
            </span>
            {isResolved && (
              <span className="inline-flex items-center gap-1 rounded-full bg-[var(--severity-normal-wash)] px-2 py-0.5 text-xs text-[var(--severity-normal)]">
                <Check className="h-3 w-3" />
                Resolvido
              </span>
            )}
          </div>

          {/* Message */}
          <p className="text-sm text-[var(--text-secondary)] line-clamp-2">
            {alert.message}
          </p>

          {/* Meta */}
          <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
            {alert.pathway_name && (
              <span className="inline-flex items-center gap-1">
                <GitBranch className="h-3 w-3" />
                {alert.pathway_name}
              </span>
            )}
            <span className="inline-flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(alert.created_at).toLocaleString('pt-BR')}
            </span>
          </div>
        </div>

        {/* Actions */}
        {!isResolved && (
          <div className="flex flex-col gap-1.5 shrink-0">
            {!isAcknowledged && onAcknowledge && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAcknowledge(alert.id);
                }}
                disabled={disabled}
                className="inline-flex items-center gap-1 rounded-md border border-[var(--border-default)] px-2 py-1 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--text-secondary)] transition-colors disabled:opacity-50"
                aria-label={`Confirmar alerta: ${alert.title}`}
              >
                <Bell className="h-3 w-3" />
                Confirmar
              </button>
            )}
            {onEscalate && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEscalate(alert.id);
                }}
                disabled={disabled}
                className="inline-flex items-center gap-1 rounded-md border border-[var(--severity-urgent)] px-2 py-1 text-xs text-[var(--severity-urgent)] hover:bg-[var(--severity-urgent-wash)] transition-colors disabled:opacity-50"
                aria-label={`Escalar alerta: ${alert.title}`}
              >
                <ArrowUp className="h-3 w-3" />
                Escalar
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
