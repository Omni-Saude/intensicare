// ─── Re-export base types from BundleCard for canonical access ──────────────
export type { BundleCriterion, BundleStatus, BundleInfo } from '@/components/BundleCard';

import type { BundleInfo } from '@/components/BundleCard';

// ─── Mock Data: 5 Prophylaxis Bundles ───────────────────────────────────────

export const PROPHYLAXIS_BUNDLES: BundleInfo[] = [
  // ── Bundle 1: LAMGD — Úlcera de Estresse ─────────────────────────────────
  {
    id: 'lamgd',
    name: 'LAMGD — Úlcera de Estresse',
    status: 'partial',
    score: 75,
    criteria: [
      { id: 'lamgd-vm', label: 'Ventilação mecânica > 48h', met: true },
      { id: 'lamgd-coag', label: 'Coagulopatia (INR > 1.5 ou Plq < 50k)', met: true },
      { id: 'lamgd-choque', label: 'Choque (vasopressor)', met: true },
      { id: 'lamgd-cortico', label: 'Corticoterapia (hidrocortisona > 300mg/dia)', met: false },
    ],
  },

  // ── Bundle 2: TEV — Tromboembolismo Venoso ───────────────────────────────
  {
    id: 'tev',
    name: 'TEV — Tromboembolismo Venoso',
    status: 'complete',
    score: 100,
    criteria: [
      { id: 'tev-heparina', label: 'Heparina não fracionada ou HBPM prescrita', met: true },
      { id: 'tev-deamb', label: 'Deambulação contraindicada (ajuste de dose)', met: true },
      { id: 'tev-imc', label: 'Ajuste para IMC > 40 (dose aumentada)', met: true },
      { id: 'tev-renal', label: 'Ajuste renal (ClCr < 30 — HNF em vez de HBPM)', met: true },
      { id: 'tev-cpi', label: 'Compressão pneumática intermitente (se contraindicação)', met: true },
    ],
  },

  // ── Bundle 3: Hiperglicemia — Controle Glicêmico ─────────────────────────
  {
    id: 'hiperglicemia',
    name: 'Hiperglicemia — Controle Glicêmico',
    status: 'partial',
    score: 67,
    criteria: [
      { id: 'hg-insulina', label: 'Protocolo de insulina NPH ou escala móvel ativo', met: true },
      { id: 'hg-meta', label: 'Meta glicêmica 140-180 mg/dL', met: true },
      { id: 'hg-monitor', label: 'Monitorização glicêmica a cada 4-6h', met: false },
    ],
  },

  // ── Bundle 4: Mobilização Precoce ────────────────────────────────────────
  {
    id: 'mobilizacao',
    name: 'Mobilização Precoce',
    status: 'pending',
    score: 0,
    criteria: [
      { id: 'mob-avaliacao', label: 'Avaliação de mobilidade documentada nas últimas 24h', met: false },
      { id: 'mob-contraindic', label: 'Sem contraindicação absoluta', met: false },
      { id: 'mob-meta', label: 'Meta de saída do leito atingida', met: false },
    ],
  },

  // ── Bundle 5: Dispositivos Invasivos ─────────────────────────────────────
  {
    id: 'dispositivos',
    name: 'Dispositivos Invasivos',
    status: 'na',
    score: 0,
    criteria: [
      { id: 'disp-cvc-barreira', label: 'CVC: inserção com barreira máxima', met: false, na: true },
      { id: 'disp-cvc-curativo', label: 'CVC: curativo transparente (troca a cada 7 dias)', met: false, na: true },
      { id: 'disp-cvc-revisao', label: 'CVC: revisão diária de necessidade', met: false, na: true },
      { id: 'disp-svd', label: 'SVD: sistema fechado, fixação, abaixo do nível da bexiga', met: false, na: true },
      { id: 'disp-tot', label: 'TOT: pressão do cuff 20-30 cmH2O, cabeceira 30-45°', met: false, na: true },
    ],
  },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Derive computed score from criteria if not explicitly set. */
export function computeBundleScore(bundle: BundleInfo): number {
  if (bundle.score !== undefined) return bundle.score;
  const applicable = bundle.criteria.filter((c) => !c.na);
  if (applicable.length === 0) return 0;
  const met = applicable.filter((c) => c.met).length;
  return Math.round((met / applicable.length) * 100);
}

/** Maps a BundleStatus to a human-readable label. */
export const BUNDLE_STATUS_LABELS: Record<BundleInfo['status'], string> = {
  complete: 'Completo',
  partial: 'Parcial',
  pending: 'Pendente',
  na: 'N/A',
};
