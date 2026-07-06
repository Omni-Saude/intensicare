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
  X,
  UserPlus,
} from 'lucide-react';
import Layout from '@/components/Layout';
import {
  fetchUsers,
  updateUser,
  createUser,
  type UserResponse,
} from '@/lib/api';
import { getUser } from '@/lib/auth';

const ABAC_ROLES = [
  { value: 'physician', label: 'Physician' },
  { value: 'nurse', label: 'Nurse' },
  { value: 'pharmacist', label: 'Pharmacist' },
  { value: 'lab_tech', label: 'Lab Technician' },
  { value: 'admin', label: 'Admin' },
  { value: 'viewer', label: 'Viewer' },
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
      setError(err instanceof Error ? err.message : 'Failed to load users');
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
      setError(err instanceof Error ? err.message : 'Failed to update role');
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
      setError(err instanceof Error ? err.message : 'Failed to update admin status');
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
      setError(err instanceof Error ? err.message : 'Failed to update status');
      setTimeout(() => setError(null), 3000);
    } finally {
      setUpdating(null);
    }
  };

  // --- Create user ---
  const handleCreateUser = async () => {
    if (!createForm.username || !createForm.email || !createForm.password) {
      setCreateError('Username, email, and password are required');
      return;
    }
    if (createForm.password.length < 8) {
      setCreateError('Password must be at least 8 characters');
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
      setCreateError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setCreating(false);
    }
  };

  function formatDate(iso: string | null): string {
    if (!iso) return 'Never';
    return new Date(iso).toLocaleString();
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/admin')}
          className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-3 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Admin
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">User Management</h1>
            <p className="text-slate-500 text-sm mt-1">
              {total} user{total !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadUsers}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-medium rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all shadow-md"
            >
              <UserPlus className="w-4 h-4" />
              Add User
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-red-700 text-sm mb-4">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 text-slate-400 animate-spin" />
        </div>
      )}

      {/* Users table */}
      {!loading && users.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {/* Table header */}
          <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <div className="col-span-2">User</div>
            <div className="col-span-2">Email</div>
            <div className="col-span-2 text-center">ABAC Role</div>
            <div className="col-span-1 text-center">Admin</div>
            <div className="col-span-1 text-center">Status</div>
            <div className="col-span-2 text-center">Created</div>
            <div className="col-span-2 text-center">Actions</div>
          </div>

          {/* User rows */}
          <div className="divide-y divide-slate-100">
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
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        {user.display_name?.[0]?.toUpperCase() || user.username[0]?.toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-slate-800 text-sm truncate">
                          {user.display_name || user.username}
                          {isSelf && (
                            <span className="ml-1.5 text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full font-medium">
                              You
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-400">@{user.username}</div>
                      </div>
                    </div>
                  </div>

                  {/* Email */}
                  <div className="md:col-span-2 flex items-center gap-1.5 text-sm text-slate-600">
                    <Mail className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span className="truncate">{user.email}</span>
                  </div>

                  {/* ABAC Role dropdown */}
                  <div className="md:col-span-2 flex justify-center">
                    {editingRole === user.id ? (
                      <select
                        value={user.role || 'viewer'}
                        onChange={(e) => handleRoleChange(user.id, e.target.value)}
                        disabled={isUpdating || isSelf}
                        className="px-2 py-1 text-xs border border-slate-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none disabled:opacity-40"
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
                        title={isSelf ? 'Cannot change your own role' : 'Click to change role'}
                      >
                        {ABAC_ROLES.find((r) => r.value === user.role)?.label ||
                          user.role ||
                          'Viewer'}
                      </button>
                    )}
                  </div>

                  {/* Admin badge */}
                  <div className="md:col-span-1 flex justify-center">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        user.is_admin
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-slate-100 text-slate-500'
                      }`}
                    >
                      <Shield className="w-3 h-3" />
                      {user.is_admin ? 'Yes' : 'No'}
                    </span>
                  </div>

                  {/* Status */}
                  <div className="md:col-span-1 flex justify-center">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {user.is_active ? (
                        <UserCheck className="w-3 h-3" />
                      ) : (
                        <UserX className="w-3 h-3" />
                      )}
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  {/* Created date */}
                  <div className="md:col-span-2 flex justify-center items-center gap-1 text-xs text-slate-400">
                    <Clock className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">{formatDate(user.created_at)}</span>
                  </div>

                  {/* Actions */}
                  <div className="md:col-span-2 flex justify-center gap-2">
                    <button
                      onClick={() => handleAdminToggle(user.id, user.is_admin)}
                      disabled={isUpdating || isSelf}
                      className="px-2.5 py-1 text-xs rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 transition-colors"
                      title={isSelf ? 'Cannot change your own admin status' : user.is_admin ? 'Remove admin' : 'Make admin'}
                    >
                      {isUpdating ? '...' : user.is_admin ? 'Demote' : 'Promote'}
                    </button>
                    <button
                      onClick={() => handleActiveToggle(user.id, user.is_active)}
                      disabled={isUpdating || isSelf}
                      className={`px-2.5 py-1 text-xs rounded-lg border transition-colors disabled:opacity-40 ${
                        user.is_active
                          ? 'border-red-200 text-red-600 hover:bg-red-50'
                          : 'border-green-200 text-green-600 hover:bg-green-50'
                      }`}
                      title={isSelf ? 'Cannot deactivate yourself' : ''}
                    >
                      {isUpdating ? '...' : user.is_active ? 'Deactivate' : 'Activate'}
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
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <Shield className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 font-medium">No users found</p>
        </div>
      )}

      {/* --- Create User Modal --- */}
      {showCreate && (
        <div
          className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowCreate(false);
          }}
        >
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-blue-600" />
                Create New User
              </h2>
              <button
                onClick={() => setShowCreate(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {createError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm mb-4">
                {createError}
              </div>
            )}

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                  Username *
                </label>
                <input
                  type="text"
                  value={createForm.username}
                  onChange={(e) => setCreateForm((f) => ({ ...f, username: e.target.value }))}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  placeholder="johndoe"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={createForm.email}
                  onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  placeholder="john@hospital.com"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                  Password * (min 8 chars)
                </label>
                <input
                  type="password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm((f) => ({ ...f, password: e.target.value }))}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                  Display Name
                </label>
                <input
                  type="text"
                  value={createForm.display_name}
                  onChange={(e) => setCreateForm((f) => ({ ...f, display_name: e.target.value }))}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                  placeholder="Dr. John Doe"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                  ABAC Role
                </label>
                <select
                  value={createForm.role}
                  onChange={(e) => setCreateForm((f) => ({ ...f, role: e.target.value as AbacRole }))}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
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
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-slate-700">Grant admin privileges</span>
              </label>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreate(false)}
                className="flex-1 px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateUser}
                disabled={creating}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg hover:from-cyan-600 hover:to-blue-700 shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {creating ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                {creating ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
