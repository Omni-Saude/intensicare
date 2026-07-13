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
// Clinical tooltip text — built from the icon's own state (met/severity),
// never hardcoded to a specific patient or criterion instance.
// ---------------------------------------------------------------------------

const SEVERITY_MEANINGS: Record<SeverityLevel, string> = {
  critical: 'faixa crítica — requer ação imediata',
  urgent: 'fora da faixa aceitável — requer atenção prioritária',
  watch: 'tendência de alerta — monitorar de perto',
  normal: 'dentro da faixa esperada',
};

function criteriaTooltip(
  criterionName: string | undefined,
  met: boolean | null | undefined,
  severity: SeverityLevel | null | undefined,
  label: string,
): string {
  const meaning =
    met === true
      ? 'critério clínico cumprido conforme protocolo da trilha'
      : met === false
        ? 'critério clínico não cumprido — requer avaliação'
        : SEVERITY_MEANINGS[severity ?? 'normal'];

  return criterionName ? `${criterionName} — ${label}: ${meaning}` : `${label}: ${meaning}`;
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface SeverityIconProps {
  /** Whether the criterion has been met (overrides severity colour). */
  met?: boolean | null;
  /** Severity level when `met` is not explicitly set. */
  severity?: SeverityLevel | null;
  /** Criterion name, used to build a more specific clinical tooltip. */
  criterionName?: string;
  /** Additional class names. */
  className?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SeverityIcon({
  met,
  severity,
  criterionName,
  className,
}: SeverityIconProps) {
  const { Icon, colorVar, label } = resolveCriteriaIcon(met, severity);
  const isPulse = severity === 'critical' && met !== true;
  const title = criteriaTooltip(criterionName, met, severity, label);

  return (
    <span
      role="img"
      aria-label={label}
      title={title}
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
