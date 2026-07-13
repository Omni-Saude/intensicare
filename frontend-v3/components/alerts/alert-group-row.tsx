'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import {
  ChevronDown,
  ChevronRight,
  User,
  Clock,
  Layers,
  TrendingUp,
  CheckCircle,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  acknowledgeAlert,
  ApiError,
  type AlertGroup,
  type AlertInfo,
  type SeverityLevel,
} from '@/lib/api';
import { AlertRow } from './alert-row';
import { SeverityBadge } from './severity-badge';

interface AlertGroupRowProps {
  group: AlertGroup;
  onAlertUpdate: (updated: AlertInfo) => void;
  onError: (message: string) => void;
  /**
   * Called exactly once after the sequential group-acknowledge run
   * finishes (success or partial failure), with every member that was
   * actually acknowledged (ADR-0039 §4: one call at the end, not
   * per-member). The caller folds these straight into the SWR cache — see
   * app/alerts/page.tsx's `applyAlertUpdates` — rather than issuing a
   * fresh GET, so this never races a concurrent WebSocket-triggered
   * revalidation (GK-RESP achado C).
   */
  onGroupAcknowledged: (succeeded: AlertInfo[]) => void;
}

// Local label map — mirrors SeverityBadge's private SEVERITY_CONFIG labels
// without reaching into that module's internals. Small, file-local
// duplication in the same spirit as formatApiErrorDetail in
// components/admin/user-manager.tsx.
const SEVERITY_LABEL: Record<SeverityLevel, string> = {
  normal: 'Normal',
  watch: 'Observação',
  urgent: 'Urgente',
  critical: 'Crítico',
};

// `nowMs` defaults to Date.now() the same way lib/vitals-staleness.ts's
// computeStaleness() does — a plain (non-component) function evaluating
// Date.now() in its own default parameter, rather than the component body
// calling it directly (react-hooks/purity forbids the latter).
function formatShortRelative(iso: string, nowMs: number = Date.now()): string {
  const diffMs = Math.max(0, nowMs - new Date(iso).getTime());
  const diffMin = Math.round(diffMs / 60_000);
  if (diffMin < 1) return 'agora mesmo';
  if (diffMin < 60) return `há ${diffMin} min`;
  const diffH = diffMin / 60;
  if (diffH < 24) return `há ${diffH.toFixed(1)}h`;
  const diffD = Math.floor(diffH / 24);
  return `há ${diffD} dia${diffD === 1 ? '' : 's'}`;
}

function formatSpan(firstIso: string, latestIso: string): string {
  const diffMs = Math.max(0, new Date(latestIso).getTime() - new Date(firstIso).getTime());
  const diffMin = Math.round(diffMs / 60_000);
  if (diffMin < 1) return 'mesmo instante';
  if (diffMin < 60) return `${diffMin} min`;
  const diffH = diffMin / 60;
  if (diffH < 24) return `${diffH.toFixed(1)}h`;
  const diffD = Math.floor(diffH / 24);
  return `${diffD} dia${diffD === 1 ? '' : 's'}`;
}

// Mirrors formatApiErrorDetail (components/admin/user-manager.tsx) so a
// failed group-acknowledge never surfaces "[object Object]" — ApiError's
// `.detail` can be a plain string, a Pydantic validation-error array, or
// (defensively) another object shape.
function describeAckError(err: unknown): string {
  if (err instanceof ApiError) {
    const raw: unknown = err.detail;
    if (typeof raw === 'string' && raw.trim()) return raw;
    if (Array.isArray(raw)) {
      const messages = raw
        .map((item) =>
          item && typeof item === 'object' && 'msg' in item
            ? String((item as { msg: unknown }).msg)
            : String(item),
        )
        .filter(Boolean);
      if (messages.length > 0) return messages.join('; ');
    }
    if (raw && typeof raw === 'object') {
      try {
        return JSON.stringify(raw);
      } catch {
        // fall through to the generic message below
      }
    }
  }
  return err instanceof Error ? err.message : 'Erro desconhecido';
}

export function AlertGroupRow({
  group,
  onAlertUpdate,
  onError,
  onGroupAcknowledged,
}: AlertGroupRowProps) {
  const [expanded, setExpanded] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [acking, setAcking] = useState(false);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);

  const detailsId = `alert-group-${group.mpi_id}-${group.score_type}-details`;
  const groupLabel = `${group.patient_name} — ${group.score_type}`;

  // ADR-0039 §4: group actions are N explicit individual actions — the
  // backend never gains a "group" state. AlertInfo does not expose the
  // backend's internal lifecycle `status` string to the client, so
  // eligibility ("status active") is derived the same way the existing
  // single-alert acknowledge button already does (components/alerts/
  // quick-actions.tsx: `{!alert.acknowledged_at && (...)}`) — not yet
  // acknowledged and not resolved.
  const eligibleMembers = useMemo(
    () => group.members.filter((m) => !m.acknowledged_at && !m.resolved_at),
    [group.members],
  );

  const windowLabel =
    group.count > 1 && group.first_created_at !== group.latest_created_at
      ? `${formatShortRelative(group.latest_created_at)} · janela de ${formatSpan(
          group.first_created_at,
          group.latest_created_at,
        )}`
      : formatShortRelative(group.latest_created_at);

  const handleConfirmAck = async () => {
    setAcking(true);
    setProgress({ done: 0, total: eligibleMembers.length });
    const failures: { id: number; message: string }[] = [];
    const succeeded: AlertInfo[] = [];

    // Sequential by design (ADR-0039 §4) — no bulk endpoint exists; each
    // acknowledge is its own state transition, audited individually.
    for (const member of eligibleMembers) {
      try {
        succeeded.push(await acknowledgeAlert(member.id));
      } catch (err) {
        failures.push({ id: member.id, message: describeAckError(err) });
      }
      setProgress((prev) => (prev ? { ...prev, done: prev.done + 1 } : prev));
    }

    setAcking(false);
    setConfirming(false);
    setProgress(null);

    if (failures.length > 0) {
      onError(
        `Reconhecidos ${succeeded.length} de ${eligibleMembers.length} alertas de ${groupLabel}. ` +
          `Falhas: ${failures.map((f) => `#${f.id} (${f.message})`).join('; ')}`,
      );
    }

    // Fold every member that actually succeeded into the cache once, at the
    // end, not per-member — see prop doc above.
    onGroupAcknowledged(succeeded);
  };

  return (
    <div
      className={cn(
        'rounded-lg border transition-colors',
        group.escalating
          ? 'border-[var(--severity-critical)]/50 bg-[var(--severity-critical-wash)]'
          : 'border-[var(--border-default)] bg-[var(--surface-raised)]',
      )}
      role="listitem"
    >
      {/*
        Summary row — same APG disclosure pattern as alert-row.tsx: the
        container itself is not interactive (it holds nested links/
        buttons), a sibling <button> below owns aria-expanded/
        aria-controls, and the row's onClick is a mouse-only convenience
        (no tabIndex on the div, so it never competes with the disclosure
        button or nested controls for keyboard focus).
      */}
      <div
        className="flex cursor-pointer flex-wrap items-center gap-3 px-4 py-3"
        onClick={() => setExpanded(!expanded)}
      >
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setExpanded(!expanded);
          }}
          aria-expanded={expanded}
          aria-controls={detailsId}
          aria-label={`Grupo ${groupLabel} — ${expanded ? 'Recolher' : 'Expandir'} ${group.count} alertas`}
          className="flex-shrink-0 rounded text-[var(--text-secondary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
        >
          {expanded ? (
            <ChevronDown className="h-4 w-4" aria-hidden="true" />
          ) : (
            <ChevronRight className="h-4 w-4" aria-hidden="true" />
          )}
        </button>

        {/*
          GK-RESP NOVO A — color-contrast (serious): SeverityBadge's default
          "wash" rendering is a translucent tint (config.washVar, ~16% alpha)
          set via *inline* style, so no external className can override it.
          When the row is also escalating (this container adds its own
          severity-critical-wash background — see className above), the
          badge's wash paints a SECOND time on top of the row's wash,
          double-compositing #FF7077 at 16% alpha twice over
          --surface-canvas. That crushes text-on-background contrast for the
          "Crítico" badge to ~4.48:1 (WCAG AA text requires >=4.5:1):
            layer1 = 0.16*(255,112,119) + 0.84*(10,14,20)   = (49,30,36)
            layer2 = 0.16*(255,112,119) + 0.84*(49,30,36)   = (82,43,49)
            contrast(#FF7077, #522b31) = 4.483:1  -- FAIL
          Fix (ADR-0039 §3, mirrors filter-bar.tsx's solid-severity-bg +
          #0a0e14 text pattern): only for the escalating+critical case,
          render an opaque critical-colored badge instead of the wash
          variant — solid bg is immune to the row's wash sitting behind it,
          and dark text on the solid critical color also reads as a
          stronger "escalating to critical" signal.
            contrast(#0a0e14, #FF7077 solid) = 7.217:1  -- PASS
          Non-escalating rows, and escalating rows whose max_severity isn't
          'critical', are untouched — SeverityBadge already passes contrast
          there, so this stays scoped to the one flagged case rather than
          risking severity-badge.tsx's other three call sites.
        */}
        {group.escalating && group.max_severity === 'critical' ? (
          <span
            role="status"
            aria-label={`Severidade: ${SEVERITY_LABEL[group.max_severity]}`}
            className="severity-critical-pulse inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium whitespace-nowrap"
            style={{
              backgroundColor: 'var(--severity-critical)',
              color: 'var(--surface-canvas)',
              border: '1px solid var(--severity-critical)',
            }}
          >
            <span
              className="inline-block h-1.5 w-1.5 rounded-full"
              style={{ backgroundColor: 'var(--surface-canvas)' }}
              aria-hidden="true"
            />
            {SEVERITY_LABEL[group.max_severity]}
          </span>
        ) : (
          <SeverityBadge severity={group.max_severity} />
        )}

        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
          Paciente
        </span>
        <Link
          href={`/patient/${group.mpi_id}`}
          onClick={(e) => e.stopPropagation()}
          className="flex items-center gap-1 text-sm font-medium text-[var(--text-primary)] hover:underline"
          aria-label={`Paciente: ${group.patient_name}`}
        >
          <User className="h-3.5 w-3.5 text-[var(--text-secondary)]" aria-hidden="true" />
          {group.patient_name}
        </Link>

        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">Sinal</span>
        <span
          className="inline-flex items-center gap-1 rounded-full border border-[var(--border-default)] bg-[var(--surface-overlay)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]"
          aria-label={`Tipo de sinal: ${group.score_type}`}
        >
          <Layers className="h-3 w-3" aria-hidden="true" />
          {group.score_type}
        </span>

        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
          Ocorrências
        </span>
        <span className="text-sm text-[var(--text-primary)]">
          {group.count} {group.count === 1 ? 'ocorrência' : 'ocorrências'}
        </span>

        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">Janela</span>
        <span className="flex items-center gap-1 text-xs text-[var(--text-secondary)] whitespace-nowrap">
          <Clock className="h-3 w-3" aria-hidden="true" />
          {windowLabel}
        </span>

        {/*
          Escalation badge — ADR-0039 §3: never suppressed, always rendered
          in the collapsed summary (not gated behind expand).

          GK-RESP NOVO A — color-contrast (serious): this badge used to set
          its OWN severity-critical-wash (~16% alpha) as background, but it
          renders as a direct child of the row container, which *also* gets
          severity-critical-wash as background while escalating (see
          className on the outer <div> above). Two 16%-alpha washes stacked
          double-composite #FF7077 over --surface-canvas, crushing
          text-on-background contrast to ~4.48:1 (axe-confirmed live:
          "foreground #ff7077, background #522b31" — same math as the
          SeverityBadge case above):
            layer1 = 0.16*(255,112,119) + 0.84*(10,14,20) = (49,30,36)
            layer2 = 0.16*(255,112,119) + 0.84*(49,30,36) = (82,43,49) = #522b31
            contrast(#FF7077, #522b31) = 4.483:1  -- FAIL (< 4.5 AA)
          Fix: solid critical background + #0a0e14 text (opaque, so the
          row's wash sitting behind it no longer matters) — same pattern as
          filter-bar.tsx's solid-severity-bg + dark-text badges, and the
          same fix applied to the SeverityBadge case above:
            contrast(#0a0e14, #FF7077 solid) = 7.217:1  -- PASS
          `severity-critical-pulse` (the same animation SeverityBadge
          applies to critical badges) is kept for emphasis.
        */}
        {group.escalating && (
          <span
            className="severity-critical-pulse inline-flex items-center gap-1 rounded-full border border-[var(--severity-critical)] px-2 py-0.5 text-xs font-semibold"
            style={{ backgroundColor: 'var(--severity-critical)', color: 'var(--surface-canvas)' }}
            role="status"
            aria-label="Em escalação: a severidade subiu desde o alerta ativo mais antigo deste grupo"
          >
            <TrendingUp className="h-3 w-3" aria-hidden="true" />
            Escalando
          </span>
        )}

        {/* Group action — stop propagation so it never toggles expand */}
        <div
          className="ml-auto flex items-center gap-2"
          onClick={(e) => e.stopPropagation()}
          onKeyDown={(e) => e.stopPropagation()}
        >
          {!confirming ? (
            <button
              type="button"
              onClick={() => setConfirming(true)}
              disabled={eligibleMembers.length === 0}
              className={cn(
                'inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors',
                'bg-[var(--severity-normal-wash)] text-[var(--severity-normal)]',
                'hover:brightness-125 disabled:opacity-50 disabled:cursor-not-allowed',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
              )}
              aria-label={
                eligibleMembers.length === 0
                  ? 'Reconhecer grupo — nenhum alerta pendente'
                  : `Reconhecer os ${eligibleMembers.length} alertas pendentes de ${groupLabel}`
              }
              title={
                eligibleMembers.length === 0
                  ? 'Todos os alertas do grupo já foram reconhecidos ou resolvidos'
                  : 'Reconhecer grupo'
              }
            >
              <CheckCircle className="h-3 w-3" aria-hidden="true" />
              Reconhecer grupo
            </button>
          ) : (
            <div
              className="flex flex-wrap items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--surface-canvas)] px-2.5 py-1.5"
              role="group"
              aria-label="Confirmar reconhecimento em grupo"
            >
              <span className="text-xs text-[var(--text-primary)]">
                {acking && progress
                  ? `Reconhecendo ${progress.done}/${progress.total}…`
                  : `Reconhecer ${eligibleMembers.length} ${
                      eligibleMembers.length === 1 ? 'alerta' : 'alertas'
                    } de ${group.patient_name} — ${group.score_type} ${
                      SEVERITY_LABEL[group.max_severity]
                    }?`}
              </span>
              {!acking && (
                <>
                  <button
                    type="button"
                    onClick={handleConfirmAck}
                    className="rounded-md bg-[var(--severity-normal-wash)] px-2 py-1 text-xs font-medium text-[var(--severity-normal)] hover:brightness-125 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
                  >
                    Confirmar
                  </button>
                  <button
                    type="button"
                    onClick={() => setConfirming(false)}
                    className="rounded-md px-2 py-1 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
                  >
                    Cancelar
                  </button>
                </>
              )}
              {acking && (
                <Loader2
                  className="h-3 w-3 animate-spin text-[var(--text-secondary)]"
                  aria-hidden="true"
                />
              )}
            </div>
          )}
        </div>
      </div>

      {/*
        Expanded members — kept mounted at all times (visibility toggled via
        the `hidden` attribute) so aria-controls always resolves to a real
        node. Each member renders via the existing AlertRow, unmodified —
        individual ack/resolve/escalate stay per-alert.
      */}
      <div
        id={detailsId}
        hidden={!expanded}
        className="border-t border-[var(--border-default)] px-2 py-2 sm:px-4 sm:py-3"
        role="region"
        aria-label={`Alertas do grupo ${groupLabel}`}
      >
        <div
          className="flex flex-col gap-2"
          role="list"
          aria-label={`Membros do grupo ${groupLabel}`}
        >
          {group.members.map((member) => (
            <AlertRow
              key={member.id}
              alert={member}
              onAlertUpdate={onAlertUpdate}
              onError={onError}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
