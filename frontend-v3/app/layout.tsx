import type { Metadata } from 'next';
import { AuthProvider } from '@/lib/auth';
import './globals.css';
import { AppShell } from '@/components/app-shell';

export const metadata: Metadata = {
  title: 'IntensiCare',
  description: 'Plataforma de acompanhamento de pacientes críticos',
};

// Required for the CSP nonce set in middleware.ts to actually reach the
// HTML: nonces are per-request, but nothing else in this tree calls a
// dynamic API (cookies()/headers()), so without this Next would statically
// prerender the shell at build time — before any request/nonce exists —
// and the RSC bootstrap script would ship without a matching nonce,
// reproducing the same hydration failure this change fixes. See
// https://nextjs.org/docs/app/guides/content-security-policy#forcing-dynamic-rendering
export const dynamic = 'force-dynamic';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" data-theme="dark" className="dark h-full antialiased">
      <body className="min-h-full bg-[var(--surface-canvas)] text-[var(--text-primary)]">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-[var(--surface-overlay)] focus:text-[var(--text-primary)] focus:rounded focus:outline-none focus:ring-2 focus:ring-[var(--severity-watch)]"
        >
          Pular para conteúdo principal
        </a>
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
