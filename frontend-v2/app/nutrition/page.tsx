'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Scale,
  Save,
  RefreshCw,
  AlertTriangle,
  User,
  Stethoscope,
  Target,
  Heart,
  Loader2,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import SeverityBadge from '@/components/SeverityBadge';
import {
  type NutritionalAssessment,
  type NutritionStatus,
  computeBMI,
  computeNutritionalStatus,
} from '@/lib/nutrition-types';
import { fetchDashboard, submitClinicalForm } from '@/lib/api';
import type { PatientBedSummary } from '@/lib/api';

// ─── Form Schema (Zod) ──────────────────────────────────────────────────────

const nutritionFormSchema = z.object({
  height: z
    .number({ message: 'Altura é obrigatória' })
    .min(50, 'Altura mínima: 50 cm')
    .max(250, 'Altura máxima: 250 cm'),
  weight: z
    .number({ message: 'Peso é obrigatório' })
    .min(20, 'Peso mínimo: 20 kg')
    .max(300, 'Peso máximo: 300 kg'),
  calorieGoal: z
    .number({ message: 'Meta calórica é obrigatória' })
    .min(500, 'Mínimo: 500 kcal/dia')
    .max(5000, 'Máximo: 5000 kcal/dia'),
  proteinGoal: z
    .number({ message: 'Meta proteica é obrigatória' })
    .min(0.5, 'Mínimo: 0,5 g/kg/dia')
    .max(3.0, 'Máximo: 3,0 g/kg/dia'),
});

type NutritionFormValues = z.infer<typeof nutritionFormSchema>;

// ─── Default form values ────────────────────────────────────────────────────

const DEFAULT_FORM_VALUES: NutritionFormValues = {
  height: 170,
  weight: 70,
  calorieGoal: 2000,
  proteinGoal: 1.5,
};

// ─── Token helpers ──────────────────────────────────────────────────────────

const NUTRITION_TOKEN_MAP: Record<
  NutritionStatus,
  {
    onSurface: string;
    signal: string;
    fill: string;
    onFill: string;
    wash: string;
    severityLabel: string;
    severity: 'normal' | 'watch' | 'critical';
  }
> = {
  optimal: {
    onSurface: 'var(--clinical-nutrition-optimal-on-surface)',
    signal: 'var(--clinical-nutrition-optimal-signal)',
    fill: 'var(--clinical-nutrition-optimal-fill)',
    onFill: 'var(--clinical-nutrition-optimal-on-fill)',
    wash: 'var(--clinical-nutrition-optimal-wash)',
    severityLabel: 'Adequado',
    severity: 'normal',
  },
  'at-risk': {
    onSurface: 'var(--clinical-nutrition-at-risk-on-surface)',
    signal: 'var(--clinical-nutrition-at-risk-signal)',
    fill: 'var(--clinical-nutrition-at-risk-fill)',
    onFill: 'var(--clinical-nutrition-at-risk-on-fill)',
    wash: 'var(--clinical-nutrition-at-risk-wash)',
    severityLabel: 'Em Risco',
    severity: 'watch',
  },
  critical: {
    onSurface: 'var(--clinical-nutrition-critical-on-surface)',
    signal: 'var(--clinical-nutrition-critical-signal)',
    fill: 'var(--clinical-nutrition-critical-fill)',
    onFill: 'var(--clinical-nutrition-critical-on-fill)',
    wash: 'var(--clinical-nutrition-critical-wash)',
    severityLabel: 'Crítico',
    severity: 'critical',
  },
};

// ─── Skeleton ────────────────────────────────────────────────────────────────

function SkeletonHeader(): React.ReactElement {
  return (
    <div className="animate-pulse space-y-3" role="status" aria-label="Carregando">
      <div
        className="h-8 w-64 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
      <div
        className="h-5 w-48 rounded"
        style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
      />
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function NutritionPage(): React.ReactElement {
  const [patients, setPatients] = useState<PatientBedSummary[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [isLoadingPatients, setIsLoadingPatients] = useState(true);
  const [patientsError, setPatientsError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // ── Fetch patients from API ──────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    fetchDashboard()
      .then((data) => {
        if (!cancelled) {
          const list = data.patients || [];
          setPatients(list);
          if (list.length > 0 && !selectedPatient) {
            setSelectedPatient(list[0]!.mpi_id);
          }
          setIsLoadingPatients(false);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setPatientsError(err.message || 'Erro ao carregar pacientes');
          setIsLoadingPatients(false);
        }
      });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const form = useForm<NutritionFormValues>({
    resolver: zodResolver(nutritionFormSchema),
    defaultValues: DEFAULT_FORM_VALUES,
    mode: 'onChange',
  });

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isValid },
  } = form;

  // Watch form values for BMI calculation
  const height = watch('height');
  const weight = watch('weight');
  const calorieGoal = watch('calorieGoal');
  const proteinGoal = watch('proteinGoal');

  // ─── Derived state ─────────────────────────────────────────────────────────

  const bmiResult = useMemo(() => computeBMI(height, weight), [height, weight]);

  const meetsCalorieGoal = useMemo(
    () => calorieGoal >= 1500,
    [calorieGoal],
  );
  const meetsProteinGoal = useMemo(
    () => proteinGoal >= 1.2,
    [proteinGoal],
  );

  const nutritionStatus: NutritionStatus = useMemo(
    () =>
      computeNutritionalStatus(
        bmiResult.value,
        meetsCalorieGoal,
        meetsProteinGoal,
      ),
    [bmiResult.value, meetsCalorieGoal, meetsProteinGoal],
  );

  const selectedPatientData = patients.find(
    (p) => p.mpi_id === selectedPatient,
  );

  const statusTokens = NUTRITION_TOKEN_MAP[nutritionStatus];

  // ─── Handlers ──────────────────────────────────────────────────────────────

  const handleSave = useCallback(
    (data: NutritionFormValues) => {
      setIsLoading(true);
      setSaveSuccess(false);
      setSaveError(null);

      const assessment: NutritionalAssessment = {
        patientMpiId: selectedPatient,
        height: data.height,
        weight: data.weight,
        bmi: bmiResult.value,
        calorieGoal: data.calorieGoal,
        proteinGoal: data.proteinGoal,
        meetsCalorieGoal,
        meetsProteinGoal,
        status: nutritionStatus,
        assessedAt: new Date().toISOString(),
        assessedBy: 'Dr. Plantonista',
      };

      submitClinicalForm(selectedPatient, {
        form_type: 'nutrition_assessment',
        definition_version: '1.0',
        data: assessment as unknown as Record<string, unknown>,
      })
        .then(() => {
          setIsLoading(false);
          setSaveSuccess(true);
        })
        .catch((err: Error) => {
          setIsLoading(false);
          setSaveError(err.message || 'Erro ao salvar avaliação nutricional');
          console.error('[Nutrition] Save failed:', err);
        });
    },
    [
      selectedPatient,
      bmiResult.value,
      meetsCalorieGoal,
      meetsProteinGoal,
      nutritionStatus,
    ],
  );

  const handleReset = useCallback(() => {
    reset(DEFAULT_FORM_VALUES);
    setSaveSuccess(false);
  }, [reset]);

  // ─── Loading state ─────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto space-y-6">
          <SkeletonHeader />
          {/* Form skeleton */}
          <div
            className="rounded-xl border p-6 space-y-4 animate-pulse"
            role="status"
            aria-label="Carregando formulário"
            style={{
              borderColor: 'var(--semantic-border-default)',
              backgroundColor: 'var(--semantic-surface-raised)',
            }}
          >
            <div
              className="h-10 rounded w-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div
              className="h-10 rounded w-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div
              className="h-10 rounded w-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div
              className="h-10 rounded w-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
          </div>
        </div>
      </Layout>
    );
  }

  // ─── Main render ───────────────────────────────────────────────────────────

  return (
    <Layout>
      <ErrorBoundary>
        <div className="max-w-3xl mx-auto space-y-6 pb-12">
          {/* ── Header ─────────────────────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: 'var(--clinical-nutrition-optimal-fill)',
                    color: 'var(--clinical-nutrition-optimal-on-fill)',
                  }}
                >
                  <Scale className="w-5 h-5" aria-hidden="true" />
                </div>
                <h1
                  className="text-2xl font-bold"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Avaliação Nutricional
                </h1>
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Cálculo de IMC e verificação de metas calóricas e proteicas para
                pacientes em UTI
              </p>
            </div>

            {/* Patient selector */}
            <div className="flex items-center gap-2">
              <User
                className="w-4 h-4 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <select
                value={selectedPatient}
                onChange={(e) => {
                  setSelectedPatient(e.target.value);
                  setSaveSuccess(false);
                }}
                className="text-sm rounded-lg border px-3 py-2 min-w-[200px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  color: 'var(--semantic-text-primary)',
                }}
                aria-label="Selecionar paciente"
              >
                {patients.map((p) => (
                  <option key={p.mpi_id} value={p.mpi_id}>
                    {p.display_name} — {p.bed_id || 'Sem leito'}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* ── Patient info bar ────────────────────────────────────────── */}
          {selectedPatientData && (
            <div
              className="flex items-center gap-3 px-4 py-3 rounded-xl border text-sm"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <Stethoscope
                className="w-4 h-4 flex-shrink-0"
                style={{ color: 'var(--semantic-text-secondary)' }}
                aria-hidden="true"
              />
              <span style={{ color: 'var(--semantic-text-primary)' }}>
                <strong>{selectedPatientData.display_name}</strong>
              </span>
              <span
                className="tabular-nums"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                MPI: {selectedPatientData.mpi_id}
              </span>
              <span
                className="tabular-nums ml-auto"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                Leito: {selectedPatientData.bed_id || 'N/D'}
              </span>
              <SeverityBadge
                severity={statusTokens.severity}
                showLabel={false}
              />
            </div>
          )}


          {/* ── BMI Display ─────────────────────────────────────────────── */}
          <div>
            <h2
              className="text-sm font-semibold uppercase tracking-wider mb-3"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Índice de Massa Corporal (IMC)
            </h2>
            <div
              className="rounded-xl border p-6"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{
                      backgroundColor: statusTokens.wash,
                      color: statusTokens.onSurface,
                    }}
                  >
                    <Target className="w-6 h-6" aria-hidden="true" />
                  </div>
                  <div>
                    <p
                      className="text-3xl font-bold tabular-nums"
                      style={{ color: statusTokens.onSurface }}
                    >
                      {bmiResult.value > 0
                        ? bmiResult.value.toFixed(1)
                        : '--'}
                    </p>
                    <p
                      className="text-sm"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      kg/m²
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold"
                    style={{
                      backgroundColor: statusTokens.wash,
                      color: statusTokens.onSurface,
                      borderColor: statusTokens.signal,
                      borderWidth: '1px',
                    }}
                  >
                    {bmiResult.classification}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Form ────────────────────────────────────────────────────── */}
          <div>
            <h2
              className="text-sm font-semibold uppercase tracking-wider mb-3"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Parâmetros Nutricionais
            </h2>

            <form
              onSubmit={handleSubmit(handleSave)}
              className="rounded-xl border overflow-hidden"
              style={{
                borderColor: 'var(--semantic-border-default)',
                backgroundColor: 'var(--semantic-surface-raised)',
              }}
            >
              <div className="p-6 space-y-4">
                {/* Altura */}
                <div>
                  <label
                    htmlFor="height"
                    className="block text-sm font-medium mb-1.5"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    Altura (cm)
                  </label>
                  <input
                    id="height"
                    type="number"
                    step="0.1"
                    min={50}
                    max={250}
                    {...register('height', { valueAsNumber: true })}
                    className="w-full rounded-lg border px-3 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                    style={{
                      borderColor: errors.height
                        ? 'var(--feedback-error-border-dark)'
                        : 'var(--semantic-border-default)',
                      backgroundColor: 'var(--semantic-surface-raised)',
                      color: 'var(--semantic-text-primary)',
                    }}
                    aria-describedby={errors.height ? 'height-error' : undefined}
                    aria-invalid={!!errors.height}
                  />
                  {errors.height && (
                    <p
                      id="height-error"
                      className="text-xs mt-1"
                      style={{ color: 'var(--feedback-error-text-dark)' }}
                      role="alert"
                    >
                      {errors.height.message}
                    </p>
                  )}
                </div>

                {/* Peso */}
                <div>
                  <label
                    htmlFor="weight"
                    className="block text-sm font-medium mb-1.5"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    Peso (kg)
                  </label>
                  <input
                    id="weight"
                    type="number"
                    step="0.1"
                    min={20}
                    max={300}
                    {...register('weight', { valueAsNumber: true })}
                    className="w-full rounded-lg border px-3 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                    style={{
                      borderColor: errors.weight
                        ? 'var(--feedback-error-border-dark)'
                        : 'var(--semantic-border-default)',
                      backgroundColor: 'var(--semantic-surface-raised)',
                      color: 'var(--semantic-text-primary)',
                    }}
                    aria-describedby={errors.weight ? 'weight-error' : undefined}
                    aria-invalid={!!errors.weight}
                  />
                  {errors.weight && (
                    <p
                      id="weight-error"
                      className="text-xs mt-1"
                      style={{ color: 'var(--feedback-error-text-dark)' }}
                      role="alert"
                    >
                      {errors.weight.message}
                    </p>
                  )}
                </div>

                {/* Meta calórica */}
                <div>
                  <label
                    htmlFor="calorieGoal"
                    className="block text-sm font-medium mb-1.5"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    Meta Calórica (kcal/dia)
                  </label>
                  <input
                    id="calorieGoal"
                    type="number"
                    step="50"
                    min={500}
                    max={5000}
                    {...register('calorieGoal', { valueAsNumber: true })}
                    className="w-full rounded-lg border px-3 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                    style={{
                      borderColor: errors.calorieGoal
                        ? 'var(--feedback-error-border-dark)'
                        : 'var(--semantic-border-default)',
                      backgroundColor: 'var(--semantic-surface-raised)',
                      color: 'var(--semantic-text-primary)',
                    }}
                    aria-describedby={
                      errors.calorieGoal ? 'calorieGoal-error' : undefined
                    }
                    aria-invalid={!!errors.calorieGoal}
                  />
                  {errors.calorieGoal && (
                    <p
                      id="calorieGoal-error"
                      className="text-xs mt-1"
                      style={{ color: 'var(--feedback-error-text-dark)' }}
                      role="alert"
                    >
                      {errors.calorieGoal.message}
                    </p>
                  )}
                </div>

                {/* Meta proteica */}
                <div>
                  <label
                    htmlFor="proteinGoal"
                    className="block text-sm font-medium mb-1.5"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    Meta Proteica (g/kg/dia)
                  </label>
                  <input
                    id="proteinGoal"
                    type="number"
                    step="0.1"
                    min={0.5}
                    max={3.0}
                    {...register('proteinGoal', { valueAsNumber: true })}
                    className="w-full rounded-lg border px-3 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
                    style={{
                      borderColor: errors.proteinGoal
                        ? 'var(--feedback-error-border-dark)'
                        : 'var(--semantic-border-default)',
                      backgroundColor: 'var(--semantic-surface-raised)',
                      color: 'var(--semantic-text-primary)',
                    }}
                    aria-describedby={
                      errors.proteinGoal ? 'proteinGoal-error' : undefined
                    }
                    aria-invalid={!!errors.proteinGoal}
                  />
                  {errors.proteinGoal && (
                    <p
                      id="proteinGoal-error"
                      className="text-xs mt-1"
                      style={{ color: 'var(--feedback-error-text-dark)' }}
                      role="alert"
                    >
                      {errors.proteinGoal.message}
                    </p>
                  )}
                </div>
              </div>

              {/* Nutritional status bar */}
              <div
                className="flex items-center gap-3 px-6 py-3 border-t"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  backgroundColor: 'var(--semantic-surface-overlay)',
                }}
              >
                <Heart
                  className="w-4 h-4"
                  style={{ color: statusTokens.onSurface }}
                  aria-hidden="true"
                />
                <span
                  className="text-sm font-medium"
                  style={{ color: 'var(--semantic-text-primary)' }}
                >
                  Status Nutricional:
                </span>
                <span
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold"
                  style={{
                    backgroundColor: statusTokens.fill,
                    color: statusTokens.onFill,
                  }}
                >
                  {statusTokens.severityLabel}
                </span>
                <span
                  className="text-xs ml-auto"
                  style={{ color: 'var(--semantic-text-secondary)' }}
                >
                  Meta calórica:{' '}
                  <span
                    style={{
                      color: meetsCalorieGoal
                        ? 'var(--clinical-nutrition-optimal-on-surface)'
                        : 'var(--clinical-nutrition-at-risk-on-surface)',
                      fontWeight: 600,
                    }}
                  >
                    {meetsCalorieGoal ? 'Atingida' : 'Não atingida'}
                  </span>
                  {' | '}
                  Meta proteica:{' '}
                  <span
                    style={{
                      color: meetsProteinGoal
                        ? 'var(--clinical-nutrition-optimal-on-surface)'
                        : 'var(--clinical-nutrition-at-risk-on-surface)',
                      fontWeight: 600,
                    }}
                  >
                    {meetsProteinGoal ? 'Atingida' : 'Não atingida'}
                  </span>
                </span>
              </div>

              {/* ── Actions ─────────────────────────────────────────────────── */}
              <div
                className="flex items-center gap-3 pt-4 border-t"
                style={{ borderColor: 'var(--semantic-border-default)' }}
              >
                <button
                  type="submit"
                  onClick={handleSubmit(handleSave)}
                  disabled={isLoading || !isValid}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: 'var(--clinical-nutrition-optimal-fill)',
                    color: 'var(--clinical-nutrition-optimal-on-fill)',
                  }}
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  ) : (
                    <Save className="w-4 h-4" aria-hidden="true" />
                  )}
                  Salvar Avaliação
                </button>

                <button
                  type="button"
                  onClick={handleReset}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 hover:opacity-80"
                  style={{
                    backgroundColor: 'var(--semantic-surface-raised)',
                    color: 'var(--semantic-text-primary)',
                    borderColor: 'var(--semantic-border-default)',
                    borderWidth: '1px',
                  }}
                >
                  <RefreshCw className="w-4 h-4" aria-hidden="true" />
                  Resetar
                </button>

              </div>
            </form>
          </div>

          {/* ── Save confirmation ──────────────────────────────────────── */}
          {saveSuccess && (
            <div
              role="status"
              aria-live="polite"
              className="flex items-center gap-2 px-4 py-3 rounded-xl border text-sm"
              style={{
                borderColor: 'var(--clinical-nutrition-optimal-signal)',
                backgroundColor: 'var(--clinical-nutrition-optimal-wash)',
                color: 'var(--clinical-nutrition-optimal-on-surface)',
              }}
            >
              <Scale className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              <span>
                Avaliação nutricional salva com sucesso para{' '}
                <strong>{selectedPatientData?.display_name}</strong> — IMC:{' '}
                {bmiResult.value > 0 ? bmiResult.value.toFixed(1) : '--'} kg/m²
                ({bmiResult.classification}) — Status:{' '}
                {statusTokens.severityLabel}
              </span>
            </div>
          )}
        </div>
      </ErrorBoundary>
    </Layout>
  );
}
