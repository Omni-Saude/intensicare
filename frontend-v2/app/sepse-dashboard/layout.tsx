import type { Metadata } from 'next';
import ErrorBoundary from '@/components/ErrorBoundary';
import Layout from '@/components/Layout';

export const metadata: Metadata = {
  title: 'Sepse Dashboard — Intensicare',
  description: 'Monitoramento de sepse: triagem, critérios clínicos e bundle Hour-1',
};

export default function SepseDashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ErrorBoundary>
      <Layout>{children}</Layout>
    </ErrorBoundary>
  );
}
