'use client';

import React from 'react';
import {
  AlertTriangle,
  Eye,
  CheckCircle,
  AlertOctagon,
  Info,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import ClinicalTooltip from '@/components/ClinicalTooltip';

type Severity = 'normal' | 'watch' | 'urgent' | 'critical' | 'info';

interface SeverityBadgeProps {
  severity: Severity;
  className?: string;
  showLabel?: boolean;
}

interface SeverityStyleConfig {
  fillBg: string;
  fillText: string;
  borderColor: string;
  washBg: string;
  shapeStyle: React.CSSProperties;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  pulse?: boolean;
  isCritical?: boolean;
}

/**
 * Canonical spec per:
 * - docs/plan/_work/platform/severity-model.yaml (encoding.icon + encoding.shape)
 * - docs/plan/design/design-tokens.md §6 (CSS custom properties)
 */
const severityConfig: Record<Severity, SeverityStyleConfig> = {
  normal: {
    fillBg: 'var(--clinical-severity-normal-fill)',
    fillText: 'var(--clinical-severity-normal-on-fill)',
    borderColor: 'var(--clinical-severity-normal-signal)',
    washBg: 'var(--clinical-severity-normal-wash)',
    shapeStyle: { borderRadius: '9999px' }, // circle
    icon: CheckCircle, // spec: check-circle ✅
    label: 'Normal',
  },
  watch: {
    fillBg: 'var(--clinical-severity-watch-fill)',
    fillText: 'var(--clinical-severity-watch-on-fill)',
    borderColor: 'var(--clinical-severity-watch-signal)',
    washBg: 'var(--clinical-severity-watch-wash)',
    shapeStyle: { borderRadius: '6px' }, // rounded-square ✅ (not rounded-full)
    icon: Eye, // spec: eye ✅ (not AlertCircle)
    label: 'Watch',
  },
  urgent: {
    fillBg: 'var(--clinical-severity-urgent-fill)',
    fillText: 'var(--clinical-severity-urgent-on-fill)',
    borderColor: 'var(--clinical-severity-urgent-signal)',
    washBg: 'var(--clinical-severity-urgent-wash)',
    // Triangle — NOT rounded-lg ✅
    shapeStyle: { clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' },
    icon: AlertTriangle, // spec: exclamation (AlertTriangle) ✅
    label: 'Urgent',
  },
  critical: {
    fillBg: 'var(--clinical-severity-critical-fill)',
    fillText: 'var(--clinical-severity-critical-on-fill)',
    borderColor: 'var(--clinical-severity-critical-signal)',
    washBg: 'var(--clinical-severity-critical-wash)',
    // Octagon — NOT rounded-lg ✅
    shapeStyle: {
      clipPath:
        'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
    },
    icon: AlertOctagon, // spec: alert-octagon ✅ (not ShieldAlert)
    label: 'Critical',
    pulse: true,
    isCritical: true,
  },
  info: {
    // INFO maps to 'normal' band per severity-model.yaml §6.4
    fillBg: 'var(--clinical-severity-normal-fill)',
    fillText: 'var(--clinical-severity-normal-on-fill)',
    borderColor: 'var(--clinical-severity-normal-signal)',
    washBg: 'var(--clinical-severity-normal-wash)',
    shapeStyle: { borderRadius: '9999px' },
    icon: Info,
    label: 'Info',
  },
};

export default function SeverityBadge({
  severity,
  className = '',
  showLabel = true,
}: SeverityBadgeProps) {
  const config = severityConfig[severity] || severityConfig.info;
  const Icon = config.icon;

  // Triangle shape needs extra top padding to fit content below the point
  const isTriangle = severity === 'urgent';
  const isOctagon = severity === 'critical';

  // Common inline styles using CSS custom properties (replaces hardcoded Tailwind colors)
  const badgeStyle: React.CSSProperties = {
    backgroundColor: config.fillBg,
    color: config.fillText,
    borderColor: config.borderColor,
    ...config.shapeStyle,
  };

  // Accessibility attributes
  const a11yAttrs: Record<string, string> = {
    'aria-label': `Severity: ${config.label}`,
  };
  if (config.isCritical) {
    a11yAttrs['role'] = 'alert';
    a11yAttrs['aria-live'] = 'assertive';
  }

  return (
    <span
      style={badgeStyle}
      className={`inline-flex items-center gap-1.5 border text-xs font-semibold ${className} ${
        config.pulse ? 'animate-pulse-critical' : ''
      } ${
        isTriangle
          ? 'px-3 pt-3.5 pb-1.5'
          : isOctagon
          ? 'px-3 py-1.5'
          : 'px-2.5 py-1'
      }`}
      {...a11yAttrs}
      title={`Severity: ${config.label}`}
    >
      <Icon className="w-3.5 h-3.5 flex-shrink-0" />
      {showLabel && <span>{config.label}</span>}
    </span>
  );
}

// ─── Trend indicator ─────────────────────────────────────────────────────────

interface TrendBadgeProps {
  trend: string | null;
  className?: string;
}

export function TrendBadge({ trend, className = '' }: TrendBadgeProps) {
  if (!trend) {
    return (
      <span
        className={`inline-flex items-center ${className}`}
        style={{ color: 'var(--semantic-text-secondary)' }}
        aria-label="Trend: stable"
      >
        <Minus className="w-3.5 h-3.5" />
      </span>
    );
  }

  if (trend === 'increasing') {
    return (
      <span
        className={`inline-flex items-center gap-0.5 font-bold ${className}`}
        style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
        aria-label="Trend: increasing"
      >
        <TrendingUp className="w-3.5 h-3.5" />
        <span className="text-[10px]">↑</span>
      </span>
    );
  }

  if (trend === 'decreasing') {
    return (
      <span
        className={`inline-flex items-center gap-0.5 font-bold ${className}`}
        style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
        aria-label="Trend: decreasing"
      >
        <TrendingDown className="w-3.5 h-3.5" />
        <span className="text-[10px]">↓</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center ${className}`}
      style={{ color: 'var(--semantic-text-secondary)' }}
      aria-label="Trend: stable"
    >
      <Minus className="w-3.5 h-3.5" />
    </span>
  );
}

// ─── Score display ────────────────────────────────────────────────────────────

interface ScoreDisplayProps {
  label: string;
  score: number | null;
  risk?: string | null;
  trend?: string | null;
  className?: string;
}

export function ScoreDisplay({
  label,
  score,
  risk,
  trend,
  className = '',
}: ScoreDisplayProps) {
  if (score === null || score === undefined) {
    return (
      <div className={`text-center ${className}`}>
        <div
          className="text-xs uppercase font-semibold"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {label}
        </div>
        <div
          className="text-lg"
          style={{ color: 'var(--semantic-text-secondary)', opacity: 0.5 }}
        >
          --
        </div>
      </div>
    );
  }

  let colorVar = 'var(--semantic-text-primary)';
  if (label === 'MEWS') {
    if (score >= 5)
      colorVar = 'var(--clinical-severity-critical-on-surface)';
    else if (score >= 3)
      colorVar = 'var(--clinical-severity-watch-on-surface)';
  } else {
    if (risk === 'high') colorVar = 'var(--clinical-severity-critical-on-surface)';
    else if (risk === 'medium')
      colorVar = 'var(--clinical-severity-watch-on-surface)';
  }

  const isBold =
    (label === 'MEWS' && score >= 5) ||
    (label !== 'MEWS' && risk === 'high');

  return (
    <div className={`text-center ${className}`}>
      <div
        className="text-xs uppercase font-semibold"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {label}
      </div>
      <div className="flex items-center justify-center gap-1">
        <span
          className={`text-lg ${isBold ? 'font-bold' : 'font-semibold'}`}
          style={{ color: colorVar }}
        >
          {score}
        </span>
        {trend && <TrendBadge trend={trend} />}
      </div>
      {risk && risk !== 'low' && (
        <div
          className="text-[10px] uppercase font-semibold"
          style={{ color: colorVar }}
        >
          {risk}
        </div>
      )}
    </div>
  );
}
