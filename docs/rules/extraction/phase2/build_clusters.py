#!/usr/bin/env python3
"""Phase 2 pre-processing: assign every extracted rule to a reconciliation cluster.

Slug -> cluster mapping derived from manual review of all 143 provisional domain
slugs (see rules-index.json). Two slugs are partition-conditional. Unknown slugs
land in UNMAPPED for manual triage — the build fails loudly if any appear.
"""
import json, re, sys, os
from collections import defaultdict

SP = '/private/tmp/claude-501/-Users-familia-intensicare/dc1c3d01-243b-43fa-9645-7c872cd95c26/scratchpad'

CLUSTERS = {
    'sepse': ['sepse', 'sepsis', 'interativa', 'trilhainterativa'],
    'piora-clinica': ['piora'],
    'clinical-scoring': ['sofa', 'scoring', 'neuro', 'pain', 'pfratio', 'pam'],
    'ventilacao': ['vent', 'ventilacao', 'resp', 'devices'],
    'sedacao': ['sedacao'],
    'nutricao': ['nutricao', 'nutrition', 'nutri'],
    'profilaxia': ['profilaxia'],
    'antimicrobiano': ['antimicrobiano'],
    'equilibrio': ['equilibrio'],
    'estabilidade': ['estabilidade', 'estab', 'estabilizacao'],
    'eficiencia': ['eficiencia'],
    'balanco-hidrico': ['balanco', 'balancohidrico', 'fluidbalance', 'entrada', 'saida'],
    'prescricao': ['prescricao', 'presc', 'pharma', 'drug', 'medicacao'],
    'evolucoes': ['evolucao', 'evo', 'prontuario', 'formulario', 'formdinamico'],
    'formularios-clinicos': ['medico', 'nursing', 'tecnursing', 'fono', 'psico',
                             'music', 'physio', 'wound', 'lpp', 'lesoes',
                             'diagnostico', 'intercorrencia'],
    'sinais-vitais': ['vitais', 'vitals', 'sinal', 'val', 'labs', 'time'],
    'movimentacao-adt': ['movimentacao', 'mov', 'leito', 'ocupacao', 'op',
                         'gestaopaciente', 'paciente', 'patient', 'vinculo'],
    'tenancy-organizacao': ['empresa', 'estabelecimento', 'setor', 'mw', 'tenant',
                            'selectplace', 'grupo'],
    'auth-usuarios': ['acesso', 'auth', 'authz', 'permissao', 'permissoes', 'login',
                      'usuario', 'cargos', 'profissional', 'cons', 'cpf', 'rotas'],
    'alertas': ['alerta', 'alert', 'assistido', 'status'],
    'comunicacao': ['observacao', 'checagem', 'notificacao', 'mensagem', 'msg',
                    'chat', 'feed', 'video', 'acao', 'reacao'],
    'indicadores-etl': ['indicador', 'indicadores', 'indic', 'etl', 'dashboard',
                        'integracao'],
    'trilhas-engine': ['trilha', 'config'],
    'documentacao-faturamento': ['glosa', 'billing', 'auditoria', 'audit', 'pdf',
                                 'doc', 'assinatura', 'sign', 'relatorio',
                                 'reporting', 'inconsistencia', 'arquivo', 'upload'],
    'operacional-infra': ['ops', 'operational', 'scheduling', 'turno', 'settings',
                          'util', 'model', 'ser', 'err', 'paginacao', 'seed',
                          'data', 'systemic', 'breadcrumb', 'search', 'offline'],
    'cadastros-ui': ['cadastro', 'filtro'],
    'auditoria-logs': ['log'],
}

# gap-partition slugs (BE-12/BE-13/FE-09/COORD) — defaults; specific rules overridden below
GAP_SLUGS = {
    'carepath': 'trilhas-engine', 'classif': 'ventilacao', 'sched': 'operacional-infra',
    'access': 'auth-usuarios', 'admin': 'operacional-infra', 'deploy': 'operacional-infra',
    'build': 'operacional-infra', 'pwa': 'operacional-infra', 'ui': 'alertas',
    'clinical': 'formularios-clinicos',
}

OVERRIDES = {
    'RULE-PHYSIO-BE-12-001': 'clinical-scoring',        # age //365 calculation
    'RULE-CAREPATH-BE-12-002': 'sepse',
    'RULE-CAREPATH-BE-12-003': 'sepse',
    'RULE-CAREPATH-BE-12-004': 'sepse',
    'RULE-CAREPATH-BE-12-005': 'sepse',
    'RULE-ALERT-BE-12-006': 'alertas',
    'RULE-ALERT-BE-12-007': 'alertas',
    'RULE-ALERT-BE-12-008': 'alertas',
    'RULE-ALERT-BE-12-009': 'alertas',
    'RULE-ALERT-BE-12-011': 'alertas',
    'RULE-SCHED-BE-12-020': 'auditoria-logs',           # log retention purge
    'RULE-VALIDATION-BE-12-014': 'tenancy-organizacao', # GrupoAcesso xor
    'RULE-VALIDATION-BE-12-022': 'auth-usuarios',       # API key uniqueness
    'RULE-ADMIN-BE-12-021': 'prescricao',               # offline prescription validity
    'RULE-ADMIN-BE-12-031': 'movimentacao-adt',         # leito default type
    'RULE-OPERATIONAL-BE-12-023': 'comunicacao',        # notification interaction
    'RULE-CAREPATH-BE-12-027': 'movimentacao-adt',
    'RULE-CAREPATH-BE-12-028': 'trilhas-engine',
    'RULE-CAREPATH-BE-12-029': 'movimentacao-adt',
    'RULE-CAREPATH-FE-09-009': 'comunicacao',           # telemedicine stack
    'RULE-choice-BE-10-069': 'clinical-scoring',        # RASS enum
    'RULE-choice-BE-10-070': 'ventilacao',              # ventilation/device/modality enums
    'RULE-choice-BE-10-071': 'sedacao',                 # sedative drug enum
    'RULE-choice-BE-10-072': 'clinical-scoring',        # SDRA/ARDS severity enum
}

# partition-conditional slugs (mixed content confirmed by sampling)
def conditional(slug, partition):
    if slug == 'validation':
        return 'movimentacao-adt' if partition.startswith('BE') else 'sinais-vitais'
    if slug == 'filter':
        return 'operacional-infra'
    return None

SLUG2CLUSTER = {}
for c, slugs in CLUSTERS.items():
    for s in slugs:
        assert s not in SLUG2CLUSTER, f'slug {s} mapped twice'
        SLUG2CLUSTER[s] = c
for s, c in GAP_SLUGS.items():
    SLUG2CLUSTER.setdefault(s, c)

def main():
    idx = json.load(open(f'{SP}/findings/rules-index.json'))
    full = json.load(open(f'{SP}/findings/rules-full.json'))
    assign = {}
    unmapped = []
    for r in idx:
        if r['id'] in OVERRIDES:
            assign[r['id']] = OVERRIDES[r['id']]
            continue
        m = re.match(r'RULE-(.+?)-(BE|FE|COORD)-', r['id'])
        slug = m.group(1).lower() if m else None
        cl = conditional(slug, r['partition']) or SLUG2CLUSTER.get(slug)
        if not cl:
            unmapped.append((r['id'], slug))
            continue
        assign[r['id']] = cl
    if unmapped:
        print('UNMAPPED SLUGS — extend the map:', file=sys.stderr)
        for rid, slug in unmapped:
            print('  ', slug, rid, file=sys.stderr)
        sys.exit(1)
    by = defaultdict(list)
    for rid, cl in assign.items():
        by[cl].append(rid)
    os.makedirs(f'{SP}/clusters', exist_ok=True)
    manifest = {}
    for cl, rids in sorted(by.items(), key=lambda kv: -len(kv[1])):
        entries = {rid: full[rid] for rid in sorted(rids)}
        path = f'{SP}/clusters/{cl}.json'
        json.dump(entries, open(path, 'w'), indent=1, default=str)
        manifest[cl] = {'count': len(rids), 'file': path,
                        'size_kb': os.path.getsize(path) // 1024}
        print(f'{len(rids):4d}  {manifest[cl]["size_kb"]:5d}KB  {cl}')
    json.dump(manifest, open(f'{SP}/clusters/manifest.json', 'w'), indent=1)
    print('total assigned:', len(assign), 'of', len(idx))

if __name__ == '__main__':
    main()
