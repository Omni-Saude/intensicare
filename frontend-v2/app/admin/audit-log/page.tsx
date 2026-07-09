'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table';
import {
  Search,
  Filter,
  Download,
  Eye,
  Shield,
  ChevronLeft,
  ChevronRight,
  X,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import DrawerBuilder from '@/components/DrawerBuilder';
import { fetchAuditLogs } from '@/lib/api';
import {
  type AuditLogEntry,
  type AuditAction,
  type AuditLogFilter,
  ACTION_LABELS,
  ACTION_COLORS,
  formatDateTime,
  formatRelativeTime,
} from '@/lib/audit-types';

// ─── Column Helper ────────────────────────────────────────────────────────

const columnHelper = createColumnHelper<AuditLogEntry>();

const columns = [
  columnHelper.accessor('event_ts', {
    header: 'Data/Hora',
    cell: (info) => (
      <div className="flex flex-col">
        <span
          className="text-sm font-medium whitespace-nowrap"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {formatDateTime(info.getValue())}
        </span>
        <span
          className="text-xs whitespace-nowrap"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {formatRelativeTime(info.getValue())}
        </span>
      </div>
    ),
    sortingFn: 'datetime',
  }),
  columnHelper.accessor('actor', {
    header: 'Ator',
    cell: (info) => (
      <span
        className="text-sm font-medium"
        style={{ color: 'var(--semantic-text-primary)' }}
      >
        {info.getValue()}
      </span>
    ),
  }),
  columnHelper.accessor('action', {
    header: 'Ação',
    cell: (info) => {
      const action = info.getValue();
      const colors = ACTION_COLORS[action];
      return (
        <span
          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
          style={{
            backgroundColor: colors.bg,
            color: colors.text,
            border: `1px solid ${colors.border}`,
          }}
        >
          {ACTION_LABELS[action]}
        </span>
      );
    },
  }),
  columnHelper.accessor('entity_table', {
    header: 'Entidade',
    cell: (info) => (
      <span
        className="text-sm font-mono"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {info.getValue()}
      </span>
    ),
  }),
  columnHelper.accessor('entity_id', {
    header: 'ID Entidade',
    cell: (info) => (
      <span
        className="text-sm font-mono text-xs"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {info.getValue()}
      </span>
    ),
  }),
  columnHelper.accessor('mpi_id', {
    header: 'MPI',
    cell: (info) => {
      const val = info.getValue();
      if (!val) {
        return (
          <span
            className="text-sm italic"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            —
          </span>
        );
      }
      return (
        <span
          className="text-sm font-mono"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {val}
        </span>
      );
    },
  }),
  columnHelper.display({
    id: 'actions',
    header: 'Ações',
    cell: (info) => (
      <button
        onClick={(e) => {
          e.stopPropagation();
          const onView = (info.table.options.meta as { onView?: (log: AuditLogEntry) => void })?.onView;
          onView?.(info.row.original);
        }}
        className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium transition-colors hover:opacity-80 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
        style={{
          backgroundColor: 'var(--feedback-info-bg-dark)',
          color: 'var(--feedback-info-text-dark)',
          border: '1px solid var(--feedback-info-border-dark)',
        }}
        aria-label="Ver detalhes"
        title="Ver detalhes"
      >
        <Eye className="w-3.5 h-3.5" aria-hidden="true" />
        Detalhes
      </button>
    ),
  }),
];

// ─── Page Component ───────────────────────────────────────────────────────

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);

  // Filtros
  const [filterActor, setFilterActor] = useState('');
  const [filterAction, setFilterAction] = useState<AuditAction | ''>('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');

  // ── Fetch from API ───────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchAuditLogs()
      .then((data: { logs: unknown[]; total: number }) => {
        if (cancelled) return;
        setLogs(data.logs as AuditLogEntry[]);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Erro ao carregar registros de auditoria');
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Filtragem dos dados
  const filteredLogs = useMemo(() => {
    let result = [...logs];

    // Ordenar por event_ts DESC (mais recentes primeiro)
    result.sort(
      (a, b) => new Date(b.event_ts).getTime() - new Date(a.event_ts).getTime(),
    );

    if (filterActor.trim()) {
      const q = filterActor.trim().toLowerCase();
      result = result.filter((l) => l.actor.toLowerCase().includes(q));
    }

    if (filterAction) {
      result = result.filter((l) => l.action === filterAction);
    }

    if (filterDateFrom) {
      const from = new Date(filterDateFrom + 'T00:00:00').getTime();
      result = result.filter((l) => new Date(l.event_ts).getTime() >= from);
    }

    if (filterDateTo) {
      const to = new Date(filterDateTo + 'T23:59:59').getTime();
      result = result.filter((l) => new Date(l.event_ts).getTime() <= to);
    }

    return result;
  }, [logs, filterActor, filterAction, filterDateFrom, filterDateTo]);

  const hasFilters =
    filterActor.trim() !== '' ||
    filterAction !== '' ||
    filterDateFrom !== '' ||
    filterDateTo !== '';

  const clearFilters = () => {
    setFilterActor('');
    setFilterAction('');
    setFilterDateFrom('');
    setFilterDateTo('');
  };

  // TanStack Table
  const table = useReactTable({
    data: filteredLogs,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 10 },
    },
    meta: {
      onView: (log: AuditLogEntry) => setSelectedLog(log),
    },
  });

  // Export CSV – download real via Blob + URL.createObjectURL
  const handleExport = () => {
    const escapeCSV = (val: string): string => {
      if (val.includes(',') || val.includes('"') || val.includes('\n')) {
        return `"${val.replace(/"/g, '""')}"`;
      }
      return val;
    };

    const headers = [
      'id',
      'event_ts',
      'tenant_id',
      'actor',
      'action',
      'entity_table',
      'entity_id',
      'mpi_id',
      'request_id',
    ];

    const rows = filteredLogs.map((l) =>
      [
        escapeCSV(String(l.id)),
        escapeCSV(l.event_ts),
        escapeCSV(l.tenant_id ?? ''),
        escapeCSV(l.actor),
        escapeCSV(l.action),
        escapeCSV(l.entity_table),
        escapeCSV(l.entity_id),
        escapeCSV(l.mpi_id ?? ''),
        escapeCSV(l.request_id ?? ''),
      ].join(','),
    );

    const csv = [headers.join(','), ...rows].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const today = new Date().toISOString().slice(0, 10);
    link.download = `auditoria-intensicare-${today}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // ─── Render ───────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" aria-hidden="true" />
              </div>
              <div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Trilha de Auditoria
                </h1>
                <p
                  className="text-sm mt-0.5"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Registro imutável de ações clínicas e administrativas
                </p>
              </div>
            </div>

            {/* Botão Exportar */}
            <div className="flex justify-end">
              <button
                onClick={handleExport}
                disabled={filteredLogs.length === 0}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80 disabled:opacity-40 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                style={{
                  backgroundColor: 'var(--feedback-warning-bg-dark)',
                  color: 'var(--feedback-warning-text-dark)',
                  border: '1px solid var(--feedback-warning-border-dark)',
                }}
              >
                <Download className="w-4 h-4" aria-hidden="true" />
                Exportar CSV
              </button>
            </div>
          </div>

          {/* Barra de Filtros */}
          <div
            className="rounded-xl border p-4 mb-6"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              borderColor: 'var(--semantic-border-default)',
            }}
          >
            <div className="flex flex-wrap items-end gap-3">
              {/* Busca por Ator */}
              <div className="flex-1 min-w-[180px]">
                <label
                  className="block text-xs font-medium mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  htmlFor="filter-actor"
                >
                  Buscar ator
                </label>
                <div className="relative">
                  <Search
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                    aria-hidden="true"
                  />
                  <input
                    id="filter-actor"
                    type="text"
                    value={filterActor}
                    onChange={(e) => setFilterActor(e.target.value)}
                    placeholder="Nome do usuário..."
                    className="w-full pl-9 pr-3 py-2 rounded-lg text-sm border focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
                    style={{
                      backgroundColor: 'var(--semantic-surface-canvas)',
                      color: 'var(--semantic-text-primary)',
                      borderColor: 'var(--semantic-border-default)',
                    }}
                  />
                </div>
              </div>

              {/* Filtro por Ação */}
              <div className="min-w-[160px]">
                <label
                  className="block text-xs font-medium mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  htmlFor="filter-action"
                >
                  <Filter className="w-3 h-3 inline mr-1" aria-hidden="true" />
                  Ação
                </label>
                <select
                  id="filter-action"
                  value={filterAction}
                  onChange={(e) =>
                    setFilterAction(e.target.value as AuditAction | '')
                  }
                  className="w-full px-3 py-2 rounded-lg text-sm border focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
                  style={{
                    backgroundColor: 'var(--semantic-surface-canvas)',
                    color: 'var(--semantic-text-primary)',
                    borderColor: 'var(--semantic-border-default)',
                  }}
                >
                  <option value="">Todas as ações</option>
                  {(Object.keys(ACTION_LABELS) as AuditAction[]).map((a) => (
                    <option key={a} value={a}>
                      {ACTION_LABELS[a]}
                    </option>
                  ))}
                </select>
              </div>

              {/* Data De */}
              <div className="min-w-[140px]">
                <label
                  className="block text-xs font-medium mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  htmlFor="filter-date-from"
                >
                  Data de
                </label>
                <input
                  id="filter-date-from"
                  type="date"
                  value={filterDateFrom}
                  onChange={(e) => setFilterDateFrom(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm border focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
                  style={{
                    backgroundColor: 'var(--semantic-surface-canvas)',
                    color: 'var(--semantic-text-primary)',
                    borderColor: 'var(--semantic-border-default)',
                  }}
                />
              </div>

              {/* Data Até */}
              <div className="min-w-[140px]">
                <label
                  className="block text-xs font-medium mb-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                  htmlFor="filter-date-to"
                >
                  Data até
                </label>
                <input
                  id="filter-date-to"
                  type="date"
                  value={filterDateTo}
                  onChange={(e) => setFilterDateTo(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm border focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
                  style={{
                    backgroundColor: 'var(--semantic-surface-canvas)',
                    color: 'var(--semantic-text-primary)',
                    borderColor: 'var(--semantic-border-default)',
                  }}
                />
              </div>

              {/* Botão Limpar */}
              {hasFilters && (
                <div className="flex items-end">
                  <button
                    onClick={clearFilters}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                    style={{
                      backgroundColor: 'var(--semantic-surface-canvas)',
                      color: 'var(--semantic-text-secondary)',
                      border: '1px solid var(--semantic-border-default)',
                    }}
                  >
                    <X className="w-4 h-4" aria-hidden="true" />
                    Limpar filtros
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* ─── Error State ─── */}
          {error && (
            <div
              className="border rounded-xl p-6 mb-6"
              role="alert"
              aria-live="assertive"
              style={{
                backgroundColor: 'var(--feedback-error-bg-dark)',
                borderColor: 'var(--feedback-error-border-dark)',
                color: 'var(--feedback-error-text-dark)',
              }}
            >
              <p className="font-semibold">Erro ao carregar registros de auditoria</p>
              <p className="text-sm mt-1 opacity-90">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  fetchAuditLogs()
                    .then((data: { logs: unknown[]; total: number }) => {
                      setLogs(data.logs as AuditLogEntry[]);
                      setLoading(false);
                    })
                    .catch((err: unknown) => {
                      setError(err instanceof Error ? err.message : 'Erro ao carregar registros de auditoria');
                      setLoading(false);
                    });
                }}
                className="mt-3 inline-flex items-center gap-2 text-sm underline focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                style={{ color: 'var(--feedback-error-text-dark)' }}
              >
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
                Tentar novamente
              </button>
            </div>
          )}

          {/* ─── Loading State ─── */}
          {loading && !error && (
            <div
              className="rounded-xl border overflow-hidden"
              style={{
                borderColor: 'var(--semantic-border-default)',
              }}
            >
              <table className="w-full" role="table">
                <thead>
                  <tr
                    style={{
                      backgroundColor: 'var(--semantic-surface-canvas)',
                      borderBottom: '1px solid var(--semantic-border-default)',
                    }}
                  >
                    {['Data/Hora', 'Ator', 'Ação', 'Entidade', 'ID Entidade', 'MPI', 'Ações'].map(
                      (h) => (
                        <th
                          key={h}
                          scope="col"
                          className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          {h}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <tr
                      key={i}
                      style={{
                        borderBottom: '1px solid var(--semantic-border-default)',
                      }}
                    >
                      {Array.from({ length: 7 }).map((_, j) => (
                        <td key={j} className="px-4 py-3">
                          <div
                            className="h-4 rounded animate-pulse"
                            style={{
                              backgroundColor: 'var(--semantic-surface-canvas)',
                              width: j === 2 ? '60%' : '75%',
                            }}
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* ─── Empty State ─── */}
          {!loading && !error && filteredLogs.length === 0 && (
            <div
              className="rounded-xl border p-10 text-center"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                borderColor: 'var(--semantic-border-default)',
              }}
            >
              <Shield
                className="w-12 h-12 mx-auto mb-4 opacity-50"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <p
                className="text-lg font-semibold mb-1"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {hasFilters
                  ? 'Nenhum registro corresponde aos filtros aplicados'
                  : 'Nenhum registro de auditoria encontrado'}
              </p>
              <p
                className="text-sm mb-4"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {hasFilters
                  ? 'Tente ajustar os critérios de busca ou limpar os filtros.'
                  : 'Os registros de ações realizadas no sistema aparecerão aqui.'}
              </p>
              {hasFilters && (
                <button
                  onClick={clearFilters}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  style={{
                    backgroundColor: 'var(--semantic-surface-canvas)',
                    color: 'var(--semantic-text-primary)',
                    border: '1px solid var(--semantic-border-default)',
                  }}
                >
                  <X className="w-4 h-4" aria-hidden="true" />
                  Limpar filtros
                </button>
              )}
            </div>
          )}

          {/* ─── Table ─── */}
          {!loading && !error && filteredLogs.length > 0 && (
            <>
              <div
                className="rounded-xl border overflow-hidden"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                }}
              >
                <div className="overflow-x-auto">
                  <table className="w-full" role="table">
                    <caption className="sr-only">
                      Trilha de Auditoria — Registro de ações clínicas e administrativas
                    </caption>
                    <thead>
                      {table.getHeaderGroups().map((headerGroup) => (
                        <tr
                          key={headerGroup.id}
                          style={{
                            backgroundColor: 'var(--semantic-surface-canvas)',
                            borderBottom: '1px solid var(--semantic-border-default)',
                          }}
                        >
                          {headerGroup.headers.map((header) => (
                            <th
                              key={header.id}
                              scope="col"
                              className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                              style={{ color: 'var(--semantic-text-secondary)' }}
                            >
                              {header.isPlaceholder
                                ? null
                                : flexRender(
                                    header.column.columnDef.header,
                                    header.getContext(),
                                  )}
                            </th>
                          ))}
                        </tr>
                      ))}
                    </thead>
                    <tbody>
                      {table.getRowModel().rows.map((row) => (
                        <tr
                          key={row.id}
                          className="transition-colors"
                          style={{
                            borderBottom: '1px solid var(--semantic-border-default)',
                          }}
                          onMouseEnter={(e) => {
                            (e.currentTarget as HTMLTableRowElement).style.backgroundColor =
                              'color-mix(in srgb, var(--semantic-surface-canvas) 60%, transparent)';
                          }}
                          onMouseLeave={(e) => {
                            (e.currentTarget as HTMLTableRowElement).style.backgroundColor =
                              'transparent';
                          }}
                        >
                          {row.getVisibleCells().map((cell) => (
                            <td
                              key={cell.id}
                              className="px-4 py-3"
                              style={{
                                backgroundColor: 'var(--semantic-surface-raised)',
                              }}
                            >
                              {flexRender(cell.column.columnDef.cell, cell.getContext())}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Paginação */}
              <div className="flex items-center justify-between mt-4 px-1">
                <div
                  className="text-sm"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Página {table.getState().pagination.pageIndex + 1} de{' '}
                  {table.getPageCount()}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                    className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80 disabled:opacity-40 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                    style={{
                      backgroundColor: 'var(--semantic-surface-raised)',
                      color: 'var(--semantic-text-primary)',
                      border: '1px solid var(--semantic-border-default)',
                    }}
                    aria-label="Página anterior"
                  >
                    <ChevronLeft className="w-4 h-4" aria-hidden="true" />
                    Anterior
                  </button>
                  <button
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                    className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80 disabled:opacity-40 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                    style={{
                      backgroundColor: 'var(--semantic-surface-raised)',
                      color: 'var(--semantic-text-primary)',
                      border: '1px solid var(--semantic-border-default)',
                    }}
                    aria-label="Próxima página"
                  >
                    Próxima
                    <ChevronRight className="w-4 h-4" aria-hidden="true" />
                  </button>
                </div>
              </div>
            </>
          )}

          {/* ─── Drawer de Detalhes ─── */}
          <DrawerBuilder
            open={selectedLog !== null}
            onClose={() => setSelectedLog(null)}
            title="Detalhes do Registro de Auditoria"
            size="md"
          >
            {selectedLog && (
              <div className="space-y-3">
                {(
                  [
                    ['ID', String(selectedLog.id)],
                    ['Data/Hora', formatDateTime(selectedLog.event_ts)],
                    ['Tempo Relativo', formatRelativeTime(selectedLog.event_ts)],
                    ['Ator', selectedLog.actor],
                    ['Ação', ACTION_LABELS[selectedLog.action]],
                    ['Entidade', selectedLog.entity_table],
                    ['ID da Entidade', selectedLog.entity_id],
                    ['MPI', selectedLog.mpi_id ?? '—'],
                    ['Tenant ID', selectedLog.tenant_id ?? '—'],
                    ['Request ID', selectedLog.request_id ?? '—'],
                  ] as [string, string][]
                ).map(([label, value]) => (
                  <div
                    key={label}
                    className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 py-2"
                    style={{
                      borderBottom: '1px solid var(--semantic-border-default)',
                    }}
                  >
                    <dt
                      className="text-xs font-semibold uppercase tracking-wider sm:w-36 flex-shrink-0"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      {label}
                    </dt>
                    <dd
                      className="text-sm font-medium"
                      style={{ color: 'var(--semantic-text-primary)' }}
                    >
                      {value}
                    </dd>
                  </div>
                ))}
              </div>
            )}
          </DrawerBuilder>
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
