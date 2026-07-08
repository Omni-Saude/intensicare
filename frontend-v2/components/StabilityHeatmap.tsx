'use client';

import React, { useMemo, useState, useCallback, useRef, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Filter,
} from 'lucide-react';
import {
  type StabilityCriterion,
  type StabilityCriterionStatus,
  type StabilityCategory,
  STABILITY_CATEGORIES,
  CATEGORY_LABELS,
  getCategoryLabel,
  getCriterionWashToken,
  getCriterionSignalToken,
} from '@/lib/stability-types';

// ─── Props ──────────────────────────────────────────────────────────────────

interface StabilityHeatmapProps {
  criteria: StabilityCriterion[];
  categoryFilter?: string;
  isLoading?: boolean;
  error?: string | null;
}

// ─── Tooltip ────────────────────────────────────────────────────────────────

interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  criterion: StabilityCriterion | null;
}

function CriterionTooltip({
  criterion,
  style,
}: {
  criterion: StabilityCriterion;
  style: React.CSSProperties;
}): React.ReactElement {
  const statusLabel =
    criterion.status === 'normal'
      ? 'Normal'
      : criterion.status === 'warning'
      ? 'Atenção'
      : 'Crítico';

  const statusColor =
    criterion.status === 'normal'
      ? 'var(--clinical-stability-estavel-on-surface-dark)'
      : criterion.status === 'warning'
      ? 'var(--clinical-stability-atencao-on-surface-dark)'
      : 'var(--clinical-stability-critico-on-surface-dark)';

  return (
    <div
      className="fixed z-50 pointer-events-none"
      style={style}
      role="tooltip"
    >
      <div
        className="rounded-lg px-3 py-2.5 text-xs shadow-lg max-w-[260px]"
        style={{
          backgroundColor: 'var(--semantic-surface-raised)',
          color: 'var(--semantic-text-primary)',
          borderColor: 'var(--semantic-border-default)',
          borderWidth: '1px',
        }}
      >
        <div className="font-semibold mb-1" style={{ color: statusColor }}>
          {criterion.name}
        </div>
        <div className="space-y-0.5">
          <div className="flex justify-between gap-3">
            <span style={{ color: 'var(--semantic-text-secondary)' }}>Valor:</span>
            <span className="font-medium tabular-nums">{criterion.value}</span>
          </div>
          <div className="flex justify-between gap-3">
            <span style={{ color: 'var(--semantic-text-secondary)' }}>Limiar:</span>
            <span className="font-medium tabular-nums">{criterion.threshold}</span>
          </div>
          <div className="flex justify-between gap-3">
            <span style={{ color: 'var(--semantic-text-secondary)' }}>Status:</span>
            <span className="font-semibold" style={{ color: statusColor }}>
              {statusLabel}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Skeleton ────────────────────────────────────────────────────────────────

function HeatmapSkeleton(): React.ReactElement {
  return (
    <div
      className="animate-pulse"
      role="status"
      aria-label="Carregando mapa de estabilidade"
    >
      {/* Grid skeleton */}
      <div
        className="rounded-xl overflow-hidden"
        style={{
          borderColor: 'var(--semantic-border-default)',
          borderWidth: '1px',
        }}
      >
        {/* Header row */}
        <div
          className="grid gap-px"
          style={{
            gridTemplateColumns: 'repeat(6, 1fr)',
            backgroundColor: 'var(--semantic-surface-overlay)',
            padding: '1px',
          }}
        >
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-8 flex items-center justify-center"
              style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
            >
              <div
                className="h-3 rounded w-16"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            </div>
          ))}
        </div>
        {/* Body rows */}
        {Array.from({ length: 5 }).map((_, row) => (
          <div
            key={row}
            className="grid gap-px"
            style={{
              gridTemplateColumns: 'repeat(6, 1fr)',
              backgroundColor: 'var(--semantic-surface-overlay)',
              padding: '0 1px 1px 1px',
            }}
          >
            {Array.from({ length: 6 }).map((_, col) => (
              <div
                key={col}
                className="flex items-center justify-center h-12"
                style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
              >
                <div
                  className="w-3.5 h-3.5 rounded-full"
                  style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
                />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function StabilityHeatmap({
  criteria,
  categoryFilter,
  isLoading = false,
  error = null,
}: StabilityHeatmapProps): React.ReactElement {
  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false,
    x: 0,
    y: 0,
    criterion: null,
  });
  const gridRef = useRef<HTMLDivElement>(null);
  const [focusedCell, setFocusedCell] = useState<{ row: number; col: number } | null>(null);
  const cellRefs = useRef<Map<string, HTMLElement>>(new Map());

  // ── Group criteria by category ──────────────────────────────────────────
  const grouped = useMemo(() => {
    const map = new Map<StabilityCategory, StabilityCriterion[]>();
    for (const cat of STABILITY_CATEGORIES) {
      map.set(cat, []);
    }
    for (const c of criteria) {
      const existing = map.get(c.category) || [];
      existing.push(c);
      map.set(c.category, existing);
    }
    return map;
  }, [criteria]);

  // ── Filter categories ───────────────────────────────────────────────────
  const displayCategories = useMemo(() => {
    if (!categoryFilter) return STABILITY_CATEGORIES;
    return STABILITY_CATEGORIES.filter((cat) => cat === categoryFilter);
  }, [categoryFilter]);

  // ── Max rows (for consistent grid height) ───────────────────────────────
  const maxRows = useMemo(() => {
    return Math.max(...displayCategories.map((cat) => grouped.get(cat)?.length || 0));
  }, [grouped, displayCategories]);

  // ── Handlers ────────────────────────────────────────────────────────────
  const handleCellMouseEnter = useCallback(
    (e: React.MouseEvent, criterion: StabilityCriterion) => {
      const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      setTooltip({
        visible: true,
        x: rect.left + rect.width / 2,
        y: rect.top - 8,
        criterion,
      });
    },
    [],
  );

  const handleCellMouseLeave = useCallback(() => {
    setTooltip((prev) => ({ ...prev, visible: false }));
  }, []);

  const handleCellFocus = useCallback(
    (e: React.FocusEvent, criterion: StabilityCriterion) => {
      const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      setTooltip({
        visible: true,
        x: rect.left + rect.width / 2,
        y: rect.top - 8,
        criterion,
      });
    },
    [],
  );

  const handleCellBlur = useCallback(() => {
    setTooltip((prev) => ({ ...prev, visible: false }));
  }, []);

  const setCellRef = useCallback(
    (row: number, col: number) => (el: HTMLElement | null) => {
      const key = `${row}-${col}`;
      if (el) {
        cellRefs.current.set(key, el);
      } else {
        cellRefs.current.delete(key);
      }
    },
    [],
  );

  const handleGridKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const numCols = displayCategories.length;
      const numRows = maxRows;
      if (numCols === 0 || numRows === 0) return;

      setFocusedCell((prev) => {
        let nextRow = prev?.row ?? 0;
        let nextCol = prev?.col ?? 0;

        switch (e.key) {
          case 'ArrowRight':
            e.preventDefault();
            nextCol = Math.min(nextCol + 1, numCols - 1);
            break;
          case 'ArrowLeft':
            e.preventDefault();
            nextCol = Math.max(nextCol - 1, 0);
            break;
          case 'ArrowDown':
            e.preventDefault();
            nextRow = Math.min(nextRow + 1, numRows - 1);
            break;
          case 'ArrowUp':
            e.preventDefault();
            nextRow = Math.max(nextRow - 1, 0);
            break;
          case 'Home':
            if (e.ctrlKey || e.metaKey) {
              e.preventDefault();
              nextRow = 0;
              nextCol = 0;
            } else {
              e.preventDefault();
              nextCol = 0;
            }
            break;
          case 'End':
            if (e.ctrlKey || e.metaKey) {
              e.preventDefault();
              nextRow = numRows - 1;
              nextCol = numCols - 1;
            } else {
              e.preventDefault();
              nextCol = numCols - 1;
            }
            break;
          default:
            return prev;
        }

        return { row: nextRow, col: nextCol };
      });
    },
    [displayCategories.length, maxRows],
  );

  // Focus the DOM element when focusedCell changes
  useEffect(() => {
    if (focusedCell) {
      const key = `${focusedCell.row}-${focusedCell.col}`;
      const cell = cellRefs.current.get(key);
      if (cell) {
        cell.focus();
      }
    }
  }, [focusedCell]);

  // ── Loading state ───────────────────────────────────────────────────────
  if (isLoading) {
    return <HeatmapSkeleton />;
  }

  // ── Error state ─────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm"
        style={{
          backgroundColor: 'var(--clinical-severity-critical-wash)',
          color: 'var(--clinical-severity-critical-on-surface)',
          borderColor: 'var(--clinical-severity-critical-signal)',
          borderWidth: '1px',
        }}
      >
        <AlertTriangle className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // ── Empty state ─────────────────────────────────────────────────────────
  if (criteria.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-10 text-sm"
        style={{ color: 'var(--semantic-text-secondary)' }}
        role="status"
      >
        <Filter className="w-10 h-10 opacity-30" aria-hidden="true" />
        <p>Nenhum critério configurado</p>
      </div>
    );
  }

  // ── Signal dot component ────────────────────────────────────────────────
  const SignalDot = ({ status }: { status: StabilityCriterionStatus }) => {
    const Icon =
      status === 'normal'
        ? CheckCircle2
        : status === 'warning'
        ? AlertCircle
        : XCircle;

    const color =
      status === 'normal'
        ? 'var(--clinical-stability-estavel-signal-dark)'
        : status === 'warning'
        ? 'var(--clinical-stability-atencao-signal-dark)'
        : 'var(--clinical-stability-critico-signal-dark)';

    return <Icon className="w-4 h-4" style={{ color }} aria-hidden="true" />;
  };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div>
      {/* ── Heatmap Grid ─────────────────────────────────────────────────── */}
      <div
        ref={gridRef}
        className="rounded-xl overflow-hidden focus-visible:outline-none"
        style={{
          borderColor: 'var(--semantic-border-default)',
          borderWidth: '1px',
        }}
        role="grid"
        aria-label="Mapa de calor de estabilidade hemodinâmica"
        tabIndex={0}
        onKeyDown={handleGridKeyDown}
        onFocus={() => {
          if (!focusedCell) {
            setFocusedCell({ row: 0, col: 0 });
          }
        }}
      >
        {/* Header row */}
        <div
          className="grid gap-px"
          style={{
            gridTemplateColumns: `repeat(${displayCategories.length}, 1fr)`,
            backgroundColor: 'var(--semantic-surface-overlay)',
            padding: '1px',
          }}
          role="row"
        >
          {displayCategories.map((cat) => (
            <div
              key={cat}
              className="flex items-center justify-center h-9 px-2"
              style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
              role="columnheader"
            >
              <span
                className="text-xs font-semibold truncate"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {getCategoryLabel(cat)}
              </span>
            </div>
          ))}
        </div>

        {/* Body rows */}
        {Array.from({ length: maxRows }).map((_, rowIdx) => (
          <div
            key={rowIdx}
            className="grid gap-px"
            style={{
              gridTemplateColumns: `repeat(${displayCategories.length}, 1fr)`,
              backgroundColor: 'var(--semantic-surface-overlay)',
              padding: '0 1px 1px 1px',
            }}
            role="row"
          >
            {displayCategories.map((cat, colIdx) => {
              const catCriteria = grouped.get(cat) || [];
              const criterion = catCriteria[rowIdx] || null;

              if (!criterion) {
                return (
                  <div
                    key={`${cat}-${rowIdx}`}
                    className={`flex items-center justify-center h-12 ${
                      focusedCell?.row === rowIdx && focusedCell?.col === colIdx
                        ? 'ring-2 ring-blue-500 ring-offset-1 rounded-sm'
                        : ''
                    }`}
                    style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
                    role="gridcell"
                    aria-label={`${getCategoryLabel(cat)} — vazio`}
                    tabIndex={-1}
                    ref={setCellRef(rowIdx, colIdx)}
                    onFocus={() => setFocusedCell({ row: rowIdx, col: colIdx })}
                  />
                );
              }

              const washColor = getCriterionWashToken(criterion.status);
              const signalColor = getCriterionSignalToken(criterion.status);

              return (
                <div
                  key={criterion.alert_id}
                  className={`relative flex items-center justify-center h-12 cursor-pointer transition-opacity hover:opacity-80 ${
                    focusedCell?.row === rowIdx && focusedCell?.col === colIdx
                      ? 'ring-2 ring-blue-500 ring-offset-1 rounded-sm'
                      : ''
                  }`}
                  style={{
                    backgroundColor: washColor,
                    opacity: focusedCell?.row === rowIdx && focusedCell?.col === colIdx ? 0.3 : 0.16,
                  }}
                  role="gridcell"
                  aria-label={`${criterion.name}: ${criterion.status === 'normal' ? 'Normal' : criterion.status === 'warning' ? 'Atenção' : 'Crítico'}`}
                  tabIndex={-1}
                  ref={setCellRef(rowIdx, colIdx)}
                  onFocus={(e) => {
                    setFocusedCell({ row: rowIdx, col: colIdx });
                    handleCellFocus(e, criterion);
                  }}
                  onBlur={handleCellBlur}
                  onMouseEnter={(e) => handleCellMouseEnter(e, criterion)}
                  onMouseLeave={handleCellMouseLeave}
                >
                  <SignalDot status={criterion.status} />
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* ── Legend ────────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-4 mt-3 text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" style={{ color: 'var(--clinical-stability-estavel-signal-dark)' }} aria-hidden="true" />
          <span>Normal</span>
        </div>
        <div className="flex items-center gap-1.5">
          <AlertCircle className="w-3.5 h-3.5" style={{ color: 'var(--clinical-stability-atencao-signal-dark)' }} aria-hidden="true" />
          <span>Atenção</span>
        </div>
        <div className="flex items-center gap-1.5">
          <XCircle className="w-3.5 h-3.5" style={{ color: 'var(--clinical-stability-critico-signal-dark)' }} aria-hidden="true" />
          <span>Crítico</span>
        </div>
      </div>

      {/* ── Tooltip (portal simples via fixed) ────────────────────────────── */}
      {tooltip.visible && tooltip.criterion && (
        <CriterionTooltip
          criterion={tooltip.criterion}
          style={{
            left: tooltip.x,
            top: tooltip.y,
            transform: 'translate(-50%, -100%)',
          }}
        />
      )}
    </div>
  );
}
