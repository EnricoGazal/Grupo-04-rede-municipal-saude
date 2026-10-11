# Entrega 4a — Objeções enviadas ao Grupo 2

**Revisor:** Grupo 04 — Saúde D. **Revisado:** Grupo 02 — Saúde E.

As objeções abaixo devem ser confrontadas com o repositório efetivamente recebido. Elas são perguntas técnicas preparadas a partir das exigências do caso Saúde E.

> **Formato de impressão:** cada objeção está em bloco vertical para evitar tabelas estreitas e rolagem horizontal.

## Objeção 1 — Retenção e auditoria

**Decisão ou trecho atacado:** ADR de retenção e auditoria.

**Argumento:** Guardar todos os eventos clínicos para reconstrução pode conflitar com o direito ao esquecimento. O projeto precisa distinguir log de auditoria, dado clínico e dado derivado.

**Alternativa do Grupo 4:** Separar retenção legal, auditoria minimizada e projeções apagáveis; registrar a base legal de cada campo.

## Objeção 2 — Arquitetura multi-tenant

**Decisão ou trecho atacado:** Arquitetura multi-tenant.

**Argumento:** Se todos os clientes compartilham fila e limites, uma campanha pode impedir a auditoria de outro cliente.

**Alternativa do Grupo 4:** Usar células ou, no mínimo, quotas, filas e consumidores isolados por tenant.

## Objeção 3 — Integração federal síncrona

**Decisão ou trecho atacado:** Integração síncrona com o sistema federal.

**Argumento:** Se a notificação depender de resposta síncrona, a indisponibilidade federal viola o prazo e bloqueia a unidade.

**Alternativa do Grupo 4:** Usar outbox local, fila durável, retry e dead-letter com métrica de idade.

## Objeção 4 — Auditoria no mesmo banco operacional

**Decisão ou trecho atacado:** Auditoria persistida no mesmo banco do prontuário.

**Argumento:** Uma transação de auditoria que compartilha lock com prontuário pode degradar o atendimento.

**Alternativa do Grupo 4:** Fazer escrita local rápida e exportação assíncrona para armazenamento de auditoria imutável.

## Objeção 5 — Exclusão física indiscriminada

**Decisão ou trecho atacado:** Exclusão de registros para atender LGPD.

**Argumento:** Apagar prontuário sem preservar o que a lei exige quebra a reconstrução sanitária e a prestação de contas.

**Alternativa do Grupo 4:** Usar workflow jurídico que classifica campos, anonimiza o que puder e mantém somente o mínimo legal.

## Objeção 6 — Event Sourcing geral

**Decisão ou trecho atacado:** Event Sourcing como padrão para todos os agregados.

**Argumento:** A escolha pode tornar o apagamento seletivo e a minimização de dados muito complexos.

**Alternativa do Grupo 4:** Usar estado atual e auditoria referencial, reservando eventos detalhados para agregados sem dado pessoal direto.

## Objeção 7 — Falta de teste de reprocessamento

**Decisão ou trecho atacado:** Fluxo de reconstrução de auditoria.

**Argumento:** Auditoria completa exige que um evento possa ser reprocessado sem duplicar notificação ou dispensação.

**Alternativa do Grupo 4:** Usar idempotência por `event_id`, versão do agregado e teste de replay.

## Objeção 8 — Escalabilidade global

**Decisão ou trecho atacado:** Escalonamento regional único.

**Argumento:** Escalar tudo junto mascara qual tenant causa o pico e aumenta custo sem necessidade.

**Alternativa do Grupo 4:** Usar métricas por tenant, quotas e escala por célula ou partição.

## Referências

[1]: ../entrega-2-documento-de-arquitetura/documento-arquitetura.md "Documento de arquitetura do Grupo 4"
[2]: https://puc-campinas.instructure.com/courses/97274/pages/um-problema-cinco-realidades "Enunciado da atividade"

- [Documento de arquitetura do Grupo 4][1]
- [Enunciado da atividade][2]
