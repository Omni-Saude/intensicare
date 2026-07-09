'use client';

import React, { useState, useCallback, useMemo } from 'react';
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
  Stethoscope,
  Eye,
  ShieldAlert,
  Clock,
  ChevronDown,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ClinicalTooltip from '@/components/ClinicalTooltip';
import FormEngine from '@/lib/form-engine/FormEngine';
import ScoreDisplay from '@/components/ScoreDisplay';
import type { FormConfig } from '@/lib/form-engine/types';
import type { FormType } from '@/lib/clinical-forms-types';
import {
  FORM_LABELS,
  FORM_SCORE_RANGES,
  SOFA_SYSTEMS,
  GLASGOW_COMPONENTS,
  MOCK_FORMS,
  computeSOFATotal,
  computeGlasgowTotal,
  getScoreColor,
  getScoreInterpretation,
} from '@/lib/clinical-forms-types';

// ─── Config imports ──────────────────────────────────────────────────────────

import rassConfig from '@/config/forms/rass.json';
import camIcuConfig from '@/config/forms/cam-icu.json';
import bpsNrsConfig from '@/config/forms/bps-nrs.json';
import sofaConfig from '@/config/forms/sofa.json';
import glasgowConfig from '@/config/forms/glasgow.json';
import lppConfig from '@/config/forms/lpp.json';

// ─── Types ───────────────────────────────────────────────────────────────────

type FormTab = 'rass' | 'cam-icu' | 'bps-nrs' | 'sofa' | 'glasgow' | 'lpp';

interface PatientOption {
  mpiId: string;
  name: string;
  bedId?: string;
}

interface SubmissionResult {
  formType: FormType;
  score: number | null;
  data: Record<string, any>;
  timestamp: string;
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
  sofa: sofaConfig as FormConfig,
  glasgow: glasgowConfig as FormConfig,
  lpp: lppConfig as FormConfig,
};

// ─── Tab definitions ─────────────────────────────────────────────────────────

interface TabDef {
  key: FormTab;
  display: string;
  tooltip: string;
  icon: React.ReactNode;
  formType: FormType;
}

const TABS: TabDef[] = [
  { key: 'rass', display: 'RASS', tooltip: 'RASS', icon: <Brain className="w-4 h-4" aria-hidden="true" />, formType: 'rass' },
  { key: 'cam-icu', display: 'CAM-ICU', tooltip: 'CAM-ICU', icon: <Activity className="w-4 h-4" aria-hidden="true" />, formType: 'cam_icu' },
  { key: 'bps-nrs', display: 'BPS/NRS', tooltip: 'BPS/NRS', icon: <Heart className="w-4 h-4" aria-hidden="true" />, formType: 'bps_nrs' },
  { key: 'glasgow', display: 'Glasgow', tooltip: 'Escala de Coma de Glasgow', icon: <Eye className="w-4 h-4" aria-hidden="true" />, formType: 'glasgow' },
  { key: 'sofa', display: 'SOFA', tooltip: 'SOFA', icon: <Stethoscope className="w-4 h-4" aria-hidden="true" />, formType: 'sofa' },
  { key: 'lpp', display: 'LPP', tooltip: 'Lesão por Pressão (NPUAP/Braden)', icon: <ShieldAlert className="w-4 h-4" aria-hidden="true" />, formType: 'lpp' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Decide the form type used for score display (lpp doesn't have a clinical score) */
function tabToFormType(tab: FormTab): FormType {
  switch (tab) {
    case 'rass': return 'rass';
    case 'cam-icu': return 'cam_icu';
    case 'bps-nrs': return 'bps_nrs';
    case 'sofa': return 'sofa';
    case 'glasgow': return 'glasgow';
    case 'lpp': return 'lpp';
  }
}

/** Computes the clinical score from form data */
function computeScore(formType: FormType, data: Record<string, any>): number | null {
  switch (formType) {
    case 'sofa':
      return computeSOFATotal(data);
    case 'glasgow':
      return computeGlasgowTotal(data);
    case 'rass':
      return data.rassScore !== undefined ? parseInt(data.rassScore, 10) : null;
    case 'bps_nrs': {
      const bps = data.bpsScore !== undefined && data.bpsScore !== '' ? parseInt(data.bpsScore, 10) : null;
      const nrs = data.nrsScore !== undefined && data.nrsScore !== '' ? parseInt(data.nrsScore, 10) : null;
      return bps ?? nrs ?? null;
    }
    case 'cam_icu': {
      const features = [data.camFeature1, data.camFeature2, data.camFeature3, data.camFeature4];
      const positiveCount = features.filter(Boolean).length;
      // CAM-ICU: positive if feature 1+2 AND either 3 OR 4
      const isPositive =
        data.camFeature1 && data.camFeature2 && (data.camFeature3 || data.camFeature4);
      return isPositive ? 1 : 0;
    }
    case 'lpp': {
      // Braden total: sum of 6 subscales (6-23). Lower = higher risk.
      const bradenFields = [
        'bradenPercepcaoSensorial',
        'bradenUmidade',
        'bradenAtividade',
        'bradenMobilidade',
        'bradenNutricao',
        'bradenFriccao',
      ];
      let total = 0;
      let allFilled = true;
      for (const field of bradenFields) {
        const val = parseInt(data[field], 10);
        if (isNaN(val)) { allFilled = false; break; }
        total += val;
      }
      return allFilled ? total : null;
    }
    default:
      return null;
  }
}

/** Formats ISO timestamp to PT-BR locale string */
function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR', {
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

// ─── Page ────────────────────────────────────────────────────────────────────

export default function ClinicalFormsPage() {
  const [selectedPatient, setSelectedPatient] = useState<PatientOption | null>(null);
  const [patientSearch, setPatientSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeTab, setActiveTab] = useState<FormTab>('rass');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<'success' | 'error' | null>(null);
  const [lastSubmission, setLastSubmission] = useState<SubmissionResult | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const filteredPatients = MOCK_PATIENTS.filter(
    (p) =>
      !patientSearch ||
      p.name.toLowerCase().includes(patientSearch.toLowerCase()) ||
      p.mpiId.toLowerCase().includes(patientSearch.toLowerCase()),
  );

  const handleSubmit = useCallback(
    async (data: Record<string, any>) => {
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

        const formType = tabToFormType(activeTab);
        const score = computeScore(formType, data);

        console.log('[ClinicalForms] Submitted:', {
          formId: activeTab,
          patient: selectedPatient,
          data,
          score,
        });

        setLastSubmission({
          formType,
          score,
          data,
          timestamp: new Date().toISOString(),
        });
        setResult('success');
      } catch {
        setResult('error');
      } finally {
        setSubmitting(false);
      }
    },
    [selectedPatient, activeTab],
  );

  const config = FORM_CONFIGS[activeTab];

  // ─── SOFA / Glasgow detail lines ──────────────────────────────────────────

  const scoreDetails = useMemo(() => {
    if (!lastSubmission) return undefined;

    const { formType, data } = lastSubmission;

    if (formType === 'sofa') {
      return SOFA_SYSTEMS.map((sys) => ({
        label: sys.label,
        score: parseInt(data[sys.key], 10) || 0,
        max: 4,
      }));
    }

    if (formType === 'glasgow') {
      return GLASGOW_COMPONENTS.map((comp) => ({
        label: comp.label,
        score: parseInt(data[comp.key], 10) || 0,
        max: comp.maxScore,
      }));
    }

    return undefined;
  }, [lastSubmission]);

  // ─── History for selected patient ────────────────────────────────────────

  const patientHistory = useMemo(() => {
    if (!selectedPatient) return [];
    return MOCK_FORMS
      .filter((f) => f.mpiId === selectedPatient.mpiId)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }, [selectedPatient]);

  // ─── Render ──────────────────────────────────────────────────────────────

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
                    setLastSubmission(null);
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
      <div className="flex gap-1 mb-6 border-b overflow-x-auto" style={{ borderColor: 'var(--semantic-border-default)' }}>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveTab(tab.key);
              setResult(null);
              setLastSubmission(null);
            }}
            aria-label={`Mudar para formulário ${tab.display}`}
            aria-selected={activeTab === tab.key}
            role="tab"
            className="px-4 py-3 text-sm font-medium transition-all border-b-2 -mb-px whitespace-nowrap"
            style={{
              color:
                activeTab === tab.key
                  ? 'var(--semantic-text-primary)'
                  : 'var(--semantic-text-secondary)',
              borderBottomColor:
                activeTab === tab.key
                  ? 'var(--clinical-status-attended-color)'
                  : 'transparent',
            }}
          >
            <span className="flex items-center gap-2">
              {tab.icon}
              <ClinicalTooltip term={tab.tooltip}>{tab.display}</ClinicalTooltip>
            </span>
          </button>
        ))}
      </div>

      {/* Form Area */}
      {selectedPatient ? (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Main form column */}
          <div className="xl:col-span-2 space-y-6">
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

            {/* Score Display — shown after successful submission */}
            {lastSubmission && lastSubmission.score !== null && (
              <ScoreDisplay
                formType={lastSubmission.formType}
                score={lastSubmission.score}
                maxScore={FORM_SCORE_RANGES[lastSubmission.formType].max}
                label={FORM_LABELS[lastSubmission.formType]}
                details={scoreDetails}
              />
            )}
          </div>

          {/* Sidebar: History */}
          <div className="xl:col-span-1">
            <div
              className="rounded-xl border"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              {/* History header */}
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="w-full flex items-center justify-between px-5 py-4 text-left"
                aria-expanded={showHistory}
                aria-label={showHistory ? 'Recolher histórico' : 'Expandir histórico'}
              >
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
                  <span
                    className="text-sm font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    Histórico ({patientHistory.length})
                  </span>
                </div>
                <ChevronDown
                  className="w-4 h-4 transition-transform"
                  style={{
                    color: 'var(--semantic-text-secondary)',
                    transform: showHistory ? 'rotate(180deg)' : 'rotate(0deg)',
                  }}
                  aria-hidden="true"
                />
              </button>

              {showHistory && (
                <div className="px-5 pb-4 max-h-[500px] overflow-y-auto">
                  {patientHistory.length === 0 ? (
                    <p
                      className="text-sm py-3"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      Nenhum formulário submetido para este paciente.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {patientHistory.map((form) => {
                        const colorVar = form.score !== null
                          ? getScoreColor(form.formType, form.score)
                          : 'var(--semantic-text-secondary)';
                        const interpretation = form.score !== null
                          ? getScoreInterpretation(form.formType, form.score)
                          : '';

                        return (
                          <div
                            key={form.id}
                            className="rounded-lg border p-3 text-sm"
                            style={{
                              borderColor: 'var(--semantic-border-default)',
                              backgroundColor: 'var(--semantic-surface-canvas)',
                            }}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span
                                className="font-semibold text-xs uppercase"
                                style={{ color: 'var(--semantic-text-secondary)' }}
                              >
                                {FORM_LABELS[form.formType]}
                              </span>
                              <span
                                className="text-xs"
                                style={{ color: 'var(--semantic-text-secondary)' }}
                              >
                                {formatTimestamp(form.createdAt)}
                              </span>
                            </div>
                            {form.score !== null && (
                              <div className="flex items-baseline gap-2">
                                <span className="text-xl font-bold" style={{ color: colorVar }}>
                                  {form.score}
                                </span>
                                {interpretation && (
                                  <span className="text-xs" style={{ color: colorVar, opacity: 0.8 }}>
                                    {interpretation}
                                  </span>
                                )}
                              </div>
                            )}
                            {form.createdBy && (
                              <p
                                className="text-xs mt-1"
                                style={{ color: 'var(--semantic-text-secondary)' }}
                              >
                                {form.createdBy}
                              </p>
                            )}
                            {form.notes && (
                              <p
                                className="text-xs mt-1 italic"
                                style={{ color: 'var(--semantic-text-secondary)' }}
                              >
                                {form.notes}
                              </p>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
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
