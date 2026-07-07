'use client';

import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';

interface DrawerBuilderProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'full';
}

const sizeClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  full: 'inset-0 w-full h-full max-w-none rounded-none',
};

const isFull = (size: string) => size === 'full';

export default function DrawerBuilder({
  open,
  onClose,
  title,
  children,
  size = 'md',
}: DrawerBuilderProps) {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <Dialog.Portal>
        {/* Overlay */}
        <Dialog.Overlay className="fixed inset-0 bg-black/40 z-40 data-[state=open]:animate-[fadeIn_150ms_ease-out]" />

        {/* Content */}
        <Dialog.Content
          className={
            isFull(size)
              ? 'fixed inset-0 z-50 overflow-auto'
              : `fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full ${sizeClasses[size]} rounded-2xl shadow-xl overflow-auto max-h-[90vh]`
          }
          style={{
            backgroundColor: 'var(--semantic-surface-raised)',
            color: 'var(--semantic-text-primary)',
          }}
        >
          {/* Header: title (optional) + close button */}
          <div className={isFull(size) ? 'p-0' : 'px-6 pt-6 pb-0'}>
            {title && (
              <Dialog.Title
                className="text-lg font-semibold pr-8"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {title}
              </Dialog.Title>
            )}

            <Dialog.Close asChild>
              <button
                onClick={onClose}
                className={`absolute top-4 right-4 p-1 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 transition-colors z-10 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center`}
                aria-label="Close"
              >
                <X className="w-5 h-5" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
              </button>
            </Dialog.Close>
          </div>

          {/* Body */}
          <div className={isFull(size) ? '' : 'px-6 pb-6 pt-4'}>
            {children}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
