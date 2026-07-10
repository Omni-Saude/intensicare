'use client';

import useSWR from 'swr';
import { fetchUsers, type UserInfo } from '@/lib/api';
import {
  Shield,
  ShieldOff,
  User,
  Mail,
  AlertTriangle,
  RefreshCw,
  Users,
  ChevronUp,
  ChevronDown,
  Search,
} from 'lucide-react';
import { useState, useMemo } from 'react';

type SortField = 'name' | 'email' | 'role';
type SortDir = 'asc' | 'desc';

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      <td className="px-4 py-3">
        <div
          className="h-4 w-32 rounded"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
      </td>
      <td className="px-4 py-3">
        <div
          className="h-4 w-48 rounded"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
      </td>
      <td className="px-4 py-3">
        <div
          className="h-4 w-20 rounded"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
      </td>
      <td className="px-4 py-3">
        <div
          className="h-5 w-16 rounded-full"
          style={{ backgroundColor: 'var(--surface-overlay)' }}
        />
      </td>
    </tr>
  );
}

function SortIcon({ field, currentField, direction }: { field: SortField; currentField: SortField; direction: SortDir }) {
  if (field !== currentField) {
    return (
      <ChevronDown className="size-3 opacity-30" aria-hidden="true" />
    );
  }
  return direction === 'asc' ? (
    <ChevronUp className="size-3" aria-hidden="true" />
  ) : (
    <ChevronDown className="size-3" aria-hidden="true" />
  );
}

export function UserManager() {
  const { data, error, isLoading, mutate } = useSWR(
    'admin-users',
    fetchUsers,
  );

  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [search, setSearch] = useState('');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const filteredAndSorted = useMemo(() => {
    if (!data?.items) return [];
    let items = [...data.items];

    // Filter by search
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (u) =>
          u.name.toLowerCase().includes(q) ||
          u.email.toLowerCase().includes(q) ||
          u.role.toLowerCase().includes(q),
      );
    }

    // Sort
    items.sort((a, b) => {
      const aVal = a[sortField].toLowerCase();
      const bVal = b[sortField].toLowerCase();
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });

    return items;
  }, [data, search, sortField, sortDir]);

  // Error state
  if (error) {
    return (
      <div
        role="alert"
        className="flex flex-col items-center justify-center gap-4 py-16 px-4 rounded-[var(--radius-lg)]"
        style={{
          backgroundColor: 'var(--severity-critical-wash)',
          borderColor: 'var(--severity-critical)',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
      >
        <AlertTriangle
          className="size-10"
          style={{ color: 'var(--severity-critical)' }}
        />
        <p
          className="text-sm font-medium text-center"
          style={{ color: 'var(--severity-critical)' }}
        >
          Erro ao carregar usuários
        </p>
        <p
          className="text-xs text-center"
          style={{ color: 'var(--text-secondary)' }}
        >
          {(error as Error).message}
        </p>
        <button
          onClick={() => mutate()}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-[var(--radius-sm)] transition-colors hover:opacity-80"
          style={{
            backgroundColor: 'var(--surface-overlay)',
            color: 'var(--text-primary)',
            borderColor: 'var(--border-default)',
            borderWidth: '1px',
            borderStyle: 'solid',
          }}
          aria-label="Tentar novamente"
        >
          <RefreshCw className="size-4" />
          Tentar novamente
        </button>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div aria-label="Carregando usuários" aria-busy="true">
        {/* Search skeleton */}
        <div className="mb-4">
          <div
            className="h-9 w-full max-w-sm rounded-[var(--radius-sm)] animate-pulse"
            style={{ backgroundColor: 'var(--surface-overlay)' }}
          />
        </div>
        {/* Table skeleton */}
        <div
          className="overflow-hidden rounded-[var(--radius-lg)]"
          style={{
            borderColor: 'var(--border-default)',
            borderWidth: '1px',
            borderStyle: 'solid',
          }}
        >
          <table className="w-full">
            <thead>
              <tr style={{ backgroundColor: 'var(--surface-raised)' }}>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  Nome
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  Email
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  Função
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                  Admin
                </th>
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <SkeletonRow key={i} />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // Empty state
  if (!data || data.items.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-16 px-4 rounded-[var(--radius-lg)]"
        style={{
          backgroundColor: 'var(--surface-raised)',
          borderColor: 'var(--border-default)',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
      >
        <Users className="size-10" style={{ color: 'var(--text-secondary)' }} />
        <p
          className="text-sm font-medium"
          style={{ color: 'var(--text-secondary)' }}
        >
          Nenhum usuário encontrado
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Search bar */}
      <div className="mb-4">
        <div
          className="relative max-w-sm"
          style={{ color: 'var(--text-secondary)' }}
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4" aria-hidden="true" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar usuários..."
            aria-label="Buscar usuários por nome, email ou função"
            className="w-full pl-9 pr-3 py-2 text-sm rounded-[var(--radius-sm)] outline-none transition-colors placeholder:text-[var(--text-secondary)] focus:ring-2 focus:ring-offset-0"
            style={{
              backgroundColor: 'var(--surface-raised)',
              color: 'var(--text-primary)',
              borderColor: 'var(--border-default)',
              borderWidth: '1px',
              borderStyle: 'solid',
              '--tw-ring-color': 'var(--severity-watch)',
            } as React.CSSProperties}
          />
        </div>
        <p
          className="mt-2 text-xs"
          style={{ color: 'var(--text-secondary)' }}
        >
          {filteredAndSorted.length} de {data.total} usuário{data.total !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Table */}
      <div
        className="overflow-hidden rounded-[var(--radius-lg)]"
        style={{
          borderColor: 'var(--border-default)',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
      >
        <table className="w-full" role="table" aria-label="Lista de usuários">
          <thead>
            <tr style={{ backgroundColor: 'var(--surface-raised)' }}>
              {([
                { field: 'name' as SortField, label: 'Nome', icon: User },
                { field: 'email' as SortField, label: 'Email', icon: Mail },
                { field: 'role' as SortField, label: 'Função', icon: Shield },
              ]).map(({ field, label }) => (
                <th key={field} className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort(field)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider transition-colors hover:opacity-80"
                    style={{ color: 'var(--text-secondary)' }}
                    aria-label={`Ordenar por ${label}`}
                  >
                    {label}
                    <SortIcon field={field} currentField={sortField} direction={sortDir} />
                  </button>
                </th>
              ))}
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                Admin
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSorted.map((user, idx) => (
              <tr
                key={user.id}
                style={{
                  borderTop: idx > 0 ? `1px solid var(--border-default)` : 'none',
                }}
                className="transition-colors hover:bg-[var(--surface-overlay)]"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <User className="size-4 shrink-0" style={{ color: 'var(--text-secondary)' }} aria-hidden="true" />
                    <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      {user.name}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Mail className="size-4 shrink-0" style={{ color: 'var(--text-secondary)' }} aria-hidden="true" />
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {user.email}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span
                    className="inline-block px-2.5 py-0.5 text-xs font-medium rounded-full"
                    style={{
                      backgroundColor: 'var(--surface-overlay)',
                      color: 'var(--text-primary)',
                    }}
                  >
                    {user.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {user.is_admin ? (
                    <span
                      className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-medium rounded-full"
                      style={{
                        backgroundColor: 'var(--severity-normal-wash)',
                        color: 'var(--severity-normal)',
                      }}
                      role="status"
                      aria-label="Administrador"
                    >
                      <Shield className="size-3" aria-hidden="true" />
                      Sim
                    </span>
                  ) : (
                    <span
                      className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-medium rounded-full"
                      style={{
                        backgroundColor: 'var(--surface-overlay)',
                        color: 'var(--text-secondary)',
                      }}
                      role="status"
                      aria-label="Não administrador"
                    >
                      <ShieldOff className="size-3" aria-hidden="true" />
                      Não
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty result after filtering */}
      {filteredAndSorted.length === 0 && search.trim() !== '' && (
        <div
          className="flex flex-col items-center justify-center gap-2 py-12 px-4 mt-4 rounded-[var(--radius-lg)]"
          style={{
            backgroundColor: 'var(--surface-raised)',
            borderColor: 'var(--border-default)',
            borderWidth: '1px',
            borderStyle: 'solid',
          }}
        >
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Nenhum usuário corresponde à busca &ldquo;{search}&rdquo;
          </p>
        </div>
      )}
    </div>
  );
}
