// ─── Nutrition Types ─────────────────────────────────────────────────────────
// M4 — Tipos e dados mock para avaliação nutricional.
// Contrato OpenAPI pendente; estrutura provisória.

export type NutritionStatus = 'optimal' | 'at-risk' | 'critical';

export interface NutritionalAssessment {
  patientMpiId: string;
  height: number; // altura em cm
  weight: number; // peso em kg
  bmi: number;
  calorieGoal: number; // meta calórica em kcal/dia
  proteinGoal: number; // meta proteica em g/kg/dia
  meetsCalorieGoal: boolean;
  meetsProteinGoal: boolean;
  status: NutritionStatus;
  assessedAt: string;
  assessedBy: string;
}

export interface MockPatient {
  mpiId: string;
  name: string;
  bed: string;
}

// ─── Mock Patients ──────────────────────────────────────────────────────────

export const MOCK_PATIENTS: MockPatient[] = [
  { mpiId: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpiId: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpiId: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];

// ─── BMI Classification (PT-BR) ─────────────────────────────────────────────

export interface BMIResult {
  value: number;
  classification: string;
}

/** Calcula IMC a partir de altura (cm) e peso (kg). */
export function computeBMI(heightCm: number, weightKg: number): BMIResult {
  if (heightCm <= 0 || weightKg <= 0) {
    return { value: 0, classification: 'Dados insuficientes' };
  }
  const heightM = heightCm / 100;
  const bmi = weightKg / (heightM * heightM);
  const rounded = Math.round(bmi * 10) / 10;

  let classification: string;
  if (bmi < 18.5) classification = 'Baixo peso';
  else if (bmi < 25) classification = 'Eutrófico';
  else if (bmi < 30) classification = 'Sobrepeso';
  else if (bmi < 35) classification = 'Obesidade Grau I';
  else if (bmi < 40) classification = 'Obesidade Grau II';
  else classification = 'Obesidade Grau III';

  return { value: rounded, classification };
}

// ─── Nutritional Status ─────────────────────────────────────────────────────

/**
 * Determina o status nutricional baseado no IMC e metas nutricionais.
 *
 * Regras:
 * - IMC < 16 ou IMC ≥ 40 com metas não atingidas → critical
 * - IMC fora da faixa eutrófica ou metas não atingidas → at-risk
 * - Caso contrário → optimal
 */
export function computeNutritionalStatus(
  bmi: number,
  meetsCalorieGoal: boolean,
  meetsProteinGoal: boolean,
): NutritionStatus {
  if (bmi < 16 || (bmi >= 40 && (!meetsCalorieGoal || !meetsProteinGoal))) {
    return 'critical';
  }

  if (
    bmi < 18.5 ||
    bmi >= 30 ||
    !meetsCalorieGoal ||
    !meetsProteinGoal
  ) {
    return 'at-risk';
  }

  return 'optimal';
}
