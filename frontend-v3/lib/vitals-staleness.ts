// Shared staleness formatting for vitals timestamps.
//
// BUG-F3-01: the patient detail page renders vitals served by the backend's
// "N most recent" fallback (used when the 24h window is empty) with only an
// HH:MM time, indistinguishable from live data. This module centralizes the
// age calculation + labeling so the dashboard bed card and the patient
// detail vitals panel agree on thresholds and wording.

export type StalenessTier = 'fresh' | 'watch' | 'stale';

export interface Staleness {
  /** Age of the reading in whole minutes. Never negative (clock skew clamped by caller returning null). */
  diffMin: number;
  tier: StalenessTier;
  /** Severity color token matching the tier (design tokens in app/globals.css). */
  color: string;
  /** Wash/background color token matching the tier. */
  washColor: string;
  /** Compact relative label, e.g. "há 12 min" / "há 2.3h". Used in tight spaces (bed card). */
  shortLabel: string;
  /** Absolute date+time + relative age, e.g. "Dados de 26/06 11:00 — há 17 dias". Used for prominent warnings. */
  longLabel: string;
}

const WATCH_THRESHOLD_MIN = 30;
const STALE_THRESHOLD_MIN = 60;

function formatRelative(diffMin: number): string {
  if (diffMin < 60) return `há ${diffMin} min`;
  const diffHours = diffMin / 60;
  if (diffHours < 24) return `há ${diffHours.toFixed(1)}h`;
  const diffDays = Math.floor(diffHours / 24);
  return `há ${diffDays} dia${diffDays === 1 ? '' : 's'}`;
}

function formatAbsolute(iso: string): string {
  const d = new Date(iso);
  const date = d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  const time = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  return `${date} ${time}`;
}

/** Computes the staleness of a single measurement. Returns null for missing/invalid/future timestamps. */
export function computeStaleness(measuredAt: string, now: number = Date.now()): Staleness | null {
  const measuredMs = new Date(measuredAt).getTime();
  if (Number.isNaN(measuredMs)) return null;

  const diffMs = now - measuredMs;
  const diffMin = Math.floor(diffMs / 60_000);
  if (diffMin < 0) return null;

  let tier: StalenessTier;
  let color: string;
  let washColor: string;
  if (diffMin < WATCH_THRESHOLD_MIN) {
    tier = 'fresh';
    color = 'var(--severity-normal)';
    washColor = 'var(--severity-normal-wash)';
  } else if (diffMin < STALE_THRESHOLD_MIN) {
    tier = 'watch';
    color = 'var(--severity-watch)';
    washColor = 'var(--severity-watch-wash)';
  } else {
    tier = 'stale';
    color = 'var(--severity-critical)';
    washColor = 'var(--severity-critical-wash)';
  }

  return {
    diffMin,
    tier,
    color,
    washColor,
    shortLabel: formatRelative(diffMin),
    longLabel: `Dados de ${formatAbsolute(measuredAt)} — ${formatRelative(diffMin)}`,
  };
}

/** True when `iso` falls on the same calendar day as `now` (local time). */
export function isSameDay(iso: string, now: number = Date.now()): boolean {
  const d = new Date(iso);
  const n = new Date(now);
  return (
    d.getFullYear() === n.getFullYear() &&
    d.getMonth() === n.getMonth() &&
    d.getDate() === n.getDate()
  );
}
