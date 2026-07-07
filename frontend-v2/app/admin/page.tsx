'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, UserCog, Sliders, Activity, Users, AlertTriangle, Gauge, RefreshCw } from 'lucide-react';
import Layout from '@/components/Layout';
import { fetchAdminStats, type AdminStatsResponse } from '@/lib/api';

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<AdminStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = () => {
    setLoading(true);
    setError(null);
    fetchAdminStats()
      .then(setStats)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load stats'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadStats();
  }, []);

  const adminCards = [
    {
      title: 'Gerenciamento de Usuários',
      description: 'Gerenciar usuários, funções e permissões de acesso',
      icon: UserCog,
      href: '/admin/users',
      color: 'from-blue-500 to-indigo-600',
      bgIcon: 'bg-blue-50 text-blue-600',
    },
    {
      title: 'Configuração de Limiares',
      description: 'Configurar limiares de pontuação clínica e regras de alerta',
      icon: Sliders,
      href: '/admin/thresholds',
      color: 'from-[var(--clinical-severity-watch-on-surface)] to-[var(--clinical-severity-urgent-on-surface)]',
      bgIcon: 'bg-[var(--clinical-severity-watch-wash)] text-[var(--clinical-severity-watch-on-surface)]',
    },
  ];

  const statCards = [
    {
      label: 'Total de Usuários',
      value: stats?.total_users ?? '—',
      icon: Users,
      color: 'from-blue-500 to-indigo-600',
    },
    {
      label: 'Alertas Ativos',
      value: stats?.active_alerts ?? '—',
      icon: AlertTriangle,
      color: 'from-[var(--clinical-severity-critical-signal)] to-[var(--clinical-severity-critical-fill)]',
    },
    {
      label: 'Limiares Configurados',
      value: stats?.thresholds_configured ?? '—',
      icon: Gauge,
      color: 'from-[var(--clinical-severity-watch-on-surface)] to-[var(--clinical-severity-urgent-on-surface)]',
    },
  ];

  return (
    <Layout>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Administração</h1>
            <p className="text-slate-500 text-sm mt-0.5">Configuração do sistema e gerenciamento de usuários</p>
          </div>
        </div>
      </div>

      {/* Global error banner */}
      {error && (
        <div
          className="border rounded-xl p-4 mb-6"
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          role="alert"
          aria-live="assertive"
        >
          <div className="flex items-center justify-between">
            <div>
            <p className="font-medium">Falha ao carregar painel administrativo</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
            <button
              onClick={loadStats}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border transition-all"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
                borderColor: 'var(--semantic-border-default)',
              }}
            >
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Tentar novamente
            </button>
          </div>
        </div>
      )}

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
                  <p className="text-2xl font-bold text-[var(--clinical-severity-critical-on-surface)] mt-0.5">!</p>
                ) : (
                  <p className="text-2xl font-bold text-slate-800 mt-0.5">{stat.value}</p>
                )}
              </div>
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center`}>
                <stat.icon className="w-5 h-5 text-white" aria-hidden="true" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Admin cards */}
      <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Ações Rápidas</h2>
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
                <card.icon className="w-6 h-6 text-white" aria-hidden="true" />
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
          Informações do Sistema
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Versão</div>
            <div className="font-semibold text-slate-700">0.1.0</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Ambiente</div>
            <div className="font-semibold text-slate-700">Development</div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg">
            <div className="text-xs text-slate-400 mb-1">Modo de Autenticação</div>
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
