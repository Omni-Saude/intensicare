'use client';

import React, { useState } from 'react';
import {
  ChevronDown, ChevronUp, Droplets, TrendingUp, TrendingDown,
  Minus, Coffee, Syringe, Pill, FlaskConical, Activity,
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface FluidBalanceData {
  intake: { oral: number; iv: number; enteral: number };
  output: { urine: number; drain: number; stool: number };
  target24h?: number;
}

interface FluidBalanceSummaryProps {
  data: FluidBalanceData;
  className?: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtVol(mL: number): string {
  return Math.abs(mL) >= 1000 ? `${(mL / 1000).toFixed(1)} L` : `${mL} mL`;
}

type Bal = 'positive' | 'negative' | 'balanced';
function balStatus(b: number): Bal {
  return b > 250 ? 'positive' : b < -250 ? 'negative' : 'balanced';
}

// ─── Sub-component: proportional bar row ──────────────────────────────────────

function BarRow({
  label, volume, total, icon: Icon, color,
}: {
  label: string; volume: number; total: number;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>; color: string;
}) {
  const pct = total > 0 ? (volume / total) * 100 : 0;
  return (
    <div className="flex items-center gap-2 text-xs">
      <Icon className="w-3.5 h-3.5 flex-shrink-0" style={{ color }} />
      <span className="w-14 flex-shrink-0 truncate" style={{ color: 'var(--semantic-text-secondary)' }}>{label}</span>
      <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--semantic-border-default)' }}>
        <div className="h-full rounded-full transition-all duration-300" style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }} />
      </div>
      <span className="w-14 text-right tabular-nums flex-shrink-0" style={{ color: 'var(--semantic-text-primary)' }}>{fmtVol(volume)}</span>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function FluidBalanceSummary({ data, className = '' }: FluidBalanceSummaryProps) {
  const [expanded, setExpanded] = useState(false);

  const totalIn = data.intake.oral + data.intake.iv + data.intake.enteral;
  const totalOut = data.output.urine + data.output.drain + data.output.stool;
  const balance = totalIn - totalOut;
  const status = balStatus(balance);

  const grand = totalIn + totalOut;
  const inPct = grand > 0 ? (totalIn / grand) * 100 : 50;
  const outPct = grand > 0 ? (totalOut / grand) * 100 : 50;

  const target = data.target24h ?? 0;
  const targetPct = target > 0 && totalIn > 0 ? (target / totalIn) * 100 : 0;

  // Color tokens
  const cIn = 'var(--clinical-status-attended-color)';
  const cOut = 'var(--clinical-severity-urgent-on-surface)';
  const barIn = 'rgba(76,159,232,0.7)';
  const barOut = 'rgba(249,111,6,0.6)';

  // Balance config
  const balCfg: Record<Bal, { icon: typeof TrendingUp; label: string; c: string }> = {
    positive: { icon: TrendingUp, label: 'Positivo', c: 'var(--clinical-severity-urgent-on-surface)' },
    negative: { icon: TrendingDown, label: 'Negativo', c: 'var(--clinical-severity-critical-on-surface)' },
    balanced:  { icon: Minus, label: 'Balanceado', c: 'var(--clinical-severity-normal-on-surface)' },
  };
  const BalIcon = balCfg[status].icon;

  return (
    <div
      className={`rounded-lg border p-4 ${className}`}
      style={{ backgroundColor: 'var(--semantic-surface-raised)', borderColor: 'var(--semantic-border-default)' }}
    >
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Droplets className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} />
          <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--semantic-text-secondary)' }}>
            Balanço Hídrico
          </span>
        </div>
        <span className="text-xs font-medium px-2 py-0.5 rounded-full"
          style={{ backgroundColor: 'var(--semantic-border-default)', color: 'var(--semantic-text-secondary)' }}>
          Plantão 07:00 – 07:00
        </span>
      </div>

      {/* ── Intake / Output bars ── */}
      <div className="mb-3 space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5" style={{ color: cIn }} />
            <span style={{ color: 'var(--semantic-text-secondary)' }}>Ganhos</span>
            <span className="font-semibold tabular-nums" style={{ color: 'var(--semantic-text-primary)' }}>{fmtVol(totalIn)}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-semibold tabular-nums" style={{ color: 'var(--semantic-text-primary)' }}>{fmtVol(totalOut)}</span>
            <span style={{ color: 'var(--semantic-text-secondary)' }}>Perdas</span>
            <FlaskConical className="w-3.5 h-3.5" style={{ color: cOut }} />
          </div>
        </div>
        <div className="flex h-4 rounded-full overflow-hidden" role="meter" aria-label={`Ganhos ${totalIn} mL, Perdas ${totalOut} mL`}>
          <div className="h-full transition-all duration-300 flex items-center justify-end pr-1" style={{ width: `${inPct}%`, backgroundColor: barIn }}>
            {inPct > 20 && <span className="text-[10px] font-semibold text-white/90 tabular-nums">{fmtVol(totalIn)}</span>}
          </div>
          <div className="h-full transition-all duration-300 flex items-center pl-1" style={{ width: `${outPct}%`, backgroundColor: barOut }}>
            {outPct > 20 && <span className="text-[10px] font-semibold text-white/90 tabular-nums">{fmtVol(totalOut)}</span>}
          </div>
        </div>
      </div>

      {/* ── 24h Target line ── */}
      {target > 0 && (
        <div className="mb-3 relative" aria-label={`Meta 24h: ${fmtVol(target)}`}>
          <div className="absolute border-l-2 border-dashed h-4"
            style={{ left: `${Math.min(targetPct, 100)}%`, borderColor: 'var(--semantic-text-secondary)', opacity: 0.5 }} />
          <div style={{ paddingLeft: `${Math.min(targetPct, 100)}%` }}>
            <span className="text-[10px] pl-1" style={{ color: 'var(--semantic-text-secondary)', opacity: 0.6 }}>
              Meta {fmtVol(target)}
            </span>
          </div>
        </div>
      )}

      {/* ── Cumulative balance ── */}
      <div className="flex items-center gap-1.5 mb-2" aria-label={`Balanço acumulado: ${balCfg[status].label}, ${fmtVol(balance)}`}>
        <BalIcon className="w-4 h-4" color={balCfg[status].c} />
        <span className="text-sm font-semibold tabular-nums" style={{ color: balCfg[status].c }}>{fmtVol(balance)}</span>
        <span className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>{balCfg[status].label}</span>
      </div>

      {/* ── Expand toggle ── */}
      <button
        onClick={() => setExpanded(p => !p)}
        className="flex items-center gap-1 text-xs w-full py-1.5 rounded-md hover:opacity-80 transition-opacity"
        style={{ color: 'var(--semantic-text-secondary)' }}
        aria-expanded={expanded} aria-controls="fluid-detail"
      >
        {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        {expanded ? 'Ocultar detalhamento' : 'Ver detalhamento'}
      </button>

      {/* ── Expandable details ── */}
      {expanded && (
        <div id="fluid-detail" className="pt-2 border-t space-y-3" style={{ borderColor: 'var(--semantic-border-default)' }}>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--semantic-text-secondary)' }}>Ganhos</span>
            <div className="mt-1.5 space-y-1.5">
              <BarRow label="Oral" volume={data.intake.oral} total={totalIn} icon={Coffee} color={cIn} />
              <BarRow label="Endovenoso" volume={data.intake.iv} total={totalIn} icon={Syringe} color={cIn} />
              <BarRow label="Enteral" volume={data.intake.enteral} total={totalIn} icon={Pill} color={cIn} />
            </div>
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--semantic-text-secondary)' }}>Perdas</span>
            <div className="mt-1.5 space-y-1.5">
              <BarRow label="Diurese" volume={data.output.urine} total={totalOut} icon={FlaskConical} color={cOut} />
              <BarRow label="Drenos" volume={data.output.drain} total={totalOut} icon={Droplets} color={cOut} />
              <BarRow label="Fezes" volume={data.output.stool} total={totalOut} icon={Activity} color={cOut} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
