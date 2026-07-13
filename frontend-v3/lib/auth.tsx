'use client';

import type { ReactNode } from 'react';
import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import {
  getToken,
  setToken,
  ensureSession,
  login as apiLogin,
  logout as apiLogout,
  type UserInfo,
} from './api';

// Decodes the (in-memory only, non-persisted) token synchronously to build
// the initial auth state. Safe to call during render/SSR: getToken() reads a
// plain in-module variable (never localStorage), so it is always `null` on a
// fresh module instance and only becomes non-null after an explicit login()
// call later in the same client session.
//
// When there is no in-memory token, the state starts as `isLoading: true`
// rather than jumping straight to "unauthenticated": on a fresh page load
// (F5 reload / deep-link) the browser may still hold a valid HttpOnly
// `refresh_token` cookie even though this module's `_token` was just reset
// to `null`. The mount effect below (via ensureSession()) resolves that
// ambiguity — session bootstrap CRITICAL B-C2 fix — before isLoading flips
// to false, so consumers that gate rendering/redirects on isLoading don't
// treat "haven't checked yet" as "logged out".
function initialAuthState(): AuthState {
  const token = getToken();
  if (!token) {
    return { user: null, isLoading: true, isAuthenticated: false };
  }

  // Decode JWT payload to get user info without an extra network call
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const user: UserInfo = {
      id: payload.sub || '',
      name: payload.name || '',
      email: payload.email || '',
      role: payload.role || 'viewer',
      is_admin: payload.is_admin === true,
    };
    return { user, isLoading: false, isAuthenticated: true };
  } catch {
    // Invalid token format — keep default (unauthenticated) state
    return { user: null, isLoading: false, isAuthenticated: false };
  }
}

// ---------- types ----------

interface AuthState {
  user: UserInfo | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

// ---------- context ----------

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ---------- provider ----------

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(initialAuthState);

  // Session bootstrap (CRITICAL B-C2 fix): on mount, if no token survived
  // in memory (always true on a full reload / deep-link, since _token is a
  // plain module-level variable — see lib/api.ts), try to recover the
  // session from the HttpOnly refresh_token cookie via POST
  // /api/v1/auth/refresh. ensureSession() is memoized/single-flight, so if
  // a page's own data fetch (e.g. useSWR firing on mount) already kicked
  // off the same bootstrap through request<T>, this just awaits that
  // in-flight call instead of firing a second one.
  useEffect(() => {
    if (getToken()) {
      // initialAuthState() already derived a valid user synchronously
      // (e.g. AuthProvider remounting during client-side navigation, not a
      // full page load) — nothing to bootstrap.
      return;
    }

    let cancelled = false;
    ensureSession().then((user) => {
      if (cancelled) return;
      setState(
        user
          ? { user, isLoading: false, isAuthenticated: true }
          : { user: null, isLoading: false, isAuthenticated: false },
      );
    });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await apiLogin(username, password);
    setToken(response.access_token);
    setState({
      user: response.user,
      isLoading: false,
      isAuthenticated: true,
    });
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setState({ user: null, isLoading: false, isAuthenticated: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// ---------- hook ----------

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
