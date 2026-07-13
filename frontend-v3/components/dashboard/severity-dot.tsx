'use client';

import type { SeverityLevel } from '@/lib/api';
import { cn } from '@/lib/utils';

const SEVERITY_VAR: Record<SeverityLevel, string> = {
  normal: 'var(--severity-normal)',
  watch: 'var(--severity-watch)',
  urgent: 'var(--severity-urgent)',
  critical: 'var(--severity-critical)',
};

const SEVERITY_LABEL: Record<SeverityLevel, string> = {
  normal: 'Normal',
  watch: 'Observação',
  urgent: 'Urgente',
  critical: 'Crítico',
};

// RF-018 — WCAG 1.4.1 Use of Color: severity was communicated by
// `backgroundColor` alone (plus a pulse reserved for `critical`), so a
// colorblind sighted user had no way to tell `watch` apart from `urgent`
// short of hue. Each level now escalates a non-chromatic cue too, so the
// 4 levels stay distinguishable in grayscale/protanopia simulation:
//   normal  -> plain dot (baseline)
//   watch   -> dot + static ring (halo appears)
//   urgent  -> dot + ring + larger dot (halo grows)
//   critical -> dot + pulse animation (motion; already existed)
// Ring colors reuse the `--severity-*-ring` tokens (translucent
// color-mix) added for RF-001/state-label — no new hardcoded values.
const SEVERITY_RING: Partial<Record<SeverityLevel, string>> = {
  watch: '0 0 0 2px var(--severity-watch-ring)',
  urgent: '0 0 0 2px var(--severity-urgent-ring)',
};

const SEVERITY_SIZE: Record<SeverityLevel, string> = {
  normal: 'size-2.5',
  watch: 'size-2.5',
  urgent: 'size-3',
  critical: 'size-3',
};

interface SeverityDotProps {
  // Defensive: accepts null/undefined even though the domain type is
  // non-nullable, since the backend has been observed sending an absent
  // severity (audit Dim B/D). Falls back to 'normal' rather than
  // rendering an undefined color / "Severidade null" label.
  severity: SeverityLevel | null | undefined;
}

export function SeverityDot({ severity }: SeverityDotProps) {
  const sev = severity ?? 'normal';
  const isCritical = sev === 'critical';

  return (
    <span
      role="status"
      aria-label={`Severidade ${SEVERITY_LABEL[sev]}`}
      className={cn(
        'inline-block shrink-0 rounded-full',
        SEVERITY_SIZE[sev],
        isCritical && 'severity-critical-pulse',
      )}
      style={{
        backgroundColor: SEVERITY_VAR[sev],
        boxShadow: SEVERITY_RING[sev],
      }}
    />
  );
}
