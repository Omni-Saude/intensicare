'use client';

import useSWR from 'swr';
import {
  fetchUsers,
  createUser,
  ApiError,
  CLINICAL_ROLE_OPTIONS,
  type ClinicalRole,
} from '@/lib/api';
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
  Plus,
  X,
  Loader2,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

type SortField = 'name' | 'email' | 'role';
type SortDir = 'asc' | 'desc';

// FastAPI/Pydantic 422 responses send `detail` as an array of
// { loc, msg, type } objects rather than a string. lib/api.ts's ApiError
// types `detail` as `string` but doesn't validate it at runtime (the value
// comes straight from `response.json()`), so it can actually be an array or
// object here. Render it readably instead of "[object Object]". (Known
// cross-cutting defect C-N1 — being fixed globally elsewhere; handled
// locally here so this form doesn't depend on that other fix landing.)
function formatApiErrorDetail(err: unknown): string {
  if (err instanceof ApiError) {
    const raw: unknown = err.detail;
    if (typeof raw === 'string' && raw.trim()) return raw;
    if (Array.isArray(raw)) {
      const messages = raw
        .map((item) =>
          item && typeof item === 'object' && 'msg' in item
            ? String((item as { msg: unknown }).msg)
            : String(item),
        )
        .filter(Boolean);
      if (messages.length > 0) return messages.join('; ');
    }
    if (raw && typeof raw === 'object') {
      try {
        return JSON.stringify(raw);
      } catch {
        // fall through to generic message below
      }
    }
    return err.message || 'Erro desconhecido';
  }
  if (err instanceof Error) return err.message;
  return 'Erro desconhecido';
}

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

// ---------------------------------------------------------------------------
// Create-user dialog — role=dialog, Esc closes, basic Tab focus trap, focus
// moves to the first field on open and returns to the trigger button on
// close. Pattern copied from KeyboardShortcutsHelp in
// lib/keyboard-shortcuts.tsx (the app's existing accessible-dialog example).
// ---------------------------------------------------------------------------

interface CreateUserDialogProps {
  onClose: () => void;
  onCreated: () => void;
}

function CreateUserDialog({ onClose, onCreated }: CreateUserDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const firstFieldRef = useRef<HTMLInputElement>(null);

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [role, setRole] = useState<ClinicalRole>('readonly');
  const [isAdmin, setIsAdmin] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Coherence guard (backend defect C-N1: the API accepts an incoherent
  // is_admin/role combo, e.g. is_admin=true with role='enfermeiro'). The
  // constraint is one-directional — is_admin=true requires role='admin' —
  // so we enforce it by forcing role to 'admin' when the toggle is checked,
  // and disabling manual role selection while it's on. Unchecking the
  // toggle frees the role select again (any role is valid with is_admin
  // false, including 'admin' itself, which the backend permits).
  const handleIsAdminChange = (checked: boolean) => {
    setIsAdmin(checked);
    if (checked) setRole('admin');
  };

  useEffect(() => {
    firstFieldRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== 'Tab') return;
      const dialog = dialogRef.current;
      if (!dialog) return;

      const focusable = dialog.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await createUser({
        username,
        email,
        password,
        display_name: displayName.trim() ? displayName.trim() : undefined,
        is_admin: isAdmin,
        is_active: true,
        role,
      });
      onCreated();
    } catch (err) {
      setSubmitError(formatApiErrorDetail(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    backgroundColor: 'var(--surface-canvas)',
    color: 'var(--text-primary)',
    borderColor: 'var(--border-default)',
    borderWidth: '1px',
    borderStyle: 'solid',
  };

  const labelStyle: React.CSSProperties = { color: 'var(--text-secondary)' };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-user-dialog-title"
        className="w-full max-w-md rounded-lg p-5 shadow-xl"
        style={{ backgroundColor: 'var(--surface-raised)', borderColor: 'var(--border-default)', borderWidth: '1px', borderStyle: 'solid' }}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 id="create-user-dialog-title" className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Novo usuário
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar formulário de novo usuário"
            className="p-1 rounded hover:bg-[var(--surface-overlay)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
            style={{ color: 'var(--text-secondary)' }}
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label htmlFor="new-user-username" className="block text-xs font-medium mb-1" style={labelStyle}>
              Usuário
            </label>
            <input
              ref={firstFieldRef}
              id="new-user-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              maxLength={64}
              className="w-full px-3 py-2 text-sm rounded-[var(--radius-sm)] outline-none focus:ring-2 focus:ring-offset-0"
              style={{ ...inputStyle, '--tw-ring-color': 'var(--severity-watch)' } as React.CSSProperties}
            />
          </div>

          <div>
            <label htmlFor="new-user-email" className="block text-xs font-medium mb-1" style={labelStyle}>
              Email
            </label>
            <input
              id="new-user-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              maxLength={255}
              className="w-full px-3 py-2 text-sm rounded-[var(--radius-sm)] outline-none focus:ring-2 focus:ring-offset-0"
              style={{ ...inputStyle, '--tw-ring-color': 'var(--severity-watch)' } as React.CSSProperties}
            />
          </div>

          <div>
            <label htmlFor="new-user-password" className="block text-xs font-medium mb-1" style={labelStyle}>
              Senha
            </label>
            <input
              id="new-user-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
              className="w-full px-3 py-2 text-sm rounded-[var(--radius-sm)] outline-none focus:ring-2 focus:ring-offset-0"
              style={{ ...inputStyle, '--tw-ring-color': 'var(--severity-watch)' } as React.CSSProperties}
            />
            <p className="mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
              Mínimo de 8 caracteres.
            </p>
          </div>

          <div>
            <label htmlFor="new-user-display-name" className="block text-xs font-medium mb-1" style={labelStyle}>
              Nome de exibição
            </label>
            <input
              id="new-user-display-name"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              maxLength={255}
              className="w-full px-3 py-2 text-sm rounded-[var(--radius-sm)] outline-none focus:ring-2 focus:ring-offset-0"
              style={{ ...inputStyle, '--tw-ring-color': 'var(--severity-watch)' } as React.CSSProperties}
            />
          </div>

          <div>
            <label htmlFor="new-user-role" className="block text-xs font-medium mb-1" style={labelStyle}>
              Função
            </label>
            <select
              id="new-user-role"
              value={role}
              onChange={(e) => setRole(e.target.value as ClinicalRole)}
              disabled={isAdmin}
              className="w-full px-3 py-2 text-sm rounded-[var(--radius-sm)] outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-60"
              style={{ ...inputStyle, '--tw-ring-color': 'var(--severity-watch)' } as React.CSSProperties}
            >
              {CLINICAL_ROLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {isAdmin && (
              <p className="mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
                Fixado em &ldquo;Administrador&rdquo; enquanto o acesso administrativo estiver ativo.
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <input
              id="new-user-is-admin"
              type="checkbox"
              checked={isAdmin}
              onChange={(e) => handleIsAdminChange(e.target.checked)}
              className="size-4 rounded"
              style={{ accentColor: 'var(--severity-watch)' }}
            />
            <label htmlFor="new-user-is-admin" className="text-sm" style={{ color: 'var(--text-primary)' }}>
              Acesso administrativo
            </label>
          </div>

          {submitError && (
            <p role="alert" className="text-xs" style={{ color: 'var(--severity-critical)' }}>
              {submitError}
            </p>
          )}

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-3 py-2 text-sm font-medium rounded-[var(--radius-sm)] transition-colors hover:opacity-80 disabled:opacity-50"
              style={{
                backgroundColor: 'var(--surface-overlay)',
                color: 'var(--text-primary)',
                borderColor: 'var(--border-default)',
                borderWidth: '1px',
                borderStyle: 'solid',
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-[var(--radius-sm)] transition-colors hover:opacity-80 disabled:opacity-50"
              style={{
                backgroundColor: 'var(--severity-normal-wash)',
                color: 'var(--severity-normal)',
              }}
            >
              {isSubmitting && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
              Criar usuário
            </button>
          </div>
        </form>
      </div>
    </div>
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
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const createButtonRef = useRef<HTMLButtonElement>(null);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const closeCreateDialog = () => {
    setIsCreateOpen(false);
    // Focus returns to the button that opened the dialog.
    createButtonRef.current?.focus();
  };

  const handleCreated = () => {
    closeCreateDialog();
    setSuccessMessage('Usuário criado com sucesso.');
    void mutate();
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

  const header = (
    <div className="mb-4 flex items-start justify-between gap-4">
      <div className="flex-1">
        <div className="relative max-w-sm" style={{ color: 'var(--text-secondary)' }}>
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
        {data && (
          <p className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
            {filteredAndSorted.length} de {data.total} usuário{data.total !== 1 ? 's' : ''}
          </p>
        )}
      </div>
      <button
        ref={createButtonRef}
        type="button"
        onClick={() => {
          setSuccessMessage(null);
          setIsCreateOpen(true);
        }}
        className="inline-flex shrink-0 items-center gap-2 px-3 py-2 text-sm font-medium rounded-[var(--radius-sm)] transition-colors hover:opacity-80"
        style={{
          backgroundColor: 'var(--severity-normal-wash)',
          color: 'var(--severity-normal)',
        }}
        aria-label="Criar novo usuário"
      >
        <Plus className="size-4" aria-hidden="true" />
        Novo usuário
      </button>
    </div>
  );

  const dialog = isCreateOpen && (
    <CreateUserDialog onClose={closeCreateDialog} onCreated={handleCreated} />
  );

  const successBanner = successMessage && (
    <p
      role="status"
      className="mb-4 px-3 py-2 text-sm rounded-[var(--radius-sm)]"
      style={{ backgroundColor: 'var(--severity-normal-wash)', color: 'var(--severity-normal)' }}
    >
      {successMessage}
    </p>
  );

  // Error state
  if (error) {
    return (
      <div>
        {header}
        {successBanner}
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
        {dialog}
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div>
        {header}
        <div aria-label="Carregando usuários" aria-busy="true">
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
        {dialog}
      </div>
    );
  }

  // Empty state
  if (!data || data.items.length === 0) {
    return (
      <div>
        {header}
        {successBanner}
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
        {dialog}
      </div>
    );
  }

  return (
    <div>
      {/* Search bar + create button */}
      {header}
      {successBanner}

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
                    className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)]"
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

      {dialog}
    </div>
  );
}
