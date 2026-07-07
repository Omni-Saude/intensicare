'use client';

import React from 'react';
import type { UseFormReturn } from 'react-hook-form';
import type { FormField } from '../types';

interface Props {
  field: FormField;
  form: UseFormReturn<any>;
  error?: string;
}

export default function NumberField({ field, form, error }: Props) {
  const { onChange, onBlur, name, ref } = form.register(field.name, {
    valueAsNumber: true,
  });

  return (
    <div className="mb-5">
      <label
        htmlFor={field.name}
        className="text-sm font-medium mb-2 block"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {field.label}
      </label>
      <input
        id={field.name}
        name={name}
        ref={ref}
        onChange={onChange}
        onBlur={onBlur}
        type="number"
        min={field.min}
        max={field.max}
        step={1}
        placeholder={field.placeholder}
        aria-required={field.required ?? false}
        aria-label={field.label}
        className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
        style={{
          borderColor: error ? 'var(--clinical-severity-critical-signal)' : 'var(--semantic-border-default)',
          color: 'var(--semantic-text-primary)',
          backgroundColor: 'var(--semantic-surface-canvas)',
        }}
      />
      {field.hint && !error && (
        <p
          className="text-xs mt-1.5"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {field.hint}
        </p>
      )}
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
