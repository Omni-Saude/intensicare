'use client';

import type { PatientDetailResponse } from '@/lib/api';

interface PatientHeaderProps {
  patient: PatientDetailResponse;
}

function mewsColor(mews: number | undefined): string {
  if (mews === undefined) return 'var(--text-secondary)';
  if (mews >= 7) return 'var(--severity-critical)';
  if (mews >= 5) return 'var(--severity-urgent)';
  if (mews >= 3) return 'var(--severity-watch)';
  return 'var(--severity-normal)';
}

function news2Color(news2: number | undefined): string {
  if (news2 === undefined) return 'var(--text-secondary)';
  if (news2 >= 7) return 'var(--severity-critical)';
  if (news2 >= 5) return 'var(--severity-urgent)';
  if (news2 >= 3) return 'var(--severity-watch)';
  return 'var(--severity-normal)';
}

export function PatientHeader({ patient }: PatientHeaderProps) {
  // Extract latest MEWS/NEWS2 from scores
  const latestMews = patient.scores
    .filter((s) => s.name === 'MEWS')
    .sort((a, b) => new Date(b.measured_at).getTime() - new Date(a.measured_at).getTime())[0];
  
  const latestNews2 = patient.scores
    .filter((s) => s.name === 'NEWS2')
    .sort((a, b) => new Date(b.measured_at).getTime() - new Date(a.measured_at).getTime())[0];

  return (
    <header
      className="flex flex-wrap items-start justify-between gap-4 rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-5"
      role="banner"
      aria-label={`Cabeçalho do paciente ${patient.patient_name}`}
    >
      {/* Left: patient identity */}
      <div className="flex flex-col gap-1 min-w-0">
        <h1 className="text-xl font-bold text-[var(--text-primary)] truncate">
          {patient.patient_name}
        </h1>
        <div className="flex flex-wrap items-center gap-3 text-sm text-[var(--text-secondary)]">
          <span className="inline-flex items-center gap-1">
            <span className="text-xs uppercase tracking-wider opacity-60">MPI</span>
            <span className="font-mono text-[var(--text-primary)]">{patient.mpi_id}</span>
          </span>
          <span className="inline-flex items-center gap-1" aria-label={`Leito ${patient.bed}`}>
            <span className="text-xs uppercase tracking-wider opacity-60">Leito</span>
            <span className="font-semibold text-[var(--text-primary)]">{patient.bed}</span>
          </span>
          <span className="inline-flex items-center gap-1" aria-label={`Unidade ${patient.unit}`}>
            <span className="text-xs uppercase tracking-wider opacity-60">Unidade</span>
            <span className="text-[var(--text-primary)]">{patient.unit}</span>
          </span>
        </div>
      </div>

      {/* Right: live scores */}
      <div className="flex items-center gap-3" role="group" aria-label="Escores ao vivo">
        {/* MEWS */}
        <div
          className="flex flex-col items-center rounded-md border border-[var(--border-default)] bg-[var(--surface-overlay)] px-4 py-2 min-w-[72px]"
          aria-label={`MEWS ${latestMews?.value ?? '—'}`}
        >
          <span className="text-xs text-[var(--text-secondary)]">MEWS</span>
          <span
            className="text-2xl font-bold tabular-nums"
            style={{ color: mewsColor(latestMews?.value) }}
          >
            {latestMews?.value ?? '—'}
          </span>
        </div>

        {/* NEWS2 */}
        <div
          className="flex flex-col items-center rounded-md border border-[var(--border-default)] bg-[var(--surface-overlay)] px-4 py-2 min-w-[72px]"
          aria-label={`NEWS2 ${latestNews2?.value ?? '—'}`}
        >
          <span className="text-xs text-[var(--text-secondary)]">NEWS2</span>
          <span
            className="text-2xl font-bold tabular-nums"
            style={{ color: news2Color(latestNews2?.value) }}
          >
            {latestNews2?.value ?? '—'}
          </span>
        </div>
      </div>
    </header>
  );
}
