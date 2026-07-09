'use client';

import { useEffect } from 'react';

/**
 * TenantProvider — sets data-tenant on <html> from the current tenant context.
 *
 * Reads the tenant slug from the client-side auth context / localStorage.
 * Falls back to "default" when no tenant is specified, which maps to the
 * default IntensiCare orange brand (see globals.css [data-tenant="default"]).
 *
 * ADR-0004 § Tenant White-Labelling
 */
interface TenantProviderProps {
  /** Optionally override the tenant slug. Defaults to 'default'. */
  tenant?: string;
}

export default function TenantProvider({
  tenant = 'default',
}: TenantProviderProps) {
  useEffect(() => {
    // 1. Check for an explicit prop
    if (tenant && tenant !== 'default') {
      document.documentElement.setAttribute('data-tenant', tenant);
      return;
    }

    // 2. Fallback: read from localStorage (set by auth layer after login)
    const stored = localStorage.getItem('intensicare:tenant');
    if (stored) {
      document.documentElement.setAttribute('data-tenant', stored);
      return;
    }

    // 3. Final fallback: default tenant
    document.documentElement.setAttribute('data-tenant', 'default');
  }, [tenant]);

  return null; // renders nothing — side-effect only
}
