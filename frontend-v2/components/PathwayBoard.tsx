'use client';

import React from 'react';
import {
  GitBranch,
  Play,
  CheckCircle,
  Clock,
  AlertTriangle,
  Loader2,
  User,
  Stethoscope,
  ChevronRight,
  Activity,
  XCircle,
} from 'lucide-react';
import CriteriaChecklist from '@/components/CriteriaChecklist';
import ClinicalTimeline from '@/components/ClinicalTimeline';
import SeverityBadge from '@/components/SeverityBadge';
import type { PatientPathway, PathwayProgress } from '@/lib/pathway-types';
import {
  getStatusLabel,
  computeProgress,
  stateHistoryToTimeline,
  pathwayCriteriaToChecklistItems,
} from '@/lib/pathway-types';

// ─── Props ─────────────────────────────────────────────────────────────────

interface PathwayBoardProps {
  patientPathway: PatientPathway | null;
  progress: PathwayProgress | null;
  isLoading?: boolean;
  error?: string | null;
}

// ─── Skeleton ──────────────────────────────────────────────────────────────

function BoardSkeleton(): React.ReactElement {
  return (
    <div
      className="space-y-6 animate-pulse"
      role="status"
      aria-label="Carregando pathway board"
    >
      {/* Header skeleton */}
      <div className="flex items-center gap-3">
        <div
          className="w-64 h-7 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="w-16 h-6 rounded-full"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="w-20 h-6 rounded"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>

      {/* Progress bar skeleton */}
      <div
        className="w-full h-3 rounded-full"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />

      {/* Content skeletons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="flex gap-3">
              <div
                className="w-5 h-5 rounded"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div className="flex-1 space-y-1.5">
                <div
                  className="h-3.5 rounded w-3/4"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
                <div
                  className="h-2.5 rounded w-1/2"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="flex gap-4">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div className="flex-1 space-y-1.5">
                <div
                  className="h-3.5 rounded w-1/3"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
                <div
                  className="h-2.5 rounded w-2/3"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Progress Bar ──────────────────────────────────────────────────────────

function ProgressBar({
  met,
  total,
  percent,
}: {
  met: number;
  total: number;
  percent: number;
}): React.ReactElement {
  const barStyle: React.CSSProperties = {
    width: `${percent}%`,
    backgroundColor: 'var(--clinical-pathway-active-signal)',
    borderRadius: '9999px',
    height: '100%',
    transition: 'width 0.5s ease',
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <span
          className="text-xs font-medium"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Critérios atendidos
        </span>
        <span
          className="text-xs font-semibold tabular-nums"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {met}/{total} ({percent}%)
        </span>
      </div>
      <div
        className="w-full h-2.5 rounded-full overflow-hidden"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${percent}% dos critérios atendidos`}
      >
        <div style={barStyle} />
      </div>
    </div>
  );
}

// ─── Status Badge for Pathway ─────────────────────────────────────────────

function PathwayStatusBadge({
  status,
}: {
  status: PatientPathway['status'];
}): React.ReactElement {
  const config: Record<
    PatientPathway['status'],
    {
      icon: React.ComponentType<{ className?: string }>;
      label: string;
      signal: string;
      onSurface: string;
      fill: string;
    }
  > = {
    active: {
      icon: Play,
      label: 'Ativo',
      signal: 'var(--clinical-pathway-active-signal)',
      onSurface: 'var(--clinical-pathway-active-on-surface)',
      fill: 'var(--clinical-pathway-active-fill)',
    },
    completed: {
      icon: CheckCircle,
      label: 'Concluído',
      signal: 'var(--clinical-pathway-completed-signal)',
      onSurface: 'var(--clinical-pathway-completed-on-surface)',
      fill: 'var(--clinical-pathway-completed-fill)',
    },
    archived: {
      icon: Clock,
      label: 'Arquivado',
      signal: 'var(--semantic-text-secondary)',
      onSurface: 'var(--semantic-text-secondary)',
      fill: 'var(--semantic-surface-overlay)',
    },
  };

  const c = config[status];
  const Icon = c.icon;

  return (
    <span
      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border"
      style={{
        backgroundColor: c.fill,
        color: c.onSurface,
        borderColor: c.signal,
      }}
      aria-label={`Status: ${c.label}`}
    >
      <Icon className="w-3 h-3" aria-hidden="true" />
      <span>{c.label}</span>
    </span>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────

export default function PathwayBoard({
  patientPathway,
  progress,
  isLoading = false,
  error = null,
}: PathwayBoardProps): React.ReactElement {
  // ─── Loading state ──────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div
        className="p-6"
        role="status"
        aria-label="Carregando pathway"
      >
        <BoardSkeleton />
      </div>
    );
  }

  // ─── Error state ────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-3 p-4 m-4 rounded-lg border text-sm"
        style={{
          backgroundColor: 'var(--feedback-error-bg-dark)',
          color: 'var(--feedback-error-text-dark)',
          borderColor: 'var(--feedback-error-border-dark)',
          borderWidth: '1px',
        }}
      >
        <AlertTriangle className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // ─── Empty state ────────────────────────────────────────────────────────
  if (!patientPathway) {
    return (
      <div
        className="flex flex-col items-center justify-center h-full py-20 gap-4"
        style={{ color: 'var(--semantic-text-secondary)' }}
        role="status"
        aria-label="Nenhum pathway selecionado"
      >
        <GitBranch className="w-16 h-16 opacity-20" aria-hidden="true" />
        <div className="text-center space-y-1">
          <p className="text-base font-medium">Selecione um paciente</p>
          <p className="text-sm">
            Escolha um paciente na lista à esquerda para visualizar o pathway
            clínico.
          </p>
        </div>
      </div>
    );
  }

  // ─── Data ───────────────────────────────────────────────────────────────
  const { pathway, current_state, criteria, status, severity } = patientPathway;
  const progressData = computeProgress(criteria);
  const checklistItems = pathwayCriteriaToChecklistItems(criteria);
  const timelineEvents = progress
    ? stateHistoryToTimeline(progress.state_history, progress.current_state)
    : [];

  const isActive = status === 'active';
  const isCritical = severity === 'critical';
  const isOverdue = severity === 'urgent' || severity === 'critical';

  // ─── Render ─────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* ── Header ────────────────────────────────────────────────────── */}
      <div
        className="p-6 pb-4 border-b"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      >
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap mb-2">
              <h2
                className="text-xl font-bold truncate"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {pathway.name}
              </h2>
              <PathwayStatusBadge status={status} />
              <SeverityBadge
                severity={severity === 'watch' ? 'urgent' : severity === 'urgent' ? 'urgent' : severity as 'normal' | 'watch' | 'urgent' | 'critical'}
                showLabel
              />
            </div>
            <p
              className="text-sm line-clamp-2"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {pathway.description}
            </p>
          </div>

          {/* Current state indicator */}
          <div
            className="flex items-center gap-2 px-3 py-2 rounded-lg border"
            style={{
              borderColor: 'var(--clinical-pathway-active-signal)',
              backgroundColor: 'var(--clinical-pathway-active-fill)',
            }}
          >
            <Activity
              className="w-4 h-4"
              style={{ color: 'var(--clinical-pathway-active-signal)' }}
              aria-hidden="true"
            />
            <div className="text-right">
              <p
                className="text-[10px] uppercase font-semibold tracking-wider"
                style={{
                  color: 'var(--clinical-pathway-active-on-surface)',
                }}
              >
                Estado Atual
              </p>
              <p
                className="text-sm font-bold"
                style={{
                  color: 'var(--clinical-pathway-active-signal)',
                }}
              >
                {current_state.name}
              </p>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <ProgressBar
            met={progressData.met}
            total={progressData.total}
            percent={progressData.percent}
          />
        </div>
      </div>

      {/* ── Content Grid ────────────────────────────────────────────────── */}
      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-y-auto">
        {/* Left column: State Timeline + Recommendation */}
        <div className="space-y-6">
          {/* State Timeline */}
          <section>
            <h3
              className="flex items-center gap-2 text-sm font-semibold mb-3"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <GitBranch className="w-4 h-4" aria-hidden="true" />
              Histórico de Estados
            </h3>
            <div
              className="rounded-xl border p-4"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              {timelineEvents.length > 0 ? (
                <ClinicalTimeline
                  events={timelineEvents}
                  domain="general"
                />
              ) : (
                <p
                  className="text-sm py-4 text-center"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Nenhum histórico de transições disponível
                </p>
              )}
            </div>
          </section>

          {/* Recommendation */}
          {progress?.recommendation && (
            <section>
              <h3
                className="flex items-center gap-2 text-sm font-semibold mb-3"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                <Stethoscope className="w-4 h-4" aria-hidden="true" />
                Recomendação Clínica
              </h3>
              <div
                className={`rounded-xl border p-4 ${
                  isOverdue ? 'animate-pulse-critical' : ''
                }`}
                style={{
                  borderColor: isOverdue
                    ? 'var(--clinical-pathway-overdue-signal)'
                    : 'var(--clinical-pathway-active-signal)',
                  backgroundColor: isOverdue
                    ? 'var(--clinical-pathway-overdue-fill)'
                    : 'var(--clinical-pathway-active-fill)',
                  color: isOverdue
                    ? 'var(--clinical-pathway-overdue-on-surface)'
                    : 'var(--clinical-pathway-active-on-surface)',
                }}
              >
                <div className="flex items-start gap-2">
                  {isOverdue ? (
                    <AlertTriangle
                      className="w-5 h-5 flex-shrink-0 mt-0.5"
                      aria-hidden="true"
                    />
                  ) : (
                    <Activity
                      className="w-5 h-5 flex-shrink-0 mt-0.5"
                      aria-hidden="true"
                    />
                  )}
                  <p className="text-sm leading-relaxed">
                    {progress.recommendation}
                  </p>
                </div>
                {progress.trend !== 'none' && (
                  <div className="mt-3 flex items-center gap-2">
                    <span
                      className="text-xs font-semibold uppercase tracking-wider"
                      style={{ opacity: 0.8 }}
                    >
                      Tendência:
                    </span>
                    <span className="text-xs font-bold">
                      {progress.trend === 'improving'
                        ? 'Melhorando'
                        : progress.trend === 'worsening'
                        ? 'Piorando'
                        : 'Estável'}
                    </span>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Pathway States Overview */}
          <section>
            <h3
              className="flex items-center gap-2 text-sm font-semibold mb-3"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <Activity className="w-4 h-4" aria-hidden="true" />
              Estados do Pathway
            </h3>
            <div className="space-y-0.5">
              {pathway.states.map((state, idx) => {
                const isCurrent = state.id === current_state.id;
                const isPast =
                  pathway.states.findIndex((s) => s.id === state.id) <
                  pathway.states.findIndex((s) => s.id === current_state.id);
                return (
                  <div
                    key={state.id}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg ${
                      isCurrent ? 'font-semibold' : ''
                    }`}
                    style={{
                      backgroundColor: isCurrent
                        ? 'var(--clinical-pathway-active-fill)'
                        : isPast
                        ? 'var(--semantic-surface-overlay)'
                        : 'transparent',
                      color: isCurrent
                        ? 'var(--clinical-pathway-active-on-surface)'
                        : isPast
                        ? 'var(--semantic-text-secondary)'
                        : 'var(--semantic-text-primary)',
                    }}
                  >
                    <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center">
                      {isPast ? (
                        <CheckCircle
                          className="w-5 h-5"
                          style={{
                            color:
                              'var(--clinical-pathway-completed-signal)',
                          }}
                        />
                      ) : isCurrent ? (
                        <Activity
                          className="w-5 h-5"
                          style={{
                            color:
                              'var(--clinical-pathway-active-signal)',
                          }}
                        />
                      ) : (
                        <span
                          className="w-2.5 h-2.5 rounded-full"
                          style={{
                            backgroundColor:
                              'var(--semantic-surface-overlay)',
                          }}
                        />
                      )}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="text-sm">{state.name}</span>
                      {state.is_terminal && (
                        <span
                          className="ml-2 text-[10px] uppercase font-semibold"
                          style={{
                            color: 'var(--semantic-text-secondary)',
                          }}
                        >
                          Terminal
                        </span>
                      )}
                    </div>
                    {isCurrent && (
                      <ChevronRight
                        className="w-4 h-4"
                        style={{
                          color: 'var(--clinical-pathway-active-signal)',
                        }}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        {/* Right column: Criteria Checklist */}
        <div className="space-y-6">
          <section>
            <h3
              className="flex items-center gap-2 text-sm font-semibold mb-3"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <CheckCircle className="w-4 h-4" aria-hidden="true" />
              Critérios Clínicos
            </h3>
            <div
              className="rounded-xl border overflow-hidden"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <CriteriaChecklist
                items={checklistItems}
                domain="pathway"
                readOnly
              />
            </div>
          </section>

          {/* Patient enrollment info */}
          <section>
            <h3
              className="flex items-center gap-2 text-sm font-semibold mb-3"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <User className="w-4 h-4" aria-hidden="true" />
              Informações do Paciente
            </h3>
            <div
              className="rounded-xl border p-4 space-y-2 text-sm"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="flex justify-between">
                <span style={{ color: 'var(--semantic-text-secondary)' }}>
                  MPI
                </span>
                <span
                  className="font-mono font-medium"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  {patientPathway.mpi_id}
                </span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--semantic-text-secondary)' }}>
                  Inscrito em
                </span>
                <span style={{ color: 'var(--semantic-text-primary)' }}>
                  {new Date(patientPathway.enrolled_at).toLocaleDateString(
                    'pt-BR',
                    { day: '2-digit', month: '2-digit', year: 'numeric' },
                  )}
                </span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: 'var(--semantic-text-secondary)' }}>
                  Inscrito por
                </span>
                <span style={{ color: 'var(--semantic-text-primary)' }}>
                  {patientPathway.enrolled_by}
                </span>
              </div>
              {patientPathway.completed_at && (
                <div className="flex justify-between">
                  <span style={{ color: 'var(--semantic-text-secondary)' }}>
                    Concluído em
                  </span>
                  <span style={{ color: 'var(--semantic-text-primary)' }}>
                    {new Date(patientPathway.completed_at).toLocaleDateString(
                      'pt-BR',
                      { day: '2-digit', month: '2-digit', year: 'numeric' },
                    )}
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span style={{ color: 'var(--semantic-text-secondary)' }}>
                  Atualizado em
                </span>
                <span
                  className="text-xs"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  {new Date(patientPathway.updated_at).toLocaleString(
                    'pt-BR',
                    {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    },
                  )}
                </span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
