# RUNBOOK — IntensiCare Platform Local Execution

**Target:** Parreira (DevOps Orchestrator)  
**Source:** Niemeyer (System Architect)  
**Date:** 2026-07-09  
**Goal:** Subir plataforma completa (backend + frontend) localmente, monitorar, e coordenar fixes durante showcase  

---

## ═══════ ENVELOPE ═══════

| Campo | Valor |
|-------|-------|
| **Goal** | Plataforma IntensiCare rodando localmente — backend FastAPI (porta 8000) + frontend Next.js (porta 3000) — com health checks ativos e monitoramento de erros |
| **Context** | Docker PostgreSQL+Redis já rodando. Migrations no head. Backend e frontend compilam sem erros (Ive verificou). 89 API functions, 33 páginas, 24 routers. |
| **Constraints** | Não modificar código (showcase = versão atual). Rodar localmente. Manter logs para debugging. |
| **Done When** | `curl localhost:8000/health` retorna 200. `curl localhost:3000` retorna HTML. Navegação entre 3+ páginas funciona. Zero crashes em 10min. |
| **Risk** | LOW — ambiente local, sem dados reais |
| **Scope** | Apenas runtime — iniciar, monitorar, manter vivo |

---

## ═══════ FASE 0 — RECON (≤5min) ═══════

### Verificar pré-requisitos

```bash
# 1. Docker containers (PostgreSQL + Redis) — DEVEM estar rodando
docker ps --format '{{.Names}} {{.Status}}' | grep -E 'intensicare-postgres|intensicare-redis'

# 2. Python venv
/Users/familia/intensicare/.venv/bin/python --version  # Deve ser 3.14.x

# 3. Node
node --version  # Deve ser v22+

# 4. Portas livres
lsof -ti:8000 && echo "⚠️ PORTA 8000 OCUPADA — matar processo" || echo "✅ Porta 8000 livre"
lsof -ti:3000 && echo "⚠️ PORTA 3000 OCUPADA — matar processo" || echo "✅ Porta 3000 livre"

# 5. Migrations no head
cd /Users/familia/intensicare && .venv/bin/python -m alembic current 2>&1 | grep '(head)'

# 6. Dependências instaladas
.venv/bin/pip check 2>&1 | tail -1  # Deve ser "No broken requirements found"
```

### Se portas ocupadas

```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

### Gate FASE 0

Todos os 6 checks acima DEVEM passar antes de prosseguir.

---

## ═══════ FASE 1 — Backend (≤2min) ═══════

### 1.1 Configurar variáveis de ambiente

O arquivo `/Users/familia/intensicare/.env` já está configurado. Verificar apenas:

```bash
cd /Users/familia/intensicare
source .env 2>/dev/null || export $(grep -v '^#' .env | grep -v '^$' | xargs)
```

**Atenção:** `SECRET_KEY=***` está com placeholder. Para showcase local, usar:

```bash
export SECRET_KEY="intensicare-local-showcase-2026"
export JWT_SECRET_KEY="intensicare-local-showcase-2026"
```

### 1.2 Iniciar uvicorn

```bash
cd /Users/familia/intensicare

.venv/bin/uvicorn intensicare.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info \
  2>&1 | tee /tmp/intensicare-backend.log
```

**Modo Parreira:** Usar `terminal(background=true, notify_on_complete=true)` para o comando acima. O `tee` grava logs em `/tmp/intensicare-backend.log` para monitoramento.

### 1.3 Health check

```bash
# Aguardar 4s para startup
sleep 4

# Health básico
curl -s http://localhost:8000/health | python3 -m json.tool

# Deve retornar:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "checks": {
#     "database": {"status": "pass", ...},
#     "redis": {"status": "pass", ...}
#   }
# }

# API v1 health (mais detalhado)
curl -s http://localhost:8000/api/v1/health

# Listar pathways (verifica DB + API)
curl -s http://localhost:8000/api/v1/pathways | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d.get(\"pathways\",[]))} pathways')"
```

### Gate FASE 1

- [ ] `curl localhost:8000/health` retorna `"status": "healthy"`
- [ ] `curl localhost:8000/api/v1/pathways` retorna JSON válido
- [ ] Sem erros no log (`grep ERROR /tmp/intensicare-backend.log` vazio)

---

## ═══════ FASE 2 — Frontend (≤2min) ═══════

### 2.1 Verificar conectividade com backend

O frontend em dev mode usa o `rewrites` do Next.js para proxy ao backend. Verificar:

```bash
cd /Users/familia/intensicare/frontend-v2
grep -A10 'rewrites' next.config.ts 2>/dev/null || grep -A10 'rewrites' next.config.js 2>/dev/null
```

Se houver rewrite configurado para `localhost:8000`, o frontend consegue chamar a API localmente.

### 2.2 Iniciar Next.js dev server

```bash
cd /Users/familia/intensicare/frontend-v2
npm run dev 2>&1 | tee /tmp/intensicare-frontend.log
```

### 2.3 Health check

```bash
# Aguardar compilação (~5-10s)
sleep 8

# Verificar se serviu HTML
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Deve retornar 200

# Verificar página de login
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/login
# Deve retornar 200 (ou 307 redirect)

# Verificar dashboard
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/dashboard
# Deve retornar 307 (redirect para login se não autenticado) — NÃO 500
```

### Gate FASE 2

- [ ] `curl localhost:3000` retorna HTTP 200
- [ ] `curl localhost:3000/dashboard` retorna HTTP 307 (redirect) — NÃO 500
- [ ] Sem erros no log de build (`grep ERROR /tmp/intensicare-frontend.log` vazio)

---

## ═══════ FASE 3 — Smoke Test (≤5min) ═══════

### 3.1 Testar fluxo completo via API

```bash
BASE="http://localhost:8000"

# Login
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")

if [ -z "$TOKEN" ]; then
  echo "⚠️  Login falhou — verificar se usuário admin existe no banco"
  echo "   Criar via: curl -X POST $BASE/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"email\":\"admin@intensicare.local\",\"password\":\"admin\",\"display_name\":\"Admin\"}'"
else
  echo "✅ Login OK"

  # Dashboard
  curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/v1/dashboard" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Dashboard: {d.get(\"total\",0)} patients')"

  # Pathways
  curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/v1/pathways" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Pathways: {len(d.get(\"pathways\",[]))}')"

  # Alerts
  curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/v1/alerts?status=active&limit=5" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Alerts: {d.get(\"total\",0)}')"

  # Evos
  curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/v1/patients/MPI-001/evolucoes" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Evolucoes: {len(d.get(\"evolucoes\",[]))}')"
fi
```

### 3.2 Verificar endpoints críticos

```bash
ENDPOINTS=(
  "/api/v1/pathways"
  "/api/v1/pathways/1"
  "/api/v1/beds"
  "/api/v1/indicators"
  "/api/v1/alert-routing"
  "/api/v1/prophylaxis/bundles"
  "/api/v1/antimicrobial/criteria"
  "/api/v1/clinical-forms"
)

for ep in "${ENDPOINTS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$ep")
  if [ "$code" = "200" ] || [ "$code" = "401" ] || [ "$code" = "307" ]; then
    echo "✅ $ep → $code"
  else
    echo "❌ $ep → $code"
  fi
done
```

401 é aceitável (requer auth). 500 NÃO é aceitável.

### Gate FASE 3

- [ ] Login funciona (ou user admin criado)
- [ ] Dashboard retorna JSON
- [ ] Pathways retorna JSON
- [ ] Nenhum endpoint retorna 500

---

## ═══════ FASE 4 — Monitoramento Contínuo ═══════

### 4.1 Log tail (terminal separado)

```bash
# Terminal 1: backend logs
tail -f /tmp/intensicare-backend.log

# Terminal 2: frontend logs
tail -f /tmp/intensicare-frontend.log
```

### 4.2 Health check loop (cronjob ou watch)

```bash
# Rodar a cada 30s, alertar se falhar
watch -n 30 '
  echo "=== $(date) ==="
  curl -s -o /dev/null -w "Backend: %{http_code}\n" http://localhost:8000/health
  curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost:3000
'
```

### 4.3 Sinais de erro a monitorar

| Sintoma | Causa provável | Ação |
|---------|---------------|------|
| Backend 500 no `/health` | DB desconectou | `docker restart intensicare-postgres` |
| Backend `Address already in use` | Processo zumbi na porta 8000 | `lsof -ti:8000 \| xargs kill -9` |
| Frontend `ECONNREFUSED` no proxy | Backend caiu | Verificar FASE 1, reiniciar uvicorn |
| Frontend build loop infinito | Arquivo corrompido no hot-reload | `rm -rf .next && npm run dev` |
| Autenticação 401 em tudo | `SECRET_KEY` inconsistente | Re-exportar `SECRET_KEY` e reiniciar backend |
| Página em branco no browser | Erro React não capturado | Ver console do navegador (F12) |

---

## ═══════ FASE 5 — Coordenação de Fixes ═══════

### Se um bug for encontrado durante o showcase

```
1. NÃO parar a plataforma (a menos que seja crash total)
2. Anotar: página, ação, erro exato
3. Classificar severidade:
   - BLOCKER: crash, 500, página em branco → Parreira corrige IMEDIATO
   - MAJOR: funcionalidade quebrada mas plataforma funciona → Niemeyer diagnostica
   - MINOR: visual, texto, UX → Ive corrige depois
4. Se backend: Parreira verifica logs → Niemeyer analisa causa raiz → coding agent corrige
5. Se frontend: Ive verifica console → corrige com hot-reload ativo
6. Após fix: repetir smoke test da FASE 3
```

### Quem chamar para cada tipo de erro

| Tipo de erro | Diagnosticador | Executor do fix |
|-------------|---------------|-----------------|
| Erro 500 no backend | Niemeyer (lê stack trace, identifica causa) | Parreira (reinicia serviço) ou coding agent |
| Erro de tipo/API no frontend | Ive (verifica `lib/api.ts`, tipos) | Ive |
| Container caiu (DB/Redis) | Parreira | Parreira (`docker restart`) |
| Build quebrado | Ive (`npm run build` logs) | Ive |
| Dados inconsistentes | Niemeyer (verifica schema vs query) | Parreira ou coding agent |
| Performance/lentidão | Parreira (`ops-observability`) | Parreira |

---

## ═══════ QUICK REFERENCE ═══════

### Comandos essenciais

```bash
# Status rápido
curl -s localhost:8000/health | python3 -m json.tool | grep status
curl -s -o /dev/null -w "%{http_code}" localhost:3000

# Reiniciar backend
lsof -ti:8000 | xargs kill -9 2>/dev/null
cd /Users/familia/intensicare && .venv/bin/uvicorn intensicare.main:app --host 0.0.0.0 --port 8000 --reload &

# Reiniciar frontend
lsof -ti:3000 | xargs kill -9 2>/dev/null
cd /Users/familia/intensicare/frontend-v2 && npm run dev &

# Reiniciar DB
docker restart intensicare-postgres

# Ver logs
tail -50 /tmp/intensicare-backend.log
tail -50 /tmp/intensicare-frontend.log
```

### Portas e URLs

| Serviço | Porta | Health Check |
|---------|-------|-------------|
| PostgreSQL | 5432 | `docker exec intensicare-postgres pg_isready` |
| Redis | 6379 | `redis-cli ping` |
| Backend API | 8000 | `GET /health` |
| Frontend | 3000 | `GET /` |

### Arquivos importantes

| Arquivo | Propósito |
|---------|----------|
| `/Users/familia/intensicare/.env` | Variáveis de ambiente do backend |
| `/tmp/intensicare-backend.log` | Logs do uvicorn |
| `/tmp/intensicare-frontend.log` | Logs do Next.js |
| `/Users/familia/intensicare/docker-compose.yml` | Infra (DB + Redis) |
| `/Users/familia/intensicare/docs/audit/FRONTEND_AUDIT.md` | Diagnóstico frontend |
| `/Users/familia/intensicare/docs/audit/FORENSICS_SYNTHESIS.md` | Estado completo da plataforma |

---

## ═══════ DONE WHEN ═══════

- [ ] PostgreSQL + Redis rodando (Docker)
- [ ] Backend respondendo em `localhost:8000/health` com `"status": "healthy"`
- [ ] Frontend respondendo em `localhost:3000` com HTML
- [ ] Login funcional (ou user admin criado)
- [ ] Dashboard, Pathways, Beds endpoints retornam JSON
- [ ] Navegação entre 3+ páginas no browser funciona
- [ ] Zero crashes em 10 minutos de monitoramento
- [ ] Logs sem ERROR após startup

---

*RUNBOOK produzido por Niemeyer (System Architect) para Parreira (DevOps Orchestrator).*  
*Baseado em: forensics audit, gap closure reports, Ive handoff verification.*
