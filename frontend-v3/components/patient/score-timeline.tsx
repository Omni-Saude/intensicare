'use client';

import type { ScoreRecord } from '@/lib/api';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

// ---------- Lightweight SVG Sparkline (no recharts dependency) ----------

function Sparkline({
  data,
  alertTimes,
}: {
  data: { value: number; time: string; measured_at: string }[];
  alertTimes?: string[];
}) {
  if (data.length < 2) {
    return (
      <div className="flex items-center justify-center h-[130px] text-xs text-[var(--text-secondary)]">
        Dados insuficientes para o gráfico
      </div>
    );
  }

  const values = data.map((d) => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const width = 600;
  const height = 130;
  const padX = 10;
  const padY = 10;
  const drawW = width - padX * 2;
  const drawH = height - padY * 2;

  const points = data.map((d, i) => {
    const x = padX + (i / (data.length - 1)) * drawW;
    const y = padY + drawH - ((d.value - min) / range) * drawH;
    return `${x},${y}`;
  });

  const isNearAlert = (measuredAt: string): boolean => {
    if (!alertTimes || alertTimes.length === 0) return false;
    const t = new Date(measuredAt).getTime();
    return alertTimes.some((at) => Math.abs(t - new Date(at).getTime()) <= 30 * 60 * 1000);
  };

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full h-[130px]"
      role="img"
      aria-label="Gráfico de evolução dos scores"
    >
      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
        const y = padY + drawH * (1 - pct);
        return (
          <line
            key={pct}
            x1={padX}
            y1={y}
            x2={padX + drawW}
            y2={y}
            stroke="var(--border-default)"
            strokeWidth={0.5}
            strokeDasharray="3 3"
          />
        );
      })}

      {/* Area fill */}
      <polygon
        points={`${padX},${padY + drawH} ${points.join(' ')} ${padX + drawW},${padY + drawH}`}
        fill="var(--severity-watch-wash)"
        opacity={0.3}
      />

      {/* Line */}
      <polyline
        points={points.join(' ')}
        fill="none"
        stroke="var(--severity-watch)"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Dots */}
      {data.map((d, i) => {
        const x = padX + (i / (data.length - 1)) * drawW;
        const y = padY + drawH - ((d.value - min) / range) * drawH;
        const alert = isNearAlert(d.measured_at);
        return alert ? (
          <circle
            key={i}
            cx={x}
            cy={y}
            r={5}
            fill="var(--severity-critical)"
            stroke="var(--surface-raised)"
            strokeWidth={2}
          >
            <title>{`Alerta: ${d.value}`}</title>
          </circle>
        ) : (
          <circle
            key={i}
            cx={x}
            cy={y}
            r={2.5}
            fill="var(--severity-watch)"
            stroke="var(--surface-raised)"
            strokeWidth={1}
          />
        );
      })}
    </svg>
  );
}

// ---------- Score timeline ----------

interface ScoreTimelineProps {
  scores: ScoreRecord[];
  alertTimes?: string[];
  isLoading?: boolean;
  error?: string | null;
}

function scoreColor(scoreName: string, value: number): string {
  if (scoreName === 'MEWS' || scoreName === 'NEWS2') {
    if (value >= 7) return 'var(--severity-critical)';
    if (value >= 5) return 'var(--severity-urgent)';
    if (value >= 3) return 'var(--severity-watch)';
    return 'var(--severity-normal)';
  }
  return 'var(--text-primary)';
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  });
}

function TrendIcon({ trend }: { trend?: string }) {
  if (!trend) return null;
  const cls = 'h-3.5 w-3.5';
  switch (trend) {
    case 'up':
      return <TrendingUp className={cls} style={{ color: 'var(--severity-urgent)' }} aria-label="Tendência de alta" />;
    case 'down':
      return <TrendingDown className={cls} style={{ color: 'var(--severity-normal)' }} aria-label="Tendência de baixa" />;
    default:
      return <Minus className={cls} style={{ color: 'var(--text-secondary)' }} aria-label="Estável" />;
  }
}

export function ScoreTimeline({ scores, alertTimes, isLoading, error }: ScoreTimelineProps) {
  const [selectedScore, setSelectedScore] = useState<string>('MEWS');

  const scoreNames = [...new Set(scores.map((s) => s.name))];
  const active = selectedScore || scoreNames[0] || 'MEWS';

  // Chart data (sorted ascending)
  const chartData = scores
    .filter((s) => s.name === active)
    .sort((a, b) => new Date(a.measured_at).getTime() - new Date(b.measured_at).getTime())
    .map((s) => ({
      time: formatTime(s.measured_at),
      value: s.value,
      measured_at: s.measured_at,
    }));

  // Table data (most recent first)
  const tableData = scores
    .filter((s) => s.name === active)
    .sort((a, b) => new Date(b.measured_at).getTime() - new Date(a.measured_at).getTime())
    .slice(0, 20);

  return (
    <section aria-label="Histórico de scores" className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
          Scores
        </h2>

        {scoreNames.length > 1 && (
          <div className="flex gap-1 rounded-lg bg-[var(--surface-overlay)] p-1" role="tablist" aria-label="Selecionar score">
            {scoreNames.map((name) => (
              <button
                key={name}
                role="tab"
                aria-selected={active === name}
                onClick={() => setSelectedScore(name)}
                className={cn(
                  'rounded-md px-3 py-1 text-xs font-medium transition-colors',
                  active === name
                    ? 'bg-[var(--surface-raised)] text-[var(--text-primary)] shadow-sm'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
                )}
              >
                {name}
              </button>
            ))}
          </div>
        )}
      </div>

      {isLoading && (
        <div className="space-y-3">
          <div className="h-[150px] animate-pulse rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]" />
          <div className="h-[200px] animate-pulse rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]" />
        </div>
      )}

      {error && (
        <div
          className="rounded-lg border border-[var(--severity-critical)] bg-[var(--severity-critical-wash)] p-4 text-sm text-[var(--severity-critical)]"
          role="alert"
        >
          Erro ao carregar scores: {error}
        </div>
      )}

      {!isLoading && !error && scores.length === 0 && (
        <div className="rounded-lg border border-dashed border-[var(--border-default)] bg-[var(--surface-raised)] p-6 text-center text-sm text-[var(--text-secondary)]">
          Nenhum score registrado para este paciente.
        </div>
      )}

      {!isLoading && !error && chartData.length > 0 && (
        <>
          {/* Sparkline */}
          <div className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-3">
            <Sparkline data={chartData} alertTimes={alertTimes} />
          </div>

          {/* Table */}
          <div className="overflow-hidden rounded-lg border border-[var(--border-default)]">
            <table className="w-full text-sm" aria-label={`Tabela de valores de ${active}`}>
              <thead>
                <tr className="border-b border-[var(--border-default)] bg-[var(--surface-overlay)]">
                  <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-secondary)]">
                    Data/Hora
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-secondary)]">
                    Valor
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-[var(--text-secondary)]">
                    Tendência
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-default)]">
                {tableData.map((s, i) => (
                  <tr
                    key={`${s.measured_at}-${i}`}
                    className="hover:bg-[var(--surface-overlay)] transition-colors"
                  >
                    <td className="px-4 py-2 text-[var(--text-secondary)] whitespace-nowrap">
                      {formatTime(s.measured_at)}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className="font-semibold tabular-nums"
                        style={{ color: scoreColor(active, s.value) }}
                      >
                        {s.value}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <TrendIcon trend={s.trend} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!isLoading && !error && chartData.length === 0 && scores.length > 0 && (
        <div className="rounded-lg border border-dashed border-[var(--border-default)] bg-[var(--surface-raised)] p-6 text-center text-sm text-[var(--text-secondary)]">
          Nenhum dado para o score &quot;{active}&quot;.
        </div>
      )}
    </section>
  );
}
