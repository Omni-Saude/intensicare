import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// CSP lives here, not in next.config.ts: next.config.ts's headers() are
// static and baked in at build time, so they can't carry a per-request
// nonce. Next.js parses the Content-Security-Policy header it finds on the
// *request* (see requestHeaders below) and auto-applies the nonce it
// contains to its own inline RSC bootstrap script and framework chunks —
// that's the documented mechanism (https://nextjs.org/docs/app/guides/content-security-policy)
// and it's what makes hydration work under a strict script-src. This is
// the single source of truth for CSP; next.config.ts no longer sets it.
//
// connect-src (WebSocket/API allowlist) is unrelated to the nonce fix and
// is preserved as configured for ADR-0034 (direct-to-backend WebSocket).
export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const { pathname } = request.nextUrl;

  const publicPaths = ['/login'];

  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const isDev = process.env.NODE_ENV === 'development';

  // 'unsafe-eval' is dev-only: React uses eval() in development to
  // reconstruct server-side error stacks in the browser. Neither React nor
  // Next.js use eval in production, so it's dropped there entirely.
  const cspHeader = isDev
    ? `default-src 'self'; connect-src 'self' ws://localhost:8000 wss://localhost:8000 http://localhost:8000 ws://localhost:3000 wss://localhost:3000; script-src 'self' 'nonce-${nonce}' 'strict-dynamic' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'; report-uri /api/csp-report`
    : `default-src 'self'; connect-src 'self' wss:; script-src 'self' 'nonce-${nonce}' 'strict-dynamic'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'; report-uri /api/csp-report; upgrade-insecure-requests`;

  if (!token && !publicPaths.includes(pathname)) {
    const redirectResponse = NextResponse.redirect(new URL('/login', request.url));
    redirectResponse.headers.set('Content-Security-Policy', cspHeader);
    return redirectResponse;
  }

  // Propagate both the raw nonce (for any future manual <Script nonce={...}>
  // via headers()) and the CSP header itself on the *request* — Next.js
  // needs the CSP header on the request to auto-nonce its own scripts.
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-nonce', nonce);
  requestHeaders.set('Content-Security-Policy', cspHeader);

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  });
  response.headers.set('Content-Security-Policy', cspHeader);

  return response;
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
