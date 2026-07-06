{{/*
Expand the name of the chart.
*/}}
{{- define "intensicare.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "intensicare.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "intensicare.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "intensicare.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "intensicare.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: intensicare-platform
app.kubernetes.io/environment: {{ .Values.global.environment }}
{{- end }}

{{/*
API labels
*/}}
{{- define "intensicare.apiLabels" -}}
{{ include "intensicare.labels" . }}
app.kubernetes.io/component: api
{{- end }}

{{/*
Worker labels
*/}}
{{- define "intensicare.workerLabels" -}}
{{ include "intensicare.labels" . }}
app.kubernetes.io/component: worker
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "intensicare.frontendLabels" -}}
{{ include "intensicare.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
API selector labels
*/}}
{{- define "intensicare.apiSelectorLabels" -}}
app.kubernetes.io/name: {{ include "intensicare.name" . }}-api
app.kubernetes.io/component: api
{{- end }}

{{/*
Worker selector labels
*/}}
{{- define "intensicare.workerSelectorLabels" -}}
app.kubernetes.io/name: {{ include "intensicare.name" . }}-worker
app.kubernetes.io/component: worker
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "intensicare.frontendSelectorLabels" -}}
app.kubernetes.io/name: {{ include "intensicare.name" . }}-frontend
app.kubernetes.io/component: frontend
{{- end }}

{{/*
OTEL Collector config as JSON (for ConfigMap)
*/}}
{{- define "intensicare.otelConfig" -}}
{{- .Values.otelCollector.config | toYaml }}
{{- end }}
