// ─── Communication Types ──────────────────────────────────────────────────
// Handoff / plantão SBAR types & mock data for Intensicare frontend-v2

export interface HandoffMessage {
  id: string;
  from_user: string;
  to_shift: string;
  sbar_s: string;
  sbar_b: string;
  sbar_a: string;
  sbar_r: string;
  created_at: string;
  read: boolean;
  urgent: boolean;
}

export interface NewHandoffMessage {
  to_shift: string;
  sbar_s: string;
  sbar_b: string;
  sbar_a: string;
  sbar_r: string;
  urgent: boolean;
}

// ─── Mock Data ─────────────────────────────────────────────────────────────

export const MOCK_SHIFTS = [
  'Manhã (07:00-13:00)',
  'Tarde (13:00-19:00)',
  'Noite (19:00-07:00)',
];

export const MOCK_MESSAGES: HandoffMessage[] = [
  {
    id: 'msg-001',
    from_user: 'Dra. Camila Rocha',
    to_shift: 'Tarde (13:00-19:00)',
    sbar_s: 'Paciente João, 68a, pós-op cardíaco (revascularização), extubado há 4h. Glasgow 15, estável hemodinamicamente.',
    sbar_b: 'IMC 29, DM2 controlado, IAM há 2 anos. Cirurgia sem intercorrências. CEC 72 min. Dreno mediastinal com débito sero-hemático 50 mL/h.',
    sbar_a: 'Evolução favorável. Sem sinais de tamponamento ou sangramento ativo. Gasometria arterial com PaO2 92 mmHg, lactato 1.4 mmol/L.',
    sbar_r: 'Manter monitorização do débito do dreno a cada hora. Previsão de retirada do dreno amanhã cedo. Iniciar deambulação assistida se mantiver estabilidade.',
    created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    read: false,
    urgent: false,
  },
  {
    id: 'msg-002',
    from_user: 'Enf. Marcos Teixeira',
    to_shift: 'Noite (19:00-07:00)',
    sbar_s: 'Paciente Maria, 74a, sepse urinária, em meropenem. PAM 68 mmHg, noradrenalina 0.12 mcg/kg/min.',
    sbar_b: 'Admitida há 48h por ITU complicada com progressão para choque séptico. Hemoculturas colhidas na admissão com E. coli sensível a meropenem. Balanço hídrico +1800 mL.',
    sbar_a: 'Ainda dependente de vasopressor em dose baixa-moderada. Diurese mantida (~0.6 mL/kg/h). Procalcitonina em queda (12 → 4.5 ng/mL). Resposta clínica parcial.',
    sbar_r: 'Tentar desmame da noradrenalina durante a noite (meta PAM ≥ 65). Colher nova procalcitonina às 23h. Manter vigilância de sobrecarga hídrica — avaliar furosemida se necessário.',
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    read: false,
    urgent: true,
  },
  {
    id: 'msg-003',
    from_user: 'Dr. Rafael Cunha',
    to_shift: 'Manhã (07:00-13:00)',
    sbar_s: 'Paciente Carlos, 55a, TCE grave, pós-craniectomia descompressiva. PIC controlada, sedação com propofol e fentanil.',
    sbar_b: 'Vítima de acidente automobilístico há 5 dias. Craniectomia frontotemporal direita. Monitorização com cateter de PIC (valores 12-18 mmHg). Sob DVA para controle pressórico e sedação profunda.',
    sbar_a: 'PIC estável nas últimas 12h, sem ondas plateau. Tomografia de controle sem novas lesões. Edema cerebral em regressão. Perfusão cerebral adequada (PCC > 60 mmHg).',
    sbar_r: 'Manter cabeceira elevada 30°, sedação profunda (RASS -4). Evitar hipertermia e hiponatremia. Coletar eletrólitos às 6h. Neurocirurgia avaliará tentativa de despertar às 10h.',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    read: true,
    urgent: false,
  },
  {
    id: 'msg-004',
    from_user: 'Enf. Juliana Andrade',
    to_shift: 'Noite (19:00-07:00)',
    sbar_s: 'Paciente Ana, 32a, pós-parto cesárea de urgência, em UTI por síndrome HELLP. Plaquetas 52.000, transaminases elevadas.',
    sbar_b: 'Gestação de 37 semanas, pré-eclâmpsia grave evoluindo para síndrome HELLP. Parto cesáreo há 36h sem complicações cirúrgicas. Recebeu plasmaférese pós-parto imediato.',
    sbar_a: 'Melhora progressiva das plaquetas (32k → 52k). Transaminases ainda elevadas mas em queda. PA controlada com nifedipino. Diurese mantida, bom débito.',
    sbar_r: 'Manter controle pressórico rigoroso (PA a cada 2h). Repetir plaquetas e transaminases às 2h da manhã. Se plaquetas > 80.000, avaliar alta da UTI pela manhã. Cuidado com sinais de hemorragia.',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    read: true,
    urgent: false,
  },
  {
    id: 'msg-005',
    from_user: 'Dr. Thiago Menezes',
    to_shift: 'Tarde (13:00-19:00)',
    sbar_s: 'Paciente Roberto, 81a, DPOC exacerbado, em VNI (BiPAP) há 2h. FR 28, SpO2 91% com FiO2 40%.',
    sbar_b: 'DPOC GOLD 4, múltiplas internações prévias. Admitido hoje com dispneia aguda e acidose respiratória (pH 7.29, pCO2 68). Iniciado BiPAP e broncodilatadores + corticoide EV.',
    sbar_a: 'Resposta parcial à VNI: FR caindo (34 → 28), SpO2 melhorando. Gasometria de controle em 1h definirá necessidade de IOT. Paciente consciente, cooperativo com VNI.',
    sbar_r: 'URGENTE: gasometria de controle às 15h. Se pH < 7.25 ou rebaixamento de consciência, preparar para IOT. Manter VNI com FiO2 40%, IPAP 14, EPAP 6. Familiar presente — comunicar evolução.',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 7).toISOString(),
    read: false,
    urgent: true,
  },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

export function formatRelativeTime(ts: string): string {
  const now = Date.now();
  const then = new Date(ts).getTime();
  const diffMs = now - then;

  if (diffMs < 0) return 'agora mesmo';

  const minutes = Math.floor(diffMs / (1000 * 60));
  if (minutes < 1) return 'agora mesmo';
  if (minutes === 1) return 'há 1 minuto';
  if (minutes < 60) return `há ${minutes} minutos`;

  const hours = Math.floor(minutes / 60);
  if (hours === 1) return 'há 1 hora';
  if (hours < 24) return `há ${hours} horas`;

  const days = Math.floor(hours / 24);
  if (days === 1) return 'há 1 dia';
  return `há ${days} dias`;
}
