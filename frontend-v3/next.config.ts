import type { NextConfig } from "next";

const API_URL = process.env.API_URL || 'http://localhost:8000';

const nextConfig: NextConfig = {
  transpilePackages: ['recharts'],

  // Proxy /api/v1/* → backend (dev and prod)
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${API_URL}/api/v1/:path*`,
      },
      // WebSocket proxy
      {
        source: '/ws',
        destination: `${API_URL}/ws`,
      },
    ];
  },

  // CSP: allow WebSocket + API for dev and prod (ADR-0034)
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: process.env.NODE_ENV === 'production'
              ? "default-src 'self'; connect-src 'self' wss://intensicare.api; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'; report-uri /api/csp-report; upgrade-insecure-requests"
              : "default-src 'self'; connect-src 'self' ws://localhost:8000 wss://localhost:8000 http://localhost:8000 ws://localhost:3000 wss://localhost:3000; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'; report-uri /api/csp-report",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
