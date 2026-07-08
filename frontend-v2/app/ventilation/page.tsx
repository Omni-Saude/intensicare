'use client';

import React, { useState, useMemo } from 'react';
import {
  Wind,
  Gauge,
  Activity,
  AlertTriangle,
  Clock,
  User,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import VentilationTrendChart from '@/components/VentilationTrendChart';
import {
  type VentilationParameters,
  type VentilationTrend,
  type VentilationMode,
  type PFClass,
  MOCK_PARAMETERS,
  MOCK_HISTORY,
  MOCK_VENT_PATIENTS,
  MODE_LABELS,
  formatFiO2,
  formatPressure,
  formatVolume,
  formatFR,
  formatSpO2,
  formatPFRatio,
  getModeColor,
  classifyPFRatio,
  getPFColor,
  PF_CLASS_LABELS,
  generateMockTrend,
} from '@/lib/ventilation-types';

// ─── View mode ──────────────────────────────────────────────────────────────

type PeriodHours = 24 | 48 | 72;

// ─── Toggle options ─────────────────────────────────────────────────────────

const TOGGLE_OPTIONS: Array<{ value: PeriodHours; label: string }> = [
  { value: 24, label: '24 horas' },
  { value: 48, label: '48 horas' },
  { value: 72, label: '72 horas' },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Formata timestamp ISO → DD/MM HH:mm (PT-BR) */
function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '--/-- --:--';
  }
}

// ─── Parameter Card ─────────────────────────────────────────────────────────

interface ParamCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  accentColor: string;
  accentBg: string;
  isLoading?: boolean;
}

function ParamCard({
  title,
  value,
  subtitle,
  icon,
  accentColor,
  accentBg,
  isLoading = false,
}: ParamCardProps): React.ReactElement {
  if (isLoading) {
    return (
      <div
        className="animate-pulse rounded-xl border p-4 flex items-start gap-3"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
        role="status"
        aria-label={`Carregando ${title}`}
      >
        <div
          className="w-10 h-10 rounded-lg flex-shrink-0"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div className="flex-1 space-y-2">
          <div
            className="h-4 w-20 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-6 w-28 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
      </div>
    );
  }

  return (
    <div
      className="rounded-xl border p-4 flex items-start gap-3"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: accentBg, color: accentColor }}
      >
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <p
          className="text-xs font-medium uppercase tracking-wider"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {title}
        </p>
        <p
          className="text-xl font-bold tabular-nums mt-0.5"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {value}
        </p>
        {subtitle && (
          <p
            className="text-xs mt-0.5"
            style={{ color: accentColor }}
          >
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

// ─── Toggle Button Group ────────────────────────────────────────────────────

interface ToggleGroupProps {
  options: Array<{ value: PeriodHours; label: string }>;
  active: PeriodHours;
  onChange: (value: PeriodHours) => void;
  disabled?: boolean;
}

function ToggleGroup({
  options,
  active,
  onChange,
  disabled = false,
}: ToggleGroupProps): React.ReactElement {
  return (
    <div
      className="inline-flex rounded-lg border overflow-hidden"
      style={{ borderColor: 'var(--semantic-border-default)' }}
      role="radiogroup"
      aria-label="Período de visualização"
    >
      {options.map((opt) => {
        const isActive = opt.value === active;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={isActive}
            disabled={disabled}
            onClick={() => onChange(opt.value)}
            className="px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: isActive
                ? 'var(--action-primary-bg-dark)'
                : 'transparent',
              color: isActive
                ? 'var(--action-primary-text-dark)'
                : 'var(--semantic-text-secondary)',
            }}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

// ─── Patient Selector ───────────────────────────────────────────────────────

interface PatientSelectorProps {
  patients: Array<{ mpiId: string; name: string; bed: string }>;
  selectedMpiId: string;
  onChange: (mpiId: string) => void;
  disabled?: boolean;
}

function PatientSelector({
  patients,
  selectedMpiId,
  onChange,
  disabled = false,
}: PatientSelectorProps): React.ReactElement {
  return (
    <div className="flex items-center gap-2">
      <User
        className="w-4 h-4 flex-shrink-0"
        style={{ color: 'var(--semantic-text-secondary)' }}
        aria-hidden="true"
      />
      <select
        value={selectedMpiId}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="rounded-lg border px-3 py-2 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset disabled:opacity-50"
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
  );
}

// ─── P/F Ratio Badge ────────────────────────────────────────────────────────

function PFRatioBadge({ ratio }: { ratio: number }): React.ReactElement {
  const cls: PFClass = classifyPFRatio(ratio);
  const color = getPFColor(ratio);

  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: color,
        color: '#ffffff',
      }}
    >
      {PF_CLASS_LABELS[cls]}
    </span>
  );
}

// ─── Mode Badge ─────────────────────────────────────────────────────────────

function ModeBadge({ mode }: { mode: VentilationMode }): React.ReactElement {
  const color = getModeColor(mode);

  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: color,
        color: '#ffffff',
      }}
    >
      {MODE_LABELS[mode]}
    </span>
  );
}

// ─── History Table Skeleton ─────────────────────────────────────────────────

function TableSkeleton(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-2" role="status" aria-label="Carregando histórico">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="h-10 rounded-lg"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      ))}
    </div>
  );
}

// ─── Full Page Skeleton ─────────────────────────────────────────────────────

function PageSkeleton(): React.ReactElement {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header skeleton */}
        <div className="animate-pulse space-y-3">
          <div
            className="h-8 w-72 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-5 w-48 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>

        {/* Parameter cards skeleton: 6 cards in 4-col grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <ParamCard
              key={i}
              title=""
              value=""
              icon={null}
              accentColor=""
              accentBg=""
              isLoading
            />
          ))}
        </div>

        {/* Chart skeleton */}
        <div
          className="animate-pulse rounded-xl"
          style={{
            height: '340px',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
          role="status"
          aria-label="Carregando gráfico"
        />

        {/* Table skeleton */}
        <TableSkeleton />
      </div>
    </Layout>
  );
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function VentilationPage(): React.ReactElement {
  const [periodHours, setPeriodHours] = useState<PeriodHours>(24);
  const [selectedParam, setSelectedParam] = useState<string>('FiO2');
  const [selectedPatient, setSelectedPatient] = useState<string>(MOCK_VENT_PATIENTS[0]?.mpiId ?? 'MPI-001');
  const [isLoading, setIsLoading] = useState(false);

  // ── Derived state ─────────────────────────────────────────────────────
  const params: VentilationParameters = useMemo(() => MOCK_PARAMETERS, []);

  const trend: VentilationTrend = useMemo(
    () => generateMockTrend(periodHours),
    [periodHours],
  );

  const history: VentilationParameters[] = useMemo(
    () => MOCK_HISTORY.slice(-5).reverse(), // últimas 5 leituras, mais recente primeiro
    [],
  );

  const pfClass: PFClass = useMemo(
    () => classifyPFRatio(params.PaO2_FiO2_ratio),
    [params.PaO2_FiO2_ratio],
  );

  const pfColor: string = useMemo(
    () => getPFColor(params.PaO2_FiO2_ratio),
    [params.PaO2_FiO2_ratio],
  );

  // ── Loading state ─────────────────────────────────────────────────────
  if (isLoading) {
    return <PageSkeleton />;
  }

  // ── Main render ───────────────────────────────────────────────────────
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
                    backgroundColor: 'var(--clinical-ventilation-pressure)',
                    color: '#ffffff',
                  }}
                >
                  <Wind className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Parâmetros Ventilatórios
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Monitoramento contínuo dos parâmetros do ventilador mecânico
              </p>
            </div>
          </div>

          {/* ── Patient Selector ────────────────────────────────────────── */}
          <PatientSelector
            patients={MOCK_VENT_PATIENTS}
            selectedMpiId={selectedPatient}
            onChange={setSelectedPatient}
            disabled={isLoading}
          />

          {/* ── Main content ────────────────────────────────────────────── */}
          {/* ── Parameter Cards ─────────────────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1: Modo Ventilatório */}
            <ParamCard
              title="Modo Ventilatório"
              value={MODE_LABELS[params.mode]}
              icon={
                <Wind className="w-5 h-5" aria-hidden="true" />
              }
              accentColor={getModeColor(params.mode)}
              accentBg={`${getModeColor(params.mode)}33`}
            />

            {/* Card 2: FiO₂ + PEEP */}
            <ParamCard
              title="FiO₂ / PEEP"
              value={`${formatFiO2(params.FiO2)} / ${formatPressure(params.PEEP)}`}
              subtitle="Fração inspirada / Pressão expiratória"
              icon={
                <Gauge className="w-5 h-5" aria-hidden="true" />
              }
              accentColor="var(--clinical-ventilation-fio2)"
              accentBg="var(--clinical-ventilation-fio2-wash, rgba(59, 130, 246, 0.1))"
            />

            {/* Card 3: VC + FR */}
            <ParamCard
              title="VC / FR"
              value={`${formatVolume(params.VC)} / ${formatFR(params.FR)}`}
              subtitle="Volume corrente / Frequência"
              icon={
                <Activity className="w-5 h-5" aria-hidden="true" />
              }
              accentColor="var(--clinical-ventilation-vc)"
              accentBg="var(--clinical-ventilation-vc-wash, rgba(16, 185, 129, 0.1))"
            />

            {/* Card 4: Pplat + Driving Pressure */}
            <ParamCard
              title="Pplat / ΔP"
              value={`${formatPressure(params.Pplat)} / ${formatPressure(params.driving_pressure)}`}
              subtitle={params.driving_pressure > 15 ? 'Atenção: ΔP elevado' : 'Pressão de platô / Driving'}
              icon={
                params.driving_pressure > 15 ? (
                  <AlertTriangle className="w-5 h-5" aria-hidden="true" />
                ) : (
                  <Gauge className="w-5 h-5" aria-hidden="true" />
                )
              }
              accentColor={
                params.driving_pressure > 15
                  ? 'var(--clinical-ventilation-attention)'
                  : 'var(--clinical-ventilation-pplat)'
              }
              accentBg={
                params.driving_pressure > 15
                  ? 'var(--clinical-ventilation-attention-wash, rgba(245, 158, 11, 0.1))'
                  : 'var(--clinical-ventilation-pplat-wash, rgba(99, 102, 241, 0.1))'
              }
            />

            {/* Card 5: P/F Ratio */}
            <ParamCard
              title="Relação P/F"
              value={formatPFRatio(params.PaO2_FiO2_ratio)}
              subtitle={PF_CLASS_LABELS[pfClass]}
              icon={
                <Activity className="w-5 h-5" aria-hidden="true" />
              }
              accentColor={pfColor}
              accentBg={`${pfColor}33`}
            />

            {/* Card 6: SpO₂ */}
            <ParamCard
              title="SpO₂"
              value={formatSpO2(params.SpO2)}
              subtitle={params.SpO2 >= 92 ? 'Dentro do alvo' : 'Abaixo do alvo'}
              icon={
                <Gauge className="w-5 h-5" aria-hidden="true" />
              }
              accentColor={
                params.SpO2 >= 92
                  ? 'var(--clinical-ventilation-spo2-normal)'
                  : 'var(--clinical-ventilation-spo2-low)'
              }
              accentBg={
                params.SpO2 >= 92
                  ? 'var(--clinical-ventilation-spo2-normal-wash, rgba(34, 197, 94, 0.1))'
                  : 'var(--clinical-ventilation-spo2-low-wash, rgba(239, 68, 68, 0.1))'
              }
            />
          </div>

          {/* ── Chart Section ───────────────────────────────────────── */}
          <div
            className="rounded-xl border p-4"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2
                className="text-sm font-semibold uppercase tracking-wider"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Tendência Ventilatória
              </h2>
              <ToggleGroup
                options={TOGGLE_OPTIONS}
                active={periodHours}
                onChange={setPeriodHours}
              />
            </div>

            <VentilationTrendChart
              trend={trend}
              selectedParam={selectedParam}
              onParamChange={setSelectedParam}
              isLoading={false}
              error={null}
            />
          </div>

          {/* ── History Table ────────────────────────────────────────── */}
          <div
            className="rounded-xl border overflow-hidden"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div
              className="flex items-center gap-2 px-4 py-3 border-b"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-overlay)',
              }}
            >
              <Clock
                className="w-4 h-4"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <h2
                className="text-sm font-semibold uppercase tracking-wider"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                Histórico de Parâmetros
              </h2>
              <span
                className="text-xs ml-auto tabular-nums"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Últimas {history.length} leituras
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr
                    className="border-b"
                    style={{
                      borderColor: 'var(--semantic-border-default)',
                    }}
                  >
                    <th
                      scope="col"
                      className="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      Data/Hora
                    </th>
                    <th
                      scope="col"
                      className="text-left px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      Modo
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      FiO₂
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      PEEP
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      VC
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      FR
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      Pplat
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      ΔP
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      P/F
                    </th>
                    <th
                      scope="col"
                      className="text-right px-4 py-2.5 text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      SpO₂
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((record, idx) => (
                    <tr
                      key={idx}
                      className="border-b transition-colors hover:opacity-80"
                      style={{
                        borderColor: 'var(--semantic-border-default)',
                      }}
                    >
                      <td
                        className="px-4 py-2.5 tabular-nums whitespace-nowrap"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {formatDateTime(record.collected_at)}
                      </td>
                      <td className="px-4 py-2.5">
                        <ModeBadge mode={record.mode} />
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums font-medium"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        {formatFiO2(record.FiO2)}
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {record.PEEP}
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {record.VC}
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {record.FR}
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums"
                        style={{
                          color: record.Pplat > 30
                            ? 'var(--clinical-ventilation-attention)'
                            : 'var(--semantic-text-secondary)',
                        }}
                      >
                        {record.Pplat}
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums"
                        style={{
                          color: record.driving_pressure > 15
                            ? 'var(--clinical-ventilation-attention)'
                            : 'var(--semantic-text-secondary)',
                        }}
                      >
                        {record.driving_pressure}
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <PFRatioBadge ratio={record.PaO2_FiO2_ratio} />
                      </td>
                      <td
                        className="px-4 py-2.5 text-right tabular-nums font-medium"
                        style={{
                          color: record.SpO2 >= 92
                            ? 'var(--clinical-ventilation-spo2-normal)'
                            : 'var(--clinical-ventilation-spo2-low)',
                        }}
                      >
                        {formatSpO2(record.SpO2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
