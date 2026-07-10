'use client';

import { FileClock, Wrench } from 'lucide-react';

export function AuditLog() {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 py-16 px-4 rounded-[var(--radius-lg)]"
      style={{
        backgroundColor: 'var(--surface-raised)',
        borderColor: 'var(--border-default)',
        borderWidth: '1px',
        borderStyle: 'solid',
      }}
      role="status"
      aria-label="Registro de auditoria — em breve"
    >
      <div
        className="flex items-center justify-center size-16 rounded-full"
        style={{ backgroundColor: 'var(--surface-overlay)' }}
      >
        <FileClock
          className="size-8"
          style={{ color: 'var(--text-secondary)' }}
          aria-hidden="true"
        />
      </div>
      <div className="text-center">
        <h3
          className="text-lg font-semibold mb-1"
          style={{ color: 'var(--text-primary)' }}
        >
          Registro de Auditoria
        </h3>
        <p
          className="text-sm max-w-md"
          style={{ color: 'var(--text-secondary)' }}
        >
          O registro de auditoria estará disponível em breve. Esta seção exibirá
          o histórico de ações administrativas, alterações de configuração e
          eventos de segurança.
        </p>
      </div>
      <div
        className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium"
        style={{
          backgroundColor: 'var(--severity-watch-wash)',
          color: 'var(--severity-watch)',
        }}
      >
        <Wrench className="size-3.5" aria-hidden="true" />
        Em desenvolvimento
      </div>
    </div>
  );
}
