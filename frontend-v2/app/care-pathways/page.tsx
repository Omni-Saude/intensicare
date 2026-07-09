'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  GitBranch,
  Play,
  CheckCircle,
  Clock,
  XOctagon,
  AlertTriangle,
  Loader2,
  User,
  Stethoscope,
  ChevronRight,
  Activity,
  Bed,
  List,
  Columns,
} from 'lucide-react';
import { FullScreenLayout } from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import PathwayBoard from '@/components/PathwayBoard';
import SeverityBadge from '@/components/SeverityBadge';
import type {
  PatientPathway,
  PathwayPatient,
  PathwayProgress,
} from '@/lib/pathway-types';
import { fetchBedGrid, fetchPatientPathways, fetchPathwayProgress } from '@/lib/api';

// ─── Unit Options ──────────────────────────────────────────────────────────

type UnitOption = 'uti-1' | 'uti-2' | 'uti-cardio';

const UNITS: { value: UnitOption; label: string }[] = [
  { value: 'uti-1', label: 'UTI 1' },
  { value: 'uti-2', label: 'UTI 2' },
  { value: 'uti-cardio', label: 'UTI Cardio' },
];

// ─── Skeleton Components ──────────────────────────────────────────────────

function SplitScreenSkeleton(): React.ReactElement {
  return (
    <div className="flex h-full animate-pulse" role="status" aria-label="Carregando">
      {/* Left panel skeleton */}
      <aside className="hidden md:flex md:w-[280px] flex-col border-r p-4 space-y-3 flex-shrink-0"
        style={{ borderColor: 'var(--semantic-border-default)' }}>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-lg"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}>
            <div className="w-8 h-8 rounded-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
            <div className="flex-1 space-y-1.5">
              <div className="h-3.5 rounded w-2/3"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
              <div className="h-2.5 rounded w-1/2"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
            </div>
          </div>
        ))}
      </aside>
      {/* Right panel skeleton */}
      <main className="flex-1 p-6 space-y-4">
        <div className="h-7 rounded w-64"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
        <div className="h-3 rounded-full w-full"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div className="space-y-3">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="h-10 rounded"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
            ))}
          </div>
          <div className="space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-16 rounded"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

// ─── Patient List Item ────────────────────────────────────────────────────

function PatientListItem({
  patient,
  isSelected,
  onClick,
  pathways,
}: {
  patient: PathwayPatient;
  isSelected: boolean;
  onClick: () => void;
  pathways: PatientPathway[];
}): React.ReactElement {
  const activePathways = pathways.filter((pp) => pp.status === 'active');
  const hasCritical = activePathways.some((pp) => pp.severity === 'critical');
  const hasUrgent = activePathways.some((pp) => pp.severity === 'urgent');
  const hasWatch = activePathways.some((pp) => pp.severity === 'watch');

  const severitySignal = hasCritical
    ? 'critical'
    : hasUrgent
    ? 'urgent'
    : hasWatch
    ? 'watch'
    : 'normal';

  const leftBorderColor =
    severitySignal === 'critical'
      ? 'var(--clinical-pathway-overdue-signal)'
      : severitySignal === 'urgent'
      ? 'var(--clinical-severity-urgent-signal)'
      : severitySignal === 'watch'
      ? 'var(--clinical-severity-watch-signal)'
      : isSelected
      ? 'var(--clinical-pathway-active-signal)'
      : 'transparent';

  const bgColor = isSelected
    ? 'var(--clinical-pathway-active-fill)'
    : hasCritical
    ? 'var(--clinical-pathway-overdue-fill)'
    : 'var(--semantic-surface-raised)';

  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-3 border-l-4 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
        hasCritical ? 'animate-pulse-critical' : ''
      }`}
      style={{
        borderColor: leftBorderColor,
        borderLeftWidth: '4px',
        backgroundColor: bgColor,
        color: isSelected
          ? 'var(--clinical-pathway-active-on-surface)'
          : 'var(--semantic-text-primary)',
        cursor: 'pointer',
      }}
      aria-label={`${patient.name}, Leito ${patient.bed}, ${patient.pathway_count} pathway(s)${
        hasCritical ? ', crítico' : ''
      }`}
      aria-current={isSelected ? 'true' : undefined}
    >
      <div className="flex items-center gap-3">
        {/* Bed icon + number */}
        <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}>
          <Bed className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-semibold truncate">{patient.name}</span>
            {hasCritical && (
              <XOctagon className="w-3.5 h-3.5 flex-shrink-0"
                style={{ color: 'var(--clinical-pathway-overdue-signal)' }}
                aria-label="Crítico" />
            )}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              {patient.bed}
            </span>
            {patient.pathway_count > 0 && (
              <span className="flex items-center gap-1 text-xs">
                <GitBranch className="w-3 h-3" aria-hidden="true" />
                <span style={{ color: 'var(--semantic-text-secondary)' }}>
                  {patient.pathway_count}
                </span>
              </span>
            )}
          </div>
        </div>

        <ChevronRight
          className="w-4 h-4 flex-shrink-0"
          style={{
            color: 'var(--semantic-text-secondary)',
            opacity: isSelected ? 1 : 0.3,
          }}
          aria-hidden="true"
        />
      </div>
    </button>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export default function CarePathwaysPage(): React.ReactElement {
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [selectedPathwayIdx, setSelectedPathwayIdx] = useState<number>(0);
  const [unit, setUnit] = useState<UnitOption>('uti-1');
  const [viewMode, setViewMode] = useState<'split' | 'list' | 'board'>('split');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patients, setPatients] = useState<PathwayPatient[]>([]);
  const [patientPathways, setPatientPathways] = useState<PatientPathway[]>([]);
  const [currentProgress, setCurrentProgress] = useState<PathwayProgress | null>(null);

  // ─── Carregar lista de pacientes via API de leitos ───────────────────
  useEffect(() => {
    setLoading(true);
    fetchBedGrid()
      .then((data) => {
        const occupied = data.beds.filter(
          (b) => b.status === 'occupied' && b.current_patient_mpi_id && b.current_patient_name,
        );
        const mapped: PathwayPatient[] = occupied.map((b) => ({
          id: b.current_patient_mpi_id!,
          mpi_id: b.current_patient_mpi_id!,
          name: b.current_patient_name!,
          bed: b.bed_id,
          age: 0,
          admission_diagnosis: '',
          pathway_count: 0,
          has_overdue: false,
        }));
        setPatients(mapped);
        setError(null);
      })
      .catch((err) => setError(err.message || 'Erro ao carregar pacientes'))
      .finally(() => setLoading(false));
  }, []);

  // ─── Filtrar pacientes por unidade ────────────────────────────────────
  const filteredPatients = useMemo(() => {
    const unitMap: Record<UnitOption, string> = {
      'uti-1': 'UTI-1',
      'uti-2': 'UTI-2',
      'uti-cardio': 'UTI Cardio',
    };
    return patients.filter((p) => p.bed.startsWith(unitMap[unit]));
  }, [patients, unit]);

  // ─── Auto-selecionar primeiro paciente quando lista carregar ──────────
  useEffect(() => {
    if (!selectedPatientId && filteredPatients.length > 0 && filteredPatients[0]) {
      setSelectedPatientId(filteredPatients[0].id);
    }
  }, [filteredPatients, selectedPatientId]);

  const selectedPatient = useMemo(
    () => patients.find((p) => p.id === selectedPatientId) ?? null,
    [patients, selectedPatientId],
  );

  // ─── Carregar pathways do paciente selecionado ───────────────────────
  useEffect(() => {
    if (!selectedPatient) {
      setPatientPathways([]);
      return;
    }
    fetchPatientPathways(selectedPatient.mpi_id)
      .then((data) => {
        const mapped: PatientPathway[] = data.pathways.map((apiPp) => ({
          id: String(apiPp.id),
          mpi_id: apiPp.mpi_id,
          pathway: {
            id: String(apiPp.pathway.id),
            name: apiPp.pathway.name,
            description: apiPp.pathway.description,
            slug: apiPp.pathway.slug,
            active: apiPp.pathway.active,
            states: apiPp.pathway.states.map((s) => ({
              id: s.id,
              name: s.name,
              order: s.order,
              description: '',
              is_terminal: s.is_terminal ?? false,
            })),
            criteria: apiPp.pathway.criteria.map((c) => ({
              id: c.id,
              name: c.name,
              category: c.category,
              description: '',
              unit: c.unit,
              normal_range: c.normal_range,
              alert_threshold: c.alert_threshold,
              met: apiPp.criteria.find((e) => e.criteria_id === c.id)?.met ?? false,
              value: apiPp.criteria.find((e) => e.criteria_id === c.id)?.value,
              evaluated_at: apiPp.criteria.find((e) => e.criteria_id === c.id)?.evaluated_at,
            })),
          },
          current_state: (() => {
            const found = apiPp.pathway.states.find((s) => s.id === apiPp.current_state_id);
            return {
              id: found?.id ?? apiPp.current_state_id,
              name: found?.name ?? apiPp.current_state_id,
              order: found?.order ?? 0,
              description: '',
              is_terminal: found?.is_terminal ?? false,
            };
          })(),
          criteria: apiPp.pathway.criteria.map((c) => ({
            id: c.id,
            name: c.name,
            category: c.category,
            description: '',
            unit: c.unit,
            normal_range: c.normal_range,
            alert_threshold: c.alert_threshold,
            met: apiPp.criteria.find((e) => e.criteria_id === c.id)?.met ?? false,
            value: apiPp.criteria.find((e) => e.criteria_id === c.id)?.value,
            evaluated_at: apiPp.criteria.find((e) => e.criteria_id === c.id)?.evaluated_at,
          })),
          status: apiPp.status,
          severity: apiPp.severity,
          enrolled_at: apiPp.enrolled_at,
          enrolled_by: '',
          completed_at: apiPp.completed_at,
          updated_at: apiPp.enrolled_at,
        }));
        setPatientPathways(mapped);
        setError(null);
      })
      .catch((err) => setError(err.message || 'Erro ao carregar pathways'));
  }, [selectedPatient]);

  const currentPathway = patientPathways[selectedPathwayIdx] ?? null;

  // ─── Carregar progresso do pathway selecionado ───────────────────────
  useEffect(() => {
    if (!currentPathway || !selectedPatient) {
      setCurrentProgress(null);
      return;
    }
    fetchPathwayProgress(selectedPatient.mpi_id, Number(currentPathway.id))
      .then((progress) => {
        setCurrentProgress({
          patient_pathway_id: String(progress.patient_pathway_id),
          mpi_id: progress.mpi_id,
          pathway_name: progress.pathway_name,
          current_state: progress.current_state,
          criteria_summary: progress.criteria_summary,
          criteria: currentPathway.criteria,
          state_history: progress.state_history.map((entry) => ({
            from_state: entry.from_state,
            to_state: entry.to_state,
            changed_at: entry.changed_at,
            reason: entry.reason,
          })),
          trend: progress.trend as PathwayProgress['trend'],
          recommendation: progress.recommendation,
        });
      })
      .catch((err) => {
        console.error('Erro ao carregar progresso:', err);
        setCurrentProgress(null);
      });
  }, [currentPathway, selectedPatient]);

  const handleSelectPatient = useCallback((patientId: string) => {
    setSelectedPatientId(patientId);
    setSelectedPathwayIdx(0);
    setCurrentProgress(null);
    if (viewMode === 'list') {
      setViewMode('board');
    }
  }, [viewMode]);

  const handleSelectPathway = useCallback((idx: number) => {
    setSelectedPathwayIdx(idx);
    setCurrentProgress(null);
  }, []);

  // ─── Mobile: view mode toggle ──────────────────────────────────────────

  const showList = viewMode === 'split' || viewMode === 'list';
  const showBoard = viewMode === 'split' || viewMode === 'board';

  // ─── Loading ────────────────────────────────────────────────────────────
  const pageLoading = loading;

  // ─── Error ──────────────────────────────────────────────────────────────
  const pageError = error;

  return (
    <FullScreenLayout>
      <ErrorBoundary>
        <div className="flex flex-col h-[calc(100vh-56px)]">
          {/* ── Global Header ──────────────────────────────────────────── */}
          <header
            className="flex items-center justify-between px-6 py-3 border-b flex-shrink-0"
            style={{ borderColor: 'var(--semantic-border-default)' }}
          >
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: 'var(--clinical-pathway-active-fill)',
                  }}
                >
                  <GitBranch
                    className="w-5 h-5"
                    style={{ color: 'var(--clinical-pathway-active-signal)' }}
                    aria-hidden="true"
                  />
                </div>
                <h1
                  className="text-lg font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Care Pathways
                </h1>
              </div>

              {/* Unit selector */}
              <div className="flex items-center gap-2 ml-4">
                <label
                  className="text-xs font-medium"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  htmlFor="unit-selector"
                >
                  Unidade:
                </label>
                <select
                  id="unit-selector"
                  value={unit}
                  onChange={(e) => setUnit(e.target.value as UnitOption)}
                  className="text-sm rounded-lg border px-3 py-1.5 outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                >
                  {UNITS.map((u) => (
                    <option key={u.value} value={u.value}>
                      {u.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Mobile: view toggle */}
            <div className="flex md:hidden items-center gap-1">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg ${
                  viewMode === 'list' ? '' : 'opacity-50'
                }`}
                style={{
                  backgroundColor:
                    viewMode === 'list'
                      ? 'var(--semantic-surface-overlay)'
                      : 'transparent',
                }}
                aria-label="Ver lista de pacientes"
                aria-pressed={viewMode === 'list'}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('board')}
                className={`p-2 rounded-lg ${
                  viewMode === 'board' ? '' : 'opacity-50'
                }`}
                style={{
                  backgroundColor:
                    viewMode === 'board'
                      ? 'var(--semantic-surface-overlay)'
                      : 'transparent',
                }}
                aria-label="Ver pathway board"
                aria-pressed={viewMode === 'board'}
              >
                <Columns className="w-4 h-4" />
              </button>
            </div>
          </header>

          {/* ── Page States ────────────────────────────────────────────── */}

          {/* Loading */}
          {pageLoading && <SplitScreenSkeleton />}

          {/* Error */}
          {pageError && (
            <div className="flex items-center justify-center flex-1">
              <div
                role="alert"
                aria-live="assertive"
                className="flex flex-col items-center gap-3 p-8 rounded-xl border max-w-md text-center"
                style={{
                  backgroundColor: 'var(--feedback-error-bg-dark)',
                  color: 'var(--feedback-error-text-dark)',
                  borderColor: 'var(--feedback-error-border-dark)',
                }}
              >
                <AlertTriangle className="w-10 h-10" aria-hidden="true" />
                <div>
                  <h2 className="font-semibold text-base">
                    Erro ao carregar
                  </h2>
                  <p className="text-sm mt-1 opacity-90">{pageError}</p>
                </div>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-2 px-4 py-2 rounded-lg text-sm font-medium border"
                  style={{
                    borderColor: 'var(--semantic-border-default)',
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                  }}
                >
                  Tentar novamente
                </button>
              </div>
            </div>
          )}

          {/* Normal state */}
          {!pageLoading && !pageError && (
            <div className="flex flex-1 overflow-hidden">
              {/* ── Left Panel: Patient List ──────────────────────────── */}
              {(showList || !('ontouchstart' in window)) && (
                <aside
                  className={`${
                    viewMode === 'list'
                      ? 'w-full'
                      : 'hidden md:flex md:w-[280px]'
                  } flex-col border-r flex-shrink-0`}
                  style={{ borderColor: 'var(--semantic-border-default)' }}
                >
                  {/* Panel header */}
                  <div
                    className="px-4 py-3 border-b"
                    style={{ borderColor: 'var(--semantic-border-default)' }}
                  >
                    <h2
                      className="text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      Pacientes
                    </h2>
                    <p
                      className="text-[10px] mt-0.5"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      {filteredPatients.length} pacientes na unidade
                    </p>
                  </div>

                  {/* Patient list */}
                  <div className="flex-1 overflow-y-auto">
                    {filteredPatients.length === 0 ? (
                      <div
                        className="flex flex-col items-center justify-center gap-2 py-12 text-sm"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                        role="status"
                        aria-label="Nenhum paciente nesta unidade"
                      >
                        <Bed className="w-10 h-10 opacity-30" aria-hidden="true" />
                        <p>Nenhum paciente nesta unidade</p>
                      </div>
                    ) : (
                      filteredPatients.map((patient) => {
                        const pathways = patient.id === selectedPatientId ? patientPathways : [];
                        return (
                          <PatientListItem
                            key={patient.id}
                            patient={patient}
                            isSelected={patient.id === selectedPatientId}
                            onClick={() => handleSelectPatient(patient.id)}
                            pathways={pathways}
                          />
                        );
                      })
                    )}
                  </div>
                </aside>
              )}

              {/* ── Right Panel: Pathway Board ────────────────────────── */}
              {showBoard && (
                <main
                  className={`${
                    viewMode === 'board' ? 'w-full' : 'hidden md:flex md:flex-1'
                  } flex-col overflow-hidden`}
                >
                  {/* Sub-header: Pathway selector when multiple pathways */}
                  {patientPathways.length > 1 && (
                    <div
                      className="px-6 py-2 border-b flex items-center gap-1 overflow-x-auto"
                      style={{ borderColor: 'var(--semantic-border-default)' }}
                    >
                      <span
                        className="text-xs font-medium mr-2 flex-shrink-0"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        Pathways:
                      </span>
                      {patientPathways.map((pp, idx) => {
                        const isActive = idx === selectedPathwayIdx;
                        const hasProgress = currentProgress !== null && currentProgress.patient_pathway_id === String(pp.id);
                        const isOverdue =
                          pp.severity === 'critical' ||
                          pp.severity === 'urgent';

                        return (
                          <button
                            key={pp.id}
                            onClick={() => handleSelectPathway(idx)}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                              isOverdue ? 'animate-pulse-critical' : ''
                            }`}
                            style={{
                              backgroundColor: isActive
                                ? 'var(--clinical-pathway-active-fill)'
                                : 'transparent',
                              color: isActive
                                ? 'var(--clinical-pathway-active-on-surface)'
                                : isOverdue
                                ? 'var(--clinical-pathway-overdue-on-surface)'
                                : 'var(--semantic-text-secondary)',
                              borderColor: isActive
                                ? 'var(--clinical-pathway-active-signal)'
                                : isOverdue
                                ? 'var(--clinical-pathway-overdue-signal)'
                                : 'transparent',
                              borderWidth: '1px',
                              borderStyle: 'solid',
                            }}
                          >
                            <GitBranch
                              className="w-3 h-3"
                              aria-hidden="true"
                            />
                            <span>{pp.pathway.name}</span>
                            {pp.status === 'active' ? (
                              <Play
                                className="w-2.5 h-2.5"
                                aria-hidden="true"
                              />
                            ) : (
                              <CheckCircle
                                className="w-2.5 h-2.5"
                                aria-hidden="true"
                              />
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Pathway path or no-pathway message */}
                  {patientPathways.length === 0 ? (
                    <div
                      className="flex flex-col items-center justify-center flex-1 gap-4 py-20"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                      role="status"
                      aria-label="Nenhum pathway para este paciente"
                    >
                      <GitBranch
                        className="w-16 h-16 opacity-20"
                        aria-hidden="true"
                      />
                      <div className="text-center space-y-1">
                        <p className="text-base font-medium">
                          Paciente sem pathway
                        </p>
                        <p className="text-sm">
                          {selectedPatient?.name} não está inscrito em nenhum
                          pathway clínico.
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 overflow-hidden">
                      <PathwayBoard
                        patientPathway={currentPathway}
                        progress={currentProgress}
                        isLoading={pageLoading}
                        error={null}
                      />
                    </div>
                  )}
                </main>
              )}
            </div>
          )}
        </div>
      </ErrorBoundary>
    </FullScreenLayout>
  );
}
