'use client';

import React, { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Activity, Eye, EyeOff } from 'lucide-react';
import { loginApi, setApiToken, type LoginRequest } from '@/lib/api';
import { setUser } from '@/lib/auth';
import { type ClinicalRole } from '@/hooks/useRole';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get('redirect') || '/dashboard';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const result = await loginApi({ username, password });
      const accessToken = result.access_token;
      if (!accessToken) {
        throw new Error('No access token received');
      }
      setApiToken(accessToken);

      // Decode JWT to extract user info
      try {
        const tokenParts = accessToken.split('.');
        const middlePart = tokenParts[1];
        if (!middlePart) {
          throw new Error('Invalid token format');
        }
        const payload = JSON.parse(atob(middlePart));
        setUser({
          id: payload.user_id || 0,
          username: payload.sub || username,
          email: '',
          display_name: username,
          is_admin: payload.is_admin || false,
          is_active: true,
          role: (payload.role as ClinicalRole) || null,
        });
      } catch {
        // Fallback minimal user
        setUser({
          id: 0,
          username,
          email: '',
          display_name: username,
          is_admin: false,
          is_active: true,
          role: null,
        });
      }

      router.push(redirect);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 mb-4 shadow-lg shadow-cyan-500/25">
             <Activity className="w-8 h-8 text-white" aria-hidden="true" />
          </div>
          <h1 className="text-2xl font-bold text-white">Intensicare</h1>
          <p className="text-slate-400 text-sm mt-1">Centro de Comando Clínico</p>
        </div>

        {/* Login card */}
        <div className="bg-white/5 backdrop-blur-lg border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-lg font-semibold text-white mb-1">Bem-vindo de volta</h2>
          <p className="text-slate-400 text-sm mb-5">Faça login para continuar</p>

          {error && (
            <div
              style={{ backgroundColor: 'var(--clinical-severity-critical-wash)' }}
              className="mb-4 p-3 border border-[var(--clinical-severity-critical-on-surface)]/30 rounded-lg text-[var(--clinical-severity-critical-on-surface)] text-sm"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-1.5">
                Usuário
              </label>
              <input
                id="username"
                type="text"
                 autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                maxLength={64}
                placeholder="Digite seu usuário"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                className="w-full px-4 py-2.5 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1.5">
                Senha
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                   autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  maxLength={128}
                  placeholder="Digite sua senha"
                  style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                  className="w-full px-4 py-2.5 pr-10 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                   className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 p-1.5 rounded-lg focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                   aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !username || !password}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-cyan-500/25"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a href="/register" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
              Precisa de uma conta? Cadastre-se
            </a>
          </div>
        </div>

        <p className="text-center text-slate-600 text-xs mt-6">
          Intensicare v0.1.0 — Clinical Decision Support System
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
          <div className="text-slate-400">Carregando...</div>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
