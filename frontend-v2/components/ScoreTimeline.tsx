'use client';

import React, { useState, useCallback } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

export type ScoreType = 'MEWS' | 'NEWS2' | 'qSOFA' | 'SOFA';

export type ScoreTrend = 'increasing' | 'decreasing' | 'stable' | null;

export type SeverityBand = 'normal' | 'watch' | 'urgent' | 'critical';

/** Severity config: maps band → CSS custom properties (no hardcoded colors) */
const SEVERITY_TOKENS: Record<
  SeverityBand,
  { bgVar: string; textVar: string; borderVar: string; washVar: string }
> = {
  normal: {
    bgVar: 'var(--clinical-severity-normal-fill)',
    textVar: 'var(--clinical-severity-normal-on-fill)',
    borderVar: 'var(--clinical-severity-normal-signal)',
    washVar: 'var(--clinical-severity-normal-wash)',
  },
  watch: {
    bgVar: 'var(--clinical-severity-watch-fill)',
    textVar: 'var(--clinical-severity-watch-on-fill)',
    borderVar: 'var(--clinical-severity-watch-signal)',
    washVar: 'var(--clinical-severity-watch-wash)',
  },
  urgent: {
    bgVar: 'var(--clinical-severity-urgent-fill)',
    textVar: 'var(--clinical-severity-urgent-on-fill)',
    borderVar: 'var(--clinical-severity-urgent-signal)',
    washVar: 'var(--clinical-severity-urgent-wash)',
  },
  critical: {
    bgVar: 'var(--clinical-severity-critical-fill)',
    textVar: 'var(--clinical-severity-critical-on-fill)',
    borderVar: 'var(--clinical-severity-critical-signal)',
    washVar: 'var(--clinical-severity-critical-wash)',
  },
};

export interface ScoreComponentRow {
  /** Component label (e.g. "Freq. resp.", "SpO₂") */
  label: string;
  /** Current value with unit */
  value: string;
  /** Points contributed to aggregate (from versioned scorer service) */
  points: number;
  /** Reference range label */
  referenceRange: string;
  /** Severity band for this component */
  band: SeverityBand;
  /** Δ since previous calculation (optional) */
  delta?: string;
  /** Minutes since data was collected */
  stalenessMinutes?: number;
}

export interface ScoreChipData {
  /** Unique identifier */
  id: string;
  /** Score type: MEWS, NEWS2, qSOFA, SOFA */
  scoreType: ScoreType;
  /** Numeric aggregate value */
  value: number;
  /** Trend arrow direction */
  trend: ScoreTrend;
  /** Algorithm version (e.g. "v1.0.0") */
  algorithmVersion: string;
  /** ISO timestamp */
  timestamp: string;
  /** Per-component decomposition rows */
  decomposition: ScoreComponentRow[];
  /** Number of components present vs total expected */
  componentsPresent: number;
  componentsTotal: number;
  /** Whether this is a partial score */
  isPartial?: boolean;
  /** Improvement marker (melhora) */
  isImprovement?: boolean;
  /** Severity band for the aggregate */
  band: SeverityBand;
}

export interface ScoreTimelineProps {
  /** Chronological score entries (most recent first) */
  entries: ScoreChipData[];
  /** Optional CSS class for the container */
  className?: string;
  /** Callback when a chip is expanded */
  onChipExpand?: (chipId: string) => void;
  /** Label for the score type column header */
  scoreTypeLabel?: string;
  /** Show the decomposition panel by default for the most recent entry */
  expandLatest?: boolean;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Format ISO timestamp to HH:MM */
function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

/** Resolve severity band colors from CSS custom properties */
function severityStyle(band: SeverityBand): React.CSSProperties {
  const t = SEVERITY_TOKENS[band] ?? SEVERITY_TOKENS.normal;
  return {
    backgroundColor: t.bgVar,
    color: t.textVar,
    borderColor: t.borderVar,
  };
}

function severityTextStyle(band: SeverityBand): React.CSSProperties {
  const t = SEVERITY_TOKENS[band] ?? SEVERITY_TOKENS.normal;
  return { color: t.borderVar };
}

function severityWashStyle(band: SeverityBand): React.CSSProperties {
  const t = SEVERITY_TOKENS[band] ?? SEVERITY_TOKENS.normal;
  return { backgroundColor: t.washVar };
}

/** Score type label mapping */
const SCORE_LABELS: Record<ScoreType, string> = {
  MEWS: 'MEWS',
  NEWS2: 'NEWS2',
  qSOFA: 'qSOFA',
  SOFA: 'SOFA',
};

// ─── Sub-components ──────────────────────────────────────────────────────────

function TrendArrow({ trend }: { trend: ScoreTrend }) {
  if (trend === 'increasing') {
    return (
      <span
        className="inline-flex items-center"
        style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
        aria-label="Tendência: subindo"
        title="Em alta"
      >
        <TrendingUp className="w-3.5 h-3.5" />
      </span>
    );
  }
  if (trend === 'decreasing') {
    return (
      <span
        className="inline-flex items-center"
        style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
        aria-label="Tendência: descendo"
        title="Em baixa"
      >
        <TrendingDown className="w-3.5 h-3.5" />
      </span>
    );
  }
  return (
    <span
      className="inline-flex items-center"
      style={{ color: 'var(--semantic-text-secondary)' }}
      aria-label="Tendência: estável"
      title="Estável"
    >
      <Minus className="w-3.5 h-3.5" />
    </span>
  );
}

function ScoreChip({
  entry,
  isExpanded,
  onToggle,
}: {
  entry: ScoreChipData;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const time = formatTime(entry.timestamp);
  const chipAriaLabel = [
    entry.band === 'critical' ? 'Crítico.' : '',
    `${SCORE_LABELS[entry.scoreType]} ${entry.value}.`,
    entry.trend === 'increasing'
      ? 'Subindo.'
      : entry.trend === 'decreasing'
        ? 'Descendo.'
        : 'Estável.',
    entry.isPartial ? 'Score parcial.' : '',
    `${entry.componentsPresent} de ${entry.componentsTotal} componentes.`,
    `Versão ${entry.algorithmVersion}.`,
    `${time}.`,
  ]
    .filter(Boolean)
    .join(' ');

  const scoreTypeColor =
    entry.band === 'critical'
      ? 'var(--clinical-severity-critical-on-surface)'
      : entry.band === 'urgent'
        ? 'var(--clinical-severity-urgent-on-surface)'
        : entry.band === 'watch'
          ? 'var(--clinical-severity-watch-on-surface)'
          : 'var(--semantic-text-primary)';

  return (
    <button
      onClick={onToggle}
      className="group relative flex items-center gap-3 w-full px-3 py-2.5 rounded-lg border transition-all
                 hover:shadow-md focus-visible:outline-2 focus-visible:outline-offset-1
                 focus-visible:outline-[var(--clinical-severity-critical-signal)] text-left"
      style={{
        backgroundColor: isExpanded
          ? 'var(--semantic-surface-overlay)'
          : 'var(--semantic-surface-raised)',
        borderColor: isExpanded
          ? SEVERITY_TOKENS[entry.band].borderVar
          : 'var(--semantic-border-default)',
      }}
      aria-label={chipAriaLabel}
      aria-expanded={isExpanded}
      title={`${SCORE_LABELS[entry.scoreType]} ${entry.value} — ${time}`}
    >
      {/* Expand icon */}
      <span
        className="flex-shrink-0 w-4 h-4 flex items-center justify-center"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
      </span>

      {/* Severity indicator dot */}
      <span
        className="flex-shrink-0 w-2.5 h-2.5 rounded-full"
        style={{ backgroundColor: SEVERITY_TOKENS[entry.band].borderVar }}
        aria-hidden="true"
      />

      {/* Score type badge */}
      <span
        className="flex-shrink-0 inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide"
        style={severityStyle(entry.band)}
      >
        {SCORE_LABELS[entry.scoreType]}
      </span>

      {/* Numeric value (tabular monospace for scan-alignment) */}
      <span
        className="flex-shrink-0 font-mono text-lg font-bold tabular-nums min-w-[2ch] text-center"
        style={{ color: scoreTypeColor }}
      >
        {entry.value}
      </span>

      {/* Trend arrow */}
      <span className="flex-shrink-0">
        <TrendArrow trend={entry.trend} />
      </span>

      {/* Partial / improvement markers */}
      <span className="flex-shrink-0 inline-flex items-center gap-1">
        {entry.isPartial && (
          <span
            className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
            style={severityWashStyle('urgent')}
            aria-label="Score parcial"
          >
            parcial
          </span>
        )}
        {entry.isImprovement && (
          <span
            className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
            style={severityWashStyle('normal')}
            aria-label="Melhora"
          >
            melhora
          </span>
        )}
      </span>

      {/* Algorithm version */}
      <span
        className="flex-shrink-0 text-[10px] font-mono"
        style={{ color: 'var(--semantic-text-secondary)' }}
        aria-label={`Versão do algoritmo: ${entry.algorithmVersion}`}
      >
        {entry.algorithmVersion}
      </span>

      {/* Timestamp */}
      <span
        className="flex-shrink-0 text-xs ml-auto"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {time}
      </span>
    </button>
  );
}

function DecompositionPanel({
  entry,
}: {
  entry: ScoreChipData;
}) {
  const panelAriaLabel = `Decomposição: ${SCORE_LABELS[entry.scoreType]} ${entry.value}. ${entry.componentsPresent} de ${entry.componentsTotal} componentes. Versão ${entry.algorithmVersion}.`;

  return (
    <div
      className="ml-10 mt-1 mb-2 rounded-lg border overflow-hidden"
      style={{
        backgroundColor: 'var(--semantic-surface-raised)',
        borderColor: 'var(--semantic-border-default)',
      }}
      role="region"
      aria-label={panelAriaLabel}
    >
      {/* Panel header */}
      <div
        className="flex flex-wrap items-center gap-2 px-4 py-2.5 text-xs"
        style={{
          backgroundColor: severityWashStyle(entry.band).backgroundColor,
          borderBottom: `1px solid var(--semantic-border-default)`,
          color: 'var(--semantic-text-secondary)',
        }}
      >
        <span
          className="font-semibold"
          style={{
            color: severityTextStyle(entry.band).color,
          }}
        >
          {SCORE_LABELS[entry.scoreType]} {entry.value}
        </span>
        <span>{entry.algorithmVersion}</span>
        <span aria-label={`${entry.componentsPresent} de ${entry.componentsTotal} componentes presentes`}>
          {entry.componentsPresent} de {entry.componentsTotal}
        </span>
        <span
          className="ml-auto text-[10px] italic"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          apoio à decisão — o médico decide
        </span>
      </div>

      {/* Component table */}
      <div className="overflow-x-auto">
        <table
          className="w-full text-xs"
          style={{ color: 'var(--semantic-text-primary)' }}
          role="table"
          aria-label={`Componentes do ${SCORE_LABELS[entry.scoreType]}`}
        >
          <thead>
            <tr
              style={{
                borderBottom: `1px solid var(--semantic-border-default)`,
              }}
            >
              <th
                className="text-left px-4 py-2 font-semibold"
                style={{ color: 'var(--semantic-text-secondary)' }}
                scope="col"
              >
                Componente
              </th>
              <th
                className="text-right px-3 py-2 font-semibold font-mono"
                style={{ color: 'var(--semantic-text-secondary)' }}
                scope="col"
              >
                Valor
              </th>
              <th
                className="text-center px-3 py-2 font-semibold font-mono"
                style={{ color: 'var(--semantic-text-secondary)' }}
                scope="col"
              >
                Pts
              </th>
              <th
                className="text-left px-3 py-2 font-semibold"
                style={{ color: 'var(--semantic-text-secondary)' }}
                scope="col"
              >
                Ref.
              </th>
              {entry.decomposition.some((r) => r.delta !== undefined) && (
                <th
                  className="text-center px-3 py-2 font-semibold"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  scope="col"
                >
                  Δ
                </th>
              )}
              <th
                className="text-right px-4 py-2 font-semibold"
                style={{ color: 'var(--semantic-text-secondary)' }}
                scope="col"
              >
                Idade
              </th>
            </tr>
          </thead>
          <tbody>
            {entry.decomposition.map((row, idx) => (
              <tr
                key={`${entry.id}-decomp-${idx}`}
                className="hover:bg-opacity-50 transition-colors"
                style={{
                  borderBottom:
                    idx < entry.decomposition.length - 1
                      ? `1px solid var(--semantic-border-default)`
                      : 'none',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    SEVERITY_TOKENS[row.band].washVar;
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.backgroundColor =
                    'transparent';
                }}
                aria-label={`${row.label}: ${row.value}, ${row.points} pontos, ${row.band}`}
              >
                {/* Component label */}
                <td
                  className="px-4 py-2 font-medium"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  {row.label}
                </td>

                {/* Value */}
                <td
                  className="px-3 py-2 text-right font-mono tabular-nums font-semibold"
                  style={{ color: severityTextStyle(row.band).color }}
                >
                  {row.value}
                </td>

                {/* Points */}
                <td className="px-3 py-2 text-center font-mono tabular-nums">
                  <span
                    className="inline-flex items-center justify-center min-w-[1.5rem] px-1 py-0.5 rounded font-bold"
                    style={severityStyle(row.band)}
                  >
                    {row.points > 0 ? `+${row.points}` : row.points}
                  </span>
                </td>

                {/* Reference range */}
                <td
                  className="px-3 py-2"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {row.referenceRange}
                </td>

                {/* Delta */}
                {entry.decomposition.some((r) => r.delta !== undefined) && (
                  <td
                    className="px-3 py-2 text-center font-mono tabular-nums font-semibold"
                    style={{
                      color: row.delta?.startsWith('+')
                        ? 'var(--clinical-severity-critical-on-surface)'
                        : row.delta?.startsWith('-')
                          ? 'var(--clinical-severity-normal-on-surface)'
                          : 'var(--semantic-text-secondary)',
                    }}
                  >
                    {row.delta ?? '→'}
                  </td>
                )}

                {/* Staleness */}
                <td
                  className="px-4 py-2 text-right"
                  style={{
                    color:
                      row.stalenessMinutes !== undefined &&
                      row.stalenessMinutes > 60
                        ? 'var(--clinical-severity-watch-on-surface)'
                        : row.stalenessMinutes !== undefined &&
                            row.stalenessMinutes > 5
                          ? 'var(--semantic-text-secondary)'
                          : 'var(--clinical-severity-normal-on-surface)',
                  }}
                  aria-label={
                    row.stalenessMinutes !== undefined
                      ? `Dados de ${row.stalenessMinutes} minutos atrás`
                      : undefined
                  }
                >
                  {row.stalenessMinutes !== undefined
                    ? `${row.stalenessMinutes}min`
                    : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* What-changed summary */}
      {entry.decomposition.some((r) => r.delta !== undefined) && (
        <div
          className="px-4 py-2 text-[10px] italic border-t"
          style={{
            borderColor: 'var(--semantic-border-default)',
            color: 'var(--semantic-text-secondary)',
          }}
        >
          what-changed:{' '}
          {entry.decomposition
            .filter((r) => r.delta !== undefined)
            .map((r) => `${r.label} ${r.delta}`)
            .join(' · ')}
        </div>
      )}
    </div>
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function ScoreTimeline({
  entries,
  className = '',
  onChipExpand,
  expandLatest = false,
}: ScoreTimelineProps) {
  const [expandedId, setExpandedId] = useState<string | null>(
    expandLatest && entries.length > 0 ? entries[0]!.id : null,
  );

  const handleToggle = useCallback(
    (chipId: string) => {
      setExpandedId((prev) => {
        const next = prev === chipId ? null : chipId;
        if (next && onChipExpand) {
          onChipExpand(next);
        }
        return next;
      });
    },
    [onChipExpand],
  );

  // Empty state
  if (!entries || entries.length === 0) {
    return (
      <div
        className={`flex items-center justify-center py-8 text-sm ${className}`}
        style={{ color: 'var(--semantic-text-secondary)' }}
        role="status"
        aria-label="Nenhum score disponível"
      >
        Nenhum score computado — aguardando primeiros sinais vitais
      </div>
    );
  }

  return (
    <div
      className={`flex flex-col gap-1 ${className}`}
      role="list"
      aria-label="Linha do tempo de scores clínicos"
    >
      {entries.map((entry) => (
        <div key={entry.id} role="listitem">
          <ScoreChip
            entry={entry}
            isExpanded={expandedId === entry.id}
            onToggle={() => handleToggle(entry.id)}
          />

          {expandedId === entry.id && (
            <DecompositionPanel entry={entry} />
          )}
        </div>
      ))}
    </div>
  );
}

export { ScoreChip, DecompositionPanel, TrendArrow };
