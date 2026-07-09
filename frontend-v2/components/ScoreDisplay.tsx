'use client';

import React from 'react';
import {
  Brain,
  Activity,
  Heart,
  Eye,
  Stethoscope,
  ShieldAlert,
  AlertTriangle,
} from 'lucide-react';
import type { FormType } from '@/lib/clinical-forms-types';
import { getScoreColor, getScoreInterpretation } from '@/lib/clinical-forms-types';

// ─── Props ───────────────────────────────────────────────────────────────────

interface ScoreDisplayProps {
  formType: FormType;
  score: number;
  maxScore: number;
  label: string;
  /** Sub-scores detail for SOFA / Glasgow */
  details?: { label: string; score: number; max: number }[];
}

// ─── Icons ──────────────────────────────────────────────────────────────────

const formIcons: Record<FormType, React.ReactNode> = {
  rass: <Brain className="w-5 h-5" aria-hidden="true" />,
  cam_icu: <Activity className="w-5 h-5" aria-hidden="true" />,
  bps_nrs: <Heart className="w-5 h-5" aria-hidden="true" />,
  glasgow: <Eye className="w-5 h-5" aria-hidden="true" />,
  sofa: <Stethoscope className="w-5 h-5" aria-hidden="true" />,
  lpp: <ShieldAlert className="w-5 h-5" aria-hidden="true" />,
};

// ─── Helper: progress bar gradient ──────────────────────────────────────────

function getProgressColor(formType: FormType, pct: number): string {
  // pct: 0 = best, 1 = worst
  switch (formType) {
    case 'sofa':
      // verde (0) → amarelo (0.3) → laranja (0.55) → vermelho (0.85)
      if (pct >= 0.85) return 'var(--clinical-severity-critical-signal)';
      if (pct >= 0.55) return 'var(--clinical-severity-urgent-signal)';
      if (pct >= 0.30) return 'var(--clinical-severity-watch-signal)';
      return 'var(--clinical-severity-normal-signal)';

    case 'glasgow':
      // Invertido: 15=normal (verde), 3=grave (vermelho)
      if (pct <= 0.33) return 'var(--clinical-severity-critical-signal)'; // grave
      if (pct <= 0.53) return 'var(--clinical-severity-watch-signal)';
      return 'var(--clinical-severity-normal-signal)';

    case 'lpp':
      // Braden invertido: 23=normal (verde), 6=grave (vermelho)
      if (pct <= 0.33) return 'var(--clinical-severity-critical-signal)';
      if (pct <= 0.53) return 'var(--clinical-severity-watch-signal)';
      return 'var(--clinical-severity-normal-signal)';

    case 'rass':
      if (pct >= 0.9) return 'var(--clinical-severity-critical-signal)';
      if (pct >= 0.7 || pct <= 0.1) return 'var(--clinical-severity-watch-signal)';
      return 'var(--clinical-severity-normal-signal)';

    default:
      return 'var(--clinical-severity-normal-signal)';
  }
}

// ─── RASS Scale Visual ──────────────────────────────────────────────────────

function RASSScaleDisplay({ score }: { score: number }) {
  const levels = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4];
  const rassLabels: Record<number, string> = {
    '-5': 'Não Despertável',
    '-4': 'Sedação Profunda',
    '-3': 'Sed. Moderada',
    '-2': 'Sedação Leve',
    '-1': 'Sonolento',
    '0': 'Alerta/Calmo',
    '1': 'Inquieto',
    '2': 'Agitado',
    '3': 'Muito Agitado',
    '4': 'Combativo',
  };

  return (
    <div className="mt-3">
      <div className="flex items-end gap-px h-10 mb-1">
        {levels.map((level) => {
          const isActive = level === score;
          let bg: string;
          if (level >= 3) bg = 'var(--clinical-severity-watch-signal)';
          else if (level <= -4) bg = 'var(--clinical-severity-critical-signal)';
          else if (level >= 1) bg = 'var(--clinical-severity-watch-signal)';
          else if (level <= -1) bg = 'var(--clinical-severity-watch-signal)';
          else bg = 'var(--clinical-severity-normal-signal)';

          return (
            <div
              key={level}
              className="flex-1 rounded-t-sm transition-all"
              style={{
                height: isActive ? '100%' : '40%',
                backgroundColor: bg,
                opacity: isActive ? 1 : 0.35,
                borderTop: isActive ? '2px solid var(--semantic-text-primary)' : 'none',
              }}
              title={`${level >= 0 ? '+' : ''}${level}`}
            />
          );
        })}
      </div>
      <div className="flex justify-between text-[10px] px-0.5" style={{ color: 'var(--semantic-text-secondary)' }}>
        {levels.map((level) => (
          <span key={level} className="text-center" style={{ fontWeight: level === score ? 700 : 400 }}>
            {level >= 0 ? `+${level}` : level}
          </span>
        ))}
      </div>
      {rassLabels[score] && (
        <p className="text-xs mt-1 text-center font-medium" style={{ color: 'var(--semantic-text-secondary)' }}>
          {rassLabels[score]}
        </p>
      )}
    </div>
  );
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function ScoreDisplay({
  formType,
  score,
  maxScore,
  label,
  details,
}: ScoreDisplayProps) {
  // Compute percentage (0–1) for progress bar
  const minScore = formType === 'rass' ? -5 : formType === 'glasgow' ? 3 : formType === 'lpp' ? 6 : 0;
  const range = maxScore - minScore;
  const pct = range > 0 ? Math.max(0, Math.min(1, (score - minScore) / range)) : 0;

  const colorVar = getScoreColor(formType, score);
  const interpretation = getScoreInterpretation(formType, score);
  const progressColor = getProgressColor(formType, pct);

  const isInverted = formType === 'glasgow'; // higher is better

  return (
    <div
      className="rounded-xl border p-5 w-full"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-canvas)',
      }}
      role="region"
      aria-label={`Resultado ${label}: ${score}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {formIcons[formType]}
          <span
            className="text-sm font-semibold uppercase tracking-wider"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            {label}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
            {minScore}–{maxScore}
          </span>
        </div>
      </div>

      {/* Score number */}
      <div className="flex items-baseline gap-2 mb-3">
        <span
          className="text-4xl font-bold"
          style={{ color: colorVar }}
          aria-label={`Escore: ${score}`}
        >
          {score}
        </span>
        {interpretation && (
          <span
            className="text-sm font-medium"
            style={{ color: colorVar, opacity: 0.8 }}
          >
            {interpretation}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="w-full h-2.5 rounded-full mb-3 overflow-hidden" style={{ backgroundColor: 'var(--semantic-border-default)' }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${pct * 100}%`,
            backgroundColor: progressColor,
          }}
          role="progressbar"
          aria-valuenow={score}
          aria-valuemin={minScore}
          aria-valuemax={maxScore}
          aria-label={`${label}: ${score} de ${maxScore}`}
        />
      </div>

      {/* RASS specific scale */}
      {formType === 'rass' && <RASSScaleDisplay score={score} />}

      {/* Detail breakdown for SOFA / Glasgow */}
      {details && details.length > 0 && (
        <div className="mt-3 pt-3 border-t" style={{ borderColor: 'var(--semantic-border-default)' }}>
          <span
            className="text-xs font-semibold uppercase tracking-wider block mb-2"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Detalhamento
          </span>
          <div className="space-y-1.5">
            {details.map((d) => {
              const pctDetail = d.max > 0 ? d.score / d.max : 0;
              let detailColor: string;
              if (pctDetail >= 0.8) detailColor = 'var(--clinical-severity-critical-on-surface)';
              else if (pctDetail >= 0.5) detailColor = 'var(--clinical-severity-watch-on-surface)';
              else detailColor = 'var(--clinical-severity-normal-on-surface)';

              return (
                <div key={d.label} className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--semantic-text-secondary)' }}>{d.label}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--semantic-border-default)' }}>
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${d.max > 0 ? (d.score / d.max) * 100 : 0}%`,
                          backgroundColor: detailColor,
                        }}
                      />
                    </div>
                    <span className="font-medium text-xs min-w-[3ch] text-right" style={{ color: detailColor }}>
                      {d.score}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Alerta para scores críticos */}
      {(formType === 'sofa' && score >= 13) || (formType === 'glasgow' && score <= 8) || (formType === 'lpp' && score <= 9) ? (
        <div
          className="mt-3 flex items-center gap-2 text-xs font-medium p-2 rounded-lg"
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash, rgba(220,38,38,0.1))',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          role="alert"
        >
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
          <span>
            {formType === 'sofa'
              ? 'ATENÇÃO: Escore SOFA elevado — risco de mortalidade aumentado. Reavaliar conduta.'
              : formType === 'lpp'
                ? 'ATENÇÃO: Braden muito baixo — risco muito alto de lesão por pressão. Implementar medidas preventivas imediatas.'
                : 'ATENÇÃO: Glasgow grave — risco neurológico iminente. Avaliar neurocirurgia.'}
          </span>
        </div>
      ) : null}
    </div>
  );
}
