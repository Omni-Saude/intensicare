'use client';

import React, {
  useEffect,
  useState,
  useCallback,
  useMemo,
  useRef,
} from 'react';
import {
  Activity,
  AlertTriangle,
  Clock,
  RefreshCw,
  Search,
  Wifi,
  WifiOff,
  ChevronRight,
  Heart,
  Users,
  Bed,
  Stethoscope,
  Timer,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import CriteriaChecklist, {
  type Criterion,
} from '@/components/CriteriaChecklist';
import ClinicalTimeline, {
  type TimelineEvent,
  type TimelineStatus,
} from '@/components/ClinicalTimeline';
import AlertCard from '@/components/AlertCard';
import SeverityBadge, { ScoreDisplay, TrendBadge } from '@/components/SeverityBadge';
import DrawerBuilder from '@/components/DrawerBuilder';
import ErrorBoundary from '@/components/ErrorBoundary';
import {
  fetchAlerts,
  fetchPatientDetail,
  type AlertInfo,
  type PatientDetailResponse,
  type VitalsHistoryPoint,
} from '@/lib/api';
import {
  useRealtimeChannel,
  useConnectionStatus,
} from '@/lib/websocket';

// ─── Types ──────────────────────────────────────────────────────────────────

type SeverityRank = 'critical' | 'urgent' | 'watch' | 'normal';

interface SepsisPatientEntry {
  mpiId: string;
  highestSeverity: SeverityRank;
  alertCount: number;
  latestAlert: AlertInfo;
  displayName?: string;
  bedId?: string;
  unit?: string;
}

interface BundleTimerState {
  status: 'running' | 'warning' | 'overdue' | 'completed';
  minutesRemaining: number;
  totalMinutes: number;
  elapsedMinutes: number;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const SEVERITY_RANK: Record<SeverityRank, number> = {
  critical: 4,
  urgent: 3,
  watch: 2,
  normal: 1,
};

const BUNDLE_DEADLINE_MINUTES = 60;
const BUNDLE_WARNING_MINUTES = 30;

const UNIT_OPTIONS = ['', 'ICU-1', 'ICU-2', 'ER', 'General Ward'];

function toSeverityRank(severity: string | null | undefined): SeverityRank {
  if (!severity) return 'normal';
  const s = severity.toLowerCase();
  if (s === 'critical') return 'critical';
  if (s === 'urgent' || s === 'warning') return 'urgent';
  if (s === 'watch') return 'watch';
  return 'normal';
}

function mapToSeverityBadge(severity: string | null): 'normal' | 'watch' | 'urgent' | 'critical' {
  if (!severity) return 'normal';
  const s = severity.toLowerCase();
  if (s === 'critical') return 'critical';
  if (s === 'urgent' || s === 'warning') return 'urgent';
  if (s === 'watch') return 'watch';
  return 'normal';
}

// ─── Helper: derive qSOFA from latest vitals ────────────────────────────────

function deriveQsofa(vitals: VitalsHistoryPoint | null | undefined): {
  score: number;
  components: { label: string; met: boolean; value?: string }[];
} {
  if (!vitals) {
    return { score: 0, components: [] };
  }

  const components: { label: string; met: boolean; value?: string }[] = [];

  // Respiratory rate ≥ 22
  const rrMet = vitals.respiratory_rate !== null && vitals.respiratory_rate >= 22;
  components.push({
    label: 'FR ≥ 22 irpm',
    met: rrMet,
    value: vitals.respiratory_rate !== null ? `${vitals.respiratory_rate}` : undefined,
  });

  // Altered mental status (AVPU not "A")
  const avpuMet = vitals.avpu !== null && vitals.avpu !== 'A';
  components.push({
    label: 'AVPU ≠ Alerta',
    met: avpuMet,
    value: vitals.avpu ?? undefined,
  });

  // Systolic BP ≤ 100
  const sbpMet = vitals.systolic_bp !== null && vitals.systolic_bp <= 100;
  components.push({
    label: 'PAS ≤ 100 mmHg',
    met: sbpMet,
    value: vitals.systolic_bp !== null ? `${vitals.systolic_bp}` : undefined,
  });

  const score = components.filter((c) => c.met).length;
  return { score, components };
}

// ─── Helper: build sepsis criteria checklist ────────────────────────────────

function buildSepsisCriteria(
  detail: PatientDetailResponse,
): Criterion[] {
  const latestVitals =
    detail.vitals_history.length > 0
      ? detail.vitals_history[detail.vitals_history.length - 1]
      : null;

  const criteria: Criterion[] = [];

  // Major criteria
  // qSOFA ≥ 2
  const qsofa = deriveQsofa(latestVitals);
  criteria.push({
    id: 'major-qsofa',
    label: 'qSOFA ≥ 2 (triagem positiva)',
    description: 'Quick SOFA: FR ≥ 22, PAS ≤ 100, ou alteração neurológica (AVPU < A)',
    category: 'major',
    met: qsofa.score >= 2,
  });

  // Lactate > 2 (derived from latest NEWS2/M EWS — we don't have lactate directly, infer from scores)
  // We look at the latest MEWS or NEWS2 trend as proxy
  const latestMews =
    detail.mews_history.length > 0
      ? detail.mews_history[detail.mews_history.length - 1]
      : null;
  const latestNews2 =
    detail.news2_history.length > 0
      ? detail.news2_history[detail.news2_history.length - 1]
      : null;

  // Lactate proxy: MEWS ≥ 4 or NEWS2 ≥ 5 suggests possible lactate elevation
  const lactateElevated =
    (latestMews && latestMews.score_value >= 4) ||
    (latestNews2 && latestNews2.score_value >= 5);
  criteria.push({
    id: 'major-lactate',
    label: 'Lactato > 2 mmol/L (estimado)',
    description: 'Estimado por escores de alerta precoce elevados (MEWS ≥ 4 ou NEWS2 ≥ 5)',
    category: 'major',
    met: !!lactateElevated,
  });

  // Hypotension
  const hypotensive =
    latestVitals &&
    latestVitals.systolic_bp !== null &&
    latestVitals.systolic_bp < 90;
  criteria.push({
    id: 'major-hypotension',
    label: 'Hipotensão (PAS < 90 mmHg)',
    category: 'major',
    met: !!hypotensive,
    value: latestVitals?.systolic_bp !== null ? `${latestVitals?.systolic_bp}` : undefined,
    threshold: '90',
  });

  // Minor criteria
  // Tachycardia
  const tachycardic =
    latestVitals &&
    latestVitals.heart_rate !== null &&
    latestVitals.heart_rate > 90;
  criteria.push({
    id: 'minor-tachycardia',
    label: 'Taquicardia (FC > 90 bpm)',
    category: 'minor',
    met: !!tachycardic,
    value: latestVitals?.heart_rate !== null ? `${latestVitals?.heart_rate}` : undefined,
    threshold: '90',
  });

  // Tachypnea
  const tachypneic =
    latestVitals &&
    latestVitals.respiratory_rate !== null &&
    latestVitals.respiratory_rate > 20;
  criteria.push({
    id: 'minor-tachypnea',
    label: 'Taquipneia (FR > 20 irpm)',
    category: 'minor',
    met: !!tachypneic,
    value: latestVitals?.respiratory_rate !== null ? `${latestVitals?.respiratory_rate}` : undefined,
    threshold: '20',
  });

  // Fever or hypothermia
  const tempAbnormal =
    latestVitals &&
    latestVitals.temperature !== null &&
    (latestVitals.temperature > 38.0 || latestVitals.temperature < 36.0);
  criteria.push({
    id: 'minor-temperature',
    label: 'Temperatura alterada (> 38°C ou < 36°C)',
    category: 'minor',
    met: !!tempAbnormal,
    value: latestVitals?.temperature != null ? `${latestVitals?.temperature?.toFixed(1)}` : undefined,
    threshold: '36–38',
  });

  // SpO2 low
  const spo2Low =
    latestVitals &&
    latestVitals.spo2 !== null &&
    latestVitals.spo2 < 92;
  criteria.push({
    id: 'minor-spo2',
    label: 'SpO₂ < 92%',
    category: 'minor',
    met: !!spo2Low,
    value: latestVitals?.spo2 != null ? `${latestVitals?.spo2}` : undefined,
    threshold: '92',
  });

  return criteria;
}

// ─── Helper: build clinical timeline from patient history ───────────────────

function buildTimeline(detail: PatientDetailResponse): TimelineEvent[] {
  const events: TimelineEvent[] = [];

  // Add vitals history as timeline events
  const recentVitals = detail.vitals_history.slice(-8);
  for (const v of recentVitals) {
    const recordedAt = v.recorded_at;
    const changes: string[] = [];
    if (v.heart_rate !== null) changes.push(`FC: ${v.heart_rate} bpm`);
    if (v.systolic_bp !== null && v.diastolic_bp !== null) {
      changes.push(`PA: ${v.systolic_bp}/${v.diastolic_bp}`);
    }
    if (v.spo2 !== null) changes.push(`SpO₂: ${v.spo2}%`);
    if (v.temperature !== null) changes.push(`Temp: ${v.temperature.toFixed(1)}°C`);
    if (v.respiratory_rate !== null) changes.push(`FR: ${v.respiratory_rate}`);

    events.push({
      id: `vitals-${v.recorded_at}`,
      status: 'completed' as TimelineStatus,
      label: 'Sinais Vitais',
      description: changes.join(' · '),
      timestamp: recordedAt,
    });
  }

  // Add score history events
  const allScores = [
    ...detail.mews_history.map((s) => ({ ...s, prefix: 'MEWS' })),
    ...detail.news2_history.map((s) => ({ ...s, prefix: 'NEWS2' })),
  ].sort(
    (a, b) =>
      new Date(a.calculated_at).getTime() - new Date(b.calculated_at).getTime(),
  );

  for (const s of allScores.slice(-8)) {
    let status: TimelineStatus = 'completed';
    const scoreVal = s.score_value;
    if (s.prefix === 'MEWS') {
      if (scoreVal >= 5) status = 'overdue';
      else if (scoreVal >= 3) status = 'in-progress';
    } else {
      if (scoreVal >= 7) status = 'overdue';
      else if (scoreVal >= 5) status = 'in-progress';
    }

    const trendLabel =
      s.trend === 'increasing'
        ? ' ↑'
        : s.trend === 'decreasing'
        ? ' ↓'
        : '';

    events.push({
      id: `score-${s.prefix}-${s.calculated_at}`,
      status,
      label: `${s.prefix} = ${scoreVal}${trendLabel}`,
      description:
        s.trend === 'increasing'
          ? 'Tendência de piora'
          : s.trend === 'decreasing'
          ? 'Tendência de melhora'
          : 'Estável',
      timestamp: s.calculated_at,
    });
  }

  // Add alert events from active_alerts
  for (const alert of detail.active_alerts.slice(0, 5)) {
    const alertStatus: TimelineStatus =
      alert.status === 'resolved'
        ? 'completed'
        : alert.status === 'acknowledged'
        ? 'in-progress'
        : 'overdue';

    events.push({
      id: `alert-${alert.id}`,
      status: alertStatus,
      label: alert.title,
      description: alert.body || undefined,
      timestamp: alert.created_at,
    });
  }

  // Sort by timestamp descending (newest first)
  events.sort(
    (a, b) =>
      new Date(b.timestamp || 0).getTime() -
      new Date(a.timestamp || 0).getTime(),
  );

  return events.slice(0, 15);
}

// ─── Helper: compute bundle timer ────────────────────────────────────────────

function computeBundleTimer(alerts: AlertInfo[]): BundleTimerState | null {
  const activeAlerts = alerts.filter(
    (a) => a.status === 'active' || a.status === 'escalated',
  );
  if (activeAlerts.length === 0) return null;

  // Find the earliest active alert
  const earliest = activeAlerts.reduce((earliest, a) =>
    new Date(a.created_at).getTime() < new Date(earliest.created_at).getTime()
      ? a
      : earliest,
  );

  const createdAt = new Date(earliest.created_at).getTime();
  const deadline = createdAt + BUNDLE_DEADLINE_MINUTES * 60 * 1000;
  const now = Date.now();
  const elapsedMs = Math.max(0, now - createdAt);
  const elapsedMinutes = Math.floor(elapsedMs / 60000);
  const remainingMs = Math.max(0, deadline - now);
  const minutesRemaining = Math.floor(remainingMs / 60000);

  let status: BundleTimerState['status'];
  if (now > deadline) {
    status = 'overdue';
  } else if (minutesRemaining <= BUNDLE_WARNING_MINUTES) {
    status = 'warning';
  } else {
    status = 'running';
  }

  return {
    status,
    minutesRemaining,
    totalMinutes: BUNDLE_DEADLINE_MINUTES,
    elapsedMinutes,
  };
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function SepseDashboardPage() {
  // ── State ──────────────────────────────────────────────────────────────────
  const [alerts, setAlerts] = useState<AlertInfo[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [alertsError, setAlertsError] = useState<string | null>(null);

  const [selectedMpiId, setSelectedMpiId] = useState<string | null>(null);
  const [patientDetail, setPatientDetail] =
    useState<PatientDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const [unitFilter, setUnitFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Mobile drawer for detail
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // WebSocket connection status
  const wsStatus = useConnectionStatus();

  // Patient display names cache (populated when detail loads)
  const [patientNames, setPatientNames] = useState<Record<string, string>>({});
  const [patientBeds, setPatientBeds] = useState<Record<string, string>>({});
  const [patientUnits, setPatientUnits] = useState<Record<string, string>>({});

  // ── Data fetching: alerts ──────────────────────────────────────────────────
  const loadAlerts = useCallback(async () => {
    setAlertsLoading(true);
    setAlertsError(null);
    try {
      const result = await fetchAlerts({ status: 'active', limit: 100 });
      // Filter for sepsis-related alerts by title/content
      const sepsisAlerts = result.alerts.filter(
        (a) =>
          a.title.toLowerCase().includes('sepse') ||
          a.title.toLowerCase().includes('sepsis') ||
          a.title.toLowerCase().includes('qsofa') ||
          a.title.toLowerCase().includes('sofa') ||
          (a.body && a.body.toLowerCase().includes('sepse')),
      );
      setAlerts(sepsisAlerts);
    } catch (err: unknown) {
      setAlertsError(
        err instanceof Error ? err.message : 'Falha ao carregar alertas',
      );
    } finally {
      setAlertsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // ── WebSocket: live updates ────────────────────────────────────────────────
  useRealtimeChannel(
    'alert.updated',
    useCallback(() => {
      loadAlerts();
      // Also refresh patient detail if one is selected
      if (selectedMpiId) {
        loadPatientDetail(selectedMpiId);
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loadAlerts, selectedMpiId]),
  );

  useRealtimeChannel(
    'alert.raised',
    useCallback(() => {
      loadAlerts();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loadAlerts]),
  );

  // ── Data fetching: patient detail ──────────────────────────────────────────
  const loadPatientDetail = useCallback(async (mpiId: string) => {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const detail = await fetchPatientDetail(mpiId);
      setPatientDetail(detail);
      // Update display name cache
      setPatientNames((prev) => ({
        ...prev,
        [mpiId]: detail.display_name,
      }));
      setPatientBeds((prev) => ({
        ...prev,
        [mpiId]: detail.bed_id || '',
      }));
      setPatientUnits((prev) => ({
        ...prev,
        [mpiId]: detail.unit || '',
      }));
    } catch (err: unknown) {
      setDetailError(
        err instanceof Error ? err.message : 'Falha ao carregar detalhes',
      );
    } finally {
      setDetailLoading(false);
    }
  }, []);

  // ── Patient selection ──────────────────────────────────────────────────────
  const handleSelectPatient = useCallback(
    (mpiId: string) => {
      setSelectedMpiId(mpiId);
      loadPatientDetail(mpiId);
      // On mobile, open the detail drawer
      if (typeof window !== 'undefined' && window.innerWidth < 768) {
        setMobileDrawerOpen(true);
      }
    },
    [loadPatientDetail],
  );

  const handleDeselectPatient = useCallback(() => {
    setSelectedMpiId(null);
    setPatientDetail(null);
    setDetailError(null);
    setMobileDrawerOpen(false);
  }, []);

  // ── Build patient list from alerts ────────────────────────────────────────
  const patients = useMemo<SepsisPatientEntry[]>(() => {
    const map = new Map<string, SepsisPatientEntry>();

    for (const alert of alerts) {
      const existing = map.get(alert.mpi_id);
      const severity = toSeverityRank(alert.severity);

      if (!existing) {
        map.set(alert.mpi_id, {
          mpiId: alert.mpi_id,
          highestSeverity: severity,
          alertCount: 1,
          latestAlert: alert,
          displayName: patientNames[alert.mpi_id],
          bedId: patientBeds[alert.mpi_id],
          unit: patientUnits[alert.mpi_id],
        });
      } else {
        existing.alertCount++;
        if (SEVERITY_RANK[severity] > SEVERITY_RANK[existing.highestSeverity]) {
          existing.highestSeverity = severity;
          existing.latestAlert = alert;
        }
        // Update display name if available
        if (!existing.displayName && patientNames[alert.mpi_id]) {
          existing.displayName = patientNames[alert.mpi_id];
        }
        if (!existing.bedId && patientBeds[alert.mpi_id]) {
          existing.bedId = patientBeds[alert.mpi_id];
        }
        if (!existing.unit && patientUnits[alert.mpi_id]) {
          existing.unit = patientUnits[alert.mpi_id];
        }
      }
    }

    // Sort by severity (critical first), then by alert count
    const list = Array.from(map.values());
    list.sort((a, b) => {
      const rankDiff =
        SEVERITY_RANK[b.highestSeverity] - SEVERITY_RANK[a.highestSeverity];
      if (rankDiff !== 0) return rankDiff;
      return b.alertCount - a.alertCount;
    });

    return list;
  }, [alerts, patientNames, patientBeds, patientUnits]);

  // ── Filter patients ────────────────────────────────────────────────────────
  const filteredPatients = useMemo(() => {
    let result = patients;

    // Unit filter
    if (unitFilter) {
      result = result.filter((p) => p.unit === unitFilter);
    }

    // Search filter
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (p) =>
          p.mpiId.toLowerCase().includes(q) ||
          (p.displayName && p.displayName.toLowerCase().includes(q)) ||
          (p.bedId && p.bedId.toLowerCase().includes(q)),
      );
    }

    return result;
  }, [patients, unitFilter, searchQuery]);

  // ── Derived: criteria, timeline, bundle timer ──────────────────────────────
  const criteria = useMemo<Criterion[]>(() => {
    if (!patientDetail) return [];
    return buildSepsisCriteria(patientDetail);
  }, [patientDetail]);

  const timelineEvents = useMemo<TimelineEvent[]>(() => {
    if (!patientDetail) return [];
    return buildTimeline(patientDetail);
  }, [patientDetail]);

  const bundleTimer = useMemo<BundleTimerState | null>(() => {
    if (!patientDetail) return null;
    return computeBundleTimer(patientDetail.active_alerts);
  }, [patientDetail]);

  // ── Latest vitals / scores ─────────────────────────────────────────────────
  const latestVitals = useMemo(() => {
    if (!patientDetail || patientDetail.vitals_history.length === 0) return null;
    return patientDetail.vitals_history[
      patientDetail.vitals_history.length - 1
    ];
  }, [patientDetail]);

  const latestMews = useMemo(() => {
    if (!patientDetail || patientDetail.mews_history.length === 0) return null;
    return patientDetail.mews_history[
      patientDetail.mews_history.length - 1
    ];
  }, [patientDetail]);

  const latestNews2 = useMemo(() => {
    if (!patientDetail || patientDetail.news2_history.length === 0) return null;
    return patientDetail.news2_history[
      patientDetail.news2_history.length - 1
    ];
  }, [patientDetail]);

  const qsofaData = useMemo(() => deriveQsofa(latestVitals), [latestVitals]);

  // ── Bundle timer display ───────────────────────────────────────────────────
  const bundleTimerDisplay = useMemo(() => {
    if (!bundleTimer) return null;

    const { status, minutesRemaining, elapsedMinutes } = bundleTimer;

    let bgVar: string;
    let textVar: string;
    let label: string;

    switch (status) {
      case 'running':
        bgVar = 'var(--clinical-sepsis-confirmed-fill)';
        textVar = 'var(--clinical-sepsis-confirmed-on-surface)';
        label = `${minutesRemaining} min restantes`;
        break;
      case 'warning':
        bgVar = 'var(--clinical-sepsis-suspected-fill)';
        textVar = 'var(--clinical-sepsis-suspected-on-surface)';
        label = `Atenção: ${minutesRemaining} min restantes`;
        break;
      case 'overdue':
        bgVar = 'var(--clinical-sepsis-bundle-overdue-fill)';
        textVar = 'var(--clinical-sepsis-bundle-overdue-on-surface)';
        label = `ATRASADO: +${elapsedMinutes - BUNDLE_DEADLINE_MINUTES} min`;
        break;
      case 'completed':
        bgVar = 'var(--clinical-sepsis-confirmed-fill)';
        textVar = 'var(--clinical-sepsis-confirmed-on-surface)';
        label = 'Bundle concluído';
        break;
      default:
        bgVar = 'var(--semantic-surface-overlay)';
        textVar = 'var(--semantic-text-secondary)';
        label = '';
    }

    return { bgVar, textVar, label, status };
  }, [bundleTimer]);

  // ─── Helper: severity color for patient list items ─────────────────────────
  function getSeverityColor(severity: SeverityRank): {
    dot: string;
    border: string;
    bg: string;
  } {
    switch (severity) {
      case 'critical':
        return {
          dot: 'var(--clinical-severity-critical-signal)',
          border: 'var(--clinical-severity-critical-signal)',
          bg: 'var(--clinical-severity-critical-wash)',
        };
      case 'urgent':
        return {
          dot: 'var(--clinical-severity-urgent-signal)',
          border: 'var(--clinical-severity-urgent-signal)',
          bg: 'var(--clinical-severity-urgent-wash)',
        };
      case 'watch':
        return {
          dot: 'var(--clinical-severity-watch-signal)',
          border: 'var(--clinical-severity-watch-signal)',
          bg: 'var(--clinical-severity-watch-wash)',
        };
      default:
        return {
          dot: 'var(--clinical-severity-normal-signal)',
          border: 'var(--semantic-border-default)',
          bg: 'var(--semantic-surface-raised)',
        };
    }
  }

  // ─── Render: patient detail panel ──────────────────────────────────────────
  const renderDetailPanel = () => {
    // No patient selected
    if (!selectedMpiId) {
      return (
        <div
          className="flex flex-col items-center justify-center h-full py-16 px-6"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          <Stethoscope
            className="w-16 h-16 mb-4 opacity-20"
            aria-hidden="true"
          />
          <p className="text-lg font-medium">Selecione um paciente</p>
          <p className="text-sm mt-2 text-center">
            Escolha um paciente da lista à esquerda para visualizar os detalhes
            clínicos de sepse.
          </p>
        </div>
      );
    }

    // Loading detail
    if (detailLoading) {
      return (
        <div
          className="animate-pulse space-y-4 p-4"
          role="status"
          aria-label="Carregando detalhes do paciente"
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div className="space-y-2 flex-1">
              <div
                className="h-5 rounded w-40"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div
                className="h-3 rounded w-24"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="h-16 rounded-lg"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            ))}
          </div>
          <div className="space-y-3">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-10 rounded-lg"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            ))}
          </div>
        </div>
      );
    }

    // Error
    if (detailError) {
      return (
        <div
          role="alert"
          aria-live="assertive"
          className="flex flex-col items-center justify-center p-6"
          style={{
            backgroundColor: 'var(--feedback-error-bg-dark)',
            color: 'var(--feedback-error-text-dark)',
            borderColor: 'var(--feedback-error-border-dark)',
            borderWidth: '1px',
            borderRadius: '0.75rem',
          }}
        >
          <AlertTriangle className="w-10 h-10 mb-3" aria-hidden="true" />
          <p className="font-semibold text-sm">Erro ao carregar detalhes</p>
          <p className="text-xs mt-1">{detailError}</p>
          <button
            onClick={() => loadPatientDetail(selectedMpiId)}
            className="mt-3 px-4 py-2 rounded-lg text-sm font-medium underline hover:no-underline"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              color: 'var(--semantic-text-primary)',
            }}
          >
            Tentar novamente
          </button>
        </div>
      );
    }

    // Detail content
    if (!patientDetail) return null;

    return (
      <div className="space-y-4 p-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 12rem)' }}>
        {/* Patient header */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h2
              className="text-xl font-bold truncate"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              {patientDetail.display_name}
            </h2>
            <p
              className="text-sm"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {patientDetail.bed_id && (
                <span className="inline-flex items-center gap-1 mr-3">
                  <Bed className="w-3.5 h-3.5" aria-hidden="true" />{' '}
                  {patientDetail.bed_id}
                </span>
              )}
              {patientDetail.unit && (
                <span>{patientDetail.unit}</span>
              )}
            </p>
          </div>
          {alerts.find((a) => a.mpi_id === selectedMpiId) && (
            <SeverityBadge
              severity={mapToSeverityBadge(
                alerts.find((a) => a.mpi_id === selectedMpiId)!.severity,
              )}
              showLabel
            />
          )}
        </div>

        {/* Scores row */}
        <div
          className="grid grid-cols-3 gap-3 p-3 rounded-xl"
          style={{
            backgroundColor: 'var(--semantic-surface-canvas)',
            borderColor: 'var(--semantic-border-default)',
            borderWidth: '1px',
          }}
        >
          <div className="text-center">
            <div
              className="text-xs uppercase font-semibold mb-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              qSOFA
            </div>
            <div className="flex items-center justify-center gap-1">
              <span
                className={`text-xl ${qsofaData.score >= 2 ? 'font-bold' : 'font-semibold'}`}
                style={{
                  color:
                    qsofaData.score >= 2
                      ? 'var(--clinical-severity-critical-on-surface)'
                      : 'var(--semantic-text-primary)',
                }}
              >
                {qsofaData.score}
              </span>
              {qsofaData.score >= 2 && (
                <TrendingUp
                  className="w-4 h-4"
                  style={{
                    color: 'var(--clinical-severity-critical-signal)',
                  }}
                  aria-hidden="true"
                />
              )}
            </div>
          </div>
          <ScoreDisplay
            label="MEWS"
            score={latestMews?.score_value ?? null}
            trend={latestMews?.trend ?? null}
          />
          <ScoreDisplay
            label="NEWS2"
            score={latestNews2?.score_value ?? null}
            risk={
              latestNews2
                ? latestNews2.score_value >= 7
                  ? 'high'
                  : latestNews2.score_value >= 5
                  ? 'medium'
                  : 'low'
                : null
            }
            trend={latestNews2?.trend ?? null}
          />
        </div>

        {/* Bundle timer */}
        {bundleTimerDisplay && (
          <div
            className="flex items-center gap-3 px-4 py-3 rounded-xl"
            style={{
              backgroundColor: bundleTimerDisplay.bgVar,
              color: bundleTimerDisplay.textVar,
              borderColor:
                bundleTimerDisplay.status === 'overdue'
                  ? 'var(--clinical-sepsis-bundle-overdue-signal)'
                  : 'transparent',
              borderWidth: bundleTimerDisplay.status === 'overdue' ? '2px' : '0px',
            }}
            role={bundleTimerDisplay.status === 'overdue' ? 'alert' : 'status'}
            aria-live={bundleTimerDisplay.status === 'overdue' ? 'assertive' : 'polite'}
          >
            <Timer
              className={`w-5 h-5 flex-shrink-0 ${
                bundleTimerDisplay.status === 'overdue' ? 'animate-pulse' : ''
              }`}
              aria-hidden="true"
            />
            <div>
              <p className="text-sm font-semibold">Bundle Hour-1</p>
              <p className="text-xs opacity-90">
                {bundleTimerDisplay.label}
              </p>
            </div>
          </div>
        )}

        {/* Criteria checklist */}
        <div
          className="rounded-xl border p-3"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
        >
          <h3
            className="text-sm font-semibold mb-2 flex items-center gap-2"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            <Activity className="w-4 h-4" aria-hidden="true" />
            Critérios de Sepse
          </h3>
          <CriteriaChecklist
            items={criteria}
            domain="sepsis"
            readOnly
            isLoading={detailLoading}
            error={null}
          />
        </div>

        {/* Clinical timeline */}
        <div
          className="rounded-xl border p-3"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
        >
          <h3
            className="text-sm font-semibold mb-2 flex items-center gap-2"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            <Clock className="w-4 h-4" aria-hidden="true" />
            Linha do Tempo Clínica
          </h3>
          <ClinicalTimeline
            events={timelineEvents}
            domain="sepsis"
            isLoading={detailLoading}
            error={null}
          />
        </div>

        {/* Active alerts */}
        {patientDetail.active_alerts.length > 0 && (
          <div>
            <h3
              className="text-sm font-semibold mb-2 flex items-center gap-2"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <AlertTriangle className="w-4 h-4" aria-hidden="true" />
              Alertas Ativos ({patientDetail.active_alerts.length})
            </h3>
            <div className="space-y-3">
              {patientDetail.active_alerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onUpdate={() => {
                    loadAlerts();
                    loadPatientDetail(selectedMpiId!);
                  }}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // ─── Render: main ──────────────────────────────────────────────────────────
  return (
    <ErrorBoundary>
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 px-1">
        <div>
          <h1
            className="text-2xl font-bold flex items-center gap-2"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            <Activity className="w-6 h-6" aria-hidden="true" />
            Monitoramento de Sepse
          </h1>
          <p
            className="text-sm mt-1 flex items-center gap-2"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            {!alertsLoading && (
              <span>
                {filteredPatients.length} paciente
                {filteredPatients.length !== 1 ? 's' : ''} com alerta ativo
              </span>
            )}
            <span className="inline-flex items-center gap-1">
              {wsStatus === 'connected' ? (
                <Wifi
                  className="w-3 h-3"
                  style={{ color: 'var(--clinical-severity-normal-signal)' }}
                  aria-hidden="true"
                />
              ) : (
                <WifiOff
                  className="w-3 h-3"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  aria-hidden="true"
                />
              )}
              <span className="text-[10px]">
                {wsStatus === 'connected'
                  ? 'Ao vivo'
                  : wsStatus === 'connecting'
                  ? '...'
                  : 'Offline'}
              </span>
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Unit filter */}
          <select
            value={unitFilter}
            onChange={(e) => setUnitFilter(e.target.value)}
            aria-label="Filtrar por unidade"
            className="px-3 py-2 rounded-lg text-sm border bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <option value="">Todas as Unidades</option>
            {UNIT_OPTIONS.filter(Boolean).map((unit) => (
              <option key={unit} value={unit}>
                {unit}
              </option>
            ))}
          </select>
          <button
            onClick={loadAlerts}
            disabled={alertsLoading}
            aria-label="Atualizar alertas"
            className="p-2 rounded-lg border hover:opacity-80 disabled:opacity-50 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <RefreshCw
              className={`w-4 h-4 ${alertsLoading ? 'animate-spin' : ''}`}
              style={{ color: 'var(--semantic-text-secondary)' }}
              aria-hidden="true"
            />
          </button>
        </div>
      </div>

      {/* ── Split panel ──────────────────────────────────────────────────── */}
      <div className="flex flex-1 gap-4 min-h-0">
        {/* Left: Patient list (desktop always visible, mobile hidden when drawer open) */}
        <div
          className={`${
            mobileDrawerOpen ? 'hidden' : ''
          } md:block w-full md:w-80 lg:w-96 flex-shrink-0 overflow-y-auto rounded-xl border`}
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-canvas)',
          }}
          role="region"
          aria-label="Lista de pacientes com alerta de sepse"
        >
          {/* Search */}
          <div className="p-3 border-b sticky top-0 z-10" style={{ borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-canvas)' }}>
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar paciente ou leito..."
                aria-label="Buscar paciente"
                className="w-full pl-9 pr-3 py-2 bg-white border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                }}
              />
            </div>
          </div>

          {/* Loading state */}
          {alertsLoading && (
            <div className="space-y-2 p-3" role="status" aria-label="Carregando alertas">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 rounded-lg animate-pulse"
                  style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                >
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                  />
                  <div className="flex-1 space-y-1.5">
                    <div
                      className="h-4 rounded w-24"
                      style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                    />
                    <div
                      className="h-3 rounded w-16"
                      style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                    />
                  </div>
                  <div
                    className="h-5 rounded-full w-8"
                    style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {alertsError && !alertsLoading && (
            <div
              role="alert"
              aria-live="assertive"
              className="flex flex-col items-center p-6 m-3 rounded-xl"
              style={{
                backgroundColor: 'var(--feedback-error-bg-dark)',
                color: 'var(--feedback-error-text-dark)',
                borderColor: 'var(--feedback-error-border-dark)',
                borderWidth: '1px',
              }}
            >
              <AlertTriangle className="w-8 h-8 mb-2" aria-hidden="true" />
              <p className="font-medium text-sm">Erro ao carregar alertas</p>
              <p className="text-xs mt-1">{alertsError}</p>
              <button
                onClick={loadAlerts}
                className="mt-3 px-4 py-2 rounded-lg text-sm font-medium underline hover:no-underline"
                style={{
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
              >
                Tentar novamente
              </button>
            </div>
          )}

          {/* Empty state */}
          {!alertsLoading && !alertsError && filteredPatients.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 px-4">
              <Stethoscope
                className="w-12 h-12 mb-4 opacity-20"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <p
                className="font-medium text-center"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Nenhum paciente com alerta de sepse ativo
              </p>
              <p
                className="text-sm mt-1 text-center"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {searchQuery || unitFilter
                  ? 'Tente ajustar os filtros de busca.'
                  : 'Nenhum alerta de sepse ativo no momento.'}
              </p>
            </div>
          )}

          {/* Patient list */}
          {!alertsLoading &&
            !alertsError &&
            filteredPatients.length > 0 && (
              <div className="p-2" role="list" aria-label="Pacientes com sepse">
                {filteredPatients.map((patient) => {
                  const isSelected = selectedMpiId === patient.mpiId;
                  const colors = getSeverityColor(patient.highestSeverity);
                  const isCritical = patient.highestSeverity === 'critical';

                  return (
                    <button
                      key={patient.mpiId}
                      onClick={() => handleSelectPatient(patient.mpiId)}
                      role="listitem"
                      aria-label={`Paciente ${patient.displayName || patient.mpiId}${
                        patient.bedId ? `, ${patient.bedId}` : ''
                      } — ${patient.highestSeverity}`}
                      aria-current={isSelected ? 'true' : undefined}
                      className={`w-full text-left flex items-center gap-3 p-3 rounded-lg mb-1 transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                        isSelected ? 'ring-2 ring-blue-500' : ''
                      }`}
                      style={{
                        backgroundColor: isSelected
                          ? 'var(--semantic-surface-overlay)'
                          : colors.bg,
                        borderLeft: `3px solid ${colors.border}`,
                      }}
                    >
                      {/* Severity dot */}
                      <span
                        className={`w-3 h-3 rounded-full flex-shrink-0 ${
                          isCritical ? 'animate-pulse' : ''
                        }`}
                        style={{ backgroundColor: colors.dot }}
                        aria-hidden="true"
                      />

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div
                          className="font-semibold text-sm truncate"
                          style={{ color: 'var(--semantic-text-primary)' }}
                        >
                          {patient.displayName || patient.mpiId}
                        </div>
                        <div
                          className="text-xs truncate"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          {patient.bedId && (
                            <span className="inline-flex items-center gap-1">
                              <Bed className="w-3 h-3" aria-hidden="true" />{' '}
                              {patient.bedId}
                            </span>
                          )}
                          {!patient.bedId && 'Sem leito'}
                        </div>
                      </div>

                      {/* Alert count + chevron */}
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {patient.alertCount > 1 && (
                          <span
                            className="text-xs font-bold px-1.5 py-0.5 rounded-full"
                            style={{
                              backgroundColor: 'var(--clinical-severity-critical-fill)',
                              color: 'var(--clinical-severity-critical-on-fill)',
                            }}
                          >
                            {patient.alertCount}
                          </span>
                        )}
                        <ChevronRight
                          className="w-4 h-4"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                          aria-hidden="true"
                        />
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
        </div>

        {/* Right: Patient detail (desktop) */}
        <div
          className="hidden md:block flex-1 overflow-hidden rounded-xl border"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
          role="region"
          aria-label="Detalhes do paciente"
        >
          {renderDetailPanel()}
        </div>
      </div>

      {/* Mobile: detail drawer */}
      <DrawerBuilder
        open={mobileDrawerOpen}
        onClose={() => {
          setMobileDrawerOpen(false);
          handleDeselectPatient();
        }}
        title={
          patientDetail
            ? patientDetail.display_name
            : 'Detalhes do Paciente'
        }
        size="full"
      >
        <div className="pt-4">{renderDetailPanel()}</div>
      </DrawerBuilder>
    </div>
    </ErrorBoundary>
  );
}
