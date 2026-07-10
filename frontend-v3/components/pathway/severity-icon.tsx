'use client';

import type { SeverityLevel } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
  CircleCheck,
  CircleX,
  CircleAlert,
  Clock,
  CircleDot,
  type LucideIcon,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Severity → icon + colour mapping (data-driven, no hardcoded conditions)
// ---------------------------------------------------------------------------

interface IconConfig {
  Icon: LucideIcon;
  colorVar: string;
  label: string;
}

function resolveCriteriaIcon(
  met: boolean | null | undefined,
  severity: SeverityLevel | null | undefined,
): IconConfig {
  // Explicit met/not-met takes precedence over severity colour
  if (met === true) {
    return {
      Icon: CircleCheck,
      colorVar: 'var(--severity-normal)',
      label: 'Atendido',
    };
  }

  if (met === false) {
    return {
      Icon: CircleX,
      colorVar: 'var(--severity-critical)',
      label: 'Não atendido',
    };
  }

  // Fallback to severity-based icon
  const sev = severity ?? 'normal';

  switch (sev) {
    case 'critical':
      return {
        Icon: CircleAlert,
        colorVar: 'var(--severity-critical)',
        label: 'Crítico',
      };
    case 'urgent':
      return {
        Icon: CircleAlert,
        colorVar: 'var(--severity-urgent)',
        label: 'Urgente',
      };
    case 'watch':
      return {
        Icon: Clock,
        colorVar: 'var(--severity-watch)',
        label: 'Observação',
      };
    case 'normal':
      return {
        Icon: CircleCheck,
        colorVar: 'var(--severity-normal)',
        label: 'Normal',
      };
    default:
      return {
        Icon: CircleDot,
        colorVar: 'var(--text-secondary)',
        label: 'Pendente',
      };
  }
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface SeverityIconProps {
  /** Whether the criterion has been met (overrides severity colour). */
  met?: boolean | null;
  /** Severity level when `met` is not explicitly set. */
  severity?: SeverityLevel | null;
  /** Additional class names. */
  className?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SeverityIcon({
  met,
  severity,
  className,
}: SeverityIconProps) {
  const { Icon, colorVar, label } = resolveCriteriaIcon(met, severity);
  const isPulse = severity === 'critical' && met !== true;

  return (
    <span
      role="img"
      aria-label={label}
      className={cn(
        'inline-flex shrink-0 items-center justify-center',
        isPulse && 'severity-critical-pulse rounded-full',
        className,
      )}
      style={{ color: colorVar }}
    >
      <Icon className="h-5 w-5" aria-hidden="true" />
    </span>
  );
}
