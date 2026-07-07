'use client';

import React, { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { ChevronDown, ChevronRight } from 'lucide-react';
import type { FormConfig, FormField } from './types';

// ─── Renderer imports ────────────────────────────────────────────────────────

import StringField from './renderers/StringField';
import SelectField from './renderers/SelectField';
import NumberField from './renderers/NumberField';
import BooleanField from './renderers/BooleanField';
import CheckboxField from './renderers/CheckboxField';
import DateField from './renderers/DateField';
import MaskedField from './renderers/MaskedField';

// ─── Field renderer map ──────────────────────────────────────────────────────

const rendererMap: Record<string, React.ComponentType<{ field: FormField; form: any; error?: string }>> = {
  string: StringField,
  select: SelectField,
  number: NumberField,
  boolean: BooleanField,
  checkbox: CheckboxField,
  date: DateField,
  masked: MaskedField,
  multicheck: StringField, // fallback to multi-input; not used in current forms
};

// ─── Dynamic schema builder ──────────────────────────────────────────────────

function buildZodSchema(config: FormConfig): z.ZodObject<any> {
  const shape: Record<string, any> = {};

  for (const group of config.groups) {
    for (const field of group.fields) {
      let zodField: any;

      switch (field.type) {
        case 'number':
          zodField = z.number({ error: `${field.label} é obrigatório` });
          if (field.min !== undefined) {
            zodField = zodField.min(field.min, `${field.label} deve ser ≥ ${field.min}`);
          }
          if (field.max !== undefined) {
            zodField = zodField.max(field.max, `${field.label} deve ser ≤ ${field.max}`);
          }
          break;

        case 'boolean':
        case 'checkbox':
          zodField = z.boolean({ error: `${field.label} é obrigatório` });
          break;

        case 'multicheck':
          zodField = z.array(z.string());
          break;

        case 'string':
        case 'select':
        case 'date':
        case 'masked':
        default:
          zodField = z.string({ error: `${field.label} é obrigatório` });
          break;
      }

      if (!field.required) {
        zodField = zodField.optional();
      } else {
        // For string types, add a minimum length constraint to prevent empty strings
        if (
          field.type === 'string' ||
          field.type === 'select' ||
          field.type === 'masked'
        ) {
          zodField = zodField.min(1, `${field.label} é obrigatório`);
        }
      }

      shape[field.name] = zodField;
    }
  }

  let schema = z.object(shape);

  // ─── Cross-field validation: atLeastOne ─────────────────────────────────
  if (config.validation?.atLeastOne?.length) {
    schema = schema.superRefine((data: Record<string, any>, ctx) => {
      const atLeastOneFields = config.validation!.atLeastOne!;
      const anyFilled = atLeastOneFields.some((name) => {
        const val = data[name];
        return val !== undefined && val !== null && val !== '';
      });

      if (!anyFilled) {
        for (const name of atLeastOneFields) {
          ctx.addIssue({
            code: 'custom' as const,
            path: [name],
            message: 'Pelo menos um dos campos deve ser preenchido',
          });
        }
      }
    });
  }

  return schema as z.ZodObject<any>;
}

// ─── Component ───────────────────────────────────────────────────────────────

interface FormEngineProps {
  config: FormConfig;
  onSubmit: (data: Record<string, any>) => void | Promise<void>;
  defaultValues?: Record<string, any>;
}

export default function FormEngine({ config, onSubmit, defaultValues }: FormEngineProps) {
  const schema = useMemo(() => buildZodSchema(config), [config]);

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: defaultValues as any,
  });

  const {
    handleSubmit,
    formState: { errors, isSubmitting },
  } = form;

  const onValid = async (data: Record<string, any>) => {
    await onSubmit(data);
  };

  // ─── Collapsible group state ──────────────────────────────────────────────
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>(() => {
    const state: Record<string, boolean> = {};
    for (const group of config.groups) {
      if (group.collapsible) {
        state[group.title] = !group.defaultOpen;
      }
    }
    return state;
  });

  const toggleGroup = (title: string) => {
    setCollapsed((prev) => ({ ...prev, [title]: !prev[title] }));
  };

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onValid)} noValidate>
      <h2
        className="text-lg font-semibold mb-4"
        style={{ color: 'var(--semantic-text-primary)' }}
      >
        {config.title}
      </h2>

      {config.description && (
        <p
          className="text-sm mb-5"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {config.description}
        </p>
      )}

      {config.groups.map((group) => {
        const isCollapsible = group.collapsible === true;
        const isCollapsed = collapsed[group.title] === true;

        return (
          <div key={group.title} className="mb-5">
            {/* Group header */}
            {isCollapsible ? (
              <button
                type="button"
                onClick={() => toggleGroup(group.title)}
                aria-expanded={!isCollapsed}
                className="w-full flex items-center gap-2 text-left mb-3"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {isCollapsed ? (
                  <ChevronRight className="w-4 h-4 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-4 h-4 flex-shrink-0" />
                )}
                <span className="text-sm font-semibold uppercase tracking-wider">
                  {group.title}
                </span>
              </button>
            ) : (
              <h3
                className="text-sm font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {group.title}
              </h3>
            )}

            {/* Group body */}
            {(!isCollapsible || !isCollapsed) && (
              <div>
                {group.fields.map((field) => {
                  const errorMsg = errors[field.name]?.message as string | undefined;
                  const Renderer = rendererMap[field.type] || StringField;

                  return (
                    <Renderer
                      key={field.name}
                      field={field}
                      form={form}
                      error={errorMsg}
                    />
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      {/* Submit area */}
      <div className="mt-6 flex items-center gap-4">
        <button
          type="submit"
          disabled={isSubmitting}
          aria-label="Enviar formulário"
          className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium text-sm transition-all disabled:opacity-50 cursor-pointer"
          style={{
            backgroundColor: 'var(--clinical-severity-normal-fill)',
            color: 'var(--clinical-severity-normal-on-fill)',
          }}
        >
          {isSubmitting ? 'Enviando...' : 'Enviar Avaliação'}
        </button>
      </div>
    </form>
  );
}
