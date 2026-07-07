'use client';

import React, { useCallback } from 'react';
import type { UseFormReturn } from 'react-hook-form';
import type { FormField } from '../types';

interface Props {
  field: FormField;
  form: UseFormReturn<any>;
  error?: string;
}

/**
 * Apply a simple mask pattern to a value.
 * Pattern chars: '#' = digit, 'A' = letter, '*' = alphanumeric, others = literal.
 */
function applyMask(value: string, mask: string): string {
  if (!mask) return value;

  let result = '';
  let valueIndex = 0;
  const cleaned = value.replace(/[^a-zA-Z0-9]/g, '');

  for (let i = 0; i < mask.length && valueIndex < cleaned.length; i++) {
    const maskChar = mask[i]!;
    const valueChar = cleaned[valueIndex]!;

    if (maskChar === '#') {
      if (/\d/.test(valueChar)) {
        result += valueChar;
        valueIndex++;
      } else {
        valueIndex++; // skip non-digit
        i--; // retry this mask position
      }
    } else if (maskChar === 'A') {
      if (/[a-zA-Z]/.test(valueChar)) {
        result += valueChar;
        valueIndex++;
      } else {
        valueIndex++;
        i--;
      }
    } else if (maskChar === '*') {
      result += valueChar;
      valueIndex++;
    } else {
      result += maskChar;
    }
  }

  return result;
}

export default function MaskedField({ field, form, error }: Props) {
  const { onChange, onBlur, name, ref } = form.register(field.name);
  const mask = field.mask ?? '';

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const raw = e.target.value;
      const masked = applyMask(raw, mask);
      // Create a synthetic event-like object that react-hook-form can handle
      onChange({ target: { value: masked, name } } as any);
    },
    [onChange, mask, name],
  );

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
        onChange={handleChange}
        onBlur={onBlur}
        type="text"
        placeholder={field.placeholder ?? mask}
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
