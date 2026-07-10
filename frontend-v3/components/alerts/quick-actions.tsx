'use client';

import { useState } from 'react';
import { CheckCircle, ArrowUpCircle, CircleCheckBig, Loader2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  acknowledgeAlert,
  escalateAlert,
  resolveAlert,
  type AlertInfo,
} from '@/lib/api';

interface QuickActionsProps {
  alert: AlertInfo;
  onAction: (updated: AlertInfo) => void;
  onError: (message: string) => void;
}

type ActionState = 'idle' | 'loading' | 'resolving';

export function QuickActions({ alert, onAction, onError }: QuickActionsProps) {
  const [actionState, setActionState] = useState<ActionState>('idle');
  const [showResolveInput, setShowResolveInput] = useState(false);
  const [resolution, setResolution] = useState('');

  const handleAcknowledge = async () => {
    if (alert.acknowledged_at) return;
    setActionState('loading');
    try {
      const updated = await acknowledgeAlert(alert.id);
      onAction(updated);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Erro ao reconhecer alerta');
    } finally {
      setActionState('idle');
    }
  };

  const handleEscalate = async () => {
    setActionState('loading');
    try {
      const updated = await escalateAlert(alert.id);
      onAction(updated);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Erro ao escalar alerta');
    } finally {
      setActionState('idle');
    }
  };

  const handleDismiss = async () => {
    setActionState('loading');
    try {
      const updated = await resolveAlert(alert.id, 'não procede');
      onAction(updated);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Erro ao marcar alerta como não procedente');
    } finally {
      setActionState('idle');
    }
  };

  const handleResolve = async () => {
    if (!resolution.trim()) return;
    setActionState('loading');
    try {
      const updated = await resolveAlert(alert.id, resolution.trim());
      onAction(updated);
      setShowResolveInput(false);
      setResolution('');
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Erro ao resolver alerta');
    } finally {
      setActionState('idle');
    }
  };

  const isBusy = actionState === 'loading';

  if (alert.resolved_at) {
    return (
      <span className="text-xs text-[var(--severity-normal)] inline-flex items-center gap-1">
        <CircleCheckBig className="h-3.5 w-3.5" aria-hidden="true" />
        Resolvido
      </span>
    );
  }

  return (
    <div className="flex items-center gap-1" role="group" aria-label="Ações do alerta">
      {!alert.acknowledged_at && (
        <button
          onClick={handleAcknowledge}
          disabled={isBusy}
          className={cn(
            'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors',
            'bg-[var(--severity-normal-wash)] text-[var(--severity-normal)]',
            'hover:brightness-125 disabled:opacity-50 disabled:cursor-not-allowed',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
          )}
          aria-label="Reconhecer alerta"
          title="Reconhecer"
        >
          {isBusy ? (
            <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
          ) : (
            <CheckCircle className="h-3 w-3" aria-hidden="true" />
          )}
          <span className="hidden sm:inline">Reconhecer</span>
        </button>
      )}

      <button
        onClick={handleEscalate}
        disabled={isBusy}
        className={cn(
          'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors',
          'bg-[var(--severity-urgent-wash)] text-[var(--severity-urgent)]',
          'hover:brightness-125 disabled:opacity-50 disabled:cursor-not-allowed',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
          )}
          aria-label="Escalar alerta"
        title="Escalar"
      >
        {isBusy ? (
          <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
        ) : (
          <ArrowUpCircle className="h-3 w-3" aria-hidden="true" />
        )}
        <span className="hidden sm:inline">Escalar</span>
      </button>

      {!alert.acknowledged_at && (
        <button
          onClick={handleDismiss}
          disabled={isBusy}
          className={cn(
            'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors',
            'bg-[var(--surface-overlay)] text-[var(--text-secondary)]',
            'hover:brightness-125 disabled:opacity-50 disabled:cursor-not-allowed',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
          )}
          aria-label="Marcar alerta como não procedente"
          title="Não procede"
        >
          {isBusy ? (
            <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
          ) : (
            <XCircle className="h-3 w-3" aria-hidden="true" />
          )}
          <span className="hidden sm:inline">Não procede</span>
        </button>
      )}

      {!showResolveInput ? (
        <button
          onClick={() => setShowResolveInput(true)}
          disabled={isBusy}
          className={cn(
            'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors',
            'bg-[var(--severity-watch-wash)] text-[var(--severity-watch)]',
            'hover:brightness-125 disabled:opacity-50 disabled:cursor-not-allowed',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
          )}
          aria-label="Resolver alerta"
          title="Resolver"
        >
          <CircleCheckBig className="h-3 w-3" aria-hidden="true" />
          <span className="hidden sm:inline">Resolver</span>
        </button>
      ) : (
        <div className="flex items-center gap-1" role="group" aria-label="Formulário de resolução">
          <input
            type="text"
            value={resolution}
            onChange={(e) => setResolution(e.target.value)}
            placeholder="Resolução…"
            className={cn(
              'h-7 w-32 rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)]',
              'px-2 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]',
              'focus:outline-none focus:border-[var(--severity-watch)]',
            )}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleResolve();
              if (e.key === 'Escape') {
                setShowResolveInput(false);
                setResolution('');
              }
            }}
            autoFocus
            aria-label="Texto da resolução"
          />
          <button
            onClick={handleResolve}
            disabled={isBusy || !resolution.trim()}
            className="inline-flex items-center rounded-md bg-[var(--severity-normal-wash)] px-2 py-1 text-xs text-[var(--severity-normal)] hover:brightness-125 disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]"
            aria-label="Confirmar resolução"
          >
            {isBusy ? (
              <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
            ) : (
              'OK'
            )}
          </button>
          <button
            onClick={() => {
              setShowResolveInput(false);
              setResolution('');
            }}
            className="rounded-md px-1 py-1 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]"
            aria-label="Cancelar resolução"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
