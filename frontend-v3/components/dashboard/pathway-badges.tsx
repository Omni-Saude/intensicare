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
          className="inline-flex items-center justify-center size-3 shrink-0 rounded-full text-[8px] leading-none font-medium"
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
