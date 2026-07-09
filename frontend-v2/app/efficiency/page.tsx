'use client';

import React, { useState, useMemo, useCallback, useEffect } from 'react';
import {
  Gauge,
  Droplets,
  Hand,
  Heart,
  Clock,
  User,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Loader2,
  RefreshCw,
  TrendingDown,
  TrendingUp,
  Timer,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import SeverityBadge from '@/components/SeverityBadge';
import ClinicalTimeline, {
  type TimelineEvent,
} from '@/components/ClinicalTimeline';
import {
  type EfficiencyAssessment,
  type TransfusionCriterion,
  type RestraintStatus,
  type FrailtyScale,
  DEFAULT_TRANSFUSION_CRITERIA,
  RESTRAINT_LABELS,
  FRAILTY_SCALE_LABELS,
  getRestraintColor,
  getRestraintBgColor,
  formatLOS,
  getFrailtyLabel,
  getCFSInterpretation,
} from '@/lib/efficiency-types';
import { fetchEfficiency, fetchDashboard } from '@/lib/api';

// ─── Constants ───────────────────────────────────────────────────────────────

const EFFICIENCY_SECTIONS = [
  'transfusao',
  'contencao',
  'fragilidade',
  'los',
] as const;

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Cor da barra de progresso LOS vs benchmark */
function getLOSProgressColor(
  actual: number,
  benchmark?: number,
): string {
  if (!benchmark) return 'var(--clinical-severity-normal-on-surface)';
  const ratio = actual / benchmark;
  if (ratio < 0.75) return 'var(--clinical-severity-normal-on-surface)'; // verde — abaixo do benchmark
  if (ratio <= 1.0) return 'var(--clinical-severity-watch-on-surface)'; // âmbar — próximo ao benchmark
  return 'var(--clinical-severity-critical-on-surface)'; // vermelho — excedeu
}

/** Calcula o score global de eficiência (0-100) */
function computeGlobalEfficiency(assessment: EfficiencyAssessment): number {
  let score = 0;

  // Transfusão: % de critérios adequados (met=false ou met=true depende do critério)
  // Contamos quantos critérios estão "adequados" — na prática, met=false significa
  // que o critério está sendo atendido (não é uma não-conformidade).
  // Mas no modelo de transfusão, met=true significa que o critério foi ATENDIDO.
  const transfusionMet = assessment.transfusion_criteria.filter(
    (c) => c.met,
  ).length;
  const transfusionScore =
    (transfusionMet / assessment.transfusion_criteria.length) * 40;
  score += transfusionScore;

  // Contenção: none/removed/contraindicated = 20, planned/weaning = 12, active = 5
  const restraintScores: Record<RestraintStatus, number> = {
    none: 20,
    removed: 20,
    contraindicated: 20,
    planned: 12,
    weaning: 12,
    active: 5,
  };
  score += restraintScores[assessment.restraint_status] ?? 10;

  // Fragilidade: quanto menor, melhor (CFS 1-3 = 20, 4-5 = 14, 6-7 = 8, 8-9 = 4)
  if (assessment.frailty_score !== undefined) {
    const fs = assessment.frailty_score;
    if (fs <= 3) score += 20;
    else if (fs <= 5) score += 14;
    else if (fs <= 7) score += 8;
    else score += 4;
  }

  // LOS: abaixo do benchmark = 20, no benchmark = 14, acima = 5
  if (assessment.icu_los_benchmark && assessment.icu_los_days > 0) {
    const ratio = assessment.icu_los_days / assessment.icu_los_benchmark;
    if (ratio < 0.75) score += 20;
    else if (ratio <= 1.0) score += 14;
    else score += 5;
  } else {
    score += 10; // sem benchmark — neutro
  }

  return Math.round(Math.min(score, 100));
}

/** Classifica o score global em severidade */
function getGlobalSeverity(
  score: number,
): 'normal' | 'watch' | 'critical' {
  if (score >= 70) return 'normal';
  if (score >= 40) return 'watch';
  return 'critical';
}

/** Label PT-BR para severidade global */
const GLOBAL_SEVERITY_LABELS: Record<string, string> = {
  normal: 'Eficiente',
  watch: 'Atenção',
  critical: 'Crítico',
};

// ─── Skeletons ───────────────────────────────────────────────────────────────

function SkeletonHeader(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-3" role="status" aria-label="Carregando">
      <div
        className="h-8 w-72 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div
        className="h-5 w-96 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

function SkeletonCard(): React.ReactElement {
  return (
    <div
      className="animate-pulse rounded-xl border p-5 space-y-4"
      role="status"
      aria-label="Carregando seção"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      <div
        className="h-5 w-48 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div
        className="h-4 w-full rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div
        className="h-4 w-3/4 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function EfficiencyPage(): React.ReactElement {
  const [patients, setPatients] = useState<Array<{ mpiId: string; name: string; bed: string }>>([]);

  // ─── Fetch patients on mount ─────────────────────────────────────────────

  useEffect(() => {
    fetchDashboard()
      .then((data) =>
        setPatients(
          data.patients.map(
            (p: { mpi_id: string; display_name: string; bed_id: string | null }) => ({
              mpiId: p.mpi_id,
              name: p.display_name,
              bed: p.bed_id || '',
            }),
          ),
        ),
      )
      .catch(() => {});
  }, []);

  const [selectedPatient, setSelectedPatient] = useState<string>(
    patients[0]?.mpiId || '',
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<EfficiencyAssessment | null>(null);

  const selectedPatientData = patients.find(
    (p: { mpiId: string; name: string; bed: string }) => p.mpiId === selectedPatient,
  );

  // ─── Fetch on mount and patient change ──────────────────────────────────

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchEfficiency(selectedPatient)
      .then((data) => setAssessment(data as EfficiencyAssessment))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Erro ao carregar avaliação de eficiência'),
      )
      .finally(() => setLoading(false));
  }, [selectedPatient]);

  // ─── Derived state ─────────────────────────────────────────────────────────

  const globalScore = useMemo(
    () => (assessment ? computeGlobalEfficiency(assessment) : 0),
    [assessment],
  );

  const globalSeverity = useMemo(
    () => getGlobalSeverity(globalScore),
    [globalScore],
  );

  const transfusionMetCount = useMemo(
    () =>
      assessment
        ? assessment.transfusion_criteria.filter((c) => c.met).length
        : 0,
    [assessment],
  );

  const transfusionTotal = assessment ? assessment.transfusion_criteria.length : 0;

  // ─── Handlers ──────────────────────────────────────────────────────────────

  const handleRefresh = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchEfficiency(selectedPatient)
      .then((data) => setAssessment(data as EfficiencyAssessment))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Erro ao atualizar avaliação'),
      )
      .finally(() => setLoading(false));
  }, [selectedPatient]);

  // ─── Loading state ─────────────────────────────────────────────────────────

  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto space-y-6 pb-12">
          <SkeletonHeader />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      </Layout>
    );
  }

  // ─── Error state ─────────────────────────────────────────────────────────

  if (error) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto py-12">
          <div
            role="alert"
            className="rounded-xl border p-6 text-center"
            style={{
              borderColor: 'var(--clinical-severity-critical-signal)',
              backgroundColor: 'var(--clinical-severity-critical-wash)',
              color: 'var(--clinical-severity-critical-on-surface)',
            }}
          >
            <AlertTriangle className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold text-lg mb-1">Erro ao carregar dados</p>
            <p className="text-sm opacity-90">{error}</p>
            <button
              onClick={handleRefresh}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
                border: '1px solid var(--semantic-border-default)',
              }}
            >
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Tentar novamente
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  // ─── Empty state (no assessment) ─────────────────────────────────────────

  if (!assessment) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto py-12 text-center">
          <Gauge
            className="w-12 h-12 mx-auto mb-4"
            style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
          />
          <p className="text-lg font-medium" style={{ color: 'var(--semantic-text-secondary)' }}>
            Nenhuma avaliação encontrada
          </p>
          <button
            onClick={handleRefresh}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              color: 'var(--semantic-text-primary)',
              border: '1px solid var(--semantic-border-default)',
            }}
          >
            <RefreshCw className="w-4 h-4" aria-hidden="true" />
            Tentar novamente
          </button>
        </div>
      </Layout>
    );
  }

  // ─── Main render ───────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-4xl mx-auto space-y-6 pb-12">
          {/* ── Header ─────────────────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor:
                      'var(--clinical-severity-normal-fill)',
                    color: 'var(--clinical-severity-normal-on-fill)',
                  }}
                >
                  <Gauge className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Eficiência &amp; Stewardship
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Avaliação de recursos e adequação terapêutica — transfusão,
                contenção, fragilidade e tempo de permanência em UTI
              </p>
            </div>

            {/* Patient selector */}
            <div className="flex items-center gap-2">
              <User
                className="w-4 h-4 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <select
                value={selectedPatient}
                onChange={(e) => setSelectedPatient(e.target.value)}
                className="text-sm rounded-lg border px-3 py-2 min-w-[200px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
                aria-label="Selecionar paciente"
              >
                {patients.map((p) => (
                  <option key={p.mpiId} value={p.mpiId}>
                    {p.name} — {p.bed}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* ── Global Score Card ───────────────────────────────────────── */}
          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h2
                  className="text-sm font-semibold uppercase tracking-wider mb-2"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Score Global de Eficiência
                </h2>
                <div className="flex items-baseline gap-2">
                  <span
                    className="text-4xl font-bold tabular-nums"
                    style={{
                      color: `var(--clinical-severity-${globalSeverity}-on-surface)`,
                    }}
                  >
                    {globalScore}
                  </span>
                  <span
                    className="text-lg"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    /100
                  </span>
                </div>
              </div>
              <div className="text-right">
                <SeverityBadge
                  severity={
                    globalSeverity === 'critical'
                      ? 'critical'
                      : globalSeverity === 'watch'
                        ? 'watch'
                        : 'normal'
                  }
                  className="mb-2"
                />
                <p
                  className="text-xs"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {GLOBAL_SEVERITY_LABELS[globalSeverity]}
                </p>
              </div>
            </div>

            {/* Progress bar visual */}
            <div className="mt-4">
              <div
                className="h-2 rounded-full overflow-hidden"
                style={{
                  backgroundColor: 'var(--semantic-surface-overlay)',
                }}
              >
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${globalScore}%`,
                    backgroundColor:
                      globalSeverity === 'normal'
                        ? 'var(--clinical-severity-normal-signal)'
                        : globalSeverity === 'watch'
                          ? 'var(--clinical-severity-watch-signal)'
                          : 'var(--clinical-severity-critical-signal)',
                  }}
                />
              </div>
              <div className="flex justify-between mt-1.5">
                <span
                  className="text-[10px]"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Crítico
                </span>
                <span
                  className="text-[10px]"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Atenção
                </span>
                <span
                  className="text-[10px]"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Eficiente
                </span>
              </div>
            </div>
          </div>


          {/* ── 4 Sections Grid ─────────────────────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* ── A) Transfusão ─────────────────────────────────────────── */}
            <section
              className="rounded-xl border p-5"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Droplets
                  className="w-5 h-5 flex-shrink-0"
                  style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                  aria-hidden="true"
                />
                <h3
                  className="text-base font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Transfusão
                </h3>
                <span
                  className="ml-auto text-sm font-bold tabular-nums"
                  style={{
                    color:
                      transfusionMetCount >= 9
                        ? 'var(--clinical-severity-normal-on-surface)'
                        : transfusionMetCount >= 6
                          ? 'var(--clinical-severity-watch-on-surface)'
                          : 'var(--clinical-severity-critical-on-surface)',
                  }}
                >
                  {transfusionMetCount}/{transfusionTotal} adequados
                </span>
              </div>

              <ul className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {assessment.transfusion_criteria.map((criterion) => (
                  <li
                    key={criterion.code}
                    className="flex items-start gap-2.5 py-1.5 px-2 rounded-lg"
                    style={{
                      backgroundColor: criterion.met
                        ? 'var(--clinical-severity-normal-wash)'
                        : 'var(--semantic-surface-overlay)',
                    }}
                  >
                    {criterion.met ? (
                      <CheckCircle2
                        className="w-4 h-4 flex-shrink-0 mt-0.5"
                        style={{
                          color: 'var(--clinical-severity-normal-signal)',
                        }}
                        aria-label="Adequado"
                      />
                    ) : (
                      <XCircle
                        className="w-4 h-4 flex-shrink-0 mt-0.5"
                        style={{
                          color: 'var(--clinical-severity-critical-signal)',
                        }}
                        aria-label="Não adequado"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <p
                        className="text-sm"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        {criterion.description}
                      </p>
                      {criterion.detail && (
                        <p
                          className="text-xs mt-0.5"
                          style={{
                            color: 'var(--semantic-text-secondary)',
                          }}
                        >
                          {criterion.detail}
                        </p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </section>

            {/* ── B) Contenção Mecânica ─────────────────────────────────── */}
            <section
              className="rounded-xl border p-5"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Hand
                  className="w-5 h-5 flex-shrink-0"
                  style={{
                    color: getRestraintColor(assessment.restraint_status),
                  }}
                  aria-hidden="true"
                />
                <h3
                  className="text-base font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Contenção Mecânica
                </h3>
              </div>

              {/* Status badge */}
              <div className="mb-4">
                <span
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold border"
                  style={{
                    backgroundColor:
                      getRestraintBgColor(assessment.restraint_status),
                    color:
                      getRestraintColor(assessment.restraint_status),
                    borderColor:
                      getRestraintColor(assessment.restraint_status),
                  }}
                >
                  {RESTRAINT_LABELS[assessment.restraint_status]}
                </span>
              </div>

              {/* Detalhes */}
              {assessment.restraint_details ? (
                <div
                  className="text-sm space-y-2"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  <p>{assessment.restraint_details}</p>
                </div>
              ) : (
                <p
                  className="text-sm italic"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Sem detalhes registrados.
                </p>
              )}

              {/* Mini-timeline de contenção */}
              <div className="mt-4 pt-4 border-t" style={{ borderColor: 'var(--semantic-border-default)' }}>
                <p
                  className="text-xs font-semibold mb-2"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Status: {RESTRAINT_LABELS[assessment.restraint_status]}
                </p>
                {assessment.restraint_status === 'active' && (
                  <p
                    className="text-xs"
                    style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                  >
                    ⚠️ Requer revisão a cada 2 horas e reavaliação médica
                    diária
                  </p>
                )}
                {assessment.restraint_status === 'weaning' && (
                  <p
                    className="text-xs"
                    style={{ color: 'var(--clinical-severity-watch-on-surface)' }}
                  >
                    🔄 Desmame em andamento — monitorar tolerância
                  </p>
                )}
              </div>
            </section>

            {/* ── C) Fragilidade ────────────────────────────────────────── */}
            <section
              className="rounded-xl border p-5"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Heart
                  className="w-5 h-5 flex-shrink-0"
                  style={{ color: 'var(--clinical-severity-watch-on-surface)' }}
                  aria-hidden="true"
                />
                <h3
                  className="text-base font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Fragilidade
                </h3>
              </div>

              {assessment.frailty_score !== undefined ? (
                <div className="space-y-4">
                  {/* Score display */}
                  <div className="flex items-center gap-4">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center border-2"
                      style={{
                        borderColor:
                          assessment.frailty_score <= 3
                            ? 'var(--clinical-severity-normal-signal)'
                            : assessment.frailty_score <= 5
                              ? 'var(--clinical-severity-watch-signal)'
                              : 'var(--clinical-severity-critical-signal)',
                        backgroundColor:
                          assessment.frailty_score <= 3
                            ? 'var(--clinical-severity-normal-wash)'
                            : assessment.frailty_score <= 5
                              ? 'var(--clinical-severity-watch-wash)'
                              : 'var(--clinical-severity-critical-wash)',
                      }}
                    >
                      <span
                        className="text-2xl font-bold tabular-nums"
                        style={{
                          color:
                            assessment.frailty_score <= 3
                              ? 'var(--clinical-severity-normal-on-surface)'
                              : assessment.frailty_score <= 5
                                ? 'var(--clinical-severity-watch-on-surface)'
                                : 'var(--clinical-severity-critical-on-surface)',
                        }}
                      >
                        {assessment.frailty_score}
                      </span>
                    </div>
                    <div>
                      <p
                        className="text-sm font-semibold"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        {getFrailtyLabel(
                          assessment.frailty_score,
                          assessment.frailty_scale,
                        )}
                      </p>
                      {assessment.frailty_scale && (
                        <p
                          className="text-xs"
                          style={{
                            color: 'var(--semantic-text-secondary)',
                          }}
                        >
                          {FRAILTY_SCALE_LABELS[assessment.frailty_scale]}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Interpretation */}
                  {assessment.frailty_scale === 'CFS' && (
                    <div
                      className="text-sm p-3 rounded-lg border"
                      style={{
                        borderColor: 'var(--semantic-border-default)',
                        backgroundColor:
                          'var(--semantic-surface-overlay)',
                      }}
                    >
                      <p
                        className="font-semibold mb-1"
                        style={{
                          color: 'var(--semantic-text-primary)',
                        }}
                      >
                        Interpretação:
                      </p>
                      <p
                        style={{
                          color: 'var(--semantic-text-secondary)',
                        }}
                      >
                        {getCFSInterpretation(assessment.frailty_score)}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p
                    className="text-sm italic"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    Fragilidade não avaliada.
                  </p>
                  <button
                    className="mt-2 px-4 py-2 rounded-lg text-xs font-semibold transition-opacity hover:opacity-80"
                    style={{
                      backgroundColor: 'var(--semantic-surface-overlay)',
                      color: 'var(--semantic-text-primary)',
                      borderColor: 'var(--semantic-border-default)',
                      borderWidth: '1px',
                    }}
                  >
                    Iniciar Avaliação CFS
                  </button>
                </div>
              )}
            </section>

            {/* ── D) Tempo de UTI (LOS) ──────────────────────────────────── */}
            <section
              className="rounded-xl border p-5"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Timer
                  className="w-5 h-5 flex-shrink-0"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  aria-hidden="true"
                />
                <h3
                  className="text-base font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Tempo de UTI
                </h3>
              </div>

              <div className="space-y-4">
                {/* LOS atual */}
                <div className="flex items-center justify-between">
                  <div>
                    <p
                      className="text-xs uppercase font-semibold"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      Permanência Atual
                    </p>
                    <p
                      className="text-2xl font-bold tabular-nums"
                      style={{
                        color: assessment.icu_los_benchmark
                          ? getLOSProgressColor(
                              assessment.icu_los_days,
                              assessment.icu_los_benchmark,
                            )
                          : 'var(--semantic-text-primary)',
                      }}
                    >
                      {formatLOS(assessment.icu_los_days)}
                    </p>
                  </div>

                  {assessment.icu_admission_at && (
                    <div className="text-right">
                      <p
                        className="text-xs"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        Desde{' '}
                        {new Date(
                          assessment.icu_admission_at,
                        ).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  )}
                </div>

                {/* Benchmark comparison */}
                {assessment.icu_los_benchmark && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span
                        className="text-xs font-semibold"
                        style={{
                          color: 'var(--semantic-text-secondary)',
                        }}
                      >
                        Benchmark esperado
                      </span>
                      <span
                        className="text-sm font-bold tabular-nums"
                        style={{
                          color: 'var(--semantic-text-primary)',
                        }}
                      >
                        {formatLOS(assessment.icu_los_benchmark)}
                      </span>
                    </div>

                    {/* Barra comparativa */}
                    <div className="relative pt-1">
                      {/* Track da barra */}
                      <div
                        className="h-3 rounded-full overflow-hidden relative"
                        style={{
                          backgroundColor:
                            'var(--semantic-surface-overlay)',
                        }}
                      >
                        {/* Barra de progresso (atual vs benchmark) */}
                        <div
                          className="h-full rounded-full absolute left-0 top-0 transition-all duration-500"
                          style={{
                            width: `${Math.min(
                              (assessment.icu_los_days /
                                assessment.icu_los_benchmark) *
                                100,
                              100,
                            )}%`,
                            backgroundColor:
                              getLOSProgressColor(
                                assessment.icu_los_days,
                                assessment.icu_los_benchmark,
                              ),
                          }}
                        />
                        {/* Marcador de benchmark */}
                        <div
                          className="absolute top-0 h-full w-0.5"
                          style={{
                            left: '100%',
                            backgroundColor:
                              'var(--semantic-text-primary)',
                            opacity: 0.3,
                          }}
                        />
                      </div>

                      {/* Labels abaixo da barra */}
                      <div className="flex justify-between mt-1">
                        <span
                          className="text-[10px]"
                          style={{
                            color: 'var(--semantic-text-secondary)',
                          }}
                        >
                          0 dias
                        </span>
                        <span
                          className="text-[10px] font-semibold"
                          style={{
                            color:
                              assessment.icu_los_days >
                              assessment.icu_los_benchmark
                                ? 'var(--clinical-severity-critical-on-surface)'
                                : 'var(--semantic-text-secondary)',
                          }}
                        >
                          {assessment.icu_los_days >
                          assessment.icu_los_benchmark ? (
                            <span className="inline-flex items-center gap-0.5">
                              <TrendingUp className="w-3 h-3" />
                              Excedido
                            </span>
                          ) : assessment.icu_los_days >=
                            assessment.icu_los_benchmark * 0.75 ? (
                            <span className="inline-flex items-center gap-0.5">
                              Próximo
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-0.5">
                              <TrendingDown className="w-3 h-3" />
                              Abaixo
                            </span>
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Sem benchmark */}
                {!assessment.icu_los_benchmark && (
                  <p
                    className="text-xs italic"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    Benchmark não definido para este diagnóstico.
                  </p>
                )}
              </div>
            </section>
          </div>

          {/* ── Timeline de Eventos ──────────────────────────────────────── */}
          {selectedPatientData && (
            <div>
              <h2
                className="text-sm font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Linha do Tempo
              </h2>
              <ClinicalTimeline
                events={
                  [
                    {
                      id: 'eff-admission',
                      status: 'completed',
                      label: 'Admissão na UTI',
                      description: assessment.icu_admission_at
                        ? new Date(
                            assessment.icu_admission_at,
                          ).toLocaleString('pt-BR')
                        : '—',
                    },
                    {
                      id: 'eff-transfusion',
                      status: 'completed',
                      label: 'Transfusão',
                      description: `${transfusionMetCount}/${transfusionTotal} critérios adequados`,
                    },
                    {
                      id: 'eff-restraint-eval',
                      status:
                        assessment.restraint_status === 'active'
                          ? 'overdue'
                          : assessment.restraint_status === 'weaning'
                            ? 'in-progress'
                            : 'completed',
                      label: 'Revisão de Contenção',
                      description:
                        RESTRAINT_LABELS[
                          assessment.restraint_status
                        ],
                    },
                    {
                      id: 'eff-frailty',
                      status: 'completed',
                      label: 'Avaliação de Fragilidade',
                      description: getFrailtyLabel(
                        assessment.frailty_score,
                        assessment.frailty_scale,
                      ),
                    },
                  ] as TimelineEvent[]
                }
                domain="general"
              />
            </div>
          )}

          {/* ── Actions ─────────────────────────────────────────────────── */}
          <div
            className="flex items-center gap-3 pt-4 border-t"
            style={{ borderColor: 'var(--semantic-border-default)' }}
          >
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor:
                  'var(--clinical-severity-normal-fill)',
                color: 'var(--clinical-severity-normal-on-fill)',
              }}
            >
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Atualizar Avaliação
            </button>

          </div>
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
