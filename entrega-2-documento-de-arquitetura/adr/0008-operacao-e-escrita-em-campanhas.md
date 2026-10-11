# ADR-0008: Operação por célula e controle de escrita em campanhas

- **Status:** substitui o ADR-0004
- **Contexto:** Projeções e réplicas de leitura não resolvem a disputa concorrente por vagas. Clientes têm portes diferentes e campanhas podem multiplicar o acesso.
- **Decisão:** Cada célula mantém limites, métricas e filas próprios. O gateway usa mapa de rotas replicado em memória, carregado assincronamente. Células compartilhadas aplicam quotas por tenant. Campanhas usam fila de entrada, vagas particionadas por unidade, data e horário, chaves idempotentes e pré-aquecimento da capacidade de escrita. O escalonamento considera profundidade de fila, latência, erros e saturação de escrita.
- **Alternativas consideradas:** Escalar somente réplicas de leitura, descartado por não resolver a disputa de escrita; cluster regional único, descartado pelo blast radius; serverless em todas as transações, descartado por imprevisibilidade.
- **Consequências positivas:** Pico controlado, capacidade reservada para cada tenant e expansão apenas da célula pressionada.
- **Consequências negativas:** A fila introduz estado de espera visível, e quotas, pré-aquecimento e métricas aumentam a responsabilidade operacional.
