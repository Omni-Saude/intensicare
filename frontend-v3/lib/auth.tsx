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

  // BUG-F1-01 fix: logout() used to only call apiLogout() + setState, with
  // no navigation. The backend was correctly invalidating the session, but
  // the client stayed on the current route with the SWR-cached dashboard
  // (patient names, vitals) still mounted and rendered — indefinite PHI
  // exposure on a shared ICU terminal after clicking "Confirmar saída".
  //
  // Dashboard pages here don't gate rendering on isAuthenticated (e.g.
  // app/page.tsx renders BedGrid straight off its own useSWR state), so
  // clearing this context's state alone would not have hidden that grid.
  // A `router.push('/login')` would swap the visible route, but SWR's
  // in-memory cache is a module-level singleton that survives client-side
  // navigation — a subsequent back-button press at this shared terminal
  // could re-render the cached PHI instantly, before the 401 handler in
  // lib/api.ts even has a chance to redirect. A full browser navigation
  // (`window.location.assign`) tears down the entire JS realm — including
  // that SWR cache and any component state — so nothing can be resurrected
  // by in-app navigation. This mirrors the existing hard-redirect pattern
  // used by the 401 handler in lib/api.ts.
  const logout = useCallback(() => {
    // Synchronous, immediate UI feedback (defense in depth): clear local
    // auth state right away so anything gating on isAuthenticated (e.g.
    // the sidebar user footer) stops rendering session info before the
    // network round-trip below even starts.
    setState({ user: null, isLoading: false, isAuthenticated: false });

    // Fail-closed for privacy: apiLogout() already clears the in-memory
    // token synchronously (before its own network call) and treats its own
    // fetch failure as non-fatal, but we still guard here — even if
    // server-side revocation errors out for some other reason, the user
    // must still end up on /login with no PHI left rendered.
    apiLogout()
      .catch(() => {
        // Best-effort server-side revocation failed — session state is
        // already cleared client-side (above); still navigate below.
      })
      .finally(() => {
        window.location.assign('/login');
      });
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
