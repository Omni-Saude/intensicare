'use client';

import React from 'react';
import type { UseFormReturn } from 'react-hook-form';
import { Controller } from 'react-hook-form';
import * as Select from '@radix-ui/react-select';
import { ChevronDown } from 'lucide-react';
import type { FormField } from '../types';

interface Props {
  field: FormField;
  form: UseFormReturn<any>;
  error?: string;
}

export default function SelectField({ field, form, error }: Props) {
  return (
    <div className="mb-5">
      <label
        htmlFor={field.name}
        className="text-sm font-medium mb-2 block"
        style={{ color: 'var(--semantic-text-secondary)' }}
      >
        {field.label}
      </label>
      <Controller
        name={field.name}
        control={form.control}
        render={({ field: controllerField }) => (
          <Select.Root
            value={controllerField.value ?? ''}
            onValueChange={(value) => controllerField.onChange(value)}
            name={field.name}
          >
            <Select.Trigger
              id={field.name}
              aria-required={field.required ?? false}
              aria-label={field.label}
              className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 flex items-center justify-between"
              style={{
                borderColor: error ? 'var(--clinical-severity-critical-signal)' : 'var(--semantic-border-default)',
                color: controllerField.value ? 'var(--semantic-text-primary)' : 'var(--semantic-text-secondary)',
                backgroundColor: 'var(--semantic-surface-canvas)',
              }}
            >
              <Select.Value placeholder={field.placeholder ?? 'Selecionar...'} />
              <Select.Icon>
                <ChevronDown className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} />
              </Select.Icon>
            </Select.Trigger>

            <Select.Portal>
              <Select.Content
                position="popper"
                sideOffset={4}
                className="z-50 rounded-lg border shadow-lg overflow-hidden"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  width: 'var(--radix-select-trigger-width)',
                  maxHeight: 'var(--radix-select-content-available-height)',
                }}
              >
                <Select.Viewport className="p-1">
                  {field.options?.map((opt) => (
                    <Select.Item
                      key={opt.value}
                      value={opt.value}
                      className="px-3 py-2 text-sm rounded cursor-pointer outline-none data-[highlighted]:bg-blue-50 data-[highlighted]:outline-none"
                      style={{ color: 'var(--semantic-text-primary)' }}
                    >
                      <Select.ItemText>{opt.label}</Select.ItemText>
                    </Select.Item>
                  ))}
                </Select.Viewport>
              </Select.Content>
            </Select.Portal>
          </Select.Root>
        )}
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
