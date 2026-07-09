'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  RefreshCw,
  Shield,
  UserCheck,
  UserX,
  Mail,
  Clock,
  Plus,
  UserPlus,
} from 'lucide-react';
import Layout from '@/components/Layout';
import DrawerBuilder from '@/components/DrawerBuilder';
import {
  fetchUsers,
  updateUser,
  createUser,
  type UserResponse,
} from '@/lib/api';
import { getUser } from '@/lib/auth';

const ABAC_ROLES = [
  { value: 'physician', label: 'Médico(a)' },
  { value: 'nurse', label: 'Enfermeiro(a)' },
  { value: 'pharmacist', label: 'Farmacêutico(a)' },
  { value: 'lab_tech', label: 'Técnico(a) de Lab.' },
  { value: 'admin', label: 'Administrador' },
  { value: 'viewer', label: 'Visualizador' },
  { value: 'auditor', label: 'Auditor' },
] as const;

type AbacRole = (typeof ABAC_ROLES)[number]['value'];

export default function AdminUsersPage() {
  const router = useRouter();
  const currentUser = getUser();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<number | null>(null);

  // Create user modal state
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    username: '',
    email: '',
    password: '',
    display_name: '',
    role: 'viewer' as AbacRole,
    is_admin: false,
  });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Role editing state
  const [editingRole, setEditingRole] = useState<number | null>(null);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchUsers();
      setUsers(result.users);
      setTotal(result.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar usuários');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // --- Role change ---
  const handleRoleChange = async (userId: number, role: string) => {
    setUpdating(userId);
    try {
      const updated = await updateUser(userId, { role });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
      setEditingRole(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao atualizar função');
      setTimeout(() => setError(null), 3000);
    } finally {
      setUpdating(null);
    }
  };

  // --- Admin toggle ---
  const handleAdminToggle = async (userId: number, isAdmin: boolean) => {
    setUpdating(userId);
    try {
      const updated = await updateUser(userId, { is_admin: !isAdmin });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao atualizar status de admin');
      setTimeout(() => setError(null), 3000);
    } finally {
      setUpdating(null);
    }
  };

  // --- Active toggle ---
  const handleActiveToggle = async (userId: number, isActive: boolean) => {
    setUpdating(userId);
    try {
      const updated = await updateUser(userId, { is_active: !isActive });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao atualizar status');
      setTimeout(() => setError(null), 3000);
    } finally {
      setUpdating(null);
    }
  };

  // --- Create user ---
  const handleCreateUser = async () => {
    if (!createForm.username || !createForm.email || !createForm.password) {
      setCreateError('Usuário, e-mail e senha são obrigatórios');
      return;
    }
    if (createForm.password.length < 8) {
      setCreateError('A senha deve ter pelo menos 8 caracteres');
      return;
    }

    setCreating(true);
    setCreateError(null);
    try {
      const newUser = await createUser({
        username: createForm.username,
        email: createForm.email,
        password: createForm.password,
        display_name: createForm.display_name || undefined,
        is_admin: createForm.is_admin,
        role: createForm.role,
      });
      setUsers((prev) => [...prev, newUser]);
      setTotal((prev) => prev + 1);
      setShowCreate(false);
      setCreateForm({
        username: '',
        email: '',
        password: '',
        display_name: '',
        role: 'viewer',
        is_admin: false,
      });
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'Falha ao criar usuário');
    } finally {
      setCreating(false);
    }
  };

  function formatDate(iso: string | null): string {
    if (!iso) return 'Nunca';
    return new Date(iso).toLocaleString();
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/admin')}
          style={{ color: 'var(--semantic-text-secondary)' }}
           className="inline-flex items-center gap-1.5 text-sm mb-3 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
        >
           <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          Voltar ao Admin
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 style={{ color: 'var(--semantic-text-primary)' }} className="text-2xl font-bold">Gerenciamento de Usuários</h1>
            <p style={{ color: 'var(--semantic-text-secondary)' }} className="text-sm mt-1">
              {total} usuário{total !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadUsers}
              style={{ borderColor: 'var(--semantic-border-default)', color: 'var(--semantic-text-secondary)' }}
              className="flex items-center gap-2 px-3 py-2 bg-[var(--semantic-surface-raised)] border rounded-lg text-sm hover:bg-[var(--semantic-surface-canvas)]"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
              Atualizar
            </button>
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-medium rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all shadow-md"
            >
              <UserPlus className="w-4 h-4" aria-hidden="true" />
              Adicionar Usuário
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          className="border rounded-xl p-3 text-sm mb-4"
        >
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 animate-spin" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
        </div>
      )}

      {/* Users table */}
      {!loading && users.length > 0 && (
        <div
          style={{ borderColor: 'var(--semantic-border-default)' }}
          className="bg-[var(--semantic-surface-raised)] rounded-xl border shadow-sm overflow-hidden"
        >
          {/* Table header */}
          <div
            style={{
              backgroundColor: 'var(--semantic-surface-canvas)',
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-secondary)',
            }}
            className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 border-b text-xs font-semibold uppercase tracking-wider"
          >
            <div className="col-span-2">Usuário</div>
            <div className="col-span-2">E-mail</div>
            <div className="col-span-2 text-center">Função ABAC</div>
            <div className="col-span-1 text-center">Admin</div>
            <div className="col-span-1 text-center">Status</div>
            <div className="col-span-2 text-center">Criado em</div>
            <div className="col-span-2 text-center">Ações</div>
          </div>

          {/* User rows */}
          <div className="divide-y divide-[var(--semantic-border-default)]">
            {users.map((user) => {
              const isSelf = user.id === currentUser?.id;
              const isUpdating = updating === user.id;
              return (
                <div
                  key={user.id}
                  className={`grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-6 py-4 items-center ${
                    isSelf ? 'bg-blue-50/30' : ''
                  }`}
                >
                  {/* User info */}
                  <div className="md:col-span-2">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[var(--semantic-text-secondary)] to-[var(--semantic-text-primary)] flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        {user.display_name?.[0]?.toUpperCase() || user.username[0]?.toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div style={{ color: 'var(--semantic-text-primary)' }} className="font-medium text-sm truncate">
                          {user.display_name || user.username}
                          {isSelf && (
                            <span className="ml-1.5 text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full font-medium">
                              Você
                            </span>
                          )}
                        </div>
                        <div style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs">@{user.username}</div>
                      </div>
                    </div>
                  </div>

                  {/* Email */}
                  <div style={{ color: 'var(--semantic-text-secondary)' }} className="md:col-span-2 flex items-center gap-1.5 text-sm">
                    <Mail className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
                    <span className="truncate">{user.email}</span>
                  </div>

                  {/* ABAC Role dropdown */}
                  <div className="md:col-span-2 flex justify-center">
                    {editingRole === user.id ? (
                      <select
                        value={user.role || 'viewer'}
                        onChange={(e) => handleRoleChange(user.id, e.target.value)}
                        disabled={isUpdating || isSelf}
                        style={{ borderColor: 'var(--semantic-border-default)' }}
                        className="px-2 py-1 text-xs border rounded-lg bg-[var(--semantic-surface-raised)] focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none disabled:opacity-40"
                      >
                        {ABAC_ROLES.map((r) => (
                          <option key={r.value} value={r.value}>
                            {r.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <button
                        onClick={() => !isSelf && setEditingRole(user.id)}
                        disabled={isSelf}
                        className="px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                        title={isSelf ? 'Não pode alterar sua própria função' : 'Clique para alterar função'}
                      >
                        {ABAC_ROLES.find((r) => r.value === user.role)?.label ||
                          user.role ||
                          'Visualizador'}
                      </button>
                    )}
                  </div>

                  {/* Admin badge */}
                  <div className="md:col-span-1 flex justify-center">
                    <span
                      style={{
                        backgroundColor: user.is_admin ? undefined : 'var(--semantic-surface-canvas)',
                        color: user.is_admin ? undefined : 'var(--semantic-text-secondary)',
                      }}
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        user.is_admin
                          ? 'bg-purple-100 text-purple-700'
                          : ''
                      }`}
                    >
                      <Shield className="w-3 h-3" aria-hidden="true" />
                      {user.is_admin ? 'Sim' : 'Não'}
                    </span>
                  </div>

                  {/* Status */}
                  <div className="md:col-span-1 flex justify-center">
                    <span
                      style={{
                        backgroundColor: user.is_active
                          ? 'var(--clinical-severity-normal-wash)'
                          : 'var(--clinical-severity-critical-wash)',
                        color: user.is_active
                          ? 'var(--clinical-severity-normal-on-surface)'
                          : 'var(--clinical-severity-critical-on-surface)',
                      }}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                    >
                      {user.is_active ? (
                        <UserCheck className="w-3 h-3" aria-hidden="true" />
                      ) : (
                        <UserX className="w-3 h-3" aria-hidden="true" />
                      )}
                      {user.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </div>

                  {/* Created date */}
                  <div style={{ color: 'var(--semantic-text-secondary)' }} className="md:col-span-2 flex justify-center items-center gap-1 text-xs">
                    <Clock className="w-3 h-3 flex-shrink-0" aria-hidden="true" />
                    <span className="truncate">{formatDate(user.created_at)}</span>
                  </div>

                  {/* Actions */}
                  <div className="md:col-span-2 flex justify-center gap-2">
                    <button
                      onClick={() => handleAdminToggle(user.id, user.is_admin)}
                      disabled={isUpdating || isSelf}
                      style={{ borderColor: 'var(--semantic-border-default)' }}
                      className="px-2.5 py-1 text-xs rounded-lg border hover:bg-[var(--semantic-surface-canvas)] disabled:opacity-40 transition-colors"
                      title={isSelf ? 'Não pode alterar seu próprio status de admin' : user.is_admin ? 'Remover admin' : 'Tornar admin'}
                    >
                      {isUpdating ? '...' : user.is_admin ? 'Rebaixar' : 'Promover'}
                    </button>
                    <button
                      onClick={() => handleActiveToggle(user.id, user.is_active)}
                      disabled={isUpdating || isSelf}
                      style={{
                        borderColor: user.is_active
                          ? 'var(--clinical-severity-critical-signal)'
                          : 'var(--clinical-severity-normal-signal)',
                        color: user.is_active
                          ? 'var(--clinical-severity-critical-on-surface)'
                          : 'var(--clinical-severity-normal-on-surface)',
                      }}
                      className={`px-2.5 py-1 text-xs rounded-lg border transition-colors disabled:opacity-40 ${
                        user.is_active
                          ? 'hover:bg-[var(--clinical-severity-critical-wash)]'
                          : 'hover:bg-[var(--clinical-severity-normal-wash)]'
                      }`}
                      title={isSelf ? 'Não pode desativar a si mesmo' : ''}
                    >
                      {isUpdating ? '...' : user.is_active ? 'Desativar' : 'Ativar'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && users.length === 0 && (
        <div
          style={{ borderColor: 'var(--semantic-border-default)' }}
          className="text-center py-20 bg-[var(--semantic-surface-raised)] rounded-xl border"
        >
          <Shield className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }} aria-hidden="true" />
          <p style={{ color: 'var(--semantic-text-secondary)' }} className="font-medium">Nenhum usuário encontrado</p>
        </div>
      )}

      {/* --- Create User Modal --- */}
      <DrawerBuilder open={showCreate} onClose={() => setShowCreate(false)} title="Criar Novo Usuário" size="md">
        {createError && (
          <div
            style={{
              backgroundColor: 'var(--clinical-severity-critical-wash)',
              borderColor: 'var(--clinical-severity-critical-signal)',
              color: 'var(--clinical-severity-critical-on-surface)',
            }}
            className="border rounded-lg p-3 text-sm mb-4"
          >
            {createError}
          </div>
        )}

        <div className="space-y-3">
          <div>
             <label htmlFor="create-username" style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs font-semibold uppercase tracking-wider block mb-1">
              Username *
            </label>
            <input
               id="create-username"
              type="text"
              value={createForm.username}
              onChange={(e) => setCreateForm((f) => ({ ...f, username: e.target.value }))}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
              placeholder="johndoe"
            />
          </div>
          <div>
             <label htmlFor="create-email" style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs font-semibold uppercase tracking-wider block mb-1">
              Email *
            </label>
            <input
               id="create-email"
              type="email"
              value={createForm.email}
              onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
              placeholder="john@hospital.com"
            />
          </div>
          <div>
             <label htmlFor="create-password" style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs font-semibold uppercase tracking-wider block mb-1">
              Senha * (mín. 8 caracteres)
            </label>
            <input
               id="create-password"
              type="password"
              value={createForm.password}
              onChange={(e) => setCreateForm((f) => ({ ...f, password: e.target.value }))}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
              placeholder="••••••••"
            />
          </div>
          <div>
             <label htmlFor="create-display-name" style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs font-semibold uppercase tracking-wider block mb-1">
              Nome de Exibição
            </label>
            <input
               id="create-display-name"
              type="text"
              value={createForm.display_name}
              onChange={(e) => setCreateForm((f) => ({ ...f, display_name: e.target.value }))}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
              placeholder="Dr. John Doe"
            />
          </div>
          <div>
             <label htmlFor="create-role" style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs font-semibold uppercase tracking-wider block mb-1">
              Função ABAC
            </label>
            <select
               id="create-role"
              value={createForm.role}
              onChange={(e) => setCreateForm((f) => ({ ...f, role: e.target.value as AbacRole }))}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="w-full px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
            >
              {ABAC_ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={createForm.is_admin}
              onChange={(e) => setCreateForm((f) => ({ ...f, is_admin: e.target.checked }))}
              className="rounded border-[var(--semantic-border-default)] text-blue-600 focus:ring-blue-500"
            />
            <span style={{ color: 'var(--semantic-text-primary)' }} className="text-sm">Conceder privilégios de administrador</span>
          </label>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={() => setShowCreate(false)}
            style={{ color: 'var(--semantic-text-secondary)', borderColor: 'var(--semantic-border-default)' }}
            className="flex-1 px-4 py-2 text-sm font-medium bg-[var(--semantic-surface-raised)] border rounded-lg hover:bg-[var(--semantic-surface-canvas)] transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleCreateUser}
            disabled={creating}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg hover:from-cyan-600 hover:to-blue-700 shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {creating ? (
              <RefreshCw className="w-4 h-4 animate-spin" aria-hidden="true" />
            ) : (
              <Plus className="w-4 h-4" aria-hidden="true" />
            )}
            {creating ? 'Criando...' : 'Criar Usuário'}
          </button>
        </div>
      </DrawerBuilder>
    </Layout>
  );
}
