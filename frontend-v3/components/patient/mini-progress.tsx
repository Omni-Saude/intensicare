'use client';

interface MiniProgressProps {
  met: number;
  total: number;
  label?: string;
}

export function MiniProgress({ met, total, label }: MiniProgressProps) {
  const pct = total > 0 ? Math.round((met / total) * 100) : 0;

  return (
    <div className="flex items-center gap-2" role="progressbar" aria-valuenow={met} aria-valuemin={0} aria-valuemax={total} aria-label={label ?? `Progresso: ${met} de ${total} critérios atendidos`}>
      <div className="h-1.5 flex-1 rounded-full bg-[var(--surface-overlay)] overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${pct}%`,
            backgroundColor: pct >= 80 ? 'var(--severity-normal)' : pct >= 50 ? 'var(--severity-watch)' : 'var(--severity-urgent)',
          }}
        />
      </div>
      <span className="text-xs text-[var(--text-secondary)] whitespace-nowrap tabular-nums">
        {met}/{total}
      </span>
    </div>
  );
}
