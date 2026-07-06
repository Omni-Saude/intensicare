'use client';

import React, { useState } from 'react';
import {
  Users,
  FileText,
  AlertTriangle,
  Clock,
  Pill,
  ClipboardList,
  Printer,
  Download,
  CheckCircle,
  Search,
  UserCheck,
  Edit3,
  Save,
  ShieldAlert,
} from 'lucide-react';
import Layout from '@/components/Layout';

// ─── Types ──────────────────────────────────────────────────────────────────

type SectionName = 'summary' | 'activeIssues' | 'pendingActions' | 'medications';

interface HandoffSection {
  name: SectionName;
  label: string;
  icon: React.ReactNode;
  content: string;
}

interface PatientOption {
  mpiId: string;
  name: string;
  bedId?: string;
  status: 'stable' | 'watch' | 'critical';
}

const MOCK_PATIENTS: PatientOption[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bedId: 'ICU-1-01', status: 'watch' },
  { mpiId: 'MPI-002', name: 'Maria Santos', bedId: 'ICU-1-02', status: 'stable' },
  { mpiId: 'MPI-003', name: 'Carlos Oliveira', bedId: 'ICU-2-05', status: 'critical' },
  { mpiId: 'MPI-004', name: 'Ana Costa', bedId: 'ER-03', status: 'stable' },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

function statusColour(status: PatientOption['status']): string {
  switch (status) {
    case 'critical':
      return 'var(--clinical-severity-critical-signal)';
    case 'watch':
      return 'var(--clinical-severity-watch-signal)';
    default:
      return 'var(--clinical-severity-normal-signal)';
  }
}

function statusWash(status: PatientOption['status']): string {
  switch (status) {
    case 'critical':
      return 'var(--clinical-severity-critical-wash)';
    case 'watch':
      return 'var(--clinical-severity-watch-wash)';
    default:
      return 'var(--clinical-severity-normal-wash)';
  }
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function HandoffPage() {
  const [selectedPatients, setSelectedPatients] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState('');
  const [editingSection, setEditingSection] = useState<SectionName | null>(null);
  const [lastHandoffTimestamp, setLastHandoffTimestamp] = useState<string | null>(
    '2026-07-06T06:45:00Z',
  );

  const [sections, setSections] = useState<HandoffSection[]>([
    { name: 'summary', label: 'Summary', icon: <FileText className="w-4 h-4" />, content: '' },
    {
      name: 'activeIssues',
      label: 'Active Issues',
      icon: <AlertTriangle className="w-4 h-4" />,
      content: '',
    },
    {
      name: 'pendingActions',
      label: 'Pending Actions',
      icon: <ClipboardList className="w-4 h-4" />,
      content: '',
    },
    {
      name: 'medications',
      label: 'Medications',
      icon: <Pill className="w-4 h-4" />,
      content: '',
    },
  ]);

  const filteredPatients = MOCK_PATIENTS.filter(
    (p) =>
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.mpiId.toLowerCase().includes(search.toLowerCase()),
  );

  const togglePatient = (mpiId: string) => {
    setSelectedPatients((prev) => {
      const next = new Set(prev);
      if (next.has(mpiId)) {
        next.delete(mpiId);
      } else {
        next.add(mpiId);
      }
      return next;
    });
  };

  const updateSection = (name: SectionName, content: string) => {
    setSections((prev) =>
      prev.map((s) => (s.name === name ? { ...s, content } : s)),
    );
  };

  const formatTimestamp = (iso: string | null): string => {
    if (!iso) return 'No previous handoff';
    return new Date(iso).toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    const text = sections
      .map((s) => `=== ${s.label} ===\n${s.content || '(empty)'}`)
      .join('\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `handoff-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Handoff Report
          </h1>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Shift change handoff
            {lastHandoffTimestamp && (
              <span
                className="inline-flex items-center gap-1 ml-3 text-xs"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                <Clock className="w-3 h-3" />
                Last handoff: {formatTimestamp(lastHandoffTimestamp)}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            aria-label="Print handoff report"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <Printer className="w-4 h-4" />
            Print
          </button>
          <button
            onClick={handleExport}
            aria-label="Export handoff report"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Patient quick-select */}
        <div className="lg:col-span-1">
          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <h2
              className="text-sm font-semibold uppercase tracking-wider mb-4"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              <Users className="w-4 h-4 inline mr-1.5" />
              Patients
            </h2>

            <div className="relative mb-4">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                style={{ color: 'var(--semantic-text-secondary)' }}
              />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search patients..."
                aria-label="Search patients for handoff"
                className="w-full pl-10 pr-4 py-2 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              />
            </div>

            <div className="space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto">
              {filteredPatients.map((patient) => {
                const isSelected = selectedPatients.has(patient.mpiId);
                return (
                  <button
                    key={patient.mpiId}
                    onClick={() => togglePatient(patient.mpiId)}
                    aria-label={`${isSelected ? 'Deselect' : 'Select'} patient ${patient.name}`}
                    aria-pressed={isSelected}
                    className="w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between"
                    style={{
                      borderColor: isSelected
                        ? statusColour(patient.status)
                        : 'var(--semantic-border-default)',
                      backgroundColor: isSelected
                        ? statusWash(patient.status)
                        : 'var(--semantic-surface-canvas)',
                    }}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: statusColour(patient.status) }}
                      />
                      <div className="min-w-0">
                        <p
                          className="text-sm font-medium truncate"
                          style={{ color: 'var(--semantic-text-primary)' }}
                        >
                          {patient.name}
                        </p>
                        <p
                          className="text-xs"
                          style={{ color: 'var(--semantic-text-secondary)' }}
                        >
                          {patient.mpiId}
                          {patient.bedId && ` · ${patient.bedId}`}
                        </p>
                      </div>
                    </div>
                    {isSelected && (
                      <CheckCircle
                        className="w-5 h-5 flex-shrink-0"
                        style={{ color: statusColour(patient.status) }}
                      />
                    )}
                  </button>
                );
              })}
            </div>

            {selectedPatients.size > 0 && (
              <div
                className="mt-4 px-3 py-2 rounded-lg text-xs font-medium"
                style={{
                  backgroundColor: 'var(--clinical-severity-normal-wash)',
                  color: 'var(--clinical-severity-normal-on-surface)',
                }}
              >
                {selectedPatients.size} patient{selectedPatients.size !== 1 ? 's' : ''} selected
              </div>
            )}
          </div>
        </div>

        {/* Right: Structured sections */}
        <div className="lg:col-span-2 space-y-4">
          {sections.map((section) => {
            const isEditing = editingSection === section.name;
            return (
              <div
                key={section.name}
                className="rounded-xl border p-5"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                }}
                aria-label={`Handoff section: ${section.label}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3
                    className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {section.icon}
                    {section.label}
                  </h3>
                  <button
                    onClick={() =>
                      setEditingSection(isEditing ? null : section.name)
                    }
                    aria-label={`${isEditing ? 'Save' : 'Edit'} ${section.label} section`}
                    className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-all"
                    style={{
                      borderColor: 'var(--semantic-border-default)',
                      color: 'var(--semantic-text-secondary)',
                      backgroundColor: isEditing
                        ? 'var(--clinical-severity-normal-wash)'
                        : 'var(--semantic-surface-canvas)',
                    }}
                  >
                    {isEditing ? (
                      <>
                        <Save className="w-3.5 h-3.5" />
                        Save
                      </>
                    ) : (
                      <>
                        <Edit3 className="w-3.5 h-3.5" />
                        Edit
                      </>
                    )}
                  </button>
                </div>

                {isEditing ? (
                  <textarea
                    value={section.content}
                    onChange={(e) => updateSection(section.name, e.target.value)}
                    placeholder={`Enter ${section.label.toLowerCase()} notes...`}
                    rows={5}
                    aria-label={`Edit ${section.label}`}
                    className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
                    style={{
                      borderColor: 'var(--semantic-border-default)',
                      color: 'var(--semantic-text-primary)',
                      backgroundColor: 'var(--semantic-surface-canvas)',
                    }}
                    autoFocus
                  />
                ) : (
                  <div
                    className="text-sm leading-relaxed min-h-[2rem]"
                    style={{
                      color: section.content
                        ? 'var(--semantic-text-primary)'
                        : 'var(--semantic-text-secondary)',
                    }}
                  >
                    {section.content || (
                      <em>No {section.label.toLowerCase()} recorded. Click Edit to add notes.</em>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Handoff completion status */}
          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h3
                  className="text-sm font-semibold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Handoff Status
                </h3>
                <p
                  className="text-xs mt-1"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  {sections.some((s) => s.content)
                    ? `${sections.filter((s) => s.content).length} of ${sections.length} sections completed`
                    : 'No sections filled'}
                  {selectedPatients.size > 0 &&
                    ` · ${selectedPatients.size} patient${selectedPatients.size !== 1 ? 's' : ''} selected`}
                </p>
              </div>
              <button
                disabled={selectedPatients.size === 0 || !sections.some((s) => s.content)}
                aria-label="Submit handoff report"
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all disabled:opacity-50"
                style={{
                  backgroundColor: 'var(--clinical-severity-normal-fill)',
                  color: 'var(--clinical-severity-normal-on-fill)',
                }}
                onClick={() => {
                  setLastHandoffTimestamp(new Date().toISOString());
                }}
              >
                <ShieldAlert className="w-4 h-4" />
                Complete Handoff
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
