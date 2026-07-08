// ─── Fluid Balance Types ───────────────────────────────────────────────────
// FASE 2 — Tipos e dados mock para monitoramento de balanço hídrico.
// Estrutura alinhada com domain_fluid_balance.py (nursing day 07:00-07:00).
// Contrato OpenAPI pendente; estrutura provisória.

// ─── Categorias de entrada/saída ───────────────────────────────────────────

export type FluidIntakeCategory = 'enteral' | 'parenteral' | 'oral';

export type FluidOutputCategory = 'urine' | 'drain' | 'other';

export type FluidRecordCategory = FluidIntakeCategory | FluidOutputCategory;

// ─── Balanço líquido status ────────────────────────────────────────────────

export type BalanceStatus = 'positive' | 'negative' | 'neutral';

// ─── Registro individual ───────────────────────────────────────────────────

export interface FluidBalanceRecord {
  /** Timestamp ISO 8601 do registro */
  timestamp: string;
  /** Volume em ml (entrada positiva, saída negativa no contexto do registro) */
  intake_ml: number;
  /** Volume de saída em ml */
  output_ml: number;
  /** Balanço líquido do registro (intake - output) */
  balance_ml: number;
  /** Categoria clínica do registro */
  category: FluidRecordCategory;
}

// ─── Sumário diário (nursing day) ──────────────────────────────────────────

export interface FluidBalanceSummary {
  /** Data do plantão (YYYY-MM-DD, janela 07:00-07:00) */
  nursing_date: string;
  /** Total de entradas em ml */
  total_intake_ml: number;
  /** Total de saídas em ml */
  total_output_ml: number;
  /** Balanço líquido (intake - output) */
  net_balance_ml: number;
  /** Classificação do balanço */
  status: BalanceStatus;
}

// ─── Tendência (série temporal para gráfico) ───────────────────────────────

export interface FluidBalanceTrend {
  /** Data do registro (YYYY-MM-DD) */
  date: string;
  /** Total de entradas no dia em ml */
  intake_ml: number;
  /** Total de saídas no dia em ml */
  output_ml: number;
  /** Balanço líquido do dia */
  balance_ml: number;
}

// ─── Classificação ─────────────────────────────────────────────────────────

/**
 * Classifica o balanço hídrico com base no net balance em ml.
 *
 * Limiares clínicos:
 * - > +500 ml → 'positive' (balanço positivo — retenção hídrica)
 * - < -500 ml → 'negative' (balanço negativo — déficit)
 * - entre -500 e +500 ml → 'neutral' (equilibrado)
 */
export function classifyBalance(net_ml: number): BalanceStatus {
  if (net_ml > 500) return 'positive';
  if (net_ml < -500) return 'negative';
  return 'neutral';
}

// ─── Helpers de formatação ─────────────────────────────────────────────────

/** Formata volume em ml para exibição com sinal e unidade */
export function formatVolume(ml: number): string {
  const sign = ml > 0 ? '+' : ml < 0 ? '-' : '±';
  const abs = Math.abs(ml);
  return `${sign}${abs.toLocaleString('pt-BR')} ml`;
}

/** Converte status para label PT-BR */
export const BALANCE_STATUS_LABELS: Record<BalanceStatus, string> = {
  positive: 'Positivo',
  negative: 'Negativo',
  neutral: 'Neutro',
};

// ─── Mock Data ─────────────────────────────────────────────────────────────

/** 1 registro de sumário diário (hoje — nursing day atual) */
export const MOCK_SUMMARY: FluidBalanceSummary = {
  nursing_date: new Date().toISOString().slice(0, 10),
  total_intake_ml: 2500,
  total_output_ml: 1800,
  net_balance_ml: 700,
  status: 'positive',
};

/** 7 registros de tendência (últimos 7 dias) para gráfico */
export const MOCK_TREND: FluidBalanceTrend[] = (() => {
  const today = new Date();
  const records: FluidBalanceTrend[] = [];

  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const date = d.toISOString().slice(0, 10);

    // Dados realistas variando com padrão clínico
    const intake = 2000 + Math.round(Math.random() * 1200); // 2000–3200 ml
    const output = 1500 + Math.round(Math.random() * 1000); // 1500–2500 ml
    const balance = intake - output;

    records.push({
      date,
      intake_ml: intake,
      output_ml: output,
      balance_ml: balance,
    });
  }

  return records;
})();

/** 12 registros variados de entradas/saídas (últimas 24h) */
export const MOCK_RECORDS: FluidBalanceRecord[] = [
  {
    timestamp: new Date(Date.now() - 23 * 60 * 60 * 1000).toISOString(),
    intake_ml: 500,
    output_ml: 0,
    balance_ml: 500,
    category: 'enteral',
  },
  {
    timestamp: new Date(Date.now() - 21 * 60 * 60 * 1000).toISOString(),
    intake_ml: 0,
    output_ml: 300,
    balance_ml: -300,
    category: 'urine',
  },
  {
    timestamp: new Date(Date.now() - 19 * 60 * 60 * 1000).toISOString(),
    intake_ml: 100,
    output_ml: 0,
    balance_ml: 100,
    category: 'oral',
  },
  {
    timestamp: new Date(Date.now() - 17 * 60 * 60 * 1000).toISOString(),
    intake_ml: 250,
    output_ml: 0,
    balance_ml: 250,
    category: 'parenteral',
  },
  {
    timestamp: new Date(Date.now() - 15 * 60 * 60 * 1000).toISOString(),
    intake_ml: 0,
    output_ml: 200,
    balance_ml: -200,
    category: 'drain',
  },
  {
    timestamp: new Date(Date.now() - 13 * 60 * 60 * 1000).toISOString(),
    intake_ml: 500,
    output_ml: 0,
    balance_ml: 500,
    category: 'enteral',
  },
  {
    timestamp: new Date(Date.now() - 11 * 60 * 60 * 1000).toISOString(),
    intake_ml: 0,
    output_ml: 400,
    balance_ml: -400,
    category: 'urine',
  },
  {
    timestamp: new Date(Date.now() - 9 * 60 * 60 * 1000).toISOString(),
    intake_ml: 150,
    output_ml: 0,
    balance_ml: 150,
    category: 'oral',
  },
  {
    timestamp: new Date(Date.now() - 7 * 60 * 60 * 1000).toISOString(),
    intake_ml: 0,
    output_ml: 100,
    balance_ml: -100,
    category: 'other',
  },
  {
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    intake_ml: 500,
    output_ml: 0,
    balance_ml: 500,
    category: 'parenteral',
  },
  {
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    intake_ml: 0,
    output_ml: 350,
    balance_ml: -350,
    category: 'urine',
  },
  {
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    intake_ml: 0,
    output_ml: 250,
    balance_ml: -250,
    category: 'urine',
  },
];

// ─── Labels PT-BR ──────────────────────────────────────────────────────────

export const CATEGORY_LABELS_FLUID: Record<FluidRecordCategory, string> = {
  enteral: 'Enteral',
  parenteral: 'Parenteral',
  oral: 'Oral',
  urine: 'Diurese',
  drain: 'Dreno',
  other: 'Outros',
};

/** Status → ícone mapping para uso em cards (usa tokens Lucide) */
export const BALANCE_STATUS_ICON = {
  positive: 'TrendingUp',
  negative: 'TrendingDown',
  neutral: 'Minus',
} as const;
