'use client';

import { useParams } from 'next/navigation';
import useSWR from 'swr';
import {
  fetchPathwayProgress,
  fetchPatientDetail,
  fetchPatientPathways,
  type PathwayProgress,
  type PathwayState,
  type PatientDetailResponse,
  type PatientPathway,
  type SeverityLevel,
} from '@/lib/api';
import { useRealtimeChannel } from '@/lib/websocket';
import { useSetBreadcrumbLabel } from '@/lib/breadcrumb-context';
import { PathwayHeader } from '@/components/pathway/pathway-header';
import { StateFlow } from '@/components/pathway/state-flow';
import { CriteriaList } from '@/components/pathway/criteria-list';
import { RecommendationsPanel } from '@/components/pathway/recommendations-panel';
import { TransitionHistory } from '@/components/pathway/transition-history';
import { Loader2, AlertCircle, GitBranch } from 'lucide-react';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  return 'Erro desconhecido';
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PathwayViewPage() {
  const params = useParams();
  const mpiId = params?.mpi_id as string | undefined;
  const ppIdRaw = params?.pp_id as string | undefined;
  const ppId = ppIdRaw ? Number(ppIdRaw) : undefined;

  // ---------- Data fetching ----------
  const {
    data: progress,
    error,
    isLoading,
    mutate,
  } = useSWR<PathwayProgress>(
    mpiId && ppId ? `pathway-progress-${mpiId}-${ppId}` : null,
    () => fetchPathwayProgress(mpiId!, ppId!),
    { revalidateOnFocus: false },
  );

  // Patient detail: fetched under the same SWR key the patient page uses
  // (`patient-${mpiId}`), so navigating from /patient/{mpi_id} is an
  // instant cache hit here — this call exists purely to recover the
  // patient's display name for the breadcrumb (the progress endpoint only
  // returns mpi_id, not a human-readable name).
  const { data: patient } = useSWR<PatientDetailResponse>(
    mpiId ? `patient-${mpiId}` : null,
    () => fetchPatientDetail(mpiId!),
    { revalidateOnFocus: false },
  );

  // Active pathways list: fetched under the same SWR key the patient page
  // uses (`patient-pathways-${mpiId}`), so navigating from /patient/{mpi_id}
  // is an instant cache hit here. This call exists purely to recover the
  // backend's real, YAML-band-driven severity for THIS pp_id (BUG-F4-01):
  // `PathwayProgress` (the /progress endpoint below) carries no severity
  // field at all — only `/patients/{mpi_id}/pathways` does, via
  // `PatientPathway.severity`, computed by
  // `pathway_enrollment._determine_severity`.
  const { data: pathwaysData } = useSWR<{ items: PatientPathway[]; total: number }>(
    mpiId ? `patient-pathways-${mpiId}` : null,
    () => fetchPatientPathways(mpiId!, 'active'),
    { revalidateOnFocus: false },
  );

  // Realtime: WebSocket + polling fallback (ADR-0034)
  // BUG-F7-04 fix: the backend (PathwayEnrollmentService._publish_pathway_updated,
  // src/intensicare/services/pathway_enrollment.py) publishes the enrollment's
  // primary key as `patient_pathway_id`, not `pp_id` — confirmed both by the
  // publish() call site there and by the alias-channel doc comment in
  // lib/websocket.ts (toBackendChannel). Filtering on `pp_id` meant this
  // page's `pathway.updated` / `pathway.state_changed` events were always
  // silently dropped (payload.pp_id is always undefined, never === ppId).
  useRealtimeChannel('pathway.state_changed', (payload) => {
    const p = payload as Record<string, unknown> | undefined;
    if (!p || (p.mpi_id === mpiId && p.patient_pathway_id === ppId)) mutate();
  }, { fallbackInterval: 60_000, filter: (p) => {
    if (!p) return true;
    const d = p as Record<string, unknown>;
    return d.mpi_id === mpiId && d.patient_pathway_id === ppId;
  }});

  // Breadcrumb: show the pathway's name instead of the raw pp_id once loaded.
  useSetBreadcrumbLabel(ppIdRaw, progress?.pathway_name);
  // Breadcrumb: also re-register the patient's name at this level. The
  // patient page clears its own label on unmount when navigating here, so
  // without this the mpi_id segment regresses to the raw ID — including on
  // a direct deep-link straight to the pathway URL.
  useSetBreadcrumbLabel(mpiId, patient?.patient_name);

  // ---------- No params ----------
  if (!mpiId || ppId === undefined || isNaN(ppId)) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-10 w-10 text-[var(--severity-watch)] mb-3" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
          Parâmetros inválidos
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          MPI ID ou ID da trilha não foram fornecidos corretamente.
        </p>
      </div>
    );
  }

  // ---------- Full-page loading ----------
  if (isLoading && !progress) {
    return (
      <div className="space-y-6">
        {/* Skeleton header */}
        <div className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-5">
          <div className="space-y-3">
            <div className="h-4 w-24 rounded bg-[var(--surface-overlay)] animate-pulse" />
            <div className="flex items-center gap-3">
              <div className="h-5 w-5 rounded bg-[var(--surface-overlay)] animate-pulse" />
              <div className="h-6 w-48 rounded bg-[var(--surface-overlay)] animate-pulse" />
            </div>
            <div className="h-4 w-64 rounded bg-[var(--surface-overlay)] animate-pulse" />
          </div>
        </div>

        {/* Skeleton state flow */}
        <div className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-4">
          <div className="flex gap-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-8 w-28 rounded-full bg-[var(--surface-overlay)] animate-pulse" />
            ))}
          </div>
        </div>

        {/* Skeleton criteria */}
        <div className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-4">
          <div className="h-4 w-32 rounded bg-[var(--surface-overlay)] animate-pulse mb-4" />
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center gap-3 py-3 border-b border-[var(--border-default)] last:border-b-0">
              <div className="h-5 w-5 rounded-full bg-[var(--surface-overlay)] animate-pulse" />
              <div className="flex-1 space-y-1.5">
                <div className="h-4 w-40 rounded bg-[var(--surface-overlay)] animate-pulse" />
                <div className="h-3 w-24 rounded bg-[var(--surface-overlay)] animate-pulse" />
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-[var(--text-secondary)]" aria-hidden="true" />
          <span className="ml-2 text-sm text-[var(--text-secondary)]">Carregando dados da trilha...</span>
        </div>
      </div>
    );
  }

  // ---------- Error ----------
  if (error && !progress) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-10 w-10 text-[var(--severity-critical)] mb-3" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
          Erro ao carregar dados da trilha
        </h1>
        <p className="text-sm text-[var(--text-secondary)] max-w-md mb-4">
          {getErrorMessage(error)}
        </p>
        <button
          type="button"
          onClick={() => mutate()}
          className="inline-flex items-center gap-2 rounded-md border border-[var(--border-default)] px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--surface-overlay)] transition-colors"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  // ---------- Not found ----------
  if (!progress) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <GitBranch className="h-10 w-10 text-[var(--text-secondary)] mb-3" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
          Trilha não encontrada
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Não foi possível localizar os dados desta trilha.
        </p>
      </div>
    );
  }

  // ---------- Render ----------

  const {
    pathway_name: pathwayName,
    current_state: currentState,
    criteria_summary: criteriaSummary,
    criteria,
    state_history: stateHistory,
    trend,
    recommendation,
  } = progress;

  // Derive states list from the current state + history context
  // In a full API, states would come from the pathway definition.
  // We construct a minimal set from history transitions.
  const visitedStates = new Map<string, PathwayState>();
  if (stateHistory) {
    for (const t of stateHistory) {
      if (t.from_state && !visitedStates.has(t.from_state)) {
        visitedStates.set(t.from_state, {
          id: t.from_state,
          name: t.from_state,
          order: visitedStates.size,
        });
      }
      if (!visitedStates.has(t.to_state)) {
        visitedStates.set(t.to_state, {
          id: t.to_state,
          name: t.to_state,
          order: visitedStates.size,
        });
      }
    }
  }
  // Ensure current state is included
  if (!visitedStates.has(currentState.id)) {
    visitedStates.set(currentState.id, {
      ...currentState,
      order: visitedStates.size,
    });
  }
  const statesForFlow = Array.from(visitedStates.values());

  // Recommendations list (split by newline or semicolon)
  const recommendationList = recommendation
    ? recommendation
        .split(/[\n;]/)
        .map((r) => r.trim())
        .filter(Boolean)
    : undefined;

  // Pathway severity (BUG-F4-01): source the backend's real, YAML-band-driven
  // severity (pathway_enrollment._determine_severity) via the active-pathways
  // list fetched above, matched by pp_id. This is the SAME severity the
  // dashboard and patient page display for this pathway, so the header can no
  // longer contradict the recommendations panel / dashboard the way a locally
  // recomputed ratio did.
  //
  // Fallback: only used when this pp_id isn't present in the 'active'-status
  // list (e.g. list still loading, or this pathway is completed/archived) —
  // a crude not-met-ratio heuristic, deliberately inferior to the backend's
  // band-based calculation and kept only so the header never renders with no
  // severity at all.
  const matchedPathway = pathwaysData?.items.find((p) => p.id === ppId);
  let pathwaySeverity: SeverityLevel;
  if (matchedPathway?.severity) {
    pathwaySeverity = matchedPathway.severity;
  } else {
    const notMetRatio = criteriaSummary.total > 0
      ? criteriaSummary.not_met / criteriaSummary.total
      : 0;
    pathwaySeverity =
      notMetRatio >= 0.5 ? 'critical' :
      notMetRatio >= 0.3 ? 'urgent' :
      notMetRatio > 0 ? 'watch' :
      'normal';
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <PathwayHeader
        pathwayName={pathwayName}
        patientName={patient?.patient_name ?? `Paciente ${mpiId}`}
        mpiId={mpiId}
        currentState={currentState.name}
        severity={pathwaySeverity}
        trend={trend}
      />

      {/* State flow */}
      <StateFlow
        states={statesForFlow}
        currentStateId={currentState.id}
        history={stateHistory ?? []}
      />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main: criteria + recommendations */}
        <div className="lg:col-span-2 space-y-6">
          <CriteriaList
            criteria={criteria}
            summary={criteriaSummary}
          />

          <RecommendationsPanel recommendations={recommendationList} />
        </div>

        {/* Sidebar: transition history */}
        <div className="space-y-6">
          <TransitionHistory history={stateHistory} />
        </div>
      </div>
    </div>
  );
}
