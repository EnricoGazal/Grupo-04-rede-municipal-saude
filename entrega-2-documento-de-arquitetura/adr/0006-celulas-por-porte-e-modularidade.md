# ADR-0006: Células por porte e modularidade operacional

- **Status:** substitui o ADR-0001
- **Contexto:** A leitura cruzada mostrou que uma célula completa por cidade impõe custo fixo excessivo a clientes pequenos e que seis serviços por célula excedem a capacidade operacional de três times.
- **Decisão:** Usar células de capacidade. Clientes grandes ou críticos recebem célula dedicada; clientes pequenos podem compartilhar uma célula com quotas de CPU, memória, conexões, filas e consumidores por tenant. Dentro da célula, o padrão inicial são três unidades operacionais: núcleo clínico modular; regulação e integração; engajamento e campanhas. Um módulo só é extraído como serviço quando houver necessidade comprovada de escala, isolamento ou ciclo de implantação diferente.
- **Alternativas consideradas:** Célula dedicada para toda cidade, descartada como regra universal por custo; microsserviços completos em toda célula, descartados pela complexidade operacional; monolito multi-tenant sem quotas, descartado pelo raio de falha.
- **Consequências positivas:** Custo proporcional ao porte, ownership alinhado aos times, isolamento por quota e promoção controlada para célula dedicada.
- **Consequências negativas:** Células compartilhadas exigem quotas, observabilidade e migração controlada; módulos exigem disciplina de dependências.
