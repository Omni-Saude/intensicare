'use client';

import { useEffect, useState, useRef } from 'react';
import type { ThresholdSeverity, VitalThreshold, ScoreBand } from './types';

// ── Hardcoded medical literature defaults ──────────────────────────────

const DEFAULT_VITAL_THRESHOLDS: VitalThreshold[] = [
  {
    vitalName: 'heart_rate',
    unit: 'bpm',
    lowCritical: 40,
    lowWarn: 50,
    highWarn: 100,
    highCritical: 130,
  },
  {
    vitalName: 'systolic_bp',
    unit: 'mmHg',
    lowCritical: 80,
    lowWarn: 90,
    highWarn: 160,
    highCritical: 180,
  },
  {
    vitalName: 'diastolic_bp',
    unit: 'mmHg',
    lowCritical: 50,
    lowWarn: 60,
    highWarn: 100,
    highCritical: 110,
  },
  {
    vitalName: 'respiratory_rate',
    unit: '/min',
    lowCritical: 8,
    lowWarn: 12,
    highWarn: 25,
    highCritical: 35,
  },
  {
    vitalName: 'spo2',
    unit: '%',
    lowCritical: 88,
    lowWarn: 92,
    highWarn: 100,
    highCritical: 100,
  },
  {
    vitalName: 'temperature',
    unit: '°C',
    lowCritical: 35,
    lowWarn: 36,
    highWarn: 38,
    highCritical: 39,
  },
];

const DEFAULT_SCORE_BANDS: ScoreBand[] = [
  {
    name: 'sofa',
    bands: [
      { min: 0, max: 6, severity: 'normal' as ThresholdSeverity },
      { min: 7, max: 9, severity: 'watch' as ThresholdSeverity },
      { min: 10, max: 12, severity: 'urgent' as ThresholdSeverity },
      { min: 13, max: Number.POSITIVE_INFINITY, severity: 'critical' as ThresholdSeverity },
    ],
  },
];

// ── Module-level cache ─────────────────────────────────────────────────

interface CacheEntry {
  data: { vitals: VitalThreshold[]; scores: ScoreBand[] };
  ts: number;
}

let _cache: CacheEntry | null = null;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

// ── Helper: severity comparison ────────────────────────────────────────

function assessVitalSeverity(
  value: number,
  t: VitalThreshold,
): ThresholdSeverity {
  if (value <= t.lowCritical || value >= t.highCritical) return 'critical';
  if (value <= t.lowWarn || value >= t.highWarn) return 'watch';
  return 'normal';
}

function assessScoreBand(
  value: number,
  band: ScoreBand,
): ThresholdSeverity {
  for (const b of band.bands) {
    if (value >= b.min && value <= b.max) return b.severity;
  }
  return 'normal';
}

// ── CSS variable getters ───────────────────────────────────────────────

export function severityToColorVar(severity: ThresholdSeverity): string {
  switch (severity) {
    case 'critical':
      return 'var(--clinical-severity-critical-on-surface)';
    case 'urgent':
      return 'var(--clinical-severity-urgent-on-surface)';
    case 'watch':
      return 'var(--clinical-severity-watch-on-surface)';
    default:
      return 'var(--semantic-text-primary)';
  }
}

export function severityToWashVar(severity: ThresholdSeverity): string {
  switch (severity) {
    case 'critical':
      return 'var(--clinical-severity-critical-wash)';
    case 'urgent':
      return 'var(--clinical-severity-urgent-wash)';
    case 'watch':
      return 'var(--clinical-severity-watch-wash)';
    default:
      return 'var(--semantic-surface-canvas)';
  }
}

// ── Hook ────────────────────────────────────────────────────────────────

export interface ThresholdAPI {
  /** True while fetching / loading thresholds */
  loading: boolean;
  /** Non-null if the API fetch failed (we fell back to defaults) */
  fallback: boolean;
  /** Assess severity for a numeric vital-sign value */
  getVitalSeverity: (value: number, vitalName: string) => ThresholdSeverity;
  /** Assess severity band for a score (e.g. SOFA) */
  getScoreBand: (value: number, scoreType: string) => ThresholdSeverity;
  /** Direct access to the raw threshold data */
  thresholds: { vitals: VitalThreshold[]; scores: ScoreBand[] };
}

export function useThreshold(): ThresholdAPI {
  const [thresholds, setThresholds] = useState<{
    vitals: VitalThreshold[];
    scores: ScoreBand[];
  }>(_cache?.data ?? { vitals: DEFAULT_VITAL_THRESHOLDS, scores: DEFAULT_SCORE_BANDS });

  const [fallback, setFallback] = useState(false);
  const [loading, setLoading] = useState(!_cache);
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    // Return cached data immediately if still fresh
    if (_cache && Date.now() - _cache.ts < CACHE_TTL_MS) {
      setThresholds(_cache.data);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchRanges = async () => {
      try {
        const res = await fetch('/api/reference-ranges');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        // Expect shape: { vitals: VitalThreshold[], scores: ScoreBand[] }
        const vitals: VitalThreshold[] = Array.isArray(data?.vitals)
          ? data.vitals
          : DEFAULT_VITAL_THRESHOLDS;
        const scores: ScoreBand[] = Array.isArray(data?.scores)
          ? data.scores
          : DEFAULT_SCORE_BANDS;

        const merged = { vitals, scores };
        _cache = { data: merged, ts: Date.now() };

        if (!cancelled) {
          setThresholds(merged);
          setFallback(false);
        }
      } catch {
        console.warn(
          '[useThreshold] API unavailable, using default thresholds',
        );
        const merged = { vitals: DEFAULT_VITAL_THRESHOLDS, scores: DEFAULT_SCORE_BANDS };
        if (!cancelled) {
          setThresholds(merged);
          setFallback(true);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchRanges();

    return () => {
      cancelled = true;
    };
  }, []);

  const api: ThresholdAPI = {
    loading,
    fallback,
    thresholds,
    getVitalSeverity: (value: number, vitalName: string): ThresholdSeverity => {
      const t = thresholds.vitals.find(
        (v) => v.vitalName.toLowerCase() === vitalName.toLowerCase(),
      );
      if (!t) return 'normal';
      return assessVitalSeverity(value, t);
    },
    getScoreBand: (value: number, scoreType: string): ThresholdSeverity => {
      const band = thresholds.scores.find(
        (b) => b.name.toLowerCase() === scoreType.toLowerCase(),
      );
      if (!band) return 'normal';
      return assessScoreBand(value, band);
    },
  };

  return api;
}
