'use client';

import { cn } from '@/lib/utils';
import type { AlertInfo } from '@/lib/api';
import { AlertRow } from './alert-row';

interface AlertTableProps {
  alerts: AlertInfo[];
  isLoading: boolean;
  isEmpty: boolean;
  error: string | null;
  onAlertUpdate: (updated: AlertInfo) => void;
  onError: (message: string) => void;
}

export function AlertTable({
  alerts,
  isLoading,
  isEmpty,
  error,
  onAlertUpdate,
  onError,
}: AlertTableProps) {
  // Loading state
  if (isLoading) {
    return (
      <div
        className="flex flex-col items-center justify-center py-16"
        role="status"
        aria-label="Carregando alertas"
      >
        <div className="flex items-center gap-2 text-[var(--text-secondary)]">
          <svg
            className="h-5 w-5 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span className="text-sm">Carregando alertas…</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-3 py-16"
        role="alert"
        aria-label="Erro ao carregar alertas"
      >
        <div className="rounded-full bg-[var(--severity-critical-wash)] p-3">
          <svg
            className="h-6 w-6 text-[var(--severity-critical)]"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
            />
          </svg>
        </div>
        <p className="text-sm text-[var(--severity-critical)] font-medium">
          Erro ao carregar alertas
        </p>
        <p className="text-xs text-[var(--text-secondary)]">{error}</p>
      </div>
    );
  }

  // Empty state
  if (isEmpty) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-3 py-16"
        role="status"
        aria-label="Nenhum alerta encontrado"
      >
        <div className="rounded-full bg-[var(--surface-overlay)] p-3">
          <svg
            className="h-6 w-6 text-[var(--text-secondary)]"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-sm text-[var(--text-secondary)]">Nenhum alerta encontrado</p>
        <p className="text-xs text-[var(--text-secondary)]">
          Ajuste os filtros ou aguarde novos alertas.
        </p>
      </div>
    );
  }

  return (
    <div
      className="flex flex-col gap-2"
      role="list"
      aria-label="Lista de alertas"
    >
      {/*
        Header — visual column guide for >=sm only (`hidden` below sm removes
        it from the accessibility tree too, not just the viewport). This is
        NOT the sole source of column meaning: AlertRow renders its own
        inline `sm:hidden` labels per field (WCAG 1.3.1) so info/relationships
        survive when this header disappears at <sm — see alert-row.tsx.
      */}
      <div className="hidden sm:flex items-center gap-3 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        <span className="w-4" aria-hidden="true" />
        <span className="w-[88px]">Severidade</span>
        <span className="w-[140px]">Paciente</span>
        <span className="w-[120px]">Trilha</span>
        <span className="flex-1">Mensagem</span>
        <span className="w-[120px]">Data</span>
        <span className="w-[100px]" />
        <span className="w-[180px] text-right">Ações</span>
      </div>

      {/* Alert rows */}
      {alerts.map((alert) => (
        <AlertRow
          key={alert.id}
          alert={alert}
          onAlertUpdate={onAlertUpdate}
          onError={onError}
        />
      ))}
    </div>
  );
}
