'use client';

import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * React Error Boundary class component.
 * Catches rendering errors in its children and displays a fallback UI
 * with an error message and a retry button.
 * Uses var(--semantic-*) and var(--clinical-severity-*) tokens for styling.
 */
export default class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): React.ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          className="border rounded-xl p-6 m-4"
        >
          <div className="flex items-start gap-3">
            <AlertTriangle
              className="w-6 h-6 flex-shrink-0 mt-0.5"
              style={{ color: 'var(--clinical-severity-critical-signal)' }}
              aria-hidden="true"
            />
            <div className="min-w-0">
              <h2 className="font-semibold text-lg">Something went wrong</h2>
              <p className="text-sm mt-1 opacity-90">
                {this.state.error?.message || 'An unexpected error occurred while rendering this section.'}
              </p>
              <button
                onClick={this.handleRetry}
                className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                style={{
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                  borderColor: 'var(--semantic-border-default)',
                  border: '1px solid var(--semantic-border-default)',
                }}
              >
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
                Retry
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
