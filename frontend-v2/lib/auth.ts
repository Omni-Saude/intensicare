'use client';

import { type ClinicalRole } from '@/hooks/useRole';

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
  is_active: boolean;
  role: ClinicalRole | null;
}

// ── In-memory stores (module-scoped) ──
// SECURITY (F-SEC-005): Tokens and user data are NEVER persisted to
// sessionStorage, localStorage, or document.cookie. They live only in
// JavaScript module scope and are lost on page refresh.
//
// Page refresh → re-authentication is required.
// Tab navigation (SPA client-side routing) preserves the session.
// This is an acceptable trade-off for clinical application security:
// no XSS exfiltration vector via browser storage APIs.

let _token: string | null = null;
let _user: UserInfo | null = null;

// --- Token management ---

export function getToken(): string | null {
  return _token;
}

export function setToken(token: string): void {
  _token = token;
}

export function clearToken(): void {
  _token = null;
}

// --- User info ---

export function getUser(): UserInfo | null {
  return _user;
}

export function setUser(user: UserInfo): void {
  _user = user;
}

export function clearUser(): void {
  _user = null;
}

// --- Auth helpers ---

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function isAdmin(): boolean {
  const user = getUser();
  return user?.is_admin === true;
}

export function logout(): void {
  clearToken();
  clearUser();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

// --- JWT decode (for role checks) ---

export function decodeTokenPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const middle = parts[1];
    if (!middle) return null;
    const payload = JSON.parse(atob(middle));
    return payload;
  } catch {
    return null;
  }
}
