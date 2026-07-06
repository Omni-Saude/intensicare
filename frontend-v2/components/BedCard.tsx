import type { PatientBedSummary } from '../types';

interface BedCardProps {
  patient: PatientBedSummary;
  onClick: (mpiId: string) => void;
}

function TrendIcon({ trend }: { trend: string | null }) {
  if (!trend) return <span style={{ color: 'var(--semantic-text-secondary)' }}>→</span>;
  if (trend === 'increasing') return <span className="font-bold" style={{ color: 'var(--clinical-severity-critical-on-surface)' }}>↑</span>;
  if (trend === 'decreasing') return <span className="font-bold" style={{ color: 'var(--clinical-severity-normal-on-surface)' }}>↓</span>;
  return <span style={{ color: 'var(--semantic-text-secondary)' }}>→</span>;
}

function AlertBadge({ severity }: { severity: string | null }) {
  if (!severity) return <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--clinical-severity-normal-signal)' }} />;
  if (severity === 'critical')
    return <span className="inline-block w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: 'var(--clinical-severity-critical-signal)' }} />;
  if (severity === 'warning')
    return <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--clinical-severity-watch-signal)' }} />;
  return <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--clinical-severity-urgent-signal)' }} />;
}

function ScoreValue({ score, risk, label }: { score: number | null; risk: string | null; label: string }) {
  if (score === null || score === undefined)
    return <span className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>--</span>;

  let colorVar = 'var(--semantic-text-primary)';
  let fontWeight = '';
  if (label === 'MEWS') {
    if (score >= 5) { colorVar = 'var(--clinical-severity-critical-on-surface)'; fontWeight = 'font-bold'; }
    else if (score >= 3) { colorVar = 'var(--clinical-severity-watch-on-surface)'; fontWeight = 'font-semibold'; }
  } else {
    if (risk === 'high') { colorVar = 'var(--clinical-severity-critical-on-surface)'; fontWeight = 'font-bold'; }
    else if (risk === 'medium') { colorVar = 'var(--clinical-severity-watch-on-surface)'; fontWeight = 'font-semibold'; }
  }

  return (
    <span className={`text-sm ${fontWeight}`} style={{ color: colorVar }}>
      {score}
      {risk && risk !== 'low' && (
        <span className="text-xs ml-1 opacity-70">({risk})</span>
      )}
    </span>
  );
}

export default function BedCard({ patient, onClick }: BedCardProps) {
  const hasAlerts = patient.active_alerts_count > 0;

  const cardStyle: React.CSSProperties = {};
  let borderClass = 'border-gray-200';

  if (patient.highest_alert_severity === 'critical') {
    cardStyle.backgroundColor = 'var(--clinical-severity-critical-wash)';
    cardStyle.borderColor = 'var(--clinical-severity-critical-signal)';
    borderClass = '';
  } else if (hasAlerts) {
    cardStyle.backgroundColor = 'var(--clinical-severity-watch-wash)';
    cardStyle.borderColor = 'var(--clinical-severity-watch-signal)';
    borderClass = '';
  }

  return (
    <button
      onClick={() => onClick(patient.mpi_id)}
      style={cardStyle}
      className={`w-full text-left bg-white rounded-lg border-2 p-4 hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-blue-500 ${borderClass}`}
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <div className="flex items-center gap-2">
            <AlertBadge severity={patient.highest_alert_severity} />
            <span className="font-semibold text-slate-800 text-sm">
              {patient.display_name}
            </span>
          </div>
          <div className="text-xs text-slate-500 mt-0.5">
            {patient.bed_id ? `Bed ${patient.bed_id}` : 'No bed'}
            {patient.unit && ` · ${patient.unit}`}
          </div>
        </div>
        {patient.active_alerts_count > 0 && (
          <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: 'var(--clinical-severity-critical-fill)', color: 'var(--clinical-severity-critical-on-fill)' }}>
            {patient.active_alerts_count}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-slate-500">MEWS</span>
          <div className="flex items-center gap-1">
            <ScoreValue score={patient.latest_mews} risk={null} label="MEWS" />
            <TrendIcon trend={patient.mews_trend} />
          </div>
        </div>
        <div>
          <span className="text-slate-500">NEWS2</span>
          <div className="flex items-center gap-1">
            <ScoreValue score={patient.latest_news2} risk={patient.news2_risk} label="NEWS2" />
            <TrendIcon trend={patient.news2_trend} />
          </div>
        </div>
      </div>
    </button>
  );
}
