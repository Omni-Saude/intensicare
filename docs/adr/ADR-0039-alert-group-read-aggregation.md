# ADR-0039 — Consolidação de alertas por agregação na leitura + semântica de ações de grupo

**Status:** Aceito (2026-07-13)
**Contexto:** Baseline medido (docs/audit/ALERT_CONSOLIDATION_ANALYSIS.md): 53 alertas crus = 7 episódios clínicos (ruído 7,57×) no dataset seed; `dedup_key` parseado mas nunca aplicado (C#14); `correlation_engine` desconectado do caminho vivo; burst causado por `cooldown_minutes=0` no seed do tenant demo.

## Decisão

1. **Agregação na LEITURA** (não na escrita): `GET /api/v1/alerts?group_by=signal` agrupa por `(mpi_id, score_type)` e retorna grupos com membros crus. A fonte de verdade (`alert` rows) nunca é fundida/alterada — todo evento clínico permanece persistido, auditável e alcançável (invariante: zero perda de informação). Sem `group_by`, o contrato atual permanece intacto (mudança aditiva).
2. **Shape do grupo** (contrato adjudicado): `{ mpi_id, patient_name, score_type, max_severity, count, first_created_at, latest_created_at, escalating: bool (severidade do membro mais novo > do mais antigo ativo), members: [Alert…] }` + `total_groups`/`total_alerts`. Ordenação: max_severity desc, latest_created_at desc.
3. **Escalação fura o rollup**: `escalating=true` é sinalizado no grupo e a UI o destaca; membros individuais nunca são suprimidos — apenas apresentados dentro do grupo expansível (padrão APG disclosure já existente em alert-row).
4. **Ações de grupo = N ações individuais explícitas**: o cliente envia acknowledge/resolve POR MEMBRO (IDs visíveis no momento, com confirmação exibindo a contagem). O backend NÃO ganha estado de "grupo": cada transição continua por-alerta (state machine e auditoria intactas). Ocorrência nova após ack do grupo entra `active` e reativa o grupo na visão default — comportamento desejado (nunca silenciar sinal novo).
5. **Config, não código**: `cooldown_minutes` do seed demo sobe de 0 → 15 min (MEWS/NEWS2), reduzindo bursts futuros; o gate já existente em `alert_engine.py:77` volta a operar. Produção configura por tenant via admin/thresholds.
6. **Humanização**: títulos/corpos gerados por templates centralizados (`services/alert_copy.py`), padrão 3 partes (o que aconteceu / por que importa / o que verificar), PT-BR clínico no tom de `_build_recommendation()`/CDS; NEWS2/MEWS × watch/urgent/critical cobertos; score types não exercitados usam fallback genérico seguro. UI mostra título curto na linha e corpo explicativo no expandir.
7. **Não-objetivos deste ciclo**: dedup na escrita/`occurrence_count` persistente (opção (i) — pode ser construída por cima sem quebrar este contrato); religar `correlation_engine`; remover o site morto `ews_nrt_runner.py:656` (recebe comentário de aviso).

## Consequências

- Reversível por deploy de frontend/param de query; zero migração de banco; WS `alert.raised` inalterado (1:1 por alerta criado).
- Crescimento físico da tabela `alert` não é tratado aqui (mitigado pelo cooldown de seed; opção (i) fica como evolução futura documentada).
