import React from 'react';

export type Severity = 'normal' | 'watch' | 'urgent' | 'critical' | 'info';

/**
 * Returns inline CSS properties for a patient card border/background
 * based on an alert severity string.
 */
export function getSeverityStyle(
  severity: string | null,
  variant: 'card' | 'left-accent' = 'card',
): React.CSSProperties {
  const isLeftAccent = variant === 'left-accent';

  if (severity === null || severity === undefined) {
    return isLeftAccent
      ? { borderLeftColor: 'var(--clinical-severity-normal-signal)', borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' }
      : { borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' };
  }

  switch (severity) {
    case 'critical':
      return isLeftAccent
        ? { borderLeftColor: 'var(--clinical-severity-critical-signal)', borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--clinical-severity-critical-wash)' }
        : { borderColor: 'var(--clinical-severity-critical-signal)', backgroundColor: 'var(--clinical-severity-critical-wash)' };
    case 'warning':
      return isLeftAccent
        ? { borderLeftColor: 'var(--clinical-severity-watch-signal)', borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--clinical-severity-watch-wash)' }
        : { borderColor: 'var(--clinical-severity-watch-signal)', backgroundColor: 'var(--clinical-severity-watch-wash)' };
    default:
      return isLeftAccent
        ? { borderLeftColor: 'var(--clinical-severity-normal-signal)', borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' }
        : { borderColor: 'var(--clinical-severity-urgent-signal)', backgroundColor: 'var(--clinical-severity-urgent-wash)' };
  }
}

/**
 * Maps an alert severity string to a canonical Severity value.
 */
export function getSeverityFromAlert(severity: string | null): Severity {
  if (severity === null || severity === undefined) return 'normal';
  switch (severity) {
    case 'critical': return 'critical';
    case 'warning': return 'watch';
    case 'info': return 'info';
    default: return 'normal';
  }
}

/**
 * Returns MEWS severity styling info for a given score.
 */
export function getMEWSSeverity(score: number | null): { colorVar: string; severity: Severity } {
  if (score === null || score === undefined) {
    return { colorVar: 'var(--semantic-text-primary)', severity: 'normal' };
  }
  if (score >= 5) {
    return { colorVar: 'var(--clinical-severity-critical-on-surface)', severity: 'critical' };
  }
  if (score >= 3) {
    return { colorVar: 'var(--clinical-severity-watch-on-surface)', severity: 'watch' };
  }
  return { colorVar: 'var(--semantic-text-primary)', severity: 'normal' };
}

/**
 * Returns NEWS2 severity styling info for a given score.
 */
export function getNEWS2Severity(score: number | null): { colorVar: string; severity: Severity } {
  if (score === null || score === undefined) {
    return { colorVar: 'var(--semantic-text-primary)', severity: 'normal' };
  }
  if (score >= 7) {
    return { colorVar: 'var(--clinical-severity-critical-on-surface)', severity: 'critical' };
  }
  if (score >= 5) {
    return { colorVar: 'var(--clinical-severity-watch-on-surface)', severity: 'watch' };
  }
  return { colorVar: 'var(--semantic-text-primary)', severity: 'normal' };
}

/**
 * Returns a CSS color variable string for a score by type.
 * Used for coloring score values in lists and timelines.
 */
export function getScoreColor(type: 'mews' | 'news2' | 'sofa', value: number): string {
  if (type === 'mews') {
    if (value >= 5) return 'var(--clinical-severity-critical-on-surface)';
    if (value >= 3) return 'var(--clinical-severity-watch-on-surface)';
    return 'var(--clinical-severity-normal-on-surface)';
  }
  if (type === 'news2') {
    if (value >= 7) return 'var(--clinical-severity-critical-on-surface)';
    if (value >= 5) return 'var(--clinical-severity-watch-on-surface)';
    return 'var(--clinical-severity-normal-on-surface)';
  }
  if (type === 'sofa') {
    if (value >= 13) return 'var(--clinical-severity-critical-on-surface)';
    if (value >= 10) return 'var(--clinical-severity-urgent-on-surface)';
    if (value >= 7) return 'var(--clinical-severity-watch-on-surface)';
    return 'var(--clinical-severity-normal-on-surface)';
  }
  return 'var(--semantic-text-secondary)';
}
