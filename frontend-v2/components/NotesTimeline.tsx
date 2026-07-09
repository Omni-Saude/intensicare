'use client';

import React, { useState } from 'react';
import { AlertTriangle, Clock, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import type { Evolucao } from '@/lib/clinical-notes-types';
import {
  formatNoteType,
  getTypeColor,
  getTypeIcon,
} from '@/lib/clinical-notes-types';

// ─── Props ───────────────────────────────────────────────────────────────────

interface NotesTimelineProps {
  notes: Evolucao[];
  isLoading?: boolean;
  error?: string | null;
  /** Se true, mostra a mensagem de "Nenhuma evolução" filtrada em vez da padrão */
  emptyMessage?: string;
}

// ─── Simple Markdown Renderer ────────────────────────────────────────────────
// Suporte básico: **bold**, ## headings, linhas em branco

function renderSimpleMarkdown(content: string): React.ReactNode {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let inParagraph = false;
  let paraLines: React.ReactNode[] = [];

  const flushParagraph = () => {
    if (paraLines.length > 0) {
      elements.push(
        <p key={elements.length} className="mb-3 leading-relaxed">
          {paraLines.reduce((acc, node, i) => (
            <React.Fragment key={i}>
              {acc}
              {i > 0 && <br />}
              {node}
            </React.Fragment>
          ))}
        </p>,
      );
      paraLines = [];
    }
    inParagraph = false;
  };

  for (const line of lines) {
    // Heading
    const headingMatch = line.match(/^##\s+(.+)/);
    if (headingMatch) {
      flushParagraph();
      elements.push(
        <h3
          key={elements.length}
          className="text-base font-semibold mt-4 mb-1"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {renderBold(headingMatch[1]!)}
        </h3>,
      );
      continue;
    }

    const heading1Match = line.match(/^#\s+(.+)/);
    if (heading1Match) {
      flushParagraph();
      elements.push(
        <h2
          key={elements.length}
          className="text-lg font-bold mt-4 mb-2"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {renderBold(heading1Match[1]!)}
        </h2>,
      );
      continue;
    }

    // Horizontal rule
    if (/^-{3,}$/.test(line.trim())) {
      flushParagraph();
      elements.push(
        <hr
          key={elements.length}
          className="my-3"
          style={{ borderColor: 'var(--semantic-border-default)' }}
        />,
      );
      continue;
    }

    // Empty line → flush paragraph
    if (line.trim() === '') {
      flushParagraph();
      continue;
    }

    // Regular line — accumulated into paragraph
    if (!inParagraph) {
      inParagraph = true;
    }
    paraLines.push(renderBoldAndItalic(line));
  }
  flushParagraph();

  return <div className="text-sm">{elements}</div>;
}

/** Processa **bold** e _itálico_ em um fragmento de texto. */
function renderBoldAndItalic(text: string): React.ReactNode {
  return renderBold(text);
}

function renderBold(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    const boldMatch = part.match(/^\*\*(.+)\*\*$/);
    if (boldMatch) {
      return (
        <strong key={i} className="font-semibold">
          {boldMatch[1]}
        </strong>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

// ─── Format Date ─────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  try {
    const date = new Date(iso);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

// ─── Content Preview ─────────────────────────────────────────────────────────

function getPreview(content: string, maxChars = 150): string {
  const firstLine = content.split('\n').find((l) => l.trim() !== '' && !l.startsWith('#'));
  if (!firstLine) return content.slice(0, maxChars);
  return firstLine.length > maxChars
    ? firstLine.slice(0, maxChars) + '…'
    : firstLine;
}

// ─── Skeleton ────────────────────────────────────────────────────────────────

function TimelineSkeleton(): React.ReactElement {
  return (
    <div className="space-y-4 py-2" role="status" aria-label="Carregando evoluções">
      {[0, 1, 2, 3].map((i) => (
        <div key={i} className="flex gap-4 animate-pulse">
          <div className="flex flex-col items-center">
            <div
              className="w-10 h-10 rounded-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            {i < 3 && (
              <div
                className="w-0.5 flex-1 mt-1"
                style={{
                  backgroundColor: 'var(--semantic-surface-overlay)',
                  minHeight: '40px',
                }}
              />
            )}
          </div>
          <div className="flex-1 space-y-2 pb-4">
            <div className="flex gap-2">
              <div
                className="h-5 rounded w-20"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
              <div
                className="h-5 rounded w-32"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            </div>
            <div
              className="h-4 rounded w-2/3"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div
              className="h-3 rounded w-1/3"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function NotesTimeline({
  notes,
  isLoading = false,
  error = null,
  emptyMessage,
}: NotesTimelineProps): React.ReactElement {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // ─── Loading state ────────────────────────────────────────────────────────
  if (isLoading) {
    return <TimelineSkeleton />;
  }

  // ─── Error state ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-2 px-3 py-3 rounded-lg text-sm"
        style={{
          backgroundColor: 'var(--feedback-error-bg-dark)',
          color: 'var(--feedback-error-text-dark)',
          borderColor: 'var(--feedback-error-border-dark)',
          borderWidth: '1px',
        }}
      >
        <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // ─── Empty state ──────────────────────────────────────────────────────────
  if (notes.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-8 text-sm"
        style={{ color: 'var(--semantic-text-secondary)' }}
        role="status"
        aria-label="Nenhuma evolução registrada"
      >
        <FileText className="w-10 h-10 opacity-30" aria-hidden="true" />
        <p>{emptyMessage ?? 'Nenhuma evolução registrada'}</p>
      </div>
    );
  }

  // ─── Timeline ─────────────────────────────────────────────────────────────
  return (
    <div className="relative pl-1" role="list" aria-label="Linha do tempo de evoluções clínicas">
      {notes.map((note, index) => {
        const colors = getTypeColor(note.type);
        const Icon = getTypeIcon(note.type);
        const isExpanded = expandedId === note.id;
        const isLast = index === notes.length - 1;

        return (
          <div
            key={note.id}
            className="flex gap-4 group"
            role="listitem"
          >
            {/* Icon node + connector */}
            <div className="flex flex-col items-center">
              <div
                className="relative flex items-center justify-center rounded-full transition-all flex-shrink-0"
                style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: colors.fill,
                  borderColor: colors.signal,
                  borderWidth: '2px',
                  borderStyle: 'solid',
                  marginTop: '2px',
                }}
                aria-hidden="true"
              >
                <Icon
                  className="w-5 h-5"
                  style={{ color: colors.onFill }}
                />
              </div>
              {!isLast && (
                <div
                  className="w-0.5 flex-1 mt-1"
                  style={{
                    backgroundColor: 'var(--semantic-border-default)',
                    minHeight: '24px',
                  }}
                  aria-hidden="true"
                />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 pb-6">
              <button
                onClick={() => setExpandedId(isExpanded ? null : note.id)}
                className="w-full text-left rounded-lg transition-colors p-3 -ml-1 -mt-1 hover:bg-black/5 dark:hover:bg-white/5 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                aria-expanded={isExpanded}
                aria-label={`${isExpanded ? 'Recolher' : 'Expandir'} ${formatNoteType(note.type)} — ${formatDate(note.created_at)}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      {/* Type badge */}
                      <span
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
                        style={{
                          backgroundColor: colors.fill,
                          color: colors.onFill,
                          borderWidth: '1px',
                          borderColor: colors.signal,
                          borderStyle: 'solid',
                        }}
                      >
                        <Icon className="w-3 h-3" aria-hidden="true" />
                        {formatNoteType(note.type)}
                      </span>
                      {/* Author */}
                      <span
                        className="text-xs font-medium"
                        style={{ color: 'var(--semantic-text-primary)' }}
                      >
                        {note.created_by}
                      </span>
                    </div>

                    {/* Timestamp */}
                    <div
                      className="flex items-center gap-1 mt-1.5 text-xs"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      <Clock className="w-3 h-3" aria-hidden="true" />
                      {formatDate(note.created_at)}
                      {note.updated_at && (
                        <span className="italic">
                          (atualizado {formatDate(note.updated_at)})
                        </span>
                      )}
                    </div>

                    {/* Preview (collapsed) */}
                    {!isExpanded && (
                      <p
                        className="mt-2 text-sm leading-relaxed line-clamp-2"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {getPreview(note.content)}
                      </p>
                    )}
                  </div>

                  {/* Expand/collapse chevron */}
                  <div className="flex-shrink-0 mt-1">
                    {isExpanded ? (
                      <ChevronUp
                        className="w-4 h-4"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                        aria-hidden="true"
                      />
                    ) : (
                      <ChevronDown
                        className="w-4 h-4"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                        aria-hidden="true"
                      />
                    )}
                  </div>
                </div>

                {/* Expanded content */}
                {isExpanded && (
                  <div
                    className="mt-4 pt-4 border-t"
                    style={{
                      borderColor: 'var(--semantic-border-default)',
                      color: 'var(--semantic-text-primary)',
                    }}
                  >
                    {renderSimpleMarkdown(note.content)}
                  </div>
                )}
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
