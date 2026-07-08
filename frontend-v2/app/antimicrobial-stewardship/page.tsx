'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Shield,
  Save,
  User,
  Stethoscope,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import CriteriaChecklist, { type Criterion } from '@/components/CriteriaChecklist';
import StewardshipScoreBadge from '@/components/StewardshipScoreBadge';
import SeverityBadge from '@/components/SeverityBadge';
import ClinicalTooltip from '@/components/ClinicalTooltip';
import {
  type AntimicrobialCriterion,
  type AntimicrobialAssessment,
  type StewardshipSeverity,
  DEFAULT_CRITERIA,
  MOCK_PATIENTS,
  CATEGORY_LABELS,
  computeScore,
  computeSeverity,
  getRecommendation,
} from '@/lib/antimicrobial-types';

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Converte AntimicrobialCriterion → Criterion (label = name). */
function toChecklistCriterion(ac: AntimicrobialCriterion): Criterion {
  return {
    id: ac.id,
    label: ac.name,
    description: ac.description,
    category: ac.category,
    met: ac.met,
  };
}

// ─── Skeleton ────────────────────────────────────────────────────────────────

function SkeletonHeader(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-3" role="status" aria-label="Loading">
      <div
        className="h-8 w-64 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div
        className="h-5 w-48 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function AntimicrobialStewardshipPage(): React.ReactElement {
  const [criteria, setCriteria] = useState<AntimicrobialCriterion[]>(
    () => DEFAULT_CRITERIA,
  );
  const [selectedPatient, setSelectedPatient] = useState<string>(
    MOCK_PATIENTS[0]!.mpiId,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [simulatedError, setSimulatedError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // ─── Derived state ─────────────────────────────────────────────────────────

  const score = useMemo(() => computeScore(criteria), [criteria]);
  const severity: StewardshipSeverity = useMemo(
    () => computeSeverity(score),
    [score],
  );
  const recommendation = useMemo(
    () => getRecommendation(severity, score),
    [severity, score],
  );
  const selectedPatientData = MOCK_PATIENTS.find(
    (p) => p.mpiId === selectedPatient,
  );

  /** Mapeia StewardshipSeverity → SeverityBadge severity. */
  const clinicalSeverity = useMemo(() => {
    switch (severity) {
      case 'VERMELHO':
        return 'critical' as const;
      case 'AMARELO':
        return 'watch' as const;
      case 'NEUTRO':
        return 'normal' as const;
    }
  }, [severity]);

  // ─── Handlers ──────────────────────────────────────────────────────────────

  const handleToggle = useCallback((id: string, met: boolean) => {
    setCriteria((prev) => prev.map((c) => (c.id === id ? { ...c, met } : c)));
    setSaveSuccess(false);
  }, []);

  const handleSave = useCallback(() => {
    setSimulatedError(null);
    setIsLoading(true);
    setSaveSuccess(false);

    // Mock async save
    const timer = setTimeout(() => {
      const assessment: AntimicrobialAssessment = {
        patientMpiId: selectedPatient,
        criteria,
        score,
        severity,
        recommendation,
        assessedAt: new Date().toISOString(),
        assessedBy: 'Dr. Plantonista',
      };
      console.log(
        '[AntimicrobialStewardship] Assessment saved:',
        assessment,
      );
      setIsLoading(false);
      setSaveSuccess(true);
    }, 800);

    return () => clearTimeout(timer);
  }, [selectedPatient, criteria, score, severity, recommendation]);

  const handleReset = useCallback(() => {
    setCriteria(DEFAULT_CRITERIA);
    setSaveSuccess(false);
    setSimulatedError(null);
  }, []);

  const handleSimulateError = useCallback(() => {
    setSimulatedError(
      'Erro ao carregar dados do paciente. Verifique a conexão com o servidor e tente novamente.',
    );
  }, []);

  // ─── Loading state ─────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto space-y-6">
          <SkeletonHeader />
          <CriteriaChecklist items={[]} domain="antimicrobial" isLoading />
          <StewardshipScoreBadge
            score={0}
            totalCriteria={12}
            severity="NEUTRO"
            isLoading
          />
        </div>
      </Layout>
    );
  }

  // ─── Main render ───────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-3xl mx-auto space-y-6 pb-12">
          {/* ── Header ─────────────────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor:
                      'var(--clinical-antimicrobial-stewardship-optimal-fill)',
                    color:
                      'var(--clinical-antimicrobial-stewardship-optimal-on-fill)',
                  }}
                >
                  <Shield className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Antimicrobial Stewardship
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Avaliação estruturada de conformidade antimicrobiana — 12
                critérios de auditoria clínica
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
                onChange={(e) => {
                  setSelectedPatient(e.target.value);
                  setSaveSuccess(false);
                }}
                className="text-sm rounded-lg border px-3 py-2 min-w-[200px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
                aria-label="Selecionar paciente"
              >
                {MOCK_PATIENTS.map((p) => (
                  <option key={p.mpiId} value={p.mpiId}>
                    {p.name} — {p.bed}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* ── Patient info bar ────────────────────────────────────────── */}
          {selectedPatientData && (
            <div
              className="flex items-center gap-3 px-4 py-3 rounded-xl border text-sm"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <Stethoscope
                className="w-4 h-4 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <span style={{ color: 'var(--semantic-text-primary)' }}>
                <strong>{selectedPatientData.name}</strong>
              </span>
              <span
                className="tabular-nums"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                MPI: {selectedPatientData.mpiId}
              </span>
              <span
                className="tabular-nums ml-auto"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Leito: {selectedPatientData.bed}
              </span>
              <SeverityBadge severity={clinicalSeverity} showLabel={false} />
            </div>
          )}

          {/* ── Error state (simulated) ─────────────────────────────────── */}
          {simulatedError && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex items-center gap-3 px-4 py-3 rounded-xl border text-sm"
              style={{
                backgroundColor: 'var(--feedback-error-bg-dark)',
                color: 'var(--feedback-error-text-dark)',
                borderColor: 'var(--feedback-error-border-dark)',
              }}
            >
              <AlertTriangle
                className="w-5 h-5 flex-shrink-0"
                aria-hidden="true"
              />
              <span className="flex-1">{simulatedError}</span>
              <button
                onClick={() => setSimulatedError(null)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-opacity hover:opacity-80"
                style={{
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
              >
                Fechar
              </button>
            </div>
          )}

          {/* ── Score badge ─────────────────────────────────────────────── */}
          <div>
            <ClinicalTooltip term="Stewardship Score">
              <h2
                className="text-sm font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Score de Conformidade
              </h2>
            </ClinicalTooltip>
            <StewardshipScoreBadge
              score={score}
              totalCriteria={12}
              severity={severity}
              recommendation={recommendation}
            />
          </div>

          {/* ── Criteria checklist ──────────────────────────────────────── */}
          <div>
            <h2
              className="text-sm font-semibold uppercase tracking-wider mb-3"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Critérios de Avaliação
            </h2>

            {/* Category sections */}
            <div className="space-y-4">
              {(Object.keys(CATEGORY_LABELS) as Array<keyof typeof CATEGORY_LABELS>).map(
                (category) => {
                  const categoryCriteria = criteria.filter(
                    (c) => c.category === category,
                  );
                  if (categoryCriteria.length === 0) return null;

                  const metInCategory = categoryCriteria.filter(
                    (c) => c.met,
                  ).length;

                  return (
                    <div
                      key={category}
                      className="rounded-xl border overflow-hidden"
                      style={{
                        borderColor: 'var(--semantic-border-default)',
                        backgroundColor:
                          'var(--semantic-surface-raised)',
                      }}
                    >
                      {/* Category header */}
                      <div
                        className="flex items-center gap-2 px-4 py-2.5 border-b"
                        style={{
                          borderColor: 'var(--semantic-border-default)',
                          backgroundColor:
                            'var(--semantic-surface-overlay)',
                        }}
                      >
                        <span
                          className="text-xs font-semibold"
                          style={{
                            color: 'var(--semantic-text-primary)',
                          }}
                        >
                          {CATEGORY_LABELS[category]}
                        </span>
                        <span
                          className="text-xs tabular-nums"
                          style={{
                            color: 'var(--semantic-text-secondary)',
                          }}
                        >
                          ({metInCategory}/{categoryCriteria.length}{' '}
                          não conformidades)
                        </span>
                      </div>

                      {/* Category criteria */}
                      <CriteriaChecklist
                        items={categoryCriteria.map(
                          toChecklistCriterion,
                        )}
                        domain="antimicrobial"
                        onToggle={handleToggle}
                        readOnly={false}
                      />
                    </div>
                  );
                },
              )}
            </div>
          </div>

          {/* ── Actions ─────────────────────────────────────────────────── */}
          <div className="flex items-center gap-3 pt-4 border-t" style={{ borderColor: 'var(--semantic-border-default)' }}>
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor:
                  'var(--clinical-antimicrobial-stewardship-optimal-fill)',
                color:
                  'var(--clinical-antimicrobial-stewardship-optimal-on-fill)',
              }}
            >
              <Save className="w-4 h-4" aria-hidden="true" />
              Salvar Avaliação
            </button>

            <button
              onClick={handleReset}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 hover:opacity-80"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
                borderColor: 'var(--semantic-border-default)',
                borderWidth: '1px',
              }}
            >
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Resetar
            </button>

            <button
              onClick={handleSimulateError}
              className="inline-flex items-center gap-2 px-3 py-2.5 rounded-lg text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 hover:opacity-80 ml-auto"
              style={{
                backgroundColor: 'var(--feedback-error-bg-dark)',
                color: 'var(--feedback-error-text-dark)',
                borderColor: 'var(--feedback-error-border-dark)',
                borderWidth: '1px',
              }}
            >
              <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
              Simular Erro
            </button>
          </div>

          {/* ── Save confirmation ──────────────────────────────────────── */}
          {saveSuccess && (
            <div
              role="status"
              aria-live="polite"
              className="flex items-center gap-2 px-4 py-3 rounded-xl border text-sm"
              style={{
                borderColor:
                  'var(--clinical-antimicrobial-stewardship-optimal-signal)',
                backgroundColor:
                  'var(--clinical-antimicrobial-stewardship-optimal-wash)',
                color:
                  'var(--clinical-antimicrobial-stewardship-optimal-on-surface)',
              }}
            >
              <Shield className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              <span>
                Avaliação salva com sucesso para{' '}
                <strong>{selectedPatientData?.name}</strong> — Score:{' '}
                {score}/12 ({severity})
              </span>
            </div>
          )}
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
