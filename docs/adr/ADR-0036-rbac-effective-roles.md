# ADR-0036: RBAC com Roles Efetivos — Fim do Bypass Incondicional de `is_admin`

**Status:** accepted
**Data:** 2026-07-12
**Decisão por:** Orquestração de correção pós-auditoria (Claude Fable 5) — ratificação pendente do arquiteto

---

## Contexto

A auditoria full-spectrum (`docs/audit/fullspectrum/`) classificou o RBAC/ABAC do backend como **decorativo** (audit CRITICAL #6), com quatro falhas concretas:

1. **`_has_role` com bypass incondicional de `is_admin`** (`src/intensicare/auth/dependencies.py`) — qualquer guard clínico (`require_medico`, `require_enfermeiro`, `require_fisioterapeuta`, `require_farmacia`, `require_nutricao`) era satisfeito por `is_admin=True`, independente do `role` real do usuário.
2. **`role` inerte** — um administrador de sistema podia rodar endpoints clínicos com `user.role="readonly"` sem que isso importasse, porque o bypass do item 1 ignorava o campo.
3. **`require_abac` chamado com role hardcoded `"admin"`** em vez do `role` efetivo do usuário autenticado, em `src/intensicare/api/v1/admin.py`.
4. **Vocabulários desconexos**: `CLINICAL_ROLES` em `src/intensicare/auth/dependencies.py` (PT-BR: `admin`, `medico`, `enfermeiro`, `fisioterapeuta`, `farmacia`, `nutricao`, `readonly`) vs. `ClinicalRole` (EN) consumido pela matriz ABAC em `src/intensicare/auth/abac.py` — sem mapeamento, todo role PT-BR desconhecido do enum caía silenciosamente em `VIEWER`.

## Decisão

**Remover o bypass de `is_admin` em guards clínicos; tornar o `role` efetivo do usuário a única fonte de decisão de acesso clínico; unificar os vocabulários PT-BR/EN; e tratar inconsistência de dados como condição bloqueante, não silenciosa.**

1. **Bypass removido**: `_has_role` (`src/intensicare/auth/dependencies.py`, linhas ~122–135) passou a checar apenas `user.role in roles` — sem atalho para `is_admin`. Acesso administrativo não-clínico continua garantido separadamente por `require_admin` (linhas 92–100, que checa `current_user.is_admin`). O código documenta explicitamente que um levantamento prévio (grep) não encontrou nenhum router ativo dependendo do bypass, tornando a remoção comportamentalmente segura.
2. **`ROLE_ALIASES` PT→EN** (`src/intensicare/auth/abac.py`, linhas 457–469): `medico→PHYSICIAN`, `enfermeiro→NURSE`, `farmacia→PHARMACIST`, `admin→ADMIN`, `readonly→VIEWER`, e **`fisioterapeuta→PHYSIOTHERAPIST`** / **`nutricao→NUTRITIONIST`** — dois papéis clínicos adicionados à matriz ABAC (`ClinicalRole`) com políticas espelhando `NURSE`, por não terem equivalente EN direto na matriz original.
3. **`role` real em `require_abac`**: as três chamadas em `src/intensicare/api/v1/admin.py` (linhas 208–209, 240–241, 324–325) passam `role_str=current_admin.role` — o role clínico efetivo do usuário autenticado, não um literal hardcoded.
4. **`UserCreate.role` validado** contra `CLINICAL_ROLES` (`src/intensicare/api/v1/admin.py`, linhas 98–100 na criação, 117–119 na atualização) — role fora do vocabulário PT-BR é rejeitado na entrada, não silenciosamente aceito.
5. **Migração `0040`** (`alembic/versions/0040_backfill_admin_role.py`): backfill único de `role='admin'` para usuários com `is_admin=TRUE` e `role` ainda no default `'readonly'` — necessário porque, antes desta correção, `UserCreate` nunca expunha `role`, então todo usuário criado via API admin persistia com `role='readonly'` independente de `is_admin`. O `downgrade()` é deliberadamente no-op: reverter poderia re-travar administradores legítimos fora dos próprios endpoints admin, reintroduzindo o bug de patient-safety que a migração corrige.
6. **`ABACAccessDenied → HTTP 403`** via exception handler global (`src/intensicare/main.py`, linhas 144–154) — antes propagava como 500 (erro não tratado); agora retorna 403 com corpo JSON seguro (`{"detail": str(exc)}`, mensagem já livre de detalhes internos).

## Alternativas Consideradas

### Alternativa A: Manter o bypass de `is_admin`, mas auditar seu uso
- **Prós:** menor risco de regressão de acesso para operadores administrativos.
- **Contras:** não resolve o problema de fundo — `is_admin` é uma permissão administrativa (gestão de usuários/config), não uma credencial clínica. Um sysadmin não deveria poder assinar evoluções médicas ou prescrever como se fosse `medico`.
- **Rejeitada porque:** a auditoria classificou isso como falha CRITICAL de patient-safety, não apenas de higiene de código.

### Alternativa B: Role desconhecido → erro 500 / bloqueio total de login
- **Prós:** máxima segurança — nunca deixa passar um role não mapeado.
- **Contras:** um erro de seed de dados ou um vocabulário novo ainda não mapeado em `ROLE_ALIASES` derrubaria o login de usuários legítimos.
- **Rejeitada porque:** a estratégia adotada (fallback para `VIEWER` com `logger.warning` auditável, em `evaluate_abac`) já é segura por padrão (somente leitura) sem indisponibilizar o sistema, e o `logger.warning` mantém a rastreabilidade.

### Alternativa C: Migração 0040 com `downgrade()` reversível
- **Prós:** simetria convencional de migrações Alembic.
- **Contras:** não é possível distinguir, pós-fato, quais linhas `role='readonly'` eram bug (usuários admin travados) de quais eram configuração deliberada de um operador — reverter arriscaria re-introduzir o mesmo bug de patient-safety.
- **Rejeitada porque:** a migração documenta explicitamente essa ambiguidade e opta por `downgrade()` no-op como comportamento mais seguro.

## Consequências

### Positivas
- `is_admin` (permissão administrativa) e papel clínico (`role`) tornam-se dimensões independentes e corretamente separadas — alinhado ao princípio de menor privilégio.
- Vocabulário PT-BR (camada de guards/dependencies) e EN (camada ABAC) reconciliados por um único ponto de mapeamento (`ROLE_ALIASES`), eliminando divergência silenciosa.
- Erros de autorização ABAC agora produzem HTTP 403 correto (antes: 500), melhorando observabilidade e comportamento de clientes.
- Cobertura de `PHYSIOTHERAPIST`/`NUTRITIONIST` na matriz ABAC elimina um gap onde esses dois papéis clínicos PT-BR não tinham equivalente de política.

### Negativas
- `is_admin=True` deixou de implicar qualquer permissão clínica — administradores que também atuam clinicamente precisam ter `role` corretamente configurado (mitigado pela migração 0040 para o caso já existente em produção).
- Role desconhecido agora produz `VIEWER` (grau de acesso reduzido) em vez do comportamento anterior (que, por efeito do bypass, muitas vezes não era exercitado) — usuários com dados de role inconsistentes podem notar perda de acesso até correção manual.
- Incoerência de dados (`role` fora do vocabulário, ou `is_admin` sem `role` clínico correspondente) agora **bloqueia** em vez de ser absorvida silenciosamente — comportamento intencional ("fail-closed by design"), mas exige que operações/suporte estejam preparados para o volume inicial de correções manuais de dados legados.

---

## Referências

- `src/intensicare/auth/dependencies.py` (`_has_role`, `require_admin`, `CLINICAL_ROLES`, `require_medico`/`require_enfermeiro`/`require_fisioterapeuta`/`require_farmacia`)
- `src/intensicare/auth/abac.py` (`ROLE_ALIASES`, `evaluate_abac`, `require_abac`, `ABACAccessDenied`)
- `src/intensicare/api/v1/admin.py` (`require_abac(role_str=current_admin.role, ...)`, validação de `UserCreate.role`/`UserUpdate.role` contra `CLINICAL_ROLES`)
- `src/intensicare/main.py` (exception handler `ABACAccessDenied` → HTTP 403)
- `alembic/versions/0040_backfill_admin_role.py`
- `docs/audit/fullspectrum/` (auditoria full-spectrum, audit CRITICAL #6)
