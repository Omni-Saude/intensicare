export type FieldType =
  | 'string'
  | 'select'
  | 'number'
  | 'boolean'
  | 'checkbox'
  | 'date'
  | 'masked'
  | 'multicheck';

export interface FormField {
  name: string;
  label: string; // PT-BR
  type: FieldType;
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
  mask?: string;
  hint?: string;
}

export interface FormGroup {
  title: string;
  fields: FormField[];
  collapsible?: boolean;
  defaultOpen?: boolean;
}

export interface FormValidation {
  atLeastOne?: string[];
}

export interface FormConfig {
  id: string;
  title: string;
  description?: string;
  groups: FormGroup[];
  validation?: FormValidation;
}
