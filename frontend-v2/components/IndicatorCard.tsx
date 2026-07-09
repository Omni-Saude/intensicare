'use client';

import React from 'react';
import { TrendingDown, TrendingUp, Minus } from 'lucide-react';
import type { Indicator, Trend } from '@/lib/indicators-types';
import {
  TREND_LABELS,
  TREND_ICONS,
  CATEGORY_LABELS,
  CATEGORY_COLORS,
  CATEGORY_BG_COLORS,
  formatValue,
  getTrendColor,
  isWithinRange,
  getRangePercentage,
} from '@/lib/indicators-types';

// ─── Props ────────────────────────────────────────────────────────────────────

interface IndicatorCardProps {
  indicator: Indicator;
  onClick?: (indicator: Indicator) => void;
  isLoading?: boolean;
}

// ─── Trend Badge (reutilizável inline) ────────────────────────────────────────

function TrendBadgeInline({ trend }: { trend: Trend }) {
  const Icon = TREND_ICONS[trend];
  const color = getTrendColor(trend);
  const label = TREND_LABELS[trend];

  return (
    <span
      className="inline-flex items-center gap-1 text-xs font-medium"
      style={{ color }}
      title={label}
      aria-label={`Tendência: ${label}`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
    </span>
  );
}

// ─── Skeleton Card ────────────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div
      className="rounded-xl border-2 p-5 animate-pulse"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      {/* Category badge skeleton */}
      <div className="flex items-center justify-between mb-3">
        <div
          className="h-5 rounded-full w-16"
          style={{ backgroundColor: 'var(--semantic-border-default)' }}
        />
        <div
          className="h-5 rounded-full w-20"
          style={{ backgroundColor: 'var(--semantic-border-default)' }}
        />
      </div>

      {/* Name skeleton */}
      <div
        className="h-4 rounded w-3/4 mb-3"
        style={{ backgroundColor: 'var(--semantic-border-default)' }}
      />

      {/* Value skeleton */}
      <div
        className="h-8 rounded w-1/3 mb-4"
        style={{ backgroundColor: 'var(--semantic-border-default)' }}
      />

      {/* Progress bar skeleton */}
      <div
        className="h-2 rounded-full w-full"
        style={{ backgroundColor: 'var(--semantic-border-default)' }}
      />

      {/* Target skeleton */}
      <div className="flex items-center justify-between mt-3">
        <div
          className="h-3 rounded w-24"
          style={{ backgroundColor: 'var(--semantic-border-default)' }}
        />
        <div
          className="h-3 rounded w-16"
          style={{ backgroundColor: 'var(--semantic-border-default)' }}
        />
      </div>
    </div>
  );
}

// ─── IndicatorCard ────────────────────────────────────────────────────────────

export default function IndicatorCard({
  indicator,
  onClick,
  isLoading,
}: IndicatorCardProps) {
  if (isLoading) {
    return <SkeletonCard />;
  }

  const { name, category, current_value, target, trend, unit, reference_range } =
    indicator;

  const inRange = isWithinRange(current_value, reference_range);
  const rangePct = getRangePercentage(current_value, reference_range);
  const categoryColor = CATEGORY_COLORS[category];
  const categoryBg = CATEGORY_BG_COLORS[category];
  const categoryLabel = CATEGORY_LABELS[category];

  const progressColor = inRange
    ? 'var(--clinical-severity-normal-signal)'
    : 'var(--clinical-severity-critical-signal)';

  const progressBgColor = inRange
    ? 'var(--clinical-severity-normal-wash)'
    : 'var(--clinical-severity-critical-wash)';

  const isClickable = !!onClick;

  const cardContent = (
    <div
      className={`rounded-xl border-2 p-5 transition-all ${
        isClickable
          ? 'hover:shadow-lg hover:scale-[1.02] cursor-pointer focus-visible:ring-2 focus-visible:ring-blue-500'
          : ''
      }`}
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
    >
      {/* Top row: category badge + trend */}
      <div className="flex items-center justify-between mb-3">
        <span
          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
          style={{
            backgroundColor: categoryBg,
            color: categoryColor,
          }}
        >
          {categoryLabel}
        </span>
        <TrendBadgeInline trend={trend} />
      </div>

      {/* Indicator name */}
      <h3
        className="text-sm font-medium mb-2 truncate"
        style={{ color: 'var(--semantic-text-secondary)' }}
        title={name}
      >
        {name}
      </h3>

      {/* Value + unit */}
      <div className="flex items-baseline gap-1.5 mb-4">
        <span
          className="text-3xl font-bold"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {formatValue(current_value, unit)}
        </span>
      </div>

      {/* Progress bar */}
      <div className="relative w-full h-2 rounded-full overflow-hidden mb-2" style={{ backgroundColor: progressBgColor }}>
        {/* Reference range markers */}
        <div className="absolute inset-0 flex">
          <div className="h-full w-1/5 border-r border-white/30" />
          <div className="h-full w-1/5 border-r border-white/30" />
          <div className="h-full w-1/5 border-r border-white/30" />
          <div className="h-full w-1/5 border-r border-white/30" />
          <div className="h-full w-1/5" />
        </div>
        {/* Value indicator */}
        <div
          className="absolute top-0 left-0 h-full rounded-full transition-all duration-500"
          style={{
            width: `${rangePct}%`,
            backgroundColor: progressColor,
          }}
        />
      </div>

      {/* Range labels */}
      <div className="flex items-center justify-between text-[10px] mb-3" style={{ color: 'var(--semantic-text-secondary)' }}>
        <span>{reference_range.low}{unit === 'eventos/1000' ? '' : unit}</span>
        <span>{reference_range.high}{unit === 'eventos/1000' ? '' : unit}</span>
      </div>

      {/* Target */}
      {target !== undefined && target !== null && (
        <div
          className="flex items-center justify-between text-xs pt-2 border-t"
          style={{ borderColor: 'var(--semantic-border-default)' }}
        >
          <span style={{ color: 'var(--semantic-text-secondary)' }}>Meta</span>
          <span
            className={`font-semibold ${
              current_value <= target
                ? 'text-[var(--clinical-severity-normal-on-surface)]'
                : 'text-[var(--clinical-severity-critical-on-surface)]'
            }`}
            style={{
              color:
                // For metrics where lower is better (rates, events/1000)
                unit === 'eventos/1000' || unit === '%'
                  ? current_value <= target
                    ? 'var(--clinical-severity-normal-on-surface)'
                    : 'var(--clinical-severity-critical-on-surface)'
                  : // For occupancy and other metrics where higher can be target
                  current_value >= target
                  ? 'var(--clinical-severity-normal-on-surface)'
                  : 'var(--clinical-severity-critical-on-surface)',
            }}
          >
            {formatValue(target, unit)}
          </span>
        </div>
      )}
    </div>
  );

  if (isClickable) {
    return (
      <button
        onClick={() => onClick?.(indicator)}
        className="w-full text-left focus:outline-none"
        aria-label={`Indicador ${name}: ${formatValue(current_value, unit)}`}
      >
        {cardContent}
      </button>
    );
  }

  return cardContent;
}
