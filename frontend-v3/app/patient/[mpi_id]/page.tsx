'use client';

import { useParams } from 'next/navigation';
import useSWR from 'swr';
import {
  fetchPatientDetail,
  fetchPatientPathways,
  fetchAlerts,
  acknowledgeAlert,
  escalateAlert,
  type PatientDetailResponse,
  type PatientPathway,
  type AlertInfo,
} from '@/lib/api';
import { useRealtimeChannel } from '@/lib/websocket';
import { PatientHeader } from '@/components/patient/patient-header';
import { VitalsPanel } from '@/components/patient/vitals-panel';
import { ScoreTimeline } from '@/components/patient/score-timeline';
import { ActivePathways } from '@/components/patient/active-pathways';
import { AlertsPanel } from '@/components/patient/alerts-panel';
import { Loader2, AlertCircle, Stethoscope } from 'lucide-react';

// ---------- helpers ----------

function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  return 'Erro desconhecido';
}

// ---------- page ----------

export default function PatientDetailPage() {
  const params = useParams();
  const mpiId = params?.mpi_id as string | undefined;

  // Patient detail
  const {
    data: patient,
    error: patientError,
    isLoading: patientLoading,
    mutate: mutatePatient,
  } = useSWR<PatientDetailResponse>(
    mpiId ? `patient-${mpiId}` : null,
    () => fetchPatientDetail(mpiId!),
    { revalidateOnFocus: false },
  );

  // Active pathways
  const {
    data: pathwaysData,
    error: pathwaysError,
    isLoading: pathwaysLoading,
    mutate: mutatePathways,
  } = useSWR<{ items: PatientPathway[]; total: number }>(
    mpiId ? `patient-pathways-${mpiId}` : null,
    () => fetchPatientPathways(mpiId!, 'active'),
    { revalidateOnFocus: false },
  );

  // Alerts for this patient
  const {
    data: alertsData,
    error: alertsError,
    isLoading: alertsLoading,
    mutate: mutateAlerts,
  } = useSWR<{ items: AlertInfo[]; total: number }>(
    mpiId ? `patient-alerts-${mpiId}` : null,
    () => fetchAlerts({ limit: 50 }),
    { revalidateOnFocus: false },
  );

  // Realtime: WebSocket + polling fallback (ADR-0034)
  useRealtimeChannel('vitals.updated', (payload) => {
    const p = payload as Record<string, unknown> | undefined;
    if (!p || p.mpi_id === mpiId) mutatePatient();
  }, { fallbackInterval: 60_000, filter: (p) => !p || (p as Record<string, unknown>).mpi_id === mpiId });
  useRealtimeChannel('pathway.updated', (payload) => {
    const p = payload as Record<string, unknown> | undefined;
    if (!p || p.mpi_id === mpiId) mutatePathways();
  }, { fallbackInterval: 60_000, filter: (p) => !p || (p as Record<string, unknown>).mpi_id === mpiId });
  useRealtimeChannel('alert.raised', () => mutateAlerts(), { fallbackInterval: 60_000 });
  useRealtimeChannel('alert.updated', () => mutateAlerts(), { fallbackInterval: 60_000 });

  // Filter alerts to only those belonging to this patient
  const patientAlerts = (alertsData?.items ?? []).filter(
    (a) => a.mpi_id === mpiId,
  );

  // --- No mpiId ---
  if (!mpiId) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-10 w-10 text-[var(--severity-watch)] mb-3" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
          Paciente não identificado
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Nenhum MPI ID foi fornecido na URL.
        </p>
      </div>
    );
  }

  // --- Full-page loading ---
  if (patientLoading && !patient) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <Loader2 className="h-10 w-10 animate-spin text-[var(--text-secondary)] mb-3" aria-hidden="true" />
        <p className="text-sm text-[var(--text-secondary)]">
          Carregando dados do paciente...
        </p>
      </div>
    );
  }

  // --- Full-page error ---
  if (patientError && !patient) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-10 w-10 text-[var(--severity-critical)] mb-3" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
          Erro ao carregar paciente
        </h1>
        <p className="text-sm text-[var(--text-secondary)] max-w-md">
          {getErrorMessage(patientError)}
        </p>
      </div>
    );
  }

  // --- Patient not found ---
  if (!patient) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <Stethoscope className="h-10 w-10 text-[var(--text-secondary)] mb-3" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-[var(--text-primary)] mb-1">
          Paciente não encontrado
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Não foi possível localizar os dados do paciente {mpiId}.
        </p>
      </div>
    );
  }

  // ---------- handlers ----------

  const handleAcknowledge = async (alertId: number) => {
    await acknowledgeAlert(alertId);
    await mutateAlerts();
  };

  const handleEscalate = async (alertId: number) => {
    await escalateAlert(alertId);
    await mutateAlerts();
  };

  // ---------- render ----------

  const pathways = pathwaysData?.items ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <PatientHeader patient={patient} />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main column */}
        <div className="xl:col-span-2 space-y-6">
          {/* Vitals */}
          <VitalsPanel
            vitals={patient.vitals}
            isLoading={patientLoading}
            error={patientError ? getErrorMessage(patientError) : null}
          />

          {/* Score timeline */}
          <ScoreTimeline
            scores={patient.scores}
            isLoading={patientLoading}
            error={patientError ? getErrorMessage(patientError) : null}
          />

          {/* Active Pathways — the heart of the page */}
          <ActivePathways
            pathways={pathways}
            isLoading={pathwaysLoading}
            error={pathwaysError ? getErrorMessage(pathwaysError) : null}
          />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <AlertsPanel
            alerts={patientAlerts}
            isLoading={alertsLoading}
            error={alertsError ? getErrorMessage(alertsError) : null}
            onAcknowledge={handleAcknowledge}
            onEscalate={handleEscalate}
          />
        </div>
      </div>
    </div>
  );
}
