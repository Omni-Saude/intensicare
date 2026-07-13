'use client';

function scoreColor(value: number): string {
  if (value >= 7) return 'var(--severity-critical)';
  if (value >= 5) return 'var(--severity-urgent)';
  return 'var(--text-primary)';
}

// Clinical tooltip text per score, built from the score's own value (never
// hardcoded patient data). ">=5" thresholds follow the published scales:
//   MEWS  — Subbe et al. 2001, "Validation of a modified early warning
//           score in medical admissions".
//   NEWS2 — Royal College of Physicians, 2017 (National Early Warning
//           Score 2).
function mewsTooltip(value: number): string {
  const risk = value >= 5 ? 'risco elevado' : 'risco baixo/moderado';
  return `MEWS ${value} — Modified Early Warning Score (Subbe 2001); ≥5 = risco elevado (atual: ${risk})`;
}

function news2Tooltip(value: number): string {
  const risk = value >= 5 ? 'risco elevado' : 'risco baixo/moderado';
  return `NEWS2 ${value} — National Early Warning Score 2 (RCP 2017); ≥5 = risco elevado (atual: ${risk})`;
}

interface ScorePairProps {
  mews: number | null;
  news2: number | null;
}

export function ScorePair({ mews, news2 }: ScorePairProps) {
  if (mews == null && news2 == null) return null;

  const parts: string[] = [];
  const tooltips: string[] = [];

  if (mews != null) {
    parts.push(`MEWS ${mews}`);
    tooltips.push(mewsTooltip(mews));
  }
  if (news2 != null) {
    parts.push(`NEWS2 ${news2}`);
    tooltips.push(news2Tooltip(news2));
  }

  // Determine the highest severity color across both scores
  const maxScore = Math.max(mews ?? 0, news2 ?? 0);
  const color = scoreColor(maxScore);
  const title = tooltips.join(' | ');

  return (
    <div
      className="font-mono text-xs tracking-tight"
      style={{ color }}
      aria-label={title}
      title={title}
    >
      {parts.join(' • ')}
    </div>
  );
}
