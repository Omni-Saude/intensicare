/** @type {import('next').NextConfig} */

// ---------------------------------------------------------------------------
// Security headers — W3 Observability + Security Headers (GAP 3)
// ---------------------------------------------------------------------------
const securityHeaders = [
  // Content-Security-Policy: Restringe fontes de recursos carregados.
  // Ajuste 'script-src' e 'connect-src' conforme necessário para produção.
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Next.js dev requer unsafe-eval
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob:",
      "font-src 'self'",
      "connect-src 'self' http://localhost:8000",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
  },
  // HTTP Strict-Transport-Security (HSTS) — força HTTPS
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  // Previne clickjacking
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  // Previne MIME-type sniffing
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  // Referrer-Policy
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  // Permissions-Policy (restringe APIs do navegador)
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
  },
];

const nextConfig = {
  reactStrictMode: true,

  // -----------------------------------------------------------------------
  // Security headers aplicados em todas as rotas
  // -----------------------------------------------------------------------
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/auth/:path*',
        destination: 'http://localhost:8000/auth/:path*',
      },
      {
        source: '/admin/:path*',
        destination: 'http://localhost:8000/admin/:path*',
      },
      {
        source: '/health',
        destination: 'http://localhost:8000/health',
      },
    ];
  },
};

module.exports = nextConfig;
