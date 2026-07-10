'use client';

import { useState, useEffect } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter/dist/esm/prism-light';
import yaml from 'react-syntax-highlighter/dist/esm/languages/prism/yaml';
import oneDark from 'react-syntax-highlighter/dist/esm/styles/prism/one-dark';
import { Code2, AlertTriangle, Loader2 } from 'lucide-react';
import type { Pathway } from '@/lib/api';

SyntaxHighlighter.registerLanguage('yaml', yaml);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function pathwayToYaml(pathway: Pathway): string {
  const lines: string[] = [];

  lines.push(`# Trilha Clínica: ${pathway.name}`);
  lines.push(`# ID: ${pathway.id} | Slug: ${pathway.slug || 'N/A'}`);
  lines.push('');
  lines.push(`id: ${pathway.id}`);
  lines.push(`name: "${pathway.name}"`);
  if (pathway.slug) lines.push(`slug: "${pathway.slug}"`);
  if (pathway.description) lines.push(`description: "${pathway.description}"`);
  lines.push(`active: ${pathway.active !== false}`);
  lines.push('');

  if (pathway.states && pathway.states.length > 0) {
    lines.push('states:');
    for (const state of pathway.states) {
      lines.push(`  - id: "${state.id}"`);
      lines.push(`    name: "${state.name}"`);
      lines.push(`    order: ${state.order}`);
      if (state.description) lines.push(`    description: "${state.description}"`);
      if (state.is_terminal) lines.push(`    is_terminal: true`);
    }
    lines.push('');
  }

  if (pathway.criteria && pathway.criteria.length > 0) {
    lines.push('criteria:');
    for (const crit of pathway.criteria) {
      lines.push(`  - id: "${crit.id}"`);
      lines.push(`    name: "${crit.name}"`);
      lines.push(`    category: ${crit.category}`);
      if (crit.description) lines.push(`    description: "${crit.description}"`);
      if (crit.unit) lines.push(`    unit: "${crit.unit}"`);
      if (crit.normal_range) lines.push(`    normal_range: "${crit.normal_range}"`);
      if (crit.alert_threshold) lines.push(`    alert_threshold: "${crit.alert_threshold}"`);
      if (crit.met !== undefined) lines.push(`    met: ${crit.met}`);
      if (crit.value) lines.push(`    value: "${crit.value}"`);
      if (crit.evaluated_at) lines.push(`    evaluated_at: "${crit.evaluated_at}"`);
    }
  }

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface YamlViewerProps {
  pathway: Pathway | null;
  isLoading: boolean;
  error?: string;
}

// ---------------------------------------------------------------------------
// States
// ---------------------------------------------------------------------------

function YamlLoading() {
  return (
    <div
      className="flex flex-col items-center justify-center py-12 gap-3 text-[var(--text-secondary)]"
      role="status"
      aria-label="Carregando definição YAML"
    >
      <Loader2 className="h-6 w-6 animate-spin" />
      <span className="text-sm">Carregando YAML...</span>
    </div>
  );
}

function YamlError({ message }: { message: string }) {
  return (
    <div
      className="flex flex-col items-center justify-center py-12 gap-3"
      role="alert"
      aria-label="Erro ao carregar YAML"
    >
      <AlertTriangle className="h-8 w-8 text-[var(--severity-urgent)]" />
      <p className="text-sm text-[var(--text-secondary)]">{message}</p>
    </div>
  );
}

function YamlEmpty() {
  return (
    <div
      className="flex flex-col items-center justify-center py-12 gap-3 text-[var(--text-secondary)]"
      role="status"
      aria-label="Nenhuma trilha selecionada"
    >
      <Code2 className="h-8 w-8 opacity-40" />
      <p className="text-sm">Selecione uma trilha para visualizar sua definição YAML</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// YamlViewer
// ---------------------------------------------------------------------------

export function YamlViewer({
  pathway,
  isLoading,
  error,
}: YamlViewerProps) {
  const [yamlText, setYamlText] = useState<string>('');

  useEffect(() => {
    if (pathway) {
      setYamlText(pathwayToYaml(pathway));
    } else {
      setYamlText('');
    }
  }, [pathway]);

  if (isLoading) return <YamlLoading />;
  if (error) return <YamlError message={error} />;
  if (!pathway) return <YamlEmpty />;

  return (
    <div
      className="rounded-lg border border-[var(--border-default)] overflow-hidden"
      role="region"
      aria-label={`Definição YAML de ${pathway.name}`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-[var(--surface-overlay)] border-b border-[var(--border-default)]">
        <Code2 className="h-4 w-4 text-[var(--text-secondary)]" />
        <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wide">
          Definição YAML
        </span>
        <span className="text-xs text-[var(--text-secondary)] ml-auto">
          {pathway.slug || pathway.name}
        </span>
      </div>

      {/* Code */}
      <SyntaxHighlighter
        language="yaml"
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: 'var(--surface-canvas)',
          fontSize: '0.8125rem',
          lineHeight: '1.6',
          borderRadius: 0,
          border: 'none',
        }}
        codeTagProps={{
          style: {
            fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace',
          },
        }}
        showLineNumbers
        lineNumberStyle={{
          color: 'var(--text-secondary)',
          opacity: 0.4,
          minWidth: '2.5em',
          paddingRight: '1em',
          textAlign: 'right',
          userSelect: 'none',
        }}
      >
        {yamlText}
      </SyntaxHighlighter>
    </div>
  );
}

export { pathwayToYaml };
