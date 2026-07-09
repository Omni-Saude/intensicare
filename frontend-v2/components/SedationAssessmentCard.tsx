'use client';

import React from 'react';
import {
  AlertTriangle,
  Brain,
  Thermometer,
  Eye,
  Clock,
  User,
  ChevronDown,
} from 'lucide-react';
import type { SedationAssessment } from '@/lib/sedation-types';
import {
  getRASSLabel,
  getRASSColor,
  getRASSBgColor,
  getBPSNRSCategory,
  PAIN_CATEGORY_LABELS,
  PAIN_CATEGORY_COLORS,
  formatCAMICU,
  getCAMICULabel,
  getCAMICUIColor,
  getCAMICUBgColor,
  formatSedationTimestamp,
} from '@/lib/sedation-types';

// ─── Props ────────────────────────────────────────────────────────────────────

interface SedationAssessmentCardProps {
  assessment?: SedationAssessment;
  isLoading?: boolean;
  error?: string | null;
}

// ─── RASS Scale Bar ──────────────────────────────────────────────────────────

const RASS_RANGE = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4] as const;

interface RASSBarProps {
  currentScore: number;
}

function RASSBar({ currentScore }: RASSBarProps): React.ReactElement {
  return (
    <div className="space-y-1.5" role="img" aria-label={`Escala RASS visual: valor atual ${currentScore > 0 ? '+' : ''}${currentScore}`}>
      {/* Labels row */}
      <div className="flex justify-between text-[10px] font-medium px-0.5">
        <span style={{ color: 'var(--semantic-text-secondary)' }}>-5</span>
        <span style={{ color: 'var(--semantic-text-secondary)' }}>0</span>
        <span style={{ color: 'var(--semantic-text-secondary)' }}>+4</span>
      </div>

      {/* Color bar */}
      <div className="flex h-3 rounded-full overflow-hidden">
        {RASS_RANGE.map((val) => {
          const isActive = val === currentScore;
          return (
            <div
              key={val}
              className={`flex-1 transition-all ${isActive ? 'ring-2 ring-offset-1 ring-white dark:ring-[var(--semantic-text-primary)]' : ''}`}
              style={{
                backgroundColor: getRASSColor(val),
                opacity: isActive ? 1 : 0.45,
                boxShadow: isActive ? `0 0 6px ${getRASSColor(val)}` : undefined,
                borderRadius: val === -5 ? '9999px 0 0 9999px' : val === 4 ? '0 9999px 9999px 0' : undefined,
              }}
              title={`RASS ${val > 0 ? '+' : ''}${val}: ${getRASSLabel(val)}${isActive ? ' (atual)' : ''}`}
            />
          );
        })}
      </div>

      {/* Indicator arrow */}
      <div className="relative h-4">
        <div
          className="absolute -translate-x-1/2"
          style={{
            left: `${((currentScore + 5) / 9) * 100}%`,
          }}
        >
          <ChevronDown
            className="w-3.5 h-3.5"
            style={{ color: getRASSColor(currentScore) }}
            aria-hidden="true"
          />
        </div>
      </div>

      {/* Labels row: sedation <-> agitation */}
      <div className="flex justify-between text-[10px] font-medium px-0.5">
        <span style={{ color: 'var(--semantic-text-secondary)' }}>Sedação</span>
        <span style={{ color: 'var(--semantic-text-secondary)' }}>Alvo</span>
        <span style={{ color: 'var(--semantic-text-secondary)' }}>Agitação</span>
      </div>
    </div>
  );
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function SedationSkeleton(): React.ReactElement {
  return (
    <div
      className="rounded-xl border p-5 space-y-5 animate-pulse"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      role="status"
      aria-label="Carregando avaliação de sedação"
    >
      {/* RASS section */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-5 h-5 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-4 rounded w-10"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
        <div
          className="h-8 rounded w-20 mb-3"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
        <div
          className="h-14 rounded w-full"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>

      <div
        className="border-t"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      />

      {/* BPS/NRS section */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-5 h-5 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-4 rounded w-16"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
        <div
          className="h-6 rounded w-24 mb-2"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>

      <div
        className="border-t"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      />

      {/* CAM-ICU section */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-5 h-5 rounded"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
          <div
            className="h-4 rounded w-20"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        </div>
        <div
          className="h-6 rounded w-28"
          style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
        />
      </div>

      <div
        className="border-t"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      />

      {/* Timestamp */}
      <div
        className="h-3 rounded w-48"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function SedationAssessmentCard({
  assessment,
  isLoading = false,
  error = null,
}: SedationAssessmentCardProps): React.ReactElement {
  // ── Loading state ──────────────────────────────────────────────────────────
  if (isLoading) {
    return <SedationSkeleton />;
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm"
        style={{
          backgroundColor: 'var(--feedback-error-bg-dark)',
          color: 'var(--feedback-error-text-dark)',
          borderColor: 'var(--feedback-error-border-dark)',
          borderWidth: '1px',
        }}
      >
        <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // ── Empty state ────────────────────────────────────────────────────────────
  if (!assessment) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-8 text-sm rounded-xl border"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
          color: 'var(--semantic-text-secondary)',
        }}
        role="status"
        aria-label="Nenhuma avaliação disponível"
      >
        <Brain className="w-10 h-10 opacity-30" aria-hidden="true" />
        <p>Nenhuma avaliação de sedação disponível</p>
      </div>
    );
  }

  const camResult = formatCAMICU(assessment.cam_icu_positive);
  const painCategory = getBPSNRSCategory(assessment.bps_nrs_score, assessment.bps_nrs_type);

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      {/* ── RASS Section ──────────────────────────────────────────────────── */}
      <div className="p-5 pb-3">
        <div className="flex items-center gap-2 mb-3">
          <Brain className="w-5 h-5" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          <h3 className="text-sm font-semibold uppercase tracking-wide" style={{ color: 'var(--semantic-text-secondary)' }}>
            RASS — Nível de Sedação
          </h3>
        </div>

        {/* Score grande + label */}
        <div className="flex items-baseline gap-3 mb-4">
          <span
            className="text-4xl font-bold tabular-nums"
            style={{ color: getRASSColor(assessment.rass_score) }}
            aria-label={`RASS ${assessment.rass_score > 0 ? '+' : ''}${assessment.rass_score}`}
          >
            {assessment.rass_score > 0 ? '+' : ''}
            {assessment.rass_score}
          </span>
          <span
            className="text-base font-medium"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            {getRASSLabel(assessment.rass_score)}
          </span>
        </div>

        {/* Escala visual */}
        <div className="px-1">
          <RASSBar currentScore={assessment.rass_score} />
        </div>
      </div>

      <div
        className="border-t mx-5"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      />

      {/* ── BPS/NRS Section ───────────────────────────────────────────────── */}
      <div className="p-5 py-3">
        <div className="flex items-center gap-2 mb-2">
          <Thermometer className="w-5 h-5" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          <h3 className="text-sm font-semibold uppercase tracking-wide" style={{ color: 'var(--semantic-text-secondary)' }}>
            {assessment.bps_nrs_type === 'NRS' ? 'NRS' : 'BPS'} — Avaliação de Dor
          </h3>
        </div>

        {assessment.bps_nrs_score !== undefined && assessment.bps_nrs_score !== null ? (
          <div className="flex items-baseline gap-3">
            <span
              className="text-2xl font-bold tabular-nums"
              style={{ color: PAIN_CATEGORY_COLORS[painCategory] }}
              aria-label={`${assessment.bps_nrs_type ?? 'BPS'}: ${assessment.bps_nrs_score}`}
            >
              {assessment.bps_nrs_score}
            </span>
            <span
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
              style={{
                backgroundColor: PAIN_CATEGORY_COLORS[painCategory],
                color: 'white',
                opacity: 0.85,
              }}
            >
              {PAIN_CATEGORY_LABELS[painCategory]}
            </span>
          </div>
        ) : (
          <span style={{ color: 'var(--semantic-text-secondary)' }} className="text-sm italic">
            Não avaliada
          </span>
        )}
      </div>

      <div
        className="border-t mx-5"
        style={{ borderColor: 'var(--semantic-border-default)' }}
      />

      {/* ── CAM-ICU Section ───────────────────────────────────────────────── */}
      <div className="p-5 py-3">
        <div className="flex items-center gap-2 mb-2">
          <Eye className="w-5 h-5" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          <h3 className="text-sm font-semibold uppercase tracking-wide" style={{ color: 'var(--semantic-text-secondary)' }}>
            CAM-ICU — Delirium
          </h3>
        </div>

        <span
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold"
          style={{
            backgroundColor: getCAMICUBgColor(assessment.cam_icu_positive),
            color: getCAMICUIColor(assessment.cam_icu_positive),
          }}
        >
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: getCAMICUIColor(assessment.cam_icu_positive) }}
            aria-hidden="true"
          />
          {getCAMICULabel(assessment.cam_icu_positive)}
        </span>
      </div>

      {/* ── Footer: Timestamp + Assessor ───────────────────────────────────── */}
      <div
        className="px-5 py-3 flex items-center gap-4 text-xs flex-wrap"
        style={{
          backgroundColor: 'var(--semantic-surface-overlay)',
          color: 'var(--semantic-text-secondary)',
        }}
      >
        <span className="inline-flex items-center gap-1">
          <Clock className="w-3 h-3" aria-hidden="true" />
          Avaliado em {formatSedationTimestamp(assessment.assessed_at)}
        </span>
        {assessment.assessed_by && (
          <span className="inline-flex items-center gap-1">
            <User className="w-3 h-3" aria-hidden="true" />
            por {assessment.assessed_by}
          </span>
        )}
      </div>

      {/* ── Notes ──────────────────────────────────────────────────────────── */}
      {assessment.notes && (
        <div
          className="px-5 py-3 text-sm border-t"
          style={{
            borderColor: 'var(--semantic-border-default)',
            color: 'var(--semantic-text-secondary)',
          }}
        >
          <p className="italic">{assessment.notes}</p>
        </div>
      )}
    </div>
  );
}
