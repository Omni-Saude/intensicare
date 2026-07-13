'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { useRouter } from 'next/navigation';
import { fetchDashboard } from '@/lib/api';
import { useRealtimeChannel } from '@/lib/websocket';
import { BedGrid } from '@/components/dashboard/bed-grid';
import { StatsBar } from '@/components/dashboard/stats-bar';
import { UnitFilter } from '@/components/dashboard/unit-filter';

export default function DashboardPage() {
  const router = useRouter();
  const [unit, setUnit] = useState<string | null>(null);

  // RF-020: a chave SWR muda a cada troca do filtro de unidade. Sem
  // `keepPreviousData`, a UI cai num re-render vazio/skeleton intermediário
  // enquanto o novo fetch está em voo, colapsando a altura da página e
  // perdendo a posição de scroll do intensivista (Nielsen #3 — User Control
  // and Freedom). Manter os dados anteriores visíveis até a nova página
  // chegar resolve na raiz, sem precisar restaurar scroll artificialmente.
  const { data, error, isLoading, mutate } = useSWR(
    ['dashboard', unit],
    () => fetchDashboard(unit ?? undefined),
    { keepPreviousData: true },
  );

  // `isLoading` do SWR é por-chave: ele volta a `true` a cada troca de
  // unidade mesmo com `keepPreviousData`, porque a nova chave ainda não tem
  // cache próprio — só `data` (via `laggyDataRef`) continua com o valor
  // anterior. Gatear o skeleton por "ainda não há dado nenhum" (em vez do
  // `isLoading` cru) é o que efetivamente mantém a grade anterior visível
  // durante o refetch do filtro.
  const showSkeleton = isLoading && !data;

  // Realtime: WebSocket + polling fallback (ADR-0034)
  useRealtimeChannel('bed_grid.updated', () => mutate(), { fallbackInterval: 30_000 });
  useRealtimeChannel('alert.raised', () => mutate(), { fallbackInterval: 30_000 });

  const units = data?.unit_counts ? Object.keys(data.unit_counts) : [];

  return (
    <div className="flex flex-col gap-6">
      <h1 className="sr-only">Dashboard</h1>

      {/* Stats bar */}
      {data && (
        <StatsBar
          total={data.total}
          criticalCount={data.critical_count}
          unit={unit ?? undefined}
        />
      )}

      {/* Unit filter */}
      {units.length > 0 && (
        <UnitFilter
          units={units}
          selected={unit}
          onChange={(newUnit) => setUnit(newUnit)}
        />
      )}

      {/* Bed grid — handles loading / empty / error internally */}
      <BedGrid
        patients={data?.patients ?? []}
        onSelect={(mpiId) => router.push(`/patient/${mpiId}`)}
        isLoading={showSkeleton}
        error={error}
        onRetry={() => mutate()}
      />
    </div>
  );
}
