'use client';

function scoreColor(value: number): string {
  if (value >= 7) return 'var(--severity-critical)';
  if (value >= 5) return 'var(--severity-urgent)';
  return 'var(--text-primary)';
}

interface ScorePairProps {
  mews: number | null;
  news2: number | null;
}

export function ScorePair({ mews, news2 }: ScorePairProps) {
  if (mews == null && news2 == null) return null;

  const parts: string[] = [];

  if (mews != null) parts.push(`MEWS ${mews}`);
  if (news2 != null) parts.push(`NEWS2 ${news2}`);

  // Determine the highest severity color across both scores
  const maxScore = Math.max(mews ?? 0, news2 ?? 0);
  const color = scoreColor(maxScore);

  return (
    <div
      className="font-mono text-xs tracking-tight"
      style={{ color }}
      aria-label={parts.join(', ')}
    >
      {parts.join(' • ')}
    </div>
  );
}
