'use client';

import React, { useState } from 'react';
import {
  User,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  ArrowRightLeft,
} from 'lucide-react';
import type { HandoffMessage } from '@/lib/communication-types';
import { formatRelativeTime } from '@/lib/communication-types';

// ─── Props ──────────────────────────────────────────────────────────────────

interface HandoffMessageCardProps {
  message: HandoffMessage;
  onMarkRead?: (id: string) => void;
  isLoading?: boolean;
  error?: string | null;
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function HandoffMessageCard({
  message,
  onMarkRead,
  isLoading = false,
  error = null,
}: HandoffMessageCardProps) {
  const [sectionsOpen, setSectionsOpen] = useState<Record<string, boolean>>({
    b: false,
    a: false,
    r: false,
  });

  const toggleSection = (key: string) => {
    setSectionsOpen((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // ── Loading skeleton ────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div
        className="rounded-xl border p-5 animate-pulse"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        aria-busy="true"
        aria-label="Carregando mensagem de handoff"
      >
        <div className="flex items-center gap-3 mb-4">
          <div
            className="w-10 h-10 rounded-full"
            style={{ backgroundColor: 'var(--semantic-border-default)' }}
          />
          <div className="flex-1 space-y-2">
            <div
              className="h-4 w-48 rounded"
              style={{ backgroundColor: 'var(--semantic-border-default)' }}
            />
            <div
              className="h-3 w-32 rounded"
              style={{ backgroundColor: 'var(--semantic-border-default)' }}
            />
          </div>
        </div>
        <div className="space-y-2">
          <div
            className="h-4 w-full rounded"
            style={{ backgroundColor: 'var(--semantic-border-default)' }}
          />
          <div
            className="h-4 w-3/4 rounded"
            style={{ backgroundColor: 'var(--semantic-border-default)' }}
          />
        </div>
      </div>
    );
  }

  // ── Error state ─────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        className="rounded-xl border p-5"
        style={{
          backgroundColor: 'var(--clinical-severity-critical-wash)',
          borderColor: 'var(--clinical-severity-critical-signal)',
          color: 'var(--clinical-severity-critical-on-surface)',
        }}
      >
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <p className="text-sm font-semibold">Erro ao carregar mensagem</p>
            <p className="text-xs mt-1 opacity-90">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Normal card ─────────────────────────────────────────────────────────
  const isUnread = !message.read;

  return (
    <div
      className="rounded-xl border p-5 transition-all"
      style={{
        borderColor: message.urgent
          ? 'var(--clinical-severity-urgent-signal)'
          : isUnread
            ? 'var(--clinical-communication-unread-signal)'
            : 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
        borderLeftWidth: isUnread ? '4px' : '1px',
      }}
      aria-label={`Mensagem de handoff ${isUnread ? 'não lida' : 'lida'} — ${message.from_user}`}
    >
      {/* ── Header ──────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3 min-w-0">
          {/* Unread dot */}
          {isUnread && (
            <div
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: 'var(--clinical-communication-unread-signal)' }}
              aria-label="Não lida"
            />
          )}

          {/* User icon + from */}
          <div className="flex items-center gap-2 min-w-0">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{
                backgroundColor: 'var(--clinical-communication-unread-wash)',
                color: 'var(--clinical-communication-unread-on-surface)',
              }}
              aria-hidden="true"
            >
              <User className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <p
                className="text-sm font-semibold truncate"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {message.from_user}
              </p>
              <div
                className="flex items-center gap-1 text-xs"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <ArrowRightLeft className="w-3 h-3" aria-hidden="true" />
                <span className="truncate">{message.to_shift}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Timestamp + urgent badge */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {message.urgent && (
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
              style={{
                backgroundColor: 'var(--clinical-severity-urgent-fill)',
                color: 'var(--clinical-severity-urgent-on-fill)',
              }}
            >
              <AlertTriangle className="w-3 h-3" aria-hidden="true" />
              Urgente
            </span>
          )}
          <div
            className="flex items-center gap-1 text-xs"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            <Clock className="w-3 h-3" aria-hidden="true" />
            <time dateTime={message.created_at}>
              {formatRelativeTime(message.created_at)}
            </time>
          </div>
        </div>
      </div>

      {/* ── SBAR Body ──────────────────────────────────── */}

      {/* S — Situation (always visible) */}
      <div className="mb-2">
        <h4
          className="text-xs font-semibold uppercase tracking-wider mb-1"
          style={{ color: 'var(--clinical-communication-unread-on-surface)' }}
        >
          Situação
        </h4>
        <p
          className="text-sm leading-relaxed"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {message.sbar_s}
        </p>
      </div>

      {/* B / A / R — Accordion sections */}
      {[
        { key: 'b', label: 'Background (Antecedentes)', content: message.sbar_b },
        { key: 'a', label: 'Assessment (Avaliação)', content: message.sbar_a },
        { key: 'r', label: 'Recommendation (Recomendações)', content: message.sbar_r },
      ].map(({ key, label, content }) => (
        <div key={key} className="border-t" style={{ borderColor: 'var(--semantic-border-default)' }}>
          <button
            onClick={() => toggleSection(key)}
            className="w-full flex items-center justify-between py-2.5 text-left focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
            aria-expanded={sectionsOpen[key]}
            aria-label={`${sectionsOpen[key] ? 'Ocultar' : 'Mostrar'} ${label}`}
          >
            <span
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {label}
            </span>
            {sectionsOpen[key] ? (
              <ChevronUp
                className="w-4 h-4"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
            ) : (
              <ChevronDown
                className="w-4 h-4"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
            )}
          </button>
          {sectionsOpen[key] && (
            <div className="pb-3">
              <p
                className="text-sm leading-relaxed"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {content}
              </p>
            </div>
          )}
        </div>
      ))}

      {/* ── Footer: Mark as read ──────────────────────── */}
      {isUnread && onMarkRead && (
        <div className="border-t mt-2 pt-3" style={{ borderColor: 'var(--semantic-border-default)' }}>
          <button
            onClick={() => onMarkRead(message.id)}
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
            style={{
              color: 'var(--clinical-communication-unread-on-surface)',
              backgroundColor: 'var(--clinical-communication-unread-wash)',
            }}
            aria-label="Marcar mensagem como lida"
          >
            <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
            Marcar como lida
          </button>
        </div>
      )}
    </div>
  );
}
