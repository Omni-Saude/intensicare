'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useParams } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';

/** Human-readable labels for known route segments */
const SEGMENT_LABELS: Record<string, string> = {
  dashboard: 'Painel',
  'command-center': 'Central de Comando',
  'alert-triage': 'Triagem de Alertas',
  'sepse-dashboard': 'Sepse',
  'antimicrobial-stewardship': 'Antimicrobiano',
  'prophylaxis-bundles': 'Profilaxia',
  nutrition: 'Nutrição',
  'fluid-balance': 'Balanço Hídrico',
  communication: 'Comunicação',
  'care-pathways': 'Care Pathways',
  ventilation: 'Ventilação',
  stability: 'Estabilidade',
  'clinical-deterioration': 'Piora Clínica',
  'patient-movement': 'Movimentação',
  prescription: 'Prescrições',
  'clinical-notes': 'Evoluções',
  documentation: 'Documentação',
  sedation: 'Sedação',
  'clinical-forms': 'Formulários Clínicos',
  handoff: 'Passagem de Plantão',
  indicators: 'Indicadores',
  efficiency: 'Eficiência',
  admin: 'Administração',
  users: 'Usuários',
  thresholds: 'Limiares',
  tenancy: 'Organizações',
  'audit-log': 'Auditoria',
  registry: 'Cadastros',
  login: 'Login',
  register: 'Registrar',
  patient: 'Paciente',
  evolucoes: 'Evoluções',
};

interface BreadcrumbItem {
  label: string;
  href: string;
  isLast: boolean;
}

/**
 * Builds breadcrumb segments from the current pathname.
 *
 * Parses path segments, replaces UUID-like segments with a friendly label
 * (or the raw segment if no label mapping exists), and builds cumulative hrefs.
 */
export function useBreadcrumbs(): BreadcrumbItem[] {
  const pathname = usePathname();
  const params = useParams();

  if (!pathname) return [];

  const segments: string[] = pathname.split('/').filter((s): s is string => Boolean(s));

  const items: BreadcrumbItem[] = [];
  let cumulativePath = '';

  // Always start with Dashboard
  items.push({
    label: 'Painel',
    href: '/dashboard',
    isLast: segments.length === 0,
  });

  for (const raw of segments) {
    cumulativePath += '/' + raw;

    let label: string;

    // Replace dynamic route params with their actual value
    if (raw.startsWith(':') || /^[0-9a-f]{8,}$/i.test(raw)) {
      // Try to get label from params
      const paramValues: string[] = Object.values(params).filter(
        (v): v is string => typeof v === 'string'
      );
      const match = paramValues.find((val) => raw.includes(val) || val.includes(raw));
      if (match) {
        label = `Paciente ${match.substring(0, 8)}…`; // Shorten UUID display
      } else {
        label = raw.length > 8 ? `${raw.substring(0, 8)}…` : raw;
      }
    } else {
      label = SEGMENT_LABELS[raw.toLowerCase()] || raw;
    }

    items.push({
      label,
      href: cumulativePath,
      isLast: false, // Will be overridden below
    });
  }

  // Mark the last item
  if (items.length > 0) {
    items[items.length - 1]!.isLast = true;
  }

  return items;
}

interface BreadcrumbProps {
  /** Custom items to override auto-generated breadcrumbs */
  items?: BreadcrumbItem[];
  /** Additional className for the container */
  className?: string;
}

/**
 * Breadcrumb component that displays a navigation trail.
 *
 * Automatically generates breadcrumbs from the current route using
 * `useBreadcrumbs()`, or accepts custom items via props.
 *
 * @example
 * // Auto-generated:
 * <Breadcrumb />
 * // => Painel > Paciente > 550e8400… > Evoluções
 *
 * @example
 * // Custom items:
 * <Breadcrumb items={[{ label: 'Home', href: '/', isLast: false }, { label: 'Settings', href: '/settings', isLast: true }]} />
 */
export default function Breadcrumb({ items: customItems, className = '' }: BreadcrumbProps) {
  const autoItems = useBreadcrumbs();
  const items = customItems ?? autoItems;

  if (items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={`flex items-center gap-1 text-sm ${className}`}>
      <ol className="flex items-center gap-1 flex-wrap">
        {items.map((item, index) => (
          <li key={item.href} className="flex items-center gap-1">
            {/* Home icon for first item */}
            {index === 0 && (
              <Home
                className="w-3.5 h-3.5 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
            )}

            {/* Chevron separator (skip before first item) */}
            {index > 0 && (
              <ChevronRight
                className="w-3.5 h-3.5 flex-shrink-0 mx-0.5"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
            )}

            {item.isLast ? (
              <span
                className="font-medium truncate max-w-[200px]"
                style={{ color: 'var(--semantic-text-primary)' }}
                aria-current="page"
              >
                {item.label}
              </span>
            ) : (
              <Link
                href={item.href}
                className="hover:underline truncate max-w-[200px] transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none rounded-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
