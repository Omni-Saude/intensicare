'use client';

import type { SeverityLevel } from '@/lib/api';

const SEVERITY_GLOW_MAP: Record<SeverityLevel, string> = {
  normal: '',
  watch: 'shadow-[0_0_6px_1px_var(--severity-watch-wash)]',
  urgent: 'shadow-[0_0_8px_2px_var(--severity-urgent-wash)]',
  critical: 'shadow-[0_0_10px_3px_var(--severity-critical-wash)] severity-critical-pulse',
};

const SEVERITY_BORDER_MAP: Record<SeverityLevel, string> = {
  normal: 'border-l-[var(--severity-normal)]',
  watch: 'border-l-[var(--severity-watch)]',
  urgent: 'border-l-[var(--severity-urgent)]',
  critical: 'border-l-[var(--severity-critical)]',
};

export function severityGlow(severity: SeverityLevel): string {
  return SEVERITY_GLOW_MAP[severity] ?? '';
}

export function severityBorder(severity: SeverityLevel): string {
  return SEVERITY_BORDER_MAP[severity] ?? '';
}

export function severityColor(severity: SeverityLevel): string {
  switch (severity) {
    case 'normal':
      return 'var(--severity-normal)';
    case 'watch':
      return 'var(--severity-watch)';
    case 'urgent':
      return 'var(--severity-urgent)';
    case 'critical':
      return 'var(--severity-critical)';
    default:
      return 'var(--text-secondary)';
  }
}

export function severityWash(severity: SeverityLevel): string {
  switch (severity) {
    case 'normal':
      return 'var(--severity-normal-wash)';
    case 'watch':
      return 'var(--severity-watch-wash)';
    case 'urgent':
      return 'var(--severity-urgent-wash)';
    case 'critical':
      return 'var(--severity-critical-wash)';
    default:
      return 'var(--bg-tertiary)';
  }
}

export function severityRing(severity: SeverityLevel): string {
  switch (severity) {
    case 'normal':
      return 'var(--severity-normal-ring)';
    case 'watch':
      return 'var(--severity-watch-ring)';
    case 'urgent':
      return 'var(--severity-urgent-ring)';
    case 'critical':
      return 'var(--severity-critical-ring)';
    default:
      return 'var(--border-tertiary)';
  }
}
