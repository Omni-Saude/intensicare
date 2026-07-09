import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/login', '/register', '/health'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Allow static assets and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/auth') ||
    pathname.startsWith('/favicon') ||
    pathname === '/'
  ) {
    return NextResponse.next();
  }

  // Check for auth token via HttpOnly cookie (F-SEC-005)
  // The backend should set this cookie with Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict
  // The frontend never reads/writes this cookie from JavaScript — it is managed entirely server-side.
  // Until backend adoption, the cookie will be absent on page loads; users re-authenticate via the
  // login page (in-memory token survives SPA navigation but not refresh).
  const token = request.cookies.get('access_token')?.value;
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Admin role guard — redirect non-admin users away from /admin/* routes
  if (pathname.startsWith('/admin')) {
    try {
      const parts = token.split('.');
      const middle = parts[1];
      if (!middle) {
        throw new Error('Malformed token');
      }
      const payload = JSON.parse(atob(middle));
      const isAdmin =
        payload.is_admin === true ||
        payload.role === 'admin' ||
        payload.user_role === 'admin';

      if (!isAdmin) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
      }
    } catch {
      // If JWT decode fails (malformed token), redirect to login
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
