'use client';

import React from 'react';
import type { UseFormReturn } from 'react-hook-form';
import { CheckCircle } from 'lucide-react';
import type { FormField } from '../types';

interface Props {
  field: FormField;
  form: UseFormReturn<any>;
  error?: string;
}

export default function CheckboxField({ field, form, error }: Props) {
  const { onChange, onBlur, name, ref } = form.register(field.name);

  // We need to use a hidden checkbox approach since we styled it with custom UI
  const value = form.watch(field.name);

  return (
    <div className="mb-5">
      <div className="flex items-start gap-3">
        <button
          type="button"
          onClick={() => {
            form.setValue(field.name, !value, { shouldValidate: true });
          }}
          aria-label={field.label}
          aria-checked={!!value}
          role="checkbox"
          className="flex-shrink-0 mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
          style={{
            borderColor: value
              ? 'var(--clinical-severity-watch-signal)'
              : 'var(--semantic-border-default)',
            backgroundColor: value
              ? 'var(--clinical-severity-watch-fill)'
              : 'transparent',
          }}
        >
          {value && (
            <CheckCircle className="w-3.5 h-3.5" style={{ color: 'white' }} />
          )}
        </button>
        <div>
          <span
            className="text-sm font-medium"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            {field.label}
          </span>
          {field.hint && (
            <p
              className="text-xs mt-0.5"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {field.hint}
            </p>
          )}
        </div>
      </div>
      {/* Hidden native input for accessibility and form registration */}
      <input
        type="checkbox"
        id={field.name}
        name={name}
        ref={ref}
        onChange={onChange}
        onBlur={onBlur}
        checked={!!value}
        aria-hidden="true"
        className="sr-only"
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
