# ADR-0007: Autoridade única de reserva e adaptadores versionados por tenant

- **Status:** substitui o ADR-0003
- **Contexto:** O legado de regulação pode continuar aceitando reservas por até dois anos, e cada cidade pode possuir API, versão ou sistema diferente. Dois escritores simultâneos impediriam garantir exclusividade de leito.
- **Decisão:** Manter uma porta interna estável e adaptadores versionados por tenant. Para cada tenant existe uma autoridade única de reserva por fase. Enquanto o legado for autoridade, o serviço novo registra `SOLICITADA` ou `PENDENTE_LEGADO`, envia operação idempotente e consulta o estado após timeout. Depois da migração, o serviço novo torna-se autoridade e o legado fica somente leitura. Nenhum lock local permanece aberto durante chamada externa.
- **Alternativas consideradas:** Dois escritores simultâneos, descartados por risco de dupla reserva; banco compartilhado com legado, descartado por acoplamento; repetição sem chave idempotente, descartada por ambiguidade em timeout.
- **Consequências positivas:** Exclusividade explicável, integração específica por cliente e migração incremental.
- **Consequências negativas:** Há estados pendentes, cada adaptador exige teste de contrato e o catálogo precisa registrar autoridade e versão.
