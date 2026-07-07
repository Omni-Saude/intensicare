'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Activity } from 'lucide-react';
import { registerApi } from '@/lib/api';

export default function RegisterPage() {
  const router = useRouter();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    try {
      await registerApi({
        username,
        email,
        password,
        display_name: displayName || undefined,
      });
      setSuccess(true);
      setTimeout(() => router.push('/login'), 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha no registro');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 mb-4 shadow-lg shadow-cyan-500/25">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Intensicare</h1>
          <p className="text-slate-400 text-sm mt-1">Criar Conta</p>
        </div>

        <div className="bg-white/5 backdrop-blur-lg border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-lg font-semibold text-white mb-6">Registrar</h2>

          {error && (
            <div
              style={{ backgroundColor: 'var(--clinical-severity-critical-wash)' }}
              className="mb-4 p-3 border border-[var(--clinical-severity-critical-on-surface)]/30 rounded-lg text-[var(--clinical-severity-critical-on-surface)] text-sm"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              style={{ backgroundColor: 'var(--clinical-severity-normal-wash)' }}
              className="mb-4 p-3 border border-[var(--clinical-severity-normal-on-surface)]/30 rounded-lg text-[var(--clinical-severity-normal-on-surface)] text-sm"
            >
              Conta criada com sucesso! Redirecionando para o login...
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-1.5">
                Usuário *
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                maxLength={64}
                minLength={3}
                placeholder="Escolha um nome de usuário"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                className="w-full px-4 py-2.5 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1.5">
                E-mail *
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@hospital.com"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                className="w-full px-4 py-2.5 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label htmlFor="displayName" className="block text-sm font-medium text-slate-300 mb-1.5">
                Nome de Exibição
              </label>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                maxLength={128}
                placeholder="Dr. Smith"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                className="w-full px-4 py-2.5 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1.5">
                Senha *
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                maxLength={128}
                minLength={8}
                placeholder="Pelo menos 8 caracteres"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                className="w-full px-4 py-2.5 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !username || !email || !password}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-cyan-500/25"
            >
              {loading ? 'Criando conta...' : 'Criar Conta'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a href="/login" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
              Já tem uma conta? Entrar
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
