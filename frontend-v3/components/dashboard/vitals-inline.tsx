'use client';

interface VitalsData {
  hr?: number;
  spo2?: number;
  bp_sys?: number;
  bp_dia?: number;
}

interface VitalsInlineProps {
  vitals?: VitalsData;
}

export function VitalsInline({ vitals }: VitalsInlineProps) {
  if (!vitals) return null;

  const parts: string[] = [];

  if (vitals.hr != null) parts.push(`HR ${vitals.hr}`);
  if (vitals.spo2 != null) parts.push(`SpO₂ ${vitals.spo2}%`);

  const hasSystolic = vitals.bp_sys != null;
  const hasDiastolic = vitals.bp_dia != null;
  if (hasSystolic || hasDiastolic) {
    const sys = hasSystolic ? String(vitals.bp_sys) : '--';
    const dia = hasDiastolic ? String(vitals.bp_dia) : '--';
    parts.push(`BP ${sys}/${dia}`);
  }

  if (parts.length === 0) return null;

  return (
    <div
      className="text-xs leading-tight truncate"
      style={{ color: 'var(--text-secondary)' }}
      aria-label={`Sinais vitais: ${parts.join(', ')}`}
    >
      {parts.join(' • ')}
    </div>
  );
}
