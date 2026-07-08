// ─── Tenancy Types & Hierarchy ────────────────────────────────────────────────
// Domain model: Organization → Establishment → Sector
// Used by app/admin/tenancy/page.tsx for the expandable admin tree.

export interface Organization {
  id: string;
  name: string;
  cnpj: string;
  active: boolean;
}

export interface Establishment {
  id: string;
  organization_id: string;
  name: string;
  cnes: string;
  address: string;
  active: boolean;
}

export interface Sector {
  id: string;
  establishment_id: string;
  name: string;
  type: 'uti' | 'enfermaria' | 'cc' | 'pa' | 'outro';
  beds_count: number;
  active: boolean;
}

// ─── Tree Node Types ──────────────────────────────────────────────────────────

export interface OrganizationNode {
  kind: 'organization';
  data: Organization;
  children: EstablishmentNode[];
}

export interface EstablishmentNode {
  kind: 'establishment';
  data: Establishment;
  children: SectorNode[];
}

export interface SectorNode {
  kind: 'sector';
  data: Sector;
}

export type TenancyNode = OrganizationNode | EstablishmentNode | SectorNode;

// ─── Visible Tree Item (flattened for rendering) ─────────────────────────────

export interface VisibleTreeItem {
  id: string;
  node: TenancyNode;
  depth: number;
  hasChildren: boolean;
  isExpanded: boolean;
  parentId: string | null;
}

// ─── Mock Data: Hospital São Lucas ────────────────────────────────────────────

export const MOCK_TREE: OrganizationNode = {
  kind: 'organization',
  data: {
    id: 'org-sl',
    name: 'Hospital São Lucas',
    cnpj: '12.345.678/0001-90',
    active: true,
  },
  children: [
    {
      kind: 'establishment',
      data: {
        id: 'est-matriz',
        organization_id: 'org-sl',
        name: 'Matriz — Unidade Central',
        cnes: '1234567',
        address: 'Av. Paulista, 1000 — São Paulo/SP',
        active: true,
      },
      children: [
        {
          kind: 'sector',
          data: {
            id: 'set-uti1',
            establishment_id: 'est-matriz',
            name: 'UTI Geral Adulto',
            type: 'uti',
            beds_count: 20,
            active: true,
          },
        },
        {
          kind: 'sector',
          data: {
            id: 'set-uti2',
            establishment_id: 'est-matriz',
            name: 'UTI Coronariana',
            type: 'uti',
            beds_count: 10,
            active: true,
          },
        },
        {
          kind: 'sector',
          data: {
            id: 'set-cc',
            establishment_id: 'est-matriz',
            name: 'Centro Cirúrgico',
            type: 'cc',
            beds_count: 8,
            active: true,
          },
        },
      ],
    },
    {
      kind: 'establishment',
      data: {
        id: 'est-filial-norte',
        organization_id: 'org-sl',
        name: 'Filial Norte',
        cnes: '7654321',
        address: 'Rua das Oliveiras, 500 — São Paulo/SP',
        active: true,
      },
      children: [
        {
          kind: 'sector',
          data: {
            id: 'set-enf-norte',
            establishment_id: 'est-filial-norte',
            name: 'Enfermaria Clínica',
            type: 'enfermaria',
            beds_count: 30,
            active: true,
          },
        },
        {
          kind: 'sector',
          data: {
            id: 'set-pa-norte',
            establishment_id: 'est-filial-norte',
            name: 'Pronto Atendimento',
            type: 'pa',
            beds_count: 15,
            active: false,
          },
        },
      ],
    },
  ],
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Returns the token root name for the CSS custom properties. */
export function getTokenRoot(kind: TenancyNode['kind']): 'organization' | 'establishment' | 'sector' {
  switch (kind) {
    case 'organization':
      return 'organization';
    case 'establishment':
      return 'establishment';
    case 'sector':
      return 'sector';
  }
}

/** Maps a sector type to a human-readable PT-BR label. */
export function getTypeLabel(type: Sector['type']): string {
  switch (type) {
    case 'uti':
      return 'UTI';
    case 'enfermaria':
      return 'Enfermaria';
    case 'cc':
      return 'Centro Cirúrgico';
    case 'pa':
      return 'Pronto Atendimento';
    case 'outro':
      return 'Outro';
  }
}

/** Checks if a TenancyNode has children (i.e., is expandable). */
export function isExpandable(node: TenancyNode): node is OrganizationNode | EstablishmentNode {
  return node.kind === 'organization' || node.kind === 'establishment';
}

/** Flattens the tree into a visible-items list based on expanded node IDs. */
export function flattenTree(
  root: OrganizationNode,
  expandedIds: Set<string>,
): VisibleTreeItem[] {
  const result: VisibleTreeItem[] = [];

  function walk(node: TenancyNode, depth: number, parentId: string | null) {
    const expandable = isExpandable(node);
    const children = expandable ? node.children : [];
    const nodeId = expandable ? node.data.id : (node as SectorNode).data.id;

    result.push({
      id: nodeId,
      node,
      depth,
      hasChildren: expandable && children.length > 0,
      isExpanded: expandedIds.has(nodeId),
      parentId,
    });

    if (expandable && expandedIds.has(nodeId)) {
      for (const child of children) {
        walk(child, depth + 1, nodeId);
      }
    }
  }

  walk(root, 0, null);
  return result;
}
