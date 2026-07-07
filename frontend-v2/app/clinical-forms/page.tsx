'use client';

import React, { useState } from 'react';
import {
  ClipboardList,
  Brain,
  Activity,
  Heart,
  Search,
  UserCheck,
  Loader2,
  AlertTriangle,
  CheckCircle,
  Send,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ClinicalTooltip from '@/components/ClinicalTooltip';
import FormEngine from '@/lib/form-engine/FormEngine';
import type { FormConfig } from '@/lib/form-engine/types';

// ─── Config imports ──────────────────────────────────────────────────────────

import rassConfig from '@/config/forms/rass.json';
import camIcuConfig from '@/config/forms/cam-icu.json';
import bpsNrsConfig from '@/config/forms/bps-nrs.json';

// ─── Types ───────────────────────────────────────────────────────────────────

type FormTab = 'rass' | 'cam-icu' | 'bps-nrs';

interface PatientOption {
  mpiId: string;
  name: string;
  bedId?: string;
}

// ─── Mock patients ───────────────────────────────────────────────────────────

const MOCK_PATIENTS: PatientOption[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bedId: 'ICU-1-01' },
  { mpiId: 'MPI-002', name: 'Maria Santos', bedId: 'ICU-1-02' },
  { mpiId: 'MPI-003', name: 'Carlos Oliveira', bedId: 'ICU-2-05' },
  { mpiId: 'MPI-004', name: 'Ana Costa', bedId: 'ER-03' },
];

// ─── Config map ──────────────────────────────────────────────────────────────

const FORM_CONFIGS: Record<FormTab, FormConfig> = {
  rass: rassConfig as FormConfig,
  'cam-icu': camIcuConfig as FormConfig,
  'bps-nrs': bpsNrsConfig as FormConfig,
};

// ─── Page ────────────────────────────────────────────────────────────────────

export default function ClinicalFormsPage() {
  const [selectedPatient, setSelectedPatient] = useState<PatientOption | null>(null);
  const [patientSearch, setPatientSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeTab, setActiveTab] = useState<FormTab>('rass');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<'success' | 'error' | null>(null);

  const filteredPatients = MOCK_PATIENTS.filter(
    (p) =>
      !patientSearch ||
      p.name.toLowerCase().includes(patientSearch.toLowerCase()) ||
      p.mpiId.toLowerCase().includes(patientSearch.toLowerCase()),
  );

  const handleSubmit = async (data: Record<string, any>) => {
    if (!selectedPatient) return;

    setSubmitting(true);
    setResult(null);
    try {
      const res = await fetch('/api/clinical-forms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mpiId: selectedPatient.mpiId,
          formId: activeTab,
          data,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      console.log('[ClinicalForms] Submitted:', {
        formId: activeTab,
        patient: selectedPatient,
        data,
      });
      setResult('success');
    } catch {
      setResult('error');
    } finally {
      setSubmitting(false);
    }
  };

  const config = FORM_CONFIGS[activeTab];

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <h1
          className="text-2xl font-bold"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Formulários Clínicos
        </h1>
        <p
          className="text-sm mt-1"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Avaliações estruturadas à beira do leito
        </p>
      </div>

      {/* Patient Selector */}
      <div
        className="rounded-xl border p-5 mb-6"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        <label
          className="text-sm font-semibold uppercase tracking-wider mb-3 block"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Selecionar Paciente
        </label>
        <div className="relative">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
            style={{ color: 'var(--semantic-text-secondary)' }}
            aria-hidden="true"
          />
          <input
            type="text"
            value={patientSearch}
            onChange={(e) => {
              setPatientSearch(e.target.value);
              setShowDropdown(true);
            }}
            onFocus={() => setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder="Buscar por nome ou MPI ID..."
            aria-label="Buscar pacientes"
            className="w-full pl-10 pr-4 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
            style={{
              borderColor: 'var(--semantic-border-default)',
              color: 'var(--semantic-text-primary)',
              backgroundColor: 'var(--semantic-surface-canvas)',
            }}
          />
          {showDropdown && filteredPatients.length > 0 && (
            <div
              className="absolute z-10 w-full mt-1 rounded-lg border shadow-lg max-h-48 overflow-y-auto"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              {filteredPatients.map((patient) => (
                <button
                  key={patient.mpiId}
                  onMouseDown={() => {
                    setSelectedPatient(patient);
                    setPatientSearch(patient.name);
                    setShowDropdown(false);
                    setResult(null);
                  }}
                  className="w-full text-left px-4 py-3 text-sm transition-colors flex items-center justify-between"
                  style={{
                    color: 'var(--semantic-text-primary)',
                    borderBottom: '1px solid var(--semantic-border-default)',
                  }}
                  aria-label={`Selecionar paciente ${patient.name}`}
                >
                  <span className="flex items-center gap-2">
                    <UserCheck className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
                    {patient.name}
                  </span>
                  <span
                    className="text-xs"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {patient.bedId}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
        {selectedPatient && (
          <div
            className="mt-3 flex items-center gap-2 text-sm font-medium"
            style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
          >
            <CheckCircle className="w-4 h-4" aria-hidden="true" />
            Selecionado: {selectedPatient.name} ({selectedPatient.mpiId})
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 mb-6 border-b" style={{ borderColor: 'var(--semantic-border-default)' }}>
        {(['rass', 'cam-icu', 'bps-nrs'] as FormTab[]).map((tab) => {
          const tabLabels: Record<FormTab, { display: string; tooltip: string }> = {
            rass: { display: 'RASS', tooltip: 'RASS' },
            'cam-icu': { display: 'CAM-ICU', tooltip: 'CAM-ICU' },
            'bps-nrs': { display: 'BPS/NRS', tooltip: 'BPS' },
          };
          const tabInfo = tabLabels[tab];
          return (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab);
              setResult(null);
            }}
            aria-label={`Mudar para formulário ${tab.toUpperCase()}`}
            aria-selected={activeTab === tab}
            role="tab"
            className="px-5 py-3 text-sm font-medium transition-all border-b-2 -mb-px"
            style={{
              color:
                activeTab === tab
                  ? 'var(--semantic-text-primary)'
                  : 'var(--semantic-text-secondary)',
              borderBottomColor:
                activeTab === tab
                  ? 'var(--clinical-status-attended-color)'
                  : 'transparent',
            }}
          >
            <span className="flex items-center gap-2">
              {tab === 'rass' && <Brain className="w-4 h-4" aria-hidden="true" />}
              {tab === 'cam-icu' && <Activity className="w-4 h-4" aria-hidden="true" />}
              {tab === 'bps-nrs' && <Heart className="w-4 h-4" aria-hidden="true" />}
              <ClinicalTooltip term={tabInfo.tooltip}>{tabInfo.display}</ClinicalTooltip>
            </span>
          </button>
          );
        })}
      </div>

      {/* Form Engine */}
      {selectedPatient ? (
        <div
          className="rounded-xl border p-6"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
          role="tabpanel"
          aria-label={`Formulário ${activeTab.toUpperCase()}`}
        >
          <FormEngine
            key={activeTab}
            config={config}
            onSubmit={handleSubmit}
          />

          {/* Result indicators */}
          <div className="mt-4 flex items-center gap-4">
            {submitting && (
              <div
                className="flex items-center gap-2 text-sm font-medium"
                style={{ color: 'var(--semantic-text-secondary)' }}
                role="status"
                aria-live="polite"
              >
                <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                Enviando...
              </div>
            )}

            {result === 'success' && (
              <div
                className="flex items-center gap-2 text-sm font-medium"
                style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
                role="status"
                aria-live="polite"
              >
                <CheckCircle className="w-4 h-4" aria-hidden="true" />
                Avaliação enviada com sucesso
              </div>
            )}

            {result === 'error' && (
              <div
                className="flex items-center gap-2 text-sm font-medium"
                style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
                role="alert"
                aria-live="assertive"
              >
                <AlertTriangle className="w-4 h-4" aria-hidden="true" />
                Falha ao enviar avaliação. Tente novamente.
              </div>
            )}
          </div>
        </div>
      ) : (
        <div
          className="rounded-xl border p-12 text-center"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
        >
          <ClipboardList className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
          <p
            className="text-sm"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Selecione um paciente acima para iniciar uma avaliação clínica.
          </p>
        </div>
      )}
    </Layout>
  );
}
