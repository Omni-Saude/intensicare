export type ThresholdSeverity = 'normal' | 'watch' | 'urgent' | 'critical';

export interface VitalThreshold {
  vitalName: string;
  unit: string;
  lowCritical: number;
  lowWarn: number;
  highWarn: number;
  highCritical: number;
}

export interface ScoreBand {
  name: string;
  bands: { min: number; max: number; severity: ThresholdSeverity }[];
}
