import type { Metadata } from 'next';
import './globals.css';

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
    <html lang="pt-BR" data-theme="dark">
      <body className="min-h-screen">
        {children}
      </body>
    </html>
  );
}
