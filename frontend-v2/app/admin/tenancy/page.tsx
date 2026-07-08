'use client';

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  Building2,
  Hospital,
  DoorOpen,
  ChevronRight,
  ChevronDown,
  Settings,
  Users,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import {
  MOCK_TREE,
  flattenTree,
  getTokenRoot,
  getTypeLabel,
  type TenancyNode,
  type VisibleTreeItem,
  type OrganizationNode,
  type EstablishmentNode,
  type SectorNode,
} from '@/lib/tenancy-types';

// ─── Token Helpers ────────────────────────────────────────────────────────────

const TOKEN_MAP = {
  organization: {
    fill: 'var(--admin-tenancy-organization-fill)',
    onFill: 'var(--admin-tenancy-organization-on-fill)',
    wash: 'var(--admin-tenancy-organization-wash)',
    onSurface: 'var(--admin-tenancy-organization-on-surface-dark)',
    signal: 'var(--admin-tenancy-organization-signal-dark)',
  },
  establishment: {
    fill: 'var(--admin-tenancy-establishment-fill)',
    onFill: 'var(--admin-tenancy-establishment-on-fill)',
    wash: 'var(--admin-tenancy-establishment-wash)',
    onSurface: 'var(--admin-tenancy-establishment-on-surface-dark)',
    signal: 'var(--admin-tenancy-establishment-signal-dark)',
  },
  sector: {
    fill: 'var(--admin-tenancy-sector-fill)',
    onFill: 'var(--admin-tenancy-sector-on-fill)',
    wash: 'var(--admin-tenancy-sector-wash)',
    onSurface: 'var(--admin-tenancy-sector-on-surface-dark)',
    signal: 'var(--admin-tenancy-sector-signal-dark)',
  },
} as const;

type Level = keyof typeof TOKEN_MAP;

// ─── Icons per Level ──────────────────────────────────────────────────────────

const LEVEL_ICON: Record<Level, React.ComponentType<{ className?: string; 'aria-hidden'?: boolean | 'true' | 'false' }>> = {
  organization: Building2,
  establishment: Hospital,
  sector: DoorOpen,
};

// ─── Main Page Component ──────────────────────────────────────────────────────

export default function AdminTenancyPage() {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(() => new Set(['org-sl']));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusedId, setFocusedId] = useState<string>('org-sl');
  const [loading] = useState(false); // mock data loads instantly; set true to test skeleton
  const [error] = useState<string | null>(null); // set to trigger error state for testing

  const treeRef = useRef<HTMLDivElement>(null);

  // ── Compute visible items ─────────────────────────────────────────────────

  const visibleItems = useMemo(
    () => flattenTree(MOCK_TREE, expandedIds),
    [expandedIds],
  );

  const focusedIndex = useMemo(
    () => visibleItems.findIndex((item) => item.id === focusedId),
    [visibleItems, focusedId],
  );

  // ── Toggle expand / collapse ───────────────────────────────────────────────

  const toggleExpand = useCallback(
    (id: string) => {
      setExpandedIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
        } else {
          next.add(id);
        }
        return next;
      });
    },
    [],
  );

  // ── Select node (show detail card) ─────────────────────────────────────────

  const selectNode = useCallback((id: string) => {
    setSelectedId((prev) => (prev === id ? null : id));
  }, []);

  // ── Focus a specific item ──────────────────────────────────────────────────

  const focusItem = useCallback((id: string) => {
    setFocusedId(id);
  }, []);

  // ── Expand all ─────────────────────────────────────────────────────────────

  const expandAll = useCallback(() => {
    const allIds = new Set<string>();
    function collect(node: TenancyNode) {
      if (node.kind === 'organization' || node.kind === 'establishment') {
        allIds.add(node.data.id);
        node.children.forEach(collect);
      }
    }
    collect(MOCK_TREE);
    setExpandedIds(allIds);
  }, []);

  // ── Collapse all ───────────────────────────────────────────────────────────

  const collapseAll = useCallback(() => {
    setExpandedIds(new Set(['org-sl']));
  }, []);

  // ── Keyboard Navigation ────────────────────────────────────────────────────

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (visibleItems.length === 0) return;

      switch (e.key) {
        case 'ArrowDown': {
          e.preventDefault();
          const nextIdx = Math.min(focusedIndex + 1, visibleItems.length - 1);
          focusItem(visibleItems[nextIdx]!.id);
          break;
        }
        case 'ArrowUp': {
          e.preventDefault();
          const prevIdx = Math.max(focusedIndex - 1, 0);
          focusItem(visibleItems[prevIdx]!.id);
          break;
        }
        case 'ArrowRight': {
          e.preventDefault();
          const current = visibleItems[focusedIndex];
          if (!current) break;
          if (current.hasChildren && !current.isExpanded) {
            toggleExpand(current.id);
          } else if (current.hasChildren && current.isExpanded) {
            // Move focus to first child
            const childIdx = focusedIndex + 1;
            if (childIdx < visibleItems.length) {
              focusItem(visibleItems[childIdx]!.id);
            }
          }
          break;
        }
        case 'ArrowLeft': {
          e.preventDefault();
          const current = visibleItems[focusedIndex];
          if (!current) break;
          if (current.hasChildren && current.isExpanded) {
            toggleExpand(current.id);
          } else if (current.parentId) {
            focusItem(current.parentId);
          }
          break;
        }
        case 'Enter':
        case ' ': {
          e.preventDefault();
          const current = visibleItems[focusedIndex];
          if (current) {
            selectNode(current.id);
          }
          break;
        }
        case 'Home': {
          e.preventDefault();
          if (visibleItems.length > 0) {
            focusItem(visibleItems[0]!.id);
          }
          break;
        }
        case 'End': {
          e.preventDefault();
          if (visibleItems.length > 0) {
            focusItem(visibleItems[visibleItems.length - 1]!.id);
          }
          break;
        }
        default:
          break;
      }
    },
    [visibleItems, focusedIndex, focusItem, toggleExpand, selectNode],
  );

  // ── Auto-focus tree on mount ───────────────────────────────────────────────

  useEffect(() => {
    treeRef.current?.focus();
  }, []);

  // ── Find selected node for detail card ─────────────────────────────────────

  const selectedNode = useMemo(() => {
    if (!selectedId) return null;
    return visibleItems.find((item) => item.id === selectedId) ?? null;
  }, [visibleItems, selectedId]);

  // ── Render Helpers ─────────────────────────────────────────────────────────

  const getNodeLabel = (node: TenancyNode): string => {
    if (node.kind === 'organization') return node.data.name;
    if (node.kind === 'establishment') return node.data.name;
    return node.data.name;
  };

  const getNodeActive = (node: TenancyNode): boolean => {
    if (node.kind === 'organization') return node.data.active;
    if (node.kind === 'establishment') return node.data.active;
    return node.data.active;
  };

  // ── Loading Skeleton ───────────────────────────────────────────────────────

  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto">
          {/* Header skeleton */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-10 h-10 rounded-xl animate-pulse"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
              />
              <div>
                <div
                  className="h-6 w-56 rounded animate-pulse mb-1"
                  style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                />
                <div
                  className="h-4 w-72 rounded animate-pulse"
                  style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                />
              </div>
            </div>
          </div>

          {/* Tree skeleton — 3 levels */}
          <div
            className="rounded-xl border p-6"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              borderColor: 'var(--semantic-border-default)',
            }}
          >
            {[0, 1, 2].map((depth) => (
              <div key={depth} style={{ marginLeft: depth * 24 }} className="mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-5 h-5 rounded animate-pulse"
                    style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
                  />
                  <div
                    className="w-8 h-8 rounded-lg animate-pulse"
                    style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
                  />
                  <div
                    className="h-4 rounded animate-pulse flex-1 max-w-sm"
                    style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  // ── Error State ────────────────────────────────────────────────────────────
  if (error) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: 'var(--admin-tenancy-organization-fill)' }}
              >
                <Building2 className="w-5 h-5" style={{ color: 'var(--admin-tenancy-organization-on-fill)' }} aria-hidden="true" />
              </div>
              <div>
                <h1 className="text-2xl font-bold" style={{ color: 'var(--semantic-text-primary)' }}>
                  Gestão de Organizações
                </h1>
                <p className="text-sm mt-0.5" style={{ color: 'var(--semantic-text-secondary)' }}>
                  Estrutura hierárquica de organizações, estabelecimentos e setores
                </p>
              </div>
            </div>
          </div>

          <div
            role="alert"
            aria-live="assertive"
            className="border rounded-xl p-6"
            style={{
              backgroundColor: 'var(--clinical-severity-critical-wash)',
              borderColor: 'var(--clinical-severity-critical-signal)',
              color: 'var(--clinical-severity-critical-on-surface)',
            }}
          >
            <div className="flex items-start gap-3">
              <AlertTriangle
                className="w-6 h-6 flex-shrink-0 mt-0.5"
                style={{ color: 'var(--clinical-severity-critical-signal)' }}
                aria-hidden="true"
              />
              <div>
                <p className="font-semibold text-lg">Erro ao carregar estrutura</p>
                <p className="text-sm mt-1 opacity-90">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // ── Empty State ────────────────────────────────────────────────────────────

  if (!MOCK_TREE || MOCK_TREE.children.length === 0) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: 'var(--admin-tenancy-organization-fill)' }}
              >
                <Building2 className="w-5 h-5" style={{ color: 'var(--admin-tenancy-organization-on-fill)' }} aria-hidden="true" />
              </div>
              <div>
                <h1 className="text-2xl font-bold" style={{ color: 'var(--semantic-text-primary)' }}>
                  Gestão de Organizações
                </h1>
                <p className="text-sm mt-0.5" style={{ color: 'var(--semantic-text-secondary)' }}>
                  Estrutura hierárquica de organizações, estabelecimentos e setores
                </p>
              </div>
            </div>
          </div>

          <div
            className="rounded-xl border p-12 text-center"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              borderColor: 'var(--semantic-border-default)',
            }}
          >
            <Building2
              className="w-16 h-16 mx-auto mb-4"
              style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }}
              aria-hidden="true"
            />
            <p className="text-lg font-medium" style={{ color: 'var(--semantic-text-primary)' }}>
              Nenhuma organização configurada
            </p>
            <p className="text-sm mt-1" style={{ color: 'var(--semantic-text-secondary)' }}>
              Adicione uma organização para começar a estruturar sua rede de saúde.
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  // ── Main Render — Tree View ────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-4xl mx-auto">
          {/* ── Header ────────────────────────────────────────────────── */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: 'var(--admin-tenancy-organization-fill)' }}
              >
                <Building2 className="w-5 h-5" style={{ color: 'var(--admin-tenancy-organization-on-fill)' }} aria-hidden="true" />
              </div>
              <div>
                <h1 className="text-2xl font-bold" style={{ color: 'var(--semantic-text-primary)' }}>
                  Gestão de Organizações
                </h1>
                <p className="text-sm mt-0.5" style={{ color: 'var(--semantic-text-secondary)' }}>
                  Estrutura hierárquica de organizações, estabelecimentos e setores
                </p>
              </div>
            </div>
          </div>

          {/* ── Toolbar ────────────────────────────────────────────────── */}
          <div className="flex items-center gap-3 mb-4 flex-wrap">
            <button
              onClick={expandAll}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all border"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
                borderColor: 'var(--semantic-border-default)',
              }}
            >
              <ChevronDown className="w-4 h-4" aria-hidden="true" />
              Expandir todos
            </button>
            <button
              onClick={collapseAll}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all border"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
                borderColor: 'var(--semantic-border-default)',
              }}
            >
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
              Recolher todos
            </button>

            {/* Keyboard hint */}
            <span className="text-xs ml-auto hidden sm:inline" style={{ color: 'var(--semantic-text-secondary)' }}>
              Use as setas para navegar, Enter para selecionar
            </span>
          </div>

          {/* ── Tree ───────────────────────────────────────────────────── */}
          <div
            ref={treeRef}
            role="tree"
            aria-label="Estrutura hierárquica de organizações"
            tabIndex={0}
            onKeyDown={handleKeyDown}
            className="rounded-xl border p-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              borderColor: 'var(--semantic-border-default)',
              outline: 'none',
            }}
          >
            {visibleItems.map((item) => {
              const level = getTokenRoot(item.node.kind);
              const tokens = TOKEN_MAP[level];
              const Icon = LEVEL_ICON[level];
              const isFocused = item.id === focusedId;
              const isSelected = item.id === selectedId;
              const isActive = getNodeActive(item.node);
              const label = getNodeLabel(item.node);

              // Sector type badge label
              const sectorTypeLabel =
                item.node.kind === 'sector' ? getTypeLabel(item.node.data.type) : null;

              return (
                <div
                  key={item.id}
                  role="treeitem"
                  aria-expanded={item.hasChildren ? item.isExpanded : undefined}
                  aria-selected={isSelected}
                  aria-level={item.depth + 1}
                  tabIndex={isFocused ? 0 : -1}
                  onClick={() => {
                    focusItem(item.id);
                    selectNode(item.id);
                  }}
                  onFocus={() => focusItem(item.id)}
                  className="group flex items-center gap-2 py-2 px-3 rounded-lg cursor-pointer transition-colors outline-none"
                  style={{
                    marginLeft: item.depth * 24,
                    backgroundColor: isFocused
                      ? tokens.wash + '1A' // wash with low opacity for focus
                      : 'transparent',
                    borderRadius: '0.5rem',
                  }}
                >
                  {/* Expand/Collapse toggle */}
                  {item.hasChildren ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleExpand(item.id);
                      }}
                      className="p-0.5 rounded flex-shrink-0 transition-transform"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                      aria-label={item.isExpanded ? 'Recolher' : 'Expandir'}
                      tabIndex={-1}
                    >
                      {item.isExpanded ? (
                        <ChevronDown className="w-4 h-4" aria-hidden="true" />
                      ) : (
                        <ChevronRight className="w-4 h-4" aria-hidden="true" />
                      )}
                    </button>
                  ) : (
                    <span className="w-5 flex-shrink-0" aria-hidden="true" />
                  )}

                  {/* Level icon */}
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{
                      backgroundColor: tokens.fill,
                      color: tokens.onFill,
                    }}
                  >
                    <Icon className="w-4 h-4" aria-hidden="true" />
                  </div>

                  {/* Label */}
                  <span
                    className="text-sm font-medium flex-1 min-w-0 truncate"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {label}
                  </span>

                  {/* Sector type badge */}
                  {sectorTypeLabel && (
                    <span
                      className="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0"
                      style={{
                        backgroundColor: tokens.wash + '33',
                        color: tokens.onSurface,
                      }}
                    >
                      {sectorTypeLabel}
                    </span>
                  )}

                  {/* Active / Inactive indicator */}
                  {isActive ? (
                    <CheckCircle2
                      className="w-4 h-4 flex-shrink-0"
                      style={{ color: 'var(--clinical-severity-normal-signal)' }}
                      aria-label="Ativo"
                    />
                  ) : (
                    <XCircle
                      className="w-4 h-4 flex-shrink-0"
                      style={{ color: 'var(--semantic-text-secondary)', opacity: 0.5 }}
                      aria-label="Inativo"
                    />
                  )}
                </div>
              );
            })}

            {visibleItems.length === 0 && (
              <div className="py-8 text-center">
                <p style={{ color: 'var(--semantic-text-secondary)' }}>Nenhum item para exibir.</p>
              </div>
            )}
          </div>

          {/* ── Detail Card ──────────────────────────────────────────────── */}
          {selectedNode && (
            <div
              className="mt-6 rounded-xl border p-6"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                borderColor: 'var(--semantic-border-default)',
              }}
            >
              {selectedNode.node.kind === 'organization' && (
                <DetailCardOrganization org={selectedNode.node as OrganizationNode} />
              )}
              {selectedNode.node.kind === 'establishment' && (
                <DetailCardEstablishment est={selectedNode.node as EstablishmentNode} />
              )}
              {selectedNode.node.kind === 'sector' && (
                <DetailCardSector
                  sector={selectedNode.node as SectorNode}
                  parentEst={findParentEstablishment(visibleItems, selectedNode)}
                />
              )}
            </div>
          )}
        </div>
      </ErrorBoundary>
    </Layout>
  );
}

// ─── Detail Card Sub-Components ────────────────────────────────────────────────

function DetailCardOrganization({ org }: { org: OrganizationNode }) {
  const tokens = TOKEN_MAP.organization;
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: tokens.fill }}
        >
          <Building2 className="w-5 h-5" style={{ color: tokens.onFill }} aria-hidden="true" />
        </div>
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--semantic-text-primary)' }}>
            {org.data.name}
          </h2>
          <p className="text-xs" style={{ color: tokens.onSurface }}>
            Organização
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {org.data.active ? (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'var(--clinical-severity-normal-wash)',
                color: 'var(--clinical-severity-normal-on-surface)',
              }}
            >
              <CheckCircle2 className="w-3 h-3" aria-hidden="true" />
              Ativo
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'var(--semantic-surface-canvas)',
                color: 'var(--semantic-text-secondary)',
              }}
            >
              <XCircle className="w-3 h-3" aria-hidden="true" />
              Inativo
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <DetailField label="CNPJ" value={org.data.cnpj} />
        <DetailField label="Estabelecimentos" value={String(org.children.length)} />
        <DetailField
          label="Setores"
          value={String(org.children.reduce((acc, est) => acc + est.children.length, 0))}
        />
        <DetailField label="ID" value={org.data.id} mono />
      </div>
    </div>
  );
}

function DetailCardEstablishment({ est }: { est: EstablishmentNode }) {
  const tokens = TOKEN_MAP.establishment;
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: tokens.fill }}
        >
          <Hospital className="w-5 h-5" style={{ color: tokens.onFill }} aria-hidden="true" />
        </div>
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--semantic-text-primary)' }}>
            {est.data.name}
          </h2>
          <p className="text-xs" style={{ color: tokens.onSurface }}>
            Estabelecimento
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {est.data.active ? (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'var(--clinical-severity-normal-wash)',
                color: 'var(--clinical-severity-normal-on-surface)',
              }}
            >
              <CheckCircle2 className="w-3 h-3" aria-hidden="true" />
              Ativo
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'var(--semantic-surface-canvas)',
                color: 'var(--semantic-text-secondary)',
              }}
            >
              <XCircle className="w-3 h-3" aria-hidden="true" />
              Inativo
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <DetailField label="CNES" value={est.data.cnes} />
        <DetailField label="Endereço" value={est.data.address} />
        <DetailField label="Setores" value={String(est.children.length)} />
        <DetailField
          label="Leitos Totais"
          value={String(est.children.reduce((acc, s) => acc + s.data.beds_count, 0))}
        />
        <DetailField label="ID" value={est.data.id} mono />
      </div>
    </div>
  );
}

function DetailCardSector({
  sector,
  parentEst,
}: {
  sector: SectorNode;
  parentEst: VisibleTreeItem | null;
}) {
  const tokens = TOKEN_MAP.sector;
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: tokens.fill }}
        >
          <DoorOpen className="w-5 h-5" style={{ color: tokens.onFill }} aria-hidden="true" />
        </div>
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--semantic-text-primary)' }}>
            {sector.data.name}
          </h2>
          <p className="text-xs" style={{ color: tokens.onSurface }}>
            Setor — {getTypeLabel(sector.data.type)}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {sector.data.active ? (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'var(--clinical-severity-normal-wash)',
                color: 'var(--clinical-severity-normal-on-surface)',
              }}
            >
              <CheckCircle2 className="w-3 h-3" aria-hidden="true" />
              Ativo
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-1 text-xs font-medium px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'var(--semantic-surface-canvas)',
                color: 'var(--semantic-text-secondary)',
              }}
            >
              <XCircle className="w-3 h-3" aria-hidden="true" />
              Inativo
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <DetailField label="Tipo" value={getTypeLabel(sector.data.type)} />
        <DetailField label="Leitos" value={String(sector.data.beds_count)} />
        {parentEst?.node.kind === 'establishment' && (
          <DetailField label="CNES (Estabelecimento)" value={parentEst.node.data.cnes} />
        )}
        <DetailField label="Estabelecimento" value={parentEst ? getParentName(parentEst) : '—'} />
        <DetailField label="ID" value={sector.data.id} mono />
      </div>
    </div>
  );
}

// ─── Detail Field ─────────────────────────────────────────────────────────────

function DetailField({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs font-medium mb-1" style={{ color: 'var(--semantic-text-secondary)' }}>
        {label}
      </dt>
      <dd
        className="text-sm font-medium"
        style={{
          color: 'var(--semantic-text-primary)',
          fontFamily: mono ? 'monospace' : undefined,
        }}
      >
        {value}
      </dd>
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getParentName(item: VisibleTreeItem): string {
  if (item.node.kind === 'organization') return item.node.data.name;
  if (item.node.kind === 'establishment') return item.node.data.name;
  return item.node.data.name;
}

function findParentEstablishment(
  visibleItems: VisibleTreeItem[],
  sectorItem: VisibleTreeItem,
): VisibleTreeItem | null {
  if (!sectorItem.parentId) return null;
  return visibleItems.find((item) => item.id === sectorItem.parentId) ?? null;
}
