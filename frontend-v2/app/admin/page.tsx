'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, UserCog, Sliders, Activity, Users, AlertTriangle, Gauge } from 'lucide-react';
import Layout from '@/components/Layout';
import { fetchAdminStats, type AdminStatsResponse } from '@/lib/api';

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<AdminStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAdminStats()
      .then(setStats)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load stats'))
      .finally(() => setLoading(false));
  }, []);

  const adminCards = [
    {
      title: 'User Management',
      description: 'Manage users, roles, and access permissions',
      icon: UserCog,
      href: '/admin/users',
      color: 'from-blue-500 to-indigo-600',
      bgIcon: 'bg-blue-50 text-blue-600',
    },
    {
      title: 'Threshold Configuration',
      description: 'Configure clinical score thresholds and alert rules',
      icon: Sliders,
      href: '/admin/thresholds',
      color: 'from-amber-500 to-orange-600',
      bgIcon: 'bg-amber-50 text-amber-600',
    },
  ];

  const statCards = [
    {
      label: 'Total Users',
      value: stats?.total_users ?? '—',
      icon: Users,
      color: 'from-blue-500 to-indigo-600',
    },
    {
      label: 'Active Alerts',
      value: stats?.active_alerts ?? '—',
      icon: AlertTriangle,
      color: 'from-red-500 to-rose-600',
    },
    {
      label: 'Thresholds Configured',
      value: stats?.thresholds_configured ?? '—',
      icon: Gauge,
      color: 'from-amber-500 to-orange-600',
    },
  ];

  return (
    <Layout>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Administration</h1>
            <p className="text-slate-500 text-sm mt-0.5">System configuration and user management</p>
          </div>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {statCards.map((stat) => (
          <div
            key={stat.label}
            style={{ borderColor: 'var(--semantic-border-default)' }}
            className="bg-white rounded-xl border p-5 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">{stat.label}</p>
                {loading ? (
                  <div
                    style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}
                    className="h-8 w-16 rounded animate-pulse mt-1"
                  />
                ) : error ? (
                  <p className="text-2xl font-bold text-red-400 mt-0.5">!</p>
                ) : (
                  <p className="text-2xl font-bold text-slate-800 mt-0.5">{stat.value}</p>
                )}
              </div>
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center`}>
                <stat.icon className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Admin cards */}
      <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {adminCards.map((card) => (
          <button
            key={card.href}
            onClick={() => router.push(card.href)}
            style={{ borderColor: 'var(--semantic-border-default)' }}
            className="group text-left bg-white rounded-xl border p-6 shadow-sm hover:shadow-md transition-all hover:border-slate-300"
          >
            <div className="flex items-start gap-4">
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center flex-shrink-0`}
              >
                <card.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">
                  {card.title}
                </h3>
                <p className="text-sm text-slate-500 mt-1">{card.description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* System info */}
      <div
        style={{ borderColor: 'var(--semantic-border-default)' }}
        className="mt-8 bg-white rounded-xl border p-6 shadow-sm"
      >
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
          System Information
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Version</div>
            <div className="font-semibold text-slate-700">0.1.0</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Environment</div>
            <div className="font-semibold text-slate-700">Development</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Auth Mode</div>
            <div className="font-semibold text-slate-700">JWT (MVP)</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Frontend</div>
            <div className="font-semibold text-slate-700">Next.js 14</div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
