'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  MessageSquare,
  MessageCircle,
  Send,
  Loader2,
  AlertTriangle,
  RefreshCw,
  ArrowRightLeft,
  X,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import HandoffMessageCard from '@/components/HandoffMessageCard';
import DrawerBuilder from '@/components/DrawerBuilder';
import {
  fetchHandoffMessages,
  createHandoffMessage,
  markHandoffMessageRead,
  fetchShifts,
  type HandoffMessageResponse,
  type ShiftOption,
} from '@/lib/api';

// ─── New Message Form Type ──────────────────────────────────────────────────

interface NewHandoffMessage {
  to_shift: string;
  sbar_s: string;
  sbar_b: string;
  sbar_a: string;
  sbar_r: string;
  urgent: boolean;
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function CommunicationPage() {
  const [messages, setMessages] = useState<HandoffMessageResponse[]>([]);
  const [shifts, setShifts] = useState<ShiftOption[]>([]);
  const [activeTab, setActiveTab] = useState<'messages' | 'new'>('messages');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  // Form state
  const [form, setForm] = useState<NewHandoffMessage>({
    to_shift: '',
    sbar_s: '',
    sbar_b: '',
    sbar_a: '',
    sbar_r: '',
    urgent: false,
  });

  // ── Initial fetch ───────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([fetchHandoffMessages(), fetchShifts()])
      .then(([msgData, shiftData]) => {
        if (cancelled) return;
        setMessages(msgData.messages);
        setShifts(shiftData.shifts);
        if (shiftData.shifts.length > 0 && !form.to_shift) {
          setForm((prev) => ({ ...prev, to_shift: shiftData.shifts[0]!.value }));
        }
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Mark as read ───────────────────────────────────
  const handleMarkRead = useCallback((id: string) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, read: true } : m)),
    );
    // Fire-and-forget API call
    markHandoffMessageRead(id).catch(() => {
      // Silently ignore — UI already updated optimistically
    });
  }, []);

  // ── Submit new message ─────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.sbar_s.trim()) {
      setToast('O campo Situação (S) é obrigatório.');
      return;
    }

    setSending(true);
    setError(null);

    try {
      const newMessage = await createHandoffMessage(form);

      setMessages((prev) => [newMessage, ...prev]);
      setSending(false);
      setDrawerOpen(false);

      // Reset form
      setForm({
        to_shift: shifts[0]?.value ?? '',
        sbar_s: '',
        sbar_b: '',
        sbar_a: '',
        sbar_r: '',
        urgent: false,
      });

      setToast('Mensagem de handoff enviada com sucesso!');

      // Clear toast after 3s
      setTimeout(() => setToast(null), 3000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao enviar mensagem');
      setSending(false);
    }
  };

  // ── Render ─────────────────────────────────────────
  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-3xl mx-auto">
          {/* ── Header ─────────────────────────────── */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-1">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{
                  backgroundColor: 'var(--clinical-communication-unread-wash)',
                  color: 'var(--clinical-communication-unread-on-surface)',
                }}
                aria-hidden="true"
              >
                <ArrowRightLeft className="w-5 h-5" />
              </div>
              <div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Passagem de Plantão
                </h1>
                <p
                  className="text-sm"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Comunicação estruturada SBAR entre turnos
                </p>
              </div>
            </div>
          </div>

          {/* ── Tab toggle ──────────────────────────── */}
          <div className="flex items-center gap-1 mb-6 p-1 rounded-xl" style={{
            backgroundColor: 'var(--semantic-surface-raised)',
            borderColor: 'var(--semantic-border-default)',
            borderWidth: '1px',
          }}>
            <button
              onClick={() => setActiveTab('messages')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                activeTab === 'messages' ? '' : ''
              }`}
              style={
                activeTab === 'messages'
                  ? {
                      backgroundColor: 'var(--clinical-communication-unread-fill)',
                      color: 'var(--clinical-communication-unread-on-fill)',
                    }
                  : {
                      backgroundColor: 'transparent',
                      color: 'var(--semantic-text-secondary)',
                    }
              }
              aria-label="Ver lista de mensagens"
              aria-pressed={activeTab === 'messages'}
            >
              <MessageSquare className="w-4 h-4" aria-hidden="true" />
              Mensagens
            </button>
            <button
              onClick={() => {
                setActiveTab('new');
                setDrawerOpen(true);
              }}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                activeTab === 'new' ? '' : ''
              }`}
              style={
                activeTab === 'new'
                  ? {
                      backgroundColor: 'var(--clinical-communication-unread-fill)',
                      color: 'var(--clinical-communication-unread-on-fill)',
                    }
                  : {
                      backgroundColor: 'transparent',
                      color: 'var(--semantic-text-secondary)',
                    }
              }
              aria-label="Nova mensagem de handoff"
              aria-pressed={activeTab === 'new'}
            >
              <MessageCircle className="w-4 h-4" aria-hidden="true" />
              Nova Mensagem
            </button>
          </div>

          {/* ── Loading state ────────────────────────── */}
          {loading && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <HandoffMessageCard
                  key={i}
                  message={{
                    id: `skeleton-${i}`,
                    from_user: '',
                    to_shift: '',
                    sbar_s: '',
                    sbar_b: '',
                    sbar_a: '',
                    sbar_r: '',
                    created_at: '',
                    read: false,
                    urgent: false,
                  }}
                  isLoading
                />
              ))}
            </div>
          )}

          {/* ── Error state ──────────────────────────── */}
          {!loading && error && (
            <div
              role="alert"
              className="rounded-xl border p-6"
              style={{
                backgroundColor: 'var(--clinical-severity-critical-wash)',
                borderColor: 'var(--clinical-severity-critical-signal)',
                color: 'var(--clinical-severity-critical-on-surface)',
              }}
            >
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
                <div>
                  <h2 className="font-semibold">Erro ao carregar mensagens</h2>
                  <p className="text-sm mt-1">{error}</p>
                  <button
                    onClick={() => {
                      setError(null);
                      setLoading(true);
                      Promise.all([fetchHandoffMessages(), fetchShifts()])
                        .then(([msgData, shiftData]) => {
                          setMessages(msgData.messages);
                          setShifts(shiftData.shifts);
                          setLoading(false);
                        })
                        .catch((err: unknown) => {
                          setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
                          setLoading(false);
                        });
                    }}
                    className="mt-3 inline-flex items-center gap-2 text-sm underline focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                    style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                  >
                    <RefreshCw className="w-4 h-4" aria-hidden="true" />
                    Tentar novamente
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── Message list ─────────────────────────── */}
          {!loading && !error && (
            <>
              <div
                className="flex items-center gap-2 mb-4 text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <MessageSquare className="w-4 h-4" aria-hidden="true" />
                <span>
                  {messages.length} mensagem{messages.length !== 1 ? 'ns' : ''}
                </span>
                {messages.filter((m) => !m.read).length > 0 && (
                  <span
                    className="ml-1 px-2 py-0.5 rounded-full text-xs font-semibold"
                    style={{
                      backgroundColor: 'var(--clinical-communication-unread-wash)',
                      color: 'var(--clinical-communication-unread-on-surface)',
                    }}
                  >
                    {messages.filter((m) => !m.read).length} não lida{messages.filter((m) => !m.read).length !== 1 ? 's' : ''}
                  </span>
                )}
              </div>

              {messages.length === 0 ? (
                /* ── Empty state ────────────────────── */
                <div
                  className="rounded-xl border p-10 text-center"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                  }}
                >
                  <ArrowRightLeft
                    className="w-12 h-12 mx-auto mb-3"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                    aria-hidden="true"
                  />
                  <p
                    className="text-lg font-semibold"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    Nenhuma mensagem de handoff registrada
                  </p>
                  <p
                    className="text-sm mt-1"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    As mensagens de passagem de plantão entre turnos aparecerão aqui.
                  </p>
                  <button
                    onClick={() => {
                      setActiveTab('new');
                      setDrawerOpen(true);
                    }}
                    className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                    style={{
                      backgroundColor: 'var(--clinical-communication-unread-fill)',
                      color: 'var(--clinical-communication-unread-on-fill)',
                    }}
                  >
                    <Send className="w-4 h-4" aria-hidden="true" />
                    Criar primeira mensagem
                  </button>
                </div>
              ) : (
                /* ── Message cards ──────────────────── */
                <div className="space-y-4">
                  {messages.map((msg) => (
                    <HandoffMessageCard
                      key={msg.id}
                      message={msg}
                      onMarkRead={handleMarkRead}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {/* ── Drawer: Nova Mensagem (SBAR form) ────── */}
          <DrawerBuilder
            open={drawerOpen}
            onClose={() => {
              setDrawerOpen(false);
              setActiveTab('messages');
            }}
            title="Nova Mensagem de Handoff"
            size="lg"
          >
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Turno destino */}
              <div>
                <label
                  htmlFor="to_shift"
                  className="block text-sm font-semibold mb-1.5"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Turno de destino
                </label>
                <select
                  id="to_shift"
                  value={form.to_shift}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, to_shift: e.target.value }))
                  }
                  className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    color: 'var(--semantic-text-primary)',
                    backgroundColor: 'var(--semantic-surface-canvas)',
                  }}
                >
                  {shifts.map((shift) => (
                    <option key={shift.value} value={shift.value}>
                      {shift.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* S — Situação */}
              <div>
                <label
                  htmlFor="sbar_s"
                  className="block text-sm font-semibold mb-1.5"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <span
                    className="inline-flex items-center justify-center w-5 h-5 rounded text-xs font-bold mr-1.5"
                    style={{
                      backgroundColor: 'var(--clinical-communication-unread-fill)',
                      color: 'var(--clinical-communication-unread-on-fill)',
                    }}
                  >
                    S
                  </span>
                  Situação
                  <span className="text-red-400 ml-0.5">*</span>
                </label>
                <textarea
                  id="sbar_s"
                  value={form.sbar_s}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, sbar_s: e.target.value }))
                  }
                  placeholder="Descreva a situação atual do paciente..."
                  rows={3}
                  required
                  className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    color: 'var(--semantic-text-primary)',
                    backgroundColor: 'var(--semantic-surface-canvas)',
                  }}
                  aria-required="true"
                />
              </div>

              {/* B — Background */}
              <div>
                <label
                  htmlFor="sbar_b"
                  className="block text-sm font-semibold mb-1.5"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <span
                    className="inline-flex items-center justify-center w-5 h-5 rounded text-xs font-bold mr-1.5"
                    style={{
                      backgroundColor: 'var(--clinical-antimicrobial-stewardship-review-fill)',
                      color: 'var(--clinical-antimicrobial-stewardship-review-on-fill)',
                    }}
                  >
                    B
                  </span>
                  Background (Antecedentes)
                </label>
                <textarea
                  id="sbar_b"
                  value={form.sbar_b}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, sbar_b: e.target.value }))
                  }
                  placeholder="História clínica relevante, contexto..."
                  rows={3}
                  className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    color: 'var(--semantic-text-primary)',
                    backgroundColor: 'var(--semantic-surface-canvas)',
                  }}
                />
              </div>

              {/* A — Assessment */}
              <div>
                <label
                  htmlFor="sbar_a"
                  className="block text-sm font-semibold mb-1.5"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <span
                    className="inline-flex items-center justify-center w-5 h-5 rounded text-xs font-bold mr-1.5"
                    style={{
                      backgroundColor: 'var(--clinical-severity-watch-fill)',
                      color: 'var(--clinical-severity-watch-on-fill)',
                    }}
                  >
                    A
                  </span>
                  Assessment (Avaliação)
                </label>
                <textarea
                  id="sbar_a"
                  value={form.sbar_a}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, sbar_a: e.target.value }))
                  }
                  placeholder="Sua avaliação clínica, análise..."
                  rows={3}
                  className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    color: 'var(--semantic-text-primary)',
                    backgroundColor: 'var(--semantic-surface-canvas)',
                  }}
                />
              </div>

              {/* R — Recommendation */}
              <div>
                <label
                  htmlFor="sbar_r"
                  className="block text-sm font-semibold mb-1.5"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <span
                    className="inline-flex items-center justify-center w-5 h-5 rounded text-xs font-bold mr-1.5"
                    style={{
                      backgroundColor: 'var(--clinical-severity-critical-fill)',
                      color: 'var(--clinical-severity-critical-on-fill)',
                    }}
                  >
                    R
                  </span>
                  Recommendation (Recomendações)
                </label>
                <textarea
                  id="sbar_r"
                  value={form.sbar_r}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, sbar_r: e.target.value }))
                  }
                  placeholder="Ações recomendadas para o próximo turno..."
                  rows={3}
                  className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    color: 'var(--semantic-text-primary)',
                    backgroundColor: 'var(--semantic-surface-canvas)',
                  }}
                />
              </div>

              {/* Urgente checkbox */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="urgent"
                  checked={form.urgent}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, urgent: e.target.checked }))
                  }
                  className="w-4 h-4 rounded border focus:ring-2 focus:ring-blue-500"
                  style={{
                    accentColor: 'var(--clinical-severity-urgent-fill)',
                    borderColor: 'var(--semantic-border-default)',
                  }}
                />
                <label
                  htmlFor="urgent"
                  className="text-sm font-medium flex items-center gap-1.5"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <AlertTriangle
                    className="w-4 h-4"
                    style={{ color: 'var(--clinical-severity-urgent-signal)' }}
                    aria-hidden="true"
                  />
                  Mensagem urgente
                </label>
              </div>

              {/* Submit button */}
              <div className="flex items-center gap-3 pt-2">
                <button
                  type="submit"
                  disabled={sending}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{
                    backgroundColor: 'var(--clinical-communication-unread-fill)',
                    color: 'var(--clinical-communication-unread-on-fill)',
                  }}
                  aria-label="Enviar mensagem de handoff"
                >
                  {sending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" aria-hidden="true" />
                      Enviar mensagem
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setDrawerOpen(false);
                    setActiveTab('messages');
                  }}
                  className="px-4 py-2.5 rounded-lg text-sm font-medium transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{
                    color: 'var(--semantic-text-secondary)',
                    backgroundColor: 'transparent',
                    borderColor: 'var(--semantic-border-default)',
                    borderWidth: '1px',
                  }}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </DrawerBuilder>

          {/* ── Toast ────────────────────────────────── */}
          {toast && (
            <div
              role="status"
              aria-live="polite"
              className="fixed bottom-6 right-6 z-[var(--z-index-toast)] flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg animate-[fadeIn_150ms_ease-out]"
              style={{
                backgroundColor: 'var(--feedback-success-bg-dark)',
                color: 'var(--feedback-success-text-dark)',
                borderColor: 'var(--feedback-success-border-dark)',
                borderWidth: '1px',
              }}
            >
              <span className="text-sm font-medium">{toast}</span>
              <button
                onClick={() => setToast(null)}
                className="p-0.5 rounded hover:opacity-80 min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-label="Fechar notificação"
              >
                <X className="w-4 h-4" aria-hidden="true" />
              </button>
            </div>
          )}
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
