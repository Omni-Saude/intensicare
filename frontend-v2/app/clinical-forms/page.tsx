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

// ─── Types ──────────────────────────────────────────────────────────────────

type FormTab = 'rass' | 'cam-icu' | 'bps-nrs';

interface PatientOption {
  mpiId: string;
  name: string;
  bedId?: string;
}

// ─── Mock patients ──────────────────────────────────────────────────────────

const MOCK_PATIENTS: PatientOption[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bedId: 'ICU-1-01' },
  { mpiId: 'MPI-002', name: 'Maria Santos', bedId: 'ICU-1-02' },
  { mpiId: 'MPI-003', name: 'Carlos Oliveira', bedId: 'ICU-2-05' },
  { mpiId: 'MPI-004', name: 'Ana Costa', bedId: 'ER-03' },
];

// ─── Severity colour tokens ─────────────────────────────────────────────────

function scoreColour(score: number, thresholds: { min: number; max: number }[]): string {
  const level = thresholds.findIndex((t) => score >= t.min && score <= t.max);
  switch (level) {
    case 2:
      return 'var(--clinical-severity-critical-signal)';
    case 1:
      return 'var(--clinical-severity-watch-signal)';
    default:
      return 'var(--clinical-severity-normal-signal)';
  }
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function ClinicalFormsPage() {
  const [selectedPatient, setSelectedPatient] = useState<PatientOption | null>(null);
  const [patientSearch, setPatientSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeTab, setActiveTab] = useState<FormTab>('rass');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<'success' | 'error' | null>(null);

  // ─── RASS state ─────────────────────────────────────────────────────────

  const [rassScore, setRassScore] = useState<number | ''>('');
  const [rassNote, setRassNote] = useState('');

  // ─── CAM-ICU state ──────────────────────────────────────────────────────

  const [camFeature1, setCamFeature1] = useState<boolean>(false);
  const [camFeature2, setCamFeature2] = useState<boolean>(false);
  const [camFeature3, setCamFeature3] = useState<boolean>(false);
  const [camFeature4, setCamFeature4] = useState<boolean>(false);
  const [camNote, setCamNote] = useState('');

  // ─── BPS/NRS state ──────────────────────────────────────────────────────

  const [bpsScore, setBpsScore] = useState<number | ''>('');
  const [nrsScore, setNrsScore] = useState<number | ''>('');
  const [painNote, setPainNote] = useState('');

  const camPositive = camFeature1 || camFeature2 || (camFeature3 && camFeature4);

  const filteredPatients = MOCK_PATIENTS.filter(
    (p) =>
      !patientSearch ||
      p.name.toLowerCase().includes(patientSearch.toLowerCase()) ||
      p.mpiId.toLowerCase().includes(patientSearch.toLowerCase()),
  );

  const resetForm = () => {
    setRassScore('');
    setRassNote('');
    setCamFeature1(false);
    setCamFeature2(false);
    setCamFeature3(false);
    setCamFeature4(false);
    setCamNote('');
    setBpsScore('');
    setNrsScore('');
    setPainNote('');
    setResult(null);
  };

  const handleSubmit = async () => {
    if (!selectedPatient) return;

    setSubmitting(true);
    setResult(null);
    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      setResult('success');
      resetForm();
    } catch {
      setResult('error');
    } finally {
      setSubmitting(false);
    }
  };

  const isFormValid = (): boolean => {
    switch (activeTab) {
      case 'rass':
        return rassScore !== '' && !isNaN(Number(rassScore));
      case 'cam-icu':
        return true; // CAM-ICU is always submittable (features are optional)
      case 'bps-nrs':
        return (
          (bpsScore !== '' && !isNaN(Number(bpsScore))) ||
          (nrsScore !== '' && !isNaN(Number(nrsScore)))
        );
      default:
        return false;
    }
  };

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <h1
          className="text-2xl font-bold"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          Clinical Forms
        </h1>
        <p
          className="text-sm mt-1"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          Structured bedside assessments
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
          Select Patient
        </label>
        <div className="relative">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
            style={{ color: 'var(--semantic-text-secondary)' }}
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
            placeholder="Search by name or MPI ID..."
            aria-label="Search patients"
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
                    resetForm();
                  }}
                  className="w-full text-left px-4 py-3 text-sm transition-colors flex items-center justify-between"
                  style={{
                    color: 'var(--semantic-text-primary)',
                    borderBottom: '1px solid var(--semantic-border-default)',
                  }}
                  aria-label={`Select patient ${patient.name}`}
                >
                  <span className="flex items-center gap-2">
                    <UserCheck className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} />
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
            <CheckCircle className="w-4 h-4" />
            Selected: {selectedPatient.name} ({selectedPatient.mpiId})
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 mb-6 border-b" style={{ borderColor: 'var(--semantic-border-default)' }}>
        {(['rass', 'cam-icu', 'bps-nrs'] as FormTab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab);
              setResult(null);
            }}
            aria-label={`Switch to ${tab.toUpperCase()} form`}
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
              {tab === 'rass' && <Brain className="w-4 h-4" />}
              {tab === 'cam-icu' && <Activity className="w-4 h-4" />}
              {tab === 'bps-nrs' && <Heart className="w-4 h-4" />}
              {tab.toUpperCase()}
            </span>
          </button>
        ))}
      </div>

      {/* ─── RASS Form ──────────────────────────────────────────────────── */}
      {activeTab === 'rass' && (
        <div
          className="rounded-xl border p-6"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
          role="tabpanel"
          aria-label="RASS assessment form"
        >
          <h2
            className="text-lg font-semibold mb-4"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Richmond Agitation-Sedation Scale (RASS)
          </h2>

          <div className="mb-5">
            <label
              className="text-sm font-medium mb-2 block"
              style={{ color: 'var(--semantic-text-secondary)' }}
              htmlFor="rass-score"
            >
              RASS Score (-5 to +4)
            </label>
            <select
              id="rass-score"
              value={rassScore}
              onChange={(e) => setRassScore(e.target.value === '' ? '' : Number(e.target.value))}
              aria-label="RASS score"
              className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
              style={{
                borderColor: 'var(--semantic-border-default)',
                color: 'var(--semantic-text-primary)',
                backgroundColor: 'var(--semantic-surface-canvas)',
              }}
            >
              <option value="">Select score...</option>
              <option value="4">+4 Combative</option>
              <option value="3">+3 Very Agitated</option>
              <option value="2">+2 Agitated</option>
              <option value="1">+1 Restless</option>
              <option value="0">0 Alert & Calm</option>
              <option value="-1">-1 Drowsy</option>
              <option value="-2">-2 Light Sedation</option>
              <option value="-3">-3 Moderate Sedation</option>
              <option value="-4">-4 Deep Sedation</option>
              <option value="-5">-5 Unarousable</option>
            </select>
          </div>

          {rassScore !== '' && (
            <div
              className="mb-5 px-4 py-3 rounded-lg text-sm font-medium"
              style={{
                backgroundColor:
                  Number(rassScore) <= -3
                    ? 'var(--clinical-severity-critical-wash)'
                    : Number(rassScore) >= 2
                      ? 'var(--clinical-severity-watch-wash)'
                      : 'var(--clinical-severity-normal-wash)',
                color:
                  Number(rassScore) <= -3
                    ? 'var(--clinical-severity-critical-on-surface)'
                    : Number(rassScore) >= 2
                      ? 'var(--clinical-severity-watch-on-surface)'
                      : 'var(--clinical-severity-normal-on-surface)',
              }}
              aria-live="polite"
            >
              {Number(rassScore) <= -3
                ? '⚠️ Deep sedation — assess need for reduction'
                : Number(rassScore) >= 2
                  ? '⚠️ Agitation — assess pain and delirium'
                  : '✅ Within target range'}
            </div>
          )}

          <div className="mb-5">
            <label
              className="text-sm font-medium mb-2 block"
              style={{ color: 'var(--semantic-text-secondary)' }}
              htmlFor="rass-note"
            >
              Clinical Note
            </label>
            <textarea
              id="rass-note"
              value={rassNote}
              onChange={(e) => setRassNote(e.target.value)}
              placeholder="Additional observations..."
              rows={3}
              aria-label="RASS clinical note"
              className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
              style={{
                borderColor: 'var(--semantic-border-default)',
                color: 'var(--semantic-text-primary)',
                backgroundColor: 'var(--semantic-surface-canvas)',
              }}
            />
          </div>
        </div>
      )}

      {/* ─── CAM-ICU Form ───────────────────────────────────────────────── */}
      {activeTab === 'cam-icu' && (
        <div
          className="rounded-xl border p-6"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
          role="tabpanel"
          aria-label="CAM-ICU assessment form"
        >
          <h2
            className="text-lg font-semibold mb-4"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Confusion Assessment Method for ICU (CAM-ICU)
          </h2>

          <div className="space-y-4 mb-5">
            {[
              {
                key: 'camFeature1',
                label: 'Feature 1: Acute Onset or Fluctuating Course',
                desc: 'Is there an acute change from mental status baseline? OR has mental status fluctuated in the last 24h?',
                value: camFeature1,
                toggle: setCamFeature1,
              },
              {
                key: 'camFeature2',
                label: 'Feature 2: Inattention',
                desc: 'Errors on attention screening examination (e.g. ASE letters, ASE pictures).',
                value: camFeature2,
                toggle: setCamFeature2,
              },
              {
                key: 'camFeature3',
                label: 'Feature 3: Altered Level of Consciousness',
                desc: 'Current RASS ≠ 0 (anything other than alert and calm).',
                value: camFeature3,
                toggle: setCamFeature3,
              },
              {
                key: 'camFeature4',
                label: 'Feature 4: Disorganized Thinking',
                desc: '≥ 2 errors on YES/NO questions or unable to follow commands.',
                value: camFeature4,
                toggle: setCamFeature4,
              },
            ].map((feat) => (
              <div
                key={feat.key}
                className="flex items-start gap-4 p-3 rounded-lg"
                style={{
                  border: '1px solid var(--semantic-border-default)',
                  backgroundColor: feat.value
                    ? 'var(--clinical-severity-watch-wash)'
                    : 'var(--semantic-surface-canvas)',
                }}
              >
                <button
                  onClick={() => feat.toggle(!feat.value)}
                  aria-label={`Toggle ${feat.label}`}
                  aria-pressed={feat.value}
                  className="flex-shrink-0 mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
                  style={{
                    borderColor: feat.value
                      ? 'var(--clinical-severity-watch-signal)'
                      : 'var(--semantic-border-default)',
                    backgroundColor: feat.value
                      ? 'var(--clinical-severity-watch-fill)'
                      : 'transparent',
                  }}
                >
                  {feat.value && (
                    <CheckCircle className="w-3.5 h-3.5" style={{ color: 'white' }} />
                  )}
                </button>
                <div>
                  <p
                    className="text-sm font-medium"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {feat.label}
                  </p>
                  <p
                    className="text-xs mt-0.5"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {feat.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div
            className="mb-5 px-4 py-3 rounded-lg text-sm font-medium"
            style={{
              backgroundColor: camPositive
                ? 'var(--clinical-severity-critical-wash)'
                : 'var(--clinical-severity-normal-wash)',
              color: camPositive
                ? 'var(--clinical-severity-critical-on-surface)'
                : 'var(--clinical-severity-normal-on-surface)',
            }}
            aria-live="polite"
          >
            {camPositive
              ? '⚠️ CAM-ICU Positive — Delirium detected. Features 1+2 AND either 3 or 4 present.'
              : '✅ CAM-ICU Negative — No delirium detected.'}
          </div>

          <div className="mb-5">
            <label
              className="text-sm font-medium mb-2 block"
              style={{ color: 'var(--semantic-text-secondary)' }}
              htmlFor="cam-note"
            >
              Clinical Note
            </label>
            <textarea
              id="cam-note"
              value={camNote}
              onChange={(e) => setCamNote(e.target.value)}
              placeholder="Additional observations..."
              rows={3}
              aria-label="CAM-ICU clinical note"
              className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
              style={{
                borderColor: 'var(--semantic-border-default)',
                color: 'var(--semantic-text-primary)',
                backgroundColor: 'var(--semantic-surface-canvas)',
              }}
            />
          </div>
        </div>
      )}

      {/* ─── BPS/NRS Form ───────────────────────────────────────────────── */}
      {activeTab === 'bps-nrs' && (
        <div
          className="rounded-xl border p-6"
          style={{
            borderColor: 'var(--semantic-border-default)',
            backgroundColor: 'var(--semantic-surface-raised)',
          }}
          role="tabpanel"
          aria-label="BPS/NRS pain assessment form"
        >
          <h2
            className="text-lg font-semibold mb-4"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Pain Assessment: BPS / NRS
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-5">
            {/* BPS */}
            <div>
              <label
                className="text-sm font-medium mb-2 block"
                style={{ color: 'var(--semantic-text-secondary)' }}
                htmlFor="bps-score"
              >
                Behavioral Pain Scale (BPS) — 3 to 12
              </label>
              <select
                id="bps-score"
                value={bpsScore}
                onChange={(e) => setBpsScore(e.target.value === '' ? '' : Number(e.target.value))}
                aria-label="BPS pain score"
                className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              >
                <option value="">Select score...</option>
                {[3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((s) => (
                  <option key={s} value={s}>{s} — {s <= 5 ? 'No/Low pain' : s <= 8 ? 'Moderate' : 'Severe'}</option>
                ))}
              </select>
              {bpsScore !== '' && (
                <div
                  className="mt-2 px-3 py-1.5 rounded text-xs font-medium"
                  style={{
                    backgroundColor:
                      Number(bpsScore) >= 9
                        ? 'var(--clinical-severity-critical-wash)'
                        : Number(bpsScore) >= 6
                          ? 'var(--clinical-severity-watch-wash)'
                          : 'var(--clinical-severity-normal-wash)',
                    color:
                      Number(bpsScore) >= 9
                        ? 'var(--clinical-severity-critical-on-surface)'
                        : Number(bpsScore) >= 6
                          ? 'var(--clinical-severity-watch-on-surface)'
                          : 'var(--clinical-severity-normal-on-surface)',
                  }}
                  aria-live="polite"
                >
                  {Number(bpsScore) >= 9 ? '🔴 Severe pain' : Number(bpsScore) >= 6 ? '🟡 Moderate pain' : '🟢 No/Low pain'}
                </div>
              )}
            </div>

            {/* NRS */}
            <div>
              <label
                className="text-sm font-medium mb-2 block"
                style={{ color: 'var(--semantic-text-secondary)' }}
                htmlFor="nrs-score"
              >
                Numeric Rating Scale (NRS) — 0 to 10
              </label>
              <select
                id="nrs-score"
                value={nrsScore}
                onChange={(e) => setNrsScore(e.target.value === '' ? '' : Number(e.target.value))}
                aria-label="NRS pain score"
                className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              >
                <option value="">Select score...</option>
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((s) => (
                  <option key={s} value={s}>{s} — {s <= 3 ? 'Mild' : s <= 6 ? 'Moderate' : 'Severe'}</option>
                ))}
              </select>
              {nrsScore !== '' && (
                <div
                  className="mt-2 px-3 py-1.5 rounded text-xs font-medium"
                  style={{
                    backgroundColor:
                      Number(nrsScore) >= 7
                        ? 'var(--clinical-severity-critical-wash)'
                        : Number(nrsScore) >= 4
                          ? 'var(--clinical-severity-watch-wash)'
                          : 'var(--clinical-severity-normal-wash)',
                    color:
                      Number(nrsScore) >= 7
                        ? 'var(--clinical-severity-critical-on-surface)'
                        : Number(nrsScore) >= 4
                          ? 'var(--clinical-severity-watch-on-surface)'
                          : 'var(--clinical-severity-normal-on-surface)',
                  }}
                  aria-live="polite"
                >
                  {Number(nrsScore) >= 7 ? '🔴 Severe pain' : Number(nrsScore) >= 4 ? '🟡 Moderate pain' : '🟢 Mild pain'}
                </div>
              )}
            </div>
          </div>

          <div className="mb-5">
            <label
              className="text-sm font-medium mb-2 block"
              style={{ color: 'var(--semantic-text-secondary)' }}
              htmlFor="pain-note"
            >
              Clinical Note
            </label>
            <textarea
              id="pain-note"
              value={painNote}
              onChange={(e) => setPainNote(e.target.value)}
              placeholder="Pain location, characteristics..."
              rows={3}
              aria-label="Pain assessment clinical note"
              className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500 resize-y"
              style={{
                borderColor: 'var(--semantic-border-default)',
                color: 'var(--semantic-text-primary)',
                backgroundColor: 'var(--semantic-surface-canvas)',
              }}
            />
          </div>
        </div>
      )}

      {/* Submit button */}
      {selectedPatient && (
        <div className="mt-6 flex items-center gap-4">
          <button
            onClick={handleSubmit}
            disabled={submitting || !isFormValid()}
            aria-label="Submit assessment"
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium text-sm transition-all disabled:opacity-50"
            style={{
              backgroundColor: 'var(--clinical-severity-normal-fill)',
              color: 'var(--clinical-severity-normal-on-fill)',
            }}
          >
            {submitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {submitting ? 'Submitting...' : 'Submit Assessment'}
          </button>

          {result === 'success' && (
            <div
              className="flex items-center gap-2 text-sm font-medium"
              style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
              role="status"
              aria-live="polite"
            >
              <CheckCircle className="w-4 h-4" />
              Assessment submitted successfully
            </div>
          )}

          {result === 'error' && (
            <div
              className="flex items-center gap-2 text-sm font-medium"
              style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
              role="alert"
              aria-live="assertive"
            >
              <AlertTriangle className="w-4 h-4" />
              Failed to submit assessment. Please try again.
            </div>
          )}
        </div>
      )}
    </Layout>
  );
}
