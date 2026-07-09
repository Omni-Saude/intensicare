import type { Metadata } from 'next';
import './globals.css';
import ErrorBoundary from '@/components/ErrorBoundary';
import { OverlayStackProvider } from '@/hooks/useOverlayStack';
import TenantProvider from '@/components/TenantProvider';

export const metadata: Metadata = {
  title: 'Intensicare — Clinical Command Center',
  description: 'ICU monitoring, alert management, and clinical decision support',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" data-theme="dark" data-tenant="default">
      <body className="min-h-screen">
        <TenantProvider tenant="default" />
        <OverlayStackProvider>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </OverlayStackProvider>
      </body>
    </html>
  );
}
