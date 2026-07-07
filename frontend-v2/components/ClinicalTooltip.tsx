'use client';

import React from 'react';
import * as Tooltip from '@radix-ui/react-tooltip';

// ─── Clinical abbreviation definitions (PT-BR) ──────────────────────────────

const CLINICAL_TERMS: Record<string, string> = {
  MEWS: 'Modified Early Warning Score — pontuação de alerta precoce (0-14)',
  NEWS2: 'National Early Warning Score 2 — avaliação de risco clínico (0-20)',
  RASS: 'Richmond Agitation-Sedation Scale — escala de sedação/agitação (-5 a +4)',
  'CAM-ICU': 'Confusion Assessment Method for ICU — avaliação de delirium',
  SOFA: 'Sequential Organ Failure Assessment — avaliação de disfunção orgânica (0-24)',
  qSOFA: 'Quick SOFA — triagem rápida de sepse (0-3)',
  AVPU: 'Alert, Verbal, Pain, Unresponsive — escala de resposta neurológica',
  BPS: 'Behavioral Pain Scale — avaliação de dor (3-12)',
  NRS: 'Numeric Rating Scale — escala numérica de dor (0-10)',
};

interface ClinicalTooltipProps {
  term: string;
  children: React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  sideOffset?: number;
}

/**
 * Wraps children with a tooltip explaining the clinical abbreviation.
 * Tooltip content is in PT-BR with the English abbreviation.
 */
export default function ClinicalTooltip({
  term,
  children,
  side = 'top',
  sideOffset = 4,
}: ClinicalTooltipProps) {
  const description = CLINICAL_TERMS[term];

  if (!description) {
    // If the term is not recognized, just render the children without tooltip
    return <>{children}</>;
  }

  return (
    <Tooltip.Provider delayDuration={200}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <span className="cursor-help border-b border-dotted border-current">
            {children}
          </span>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            side={side}
            sideOffset={sideOffset}
            className="z-50 max-w-xs rounded-lg px-3 py-2 text-xs leading-relaxed shadow-lg"
            style={{
              backgroundColor: 'var(--semantic-text-primary, #1e293b)',
              color: 'var(--semantic-text-primary, #ffffff)',
            }}
          >
            <span className="font-semibold">{term}:</span> {description}
            <Tooltip.Arrow
              style={{ fill: 'var(--semantic-text-primary, #1e293b)' }}
            />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
