'use client';

import React from 'react';
import type { UseFormReturn } from 'react-hook-form';
import { Controller } from 'react-hook-form';
import type { FormField } from '../types';

interface Props {
  field: FormField;
  form: UseFormReturn<any>;
  error?: string;
}

export default function BooleanField({ field, form, error }: Props) {
  return (
    <div className="mb-5">
      <Controller
        name={field.name}
        control={form.control}
        render={({ field: controllerField }) => (
          <div className="flex items-center gap-4 p-3 rounded-lg"
            style={{
              border: '1px solid var(--semantic-border-default)',
              backgroundColor: controllerField.value
                ? 'var(--clinical-severity-watch-wash)'
                : 'var(--semantic-surface-canvas)',
            }}
          >
            <button
              type="button"
              onClick={() => controllerField.onChange(!controllerField.value)}
              aria-label={field.label}
              aria-checked={!!controllerField.value}
              role="switch"
              className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0"
              style={{
                backgroundColor: controllerField.value
                  ? 'var(--clinical-severity-watch-signal)'
                  : 'var(--semantic-border-default)',
              }}
            >
              <span
                className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                style={{
                  transform: controllerField.value ? 'translateX(22px)' : 'translateX(4px)',
                }}
              />
            </button>
            <div className="flex flex-col">
              <span
                className="text-sm font-medium"
                style={{ color: 'var(--semantic-text-primary)' }}
              >
                {field.label}
              </span>
              {field.hint && (
                <span
                  className="text-xs mt-0.5"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {field.hint}
                </span>
              )}
            </div>
          </div>
        )}
      />
      {error && (
        <p
          className="text-xs mt-1.5 font-medium"
          style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
