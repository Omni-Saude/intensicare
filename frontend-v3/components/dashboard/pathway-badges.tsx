'use client';

import type { SeverityLevel } from '@/lib/api';

const SEVERITY_VAR: Record<SeverityLevel, string> = {
  normal: 'var(--severity-normal)',
  watch: 'var(--severity-watch)',
  urgent: 'var(--severity-urgent)',
  critical: 'var(--severity-critical)',
};

interface PathwayBadge {
  slug: string;
  severity: SeverityLevel;
}

interface PathwayBadgesProps {
  pathways: PathwayBadge[];
}

const MAX_VISIBLE = 3;

export function PathwayBadges({ pathways }: PathwayBadgesProps) {
  if (!pathways || pathways.length === 0) return null;

  const visible = pathways.slice(0, MAX_VISIBLE);
  const remaining = pathways.length - MAX_VISIBLE;

  return (
    <div className="flex items-center gap-1" role="list" aria-label="Trilhas ativas">
      {visible.map((p) => (
        <span
          key={p.slug}
          role="listitem"
          aria-label={`Trilha ${p.slug}, severidade ${p.severity}`}
          className="inline-block size-3 shrink-0 rounded-full"
          style={{ backgroundColor: SEVERITY_VAR[p.severity] }}
        />
      ))}
      {remaining > 0 && (
        <span
          role="listitem"
          aria-label={`Mais ${remaining} trilhas`}
          // RF-015 fix (GK-RESP): at size-3 (12px) the "+N" digit's intrinsic
          // glyph ink box (~13px tall/14px wide even with leading-none — a
          // font-metrics floor, not a line-height cascade issue: measured
          // computed line-height is 11px, so leading-none already wins over
          // --text-2xs--line-height's 16px token here) pokes ~0.5px past the
          // circle vertically and ~1px past it horizontally. Sized measured
          // via scratchpad/badge-measure.mjs against a live dev server:
          // size-3.5 (14px) is the smallest step that fully contains the
          // digit (0px overflow both axes) — forcing line-height further
          // (e.g. an arbitrary [line-height:1]) is a no-op since leading-none
          // already sets it, confirmed by measurement.
          className="inline-flex items-center justify-center size-3.5 shrink-0 rounded-full text-2xs leading-none font-medium"
          style={{
            backgroundColor: 'var(--surface-overlay)',
            color: 'var(--text-secondary)',
          }}
        >
          +{remaining}
        </span>
      )}
    </div>
  );
}
