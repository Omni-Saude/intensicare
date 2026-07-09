'use client';

import React, {
  useState,
  useMemo,
  useCallback,
  useEffect,
} from 'react';
import {
  Brain,
  Activity,
  AlertTriangle,
  Clock,
  User,
  Plus,
  Search,
  History,
  Thermometer,
  Eye,
  ArrowRight,
  ChevronDown,
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import ClinicalTimeline, {
  type TimelineEvent,
  type TimelineStatus,
} from '@/components/ClinicalTimeline';
import SedationAssessmentCard from '@/components/SedationAssessmentCard';
import DrawerBuilder from '@/components/DrawerBuilder';
import {
  type SedationAssessment,
  type SedationAssessmentCreate,
  getRASSLabel,
  getRASSColor,
  getRASSBgColor,
  getBPSNRSCategory,
  PAIN_CATEGORY_LABELS,
  PAIN_CATEGORY_COLORS,
  getCAMICULabel,
  getCAMICUIColor,
  formatSedationTimestamp,
} from '@/lib/sedation-types';
import { fetchSedation, fetchSedationHistory, fetchDashboard } from '@/lib/api';

// ─── Patient option ──────────────────────────────────────────────────────────

interface SedationPatientOption {
  mpiId: string;
  name: string;
  bed: string;
}

// ─── Constants ─────────────────────────────────────────────────────────────

const RASS_RANGE = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4] as const;

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Delta de RASS entre duas avaliações */
function computeRASSDelta(current: number, previous: number): string {
  const delta = current - previous;
  if (delta > 0) return `+${delta}`;
  if (delta < 0) return `${delta}`;
  return '0';
}

/** Cor do delta */
function getDeltaColor(delta: number): string {
  if (delta > 0) return 'var(--clinical-severity-critical-on-surface)'; // mais agitado
  if (delta < 0) return 'var(--clinical-severity-normal-on-surface)'; // mais sedado (ou melhora)
  return 'var(--semantic-text-secondary)';
}

/** Converte SedationAssessment em TimelineEvent */
function toTimelineEvent(a: SedationAssessment): TimelineEvent {
  let status: TimelineStatus = 'completed';
  const rass = a.rass_score;

  // -5 ou -4 ou +3 ou +4 → overdue (alerta)
  if (rass <= -4 || rass >= 3) status = 'overdue';
  // -3 ou +1 ou +2 → in-progress (atenção)
  else if (rass <= -3 || rass >= 1) status = 'in-progress';
  // -2 a 0 → completed (ideal ou próximo)
  else status = 'completed';

  const details: string[] = [];
  if (a.bps_nrs_score !== undefined && a.bps_nrs_score !== null) {
    const cat = getBPSNRSCategory(a.bps_nrs_score, a.bps_nrs_type);
    details.push(`${a.bps_nrs_type ?? 'BPS'}: ${a.bps_nrs_score} — ${PAIN_CATEGORY_LABELS[cat]}`);
  }
  details.push(`CAM-ICU: ${getCAMICULabel(a.cam_icu_positive)}`);

  return {
    id: a.id,
    status,
    label: `RASS ${rass > 0 ? '+' : ''}${rass} — ${getRASSLabel(rass)}`,
    description: details.join(' · ') + (a.notes ? ` — ${a.notes}` : ''),
    timestamp: a.assessed_at,
  };
}

// ─── Skeleton de página ──────────────────────────────────────────────────────

function PageSkeleton(): React.ReactElement {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6 animate-pulse">
        {/* Header */}
        <div className="space-y-1">
          <div className="h-7 w-72 rounded" style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
          <div className="h-4 w-96 rounded" style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
        </div>
        {/* Patient selector */}
        <div className="h-10 w-64 rounded" style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
        {/* Card */}
        <div className="h-80 rounded-xl" style={{ backgroundColor: 'var(--semantic-surface-overlay)' }} />
      </div>
    </Layout>
  );
}

// ─── Error de página ─────────────────────────────────────────────────────────

function PageError({ message }: { message: string }): React.ReactElement {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div
          role="alert"
          aria-live="assertive"
          className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm border"
          style={{
            backgroundColor: 'var(--feedback-error-bg-dark)',
            color: 'var(--feedback-error-text-dark)',
            borderColor: 'var(--feedback-error-border-dark)',
          }}
        >
          <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
          <span>{message}</span>
        </div>
      </div>
    </Layout>
  );
}

// ─── Mini Card de Histórico ──────────────────────────────────────────────────

interface MiniHistoryCardProps {
  assessment: SedationAssessment;
  previousRASS?: number;
}

function MiniHistoryCard({ assessment, previousRASS }: MiniHistoryCardProps): React.ReactElement {
  const deltaNum = previousRASS !== undefined
    ? assessment.rass_score - previousRASS
    : 0;

  return (
    <div
      className="flex items-center gap-3 px-3 py-2 rounded-lg border text-sm"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      {/* RASS score */}
      <span
        className="text-lg font-bold tabular-nums min-w-[2.5rem] text-center"
        style={{ color: getRASSColor(assessment.rass_score) }}
        aria-label={`RASS ${assessment.rass_score > 0 ? '+' : ''}${assessment.rass_score}`}
      >
        {assessment.rass_score > 0 ? '+' : ''}
        {assessment.rass_score}
      </span>

      {/* Data */}
      <span className="flex-1 min-w-0 truncate" style={{ color: 'var(--semantic-text-secondary)' }}>
        {formatSedationTimestamp(assessment.assessed_at)}
      </span>

      {/* Delta */}
      {previousRASS !== undefined && deltaNum !== 0 && (
        <span
          className="text-xs font-semibold tabular-nums"
          style={{ color: getDeltaColor(deltaNum) }}
          aria-label={`Variação RASS: ${deltaNum > 0 ? '+' : ''}${deltaNum}`}
        >
          {deltaNum > 0 ? '+' : ''}
          {deltaNum}
        </span>
      )}

      <ArrowRight className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
    </div>
  );
}

// ─── Form de Nova Avaliação ──────────────────────────────────────────────────

interface NewAssessmentFormProps {
  selectedPatient: SedationPatientOption;
  onSave: (data: SedationAssessmentCreate) => void;
  onCancel: () => void;
}

function NewAssessmentForm({
  selectedPatient,
  onSave,
  onCancel,
}: NewAssessmentFormProps): React.ReactElement {
  const [rassScore, setRassScore] = useState<number>(0);
  const [painType, setPainType] = useState<'BPS' | 'NRS' | 'none'>('none');
  const [bpsNrsScore, setBpsNrsScore] = useState<number | undefined>(undefined);
  const [camIcu, setCamIcu] = useState<'yes' | 'no' | 'not_assessed'>('not_assessed');
  const [assessedBy, setAssessedBy] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data: SedationAssessmentCreate = {
        mpi_id: selectedPatient.mpiId,
        rass_score: rassScore,
        bps_nrs_score: painType !== 'none' ? bpsNrsScore : undefined,
        bps_nrs_type: painType !== 'none' ? painType : undefined,
        cam_icu_positive: camIcu === 'yes' ? true : camIcu === 'no' ? false : null,
        assessed_by: assessedBy || undefined,
        notes: notes || undefined,
      };
      onSave(data);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* RASS Select */}
      <fieldset>
        <legend className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Brain className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          RASS — Nível de Sedação
        </legend>

        {/* Visual bar + select */}
        <div className="space-y-3">
          {/* Color bar */}
          <div className="flex h-4 rounded-full overflow-hidden" aria-hidden="true">
            {RASS_RANGE.map((val) => (
              <div
                key={val}
                className="flex-1"
                style={{
                  backgroundColor: getRASSColor(val),
                  opacity: val === rassScore ? 1 : 0.4,
                }}
              />
            ))}
          </div>

          {/* Slider-like select */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1">
            {RASS_RANGE.map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => setRassScore(val)}
                className={`flex-shrink-0 min-w-[3rem] py-2 px-1 rounded-lg text-center text-xs font-semibold transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                  val === rassScore ? 'ring-2 shadow-md scale-110' : ''
                }`}
                style={{
                  backgroundColor: val === rassScore ? getRASSColor(val) : 'transparent',
                  color: val === rassScore ? 'white' : getRASSColor(val),
                  borderColor: val === rassScore ? getRASSColor(val) : 'var(--semantic-border-default)',
                  borderWidth: '1px',
                }}
                aria-pressed={val === rassScore}
                aria-label={`RASS ${val > 0 ? '+' : ''}${val}: ${getRASSLabel(val)}`}
                title={getRASSLabel(val)}
              >
                <div>{val > 0 ? '+' : ''}{val}</div>
              </button>
            ))}
          </div>

          {/* Dynamic label */}
          <div
            className="text-center py-2 rounded-lg text-sm font-medium"
            style={{
              backgroundColor: getRASSBgColor(rassScore),
              color: getRASSColor(rassScore),
            }}
          >
            RASS {rassScore > 0 ? '+' : ''}{rassScore}: {getRASSLabel(rassScore)}
          </div>
        </div>
      </fieldset>

      {/* BPS/NRS */}
      <fieldset>
        <legend className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Thermometer className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          Avaliação de Dor
        </legend>

        {/* Radio toggle for scale type */}
        <div className="flex gap-2 mb-3">
          {(['none', 'BPS', 'NRS'] as const).map((opt) => (
            <label
              key={opt}
              className="flex-1"
            >
              <input
                type="radio"
                name="painType"
                value={opt}
                checked={painType === opt}
                onChange={() => {
                  setPainType(opt);
                  if (opt === 'none') setBpsNrsScore(undefined);
                }}
                className="sr-only"
              />
              <span
                className={`block text-center py-2 rounded-lg text-sm font-medium cursor-pointer border transition-all ${
                  painType === opt ? 'ring-2 ring-offset-1' : ''
                }`}
                style={{
                  backgroundColor: painType === opt
                    ? 'var(--semantic-surface-selected)'
                    : 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                  borderColor: painType === opt
                    ? 'var(--color-primary)'
                    : 'var(--semantic-border-default)',
                }}
              >
                {opt === 'none' ? 'Não avaliar' : opt}
              </span>
            </label>
          ))}
        </div>

        {/* Score input */}
        {painType !== 'none' && (
          <div className="space-y-2">
            <label className="text-xs font-medium" style={{ color: 'var(--semantic-text-secondary)' }}>
              Valor ({painType === 'BPS' ? '3 a 12' : '0 a 10'})
            </label>
            <input
              type="number"
              min={painType === 'BPS' ? 3 : 0}
              max={painType === 'BPS' ? 12 : 10}
              step={1}
              value={bpsNrsScore ?? ''}
              onChange={(e) => setBpsNrsScore(e.target.value ? Number(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded-lg border text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
              }}
              placeholder={painType === 'BPS' ? '3-12' : '0-10'}
            />
          </div>
        )}
      </fieldset>

      {/* CAM-ICU */}
      <fieldset>
        <legend className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Eye className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          CAM-ICU — Delirium
        </legend>
        <div className="flex gap-2">
          {([
            { value: 'no', label: 'Negativo' },
            { value: 'yes', label: 'Positivo' },
            { value: 'not_assessed', label: 'Não avaliado' },
          ] as const).map((opt) => (
            <label key={opt.value} className="flex-1">
              <input
                type="radio"
                name="camIcu"
                value={opt.value}
                checked={camIcu === opt.value}
                onChange={() => setCamIcu(opt.value)}
                className="sr-only"
              />
              <span
                className={`block text-center py-2 rounded-lg text-sm font-medium cursor-pointer border transition-all ${
                  camIcu === opt.value ? 'ring-2 ring-offset-1' : ''
                }`}
                style={{
                  backgroundColor: camIcu === opt.value
                    ? 'var(--semantic-surface-selected)'
                    : 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                  borderColor: camIcu === opt.value
                    ? 'var(--color-primary)'
                    : 'var(--semantic-border-default)',
                }}
              >
                {opt.label}
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      {/* Assessor */}
      <fieldset>
        <label className="text-sm font-semibold flex items-center gap-2 mb-2">
          <User className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          Profissional
        </label>
        <input
          type="text"
          value={assessedBy}
          onChange={(e) => setAssessedBy(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          placeholder="Ex: Dr(a). Ana Costa"
        />
      </fieldset>

      {/* Notas */}
      <fieldset>
        <label className="text-sm font-semibold mb-2 block" style={{ color: 'var(--semantic-text-primary)' }}>
          Notas clínicas
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 rounded-lg border text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none resize-y"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          placeholder="Observações adicionais sobre a avaliação..."
        />
      </fieldset>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 py-2.5 rounded-lg text-sm font-medium border transition-all"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
          disabled={saving}
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="flex-1 py-2.5 rounded-lg text-sm font-medium text-white transition-all flex items-center justify-center gap-2"
          style={{ backgroundColor: 'var(--color-primary)' }}
          disabled={saving}
        >
          {saving ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              Salvando...
            </>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
              Salvar Avaliação
            </>
          )}
        </button>
      </div>
    </form>
  );
}

// ─── Page Component ─────────────────────────────────────────────────────────

export default function SedationPage(): React.ReactElement {
  // State
  const [patients, setPatients] = useState<SedationPatientOption[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentAssessment, setCurrentAssessment] = useState<SedationAssessment | null>(null);
  const [history, setHistory] = useState<SedationAssessment[]>([]);

  const [drawerOpen, setDrawerOpen] = useState(false);

  // ── Fetch patients on mount ──────────────────────────────────────────────
  useEffect(() => {
    fetchDashboard()
      .then((dashboard) => {
        const mapped: SedationPatientOption[] = dashboard.patients.map((p) => ({
          mpiId: p.mpi_id,
          name: p.display_name,
          bed: p.bed_id ?? '—',
        }));
        setPatients(mapped);
        if (mapped.length > 0 && !selectedPatientId) {
          setSelectedPatientId(mapped[0]!.mpiId);
        }
      })
      .catch((err) => {
        setError(err.message || 'Erro ao carregar lista de pacientes');
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Fetch sedation data when selectedPatientId changes ───────────────────
  useEffect(() => {
    if (!selectedPatientId) return;

    setIsLoading(true);
    setError(null);

    Promise.all([
      fetchSedation(selectedPatientId),
      fetchSedationHistory(selectedPatientId),
    ])
      .then(([assessmentData, historyData]) => {
        setCurrentAssessment(assessmentData as SedationAssessment);
        setHistory((historyData as SedationAssessment[]) ?? []);
      })
      .catch((err) => {
        setError(err.message || 'Erro ao carregar dados de sedação');
        setCurrentAssessment(null);
        setHistory([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [selectedPatientId]);

  // Derived
  const selectedPatient = useMemo(
    () => patients.find((p) => p.mpiId === selectedPatientId) ?? null,
    [patients, selectedPatientId],
  );

  const recentHistory = useMemo(() => history.slice(0, 5), [history]);

  const timelineEvents = useMemo<TimelineEvent[]>(
    () => [...history].sort((a, b) =>
      new Date(b.assessed_at).getTime() - new Date(a.assessed_at).getTime()
    ).map(toTimelineEvent),
    [history],
  );

  // Handlers
  const handlePatientChange = useCallback((mpiId: string) => {
    setSelectedPatientId(mpiId);
    setError(null);
  }, []);

  const handleNewAssessment = useCallback((data: SedationAssessmentCreate) => {
    const now = new Date().toISOString();
    const newAssessment: SedationAssessment = {
      id: `sed-${Date.now()}`,
      mpi_id: data.mpi_id,
      rass_score: data.rass_score,
      bps_nrs_score: data.bps_nrs_score,
      bps_nrs_type: data.bps_nrs_type,
      cam_icu_positive: data.cam_icu_positive,
      assessed_at: now,
      assessed_by: data.assessed_by,
      notes: data.notes,
    };

    setCurrentAssessment(newAssessment);
    setHistory((prev) => [newAssessment, ...prev]);
    setDrawerOpen(false);
  }, []);

  // Initial loading state
  if (isLoading && !currentAssessment) {
    return <PageSkeleton />;
  }

  // Error state
  if (error && !currentAssessment && !isLoading) {
    return <PageError message={error} />;
  }

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
          {/* ── Header ─────────────────────────────────────────────────────── */}
          <div>
            <h1
              className="text-2xl font-bold flex items-center gap-2"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <Brain className="w-7 h-7" style={{ color: 'var(--color-primary)' }} aria-hidden="true" />
              Monitoramento de Sedação
            </h1>
            <p className="mt-1 text-sm" style={{ color: 'var(--semantic-text-secondary)' }}>
              RASS, BPS/NRS e CAM-ICU — Avaliação do nível de sedação, dor e delirium
            </p>
          </div>

          {/* ── Patient Selector ────────────────────────────────────────────── */}
          {patients.length > 0 && (
            <div className="flex flex-wrap items-center gap-3">
              <label
                className="text-sm font-semibold flex items-center gap-1"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <Search className="w-4 h-4" aria-hidden="true" />
                Paciente:
              </label>
              <div className="relative">
                <select
                  value={selectedPatientId}
                  onChange={(e) => handlePatientChange(e.target.value)}
                  className="appearance-none pl-3 pr-8 py-2 rounded-lg border text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none cursor-pointer"
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
                <ChevronDown
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  aria-hidden="true"
                />
              </div>
              {selectedPatient && (
                <span
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: 'var(--semantic-surface-overlay)',
                    color: 'var(--semantic-text-secondary)',
                  }}
                >
                  <User className="w-3 h-3" aria-hidden="true" />
                  {selectedPatient.name} · {selectedPatient.bed}
                </span>
              )}
            </div>
          )}

          {/* ── Non-blocking error banner ───────────────────────────────────── */}
          {error && currentAssessment && (
            <div
              role="alert"
              className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm border"
              style={{
                backgroundColor: 'var(--clinical-severity-watch-wash)',
                color: 'var(--clinical-severity-watch-on-surface)',
                borderColor: 'var(--clinical-severity-watch-signal)',
              }}
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              <span>Erro ao atualizar: {error}</span>
            </div>
          )}

          {/* ── Sedation Assessment Card ────────────────────────────────────── */}
          <SedationAssessmentCard
            assessment={currentAssessment ?? undefined}
            isLoading={isLoading}
            error={error}
          />

          {/* ── Mini Histórico ──────────────────────────────────────────────── */}
          {!isLoading && history.length > 0 && (
            <section>
              <h2
                className="text-sm font-semibold uppercase tracking-wide mb-3 flex items-center gap-2"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <History className="w-4 h-4" aria-hidden="true" />
                Últimas Avaliações
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
                {recentHistory.map((a, idx) => {
                  const prevRASS = idx < recentHistory.length - 1
                    ? recentHistory[idx + 1]?.rass_score
                    : undefined;
                  return (
                    <MiniHistoryCard
                      key={a.id}
                      assessment={a}
                      previousRASS={prevRASS}
                    />
                  );
                })}
              </div>
            </section>
          )}

          {/* ── Histórico Completo (Timeline) ───────────────────────────────── */}
          {!isLoading && history.length > 0 && (
            <section>
              <h2
                className="text-sm font-semibold uppercase tracking-wide mb-3 flex items-center gap-2"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <Clock className="w-4 h-4" aria-hidden="true" />
                Histórico Completo de Avaliações
              </h2>
              <div
                className="rounded-xl border p-4"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
              >
                <ClinicalTimeline
                  events={timelineEvents}
                  domain="general"
                  isLoading={isLoading}
                  error={null}
                />
              </div>
            </section>
          )}

          {/* ── Histórico vazio ─────────────────────────────────────────────── */}
          {!isLoading && history.length === 0 && (
            <div
              className="flex flex-col items-center justify-center gap-2 py-10 text-sm rounded-xl border"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-secondary)',
              }}
              role="status"
              aria-label="Nenhum histórico de avaliação"
            >
              <History className="w-10 h-10 opacity-30" aria-hidden="true" />
              <p>Nenhuma avaliação registrada para este paciente</p>
            </div>
          )}

          {/* ── Botão Nova Avaliação ────────────────────────────────────────── */}
          <div className="flex justify-end">
            <button
              onClick={() => setDrawerOpen(true)}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold text-white transition-all shadow-md hover:shadow-lg"
              style={{ backgroundColor: 'var(--color-primary)' }}
            >
              <Plus className="w-5 h-5" aria-hidden="true" />
              Nova Avaliação
            </button>
          </div>

          {/* ── Drawer: Form de Nova Avaliação ──────────────────────────────── */}
          {selectedPatient && (
            <DrawerBuilder
              open={drawerOpen}
              onClose={() => setDrawerOpen(false)}
              title={`Nova Avaliação de Sedação — ${selectedPatient.name}`}
              size="lg"
            >
              <NewAssessmentForm
                selectedPatient={selectedPatient}
                onSave={handleNewAssessment}
                onCancel={() => setDrawerOpen(false)}
              />
            </DrawerBuilder>
          )}
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
