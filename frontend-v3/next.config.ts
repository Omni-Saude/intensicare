import type { NextConfig } from "next";

const API_URL = process.env.API_URL || 'http://localhost:8000';

const nextConfig: NextConfig = {
  transpilePackages: ['recharts'],

  // Proxy /api/v1/* → backend (dev and prod). WebSocket is NOT proxied here:
  // Next.js rewrites() do not reliably proxy WebSocket upgrades, so
  // lib/websocket.ts connects directly to the backend's /api/v1/ws
  // (resolved from NEXT_PUBLIC_WS_URL — see frontend-v3/.env.local) with a
  // ?token=<JWT> query param instead of going through this rewrite layer.
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${API_URL}/api/v1/:path*`,
      },
    ];
  },

  // CSP is NOT set here. next.config.ts's headers() are static and computed
  // once at build time, so they can't carry a fresh script-src nonce per
  // request — and a nonce is required for Next's inline RSC bootstrap
  // script to execute under a strict script-src (see the Invariant/
  // self.__next_r hydration failure this fixed). The full CSP, including
  // the nonce and the connect-src WebSocket/API allowlist (ADR-0034), lives
  // in middleware.ts instead. Keeping it in exactly one place avoids the
  // browser silently intersecting two different policies.
};

export default nextConfig;
