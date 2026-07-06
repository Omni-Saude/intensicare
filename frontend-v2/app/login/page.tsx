'use client';

import React, { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Activity, Eye, EyeOff } from 'lucide-react';
import { loginApi, type LoginRequest } from '@/lib/api';
import { setToken, setUser } from '@/lib/auth';

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
      setToken(accessToken);

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
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Intensicare</h1>
          <p className="text-slate-400 text-sm mt-1">Clinical Command Center</p>
        </div>

        {/* Login card */}
        <div className="bg-white/5 backdrop-blur-lg border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-lg font-semibold text-white mb-6">Sign In</h2>

          {error && (
            <div
              style={{ backgroundColor: 'var(--clinical-severity-critical-wash)' }}
              className="mb-4 p-3 border border-red-500/30 rounded-lg text-red-400 text-sm"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-1.5">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter your username"
                style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                className="w-full px-4 py-2.5 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                  style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
                  className="w-full px-4 py-2.5 pr-10 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !username || !password}
              className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-cyan-500/25"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a href="/register" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
              Need an account? Register
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
          <div className="text-slate-400">Loading...</div>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
